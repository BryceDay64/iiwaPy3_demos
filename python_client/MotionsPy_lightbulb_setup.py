import math
import time
import keyboard

# gripper_open_script = "/home/l5vel/kuka/onrobot-rg/src/open_demo.py"
# gripper_close_script = "/home/l5vel/kuka/onrobot-rg/src/close_demo.py"

from iiwaPy3 import iiwaPy3
from MATLABToolBoxStart import MATLABToolBoxStart

# KUKA iiwa robot IP and port
KUKA_IP = "192.168.8.147"  # Replace with actual robot IP KUKA 14
KUKA_PORT = 30300  # default port, any changes should reflect in WB
# start the matlab client

wakeup = MATLABToolBoxStart(KUKA_IP, KUKA_PORT)
try:
    print(wakeup.start_client())
    time.sleep(2)
except Exception as e:
    print(f"Starting client failed with error message: {e}")
# Connect to the robot
try:
    iiwa = iiwaPy3(KUKA_IP)
except Exception as e:
    print(f"Client running but connection failed with error message: {e}")

# Constants
radius_of_circ_move = 50
null_space_angle = 80

# Positions in degrees
available_pos = {
    'curled':                   [0, -115, 0, -115, 0, 115, 0],
    'extended':                 [1.27, -111.58, -.01, -65.79, .1, 46.99, 0],
    'beneath_bulb_unscrewed':   [129.69, -106.62, 0, -63.41, .09, 44.39, -160],
    'on_bulb_unscrewed':        [-39.69, -101.91, -.01, -60.52, .11, 42.58, -160],
    'full_bulb_unscrewed':      [-39.69, -100.21, -0.01, -59.34, 0.1, 42.07, -160],
    'full_bulb_screwed':        [-39.69, -100.21, -0.01, -59.34, 0.1, 42.07, 160],
    'on_bulb_screwed':          [-39.69, -101.91, -.01, -60.52, .11, 42.58, 160],
    'beneath_bulb_screwed':     [-39.68, -104.67, -.01, -62.29, .1, 43.57, 160]
}

for key, value in available_pos.items():
    temp_list = []
    for item in value:
        item = math.radians(item)
        temp_list.append(item)
    available_pos.update({key: temp_list})


# relVel: is a double, from zero to one, specifies the over-ride relative velocity.
# home position - gripper facing ceiling
def go_home():
    home = [0, 0, 0, 0, 0, 0, 0]
    print("Moving to home pose")
    iiwa.movePTPJointSpace(home, [0.5])


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


try:
    # subprocess.run(['python', gripper_open_script])

    poses = [
        available_pos['curled'],
        available_pos['extended'],
        available_pos['beneath_bulb_unscrewed'],
        available_pos['extended'],
        available_pos['curled'],
    ]

    # iiwa.movePTPJointSpace(poses[3], [0.25])
    # iiwa.movePTPJointSpace(poses[2], [0.1])
    # subprocess.run(['python', gripper_open_script])
    # iiwa.movePTPJointSpace(poses[4], [1])
    # exit()
    itr = 0
    vel = [0.1]
    print(poses)
    for pose in poses:
        itr += 1
        print(pose)
        iiwa.movePTPJointSpace(pose, vel)
        if itr == 3:
            print('Press esc when finished with alignment!')
            while True:
                if keyboard.is_pressed('esc'):
                    break

except Exception as e:
    print(f"An error occurred: {e}")

finally:
    iiwa.close()
