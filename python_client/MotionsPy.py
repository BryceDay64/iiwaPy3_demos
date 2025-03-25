import math
import time
import subprocess

gripper_open_script = "/home/l5vel/kuka/onrobot-rg/src/open_demo.py"
gripper_close_script = "/home/l5vel/kuka/onrobot-rg/src/close_demo.py"

from iiwaPy3 import iiwaPy3
from MATLABToolBoxStart import MATLABToolBoxStart

# KUKA iiwa robot IP and port
#KUKA_IP = "192.168.0.50"  # Replace with actual robot IP KUKA 141
KUKA_IP = "192.168.0.49"  # Replace with actual robot IP KUKA 71
KUKA_PORT = 30300 # default port, any changes should reflect in WB
# # start the matlab client
# wakeup = MATLABToolBoxStart(KUKA_IP,KUKA_PORT)
# try:
#     wakeup.start_client()
#     time.sleep(2)
# except Exception as e:
#     print(f"Starting client failed with error message: {e}")

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
    subprocess.run(['python', gripper_open_script])  
    poses = [
    # [0, 0, 0, 0, 0, 0,0],
    [0, 0.3490658503988659, 0, -1.9198621771937625, 0, -0.6981317007977318, 0],
    [-1.8519576280618033, 0.338401674539098, 0.010143388046013073, -1.7310535168188748, 0.011248297614187204, 0.9305050160863391, -0.25927043669260386],
    [-1.8471252290421376, 0.6731921426462674, 0.010166937010028685, -1.7608451015264406, 0.010367600982972363, 0.5656866344553269, -0.2585670825303519],
    [-1.8684400719132628, 0.1652240520453777, 0.010015156851456722, -1.204313516067877, 0.012278173994288235, 1.5478234665129371, 0.018026071837702762],
    [0.05550931186866582, 0.13278802823099428, 0.010055543661264791, -0.9745095919281656, 0.011293837617694867, 1.9218108587929805, 0.013936335285702506],
    [0.08888298142600895, 0.36669630976401607, 0.010013958355675992, -1.3982740615817493, 0.00486415722708451, 1.2644130257614967, 0.04091324496186948],
    [0.05550931186866582, 0.13278802823099428, 0.010055543661264791, -0.9745095919281656, 0.011293837617694867, 1.9218108587929805, 0.013936335285702506],
    # [1.5877845647728397, -0.7370301912308904, 0.010037986739820511, -1.470312615687773, 0.013016498184298444, 1.2977129922461899, 0.014328758714462495],
    # [1.5877856433863173, -0.046436055218386695, 0.010041402240083585, -1.4702307634546792, 0.013016689821450312, 1.2975146533572426, 0.014329178138898365],
    
    # [1.5877810893859667, -0.046418498296942425, 0.010031215734987399, -0.29734863350379914, 0.013013526063115222, 2.0388879875668087, 0.014328878596765491],
    # [1.5877822278860543, -0.04638362421865985, 0.010032234352772094, -0.2973507308441447, -2.67047148865588, 2.0388879875668087, 0.014329897214550184],
    
    # [0.05550931186866582, 0.13278802823099428, 0.010055543661264791, -0.9745095919281656, 0.011293837617694867, 1.9218108587929805, 0.013936335285702506],
    # [0.08888298142600895, 0.36669630976401607, 0.010013958355675992, -1.3982740615817493, 0.00486415722708451, 1.2644130257614967, 0.04091324496186948],
    
    # [0.05550931186866582, 0.13278802823099428, 0.010055543661264791, -0.9745095919281656, 0.011293837617694867, 1.9218108587929805, 0.013936335285702506],
    # [0.05550931186866582, 0.13278802823099428, 0.010055543661264791, -0.9745095919281656, 0.011293837617694867, 1.9218108587929805, 0.013936335285702506]
    ]
    # iiwa.movePTPJointSpace(poses[3], [0.25])
    # iiwa.movePTPJointSpace(poses[2], [0.1])
    # subprocess.run(['python', gripper_open_script])
    # iiwa.movePTPJointSpace(poses[4], [1])
    # exit()
    itr = 0
    for pose in poses:
        itr+=1
        print(itr)
        if itr == 4:
            subprocess.run(['python', gripper_close_script])
        if itr == 6 or itr == 16:
            vel = [0.1]
        else:
            vel = [0.25]
        iiwa.movePTPJointSpace(pose, vel)  
        if itr == 6:
            subprocess.run(['python', gripper_open_script])  
        if itr == 16:
            subprocess.run(['python', gripper_open_script])
    exit()

    go_home()
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
