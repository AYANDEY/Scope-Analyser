from PyQt5.Qt import QDoubleSpinBox, QKeyEvent
from PyQt5.uic.Compiler.qtproxies import QtCore
from PyQt5.QtCore import pyqtSignal,Qt

class window_param_spin(QDoubleSpinBox):
    val_entered=pyqtSignal()
    
    def __init__(self,parent):
        QDoubleSpinBox.__init__(self)
        
    def keyReleaseEvent(self,e):
        if e.key()==Qt.Key_Return:
            self.val_entered.emit()
