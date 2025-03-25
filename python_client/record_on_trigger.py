import math
import time
import keyboard

from iiwaPy3 import iiwaPy3
from MATLABToolBoxStart import MATLABToolBoxStart

# KUKA iiwa robot IP and port
#KUKA_IP = "192.168.0.50"  # Replace with actual robot IP KUKA 141
KUKA_IP = "192.168.0.49"  # Replace with actual robot IP KUKA 71
KUKA_PORT = 30300 # default port, any changes should reflect in WB
# start the matlab client
wakeup = MATLABToolBoxStart(KUKA_IP,KUKA_PORT)
try:
    wakeup.start_client()
    time.sleep(2)
except Exception as e:
    print(f"Starting client failed with error message: {e}")

# Connect to the robot
try:
    iiwa = iiwaPy3(KUKA_IP)
except Exception as e:
    print(f"Client running but connection failed with error message: {e}")

# default start position
def reset_pose():
    offset_axis_2_and_4 = math.radians(20)
    offset_axis_4_and_6 = math.radians(-40)
    vRel = [1.0]
    loop_center_position = [
        0,
        offset_axis_2_and_4,
        0,
        offset_axis_2_and_4 + offset_axis_4_and_6 - math.radians(90),
        0,
        offset_axis_4_and_6,
        0
    ]
    print("Moving to default pose")
    iiwa.movePTPJointSpace(loop_center_position, vRel)

def save_eef_positions():
    print("Record")
    positions = []
    print("Press any key to save EEF position. Press 'q' to quit.")
    while True:
        event = keyboard.read_event(suppress=True)  # Captures key press
        if event.event_type == keyboard.KEY_DOWN:
            eef_pos = iiwa.getEEFPos()
            positions.append(eef_pos)
            print(f"Saved position: {eef_pos}")

            if event.name == 'q':  # Exit when 'q' is pressed
                print("Exiting position logging.")
                break

if __name__ == "__main__":
    reset_pose()
    print("Starting main loop...")
    print(f"Stating EEF pos is; {iiwa.getEEFPos()}")
    save_eef_positions()