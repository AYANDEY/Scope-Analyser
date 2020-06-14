import sys
import threading
import ctypes
from os import path,remove,unlink
import time
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt,QEvent,QPoint,QRect,QLine
from PyQt5.QtWidgets import QAbstractSlider, QApplication, QMainWindow, QToolBar
from PyQt5.QtGui import QMouseEvent
from PyQt5.uic import loadUi

from Ch_color_picker import Ui_Dialog as ch_color_diag
from info_window import Ui_infoWindow
import edited_navigationtoolbar2qt_main

from measurement_ import Ui_MeasureWindow
from mplsmall_main import *
from mplsmall_FFT import *
import extended_main as exmain
from fft_widget import FFT_handler
from config import config

import csv
import numpy as np
from matplotlib.lines import Line2D
from matplotlib import cbook, cm, colors as m_colors
from matplotlib.ticker import AutoMinorLocator
from PyQt5.Qt import QMetaMethod


class Ui_MainWindow(QtWidgets.QMainWindow):
    
    def __init__(self):
        QMainWindow.__init__(self)
        loadUi("main.ui",self)
        self.setWindowTitle("SCOPE ANALYSER")
        self.fft_panel_frame.setVisible(False)
        self.mplsmall_FFT.setVisible(False)
        self.main_panel_frame.setVisible(True)
        self.mplsmall.setVisible(True)
        self.setWindowIcon(QtGui.QIcon('res\\icon.ico'))
        self.debug_=False
        ###################################################CONFIG#################################################################
        self.conf=config(self)
        ####################################################BINDINGS##############################################################
        self.axes_list=[]
        self.plot_list=[]
        self.line_list=[]
        self.label_list=[]
        self.zeroline_list=[]
        self.zeroline_visibility_list=[]
        
        user32 = ctypes.windll.user32
        self.screensize = [user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)]
        
        self.set_sizes()
        self.main_ylim=[0,0]
        self.plot_opacity=0
        self.get_config(False)####not called by actionbutton 
        
        self.tabWidget.setStyleSheet("QTabWidget::pane {border-right: 0px;border-bottom: 0px;border-left:0px;border-top:0px;}")
        self.figure = self.MplWidget.figure
        self.plot_axes = self.figure.add_subplot(1, 1, 1)
        self.canvas=self.MplWidget.canvas
        self.plot_canvas=self.figure.canvas
        self.plot_axes.patch.set_facecolor('xkcd:black')
        self.plot_axes.spines['bottom'].set_color('white')
        self.plot_axes.spines['top'].set_color('white')
        self.plot_axes.spines['right'].set_color('white')
        self.plot_axes.spines['left'].set_color('white')
        self.plot_axes.tick_params(axis='x', colors='white')
        #self.plot_axes.tick_params(axis='y', colors='white')
        #self.plot_axes.legend(loc='upper right')
        self.plot_axes.patch.set_facecolor('xkcd:black')
        
        #self.plot_axes.set_xticklabels([])
        self.plot_axes.set_yticklabels([])
        self.plot_axes.grid(which='major', axis="both", alpha=0.9, linestyle='--',color='white')
        self.plot_axes.grid(which='minor', axis="both", alpha=0.5, linestyle='-.',color='white')
        self.plot_axes.tick_params(which='minor', length=4)
        self.plot_axes.yaxis.set_minor_locator(AutoMinorLocator(5))
        self.plot_axes.xaxis.set_minor_locator(AutoMinorLocator(5))
        self.plot_axes.set_ylim(self.main_ylim)
        self.plot_canvas.draw()
        
        #self.plot_fig = self.MplWidget.figure
        self.figure.tight_layout(pad=0, w_pad=None, h_pad=None)
        self.plot_canvas.mpl_connect('draw_event',self.On_Canvas_drawn)
        self.toolbar = edited_navigationtoolbar2qt_main.NavigationToolbar2QT(self.plot_canvas, self)
        
        self.toolbar.setStyleSheet("""
        QWidget {
            background-color:qlineargradient(spread:pad, x1:0.969955, y1:0.159, x2:0, y2:1, stop:0.0945274 rgba(92, 167, 206, 255), stop:1 rgba(255, 255, 255, 255))\n
            }
        """)
        
        self.exmain=exmain.exmain(self)
        self.addToolBar(QtCore.Qt.BottomToolBarArea,self.FFT_Widget.toolbar)
        self.FFT_Widget.toolbar.setVisible(False)
        
        self.addToolBar(QtCore.Qt.BottomToolBarArea,self.toolbar)
        self.actionOpen.triggered.connect(self.file_open)
        self.actionChannel_Color.triggered.connect(self.open_MenuColor_dialog)
        self.actionReload_config.triggered.connect(self.conf.load_config)
        self.actionAbout.triggered.connect(self.exmain.show_about)
        self.ch_name_col_list=[] #list to save channel name and color
        self.ch_volt_div_list=[]##list to save volt divsss
        self.Current_file_dialog=["",""]
        self.ch_color_edit=0
        self.col_edited=False
        self.file_edited=False
        self.all_plot_count =0
        self.x_limit=[]
        self.all_x_maxs=[0]
        self.all_x_mins=[0]
        self.x=[]
        self.y=[]
        self.x_scale=[]#will be used in shift
        self.y_scale=[]
        self.line_header=[]
        self.t_base_list=[]
        self.v_base_list=[]
        self.multiplier_index_list=[]
        
        self.matched_pos=-1
        self.default_color_list=["#ffff00","#00ffff","#ff00ff","#ff0000","#00ff00","#0000ff","#7d7d00","#007d7d","#7d007d","#7d7d00","#550000","#005500","#000055","#ffaa7f"]
        self.actionChannel_Information.triggered.connect(self.Open_Information_window)
        
        self.vdial_mouse_press=0
        self.shown_flag=True
        self.drawn=False
        self.rescalex_Extended_flag=False
        self.Window_minimised=False
        
        
        self.CH_select_combo.setEnabled(False) ###########enabled after 1st entry
        self.CH_enable_sw.setEnabled(False)
        self.multiplier_combo.setEnabled(False)
        self.replotting=0 #used in v/div adjust
        
        self.vdial.sliderReleased.connect(lambda: self.vdial_on_release(3))
        self.v_spinbx.val_entered.connect(lambda: self.vdial_on_release(2))
        self.v_unit_combo.currentIndexChanged.connect(self.v_unit_combo_changed)
        self.t_dial.sliderReleased.connect(lambda: self.t_dial_value_chg(0))
        self.t_spinbx.val_entered.connect(self.t_spin_entered)
        self.vdial.valueChanged.connect(self.vdial_val_changed)
        self.t_dial.valueChanged.connect(self.tdial_changed)
        self.bypass_canvas_draw_on_reScalePlot=False####while initialisation and setting v_base and t_base
        
        
        self.v_panel_Enabled(False)
        self.t_panel_Enabled(False)
        self.panel_Extra_Enabled(False)
        
        self.v_step_vals=[1,2,5,10,20,50,100,200,500,1,2,5,10,20,50,100] #1,2,5,10,20,50,100,200,500mv ,1,2,5,10 v
        self.t_step_vals=[2,4,8,20,40,80,200,400,800]  #2,4,8,20,40,80,200,400,800 ns,2,4,8,20,40,80,200,400,800 us,2,4,8,20,40,80,200,400,800 ms ,2,4,8,20,40s
        self.t_step_unit=["ns","us","ms","s"]
        self.t_step_indx=0
        self.t_unit_indx=0
        self.v_step_indx=0
        self.v_unit_indx=1
        self.current_volt_per_div = 2
        self.default_canvas_width=-1
        self.default_canvas_height=-1
        self.plotted_with_small_scaledsize=-1
        self.plotted_in_range=False
        self.initial_members_count=0
        
        self.plotted_out_of_range=False
        self.x_limit_rescaled_out_of_range=[0,0]
        self.x_limit_rescaled_in_range_small=[0,0]
        self.zoom_within_out_ranged=0
        
        self.x_canvas_out_ranged=0
        self.xtics_step_out_ranged=0
        self.t_val=-1
        
        
        
        self.popup_width_offset=int(self.screensize[0]*8.34*1e-3)
        self.popup_height_offset=int(self.screensize[1]*(21/1080))
        #self.popup_width_offset=17
        #self.popup_height_offset=21
        if self.conf.set_time_to_base_time!=None:
            self.settings_set_to_time_base=self.conf.set_time_to_base_time
        else:
            self.settings_set_to_time_base=True
        
        if self.conf.set_to_volt_base!=None:
            self.settings_set_to_volt_base=self.conf.set_to_volt_base
        else:
            self.settings_set_to_volt_base=True
        
        self.infoWin = Ui_infoWindow(self)
        self.mWin=Ui_MeasureWindow(self)
        
        self.fftW=FFT_handler(self)
        self.fftW.initialise()
        
        self.mplsmall.init_fig(self)#####################initialise small plot
        self.mplsmall_FFT.init_fig(self)
        
        
        '''if path.exists("set.sa"):
            self.settings_file=open("set.sa",'r+')
            self.settings_data=self.settings_file.readlines()
            
        else:
            if isinstance(self.win_pos, str)==False:
                self.move(self.win_pos)'''
        
        self.define_rubberband()
        
        self.MplWidget.scrollArea.horizontalScrollBar().valueChanged.connect(self.draw_rubberbands)
        
        
        self.cycle_g_key=0
        self.tabWidget.currentChanged.connect(self.tabChanged)
        self.main_panel_width=0
        self.firstRun=True
        #self.pushButton.clicked.connect(self.exmain.test_func)
        self.conf.get_position()

    #########################################@EVENT HANDLING#################################################
    
    def tabChanged(self):
        if self.tabWidget.currentIndex()==1:
            self.main_panel_frame.setVisible(False)
            self.toolbar.setVisible(False)
            self.mplsmall.setVisible(False)
            
            self.fft_panel_frame.setVisible(True)
            self.mplsmall_FFT.setVisible(True)
            self.FFT_Widget.toolbar.setVisible(True)
        else:
            self.fft_panel_frame.setVisible(False)
            self.FFT_Widget.toolbar.setVisible(False)
            self.mplsmall_FFT.setVisible(False)
            
            self.main_panel_frame.setVisible(True)
            self.mplsmall.setVisible(True)
            self.toolbar.setVisible(True)
    
    def keyPressEvent(self, event):
        if event.key()==Qt.Key_G:###g
            self.grid_view_cycle()
        elif event.key()==Qt.Key_Escape and self.exmain.picked_==True:
            try:
                self.exmain.picked_=False
                self.exmain.p.remove()
                self.refresh_plot()
            except Exception:
                self.printf_(sys.exc_info())
                self.printf_("LINE NO:",format(sys.exc_info()[-1].tb_lineno))
        elif event.key()==Qt.Key_Control:
            self.fftW.ctrl_handle(True)
        
    def keyReleaseEvent(self,e):
        if e.key()==Qt.Key_Control:
            self.fftW.ctrl_handle(False)
    
    def resizeEvent(self,event):
        QMainWindow.resizeEvent(self, event)
        self.printf_("resize")
        if self.shown_flag==True and hasattr(self, "resize_timer")==True:
            if self.resize_timer.is_alive():
                self.resize_timer.cancel()
                self.resize_timer=threading.Timer(0.5,self.resize_thread)
            else:
                self.resize_timer=threading.Timer(0.5,self.resize_thread)
            self.resize_timer.start()
        else:
            self.resize_timer=threading.Timer(0.5,self.resize_thread)
            self.resize_timer.start()
    
    def resize_thread(self):
        if self.tabWidget.currentIndex()==0:
            w = self.MplWidget.scrollArea.size().width()
            h = self.MplWidget.scrollArea.size().height()
        elif self.tabWidget.currentIndex()==1:
            w = self.FFT_Widget.scrollArea.size().width()
            h = self.FFT_Widget.scrollArea.size().height()
        
        self.resize_self(w,h)
        self.fftW.resize_self(self.shown_flag,w,h)

    def resize_self(self,w,h):
        if self.shown_flag==True and self.plotted_in_range==True and self.rescalex_Extended_flag!=True:
            if w>self.width_during_scaling:
                self.canvas.resize(w,(h-self.mplwidget_height_offset))
                self.mplsmall.canvas.resize(w,self.mplwidget_height_offset)
                self.printf_("R1")
            else:
                #self.canvas.resize(self.canvas.size().width(),(h-self.mplwidget_height_offset))
                self.mplsmall.canvas.resize(w,self.mplwidget_height_offset)
                self.printf_("R1E")
        elif self.rescalex_Extended_flag==True:
            self.rubberBand_reds_notDrawn=True
            if w>self.width_during_scaling:
                self.canvas.resize(w,(h-self.mplwidget_height_offset))
                self.mplsmall.canvas.resize(w,self.mplwidget_height_offset)
                self.printf_("R2_1")
            else:
                self.canvas.resize(self.canvas.size().width(),(h-self.mplwidget_height_offset))
                self.mplsmall.canvas.resize(w,self.mplwidget_height_offset)
                self.printf_("R2_2")
        elif self.shown_flag==True:##INIT
            self.canvas.resize(w,(h-self.mplwidget_height_offset))
            self.fftW.canvas.resize(w,h-self.mplwidget_height_offset)
            self.mplsmall.canvas.resize(w,self.mplwidget_height_offset)
            self.mplsmall_FFT.canvas.resize(w,self.mplwidget_height_offset)#########fftw and the small of it resized on __init__
            self.printf_("R3")
      
    def showEvent(self, event):
        QMainWindow.showEvent(self, event)
        QApplication.processEvents()
        self.printf_("Shown")
        self.shown_flag=True
        self.exmain.cursor_show_all()
        if self.Window_minimised==False:
            
            if self.tabWidget.currentIndex()==0:
                w = self.MplWidget.scrollArea.size().width()
                self.MplWidget.scrollArea.resize(w,(self.frame_3.size().height()-86))
                self.FFT_Widget.scrollArea.resize(w,(self.frame_3.size().height()-86))
                h = self.MplWidget.scrollArea.size().height()
            elif self.tabWidget.currentIndex()==1:
                w = self.FFT_Widget.scrollArea.size().width()
                self.MplWidget.scrollArea.resize(w,(self.frame_3.size().height()-86))
                self.FFT_Widget.scrollArea.resize(w,(self.frame_3.size().height()-86))
                h = self.FFT_Widget.scrollArea.size().height()
            
            self.default_canvas_width=w
            self.default_canvas_height=h
            self.canvas.resize(w,h)
            self.fftW.canvas.resize(w,h)
            self.printf_("ScrollArea:",w," ",h)
            self.mplsmall.canvas.resize(w,self.mplwidget_height_offset)
            self.mplsmall_FFT.canvas.resize(w,self.mplwidget_height_offset)
        elif self.Window_minimised==True:
            self.Window_minimised==False
    
    def changeEvent(self, event):
        
        if event.type() == QEvent.WindowStateChange:
            if self.windowState() & Qt.WindowMinimized:
                self.Window_minimised=True
    
    def closeEvent(self,e):
        #self.save_win_pos()
        self.conf.save_position()
        if self.infoWin.closed==False:
            self.infoWin.close()
            self.infoWin.deleteLater()
        if self.mWin.closed==False:
            self.mWin.close()
            self.mWin.deleteLater()
        if self.exmain.aboutwin.shown==True:
            self.exmain.aboutwin.close()
            self.exmain.aboutwin.deleteLater()
        if self.fftW.zoomwin.shown==True:
            self.fftW.zoomwin.close()
            self.fftW.zoomwin.deleteLater()
        self.deleteLater()
        return super(Ui_MainWindow,self).closeEvent(e)
    
    def On_Canvas_drawn(self,draw_event):
        self.printf_("Draw_evt")
        
        if self.canvas.size().width()<self.tabWidget.size().width():
            self.canvas.resize(self.tabWidget.size().width(),self.tabWidget.size().height()-54)
            self.mplsmall.canvas.resize(self.canvas.size().width(),self.mplwidget_height_offset)
         
        for i in range(self.all_plot_count):
            self.ch_name_col_list[i][1]=str(m_colors.to_hex(self.axes_list[i].get_lines()[0].get_color()))
            #self.plot_axes.get_lines()[i].set_label(self.ch_name_col_list[i][0]) ##bug## when label changed from navigator tooolbar  initially changes but target was to make it unchangable
        self.px2pt=self.plot_axes.transData.inverted()################define axes transformation on resize
        self.pt2px=self.plot_axes.transData
        self.mplsmall_pt2px=self.mplsmall.axes.transData
        self.mplsmall_px2pt=self.mplsmall.axes.transData.inverted()
        self.draw_rubberbands()
        self.exmain.refresh_bounds()
        if self.exmain.picked_==True:  #if any plot picked to mobve and somehow redrawn without moving it then the point is removed.
            try:
                self.exmain.p.remove()
            except Exception:
                self.printf_(sys.exc_info())
                self.printf_("LINE NO:",format(sys.exc_info()[-1].tb_lineno))
        if self.drawn==False:
            self.exmain.cursor_show_all()
        self.exmain.cursor_refresh_on_redraw()
        #self.setProgress(100,True)
        
        if self.rescalex_Extended_flag:
            half_page_step=int(self.MplWidget.scrollArea.horizontalScrollBar().pageStep()/2)
            self.printf_("MID_TO_SET",self.set_scrl_val)#####midCHECK
            self.MplWidget.scrollArea.horizontalScrollBar().setValue(self.set_scrl_val-half_page_step)
        
        self.drawn=True
        if self.firstRun==True:
            ytick=self.plot_axes.get_yticks(minor=False)
            self.ydiv=ytick[1]-ytick[0]
            self.printf_("ydiv",self.ydiv)
            self.firstRun=False

        for i in range(len(self.zeroline_visibility_list)):
            self.exmain.draw_zeroline(i,self.zeroline_visibility_list[i])
        
        
        #self.setProgress(0,False)
    
    def t_spin_entered(self):
        if self.t_spinbx.value()!=self.t_val:
            self.t_dial_value_chg(1)
        elif self.t_unit_combo.currentIndex()!=self.t_unit_indx:
            self.t_dial_value_chg(1)
    
    def zline_toggled(self):
        zeroline_enabled=self.zero_line_enabled_sw.isChecked()
        CH_selected=self.CH_select_combo.currentText()
        member_match=-1
        member_matched=0
        self.printf_(self.ch_volt_div_list)
        for members in self.ch_volt_div_list:
            member_match+=1
            if members[0]==CH_selected:
                self.printf_("Channel selected:",members[0])
                member_matched=1
                break
        if member_matched==1:
            self.exmain.draw_zeroline(member_match,zeroline_enabled)
            self.zeroline_visibility_list[member_match]=zeroline_enabled
    ###############################################@FILE OPEN@###################################

    def file_open(self,MainWindow):
        if self.fftW.zoomwin.isVisible():
            self.fftW.zoomwin.close()
        self.Current_file_dialog = QtWidgets.QFileDialog.getOpenFileName(self,"Select CSV file",self.last_folder,"CSV files( *.csv)")
        if self.Current_file_dialog[0] != "":
            self.last_folder=path.dirname(self.Current_file_dialog[0])
            self.dialog = QtWidgets.QDialog()
            
            self.dialog.ui = ch_color_diag()
            self.dialog.ui.setupUi(self.dialog)
            if (self.dialog.ui.comboBox.count()>self.all_plot_count):
                self.dialog.ui.comboBox.setCurrentIndex(self.all_plot_count)
            else:
                run_num = self.all_plot_count-self.dialog.ui.comboBox.count()+1
                combo_count=self.dialog.ui.comboBox.count()+1
                for i in range(run_num):
                    self.dialog.ui.comboBox.addItem("CH"+str(combo_count+i))
                
                self.dialog.ui.comboBox.setCurrentIndex(self.all_plot_count)
            
            if self.all_plot_count<len(self.default_color_list):
                self.dialog.ui.color_btn.setStyleSheet("background-color:"+self.default_color_list[self.all_plot_count])
            else:
                
                self.dialog.ui.color_btn.setStyleSheet("background-color:#ffffff")
            
            self.dialog.ui.ok_btn.clicked.connect(self.Color_dialog_ok)
            self.dialog.ui.Cancel_btn.clicked.connect(self.Color_dialog_Cancel)
            self.dialog.ui.color_btn.clicked.connect(self.color_pick)
            self.dialog.ui.comboBox.currentIndexChanged.connect(self.color_combo_change)
            self.dialog.exec_()
        else:
            self.printf_("No file to plot")
    
    ########################################@File Open COLOLR DIALOG@#####################################
    
    def Color_dialog_ok(self):
        
        self.Current_ch_name= str(self.dialog.ui.comboBox.currentText())
        btn_color = self.dialog.ui.color_btn.palette().color(1).name(0)
        self.printf_(self.Current_ch_name)
        self.printf_(btn_color)
        self.dialog.done(1)
        
        self.disconnect_receivers(self.CH_enable_sw,self.CH_enable_sw.toggled)
        
        self.plot_from_path(self.Current_file_dialog[0],self.Current_ch_name,btn_color) #########funtion to plot form file location, chName, ch Color
    
    def Color_dialog_Cancel(self):
        self.printf_("No changes Done")
        self.dialog.done(0)
    
    def color_pick(self):
        self.ch_color= QtWidgets.QColorDialog.getColor()
        self.Current_ch_color=self.ch_color.name(0)
        if str(self.ch_color.name(0)) != "#000000":
            self.printf_("background-color:"+self.Current_ch_color)
            self.dialog.ui.color_btn.setStyleSheet("background-color:"+self.Current_ch_color)
        else:
            self.printf_("No color Selected")
    
    def color_combo_change(self):
        ch_name=str(self.dialog.ui.comboBox.currentText())
        matched_pos=-1
        match=0
        for members in self.ch_name_col_list:
            matched_pos += 1
            if members[0]==ch_name: ##if current channel matches with already plotted channel @MEMBER_MATCH
                ch_color=members[1]
                match=1
                self.dialog.ui.color_btn.setStyleSheet("background-color:"+ch_color)
                break
        if match==0:
            if self.all_plot_count<len(self.default_color_list):
                self.dialog.ui.color_btn.setStyleSheet("background-color:"+self.default_color_list[self.all_plot_count])
            else:
                self.dialog.ui.color_btn.setStyleSheet("background-color:#ffffff")
    
    #######################################@MENU EDIT COLOLR DIALOG@#######################################
    
    def open_MenuColor_dialog(self):  #pops in when window channel color select button is triggered
        self.menu_col_dialog = QtWidgets.QDialog()
        self.menu_col_dialog.ui = ch_color_diag()
        self.menu_col_dialog.ui.setupUi(self.menu_col_dialog)
        self.menu_col_dialog.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.menu_col_combo_change()
        if (self.menu_col_dialog.ui.comboBox.count()<=self.all_plot_count):
            run_num = self.all_plot_count-self.menu_col_dialog.ui.comboBox.count()
            self.printf_("COMBOCOUNT:",self.menu_col_dialog.ui.comboBox.count())
            self.printf_("ALL PLOT COUNT",self.all_plot_count)
            self.printf_("RUN_NUM",run_num)
            combo_count=self.menu_col_dialog.ui.comboBox.count()+1
            for i in range(run_num):
                self.menu_col_dialog.ui.comboBox.addItem("CH"+str(combo_count+i))
        
        self.menu_col_dialog.ui.ok_btn.clicked.connect(self.MenuColor_dialog_ok)
        self.menu_col_dialog.ui.Cancel_btn.clicked.connect(self.MenuColor_dialog_Cancel)
        self.menu_col_dialog.ui.comboBox.currentIndexChanged.connect(self.menu_col_combo_change)
        self.menu_col_dialog.ui.color_btn.clicked.connect(self.MenuColor_pick)
        self.menu_col_dialog.exec_()

    def MenuColor_dialog_ok(self):
        self.Current_ch_name= str(self.menu_col_dialog.ui.comboBox.currentText())
        btn_color = self.menu_col_dialog.ui.color_btn.palette().color(1).name(0)
        self.printf_(self.Current_ch_name)
        self.printf_(btn_color)
        self.menu_col_dialog.done(1)
        self.ch_color_edit=1
        if self.Current_file_dialog[0] !="":
            #self.setProgress(0,True)
            self.plot_from_path(self.Current_file_dialog[0],self.Current_ch_name,btn_color)
    
    def MenuColor_dialog_Cancel(self):
        self.menu_col_dialog.done(1)

    def MenuColor_pick(self):
        self.ch_color= QtWidgets.QColorDialog.getColor()
        self.Current_ch_color=self.ch_color.name(0)
        if str(self.ch_color.name(0)) != "#000000":
            
            self.printf_("background-color:"+self.Current_ch_color)
            self.menu_col_dialog.ui.color_btn.setStyleSheet("background-color:"+self.Current_ch_color)
        else:
            
            self.printf_("No color Selected")

    def menu_col_combo_change(self):
            ch_name=str(self.menu_col_dialog.ui.comboBox.currentText())
            matched_pos=-1
            match=0
            for members in self.ch_name_col_list:
                matched_pos += 1
                if members[0]==ch_name: ##if current channel matches with already plotted channel @MEMBER_MATCH
                    ch_color=members[1]
                    match=1
                    self.menu_col_dialog.ui.color_btn.setStyleSheet("background-color:"+ch_color)
                    break
            if match==0:
                if self.all_plot_count<len(self.default_color_list):
                    self.menu_col_dialog.ui.color_btn.setStyleSheet("background-color:"+self.default_color_list[self.all_plot_count])
                else:
                    self.menu_col_dialog.ui.color_btn.setStyleSheet("background-color:#ffffff")

    #########################################@INFORMATION WINDOW@##############################################
    def Open_Information_window(self):
        #MainWindow.hide()
        row_num=0
        needs_size_update=False
        if self.initial_members_count!=len(self.ch_name_col_list) or self.col_edited==True or self.file_edited==True:
            if self.infoWin.shown==True:
                Each_Row_height,Actual_win_height_0_row,table_height_offset=self.info_win_read_dimentions()
            elif self.infoWin.was_shown:
                Each_Row_height=self.infoWin.Each_Row_height_saved
                Actual_win_height_0_row=self.infoWin.Actual_win_height_0_row_saved
                table_height_offset=self.infoWin.table_height_offset_saved
                
            for i in range(self.infoWin.tableWidget.rowCount()):
                self.infoWin.tableWidget.removeRow(0)
            self.infoWin.first_run=True
            needs_size_update=True
        
        if self.infoWin.first_run==True:
            for members in self.ch_name_col_list:
                self.infoWin.tableWidget.insertRow(row_num)
                for i in range(len(members)):
                    if i!=1:
                        self.infoWin.tableWidget.setItem(row_num,i,QtWidgets.QTableWidgetItem(members[i]))
                    else:
                        self.infoWin.tableWidget.setItem(row_num,i,QtWidgets.QTableWidgetItem(members[i]))
                        self.infoWin.tableWidget.item(row_num,i).setBackground(QtGui.QColor(members[i]))
                        
                    self.infoWin.tableWidget.item(row_num,i).setTextAlignment(Qt.AlignCenter)
                    self.printf_(row_num,"  ",i,"  ",members[i])
                row_num +=1
            self.initial_members_count=row_num
            self.infoWin.tableWidget.resizeColumnsToContents()
            self.infoWin.tableWidget.resizeRowsToContents()
            self.infoWin.first_run=False
        
        if needs_size_update:
            if self.infoWin.shown==True or self.infoWin.was_shown==True:
                TH=int((self.infoWin.tableWidget.rowCount()*Each_Row_height)+Actual_win_height_0_row)
                self.printf_("TH=",TH)
                self.infoWin.resize_by_func=True
                #self.infoWin.tableWidget_Infow_size_same=False
                self.infoWin.tableWidget.resize(self.infoWin.tableWidget.size().width(),TH+table_height_offset)
                self.infoWin.resize(self.infoWin.size().width(),TH)
                self.printf_("InfoWin Size Updated")
        
        self.infoWin.activateWindow()
        self.infoWin.show()
    
    def info_win_read_dimentions(self):
        info_Win_Height=self.infoWin.size().height()
        table_height=self.infoWin.tableWidget.height()
        table_height_offset=table_height-info_Win_Height
        T_row_Height=0
        row_count=self.infoWin.tableWidget.rowCount()
        for i in range(row_count):
            T_row_Height+=self.infoWin.tableWidget.rowHeight(i)
        Each_Row_height=T_row_Height/row_count
        Actual_win_height_0_row=info_Win_Height-T_row_Height
        self.printf_("AWH=",Actual_win_height_0_row," Prow_count=",row_count,"PT_row_Height=",T_row_Height,"info_Win_Height=",info_Win_Height,"table_height=",table_height)
        return Each_Row_height,Actual_win_height_0_row,table_height_offset
    ############################################MEASUREMENT_WINDOW#############################################
    def Open_measure_window(self):
        measure_Thread=threading.Thread(target=self.mWin.Update_UI())
        measure_Thread.start()
        measure_Thread.join()
        self.mWin.show()
        
    #############################################@PLOTTING@####################################################    
    def plot_from_path(self,path,ch_name,ch_color):
        ####TODO drawing Diag
        self.member_match=0      #bool to check if Channel_name_color_array (self.ch_name_col_list) contains the channel i.e currently showed on plot @MEMBER_MATCH
        self.matched_pos=-1
        
        for members in self.ch_name_col_list:
            self.printf_(len(members))
            self.matched_pos += 1
            if members[0]==ch_name: ##if current channel matches with already plotted channel @MEMBER_MATCH
                members[1]=ch_color
                if self.ch_color_edit==1:
                    path=members[2] ###saved path will be used if channel is on edit @CHANNEL_EDIT
                else:
                    members[2]=path ##else 'path' passed to this function will be used as its new path  @CHANNEL_EDIT
                self.printf_("Member_match",self.matched_pos)
                self.printf_(path)
                self.member_match=1
                break
        
        if self.member_match==0 and self.ch_color_edit==0: # if member doesnot match and is a fresh entry @@@FRESH ENTRY
            self.ch_name_col_list.append([ch_name,ch_color,path]) ##########appended to 
            self.ch_volt_div_list.append([ch_name,2,2,1,0,0])###ch_name,volt/div,volt_unit_index(v_unit_indx),enabled_bool,SHIFT_bool,yshift
            #############Disconnections###############
            
            self.disconnect_receivers(self.CH_select_combo, self.CH_select_combo.currentIndexChanged)
            self.disconnect_receivers(self.CH_move_combo, self.CH_move_combo.currentIndexChanged)
            self.disconnect_receivers(self.fft_ch_select, self.fft_ch_select.currentIndexChanged)
            self.disconnect_receivers(self.CH_cursor_combo,self.CH_cursor_combo.currentIndexChanged )
            self.disconnect_receivers(self.multiplier_combo, self.multiplier_combo.currentIndexChanged)
            self.disconnect_receivers(self.zero_line_enabled_sw, self.zero_line_enabled_sw.toggled)
            
            #############Changes###############
            self.fft_ch_select.addItem(ch_name)
            self.fft_ch_select.setCurrentIndex(self.fft_ch_select.count()-1)
            self.CH_move_combo.addItem(ch_name)
            self.CH_move_combo.setCurrentIndex(self.CH_move_combo.count()-1)
            self.CH_cursor_combo.addItem(ch_name)
            self.CH_cursor_combo.setCurrentIndex(self.CH_cursor_combo.count()-1)
            self.CH_select_combo.addItem(ch_name)
            self.CH_select_combo.setCurrentIndex(self.CH_select_combo.count()-1)
            self.multiplier_combo.setCurrentIndex(0)
            
            #############Connections###############
            self.CH_move_combo_connection=self.CH_move_combo.currentIndexChanged.connect(self.exmain.CH_move_combo_change)
            self.fft_ch_select_connection=self.fft_ch_select.currentIndexChanged.connect(self.fftW.fft_CH_changed)
            self.CH_cursor_combo_connection=self.CH_cursor_combo.currentIndexChanged.connect(self.exmain.CH_cursor_combo_change)
            self.multiplier_combo_connection=self.multiplier_combo.currentIndexChanged.connect(self.onMultiplierChanged)
           
            
            self.all_plot_count += 1
        
        self.printf_( self.ch_name_col_list)
        if self.member_match==0 and self.ch_color_edit==1:
            self.ch_color_edit=0
            return
        
        if self.all_plot_count==1:
            if self.ch_color_edit==0:
                if self.matched_pos==0 and self.member_match==1:
                    self.disconnect_receivers(self.CH_select_combo, self.CH_select_combo.currentIndexChanged)
                    self.disconnect_receivers(self.zero_line_enabled_sw, self.zero_line_enabled_sw.toggled)
                    
                    self.axes_list[0].clear()
                    self.line_list=[]
                    self.plot_list=[]
                    self.axes_list=[]
                    self.x=[]
                    self.y=[]
                    self.x_scale=[]
                    self.y_scale=[]
                    self.exmain.hide_zeroline(0)
                    self.zeroline_list=[]
                    self.multiplier_index_list=[]
                    self.line_header=[]
                    self.file_edited=True
                    self.mplsmall.rem_plot_0()
                    self.fftW.rem_plot_0()
                    self.mplsmall_FFT.rem_plot_0()
                    self.zeroline_visibility_list=[]
                    
                xi=[]
                yi=[]
                line_headeri=[]
                with open (path,'r') as csvfile:
                    lines= csv.reader(csvfile, delimiter=',')
                    line_num=0
                    for row in lines:
                        if line_num <= 2:
                            for i in range(len(row)):
                                line_headeri.append(str(row[i]))
                        else:
                            xi.append(float(row[0]))
                            yi.append(float(row[1]))
                        line_num += 1
                
                ax=self.plot_axes.twiny()
                plot_ = ax.plot(xi,yi,color=ch_color,alpha=self.plot_opacity,label=ch_name,picker=5) ##  ax.get_lines()[0].set_color("black")
                self.x_limit=[min(xi),max(xi)]
                self.all_x_mins[0]=self.x_limit[0]
                self.all_x_maxs[0]=self.x_limit[1]
                ax.set_xlim(self.x_limit)
                self.selected_ch=ch_name
                ax.patch.set_facecolor('xkcd:black')
                ax.spines['bottom'].set_color('white')
                ax.spines['top'].set_color('white')
                ax.spines['right'].set_color('white')
                ax.spines['left'].set_color('white')
                #ax.set_xticklabels([])
                #ax.grid(False)
                ax.set_yticklabels([])
                self.axes_list.append(ax)
                self.plot_list.append(plot_)
                self.line_list.append(plot_[0])
                self.label_list.append(plot_[0].get_label())
                
                z_line=self.exmain.def_zeroline(1,ch_color)
                self.zeroline_list.append(z_line)
                                
                self.multiplier_index_list.append(0)
                
                t_base,v_base=self.parse_header(line_headeri)
                
                self.t_base_list.append(t_base)
                self.v_base_list.append(v_base)
                
                self.plot_axes.legend().set_visible(False)
                self.figure.legends=[]
                self.figure.legend(self.line_list,self.label_list,loc='upper right')
                self.x.append(xi)
                self.x_scale.append(xi)
                self.y.append(yi)
                self.y_scale.append(yi)
                self.line_header.append(line_headeri) ##########points taken to memory
                #self.setProgress(25,True)
                
                self.set_t_base()
                self.set_v_base(v_base)
                
                self.bypass_canvas_draw_on_reScalePlot=True
                ####################matplotlib_small#######################
                self.mplsmall.addplot_(xi,yi,ch_color,self.x_limit)
                self.mplsmall.refresh_plot()
                self.fftW.calculate_fft(xi,yi,ch_color,True)
                ####################matplotlib_small#######################
                self.vdial_on_release(2)
                self.t_dial_value_chg(1)
                '''self.plot_axes.set_xticks(np.arange(self.x_limit[0],self.x_limit[1],step=(self.x_limit[1]-self.x_limit[0])/5))####@TO DO
                if self.matched_pos==0 and self.member_match==1:
                    self.plot_axes.yaxis.set_minor_locator(AutoMinorLocator(5))
                #############@@@@@TO DO : defaut scale is to be set according to base time scale
                self.plot_axes.set_xlim(self.x_limit)
                if self.plotted_out_of_range==True:
                    self.plot_canvas.resize(self.default_canvas_width,self.default_canvas_height)
                else:
                    self.plot_canvas.draw_idle()
                '''
                self.v_panel_Enabled(True)
                self.t_panel_Enabled(True)
                self.panel_Extra_Enabled(True)
                
                self.CH_enable_sw.setChecked(True)
                
                self.zero_line_enabled_sw.setChecked(self.exmain.zeroline_default_enabled)
                self.zeroline_visibility_list.append(self.exmain.zeroline_default_enabled)
                #self.zline_to_draw=[True,0,self.exmain.zeroline_default_enabled]
                #self.exmain.draw_zeroline(0,self.exmain.zeroline_default_enabled)
                
                self.combo_connect=self.CH_select_combo.currentIndexChanged.connect(self.CH_select_combo_change)
                self.CH_enable_sw.toggled.connect(self.CH_enabled_changed)
                self.zline_connection=self.zero_line_enabled_sw.toggled.connect(self.zline_toggled)
                self.bypass_canvas_draw_on_reScalePlot=False
                
                
            else:
                #self.plot_axes.clear()
                #color edit for one 
                self.printf_("Editing One")
                self.axes_list[0].get_lines()[0].set_color(ch_color)
                self.axes_list[0].legend().set_visible(False)
                self.plot_axes.legend().set_visible(False)
                self.figure.legends=[]
                self.figure.legend(self.line_list,self.label_list,loc='upper right')
                self.plot_axes.yaxis.set_minor_locator(AutoMinorLocator(5))
                self.refresh_plot()
                self.ch_color_edit=0
                self.col_edited=True
                
                self.exmain.hide_zeroline(0)
                
                z_line=self.exmain.def_zeroline(1,ch_color)
                self.zeroline_list[0]=z_line
                self.zero_line_enabled_sw.setChecked(self.zeroline_visibility_list[self.matched_pos])
                #self.zline_to_draw=[True,0,self.zeroline_visibility_list[self.matched_pos]]
                #self.exmain.draw_zeroline(0,self.zeroline_visibility_list[self.matched_pos])
                ####################matplotlib_small#######################
                self.mplsmall.change_color(0,ch_color)
                self.mplsmall.refresh_plot()
                
                ####################FFT window############################
                self.fftW.change_color(0,ch_color)
                self.mplsmall_FFT.change_color(0,ch_color)
                self.mplsmall_FFT.plot_refresh()
                
            self.exmain.CH_cursor_combo_change()
            
        else:
            self.multiple_plotting(path,ch_name,ch_color,self.member_match,self.ch_color_edit)
    
    def multiple_plotting(self,path,ch_name,ch_color,edit_flag,ch_color_edit):
        xi=[]
        yi=[]
        line_headeri=[]
        with open (path,'r') as csvfile:
            lines= csv.reader(csvfile, delimiter=',')
            line_num=0
            for row in lines:
                if line_num <= 2:
                    for i in range(len(row)):
                        line_headeri.append(str(row[i]))
                else:
                    xi.append(float(row[0]))
                    yi.append(float(row[1]))
                line_num += 1
        self.printf_("On_plotting_multiple")
        self.printf_("EDIT_FLAG",edit_flag)
        self.printf_("CHANNEL_COLOR_EDIT:",ch_color_edit)
        xmin=min(xi)
        xmax=max(xi)
        self.printf_("limit:",self.x_limit[0],self.x_limit[1])
        t_base,v_base=self.parse_header(line_headeri)
        
        if edit_flag!=1 and  ch_color_edit==0:
            ###########################for fresh entry 
            ax= self.plot_axes.twiny()
            plot_ =ax.plot(xi,yi,color=ch_color,alpha=self.plot_opacity,label=ch_name,picker=5)
            ax.spines['bottom'].set_color('white')
            ax.spines['top'].set_color('white')
            ax.spines['right'].set_color('white')
            ax.spines['left'].set_color('white')
            self.CH_select_combo.setCurrentIndex(self.CH_select_combo.count()-1)
            self.t_base_list.append(t_base)
            self.v_base_list.append(v_base)
            
            self.axes_list.append(ax)
            self.plot_list.append(plot_)
            self.line_list.append(plot_[0])
            self.label_list.append(plot_[0].get_label())
            
            z_line=self.exmain.def_zeroline(self.all_plot_count, ch_color)
            self.zeroline_list.append(z_line)
            
            ax.legend().set_visible(False)
            
            self.all_x_maxs.append(xmax)
            self.all_x_mins.append(xmin)
            self.x_limit[0]=min(self.all_x_mins)
            self.x_limit[1]=max(self.all_x_maxs)
            
            self.x.append(xi)
            self.x_scale.append(xi)  #x_scale and y_scale holds the changed data set while volt/div is changed
            self.y.append(yi)
            self.y_scale.append(yi)
            self.line_header.append(line_headeri)
            self.multiplier_index_list.append(0)
            self.zero_line_enabled_sw.setChecked(self.exmain.zeroline_default_enabled)
            self.zeroline_visibility_list.append(self.exmain.zeroline_default_enabled)
            #self.exmain.draw_zeroline(self.all_plot_count-1,self.exmain.zeroline_default_enabled)
            #self.zline_to_draw=[True,self.all_plot_count-1,self.exmain.zeroline_default_enabled]
            
            ####################matplotlib_small#######################
            self.mplsmall.addplot_(xi,yi,ch_color,self.x_limit)###########plot added to small plot
            #####################fft_window#####################
            self.fftW.calculate_fft(xi,yi,ch_color,True)
            
        elif edit_flag==1 and ch_color_edit==0:
            ###############while previous entry is on edit
            self.printf_("Matched_pos:",self.matched_pos)
            self.CH_select_combo.setCurrentIndex(self.matched_pos)
            #self.plot_axes.clear()
            
            self.x[self.matched_pos]=xi
            self.y[self.matched_pos]=yi
            self.ch_name_col_list[self.matched_pos][1]=ch_color
            self.line_header[self.matched_pos]=line_headeri
            
            self.all_x_maxs[self.matched_pos]=xmax
            self.all_x_mins[self.matched_pos]=xmin
            self.x_limit[0]=min(self.all_x_mins)
            self.x_limit[1]=max(self.all_x_maxs)
            
            self.x_scale[self.matched_pos]=xi
            self.y_scale[self.matched_pos]=yi
            self.t_base_list[self.matched_pos]=t_base
            self.v_base_list[self.matched_pos]=v_base
            self.multiplier_index_list[self.matched_pos]=0
            
            self.axes_list[self.matched_pos].clear()
            col=QtGui.QColor(ch_color)
            col.setAlpha(self.plot_opacity)
            plot_=self.axes_list[self.matched_pos].plot(xi,yi, color=ch_color , alpha=self.plot_opacity,label=self.ch_name_col_list[self.matched_pos][0],picker=5)
            self.axes_list[self.matched_pos].set_yticklabels([])
            self.axes_list[self.matched_pos].set_xlim(self.x_limit[0],self.x_limit[1])
            self.line_list[self.matched_pos]=plot_[0]
            self.plot_axes.set_xlim(self.x_limit[0],self.x_limit[1])
            self.printf_("limit:",self.x_limit[0],self.x_limit[1])
            
            self.exmain.hide_zeroline(self.matched_pos)
            
            z_line=self.exmain.def_zeroline(self.matched_pos,ch_color)
            self.zeroline_list[self.matched_pos]=z_line
            self.zero_line_enabled_sw.setChecked(self.zeroline_visibility_list[self.matched_pos])
            #self.exmain.draw_zeroline(self.matched_pos,self.zeroline_visibility_list[self.matched_pos])
            #self.zline_to_draw=[True,self.matched_pos,self.zeroline_visibility_list[self.matched_pos]]
            
            self.plot_axes.yaxis.set_minor_locator(AutoMinorLocator(5))
            self.printf_(self.ch_name_col_list[i][0],self.ch_name_col_list[i][2],self.ch_name_col_list[i][1])
            self.file_edited=True
            
            self.mplsmall.edit_plot(self.matched_pos,xi,yi,ch_color,self.x_limit)
            self.fftW.calculate_fft_update(self.matched_pos,xi,yi,ch_color)
            
        elif edit_flag==1 and ch_color_edit==1:##################color Edit##############
            self.printf_("Matched_pos:",self.matched_pos)
            self.axes_list[self.matched_pos].get_lines()[0].set_color(ch_color)
            self.ch_color_edit=0
            self.col_edited=True
            self.mplsmall.change_color(self.matched_pos,ch_color)
            self.fftW.change_color(self.matched_pos,ch_color)
            self.mplsmall_FFT.change_color(self.matched_pos,ch_color)
            
            self.exmain.hide_zeroline(self.matched_pos)
            
            z_line=self.exmain.def_zeroline(self.all_plot_count,ch_color)
            self.zeroline_list[self.matched_pos]=z_line
            self.zero_line_enabled_sw.setChecked(self.zeroline_visibility_list[self.matched_pos])
            #self.exmain.draw_zeroline(self.matched_pos,self.zeroline_visibility_list[self.matched_pos])
            #self.zline_to_draw=[True,self.matched_pos,self.zeroline_visibility_list[self.matched_pos]]
            
        #self.plot_axes.legend().set_visible(False)
        self.CH_enable_sw.setEnabled(True)
        self.figure.legends=[]
        self.figure.legend(self.line_list,self.label_list,loc='upper right')
        
        for i in range(self.all_plot_count):  ####x_limit of all plots are made same
            self.axes_list[i].set_xlim(self.x_limit)
            
        if self.settings_set_to_time_base==True:############kept for settings
            self.set_t_base()
        if self.settings_set_to_volt_base==True:############kept for settings
            self.set_v_base(v_base)
        
        self.bypass_canvas_draw_on_reScalePlot=True
        #self.setProgress(25,True)
        
        self.vdial_on_release(2)##set to base volt
        self.t_dial_value_chg(1)##set to base time
        
        self.mplsmall.refresh_plot()################small plot refreshed
        self.mplsmall_FFT.plot_refresh()
        
        self.combo_connect=self.CH_select_combo.currentIndexChanged.connect(self.CH_select_combo_change)
        self.CH_enable_sw.toggled.connect(self.CH_enabled_changed)
        
        self.zline_connection=self.zero_line_enabled_sw.toggled.connect(self.zline_toggled)
        
        if edit_flag!=1 and  ch_color_edit==0 and self.infoWin.shown==True:
            self.Open_Information_window()
        self.exmain.CH_cursor_combo_change() ####set channel  cursor combo color and take values
        self.bypass_canvas_draw_on_reScalePlot=False
    
    def parse_header(self,line_header_):
        t_base=0
        v_base=0
        has_timebase=False
        has_vbase=False
        self.printf_(line_header_)
        for member in line_header_:
            if 'timebase=' in member:
                timebase_member=member
                has_timebase=True
            if 'voltbase=' in member:
                vbase_member=member
                has_vbase=True
        
        if has_timebase:
            try:
                baseindx= timebase_member.index('timebase=')
                unit_start_indx=timebase_member.index('(')
                t_base=int(timebase_member[baseindx+9:unit_start_indx])
                t_base_unit=timebase_member[unit_start_indx+1:len(timebase_member)-1]
                if t_base_unit=="ps":
                    t_base=t_base/1e3
                elif t_base_unit=="ns":
                    pass
                elif t_base_unit=="us":
                    t_base=t_base*1e3
                elif t_base_unit=="ms":
                    t_base=t_base*1e6
                elif t_base_unit=="s":
                    t_base=t_base*1e9
            except Exception:
                self.printf_(sys.exc_info())
        if has_vbase:
            baseindx= vbase_member.index('voltbase=')
            unit_start_indx=vbase_member.index('(')
            v_base=int(vbase_member[baseindx+9:unit_start_indx])
            v_base_unit=vbase_member[unit_start_indx+1:len(timebase_member)-1]
            if v_base_unit=="pV":
                v_base=v_base/1e6
            elif v_base_unit=="nV":
                v_base=v_base/1e3
            elif v_base_unit=="uV":
                pass
            elif v_base_unit=="mV":
                v_base=v_base*1e3
            elif v_base_unit=="V":
                v_base=v_base*1e6
                    
        return t_base,v_base####t_base in nanosec, v_base in uV
    
    #######################################Volt/division changes and CH selection##############################
    
    def CH_select_combo_change(self):
        self.CH_select_combo.setEnabled(False)
        try:
            threading.Thread(target=self.CH_select_combo_change_thread).start()
        except Exception:
            self.printf_(sys.exc_info())
            self.printf_("LINE NO:",format(sys.exc_info()[-1].tb_lineno))
    
    def CH_select_combo_change_thread(self):
        
        CH_selected=self.CH_select_combo.currentText()
        member_match=-1
        member_matched=0
        self.printf_(self.ch_volt_div_list)
        for members in self.ch_volt_div_list:
            member_match+=1
            if members[0]==CH_selected:
                self.printf_("Channel selected:",members[0])
                member_matched=1
                break
        if member_matched==1:
            self.disconnect_receivers(self.v_unit_combo,self.v_unit_combo.currentIndexChanged)
            self.zero_line_enabled_sw.toggled.disconnect(self.zline_connection)
            self.multiplier_combo.currentIndexChanged.disconnect(self.multiplier_combo_connection)
            
            
            current_volt_per_div=self.ch_volt_div_list[member_match][1]
            self.v_spinbx.setValue(current_volt_per_div)
            self.CH_enable_sw.setChecked(self.ch_volt_div_list[member_match][3])
            if self.ch_volt_div_list[member_match][2]==2:
                self.v_unit_combo.setCurrentIndex(1)
                self.vdisp.setText(str(current_volt_per_div)+" Volt/div")
                
                self.vdial.setValue(self.get_closest_index(self.v_step_vals,current_volt_per_div)+9) #######9 added to match unit
            elif self.ch_volt_div_list[member_match][2]==1:
                self.v_unit_combo.setCurrentIndex(0)
                self.vdisp.setText(str(current_volt_per_div)+" mVolt/div")
                self.vdial.setValue(self.get_closest_index(self.v_step_vals,current_volt_per_div))
            self.printf_("MULTI_INDEX",self.multiplier_index_list[member_match])
            self.multiplier_combo.setCurrentIndex(self.multiplier_index_list[member_match])
            self.zero_line_enabled_sw.setChecked(self.zeroline_visibility_list[member_match])
            
            self.v_unit_combo.currentIndexChanged.connect(self.v_unit_combo_changed)
            self.multiplier_combo_connection=self.multiplier_combo.currentIndexChanged.connect(self.onMultiplierChanged)
            self.zline_connection=self.zero_line_enabled_sw.toggled.connect(self.zline_toggled)

            
        self.CH_select_combo.setEnabled(True)
    
    def vdial_on_release(self,int_):
        self.v_panel_Enabled(False)
        if int_==3:
            self.disconnect_receivers(self.v_unit_combo,self.v_unit_combo.currentIndexChanged)
            #dial direct control
            self.printf_("Vdial_val_Pressed_changed")
            
            current_v_step_indx= self.vdial.value()
            self.v_step_indx=current_v_step_indx
            self.current_volt_per_div=self.v_step_vals[current_v_step_indx]
            self.v_spinbx.setValue(self.current_volt_per_div)
            #self.vslider.setValue(current_v_step_indx)
            #if prevVotlt_perdiv!=self.v_step_indx:
            if (current_v_step_indx<=8):
                self.v_unit_combo.setCurrentIndex(0)
                self.v_unit_indx=0
                self.vdisp.setText(str(self.current_volt_per_div)+" mVolt/div")
            if (current_v_step_indx>8):
                self.v_unit_indx=1
                self.v_unit_combo.setCurrentIndex(1)
                self.vdisp.setText(str(self.current_volt_per_div)+" Volt/div")
            
            if self.replotting!=1:
                reScale_thread = threading.Thread(target=self.reScalePlot)
                try:
                    reScale_thread.start()
                except Exception:
                    self.printf_(sys.exc_info())
                    self.printf_("LINE NO:",format(sys.exc_info()[-1].tb_lineno))
            else:
                self.v_panel_Enabled(True)
        elif int_==2:
            self.printf_("Vdial_val__changed")
            #v_spinbx control
            self.current_volt_per_div=self.v_spinbx.value()
            self.v_unit_indx=self.v_unit_combo.currentIndex()
            if self.v_unit_indx==1:
                
                self.vdisp.setText(str(self.current_volt_per_div)+" Volt/div")
                self.vdial.setValue(self.get_closest_index(self.v_step_vals,self.current_volt_per_div)+9) #######9 added to match unit
                
                #self.vslider.setValue(self.v_step_vals.index(self.current_volt_per_div)+9)
                if self.v_unit_indx==1 and  self.current_volt_per_div>100:
                    self.v_spinbx.setValue(100)

            if self.v_unit_indx==0:
                self.vdisp.setText(str(self.current_volt_per_div)+" mVolt/div")
                self.vdial.setValue(self.get_closest_index(self.v_step_vals,self.current_volt_per_div))
                #self.vslider.setValue(self.v_step_vals.index(self.current_volt_per_div))
                    
                if self.v_unit_indx==1 and  self.current_volt_per_div>100:
                    self.v_spinbx.setValue(100)
                
            if self.replotting!=1:
                reScale_thread = threading.Thread(target=self.reScalePlot)
                try:
                    reScale_thread.start()
                except Exception:
                    self.printf_(sys.exc_info())
                    self.printf_("LINE NO:",format(sys.exc_info()[-1].tb_lineno))
        self.v_panel_Enabled(True)
    
    def vdial_val_changed(self):
        current_v_step_indx= self.vdial.value()
        self.current_volt_per_div=self.v_step_vals[current_v_step_indx]
        if (current_v_step_indx<=8):
            self.vdisp.setText(str(self.current_volt_per_div)+" mVolt/div")
        if (current_v_step_indx>8):
            self.vdisp.setText(str(self.current_volt_per_div)+" Volt/div")
    
    def v_unit_combo_changed(self):
        ##self.setProgress(25,True)
        self.vdial_on_release(2)

    def CH_enabled_changed(self):
        self.CH_enable_sw.setEnabled(False)
        try:
            threading.Thread(target=self.Ch_enabled_changed_thread).start()
        except Exception:
            self.printf_(sys.exc_info())
            self.CH_enable_sw.setEnabled(True)
            self.printf_("LINE NO:",format(sys.exc_info()[-1].tb_lineno))
        
    def Ch_enabled_changed_thread(self):
        self.CH_enable_sw.toggled.disconnect()
        
        self.zero_line_enabled_sw.toggled.disconnect(self.zline_connection)
        curr_ch=str(self.CH_select_combo.currentText())
        matched=0
        matched_indx=-1
        for members in self.ch_name_col_list:
            matched_indx += 1
            if members[0]==curr_ch:
                self.printf_("Enbled:",curr_ch)
                matched=1
                break
        if matched==1:
            
            if self.CH_enable_sw.isChecked()==True:
                self.ch_volt_div_list[matched_indx][3]=1
                self.axes_list[matched_indx].set_visible(True)
                
                if self.zeroline_visibility_list[matched_indx]:
                    self.exmain.draw_zeroline(matched_indx,True)
            
            if self.CH_enable_sw.isChecked()==False:
                self.ch_volt_div_list[matched_indx][3]=0
                self.axes_list[matched_indx].set_visible(False)
                
                if self.zeroline_visibility_list[matched_indx]:
                    self.exmain.draw_zeroline(matched_indx,False)
                    self.zeroline_visibility_list[matched_indx]=False
                    self.zero_line_enabled_sw.setChecked(False)
            
            self.refresh_plot()
        self.zline_connection=self.zero_line_enabled_sw.toggled.connect(self.zline_toggled)
        self.CH_enable_sw.toggled.connect(self.CH_enabled_changed)
        self.CH_enable_sw.setEnabled(True)

    def v_panel_Enabled(self,bool_):
        self.toolbar.measure_win_A.setEnabled(bool_)
        self.menuEdit.setEnabled(bool_)
        self.actionChannel_Information.setEnabled(bool_)
        self.zero_line_enabled_sw.setEnabled(bool_)
        self.CH_select_combo.setEnabled(bool_)
        self.CH_enable_sw.setEnabled(bool_)
        self.vdial.setEnabled(bool_)
        self.v_spinbx.setEnabled(bool_)
        self.v_unit_combo.setEnabled(bool_)
        self.multiplier_combo.setEnabled(bool_)

    ######################################time scale changes################################################################
    def t_panel_Enabled(self,bool_):
        self.ch_move_rad.setEnabled(bool_)
        self.Cursor_enable_sw.setEnabled(bool_)
        self.t_dial.setEnabled(bool_)
        self.t_spinbx.setEnabled(bool_)
        self.t_unit_combo.setEnabled(bool_)
        
    def panel_Extra_Enabled(self,bool_):
        #self.Cursor_enable_sw.setEnabled(bool_)
        self.CH_move_combo.setEnabled(bool_)
        self.shift_t.setEnabled(bool_)
        self.shift_v.setEnabled(bool_)
        self.shf_x_label.setEnabled(bool_)
        self.shf_y_label.setEnabled(bool_)
        
    def t_dial_value_chg(self,flag_):
        self.t_panel_Enabled(False)
        if flag_==0:
            tprev=[self.t_val,self.t_unit_indx]
            t_val_indx,t_val_unit_indx=self.get_t_val(self.t_dial.value())
            self.t_unit=self.t_step_unit[t_val_unit_indx]
            self.t_val=self.t_step_vals[t_val_indx]
            self.t_step_indx=t_val_indx #@@@NO NEED may be 
            self.t_unit_indx=t_val_unit_indx
            if tprev[0]!=self.t_val or tprev[1]!=self.t_unit_indx:
                self.t_spinbx.setValue(self.t_val)
                self.t_unit_combo.setCurrentIndex(t_val_unit_indx)
                self.t_label.setText(str(self.t_val)+" "+str(self.t_unit)+"/div (minor)")
                
                #self.t_unit_combo.currentIndexChanged.connect(self.t_unit_combo_value_chg)
                if hasattr(self, "rescale_x_thread")==True:
                    if self.rescale_x_thread.is_alive():
                        self.rescale_x_thread.cancel()
                
                rescale_x_thread=threading.Thread(target=self.rescale_x)
                try:
                    rescale_x_thread.start()
                except Exception:
                    self.printf_(sys.exc_info())
                    self.printf_("LINE NO:",format(sys.exc_info()[-1].tb_lineno))
            else:
                self.t_panel_Enabled(True)
        if flag_==1:
            
            self.t_val=self.t_spinbx.value()
            self.t_unit_indx=self.t_unit_combo.currentIndex()
            self.t_unit=self.t_step_unit[self.t_unit_indx]
            try:
                t_index=self.t_step_vals.index(self.t_val)
                tdial_val=9*self.t_unit_indx+t_index+1##to have index val match index 0 is the 1st candidate of list
                self.t_dial.setValue(tdial_val)
            except Exception:
                self.printf_(sys.exc_info())
                self.printf_("LINE NO:",format(sys.exc_info()[-1].tb_lineno))
                t_index=-1
            self.t_label.setText(str(self.t_val)+" "+str(self.t_unit)+"/div (minor)")
            #self.t_unit_combo.currentIndexChanged.connect(self.t_unit_combo_value_chg)
            if hasattr(self, "rescale_x_thread")==True:
                if self.rescale_x_thread.is_alive():
                    self.rescale_x_thread.cancel()

            self.rescale_x_thread=threading.Thread(target=self.rescale_x)
            try:
                self.rescale_x_thread.start()
            except Exception:
                self.printf_(sys.exc_info())
                self.printf_("LINE NO:",format(sys.exc_info()[-1].tb_lineno))
        self.plot_axes.yaxis.set_minor_locator(AutoMinorLocator(5))
    
    def tdial_changed(self):
        t_val_indx,t_val_unit_indx=self.get_t_val(self.t_dial.value())
        t_unit=self.t_step_unit[t_val_unit_indx]
        t_val=self.t_step_vals[t_val_indx]
        self.t_label.setText(str(t_val)+" "+str(t_unit)+"/div (minor)")
    
    def get_t_val(self,t_dial_val):
        t_val_unit=t_dial_val//9
        t_val_indx=t_dial_val%9
        if t_val_indx==0:
            t_val_indx=9
            t_val_unit-=1
        return t_val_indx-1,t_val_unit
    
    def set_t_base(self):
        t_base_max=max(self.t_base_list)###max t_base is got in nanos
        if t_base_max>800:
            t_base_max=t_base_max/1000##in micros
            if t_base_max>800:
                t_base_max=t_base_max/1000##in millis
                if t_base_max>800:
                    t_base_max=t_base_max/1000##in Sec
                    self.printf_("T_base:",t_base_max,"s")
                    self.t_spinbx.setValue(int(t_base_max))
                    self.t_unit_combo.setCurrentIndex(3)
                    
                    if t_base_max>40:
                        self.printf_("timebase_out_of_range")
                else:
                    self.printf_("T_base:",t_base_max,"ms")
                    self.t_spinbx.setValue(int(t_base_max))
                    self.t_unit_combo.setCurrentIndex(2)
            else:
                self.printf_("T_base:",t_base_max,"us")
                self.t_spinbx.setValue(int(t_base_max))
                self.t_unit_combo.setCurrentIndex(1)
        else:
            self.printf_("T_base:",t_base_max,"ns")
            self.t_spinbx.setValue(int(t_base_max))
            self.t_unit_combo.setCurrentIndex(0)
        
    def set_v_base(self,v_base):
        v_base_in_volt=v_base/1e6
        self.v_spinbx.setValue(v_base_in_volt)
        self.v_unit_combo.setCurrentIndex(1)
    
    #######################################Rescaled Plot################################################################
    def reScalePlot(self):
        self.printf_("rescaling_plot")
        if self.replotting !=1:
            self.replotting=1
            ch_name=self.CH_select_combo.currentText()
            ch_match_indx=-1
            member_match=0
            if ch_name != "":
                for members in self.ch_name_col_list:
                    ch_match_indx +=1
                    if members[0]==ch_name:
                        member_match=1
                        break
                if member_match:
                    vdiv=self.v_spinbx.value()
                    self.v_unit_indx=self.v_unit_combo.currentIndex()
                    '''for scalling
                    if a perticualar point in plot is v 
                    i.e for 2v/div i.e for 2000mv/div the value is v
                    for 1mv/div the value is v*2000
                    for y mv/div the value is v*2000/y
                    '''
                    
                    self.ch_volt_div_list[ch_match_indx][1]=vdiv ###volt_div saved
                    if self.ch_volt_div_list[ch_match_indx][4]==1:
                        changey=self.ch_volt_div_list[ch_match_indx][5]
                        y_scale=np.add(self.y[ch_match_indx],changey)
                        y_scale=np.multiply(y_scale,self.ydiv) ##################changeY is always w.r.to the mother axes i.e self.plot_axes @2v/div
                    else:
                        y_scale=np.multiply(self.y[ch_match_indx],self.ydiv)###Yscaled to 1mv/div from main dataset
                    
                    if self.v_unit_indx==0:#in mv
                        y_scale=np.divide(y_scale,vdiv)
                        self.ch_volt_div_list[ch_match_indx][2]=1####vunit saved

                    if self.v_unit_indx==1:#in V
                        self.ch_volt_div_list[ch_match_indx][2]=2
                        vdiv=vdiv*1000
                        y_scale=np.divide(y_scale,vdiv)
                    
                    self.axes_list[ch_match_indx].clear()
                    self.axes_list[ch_match_indx].grid(which='minor', alpha=0.5, linestyle='-.',color='white')
                    self.axes_list[ch_match_indx].set_yticklabels([])
                    plot_ = self.axes_list[ch_match_indx].plot(self.x_scale[ch_match_indx],y_scale,alpha=self.plot_opacity,label=ch_name,color=self.ch_name_col_list[ch_match_indx][1],picker=5)
                    self.plot_list[ch_match_indx]=plot_
                    self.line_list[ch_match_indx]=plot_[0]
                                
                    if self.plotted_out_of_range==True: ###uses saved scale when was outranged
                        xlimit=self.x_limit_rescaled_out_of_range
                        xtics_step=self.xtics_step_out_ranged
                        for i in range(self.all_plot_count):  ####x_limit of all plots are changed if it was so i.e SCALED_OUT_OF_RANGE
                            self.axes_list[i].set(xlim=xlimit,autoscale_on=False)

                        self.plot_axes.set(xlim=xlimit,autoscale_on=False)
                        self.plot_axes.set_xticks(np.arange(xlimit[0],xlimit[1],step=xtics_step))
                        
                    elif self.plotted_with_small_scaledsize==1:###uses saved scale when in range and drawn small
                        xlimit=self.x_limit_rescaled_in_range_small
                        xtics_step=self.xtics_step_in_range
                        self.axes_list[ch_match_indx].set_xlim(xlimit)
                        self.plot_axes.set_xlim(xlimit)  ########x_limit of main axis made same
                        self.plot_axes.set_xticks(np.arange(xlimit[0],xlimit[1],step=xtics_step)) 
                    else:
                        self.axes_list[ch_match_indx].set_xlim(self.x_limit)##else limits kept to the max range
                        xlimit=self.x_limit
                    
                    
                    self.plot_axes.yaxis.set_minor_locator(AutoMinorLocator(5))
                    self.mplsmall.edit_plot(ch_match_indx,self.x_scale[ch_match_indx],y_scale,self.ch_name_col_list[ch_match_indx][1],xlimit)
                    self.y_scale[ch_match_indx]=y_scale
                    self.replotting=0
                    #self.setProgress(75,True)
                    if self.bypass_canvas_draw_on_reScalePlot==False:#####if declared that will be redrawn while initialisation and setting v_base and t_base
                        self.refresh_plot()
                        self.mplsmall.refresh_plot()
                    
        self.disconnect_receivers(self.v_unit_combo,self.v_unit_combo.currentIndexChanged)####reconnect
        self.v_unit_combo.currentIndexChanged.connect(self.v_unit_combo_changed)
        
        self.exmain.CH_cursor_combo_change()###############triggered to get new rescaled Y values for cursors and refresh
    
    def rescale_x(self):
        self.printf_("rescalling..")
        major_ticks=5
        minor_ticks=5
        minor_ticks_perpage=major_ticks*minor_ticks
        max_scalable_width=32768 #2^15
        
        default_canvas_width=self.default_canvas_width #in default_canvas_width total 5 main divitions wwith 25 total subdivitions fit
        t_scale=0
        
        if self.t_unit_indx==0:
            t_scale=1e9##nanosec
        if self.t_unit_indx==1:
            t_scale=1e6##microsec
        if self.t_unit_indx==2:
            t_scale=1e3##milisec
        if self.t_unit_indx==3:
            t_scale=1##sec
        
        xtics_step=self.t_val*minor_ticks/t_scale
        
        max_time=(minor_ticks_perpage*self.t_val*max_scalable_width)/default_canvas_width #time upto witch it fits in canvas of width 2^16/2 
        #max_time is also in base_unit i.e the unit seleced with time scale dial or unit combobox
        x_in_bsUnit=(self.x_limit[1]-self.x_limit[0])*t_scale  ##maximum x_limit that is to be scalled in nanosec microsec etc..
        
        if max_time>=x_in_bsUnit:#SCALING in RANGE
            self.printf_("SCALing_IN_RANGE\n")
            
            scaled_width=int((default_canvas_width*x_in_bsUnit)/(minor_ticks_perpage*self.t_val))
            self.printf_("Scaled_Width:",scaled_width)
            current_scrol_area_width=self.MplWidget.scrollArea.size().width()
            self.printf_("Curr SCRL Width:",current_scrol_area_width)
            
            self.plotted_in_range=True
            
            if scaled_width<current_scrol_area_width:
                self.printf_("SCALing_IN_RANGE:SMALL")
                scroll_val=self.MplWidget.scrollArea.horizontalScrollBar().value()
                scroll_max=self.MplWidget.scrollArea.horizontalScrollBar().maximum()
                scroll_page_step=self.MplWidget.scrollArea.horizontalScrollBar().pageStep()
                x_canvas_POS=(scroll_val+scroll_page_step/2)###@x_canvas_pos is the point of interrest arount which 
                CANVAS_pos=self.px2pt.transform((x_canvas_POS,0))
                x_canvas_pos=CANVAS_pos[0]
                
                self.rescalex_Extended_flag=False
                self.printf_("tval:",self.t_val,"MTICKSPERPAGE:",minor_ticks_perpage,"tscale:",t_scale)
                x_max=((self.t_val*minor_ticks_perpage)/t_scale)*current_scrol_area_width/default_canvas_width
                self.printf_("x_max",x_max)
                for i in range(self.all_plot_count):  ####@@@@@@@@@@@@@@@@@@@@@@@@@x_limit of all plots are made same
                    self.axes_list[i].set_xlim( self.x_limit[0],x_max)
                
                self.plot_axes.set_xlim(self.x_limit[0],x_max)  ########x_limit of main axis made same
                _step=(x_max-self.x_limit[0])/(major_ticks*current_scrol_area_width/default_canvas_width)
                self.plot_axes.set_xticks(np.arange(self.x_limit[0],x_max,step=_step)) ###reassigned xticks
                
                self.canvas.resize(current_scrol_area_width,self.MplWidget.scrollArea.size().height())  ################canvas resized
                
                if self.plotted_with_small_scaledsize==1 or self.plotted_with_small_scaledsize==-1:          ########canvas redrawn if canvas size is not changed in betwwen as resize doesnot occur no repaint job done by default so initiate re drawing
                    self.refresh_plot()
                
                self.x_limit_rescaled_in_range_small=[self.x_limit[0],x_max]
                self.xtics_step_in_range=_step
                self.plotted_with_small_scaledsize=1
                self.width_during_scaling=current_scrol_area_width
                
                
            else:
                self.printf_("SCALing_IN_RANGE:EXTENDED")
                scroll_val=self.MplWidget.scrollArea.horizontalScrollBar().value()
                scroll_max=self.MplWidget.scrollArea.horizontalScrollBar().maximum()
                scroll_page_step=self.MplWidget.scrollArea.horizontalScrollBar().pageStep()
                x_canvas_POS=(scroll_val+scroll_page_step/2)###@x_canvas_pos is the point of interrest arount which 
                CANVAS_pos=self.px2pt.transform((x_canvas_POS,0))
                x_canvas_pos=CANVAS_pos[0]
                self.rescalex_Extended_flag=True
                if self.plotted_with_small_scaledsize==1 or self.plotted_out_of_range==True:
                    
                    for i in range(self.all_plot_count):  ####x_limit of all plots are made reset if scale has changed from SCALED_SMAL
                        self.axes_list[i].set_xlim( self.x_limit[0],self.x_limit[1] )
                
                self.plot_axes.set_xlim(self.x_limit[0],self.x_limit[1] )
                self.printf_("x_max",self.x_limit[1])
                ticks=np.arange(self.x_limit[0],self.x_limit[1],step=xtics_step)
                self.printf_((ticks))
                self.printf_("start:",self.x_limit[0],"Stop:",self.x_limit[1],"step:",xtics_step)
                self.plot_axes.set_xticks(ticks) ###reassiged xticks
                if self.canvas.size().width()==scaled_width:
                    self.canvas.resize(scaled_width,self.MplWidget.scrollArea.size().height()-self.mplwidget_height_offset)###doesnot draws if the size has no change
                    self.refresh_plot()
                else:
                    self.canvas.resize(scaled_width,self.MplWidget.scrollArea.size().height()-self.mplwidget_height_offset)
                
                #self.xtics_step_in_range=xtics_step
                self.printf_("SCALED_WIDTH:",scaled_width)
                self.plotted_with_small_scaledsize=0
                self.width_during_scaling=scaled_width
            self.plotted_out_of_range=False
            #self.setProgress(50,True)
        elif max_time<x_in_bsUnit:#SCALING OUT RANGED  ########CHANGED FROM IF to ELIF
            self.plotted_in_range=False
            self.plotted_with_small_scaledsize=-1
            self.rescalex_Extended_flag=True
            self.printf_("SCALing_OUT_OF_RANGE\n")
            self.xtics_step_out_ranged=xtics_step
            scroll_val=self.MplWidget.scrollArea.horizontalScrollBar().value()
            scroll_max=self.MplWidget.scrollArea.horizontalScrollBar().maximum()
            scroll_page_step=self.MplWidget.scrollArea.horizontalScrollBar().pageStep()
            if scroll_max==0:
                scroll_max=1
            
            remapped_scroll=self.remap(scroll_val,(0.025*scroll_max),(1-0.025)*scroll_max,0,scroll_max)
            
            
            t_val_in_sec_out_ranged=self.t_val/t_scale
            
            if self.plotted_out_of_range==False:
                x_canvas_POS=(scroll_val+scroll_page_step/2)###@x_canvas_pos is the point of interrest arount which 
                CANVAS_pos=self.px2pt.transform((x_canvas_POS,0))
                x_canvas_pos=CANVAS_pos[0]
                self.printf_("x_canvas_pos",x_canvas_pos)
                x_max=self.x_limit[1]
                x_min=self.x_limit[0]
                X_tot = x_max-x_min
                
                #the plot of (2^16)/2 pixels of canvas is to be Rendered
                #@TO DO if and else
            elif  self.plotted_out_of_range==True:######changed to elif form if
                if self.t_val_in_sec_out_ranged>t_val_in_sec_out_ranged:
                    self.zoom_within_out_ranged=1#zooming in
                    self.printf_("zooming in")
                    x_canvas_POS=(scroll_val+scroll_page_step/2)###@x_canvas_pos is the point of interrest arount which 
                    CANVAS_pos=self.px2pt.transform((x_canvas_POS,0))
                    x_canvas_pos=CANVAS_pos[0]
                    x_min=self.x_limit_rescaled_out_of_range[0]
                    x_max=self.x_limit_rescaled_out_of_range[1]
                    X_tot=(x_max-x_min)
                    self.printf_("x_canvas_pos",x_canvas_pos)
                else:
                    self.zoom_within_out_ranged=-1#zooming out
                    self.printf_("Zooming out")
                    if self.mplsmall.rescale_done_by_selection:
                        x_canvas_pos=self.mplsmall.reseted_mid
                        self.mplsmall.rescale_done_by_selection=False
                    else:
                        x_canvas_pos=self.x_canvas_out_ranged
                    x_min=self.x_limit[0]
                    x_max=self.x_limit[1]
                
            self.t_val_in_sec_out_ranged=t_val_in_sec_out_ranged
            
            #### when the half of region of plot i.e "max_time/2" is higer than the 
            # regiaon between the point of interent around which it is scalled and the left edge 
            '''self.printf_(" ############################################################################################")
            self.printf_("X_left:",x_min,"  X_right:",x_max)
            self.printf_("x_total:",x_in_bsUnit)
            self.printf_("position in canvas:",x_canvas_pos)
            left_gap=x_canvas_pos-x_min #gap in left from pt of interest
            right_gap=x_max-x_canvas_pos
            self.printf_("max_time",max_time)
            self.printf_("LEFT_gap:",left_gap,"    Right_gap:",right_gap)
            self.printf_(" ############################################################################################")'''
        ##########################################################ATTACHEMENTS#########################################
            self.x_canvas_out_ranged=x_canvas_pos
            left_gap=x_canvas_pos-x_min #gap in left from pt of interest
            right_gap=x_max-x_canvas_pos
            half_max_time_sec=max_time/(2*t_scale)
            max_time_sec=max_time/t_scale
            self.printf_("half_max_time_sec:",half_max_time_sec)
        ######Attached to LEFT###############################################
            if left_gap<=half_max_time_sec:
                xlimit=[x_min,(x_min+max_time_sec)]
                self.x_limit_rescaled_out_of_range=xlimit
                '''self.printf_("Attached to left")
                self.printf_("left_gap:",left_gap)
                self.printf_("xlimit:",xlimit)'''
        ######Away from LEFT###############################################
            if left_gap>half_max_time_sec:
                right_gap=x_max-x_canvas_pos
                self.printf_("Away from left")
            #############################Attached to right ##################
                if right_gap<=half_max_time_sec:
                    xlimit=[(x_max-max_time_sec),x_max]
                    self.x_limit_rescaled_out_of_range=xlimit
                    self.printf_("Attached to right")
                    self.printf_("Xlimit:",xlimit)
                    
            ##################must be attached to somewhere middle#################
                else:
                    xlimit=[(x_canvas_pos-half_max_time_sec),(x_canvas_pos+half_max_time_sec)]
                    self.x_limit_rescaled_out_of_range=xlimit
                    self.printf_(left_gap,"away in the middle",right_gap)
                    self.printf_("Xlimit:",xlimit)
            
            
            for i in range(self.all_plot_count):  ####x_limit of all plots are made reset if scale has changed from SCALED_SMAL
                self.axes_list[i].set(xlim=xlimit,autoscale_on=False)
            
            self.plot_axes.set(xlim=xlimit,autoscale_on=False)
            self.plot_axes.set_xticks(np.arange(xlimit[0],xlimit[1],step=xtics_step))
            #self.setProgress(50,True)
            if self.canvas.size().width()==max_scalable_width:
                self.canvas.resize(max_scalable_width,self.MplWidget.scrollArea.size().height()-self.mplwidget_height_offset)###doesnot draws if the size has no change
                self.refresh_plot()
            else:
                self.canvas.resize(max_scalable_width,self.MplWidget.scrollArea.size().height()-self.mplwidget_height_offset)
            self.printf_("Drawn_OUT_OF_range")
            self.plotted_out_of_range=True
            self.width_during_scaling=max_scalable_width
        self.set_scrl_val=self.pt2px.transform((x_canvas_pos,0))[0]
        self.set_scrl_val = int(self.set_scrl_val)
        self.t_panel_Enabled(True)
        self.rubberBand_reds_notDrawn=True
        self.draw_rubberbands()
    
    def remap(self,num,oRmin,oRmax,nRmin,nRmax):
        num=num-oRmin
        mapped=(num/(oRmax-oRmin))*(nRmax-nRmin)
        mapped += nRmin
        if mapped<=nRmin:
            mapped=0
        if mapped>=nRmax:
            mapped=nRmax
        return mapped
    #####################################RUBBERBANDS#########################################
    def define_rubberband(self):
        self.rubberBand = QRubberBand(QRubberBand.Rectangle, self.mplsmall.canvas)
        self.rubberBand1 = QRubberBand(QRubberBand.Rectangle, self.mplsmall.canvas)
        self.rubberBand_red = QRubberBand(QRubberBand.Rectangle, self.mplsmall.canvas)
        self.rubberBand_red1 = QRubberBand(QRubberBand.Rectangle, self.mplsmall.canvas)
        
        self.assign_graphics(self.rubberBand,"green")
        self.assign_graphics(self.rubberBand1,"green")
        self.assign_graphics(self.rubberBand_red,"red")
        self.assign_graphics(self.rubberBand_red1,"red")
        
        #self.Cursor_t.hide()
        #self.Cursor_V.hide()
        self.rubberBand_reds_notDrawn=True
        self.small_view_start_pt=0
        self.small_view_end_pt=0
    
    def assign_graphics(self,rubberband,col):
        graphics_effect=QGraphicsColorizeEffect()
        graphics_effect.setColor(QtGui.QColor(col))
        rubberband.setGraphicsEffect(graphics_effect)
    
    def draw_rubberbands(self):
        X_lim=self.x_limit
        canvas_page_start=self.MplWidget.scrollArea.horizontalScrollBar().value()
        scroll_page_step=self.MplWidget.scrollArea.horizontalScrollBar().pageStep()
        small_canvas_width=self.mplsmall.canvas.size().width()
        canvas_page_end=canvas_page_start+scroll_page_step
        
        self.canvas_page_start_point=self.px2pt.transform((canvas_page_start,0))
        self.canvas_page_end_point=self.px2pt.transform((canvas_page_end,0))
        
        plotXlim=self.plot_axes.get_xlim()
        self.CoordMin=self.mplsmall_pt2px.transform((plotXlim[0],0))[0]
        self.CoordMax=self.mplsmall_pt2px.transform((plotXlim[1],0))[0]
        self.small_view_start_pos=self.mplsmall_pt2px.transform(self.canvas_page_start_point)[0]
        self.small_view_end_pos=self.mplsmall_pt2px.transform(self.canvas_page_end_point)[0]
        if [plotXlim[0],plotXlim[1]]==X_lim:
            self.CoordMin=0
            self.CoordMax=small_canvas_width
            self.rubberBand_red.hide()
            self.rubberBand_red1.hide()
        elif self.plotted_out_of_range and self.rubberBand_reds_notDrawn:
            self.rubberBand_red.setGeometry(QRect(QPoint(0,0),QPoint(int(self.CoordMin),self.mplwidget_height_offset)))
            self.rubberBand_red1.setGeometry(QRect(QPoint(int(self.CoordMax),0),QPoint(small_canvas_width,self.mplwidget_height_offset)))
            self.rubberBand_red.show()
            self.rubberBand_red1.show()
            self.rubberBand_reds_notDrawn=False
        elif self.plotted_in_range:
            self.rubberBand_red.hide()
            self.rubberBand_red1.hide()
            self.rubberBand.show()
            self.rubberBand1.show()
        
        self.rubberBand.setGeometry(QRect(QPoint(int(self.CoordMin),0),QPoint(int(self.small_view_start_pos),self.mplwidget_height_offset)))
        self.rubberBand1.setGeometry(QRect(QPoint(int(self.small_view_end_pos),0),QPoint(int(self.CoordMax),self.mplwidget_height_offset)))
        
        self.rubberBand.show()
        self.rubberBand1.show()
        
        '''
        self.printf_("XMIN",self.CoordMin)
        self.printf_("XMAX",self.CoordMax)
        self.printf_("small_view_start_pt",small_view_start_pos)
        self.printf_("small_view_end_pt",small_view_end_pt)'''
        '''
        self.printf_("Scrl_val",s_v)
        self.printf_("cv_start:",cv_start)
        self.printf_("cv_end:",cv_end)
        self.printf_("Xlim:",xmin,xmax)
        self.printf_("canvas_Width",cw)'''
    
    #######################################DRAW##############################################
    
    def refresh_plot(self):
        if hasattr(self, "redraw")==True:
            if self.redraw.is_alive():
                self.redraw.cancel()

        
        self.redraw=threading.Thread(target=self.canvas.draw_idle)
        self.redraw.start()
        
    def grid_view_cycle(self):
        if self.cycle_g_key==0:
            self.plot_axes.grid(b=False,which="minor",axis='x')
        elif self.cycle_g_key==1:
            self.plot_axes.grid(b=False,which="minor",axis='y')
        elif self.cycle_g_key==2:
            self.plot_axes.grid(b=False,which="major",axis='x')
        elif self.cycle_g_key==3:
            self.plot_axes.grid(b=False,which="major",axis='y')
        if self.cycle_g_key==4:
            self.plot_axes.grid(b=True,which="minor",axis='x')
        elif self.cycle_g_key==5:
            self.plot_axes.grid(b=True,which="minor",axis='y')
        elif self.cycle_g_key==6:
            self.plot_axes.grid(b=True,which="major",axis='x')
        elif self.cycle_g_key==7:
            self.plot_axes.grid(b=True,which="major",axis='y')
        self.cycle_g_key +=1
        if self.rescalex_Extended_flag:
            self.set_scrl_val=self.MplWidget.scrollArea.horizontalScrollBar().value()+self.MplWidget.scrollArea.horizontalScrollBar().pageStep()/2
        self.refresh_plot()
        if self.cycle_g_key>7:
            self.cycle_g_key=0
    
    def get_closest_index(self,list_,c):
        return (min(range(len(list_)), key=lambda i: abs(list_[i]-c)))
    
    def disconnect_receivers(self,object_,signal):
        receivers= object_.receivers(signal)
        for i in range(receivers):
            signal.disconnect()
        
     ###########################################MULTIPLIER################################################
    
    ###############################MULTIPLIER#####################################
    
    def onMultiplierChanged(self):
        self.printf_("Multiplier Change")
        multiplier_index=self.multiplier_combo.currentIndex()
        multiplier=1/10**(multiplier_index)
        ch_name=self.CH_select_combo.currentText()
        chindx=-1
        for members in self.ch_name_col_list:
            chindx+=1
            if members[0]==ch_name:
                member_matched=1
                break
        if member_matched==1:
            indx_prev=self.multiplier_index_list[chindx]
            if indx_prev!=0:
                multiplier=multiplier*10**(indx_prev)
            self.multiplier_index_list[chindx]=multiplier_index
            self.v_base_list[chindx]=self.v_base_list[chindx]*multiplier
            
            volt_per_div=self.v_spinbx.value()
            v_unit_indx=self.v_unit_combo.currentIndex()+1
            self.v_spinbx.setValue(volt_per_div*multiplier)
            
            self.y[chindx]=np.multiply(self.y[chindx],multiplier)
            self.vdial_on_release(2)####behave like spinbox is changed and call..
        
    def get_config(self,bool_):
        
        main_ylim=self.main_ylim
        if self.conf.wave_volt_limit[0]!=None and bool_==False:
            self.main_ylim=self.conf.wave_volt_limit
            self.printf_("self.conf.wave_volt_limit",self.conf.wave_volt_limit)
        elif bool_==False:
            self.main_ylim=[-5500,5500]
        
        if main_ylim!= self.conf.wave_volt_limit and bool_==True:
            self.toolbar.statusLabel.setText("RESTART REQUIRED to Change Volt limit")
            self.toolbar.statusLabelAction.setVisible(True)
            self.toolbar.coordinateLabel.setVisible(False)

        self.get_plot_opacity(bool_)
        
        if self.conf.Main_Window_always_on_top!=[None,False]:
            if self.conf.Main_Window_always_on_top:
                self.setWindowFlags(QtCore.Qt.WindowFlags(QtCore.Qt.WindowStaysOnTopHint))
            else:
                #self.setWindowFlags(QtCore.Qt.WindowFlags(QtCore.Qt.Window))
                pass
        self.last_folder=self.conf.csv_dir[0]
        self.debug_=self.conf.debug_
        
    def get_plot_opacity(self,bool_):
        plt_opacity=self.plot_opacity
        changed_opacity=False
        if self.conf.wave_plot_opacity!=[None,False]:
            self.plot_opacity=self.conf.wave_plot_opacity
        else:
            self.plot_opacity=1
        
        if plt_opacity!=self.plot_opacity and bool_==True:
            for i in range(len(self.line_list)):
                self.line_list[i].set_alpha(self.plot_opacity)
                changed_opacity=True
        if changed_opacity==True:
            self.refresh_plot()
    #####################################WINDOW SIZES##########################################
    def set_sizes(self):
        
        resize_multiplier=[self.screensize[0]/1920,self.screensize[1]/1080]
        self.zoomsize=[int(382*resize_multiplier[0]),int(220*resize_multiplier[1])]
        self.aboutwinsize=[int(442*resize_multiplier[0]),int(215*resize_multiplier[1])]
        self.default_canvas_width=int(837*resize_multiplier[0])
        self.resize(int(1012*resize_multiplier[0]),int(627*resize_multiplier[1]))
        self.mplwidget_height_offset=int(24*resize_multiplier[1])
        self.mplsmall_window_height=int(60*resize_multiplier[1])
        
        
        self.main_panel_widgets=[self.main_panel_frame,self.CH_select_combo,self.multiplier_combo,self.CH_enable_sw,self.zero_line_enabled_sw,
                                 self.v_spinbx,self.v_unit_combo,self.vdial,self.vdisp,self.t_spinbx,self.t_unit_combo,self.CH_move_combo,
                                 self.ch_move_rad,self.shf_x_label,self.shift_t,self.shf_y_label,self.shift_v,self.CH_cursor_combo,
                                 self.Cursor_of,self.Cursor_type_combo,self.Cursor_type_txt,self.Cursor_enable_sw,self.Cursor_S_rad,self.t_S,
                                 self.v_S,self.Cursor_E_rad,self.t_E,self.v_E,self.dt_inv_label,self.dt_label,
                                 self.dv_label,self.dt_,self.dt_inv_,self.dv_]
        
        self.FFT_panel_widgets=[self.fft_panel_frame,self.fft_ch_enable,self.fft_ch_select,self.label_2,self.window_type_combo,
                                self.window_params_label,self.window_params_spin,self.Window_symetric_Radio,
                                self.Window_symetric_lab,self.display_type_combo,self.label_3,self.fft_refference_select_spin,
                                self.fft_refference_select_unit,self.fft_ydiv_spin,self.fft_ydiv_unit,self.fft_y_dial,
                                self.fft_ydisp,self.label,self.label_4,self.frequency_scale,self.label_70,
                                self.freq_div_spin,self.freq_div_unit,self.fft_freqdisp,self.freq_dial,self.reset_axes]
        
        self.main_panel_widgets.extend(self.FFT_panel_widgets)
        for i in range (len(self.main_panel_widgets)):
            widget=self.main_panel_widgets[i]
            widget.resize(int(widget.size().width()*resize_multiplier[0]),int(widget.size().height()*resize_multiplier[1]))
        self.printf_("zoomWin:",self.zoomsize,"About_win_size:",self.aboutwinsize)
    
    def printf_(self,*args):
        if self.debug_:
            string=""
            for i in range(len(args)):
                string+=str(args[i])
            print(string)
    
app = QtWidgets.QApplication(sys.argv)
app.setStyleSheet("""
    QMenu::item:selected
    {
       background-color: rgb(0, 122, 216);
    }"""
    """QToolTip {
font-size:9pt;
color:white; padding:2px;
border-width:2px;
border-style:solid;
border-radius:40px;
background-color: black;
border: 1px solid white;}""")
MainWindow = QtWidgets.QMainWindow()
ui = Ui_MainWindow()
ui.show()
sys.exit(app.exec_())

#repositioning plots cursor V

#initial sizes to adapt with resolution


####on multiplier change v_base , y[] and a rescale will be done on channel selection change the multiplier will also change 
##rescale positioning has bug

#update during file input and draw
#during resize
#during rescale x and y

#rescalex thread check
