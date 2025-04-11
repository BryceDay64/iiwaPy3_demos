import math
import time
import keyboard
import numpy as np
# import subproces

from iiwaPy3 import iiwaPy3
from MATLABToolBoxStart import MATLABToolBoxStart

# KUKA iiwa robot IP and port
KUKA_IP = "192.168.8.147"  # Replace with actual robot IP KUKA 14
KUKA_PORT = 30300  # default port, any changes should reflect in WB
# start the matlab client
# Connect to the robot
# try:
#     iiwa = iiwaPy3(KUKA_IP)
# except Exception as e:
#     print(f"Client running but connection failed with error message: {e}")

# Constants
radius_of_circ_move = 50
null_space_angle = 80

# Positions in degrees
available_pos = {
    'curled':                   [0, -115, 0, -115, 0, 115, -90],
    'curled away':              [-160, -30, 0, -115, 0, 115, -90],
    'helping':                  [0, -90, 0, 45, 0, 45, -90],
    'midway':                   [-49.32, -79.38, -.55, -20.61, -.1, 55.61, -90]
}

weightOfTool = .25  # 1 kg
cOMx = 0.01554
cOMy = 0.01906
cOMz = 0.05352

cStiness = 2500
rStifness = 50
nStifness = 50

for key, value in available_pos.items():
    temp_list = []
    for item in value:
        item = math.radians(item)
        temp_list.append(item)
    available_pos.update({key: temp_list})

wakeup = MATLABToolBoxStart(KUKA_IP, KUKA_PORT)
try:
    print(wakeup.start_client())
    time.sleep(2)
except Exception as e:
    print(f"Starting client failed with error message: {e}")
print('connected here')
try:
    iiwa = iiwaPy3(KUKA_IP)
    time.sleep(1)
    print('CONNECTED')
    vel = [0.4]
    iiwa.movePTPJointSpace(available_pos['curled away'], vel)
    run = 0
    while True:
        if keyboard.is_pressed('shift'):
            vel = [0.4]
            iiwa.movePTPJointSpace(available_pos['helping'], vel)
            if run >= 1:
                iiwa.realTime_startImpedanceJoints(weightOfTool, cOMx, cOMy, cOMz, cStiness, rStifness, nStifness)
                run += 1
                iiwa.realTime_stopDirectServoJoints()
            iiwa.realTime_startImpedanceJoints(weightOfTool, cOMx, cOMy, cOMz, cStiness, rStifness, nStifness)
            run += 1
            time.sleep(1)
            vel = [0.4]
            itr = 0
            steps = 1000
            # stepLength = ((1 - (1 / (1 + steps))) * np.array(helping) +
            #             (1 / (1 + steps)) * np.array(curledAway))
            jointDiff = np.array(available_pos['curled away'])-np.array(available_pos['helping'])
            stepLength = np.array(jointDiff)/(steps-1)
            while itr < steps:
                newPoint = np.array(available_pos['helping'])+itr*np.array(stepLength)
                newPoint = newPoint.tolist()
                # temp_list = []
                # for item in newPoint:
                #     item = math.degrees(item)
                #     temp_list.append(item)
                # newPoint = temp_list
                iiwa.sendJointsPositions(newPoint)
                itr += 1
            time.sleep(4)
            iiwa.realTime_stopDirectServoJoints()
            iiwa.movePTPJointSpace(available_pos['midway'], [0.1])
            time.sleep(1.5)
            iiwa.movePTPJointSpace(available_pos['curled away'], [0.4])
            print('stopped')

        # elif keyboard.is_pressed('c'):
        #     vel = [0.1]
        #     iiwa.movePTPJointSpace(available_pos['curled away'], vel)
        #     iiwa.realTime_stopDirectServoJoints()

        elif keyboard.is_pressed('esc'):
            iiwa.realTime_stopDirectServoJoints()
            time.sleep(0.5)
            vel = [0.4]
            iiwa.movePTPJointSpace(available_pos['curled away'], vel)
            break

except Exception as e:
    print(f"An error occurred: {e}")

finally:
    iiwa.close()

'''
    itr = 0
    vel = [0.1]
    print(poses)
    for pose in poses:
        print(pose)
        itr += 1
        print(itr)
        iiwa.movePTPJointSpace(pose, vel)

        match itr:
            case 4:
                # grab
                subprocess.run(['python', gripper_close_script])
            case 5:
                # full close
                subprocess.run(['python', gripper_close_script])
                subprocess.run(['python', gripper_close_script])
            case 6:
                # release
                subprocess.run(['python', gripper_open_script])
            case 7:
                # full open
                subprocess.run(['python', gripper_open_script])
                subprocess.run(['python', gripper_open_script])
            case 8:
                time.sleep(10)
            case 9:
                # grab
                subprocess.run(['python', gripper_close_script])
            case 10:
                # full close
                subprocess.run(['python', gripper_close_script])
                subprocess.run(['python', gripper_close_script])
            case 11:
                # release
                subprocess.run(['python', gripper_open_script])
            case 12:
                # full open
                subprocess.run(['python', gripper_open_script])
                subprocess.run(['python', gripper_open_script])
        '''
