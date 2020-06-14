
from PyQt5.QtWidgets import *
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5 import QtCore

class MplWidget(QWidget):
    def __init__(self,parent=None):
        QWidget.__init__(self)
        self.verticalLayout = QVBoxLayout(self)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.scrollArea = QScrollArea(self)
        self.scrollArea.setWidgetResizable(False)
        self.scrollArea.setObjectName("scrollArea")
        self.scrollArea.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.scrollArea.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        
        self.figure = plt.figure() #QWidget  //FigureCanvas//Figure// subplot
        self.canvas = FigureCanvas(self.figure)  # FigureCanvas//Figure// called canvas
        self.figure.set_facecolor("black")
        self.scrollArea.setSizePolicy(QSizePolicy.Minimum,QSizePolicy.Minimum)
        self.scrollArea.setContentsMargins(0, 0, 0, 0)
        self.scrollArea.setStyleSheet("border:0px;padding-left:0px;padding-top:0px;padding-right:0px;padding-bottom:0px")
        self.scrollArea.setWidget(self.canvas)
        self.verticalLayout.addWidget(self.scrollArea)
        
