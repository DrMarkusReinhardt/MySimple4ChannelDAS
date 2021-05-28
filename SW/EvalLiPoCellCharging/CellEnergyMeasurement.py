"""
CellEnergyMeasurement.py

cell energy measurement display for a single channel
(suited for Max OSX, Windows, Linux)

Created 28th May 2021

Last change on 28th May 2021

@author: Dr. Markus Reinhardt

"""
import numpy as np
import matplotlib
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
matplotlib.use('Qt5Agg')
from PyQt5.Qt import *
from PyQt5.QtCore import *
from RandomMeasurementsThread import *

class MplCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=7, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(MplCanvas, self).__init__(fig)

class CellEnergyMeasurementsWindow(QWidget):
    def __init__(self, titleString):
        QWidget.__init__(self)
        
        # set the command message interface
        # self.msgIF = MsgInterface()
                                
        
        # measured values of energy (actual and mean)
        self.actualEnergy = 0.0
        self.meanEnergy = 0.0
        self.noValidMeasurements = 0
        
        # array of measurements
        self.initMeasurementsArray() 
        
        # create the plot widget
        self.createPlotWidget(titleString)
        print("plot widget created")
        self.updatePlot(titleString)
        
        # Start the measurement thread
        # periodSec = 5.0
        # measurementSlot = self.handleMeasurements;
        # measurementsThreadObj = MeasurementsThread(measurementSlot,periodSec)
        # measurementsThreadObj.start()
        

    def createPlotWidget(self,  channelString):
        self.energyPlotGroupBox = QGroupBox(self.tr(''))
        self.energyPlotGroupBox.setStyleSheet(self.getStyleSheet("./styles_lightgrey.qss")) 
        titleFont = QFont()
        titleFont.setFamily("Arial")
        titleFont.setFixedPitch(True)
        titleFont.setPointSize(25)
        self.energyPlotGroupBox.setFont(titleFont)
        
        self.plotCanvas =  MplCanvas(self, width=7, height=3, dpi=100)
        self.plotCanvas.axes.plot(self.measuredEnergyArray)
        self.plotCanvas.axes.set_xlabel('discrete time instance')
        self.plotCanvas.axes.set_ylabel(channelString + 'energy / Wh')
        self.plotCanvas.axes.grid()
        self.plotCanvas.setFixedSize(700, 370)
        
        # create the layout and add the plot widget
        self.energyPlotVBox = QVBoxLayout()
        self.energyPlotVBox.addWidget(self.plotCanvas)
        
        # set the font to be used later
        labelFont = QFont()
        labelFont.setFamily("Arial")
        labelFont.setFixedPitch(True)
        labelFont.setPointSize(15)
        
        # create the label and edit for the mean energy
        self.actualEnergyLabel = QLabel()
        self.actualEnergyLabel.setStyleSheet("QLabel { background-color: lightgrey;  }")
        self.actualEnergyLabel.setText('Actual cell energy / Wh: ')
        self.actualEnergyLabel.setFixedSize(240, 25)
        self.actualEnergyLabel.setAlignment(Qt.AlignLeft)
        self.actualEnergyLabel.setFont(labelFont)
        
        # font for the measurement displays
        displayFont = QFont()
        displayFont.setFamily("Arial")
        displayFont.setFixedPitch(True)
        displayFont.setPointSize(15)

        # mean Energy display edit
        self.actualEnergyEdit = QLineEdit()
        self.actualEnergyEdit.setText("{:2.2f}".format(self.actualEnergy))
        self.actualEnergyEdit.setFont(displayFont)
        self.actualEnergyEdit.setFixedSize(80, 25)
        self.actualEnergyEdit.setAlignment(Qt.AlignRight)
        self.actualEnergyEdit.setReadOnly(True)
        
        # create the HBox for the actual energy display
        self.actualEnergyHBox = QHBoxLayout()
        # add the widgets
        self.actualEnergyHBox.addWidget(self.actualEnergyLabel)
        self.actualEnergyHBox.addWidget(self.actualEnergyEdit)
        
        # add the mean energy display HBox
        self.energyPlotVBox.addLayout(self.actualEnergyHBox)
        
        # add the layout to the measurement box
        self.energyPlotGroupBox.setLayout(self.energyPlotVBox)
        
    def handleMeasurements(self):
        if (self.OnOffControlValueMeasurements == 1):
            # request energy measurements from the energy sensor and update the display
            try:
                measuredEnergy = self.msgIF.GetMeasuredValue()
                print("measuredEnergy =", measuredEnergy )
                
                # valid measurement received   --> update plot and displays
                self.actualEnergy = measuredEnergy
                self.noValidMeasurements = self.noValidMeasurements + 1
                if (self.noValidMeasurements > self.maxArraySize):
                    self.noValidMeasurements = self.maxArraySize
                self.actualEnergyEdit.setText("{:2.2f}".format(measuredEnergy))
                self.updateMeasurementsArray(measuredEnergy)
                self.updatePlot()
                self.updateMeanEnergy()
            except TypeError:
                print("failed to get correct measurements")
          
    def getStyleSheet(self, path):
        f = QFile(path)
        f.open(QFile.ReadOnly | QFile.Text)
        stylesheet = QTextStream(f).readAll()
        f.close()
        return stylesheet    

    def updatePlot(self,  unitString):
        print("update plot")
        self.plotCanvas.axes.clear()
        self.plotCanvas.axes.plot(self.measuredEnergyArray)
        self.plotCanvas.axes.grid()
        self.plotCanvas.axes.set_xlabel('discrete time instance')
        self.plotCanvas.axes.set_ylabel(unitString + 'Energy / Wh')
        # update the plot
        self.plotCanvas.draw()
        
    def updateMeanEnergy(self):
        # calculate the mean Energy value
        self.meanEnergy = np.mean(self.measuredEnergyArray[0:self.noValidMeasurements])
        # update the mean Energy edit
        self.meanEnergyEdit.setText("{:2.2f}".format(self.meanEnergy))        
        
    def updateMeasurementsArray(self, EnergyValue):
        self.measuredEnergyArray[self.arrayIndex] = EnergyValue
        self.arrayIndex = self.arrayIndex + 1
        if (self.arrayIndex > self.maxArraySize) :
            self.arrayIndex = 0
    
    def initMeasurementsArray(self):
        self.maxArraySize = 100
        self.measuredEnergyArray = 25.0*np.ones(self.maxArraySize+1)
        self.arrayIndex = 0
        self.noValidMeasurements = 0
