import math
import time
import keyboard
import numpy as np

from iiwaPy3 import iiwaPy3
from MATLABToolBoxStart import MATLABToolBoxStart

from python_client.EMG_trigger import EmgTrigger

impedance_help = False
emg_triggering = True

emg_threshold = 65

'''
Bryce right RF threshold is 125
Rachel left RF threshold is 65
'''

emg_local_host = True

if emg_local_host:
    # EMG Localhost IP
    emg_server_ip = "127.0.0.1"
else:
    # EMG IP
    emg_server_ip = "172.16.207.72"
emg_port = 9220

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

    if emg_triggering:
        emg = EmgTrigger(emg_server_ip, emg_port)
        emg.get_emg_channel()

    armed = False
    fired = False
    while True:
        trigger = False
        if emg_triggering:
            samples = emg.sample_get()

        if keyboard.is_pressed('a'):
            armed = True
        if keyboard.is_pressed('d'):
            armed =False

        if armed and emg_triggering:
            for ch in samples['channels']:
                trigger = emg.emg_trigger_boolean(ch, emg_threshold)
                print(trigger)
        if keyboard.is_pressed('shift') or trigger and not fired:
            fired = True
            vel = [0.4]
            iiwa.movePTPJointSpace(available_pos['helping'], vel)
            if run >= 1:
                iiwa.realTime_startImpedanceJoints(weightOfTool, cOMx, cOMy, cOMz, cStiness, rStifness, nStifness)
                run += 1
                iiwa.realTime_stopDirectServoJoints()
            iiwa.realTime_startImpedanceJoints(weightOfTool, cOMx, cOMy, cOMz, cStiness, rStifness, nStifness)
            run += 1
            time.sleep(0.5)

            step = 45
            while step <= 60:
                step_rad = math.radians(step)
                newPos = available_pos['helping']
                newPos[5] = step_rad
                iiwa.sendJointsPositions(newPos)
                step += 1
            while step >= 45:
                step_rad = math.radians(step)
                newPos = available_pos['helping']
                newPos[5] = step_rad
                iiwa.sendJointsPositions(newPos)
                step -= 1

            time.sleep(1)
            while True:
                deflection = iiwa.getJointsPos()[1]
                if deflection < math.radians(-91) or keyboard.is_pressed('shift'):
                    if impedance_help:
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
                    break

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
            iiwa.movePTPJointSpace(available_pos['curled away'], [0.4])
            break
        else:
            fired = False
        time.sleep(0.2)

except Exception as e:
    print(f"An error occurred: {e}")

finally:
    iiwa.close()
