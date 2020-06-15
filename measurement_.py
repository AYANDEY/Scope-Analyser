

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QHBoxLayout, QLabel, QPushButton, QVBoxLayout
from PyQt5.QtCore import QPoint, Qt
#from custom_titleBar import custom_TitleBar
import numpy as np
import threading
import time
import matplotlib.pyplot as plt

class Ui_MeasureWindow(QtWidgets.QWidget):
    def __init__(self,parent):
        super().__init__()
        self.main=parent
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Maximum)
        self.setSizePolicy(sizePolicy)
        self.setWindowTitle("Channel Measurement")
        self.setWindowIcon(QtGui.QIcon('res\\m_icon.ico'))
        #self.setWindowFlags(QtCore.Qt.WindowFlags(QtCore.Qt.FramelessWindowHint))
        self.layout1 = QtWidgets.QHBoxLayout()
        self.tableWidget = QtWidgets.QTableWidget(self)
        self.tableWidget.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)
        self.tableWidget.setAlternatingRowColors(True)
        self.tableWidget.setSizePolicy(sizePolicy)
        self.tableWidget.setColumnCount(12)
        self.tableWidget.setRowCount(0)
        self.tableWidget.setLineWidth(5)
        self.layout1.addWidget(self.tableWidget)
        self.layout1.setContentsMargins(0,0,0,0)
        self.layout1.setSizeConstraint(QtWidgets.QLayout.SetMaximumSize)
        self.tableWidget.verticalHeader().setVisible(False)
        header_list=["Channel","Vmin","Vmax","Vmean","Vrms","Vpk-pk","Freq","T Period","PWidth+","PWidth-","Duty+","Duty-"]
        font = QtGui.QFont("Arial",9)
        font.setBold(True)
        header_num=0
        for headers in header_list:
            header_item = QtWidgets.QTableWidgetItem(headers)
            header_item.setFont(font)
            self.tableWidget.setHorizontalHeaderItem(header_num,header_item)
            header_num +=1
        
        self.tableWidget.resizeColumnsToContents()
        self.first_run=True
        #self.title_bar = custom_TitleBar(self)
        #self.layout.addWidget(self.title_bar)
        #flags=QtCore.Qt.WindowFlags(QtCore.Qt.FramelessWindowHint)# | QtCore.Qt.WindowStaysOnTopHint)
        #self.setWindowFlags(QtCore.Qt.WindowFlags(QtCore.Qt.FramelessWindowHint))
        #self.title_bar.pressing = False
        self.freq_Pulse_Duty_list=[]
        self.Ch_Vmins=[]
        self.Ch_Vmaxs=[]
        self.Ch_Vmeans=[]
        self.Ch_Vrms=[]
        self.Ch_pk2pk=[]
        
        self.freq_Pulse_Duty_list_act=[]
        self.Ch_Vmins_act=[]
        self.Ch_Vmaxs_act=[]
        self.Ch_Vrms_act=[]
        self.Ch_pk2pk_act=[]
        
        self.closed=False
        self.shown=False
        self.was_shown=False
        self.resize_by_func=False
        self.round_factor_is_set=True
        self.round_factor=3
        self.opacity_=160
        self.initial_members_count=0
        self.Each_Row_height_saved=0
        self.Actual_win_height_0_row_saved=0
        self.table_height_offset_saved=0
        self.tableWidget_mWin_size_same=False
        self.win_pos=QPoint(0,0)
        self.get_config()
    
    def update_(self):
        self.calc_Vmean()
        self.calc_Vrms()
        self.calc_pk2pk()
        self.Calc_Times()
        
        measurement_list=[]
        measurement_list_actual=[]
        ch_name_list=[]
        mem=0
        for members in self.main.ch_name_col_list:
            ch_name_list.append(self.main.ch_name_col_list[mem][0])
            mem+=1
        Ch_Vmeans=self.set_Units(self.Ch_Vmeans,0)
        measurement_list=[ch_name_list,self.Ch_Vmins,self.Ch_Vmaxs,Ch_Vmeans,self.Ch_Vrms,self.Ch_pk2pk,self.freq_Pulse_Duty_list]
        
        measurement_list_actual=[ch_name_list,self.Ch_Vmins_act,self.Ch_Vmaxs_act,self.Ch_Vmeans,self.Ch_Vrms_act,self.Ch_pk2pk_act,self.freq_Pulse_Duty_list_act]
        ##print(measurement_list)
        
        row_num=0
        ###CH_name Vmin, Vmax, Vmean Vrms PktoPk Freq TPeriod Pwidth+ PWidth- Duty+ Duty -
        for members in self.main.ch_name_col_list:
            self.tableWidget.insertRow(row_num)
            
            for i in range(self.tableWidget.columnCount()):
                if i<=5:
                    ##print("Items:",row_num,i,measurement_list[i][row_num])
                    self.tableWidget.setItem(row_num,i,QtWidgets.QTableWidgetItem(measurement_list[i][row_num]))
                    if i!=0:
                        self.tableWidget.item(row_num,i).setToolTip(str(measurement_list_actual[i][row_num])+"mv")
                    else:
                        self.tableWidget.item(row_num,i).setToolTip(str(measurement_list_actual[i][row_num]))
                    
                    self.tableWidget.item(row_num,i).setTextAlignment(Qt.AlignCenter)
                    col=QtGui.QColor(members[1])
                    col.setAlpha(self.opacity_)
                    self.tableWidget.item(row_num,i).setBackground(QtGui.QColor(col))
                else:
                    j=i-6
                    self.tableWidget.setItem(row_num,i,QtWidgets.QTableWidgetItem(measurement_list[6][row_num][j]))
                    if j==0:
                        self.tableWidget.item(row_num,i).setToolTip(str(measurement_list_actual[6][row_num][j])+"Hz")
                    elif j>0 and j<4:
                        self.tableWidget.item(row_num,i).setToolTip(str(measurement_list_actual[6][row_num][j])+"s")
                    else:
                        self.tableWidget.item(row_num,i).setToolTip(str(measurement_list_actual[6][row_num][j])+"%")
                    
                    col=QtGui.QColor(members[1])
                    col.setAlpha(self.opacity_)
                    self.tableWidget.item(row_num,i).setBackground(QtGui.QColor(col))
                    self.tableWidget.item(row_num,i).setTextAlignment(Qt.AlignCenter)
                #print(row_num,"  ",i)
            row_num +=1
        self.initial_members_count=row_num
        self.tableWidget.resizeColumnsToContents()
        self.tableWidget.resizeRowsToContents()
        self.first_run=False
    
    def Update_UI(self):
        if self.initial_members_count!=len(self.main.ch_name_col_list) or self.main.file_edited==True:
            if self.shown==True:
                Each_Row_height,Actual_win_height_0_row,table_height_offset=self.read_dimentions()
            elif self.was_shown:
                Each_Row_height=self.Each_Row_height_saved
                Actual_win_height_0_row=self.Actual_win_height_0_row_saved
                table_height_offset=self.table_height_offset_saved
                
            for i in range(self.tableWidget.rowCount()):
                self.tableWidget.removeRow(0)
            self.first_run=True
            
            self.update_()
            
            if self.shown==True or self.was_shown==True:
                TH=int((self.tableWidget.rowCount()*Each_Row_height)+Actual_win_height_0_row)
                #print("TH=",TH)
                self.resize_by_func=True
                self.tableWidget.resize(self.tableWidget.size().width(),TH+table_height_offset)
                self.resize(self.size().width(),TH)
                #print("MeasureWin Size Updated")
        self.activateWindow()
    
    def read_dimentions(self):
        mWin_Height=self.size().height()
        table_height=self.tableWidget.height()
        table_height_offset=table_height-mWin_Height
        T_row_Height=0
        row_count=self.tableWidget.rowCount()
        for i in range(row_count):
            T_row_Height+=self.tableWidget.rowHeight(i)
        Each_Row_height=T_row_Height/row_count
        Actual_win_height_0_row=mWin_Height-T_row_Height
        ##print("AWH=",Actual_win_height_0_row," Prow_count=",row_count,"PT_row_Height=",T_row_Height,"mWin_Height=",mWin_Height,"table_height=",table_height)
        return Each_Row_height,Actual_win_height_0_row,table_height_offset
    
