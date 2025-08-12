import subprocess
import time
import sys

# Start handtracker.py first
handtracker_proc = subprocess.Popen([sys.executable, 'handtracker.py'])

# Wait a moment to ensure handtracker is ready
# (adjust if needed for your system)
time.sleep(1)

# Start pong.py
pong_proc = subprocess.Popen([sys.executable, 'pong.py'])

try:
    # Wait for both processes to finish
    handtracker_proc.wait()
    pong_proc.wait()
except KeyboardInterrupt:
    pass
finally:
    # Terminate both if still running
    handtracker_proc.terminate()
    pong_proc.terminate()
