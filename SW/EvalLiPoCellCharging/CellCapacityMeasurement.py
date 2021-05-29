"""
CellCapacityMeasurement.py

cell capacity measurement display for a single channel
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

class CellCapacityMeasurementsWindow(QWidget):
    def __init__(self, titleString):
        QWidget.__init__(self)
        
        # measured values of capacity (actual and mean)
        self.actualCapacity = 0.0
        self.meanCapacity = 0.0
        self.noValidMeasurements = 0
        
        # array of measurements
        self.initMeasurementsArray() 
        
        # create the plot widget
        self.createPlotWidget(titleString)
        print("Capacity plot widget created")
        self.updatePlot(self.measuredCapacityArray)

    def createPlotWidget(self,  channelString):
        self.capacityPlotGroupBox = QGroupBox(self.tr(''))
        self.capacityPlotGroupBox.setStyleSheet(self.getStyleSheet("./styles_lightgrey.qss")) 
        titleFont = QFont()
        titleFont.setFamily("Arial")
        titleFont.setFixedPitch(True)
        titleFont.setPointSize(25)
        self.capacityPlotGroupBox.setFont(titleFont)
        
        self.plotCanvas =  MplCanvas(self, width=7, height=3, dpi=100)
        self.plotCanvas.axes.plot(self.measuredCapacityArray)
        self.plotCanvas.axes.set_xlabel('discrete time instance')
        self.plotCanvas.axes.set_ylabel('Cell Capacity / Ah')
        self.plotCanvas.axes.grid()
        self.plotCanvas.setFixedSize(700, 370)
        
        # create the layout and add the plot widget
        self.capacityPlotVBox = QVBoxLayout()
        self.capacityPlotVBox.addWidget(self.plotCanvas)
        
        # set the font to be used later
        labelFont = QFont()
        labelFont.setFamily("Arial")
        labelFont.setFixedPitch(True)
        labelFont.setPointSize(15)
        
        # create the label and edit for the mean capacity
        self.actualCapacityLabel = QLabel()
        self.actualCapacityLabel.setStyleSheet("QLabel { background-color: lightgrey;  }")
        self.actualCapacityLabel.setText('Actual cell capacity / Ah: ')
        self.actualCapacityLabel.setFixedSize(240, 25)
        self.actualCapacityLabel.setAlignment(Qt.AlignLeft)
        self.actualCapacityLabel.setFont(labelFont)
        
        # font for the measurement displays
        displayFont = QFont()
        displayFont.setFamily("Arial")
        displayFont.setFixedPitch(True)
        displayFont.setPointSize(15)

        # mean Capacity display edit
        self.actualCapacityEdit = QLineEdit()
        self.actualCapacityEdit.setText("{:2.4f}".format(self.actualCapacity))
        self.actualCapacityEdit.setFont(displayFont)
        self.actualCapacityEdit.setFixedSize(120, 25)
        self.actualCapacityEdit.setAlignment(Qt.AlignRight)
        self.actualCapacityEdit.setReadOnly(True)
        
        # create the HBox for the actual capacity display
        self.actualCapacityHBox = QHBoxLayout()
        # add the widgets
        self.actualCapacityHBox.addWidget(self.actualCapacityLabel)
        self.actualCapacityHBox.addWidget(self.actualCapacityEdit)
        
        # add the mean capacity display HBox
        self.capacityPlotVBox.addLayout(self.actualCapacityHBox)
        
        # add the layout to the measurement box
        self.capacityPlotGroupBox.setLayout(self.capacityPlotVBox)
          
    def getStyleSheet(self, path):
        f = QFile(path)
        f.open(QFile.ReadOnly | QFile.Text)
        stylesheet = QTextStream(f).readAll()
        f.close()
        return stylesheet    

    def updatePlot(self,  data):
        print("update capacity plot")
        self.measuredCapacityArray = data
        self.plotCanvas.axes.clear()
        self.plotCanvas.axes.plot(self.measuredCapacityArray)
        self.plotCanvas.axes.grid()
        self.plotCanvas.axes.set_xlabel('discrete time instance')
        self.plotCanvas.axes.set_ylabel('Cell Capacity / Ah')
        # update the plot
        self.plotCanvas.draw()
        
    def updateMeanCapacity(self):
        # calculate the mean Capacity value
        self.meanCapacity = np.mean(self.measuredCapacityArray[0:self.noValidMeasurements])
        # update the mean Capacity edit
        self.meanCapacityEdit.setText("{:2.4f}".format(self.meanCapacity))        
        
    def updateMeasurementsArray(self, CapacityValue):
        self.measuredCapacityArray[self.arrayIndex] = CapacityValue
        self.arrayIndex = self.arrayIndex + 1
        if (self.arrayIndex > self.maxArraySize) :
            self.arrayIndex = 0
    
    def initMeasurementsArray(self):
        self.maxArraySize = 100
        self.measuredCapacityArray = 0.1*np.ones(self.maxArraySize+1)
        self.arrayIndex = 0
        self.noValidMeasurements = 0
