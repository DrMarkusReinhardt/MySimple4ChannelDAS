"""
VoltageMeasurement.py

voltage measurement display for a single channel
(suited for Max OSX, Windows, Linux)

Created 20th May 2021

Last change on 20th May 2021

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

class CellVoltageMeasurementsWindow(QWidget):
    def __init__(self, titleString):
        QWidget.__init__(self)
        
        # measured values of voltage (actual and mean)
        self.actualVoltage = 0.0
        self.meanVoltage = 0.0
        self.noValidMeasurements = 0
        
        # array of measurements
        self.initMeasurementsArray() 
        
        # create the plot widget
        self.createPlotWidget(titleString)
        print("Voltage plot widget created")
        self.updatePlot(self.measuredVoltageArray)

    def createPlotWidget(self,  titleString):
        self.voltagePlotGroupBox = QGroupBox(self.tr(''))
        self.voltagePlotGroupBox.setStyleSheet(self.getStyleSheet("./styles_lightgrey.qss")) 
        titleFont = QFont()
        titleFont.setFamily("Arial")
        titleFont.setFixedPitch(True)
        titleFont.setPointSize(25)
        self.voltagePlotGroupBox.setFont(titleFont)
        
        self.plotCanvas =  MplCanvas(self, width=7, height=3, dpi=100)
        self.plotCanvas.axes.plot(self.measuredVoltageArray)
        self.plotCanvas.axes.set_xlabel('discrete time instance')
        self.plotCanvas.axes.set_ylabel('Cell Voltage / V')
        self.plotCanvas.axes.grid()
        self.plotCanvas.setFixedSize(700, 370)
        
        # create the layout and add the plot widget
        self.voltagePlotVBox = QVBoxLayout()
        self.voltagePlotVBox.addWidget(self.plotCanvas)
        
        # set the font to be used later
        labelFont = QFont()
        labelFont.setFamily("Arial")
        labelFont.setFixedPitch(True)
        labelFont.setPointSize(15)
        
        # create the label and edit for the mean voltage
        self.actualVoltageLabel = QLabel()
        self.actualVoltageLabel.setStyleSheet("QLabel { background-color: lightgrey;  }")
        self.actualVoltageLabel.setText('Actual cell voltage / V: ')
        self.actualVoltageLabel.setFixedSize(240, 25)
        self.actualVoltageLabel.setAlignment(Qt.AlignLeft)
        self.actualVoltageLabel.setFont(labelFont)
        
        # font for the measurement displays
        displayFont = QFont()
        displayFont.setFamily("Arial")
        displayFont.setFixedPitch(True)
        displayFont.setPointSize(15)

        # mean Voltage display edit
        self.actualVoltageEdit = QLineEdit()
        self.actualVoltageEdit.setText("{:2.2f}".format(self.actualVoltage))
        self.actualVoltageEdit.setFont(displayFont)
        self.actualVoltageEdit.setFixedSize(80, 25)
        self.actualVoltageEdit.setAlignment(Qt.AlignRight)
        self.actualVoltageEdit.setReadOnly(True)
        
        # create the HBox for the actual voltage display
        self.actualVoltageHBox = QHBoxLayout()
        # add the widgets
        self.actualVoltageHBox.addWidget(self.actualVoltageLabel)
        self.actualVoltageHBox.addWidget(self.actualVoltageEdit)
        
        # add the mean voltage display HBox
        self.voltagePlotVBox.addLayout(self.actualVoltageHBox)
        
        # add the layout to the measurement box
        self.voltagePlotGroupBox.setLayout(self.voltagePlotVBox)

    def getStyleSheet(self, path):
        f = QFile(path)
        f.open(QFile.ReadOnly | QFile.Text)
        stylesheet = QTextStream(f).readAll()
        f.close()
        return stylesheet    

    def updatePlot(self,  data):
        print("update voltage plot")
        self.measuredVoltageArray = data
        self.plotCanvas.axes.clear()
        self.plotCanvas.axes.plot(self.measuredVoltageArray)
        self.plotCanvas.axes.grid()
        self.plotCanvas.axes.set_xlabel('discrete time instance')
        self.plotCanvas.axes.set_ylabel('Cell Voltage / V')
        # update the plot
        self.plotCanvas.draw()
        
    def updateMeanVoltage(self):
        # calculate the mean Voltage value
        self.meanVoltage = np.mean(self.measuredVoltageArray[0:self.noValidMeasurements])
        # update the mean Voltage edit
        self.meanVoltageEdit.setText("{:2.2f}".format(self.meanVoltage))        
        
    def updateMeasurementsArray(self, VoltageValue):
        self.measuredVoltageArray[self.arrayIndex] = VoltageValue
        self.arrayIndex = self.arrayIndex + 1
        if (self.arrayIndex > self.maxArraySize) :
            self.arrayIndex = 0
    
    def initMeasurementsArray(self):
        self.maxArraySize = 100
        self.measuredVoltageArray = 4.0*np.ones(self.maxArraySize+1)
        self.arrayIndex = 0
        self.noValidMeasurements = 0
