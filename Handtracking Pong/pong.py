import pygame
import sys
import socket

#Socket server setup
input_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
input_sock.bind(('localhost', 5005))
input_sock.setblocking(False)  # Non-blocking

# Input variables from handtracker.py
left_out = 0
right_out = 0

# Pastel color variables
PASTEL_RED = (255, 90, 90)    # Light Red
PASTEL_BLUE = (110, 170, 255)   # Light Blue
PASTEL_GREEN = (70, 255, 70)  # Liight Green
WHITE = (255, 255, 255)
DARK_GRAY = (30, 30, 30)

# Initialize Pygame
pygame.init()

# Set up the display
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Pong")

#Classes

class Paddle: 
    def __init__(self, x, y, color):
        self.rect = pygame.Rect(x, y, 10, 100)
        self.color = color

    def move(self, dy):
        self.rect.y += dy
        # Keep paddle on screen
        if self.rect.y < 0:
            self.rect.y = 0
        if self.rect.y > 600 - self.rect.height:
            self.rect.y = 600 - self.rect.height

    def draw(self, screen):
        pygame.draw.rect(screen, self.color , self.rect)

    def change_color(self, new_color):
        self.color = new_color

class Ball:
    def __init__(self, x, y, color, pixel_size):
        self.rect = pygame.Rect(x, y, 15, 15)
        self.vx = 3
        self.vy = 3
        self.color = color
        self.pixel_size = pixel_size  # Size of each pixel block

    def move(self):
        self.rect.x += self.vx
        self.rect.y += self.vy
        # Bounce off top and bottom
        

    def bounce(self, axis):
        if axis == 'x':
            self.vx = -self.vx
        elif axis == 'y':
            self.vy = -self.vy

    def draw(self, screen):
        # Draw a pixelated 15x15 circle using small filled rectangles
        cx = self.rect.x + 7
        cy = self.rect.y + 7
        for dx in range(-7, 8):
            for dy in range(-7, 8):
                if dx*dx + dy*dy <= 49:
                    if dx % self.pixel_size == 0 and dy % self.pixel_size == 0:
                        pygame.draw.rect(screen, self.color, (cx + dx, cy + dy, self.pixel_size, self.pixel_size))

class player:
    def __init__(self):
        self.score = 0
    def increment_score(self):
        self.score += 1     

player1 = player()
player2 = player()

# Create paddles and ball
paddle1 = Paddle(30, 250, color=WHITE)
paddle2 = Paddle(760, 250, color=WHITE)
ball = Ball(395, 295, PASTEL_BLUE, 3)

# Set up font for score display
font = pygame.font.SysFont(None, 36)

# Main game loop
running = True
clock = pygame.time.Clock()
waiting_for_enter = True
countdown_active = False
countdown_start_time = None
countdown_seconds = 2
score_text = font.render(f"SCORE: {player1.score} - {player2.score}", True, WHITE)
score_rect = score_text.get_rect(center=(400, 40))


def reset_game(direction):

    ball.rect.x = 395
    ball.rect.y = 295

    paddle1.rect.x = 30
    paddle1.rect.y = 250
    paddle1.change_color(WHITE)

    paddle2.rect.x = 760
    paddle2.rect.y = 250
    paddle2.change_color(WHITE)

    if direction == 'left':
        ball.vx = -abs(ball.vx)
        ball.vy = 3
    else:
        ball.vx = abs(ball.vx)
        ball.vy = 3

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            # Send quit message to handtracker.py before quitting
            try:
                input_sock.sendto(b'quit', ("localhost", 5006))
            except Exception:
                pass
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                # Send quit message to handtracker.py before quitting
                try:
                    input_sock.sendto(b'quit', ("localhost", 5006))
                except Exception:
                    pass
                running = False
            if waiting_for_enter and event.key == pygame.K_RETURN:
                countdown_active = True
                countdown_start_time = pygame.time.get_ticks()

    # Receive input from handtracker.py
    try:
        data, _ = input_sock.recvfrom(1024)
        left_out, right_out = map(int, data.decode().split(','))
    except BlockingIOError:
        # No data available, just continue
        pass

    # Handle countdown after pressing Enter
    if countdown_active:
        elapsed = (pygame.time.get_ticks() - countdown_start_time) / 1000.0
        seconds_left = countdown_seconds - int(elapsed)
        if seconds_left > 0:
            # Draw background and paddles/ball for context
            screen.fill(DARK_GRAY)
            paddle1.draw(screen)
            paddle2.draw(screen)
            ball.draw(screen)
            screen.blit(score_text, score_rect)
            
            # Draw countdown number in white, centered at 1/3 from the top
            countdown_text = font.render(str(seconds_left), True, WHITE)
            countdown_rect = countdown_text.get_rect(center=(400, 200))  # 1/3 of 600 is 200
            screen.blit(countdown_text, countdown_rect)
            pygame.display.flip()
            clock.tick(60)
            continue
        else:
            countdown_active = False
            waiting_for_enter = False

    if not waiting_for_enter:
        # Paddle movement (keyboard)
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            paddle1.move(-6)
            paddle1.change_color(PASTEL_GREEN)
        if keys[pygame.K_s]:
            paddle1.move(6)
            paddle1.change_color(PASTEL_RED)
        if keys[pygame.K_UP]:
            paddle2.move(-6)
            paddle2.change_color(PASTEL_GREEN)
        if keys[pygame.K_DOWN]:
            paddle2.move(6)
            paddle2.change_color(PASTEL_RED)

        # Paddle movement (handtracker)
        #Move up
        if left_out == 1:
            paddle1.move(-6)
            paddle1.change_color(PASTEL_GREEN)
        
        #Move down
        elif left_out == -1:
            paddle1.move(6)
            paddle1.change_color(PASTEL_RED)
        
        # No move
        else:
            paddle1.change_color(WHITE)

        #Move up
        if right_out == 1:
            paddle2.move(-6)
            paddle2.change_color(PASTEL_GREEN)
        
        #Move down
        elif right_out == -1:
            paddle2.move(6)
            paddle2.change_color(PASTEL_RED)
        
        # No move
        else:
            paddle2.change_color(WHITE)

        # Ball movement
        ball.move()

        # Paddle-ball collision detection 
        if ball.rect.colliderect(paddle1.rect) and ball.vx < 0:
            ball.bounce('x')
            ball.rect.left = paddle1.rect.right  # Prevent sticking
        if ball.rect.colliderect(paddle2.rect) and ball.vx > 0:
            ball.bounce('x')
            ball.rect.right = paddle2.rect.left  # Prevent sticking
        
        # Collision with top and bottom walls
        if ball.rect.top <= 0 or ball.rect.bottom >= 600:
            ball.bounce('y')

        # Score detection
        if ball.rect.left <= 0:
            player2.increment_score()
            reset_game(direction='right')
            waiting_for_enter = True
        if ball.rect.right >= 800:
            player1.increment_score()
            reset_game(direction='left')
            waiting_for_enter = True
        score_text = font.render(f"SCORE: {player1.score} - {player2.score}", True, WHITE)

    # Draw background
    screen.fill(DARK_GRAY)

    # Draw paddles and ball
    paddle1.draw(screen)
    paddle2.draw(screen)
    ball.draw(screen)

    # Render and draw the score centered at the top
    screen.blit(score_text, score_rect)

    # Show message if waiting for Enter
    if waiting_for_enter:
        msg = font.render("Press ENTER to start", True, WHITE)
        msg_rect = msg.get_rect(center=(400, 200))
        screen.blit(msg, msg_rect)

    pygame.display.flip()    # Update the display
    clock.tick(60)

pygame.quit()
sys.exit()