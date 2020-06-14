
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.Qt import QRubberBand,QPen

class cursorBox(QtWidgets.QRubberBand):
    
    def __init__(self,tex,col,text_color,*arg,**kwargs):
        
        super(cursorBox,self).__init__(*arg,**kwargs)
        self.tex=tex
        self.col=QtGui.QColor(col)
        self.tex_color=QtGui.QColor(text_color)
        
    def paintEvent(self, QPaintEvent):
        painter = QtGui.QPainter(self)
        painter.setBrush(QtGui.QBrush(self.col))
        painter.setOpacity(1)
        qrect=QPaintEvent.rect()
        painter.drawRect(qrect)
        painter.setPen(QtGui.QPen(self.tex_color,4))
        painter.drawText(qrect, Qt.AlignCenter,self.tex)
        painter.end()
        
    def set_color(self,col):
        self.col=QtGui.QColor(col)
    
    def set_text_color(self,text_color):
        self.tex_color=QtGui.QColor(text_color)

class cursorTrackBox(QtWidgets.QRubberBand):
        
    def __init__(self,col,*arg,**kwargs):
        
        super(cursorTrackBox,self).__init__(*arg,**kwargs)
        
        self.col=QtGui.QColor(col)
        
        
    def paintEvent(self, QPaintEvent):
        painter = QtGui.QPainter(self)
        qrect=QPaintEvent.rect()
        
        painter.setPen(QPen(Qt.white,4))
        painter.setOpacity(1)
        painter.drawRect(qrect)
        painter.end()
        

    def set_color(self,col):
        self.col=QtGui.QColor(col)

class cursorTrackLine(QtWidgets.QRubberBand):
    def __init__(self,col,*arg,**kwargs):
        
        super(cursorTrackLine,self).__init__(*arg,**kwargs)
        self.col=QtGui.QColor(col)
        
    def paintEvent(self, QPaintEvent):
        painter = QtGui.QPainter(self)
        painter.setOpacity(1)
        pen=QPen(self.col,1)
        #pen.setStyle(Qt.DashDotDotLine)
        pen.setStyle(Qt.CustomDashLine)
        pen.setDashPattern([16, 4, 8, 4])
        painter.setPen(pen)
        qrect=QPaintEvent.rect()
        painter.drawRect(qrect)
        painter.end()
        

    def set_color(self,col):
        self.col=QtGui.QColor(col)

class Bounding_Box(QtWidgets.QRubberBand):
        
    def __init__(self,col,*arg,**kwargs):
        super(Bounding_Box,self).__init__(*arg,**kwargs)
        self.col=QtGui.QColor(col)
        
        
    def paintEvent(self, QPaintEvent):
        painter = QtGui.QPainter(self)
        qrect=QPaintEvent.rect()
        
        painter.setPen(QPen(Qt.white,2))
        painter.setOpacity(1)
        painter.drawRect(qrect)
        painter.end()
        

    def set_color(self,col):
        self.col=QtGui.QColor(col)

class Zeroline(QtWidgets.QRubberBand):
    def __init__(self,col,*arg,**kwargs):
        super(Zeroline,self).__init__(*arg,**kwargs)
        self.col=QtGui.QColor(col)
        
    def paintEvent(self, QPaintEvent):
        painter = QtGui.QPainter(self)
        qrect=QPaintEvent.rect()
        painter.setPen(QPen(self.col,2))
        painter.setOpacity(1)
        painter.drawRect(qrect)
        painter.end()
        
    def set_color(self,col):
        self.col=QtGui.QColor(col)

class Zeroline_Box(QtWidgets.QRubberBand):
    def __init__(self,text,col,*arg,**kwargs):
        super(Zeroline_Box,self).__init__(*arg,**kwargs)
        self.col=QtGui.QColor(col)
        self.text=text
        
    def paintEvent(self, QPaintEvent):
        painter = QtGui.QPainter(self)
        painter.setBrush(QtGui.QBrush(self.col))
        qrect=QPaintEvent.rect()
        painter.drawRect(qrect)
        painter.setPen(QtGui.QPen(QtGui.QColor("black"),4))
        painter.drawText(qrect, Qt.AlignCenter,self.text)
        painter.end()
        
    def set_color(self,col):
        self.col=QtGui.QColor(col)