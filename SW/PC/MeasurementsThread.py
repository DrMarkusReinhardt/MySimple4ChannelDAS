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
import serial
import time
import PyCmdMessenger
from serial.tools import list_ports
from PyQt5.Qt import *
from PyQt5.QtCore import *
   
class MeasurementsThread(QThread):
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
        # make sure this baudrate matches the baudrate on the Arduino
        self.running = False
        self.baud = 9600
        self.sem = QSemaphore(1)
        print(self.sem)
        # the following enum sequence has to correspond to the sequence of the enum in the Arduino part
        self.commands = [['commError',''],
                         ['comment',''],
                         ['sendAcknowledge','s'],
                         ['areYouReady',''],
                         ['error',''],
                         ['askUsIfReady',''],
                         ['youAreReady',''],
                         ['sendMeasuredVoltage1',''],
                         ['sendMeasuredVoltage2',''],
                         ['sendMeasuredVoltage3',''],
                         ['sendMeasuredVoltage4',''],
                         ['turnOnMeasurements',''],
                         ['turnOffMeasurements',''],
                         ['resetMeasurements',''],
                         ['floatValue','f'],
                         ['int16Value','i']]
        try:
            # try to open the relevant usb port
            # self.port_name = self.list_usb_ports()[3][0]
            # self.port_name = '/dev/cu.wchusbserial1410'
            self.port_name = '/dev/ttyUSB0'
            # print('Serial port name = ',self.port_name)
            self.serial_port = serial.Serial(self.port_name, self.baud, timeout=0)
        except (serial.SerialException, IndexError):
            raise SystemExit('Could not open serial port.')
        else:
            print('Serial port',self.port_name,' sucessfully opened.\n')

            # setup the cmdMessenger
            print('Set-up PyCmdMessenger on serial port')
            # Initialize an ArduinoBoard instance.  This is where you specify baud rate and
            # serial timeout.  If you are using a non ATmega328 board, you might also need
            # to set the data sizes (bytes for integers, longs, floats, and doubles).  
            self.arduino = PyCmdMessenger.ArduinoBoard(self.port_name,baud_rate=9600)
            # Initialize the messenger
            self.messenger  = PyCmdMessenger.CmdMessenger(self.arduino,self.commands)
            
    def printReceiveMsg(self):
        ReceiveMsg = self.messenger.receive()
        print('ReceiveMsg = ')
        print(ReceiveMsg)		
        
    def list_usb_ports(self):
        """ Use the grep generator to get a list of all USB ports.
        """
        # ports = [port for port in list_ports.grep('cu')]
        ports = [port for port in list_ports.grep('ttyUSB')]
        return ports

    def on_error(self, received_command, *args, **kwargs):
        """Callback function to handle errors
        """
        print(('Error:', args[0][0]))
       
    def GetMeasuredValues(self):
        # print("GetMeasuredValues")
        try:
            if self.sem.available() > 0:
                self.sem.acquire(1)
                self.messenger.send('sendMeasuredValues')
                time.sleep(0.1)
                ReceiveMsg = self.messenger.receive()
                self.sem.release(1)
                return ReceiveMsg[1][0]
            else:
                ReceiveMsg = ('measure value skipped', [0.0,0.0])
                return ReceiveMsg[1][0]
        except TypeError:
            print("measured value receive error")
            ReceiveMsg = self.messenger.receive()
            ReceiveMsg = ('measured value receive error', [0.0,0.0])
            return ReceiveMsg[1][0]
        
    def TurnOnMeasurements(self):
        if self.sem.available() > 0:
            self.sem.acquire(1)
            self.messenger.send('turnOnMeasurements')
            time.sleep(0.1)
            ReceiveMsg = self.messenger.receive()
            print("TurnOnMeasurements: ",ReceiveMsg)
            self.sem.release(1)
        else:
            print("error: could not turn on the measurements")

    def TurnOffMeasurements(self):
        if self.sem.available() > 0:
            self.sem.acquire(1)
            self.messenger.send('turnOffMeasurements')
            time.sleep(0.1)
            ReceiveMsg = self.messenger.receive()
            print("TurnOffMeasurements: ",ReceiveMsg)
            self.sem.release(1)
        else:
            print("error: could not turn off the measurements")
        
    def ResetMeasurements(self):
        if self.sem.available() > 0:
            self.sem.acquire(1)
            self.messenger.send('resetMeasurements')   
            time.sleep(0.1)
            ReceiveMsg = self.messenger.receive()
            print("ResetMeasurements: ",ReceiveMsg)
            self.sem.release(1)
        else:
            print("error: could not reset the measurements")
                
    def wrapper(self, command):
        # ser = serial.Serial('/dev/cu.wchusbserial1410', 9600, timeout=1, rtscts=1)
        ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=1, rtscts=1)
        command = command +'\r\n'
        ser.write(command.encode())
        s = ser.read(100)
        print(s)
        ser.close()
