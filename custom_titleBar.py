
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QHBoxLayout, QLabel, QPushButton, QVBoxLayout
from PyQt5.QtWidgets import QHBoxLayout, QLabel
from PyQt5.QtCore import QPoint, Qt


class custom_TitleBar(QtWidgets.QWidget):

    def __init__(self, parent):
        super(custom_TitleBar, self).__init__()
        self.parent = parent
        self.title = QLabel("Scope Analyser")
        btn_size = 25
        self.btn_close = QPushButton("x")
        self.btn_close.clicked.connect(self.btn_close_clicked)
        self.btn_close.setFixedSize(btn_size,btn_size)
        #self.btn_close.setStyleSheet("background-color: red;")
        self.btn_min = QPushButton("-")
        self.btn_min.clicked.connect(self.btn_min_clicked)
        self.btn_min.setFixedSize(btn_size, btn_size)
        #self.btn_min.setStyleSheet("background-color: gray;")
        self.btn_max = QPushButton("+")
        self.btn_max.clicked.connect(self.btn_max_clicked)
        self.btn_max.setFixedSize(btn_size, btn_size)
        #self.btn_max.setStyleSheet("background-color: gray;")
        self.title.setFixedHeight(40)
        self.title.setAlignment(Qt.AlignLeft)
        self.layout = QHBoxLayout()
        self.layout.setContentsMargins(0,0,0,0)
        self.layout.addWidget(self.title)
        self.layout.addWidget(self.btn_min)
        self.layout.addWidget(self.btn_max)
        self.layout.addWidget(self.btn_close)
        #self.title.setStyleSheet("background-color: black;color: white;")
        self.setLayout(self.layout)
        self.start = QPoint(0, 0)
        self.pressing = False

    def resizeEvent(self, QResizeEvent):
        super(custom_TitleBar, self).resizeEvent(QResizeEvent)
        print("RRR")
        self.title.setFixedWidth(self.parent.width())
        
    def showEvent( self, QShowEvent):
        return super(custom_TitleBar, self).showEvent( QShowEvent)
    
    def mousePressEvent(self, event):
        self.start = self.mapToGlobal(event.pos())
        self.pressing = True
        
    def mouseMoveEvent(self, event):
        if self.pressing:
            self.end = self.mapToGlobal(event.pos())
            self.movement = self.end-self.start
            self.parent.setGeometry(self.mapToGlobal(self.movement).x(),
                                self.mapToGlobal(self.movement).y(),
                                self.parent.width(),
                                self.parent.height())
            self.start = self.end

    def mouseReleaseEvent(self, QMouseEvent):
        
        self.pressing = False

    def setHeight(self,h):
        self.title.setFixedHeight(h)
        
    def btn_close_clicked(self):
        self.parent.close()

    def btn_max_clicked(self):
        self.parent.showMaximized()

    def btn_min_clicked(self):
        self.parent.showMinimized()