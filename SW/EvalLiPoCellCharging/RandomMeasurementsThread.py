#!/usr/local/bin/python3
# -*- coding:utf-8 -*-
"""
Measurements thread to evaluate temperature measurements from a sensor connected to an Arduino board
(suited for Max OSX, Windows, Linux)

Created 29th March 2021

Last change on Created 30th March 2021

@author: Dr. Markus Reinhardt

"""
from __future__ import print_function
# import os
# import time
import random
from PyQt5.Qt import *
from PyQt5.QtCore import *
   
class RandomMeasurementsThread(QThread):
    def __init__(self, measurementHandler,periodSec):
        QThread.__init__(self)
        self.measurementHandler=measurementHandler
        self.periodSec = periodSec

    def run(self):
        activateMeasurementTimer(self.measurementHandler,self.periodSec)
        self.exec_()

timers = []

def activateMeasurementTimer(measurementHandler,periodSec):
    print("Measurement thread started")
    timer = QTimer()
    timer.timeout.connect(measurementHandler)
    timer.start(1000*periodSec)
    timers.append(timer)

class MsgInterface(object):
    def __init__(self):
        self.running = False
    
    def GetMeasuredVoltageValue(self):
        # print("GetMeasuredValues")
        measuredValue = 4.1 + 0.1*random.random()
        return measuredValue;

    def GetMeasuredCurrentValue(self):
        # print("GetMeasuredValues")
        measuredValue = 0.9 + 0.1*random.random()
        return measuredValue;
        
    def GetMeasuredCapacityValue(self):
        # print("GetMeasuredValues")
        measuredValue = 3.8 + 0.1*random.random()
        return measuredValue;
        
    def GetMeasuredEnergyValue(self):
        # print("GetMeasuredValues")
        measuredValue = 2.5+ 0.1*random.random()
        return measuredValue;