############################################################ MATH ###########################################################################
    def calc_Vmean(self):
        ch_num=0
        for members in self.main.ch_name_col_list:
            self.Ch_Vmeans.append(np.mean(self.main.y[ch_num]))
            ch_num +=1
     
    def calc_Vrms(self):
        ch_num=0
        Ch_Vrms=[]
        vrms=[]
        vsq=[]
        for members in self.main.ch_name_col_list:
            vsq=np.square(self.main.y[ch_num])
            Ch_Vrms.append(np.sqrt(np.mean(vsq)))
            ch_num +=1
        self.Ch_Vrms_act=Ch_Vrms
        self.Ch_Vrms=self.set_Units(Ch_Vrms,0)
    
    def calc_pk2pk(self):
        ch_num=0
        Ch_pk2pk=[]
        Ch_Vmins=[]
        Ch_Vmaxs=[]
        for members in self.main.ch_name_col_list:
            vmax=max(self.main.y[ch_num])
            vmin=min(self.main.y[ch_num])
            Ch_pk2pk.append(vmax-vmin)
            ##print(vmax-vmin)
            Ch_Vmins.append(vmin)
            Ch_Vmaxs.append(vmax)
            ch_num +=1
        self.Ch_pk2pk=self.set_Units(Ch_pk2pk,0)
        self.Ch_pk2pk_act=Ch_pk2pk
        self.Ch_Vmaxs=self.set_Units(Ch_Vmaxs,0)
        self.Ch_Vmaxs_act=Ch_Vmaxs
        self.Ch_Vmins=self.set_Units(Ch_Vmins,0)
        self.Ch_Vmins_act=Ch_Vmins
        
    def Calc_Times(self):
        self.freq_Pulse_Duty_list_act=[]
        self.freq_Pulse_Duty_list=[]
        #self.calc_Vmean()
        y_mean=self.Ch_Vmeans
        ch_num=0
        self.freq_Pulse_Duty_list=[]
        for members in self.main.ch_name_col_list:
            #print("CH NAME:",self.main.ch_name_col_list[ch_num][0]," CH Vmean:",y_mean[ch_num])
            FPD=self.single_Ch_freq(ch_num,y_mean[ch_num])#freq,period,mean_pos_pulse,mean_neg_pulse,Duty_P,Duty_N
            self.freq_Pulse_Duty_list_act.append(FPD)
            FPD=self.set_Units(FPD,1)
            self.freq_Pulse_Duty_list.append(FPD)
            ch_num+=1
    
    def single_Ch_freq(self,ch_number,ch_V_mean):
        t_list=[]
        dt_list=[]
        pulse_bool_list=[]
        count_dir_bool=0
        for i in range (len(self.main.y[ch_number])-1):
            if self.main.y[ch_number][i+1]>self.main.y[ch_number][i] and self.main.y[ch_number][i+1]> ch_V_mean:
                if count_dir_bool==-1:
                    t_list.append(self.main.x[ch_number][i+1])
                    pulse_bool_list.append(1)
                    #print("line:",str(i+1),"X:",str(self.main.x[ch_number][i+1]),"Y:",str(self.main.y[ch_number][i+1]),"1")
                count_dir_bool=1
            elif self.main.y[ch_number][i+1]<self.main.y[ch_number][i] and self.main.y[ch_number][i+1]<ch_V_mean:
                if count_dir_bool==1:
                    t_list.append(self.main.x[ch_number][i+1])
                    pulse_bool_list.append(-1)
                    #print("line:",str(i+1),"X:",str(self.main.x[ch_number][i+1]),"Y:",str(self.main.y[ch_number][i+1]),"-1")
                count_dir_bool=-1
        for j in range((len(t_list)-1)):
            dt=t_list[j+1]-t_list[j]
            ##print("",",",t_list[j],",",",",pulse_bool_list[j],file=self.main.file_)
            ##print(dt,file=self.main.file_)
            ##print("",",",t_list[j+1],",",",",pulse_bool_list[j+1],file=self.main.file_)
            puse_bool=pulse_bool_list[j+1]-pulse_bool_list[j]
            ##print(dt,",",t_list[j+1],",",t_list[j],",",puse_bool,file=self.main.file_)
            dt_list.append([dt,puse_bool])
        #print(dt_list)
        #dt_list=sorted(dt_list,key=itemgetter(0),reverse=True)
        max_end_indx_pos=-1
        max_end_indx_neg=-1
        mean_pos_pulse=0
        mean_neg_pulse=0
        pos_pulse=[]
        neg_pulse=[]
        if len(dt_list)>1:
            for i in range(len(dt_list)):
                if dt_list[i][1]==-2:
                    pos_pulse.append(dt_list[i][0])
                if dt_list[i][1]==2:
                    neg_pulse.append(dt_list[i][0])
            pos_pulse=sorted(pos_pulse,reverse=True)
            neg_pulse=sorted(neg_pulse,reverse=True)
            for i in range(len(pos_pulse)-1):
                rel_dev=(pos_pulse[i]-pos_pulse[i+1])/pos_pulse[i]
                #print("indx=",i," dtf=",dt_list[i+1]," dti=",dt_list[i]," rel_dev=",rel_dev)
                if rel_dev>0.50:   #deviations above 50% of the max pulse width is neglected... (Considering stray)
                    max_end_indx_pos=i+1
                    break
            for i in range(len(neg_pulse)-1):
                rel_dev=(neg_pulse[i]-neg_pulse[i+1])/neg_pulse[i]
                #print("indx=",i," dtf=",dt_list[i+1]," dti=",dt_list[i]," rel_dev=",rel_dev)
                if rel_dev>0.50:   #deviations above 50% of the max pulse width is neglected... (Considering stray)
                    max_end_indx_neg=i+1
                    break
            if max_end_indx_pos>=0:
                pos_pulse=pos_pulse[:max_end_indx_pos]
            if max_end_indx_neg>=0:
                neg_pulse=neg_pulse[:max_end_indx_neg]

            mean_pos_pulse=np.mean(pos_pulse)
            mean_neg_pulse=np.mean(neg_pulse)
            mean_pulse=np.mean([mean_pos_pulse,mean_neg_pulse])
        elif len(dt_list)==1:
            if dt_list[0][1]==2:
                mean_neg_pulse=dt_list[0][0]
                mean_pulse=mean_neg_pulse
                
            if dt_list[0][1]==-2:
                mean_pos_pulse=dt_list[0][0]
                mean_pulse=mean_pos_pulse
                
            
        Duty_P=(mean_pos_pulse/(mean_pos_pulse+mean_neg_pulse))*100
        Duty_N=(mean_neg_pulse/(mean_pos_pulse+mean_neg_pulse))*100
        period=2*mean_pulse
        freq=(1/(2*mean_pulse))
        #print("Freq=",freq," +PWidth=",mean_pos_pulse," -PWidth=",mean_neg_pulse," Duty_P=",Duty_P," Duty_N",Duty_N)
        return freq,period,mean_pos_pulse,mean_neg_pulse,Duty_P,Duty_N
    
    def set_Units(self,data_list,measurable_flag):
        string_list=[]
        round_b=self.round_factor_is_set
        round_f=self.round_factor
        if measurable_flag==0:###volt
            for i in range(len(data_list)):
                
                if data_list[i]>=1000:
                    if round_b:
                        string_list.append(str(round(data_list[i]/1000,round_f))+" V")
                    else:
                        string_list.append(str(data_list[i]/1000)+" V")
                else:
                    if round_b:
                        string_list.append(str(round(data_list[i],round_f))+" mV")
                    else:
                        string_list.append(str(data_list[i])+" mV")
        
        elif measurable_flag==1:###timmings
            for i in range(len(data_list)):
                if i==0:
                    if data_list[i]>=1000:
                        if round_b:
                            string_list.append(str(round(data_list[i]/1000,round_f))+" KHz")
                        else:
                            string_list.append(str(data_list[i])+" KHz")
                    else:
                        if round_b:
                            string_list.append(str(round(data_list[i],round_f))+" Hz")
                        else:
                            string_list.append(str(data_list[i])+" Hz")
                if i>0 and i<=3:
                    unit_=""
                    time_s=data_list[i]*1e9
                    unit_="ns"
                    if time_s>800:
                        time_s=time_s/1000##in micros
                        unit_="us"
                        if time_s>800:
                            time_s=time_s/1000##in millis
                            unit_="ms"
                            if time_s>800:
                                time_s=time_s/1000##in Sec
                                unit_="s"
                    if round_b:
                        string_list.append(str(round(time_s,round_f))+unit_)
                    else:
                        string_list.append(str(time_s)+unit_)
                elif i>3:
                    if round_b:
                        string_list.append(str(round(data_list[i],round_f))+"%")
                    else:
                        string_list.append(str(data_list[i])+"%")
        return string_list

