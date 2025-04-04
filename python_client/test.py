import threading
import keyboard
import time
import os

def run_continuously():
    while True:
        time.sleep(0.1)

        if keyboard.is_pressed('esc'):
            print('here')
            os._exit(32)

thread = threading.Thread(target=run_continuously)
thread.daemon = True
thread.start()

# Continue with other tasks in the main thread
while True:
    print('running')
    time.sleep(1)