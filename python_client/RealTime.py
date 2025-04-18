# -*- coding: utf-8 -*-
"""
Created on Wed Mar 28 16:12:34 2018
Updated 3rd-Jan-2021

@author: Mohammad SAFEEA
"""
# from GeneralPurpose import getDoubleFromString
import time


class RealTime:

    def __init__(self, mysoc):
        self.mysoc = mysoc

    def send(self, data):
        data = data + '\n'
        self.mysoc.send(data)
        self.mysoc.receive()

    def realTime_startDirectServoJoints(self):
        theCommand = 'startDirectServoJoints'
        self.send(theCommand)
        time.sleep(0.3)

    def realTime_stopDirectServoJoints(self):
        theCommand = 'stopDirectServoJoints'
        self.send(theCommand)
        time.sleep(0.3)

    def realTime_startDirectServoCartesian(self):
        theCommand = 'stDcEEf_'
        self.send(theCommand)
        time.sleep(0.3)

    def realTime_stopDirectServoCartesian(self):
        theCommand = 'stopDirectServoJoints'
        self.send(theCommand)
        time.sleep(0.3)

    def realTime_startImpedanceJoints(self, weightOfTool, cOMx, cOMy, cOMz, cStiness, rStifness, nStifness):
        theCommand = 'startSmartImpedneceJoints' # typo but modified to match the matlab server java script
        theCommand = theCommand + '_' + str(weightOfTool)
        theCommand = theCommand + '_' + str(cOMx)
        theCommand = theCommand + '_' + str(cOMy)
        theCommand = theCommand + '_' + str(cOMz)
        theCommand = theCommand + '_' + str(cStiness)
        theCommand = theCommand + '_' + str(rStifness)
        theCommand = theCommand + '_' + str(nStifness) + '_'
        self.send(theCommand)
        print('sent')
        time.sleep(0.3)

    def realTime_stopImpedanceJoints(self):
        theCommand = 'stopDirectServoJoints'
        self.send(theCommand)
        time.sleep(0.3)
