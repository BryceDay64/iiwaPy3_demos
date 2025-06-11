import math
import time
import keyboard
import numpy as np
import requests

from iiwaPy3 import iiwaPy3
from MATLABToolBoxStart import MATLABToolBoxStart

local_host = False

if local_host:
    # EMG Localhost IP and Port
    EMG_IP = "127.0.0.1"
    EMG_Port = 9220
else:
    # EMG IP and port
    EMG_IP = "172.16.207.72"
    EMG_Port = 9220



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
            time.sleep(0.5)

            print ('here')
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

except Exception as e:
    print(f"An error occurred: {e}")

finally:
    iiwa.close()

'''
import requests
import time
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# Configuration
SERVER_IP = "172.16.207.72"
PORT = 9220
SERVER_URL = f"http://{SERVER_IP}:{PORT}"

HEADERS_URL = f"{SERVER_URL}/headers"
SAMPLES_URL = f"{SERVER_URL}/samples"
ENABLE_URL = f"{SERVER_URL}/enable/"
DISABLE_URL = f"{SERVER_URL}/disable/"

# Step 1: Get available channels
response = requests.get(HEADERS_URL, timeout=5)
channels = response.json()["headers"]

# Step 2: Select EMG channels (or prompt selection)
print("Available Channels:")
for i, ch in enumerate(channels):
    print(f"[{i}] {ch['name']} ({ch['type']})")

selected_index = int(input("Enter channel index to stream: "))
channel = channels[selected_index]
channel_index = channel["index"]
sample_rate = channel["samplerate"]
channel_type = channel["type"]

# Step 3: Enable the selected channel and disable all others
requests.get(f"{DISABLE_URL}all")
requests.get(f"{ENABLE_URL}{channel_index}")

# Step 4: Prepare plot
buffer_size = int(sample_rate * 10)
data_buffer = [0] * buffer_size

fig, ax = plt.subplots()
line, = ax.plot(data_buffer)
ax.set_ylim(-3000, 3000)  # adjust as needed
ax.set_title(f"Streaming: {channel['name']} ({channel_type})")

def update_plot(frame):
    global data_buffer
    try:
        samples = requests.get(SAMPLES_URL, timeout=5).json()
        for ch in samples['channels']:
            if ch['index'] == channel_index:
                data_buffer = data_buffer[len(ch['samples']):] + ch['samples']
                break
        line.set_ydata(data_buffer)
    except Exception as e:
        print("Stream error:", e)
    return line,

ani = FuncAnimation(fig, update_plot, interval=200)
plt.show()
'''
