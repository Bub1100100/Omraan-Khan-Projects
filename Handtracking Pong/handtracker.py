import cv2 as cv
import mediapipe as mp
import socket
import select

# Socket client setup (to send paddle data)
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# Socket server setup (to receive quit signal)
quit_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
quit_sock.bind(("localhost", 5006))
quit_sock.setblocking(False)

#Hand class to store the hand information
class Hand:
    def __init__(self, landmarks, handedness, frame_shape):
        self.landmarks = landmarks  # List of 21 landmarks
        self.handedness = handedness  # 'Left' or 'Right'
        self.color = (0, 255, 0) if handedness == 'Left' else (255, 0, 0)
        # Calculate center position
        x = sum([lm.x for lm in landmarks]) / len(landmarks)
        y = sum([lm.y for lm in landmarks]) / len(landmarks)
        self.center = (int(x * frame_shape[1]), int(y * frame_shape[0]))

    def __repr__(self):
        return f"Hand(center={self.center}, handedness={self.handedness})"

cap = cv.VideoCapture(0)
cap.set(cv.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv.CAP_PROP_FRAME_HEIGHT, 720)



mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands
hand = mp_hands.Hands(max_num_hands=2)

left_out = 0
right_out = 0

while True:
    # Check for quit message from pong.py
    try:
        ready, _, _ = select.select([quit_sock], [], [], 0)
        if ready:
            data, _ = quit_sock.recvfrom(1024)
            if data.decode().strip() == "quit":
                break
    except Exception:
        pass
    read_scucess, frame = cap.read() #reading the frame from the camera
    frame = cv.flip(frame, 1)
    if read_scucess:
        # Convert the BGR image to RGB because mediapipe needs RGB images and opens cv uses BGR
        RGB_fixed_frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
        
        #the reult from hand detection:
        result_hands = hand.process(RGB_fixed_frame) 
       
        # Two empty variables to store the left and right hand objects
        left_hand = None 
        right_hand = None
       
        #checking if any hand is detected.
        if result_hands.multi_hand_landmarks and result_hands.multi_handedness:
            
            #looping through the detected hands
            for hand_landmark, handedness in zip(result_hands.multi_hand_landmarks, result_hands.multi_handedness):
                label = handedness.classification[0].label  # 'Left' or 'Right'
                hand_obj = Hand(hand_landmark.landmark, label, frame.shape)
                if label == 'Left' and left_hand is None:
                    left_hand = (hand_obj, hand_landmark)
                elif label == 'Right' and right_hand is None:
                    right_hand = (hand_obj, hand_landmark)
                # Stop if both found
                if left_hand and right_hand:
                    break
       
        # Draw and label the left hand if found
        if left_hand:
            mp_drawing.draw_landmarks(frame, left_hand[1], mp_hands.HAND_CONNECTIONS)
            h = frame.shape[0]
            y = left_hand[0].center[1]
            # Set color based on vertical third
            if y < 2 * h // 5:
                left_out = 1
                center_color = (0, 255, 0)  # green (top)
            elif y < 3 * h // 5:
                left_out = 0
                center_color = (255, 255, 255)  # white (middle)
            else:
                left_out = -1
                center_color = (0, 0, 255)  # red (bottom)
            cv.circle(frame, left_hand[0].center, 10, center_color, -1)
            cv.putText(frame, 'Left', (left_hand[0].center[0] - 40, left_hand[0].center[1] - 20), cv.FONT_HERSHEY_SIMPLEX, 1, center_color, 2, cv.LINE_AA)
        
        # Draw and label the right hand if found
        if right_hand:
            mp_drawing.draw_landmarks(frame, right_hand[1], mp_hands.HAND_CONNECTIONS)
            h = frame.shape[0]
            y = right_hand[0].center[1]
            if y < 2 * h // 5:
                right_out = 1
                center_color = (0, 255, 0)  # Green (top)
            elif y < 3 * h // 5:
                right_out = 0
                center_color = (255, 255, 255)  # Green (middle)
            else:
                right_out = -1
                center_color = (0, 0, 255)  # Blue (bottom)
            cv.circle(frame, right_hand[0].center, 10, center_color, -1)
            cv.putText(frame, 'Right', (right_hand[0].center[0] - 40, right_hand[0].center[1] - 20), cv.FONT_HERSHEY_SIMPLEX, 1, center_color, 2, cv.LINE_AA)
        
        # Send the left and right hand positions via UDP        
        message = f"{left_out},{right_out}".encode()
        sock.sendto(message, ('localhost', 5005))
        
        cv.imshow('Video Capture', frame)
        # If user presses 'q', send quit to pong.py and exit
        if cv.waitKey(1) == ord('q'):
            try:
                sock.sendto(b'quit', ("localhost", 5005))
            except Exception:
                pass
            break


