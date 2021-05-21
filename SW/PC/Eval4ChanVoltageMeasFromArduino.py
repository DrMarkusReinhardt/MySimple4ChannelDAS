#!/usr/local/bin/python3
# -*- coding:utf-8 -*-
"""
Project MySimple4ChannelDAS

PC program to evaluate 4-channel voltage measurements from an 4-channel ADC connected to an Arduino Uno board
(suited for Max OSX, Windows, Linux)

Created 19th May 2021

Last change on 21st May 2021

@author: Dr. Markus Reinhardt

"""
from __future__ import print_function
import sys
# import ntpath
# import os
from PyQt5.Qt import *
from PyQt5.QtCore import *
from MeasurementsThread import *
from VoltageMeasurement import VoltageMeasurementsWindow

try:
    from PyQt5.QtCore import QString
except ImportError:
    # we are using Python3 so QString is not defined
    QString = type("")

class MainWindow(QMainWindow):
    def __init__(self, *rest):
        QMainWindow.__init__(self)

        # set the command message interface
        self.msgIF = MsgInterface()
        
        # create frame
        frame = QFrame()
        frame.setStyleSheet("QFrame { background-color: white }")
        frameLayout = QGridLayout(frame)
        
        # create four voltage displays
        voltageMeasurementDisplay1 = VoltageMeasurementsWindow("Channel1: ")
        voltageMeasurementDisplay2 = VoltageMeasurementsWindow("Channel2: ")
        voltageMeasurementDisplay3 = VoltageMeasurementsWindow("Channel3: ")
        voltageMeasurementDisplay4 = VoltageMeasurementsWindow("Channel4: ")

        # the on/off control
        # on / off control values for the measurements
        self.OnOffControlValueMeasurements = 1
        self.createOnOffControlMeasurements()

        # the file selection and evaluation group
        self.createConfigFileGroupBox()

        # the status message box
        self.createStatusMsgBox()

        # - the manufacturer label
        self.createManufacturerLabel()
        
        # create the main (top level) layout
        frameLayout.addWidget(voltageMeasurementDisplay1.voltagePlotGroupBox,0,0,1,3)
        frameLayout.addWidget(voltageMeasurementDisplay2.voltagePlotGroupBox,0,3,1,3)
        frameLayout.addWidget(voltageMeasurementDisplay3.voltagePlotGroupBox,1,0,1,3)
        frameLayout.addWidget(voltageMeasurementDisplay4.voltagePlotGroupBox,1,3,1,3)
        frameLayout.addWidget(self.onOffCtrlGroupboxMeasurements,2,0)
        frameLayout.addWidget(self.configFileGroupBox,2,1)
        frameLayout.addWidget(self.statusGroupBox,2,2,1,3)
        frameLayout.addWidget(self.manufacturerGroupbox,2,5)
        
        # set the central widget
        self.setCentralWidget(frame)

        # set window title
        self.setWindowTitle(self.tr("4-Channel Voltage Measurements"))
        
        # Start the measurement thread
        periodSec = 2.0
        measurementSlot = self.handleMeasurements;
        measurementsThreadObj = MeasurementsThread(measurementSlot,periodSec)
        measurementsThreadObj.start()
        
    def createManufacturerLabel(self):
        self.manufacturerGroupbox = QGroupBox(self.tr("Made by"))
        self.manufacturerGroupbox.setStyleSheet(self.getStyleSheet("./styles_grey.qss")) 
        titleFont = QFont()
        titleFont.setFamily("Arial")
        titleFont.setFixedPitch(True)
        titleFont.setPointSize(14)
        self.manufacturerGroupbox.setFont(titleFont)

        self.manufacturerLayout = QVBoxLayout()
        # self.manufacturerGroupbox.setFixedSize(200, 50)
        # the label
        self.manufacturerLabel = QLabel()
        font = QFont()
        font.setFamily("Tokyo")
        font.setPointSize(10)
        font.setWeight(QFont.Bold)
        font.setItalic(True)
        self.manufacturerLabel.setFont(font)
        frameStyle = QFrame.Sunken | QFrame.Panel
        self.manufacturerLabel.setFrameStyle(frameStyle)
        self.manufacturerLabel.setWordWrap(True)
        self.manufacturerLabel.setText(self.tr("Dr. Markus Reinhardt\nHoMeR "))
        self.manufacturerLabel.setFixedSize(200,50)

        self.manufacturerLayout.addWidget(self.manufacturerLabel)
        self.manufacturerGroupbox.setLayout(self.manufacturerLayout)

    def createConfigFileGroupBox(self):
        self.configFileGroupBox = QGroupBox(self.tr('Measurements Config.'))
        self.configFileGroupBox.setStyleSheet(self.getStyleSheet("./styles_lightgrey.qss")) 
        titleFont = QFont()
        titleFont.setFamily("Arial")
        titleFont.setFixedPitch(True)
        titleFont.setPointSize(14)
        self.configFileGroupBox.setFont(titleFont)
        
        # the label to display the selected file
        frameStyle = QFrame.Sunken | QFrame.Panel
        self.openFileNameLabel = QLabel()
        self.openFileNameLabel.setFixedSize(200, 30)
        self.openFileNameLabel.setFrameStyle(frameStyle)

        # the push button to call the file selection dialog
        self.openFileNameButton = QPushButton(self.tr("Select Config. File"))
        self.openFileNameButton.setFixedSize(200, 30)
        self.openFileNameButton.setStyleSheet("QPushButton { background-color: yellow }")

        # define the widget
        layout = QVBoxLayout()
        layout.addWidget(self.openFileNameButton)
        layout.addWidget(self.openFileNameLabel)

        # assign the layout to the group box
        self.configFileGroupBox.setLayout(layout)

        # define the connection between labels and functions
        self.openFileNameButton.clicked.connect(self.setOpenFileName)

    def createOnOffControlMeasurements(self):
        self.onOffCtrlGroupboxMeasurements = QGroupBox(self.tr("Measurements Control"))
        self.onOffCtrlGroupboxMeasurements.setStyleSheet(self.getStyleSheet("./styles_grey.qss")) 
        titleFont = QFont()
        titleFont.setFamily("Arial")
        titleFont.setFixedPitch(True)
        titleFont.setPointSize(14)
        self.onOffCtrlGroupboxMeasurements.setFont(titleFont)
        self.onOffCtrlGroupboxMeasurements.setFixedSize(220, 180)
       
        # the state label
        self.onOffControlLabelMeasurements = QLabel()
        self.onOffControlLabelMeasurements.setFixedSize(200, 30)
        #frameStyle = QFrame.Sunken | QFrame.Panel
        frameStyle =  QFrame.Panel
        self.onOffControlLabelMeasurements.setFrameStyle(frameStyle)
        self.onOffControlLabelMeasurements.setText(self.tr("Measurements are <b>ON</b>"))
        
        # the on/off push button
        self.onOffControlButtonMeasurements = QPushButton(self.tr("Measurements On/Off"))
        self.onOffControlButtonMeasurements.setFixedSize(200, 30)
        self.onOffControlButtonMeasurements.clicked.connect(self.OnOffGenMeasurements)
        self.onOffControlButtonMeasurements.setStyleSheet("QPushButton { background-color: yellow }")
        
        # the reset push button
        self.resetControlButtonMeasurements = QPushButton(self.tr("Reset Measurements"))
        self.resetControlButtonMeasurements.setFixedSize(200, 30)
        self.resetControlButtonMeasurements.clicked.connect(self.resetGenMeasurements)
        self.resetControlButtonMeasurements.setStyleSheet("QPushButton { background-color: red }")

        # add all widgets to the layout
        self.onOffControlLayoutMeasurements = QVBoxLayout()
        # self.onOffControlLayoutMeasurements.addWidget(self.parameterUpdateButtonMeasurements)
 
        self.onOffControlLayoutMeasurements.addWidget(self.onOffControlButtonMeasurements)
        self.onOffControlLayoutMeasurements.addWidget(self.onOffControlLabelMeasurements)
        self.onOffControlLayoutMeasurements.addWidget(self.resetControlButtonMeasurements)
        self.onOffCtrlGroupboxMeasurements.setLayout(self.onOffControlLayoutMeasurements)

    def createStatusMsgBox(self):
        self.statusGroupBox = QGroupBox(self.tr('System Status'))
        self.statusGroupBox.setFixedSize(780, 180)
        self.statusGroupBox.setStyleSheet(self.getStyleSheet("./styles_lightgrey.qss")) 
        titleFont = QFont()
        titleFont.setFamily("Arial")
        titleFont.setFixedPitch(True)
        titleFont.setPointSize(14)
        self.statusGroupBox.setFont(titleFont)
        
        # the label to display the status
        labelFont = QFont()
        labelFont.setFamily("Arial")
        labelFont.setFixedPitch(True)
        labelFont.setPointSize(14)
        frameStyle = QFrame.Sunken | QFrame.Panel
        self.statusLabel = QLabel()
        self.statusLabel.setFrameStyle(frameStyle)
        self.statusLabel.setFixedSize(400, 40)
        self.statusLabel.setText("running")
        self.statusLabel.setFont(labelFont)
        
        # define the widget
        layout = QHBoxLayout()
        layout.addWidget(self.statusLabel)

        # assign the layout to the group box
        self.statusGroupBox.setLayout(layout) 

    def setOpenFileName(self):
        # selectedFilter = QString()
        fileName = QFileDialog.getOpenFileName(self,
                self.tr("Select Control File"),
                self.openFileNameLabel.text(),
                self.tr("Control File (*.ctrl)"))
        print("filename =", fileName)
        if (len(fileName[0]) > 0):
            self.openFileNameLabel.setText(ntpath.basename(fileName[0]))
            self.CtrlFile = str(ntpath.basename(fileName[0]))
            self.CtrlFileGiven = True
        else:
            self.CtrlFileGiven = False
        
    def getStyleSheet(self, path):
        f = QFile(path)
        f.open(QFile.ReadOnly | QFile.Text)
        stylesheet = QTextStream(f).readAll()
        f.close()
        return stylesheet 

    def handleMeasurements(self):
        if (self.OnOffControlValueMeasurements == 1):
            # request voltage measurements from the voltage sensor and update the display
            try:
                measuredVoltages = self.msgIF.GetMeasuredValues()
                print("measuredVoltages =", measuredVoltages )
                
                # valid measurement received   --> update plot and displays
                self.actualVoltages = measuredVoltages
                self.noValidMeasurements = self.noValidMeasurements + 1
                if (self.noValidMeasurements > self.maxArraySize):
                    self.noValidMeasurements = self.maxArraySize
                self.actualVoltageEdit.setText("{:2.2f}".format(measuredVoltages))
                self.updateMeasurementsArray(measuredVoltages)
                self.updatePlot()
                self.updateMeanVoltage()
            except TypeError:
                print("failed to get correct measurements")

    def OnOffGenMeasurements(self):
        if self.OnOffControlValueMeasurements == 1:
            self.OnOffControlValueMeasurements = 0
            self.onOffControlLabelMeasurements.setText(self.tr("Measurements are <b>OFF</b>"))
            self.msgIF.TurnOffMeasurements()
            self.statusLabel.setText("stopped")
        else:
            self.OnOffControlValueMeasurements = 1
            self.onOffControlLabelMeasurements.setText(self.tr("Measurements are <b>ON</b>"))
            self.msgIF.TurnOnMeasurements()
            self.statusLabel.setText("running")
 
    def resetGenMeasurements(self):
        # set the default state (on)
        self.OnOffControlValueMeasurements = 1
        self.onOffControlLabelMeasurements.setText(self.tr("Measurements are <b>ON</b>"))
        self.msgIF.ResetMeasurements()
        self.initMeasurementsArray()
 
if __name__ == '__main__':
    a = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    window.resize(1000, 1000)
    window.show()
    a.exec_()
