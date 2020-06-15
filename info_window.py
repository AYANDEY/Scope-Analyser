from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QFont

class Ui_infoWindow(QtWidgets.QWidget):
    def __init__(self,parent):
        super().__init__()
        self.main=parent
        self.win_pos=QtCore.QPoint(0,0)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Maximum)
        self.setSizePolicy(sizePolicy)
        self.setWindowIcon(QtGui.QIcon('res\\info.ico'))
        #self.setWindowFlags(QtCore.Qt.WindowFlags(QtCore.Qt.FramelessWindowHint))
        self.layout1 = QtWidgets.QVBoxLayout()
        self.tableWidget = QtWidgets.QTableWidget(self)
        self.tableWidget.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)
        self.tableWidget.setAlternatingRowColors(True)
        self.tableWidget.setSizePolicy(sizePolicy)
        self.tableWidget.setColumnCount(3)
        self.tableWidget.setRowCount(0)
        self.tableWidget.setLineWidth(5)
        self.layout1.addWidget(self.tableWidget)
        self.layout1.setContentsMargins(0,0,0,0)
        self.layout1.setSizeConstraint(QtWidgets.QLayout.SetMaximumSize)
        self.tableWidget.verticalHeader().setVisible(False)
        self.first_run=True
        header_list=["Channel","Channel Color","File Path"]#,"FFT Enabled","FFT Color"]
        font = QFont("Arial",9)
        font.setBold(True)
        header_num=0
        for headers in header_list:
            header_item = QtWidgets.QTableWidgetItem(headers)
            header_item.setFont(font)
            self.tableWidget.setHorizontalHeaderItem(header_num,header_item)
            header_num +=1
        
        self.closed=False
        self.shown=False
        self.was_shown=False
        self.tableWidget.resizeColumnsToContents()
        self.setWindowTitle("Channel Information")
        
        print("Offset=",self.main.popup_width_offset,self.main.popup_height_offset)
        self.rows_shown=0
        self.resize_by_func=False
        self.Each_Row_height_saved=0
        self.Actual_win_height_0_row_saved=0
        self.table_height_offset_saved=0
        self.tableWidget_Infow_size_same=False
        self.get_config()
    
    def resizeEvent(self,event):
        QtWidgets.QWidget.resizeEvent(self, event)
        print("resize")
        if self.shown==True and self.resize_by_func==False:
            self.tableWidget.resize(self.size().width(),self.size().height())
            self.tableWidget_Infow_size_same=True
        self.resize_by_func=False
    
    def showEvent(self, event):
        
        QtWidgets.QWidget.showEvent(self, event)
        if self.tableWidget_Infow_size_same==False:
            self.resize(self.tableWidget.size().width()-self.main.popup_width_offset,self.tableWidget.size().height()-self.main.popup_height_offset)
        else:
            self.resize(self.tableWidget.size().width(),self.tableWidget.size().height())
        self.shown=True
        self.was_shown=False
        if isinstance(self.win_pos, str)==False:
            self.move(self.win_pos)
        print("Shown")
        self.Each_Row_height_saved,self.Actual_win_height_0_row_saved,self.table_height_offset_saved=self.main.info_win_read_dimentions()
        self.closed=False
    
    def closeEvent(self,event):
        self.shown=False
        self.was_shown=True
        QtWidgets.QWidget.closeEvent(self,event)
        self.closed=True
    
    def moveEvent(self, e):
        if self.closed==False:
            self.win_pos=self.pos()
        super(Ui_infoWindow, self).moveEvent(e)
    
    def get_pos(self):
        if isinstance(self.win_pos, str):
            return [0 , 0]
        else:
            return self.win_pos.x(),self.win_pos.y()
    
    def set_pos(self,pos_):
        self.move(pos_[0],pos_[1])
    
    def get_config(self):
        
        if self.main.conf.Information_Window_Opacity!=[None,False]:
            self.setWindowOpacity(self.main.conf.Information_Window_Opacity)
        if self.main.conf.Information_Window_always_on_top!=[None,False]:
            
            if self.main.conf.Information_Window_always_on_top:
                self.setWindowFlags(QtCore.Qt.WindowFlags(QtCore.Qt.WindowStaysOnTopHint))
            else:
                self.setWindowFlags(QtCore.Qt.WindowFlags())

#Info window on close and reopen size remains initial size