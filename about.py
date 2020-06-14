
from PyQt5 import QtCore, QtWidgets,QtGui
from PyQt5.Qt import QMessageBox

class messege(QtWidgets.QWidget):
    def __init__(self,parent):
        super(messege,self).__init__()
        self.setWindowTitle("About")
        self.setWindowIcon(QtGui.QIcon('res\\about.ico'))
        self.main=parent
        self.resize(self.main.main.aboutwinsize[0],self.main.main.aboutwinsize[1])
        size=self.size()
        self.setMaximumSize(size)
        self.setMinimumSize(size)
        #self.resize(442,223)
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self)
        self.verticalLayout_3.setContentsMargins(5, 5, 5, 5)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.header = QtWidgets.QLabel()
        font = QtGui.QFont()
        font.setPointSize(12)
        self.header.setFont(font)
        self.header.setAlignment(QtCore.Qt.AlignCenter)
        self.verticalLayout_2.addWidget(self.header)
        self.Version = QtWidgets.QLabel()
        font = QtGui.QFont()
        font.setPointSize(9)
        self.Version.setFont(font)
        self.Version.setAlignment(QtCore.Qt.AlignCenter)
        self.verticalLayout_2.addWidget(self.Version)
        self.Description = QtWidgets.QLabel()
        font = QtGui.QFont()
        font.setPointSize(10)
        self.Description.setFont(font)
        self.Description.setAlignment(QtCore.Qt.AlignCenter)
        self.verticalLayout_2.addWidget(self.Description)
        self.developer_details = QtWidgets.QLabel()
        font = QtGui.QFont()
        font.setPointSize(9)
        self.developer_details.setFont(font)
        self.developer_details.setAlignment(QtCore.Qt.AlignCenter)
        self.verticalLayout_2.addWidget(self.developer_details)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_2.addItem(spacerItem)
        self.header.setText("Scope Analyser")
        self.Version.setText("Version 1.0")
        self.Description.setText("Created to analyse csv files of Oscilloscopes.\n"
                                 "Tested Compatibility with Hantek  \n"
                                 "For details of file parameters check \'Readme.txt\' ")
        self.developer_details.setText("Designed and Developed by Ayan Dey Date:13/06/2020 \n"
                                       "E-mail:ayandey1990phy@hotmail.com  \n"
                                       " (During the \'lockdown\' of  Covid-19 pandamic 2020)")
        self.verticalLayout_3.addLayout(self.verticalLayout_2)
        self.shown=False
    
    def showEvent(self,e):
        self.shown=True
        
    def closeEvent(self, e):
        self.shown=False