#############################################################EVENTS#############################################################
    def closeEvent(self,event):
        self.closed=True
        self.shown=False
        self.was_shown=True
        
        QtWidgets.QWidget.closeEvent(self,event)
    
    def showEvent(self,event):
        
        QtWidgets.QWidget.showEvent(self,event)
        #print("shown")
        
        if isinstance(self.win_pos, str)==False:
            self.move(self.win_pos)
        if self.tableWidget_mWin_size_same==False:
            self.resize(self.tableWidget.size().width()-self.main.popup_width_offset,self.tableWidget.size().height()-self.main.popup_height_offset)
        else:
            self.resize(self.tableWidget.size().width(),self.tableWidget.size().height())
        self.shown=True
        self.was_shown=False
        self.Each_Row_height_saved,self.Actual_win_height_0_row_saved,self.table_height_offset_saved=self.read_dimentions()
        self.closed=False
        
    def resizeEvent(self,event):
        QtWidgets.QWidget.resizeEvent(self, event)
        if self.shown==True and self.resize_by_func==False:
            #print("resize")
            self.tableWidget.resize(self.size().width(),self.size().height())
            self.tableWidget_mWin_size_same=True
        self.resize_by_func=False

    def moveEvent(self, e):
        if self.closed==False:
            self.win_pos=self.pos()
        super(Ui_MeasureWindow, self).moveEvent(e)

    def get_pos(self):
        if isinstance(self.win_pos, str):
            return [0 , 0]
        else:
            return self.win_pos.x(),self.win_pos.y()
        
    def set_pos(self,pos_):
        self.move(pos_[0],pos_[1])
    
    def get_config(self):
        if self.main.conf.Measurement_Window_Opacity!=[None,False]:
            self.setWindowOpacity(self.main.conf.Measurement_Window_Opacity)
        if self.main.conf.Measurement_Window_always_on_top!=[None,False]:
            
            if self.main.conf.Measurement_Window_always_on_top:
                self.setWindowFlags(QtCore.Qt.WindowFlags(QtCore.Qt.WindowStaysOnTopHint))
            else:
                self.setWindowFlags(QtCore.Qt.WindowFlags())
