"""
CellCurrentMeasurement.py

cell current measurement display for a single channel
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

class CellCurrentMeasurementsWindow(QWidget):
    def __init__(self, titleString):
        QWidget.__init__(self)
        
        # measured values of current (actual and mean)
        self.actualCurrent = 0.0
        self.meanCurrent = 0.0
        self.noValidMeasurements = 0
        
        # array of measurements
        self.initMeasurementsArray() 
        
        # create the plot widget
        self.createPlotWidget(titleString)
        print("Current plot widget created")
        self.updatePlot(self.measuredCurrentArray)
                

    def createPlotWidget(self,  titleString):
        self.currentPlotGroupBox = QGroupBox(self.tr(''))
        self.currentPlotGroupBox.setStyleSheet(self.getStyleSheet("./styles_lightgrey.qss")) 
        titleFont = QFont()
        titleFont.setFamily("Arial")
        titleFont.setFixedPitch(True)
        titleFont.setPointSize(25)
        self.currentPlotGroupBox.setFont(titleFont)
        
        self.plotCanvas =  MplCanvas(self, width=7, height=3, dpi=100)
        self.plotCanvas.axes.plot(self.measuredCurrentArray)
        self.plotCanvas.axes.set_xlabel('discrete time instance')
        self.plotCanvas.axes.set_ylabel('Cell Current / A')
        self.plotCanvas.axes.grid()
        self.plotCanvas.setFixedSize(700, 370)
        
        # create the layout and add the plot widget
        self.currentPlotVBox = QVBoxLayout()
        self.currentPlotVBox.addWidget(self.plotCanvas)
        
        # set the font to be used later
        labelFont = QFont()
        labelFont.setFamily("Arial")
        labelFont.setFixedPitch(True)
        labelFont.setPointSize(15)
        
        # create the label and edit for the mean current
        self.actualCurrentLabel = QLabel()
        self.actualCurrentLabel.setStyleSheet("QLabel { background-color: lightgrey;  }")
        self.actualCurrentLabel.setText('Actual cell current / A: ')
        self.actualCurrentLabel.setFixedSize(240, 25)
        self.actualCurrentLabel.setAlignment(Qt.AlignLeft)
        self.actualCurrentLabel.setFont(labelFont)
        
        # font for the measurement displays
        displayFont = QFont()
        displayFont.setFamily("Arial")
        displayFont.setFixedPitch(True)
        displayFont.setPointSize(15)

        # mean Current display edit
        self.actualCurrentEdit = QLineEdit()
        self.actualCurrentEdit.setText("{:2.3f}".format(self.actualCurrent))
        self.actualCurrentEdit.setFont(displayFont)
        self.actualCurrentEdit.setFixedSize(80, 25)
        self.actualCurrentEdit.setAlignment(Qt.AlignRight)
        self.actualCurrentEdit.setReadOnly(True)
        
        # create the HBox for the actual current display
        self.actualCurrentHBox = QHBoxLayout()
        # add the widgets
        self.actualCurrentHBox.addWidget(self.actualCurrentLabel)
        self.actualCurrentHBox.addWidget(self.actualCurrentEdit)
        
        # add the mean current display HBox
        self.currentPlotVBox.addLayout(self.actualCurrentHBox)
        
        # add the layout to the measurement box
        self.currentPlotGroupBox.setLayout(self.currentPlotVBox)
          
    def getStyleSheet(self, path):
        f = QFile(path)
        f.open(QFile.ReadOnly | QFile.Text)
        stylesheet = QTextStream(f).readAll()
        f.close()
        return stylesheet    

    def updatePlot(self,  data):
        print("update current plot")
        self.measuredCurrentArray = data
        self.plotCanvas.axes.clear()
        self.plotCanvas.axes.plot(self.measuredCurrentArray)
        self.plotCanvas.axes.grid()
        self.plotCanvas.axes.set_xlabel('discrete time instance')
        self.plotCanvas.axes.set_ylabel('Cell Current / A')
        # update the plot
        self.plotCanvas.draw()
        
    def updateMeanCurrent(self):
        # calculate the mean Current value
        self.meanCurrent = np.mean(self.measuredCurrentArray[0:self.noValidMeasurements])
        # update the mean Current edit
        self.meanCurrentEdit.setText("{:2.3f}".format(self.meanCurrent))        
        
    def updateMeasurementsArray(self, CurrentValue):
        self.measuredCurrentArray[self.arrayIndex] = CurrentValue
        self.arrayIndex = self.arrayIndex + 1
        if (self.arrayIndex > self.maxArraySize) :
            self.arrayIndex = 0
    
    def initMeasurementsArray(self):
        self.maxArraySize = 100
        self.measuredCurrentArray = 0.9*np.ones(self.maxArraySize+1)
        self.arrayIndex = 0
        self.noValidMeasurements = 0
