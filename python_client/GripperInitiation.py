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
    iiwa = iiwaPy3(KUKA_IP)

    curled = [0, -30, 0, -115, 0, 115, 0]
    iiwa.movePTPJointSpace(curled, [0.1])
finally:
    iiwa.close()
