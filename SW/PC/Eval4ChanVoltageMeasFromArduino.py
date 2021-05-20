#!/usr/local/bin/python3
# -*- coding:utf-8 -*-
"""
Project MySimple4ChannelDAS

PC program to evaluate 4-channel voltage measurements from an 4-channel ADC connected to an Arduino Uno board
(suited for Max OSX, Windows, Linux)

Created 19th May 2021

Last change on 19th May 2021

@author: Dr. Markus Reinhardt

"""
from __future__ import print_function
import sys
import ntpath
# import os
import numpy as np
import matplotlib
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
matplotlib.use('Qt5Agg')
from PyQt5.Qt import *
from PyQt5.QtCore import *
from MeasurementsThread import *

try:
    from PyQt5.QtCore import QString
except ImportError:
    # we are using Python3 so QString is not defined
    QString = type("")

class MplCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(MplCanvas, self).__init__(fig)
        
class VoltageMeasurementWidget(QWidget):
    def __init__(self, parent=None, width=5, height=4, dpi=100):


class VoltageMeasurementsCtrlWindow(QMainWindow):
    def __init__(self, *rest):
        QMainWindow.__init__(self)
        
        # set the command message interface
        self.msgIF = MsgInterface()
                                
        # on / off control values for the measurements
        self.OnOffControlValueMeasurements = 1
        
        # measured values of voltage (actual and mean)
        self.actualTemperature = 21.0
        self.meanTemperature = 21.0
        self.noValidMeasurements = 0
        
        # array of measurements
        self.initMeasurementsArray()  
        
        # Start the measurement thread
        periodSec = 2.0
        measurementSlot = self.handleMeasurements;
        measurementsThreadObj = MeasurementsThread(measurementSlot,periodSec)
        measurementsThreadObj.start()
       
        # create central widget
        self.CreateMainWidget()
                
    def CreateMainWidget(self):
        frame = QFrame()
        frame.setStyleSheet("QFrame { background-color: white }")
        frameLayout = QGridLayout(frame)
        
        # create the plot widget
        self.createPlotWidget1()
        
        # the status message box
        self.createStatusMsgBox()
        
        # create the mean temperature display
        self.createMeanTemperatureDisplay()

        # the file selection and evaluation group
        self.createConfigFileGroupBox()

        # the on/off control
        self.createOnOffControlMeasurements()

        # - the manufacturer label
        self.createManufacturerLabel()
        
        # create the main (top level) layout
        frameLayout.addWidget(self.temperaturePlotGroupBox,0,0)
        frameLayout.addWidget(self.onOffCtrlGroupboxMeasurements, 0, 1)
        frameLayout.addWidget(self.meanTemperatureGroupBox,1,0)
        frameLayout.addWidget(self.configFileGroupBox, 1, 1)
        frameLayout.addWidget(self.statusGroupBox,2,0)
        frameLayout.addWidget(self.manufacturerGroupbox, 2, 1)
        
        # set the central widget
        self.setCentralWidget(frame)

        # set window title
        self.setWindowTitle(self.tr("Temperature measurements with DS18B20 V0.1"))
        
    def getStyleSheet(self, path):
        f = QFile(path)
        f.open(QFile.ReadOnly | QFile.Text)
        stylesheet = QTextStream(f).readAll()
        f.close()
        return stylesheet    
       
    def retFloatFromValueString(valueString):
        floatValue = float(valueString)
        return floatValue
 
    def createPlotWidget1(self):
        self.temperaturePlotGroupBox = QGroupBox(self.tr(''))
        self.temperaturePlotGroupBox.setStyleSheet(self.getStyleSheet("./styles_lightgrey.qss")) 
        titleFont = QFont()
        titleFont.setFamily("Arial")
        titleFont.setFixedPitch(True)
        titleFont.setPointSize(25)
        self.temperaturePlotGroupBox.setFont(titleFont)
        
        self.plotCanvas =  MplCanvas(self, width=5, height=5, dpi=100)
        self.plotCanvas.axes.plot(self.measuredTemperatureArray)
        self.plotCanvas.axes.set_xlabel('discrete time instance')
        self.plotCanvas.axes.set_ylabel('temperature / °C')
        self.plotCanvas.axes.grid()
        
        # create the layout and add the plot widget
        self.temperaturePlotVBox = QVBoxLayout()
        self.temperaturePlotVBox.addWidget(self.plotCanvas)
        
        # set the font to be used later
        labelFont = QFont()
        labelFont.setFamily("Arial")
        labelFont.setFixedPitch(True)
        labelFont.setPointSize(20)
        
        # create the label and edit for the mean temperature
        self.actualTemperatureLabel = QLabel()
        self.actualTemperatureLabel.setStyleSheet("QLabel { background-color: lightgrey;  }")
        self.actualTemperatureLabel.setText('Actual temperature / °C: ')
        self.actualTemperatureLabel.setFixedSize(340, 30)
        self.actualTemperatureLabel.setAlignment(Qt.AlignLeft)
        self.actualTemperatureLabel.setFont(labelFont)

        # font for the measurement displays
        displayFont = QFont()
        displayFont.setFamily("Arial")
        displayFont.setFixedPitch(True)
        displayFont.setPointSize(40)

        # mean temperature display edit
        self.actualTemperatureEdit = QLineEdit()
        self.actualTemperatureEdit.setText("{:2.2f}".format(self.actualTemperature))
        self.actualTemperatureEdit.setFont(displayFont)
        self.actualTemperatureEdit.setFixedSize(140, 100)
        self.actualTemperatureEdit.setAlignment(Qt.AlignRight)
        self.actualTemperatureEdit.setReadOnly(True)
        
        # create the HBox for the actual temperature display
        self.actualTemperatureHBox = QHBoxLayout()
        # add the widgets
        self.actualTemperatureHBox.addWidget(self.actualTemperatureLabel)
        self.actualTemperatureHBox.addWidget(self.actualTemperatureEdit)
        
        # add the mean temperature display HBox
        self.temperaturePlotVBox.addLayout(self.actualTemperatureHBox)
        
        # add the layout to the measurement box
        self.temperaturePlotGroupBox.setLayout(self.temperaturePlotVBox)
        
    
    def updatePlot(self):
        self.plotCanvas.axes.clear()
        self.plotCanvas.axes.plot(self.measuredTemperatureArray)
        self.plotCanvas.axes.grid()
        self.plotCanvas.axes.set_xlabel('discrete time instance')
        self.plotCanvas.axes.set_ylabel('temperature / °C')
        # update the plot
        self.plotCanvas.draw()
        
    def updateMeanTemperature(self):
        # calculate the mean temperature value
        self.meanTemperature = np.mean(self.measuredTemperatureArray[0:self.noValidMeasurements])
        # update the mean temperature edit
        self.meanTemperatureEdit.setText("{:2.2f}".format(self.meanTemperature))        
        
    def updateMeasurementsArray(self, temperatureValue):
        self.measuredTemperatureArray[self.arrayIndex] = temperatureValue
        self.arrayIndex = self.arrayIndex + 1
        if (self.arrayIndex > self.maxArraySize) :
            self.arrayIndex = 0
    
    def initMeasurementsArray(self):
        self.maxArraySize = 100
        self.measuredTemperatureArray = 25.0*np.ones(self.maxArraySize+1)
        self.arrayIndex = 0
        self.noValidMeasurements = 0
         
    def createMeanTemperatureDisplay(self):
    ################### Measurement widgets ##############################################
        self.meanTemperatureGroupBox = QGroupBox(self.tr('Mean temperature'))
        self.meanTemperatureGroupBox.setStyleSheet(self.getStyleSheet("./styles_grey.qss")) 
        titleFont = QFont()
        titleFont.setFamily("Arial")
        titleFont.setFixedPitch(True)
        titleFont.setPointSize(14)
        self.meanTemperatureGroupBox.setFont(titleFont)
        
        # set the font to be used later
        font = QFont()
        font.setFamily("Arial")
        font.setFixedPitch(True)
        font.setPointSize(20)

        # font for the measurement displays
        displayFont = QFont()
        displayFont.setFamily("Arial")
        displayFont.setFixedPitch(True)
        displayFont.setPointSize(40)
        
        #### temperature measurement widgets ###
        # temperature measurement widgets horizontally stacked
        self.meanTemperatureHBox = QHBoxLayout()
        
        # mean temperature display label
        self.meanTemperatureLabel = QLabel()
        self.meanTemperatureLabel.setStyleSheet("QLabel { background-color: grey;  }")
        self.meanTemperatureLabel.setText('Mean temperature / °C: ')
        self.meanTemperatureLabel.setFixedSize(340, 30)
        self.meanTemperatureLabel.setAlignment(Qt.AlignLeft)
        self.meanTemperatureLabel.setFont(font)
        
        # mean temperature display edit
        self.meanTemperatureEdit = QLineEdit()
        self.meanTemperatureEdit.setText("{:2.2f}".format(self.meanTemperature))
        self.meanTemperatureEdit.setFont(displayFont)
        self.meanTemperatureEdit.setFixedSize(140, 100)
        self.meanTemperatureEdit.setAlignment(Qt.AlignRight)
        self.meanTemperatureEdit.setReadOnly(True)

        # add the widgets
        self.meanTemperatureHBox.addWidget(self.meanTemperatureLabel)
        self.meanTemperatureHBox.addWidget(self.meanTemperatureEdit)

        # add the layout to the measurement box
        self.meanTemperatureGroupBox.setLayout(self.meanTemperatureHBox)

    def createStatusMsgBox(self):
        self.statusGroupBox = QGroupBox(self.tr('System Status'))
        self.statusGroupBox.setFixedSize(780, 100)
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
        self.onOffCtrlGroupboxMeasurements.setFixedSize(220, 400)
       
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
        self.manufacturerLabel.setFixedSize(200, 50)

        self.manufacturerLayout.addWidget(self.manufacturerLabel)
        self.manufacturerGroupbox.setLayout(self.manufacturerLayout)
        
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
        
    def handleMeasurements(self):
        if (self.OnOffControlValueMeasurements == 1):
            # request temperature measurements from the temperature sensor and update the display
            try:
                measuredTemperature = self.msgIF.GetMeasuredValue()
                print("measuredTemperature =", measuredTemperature )
                
                # valid measurement received   --> update plot and displays
                self.actualTemperature = measuredTemperature
                self.noValidMeasurements = self.noValidMeasurements + 1
                if (self.noValidMeasurements > self.maxArraySize):
                    self.noValidMeasurements = self.maxArraySize
                self.actualTemperatureEdit.setText("{:2.2f}".format(measuredTemperature))
                self.updateMeasurementsArray(measuredTemperature)
                self.updatePlot()
                self.updateMeanTemperature()
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
    window = TemperatureMeasurementsCtrlWindow()
    # window.DemoPlot()
    window.resize(1000, 600)
    window.show()
    a.exec_()
