import math
import time

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


# Constants
radius_of_circ_move = 50
null_space_angle = 80

# relVel: is a double, from zero to one, specifies the over-ride relative velocity. 
# home position - gripper facing ceiling
def go_home(): 
    home = [0,0,0,0,0,0,0]
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

def create_lemniscate_spline(center_frame):
    right_frame = list(center_frame)
    left_frame = list(center_frame)
    top_left_frame = list(center_frame)
    top_right_frame = list(center_frame)
    bottom_right_frame = list(center_frame)
    bottom_left_frame = list(center_frame)
    
    right_frame[0] += 2 * radius_of_circ_move
    left_frame[0] -= 2 * radius_of_circ_move
    top_left_frame[0] -= radius_of_circ_move
    top_left_frame[1] += radius_of_circ_move
    top_right_frame[0] += radius_of_circ_move
    top_right_frame[1] += radius_of_circ_move
    bottom_right_frame[0] += radius_of_circ_move
    bottom_right_frame[1] -= radius_of_circ_move
    bottom_left_frame[0] -= radius_of_circ_move
    bottom_left_frame[1] -= radius_of_circ_move
    
    return [
        bottom_left_frame,
        left_frame,
        top_left_frame,
        center_frame,
        bottom_right_frame,
        right_frame,
        top_right_frame,
        center_frame
    ]
    
try:
    # go_home()
    # print(iiwa.getEEFPos())
    # reset_pose()
    # print(iiwa.getEEFPos())
    # Computing spline for lemniscate motion
    start_frame = iiwa.getEEFPos()
    print(start_frame)
    test = start_frame
    test[2] = start_frame[2] + 50
    # print(f"test point1: {test}")
    iiwa.movePTPLineEEF(test, [50])
    # velocity = [50]
    exit()
    # test = [456.1023819692073, 0.0033426602972159753, 497.37888346101744, 0.0, 1.570524224330064, -2.251119173941558e-05]
    test = start_frame
    test[0] = start_frame[0] + 30
    print(f"test point1: {test}")
    iiwa.movePTPLineEEF(test, velocity)
    test = [576.0882996908707, 0.005263373878154082, 497.388209280446, 0.0, 1.5706993832322678, -2.606998349239476e-05]
    print(f"test point2: {test}")
    iiwa.movePTPLineEEF(test, velocity)
    
    start_frame = iiwa.getEEFPos()
    print(start_frame)
    lemniscate_spline = create_lemniscate_spline(start_frame)
    for point in lemniscate_spline:
        print(point)
        pt = start_frame
        print(point[0]-start_frame[0])
        pt[0] = start_frame[0] + (point[0]-start_frame[0])
        pt[1] = start_frame[1]
        print(pt)
        iiwa.movePTPLineEEF(pt, velocity)
        break
        # iiwa.movePTPLineEEF(point, velocity)
    
    # print("Moving in nullspace -{} degrees".format(null_space_angle))
    # e1_offset_neg = math.radians(-null_space_angle)
    # center_frame_neg = list(start_frame)
    # center_frame_neg[6] += e1_offset_neg
    # iiwa.movePTPLineEEF(center_frame_neg, [0.25])
    
    # print("Moving in nullspace {} degrees".format(null_space_angle))
    # e1_offset_pos = math.radians(null_space_angle)
    # center_frame_pos = list(start_frame)
    # center_frame_pos[6] += e1_offset_pos
    # iiwa.movePTPLineEEF(center_frame_pos, [0.25])
    
    # print("Moving back to start position")
    # iiwa.movePTPLineEEF(start_frame, [0.25])
    
except Exception as e:
    print(f"An error occurred: {e}")

finally:
    iiwa.close()
