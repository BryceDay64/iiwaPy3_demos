import math
from time import sleep
from onrobot_sg import SG
from iiwaPy3 import iiwaPy3
from MATLABToolBoxStart import MATLABToolBoxStart

gripper_obj = SG('192.168.8.179', 502)
step = 50  # step for moving the gripper

KUKA_IP = "192.168.8.147"  # Replace with actual robot IP KUKA 14
KUKA_PORT = 30300
try:
    target_width = gripper_obj.get_gp_wd() + (5 * step)
    gripper_obj.set_target(target_width)


    wakeup = MATLABToolBoxStart(KUKA_IP, KUKA_PORT)

    try:
        print(wakeup.start_client())
        sleep(2)
    except Exception as e:
        print(f"Starting client failed with error message: {e}")
    # Connect to the robot

    iiwa = iiwaPy3(KUKA_IP)


    def go_home():
        home = [0, 0, 0, 0, 0, 0, 0]
        print("Moving to home pose")
        iiwa.movePTPJointSpace(home, [0.5])


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


    curled = [0, -30, 0, -115, 0, 115, 0]
    temp_list = []
    for item in curled:
        item = math.radians(item)
        temp_list.append(item)
    curled = temp_list

    iiwa.movePTPJointSpace(curled, [0.1])
finally:
    iiwa.close()
