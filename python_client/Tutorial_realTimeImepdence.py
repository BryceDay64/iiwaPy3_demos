# -*- coding: utf-8 -*-
"""
About the script:
An exmple on controlling KUKA iiwa robot from
Python3 using the iiwaPy3 class

Created on Tue Oct  1 11:56:31 2019
Modified on 3rd-Jan-2021

@author: Mohammad Safeea

Test script of realtime impedance mode
plot joints torques feedback while controlling the robot

"""

import math
import time
from datetime import datetime
from iiwaPy3 import iiwaPy3

from MATLABToolBoxStart import MATLABToolBoxStart

# KUKA iiwa robot IP and port
#KUKA_IP = "192.168.0.50"  # Replace with actual robot IP KUKA 141
KUKA_IP = "192.168.8.147"  # Replace with actual robot IP KUKA 71
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



def getSecs():
    t = datetime.now()
    sec = ((t.day * 24 + t.hour) * 60 + t.minute) * 60 + t.second + t.microsecond / 1000000.0
    return sec

# read some data from the robot
try:
    # Move to an initial position    
    jPos = [0, 0, 0, -math.pi / 2, 0, math.pi / 2, 0];
    vRel = [0.1]
    iiwa.movePTPJointSpace(jPos, vRel)

    # define some variables:
    counter = 0  # count the number of iterations
    index = 0  # index (the first joint angle)
    w = 0.6  # angular velocity of the motion
    theta = 0  # angular command for the first joint
    interval = 4 * math.pi  # 2*pi
    a = math.pi / 6  # amplitude of the motion
    # Read current joints positions
    jpos = iiwa.getJointsPos()
    jpos0_6 = jpos[index]
    print("Current joints positions")
    print(jpos)
    # Define the load data
    # got this data from the controller
    weightOfTool = 1.73  # 1 kg
    cOMx = 0.01554
    cOMy = 0.01906
    cOMz = 0.05352

    cStiness = 2500
    rStifness = 80
    nStifness = 50

    iiwa.realTime_startImpedanceJoints(weightOfTool, cOMx, cOMy, cOMz, cStiness, rStifness, nStifness)
    iiwa.realTime_stopDirectServoJoints()
    iiwa.realTime_startImpedanceJoints(weightOfTool, cOMx, cOMy, cOMz, cStiness, rStifness, nStifness)

    t0 = getSecs()
    t_0 = getSecs()
    while theta < interval:
        theta = w * (getSecs() - t0)
        jpos[index] = jpos0_6 + a * math.sin(theta)

        if (getSecs() - t_0) > 0.002:
            print(jpos)
            iiwa.sendJointsPositions(jpos)
            t_0 = getSecs()
            counter = counter + 1
    print('end before start')
    deltat = getSecs() - t0
    # movig point to point again
    iiwa.realTime_stopDirectServoJoints()
    print('Realtime control turned off')
    time.sleep(0.5)
    jPos = [0, 0, 0, -math.pi / 2, 0, math.pi / 2, 0]
    print('Moving in joint space to position')
    print(jPos)
    vRel = [0.1]
    iiwa.movePTPJointSpace(jPos, vRel)

except:
    print('an error happened')

iiwa.close()
print('Socket update freq for the ServoMotion')
print(counter / deltat)
