from PyQt5.QtWidgets import *
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5 import QtCore,QtGui
from PyQt5.QtCore import pyqtSignal

from scipy import signal, fftpack
from scipy.fftpack import fft, fftshift
from scipy.signal import get_window

import numpy as np
from matplotlib import ticker
from matplotlib.ticker import AutoLocator, AutoMinorLocator, LinearLocator, MultipleLocator
import edited_nav_toolbar_FFT_window

from mplsmall_FFT import *
from fft_zoom import fft_zoom_

from PyQt5.Qt import QKeyEvent
from rubberbands import Bounding_Box
from matplotlib.backend_bases import MouseButton
from PyQt5.QtGui import QPalette

class FFT_Widget(QWidget):
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
        self.plot=plt
        self.canvas = FigureCanvas(self.figure)  # FigureCanvas//Figure// called canvas
        self.figure.set_facecolor("black")
        self.scrollArea.setSizePolicy(QSizePolicy.Minimum,QSizePolicy.Minimum)
        self.scrollArea.setContentsMargins(0, 0, 0, 0)
        self.scrollArea.setStyleSheet("border:0px;padding-left:0px;padding-top:0px;padding-right:0px;padding-bottom:0px")
        self.scrollArea.setWidget(self.canvas)
        self.verticalLayout.addWidget(self.scrollArea)
        self.toolbar = edited_nav_toolbar_FFT_window.NavigationToolbar2QT(self.canvas, self)
        self.toolbar.setStyleSheet("""
        QWidget {
            background-color:qlineargradient(spread:pad, x1:0.969955, y1:0.159, x2:0, y2:1, stop:0.0945274 rgba(92, 167, 206, 255), stop:1 rgba(255, 255, 255, 255))\n
            }
        """)
    
class FFT_handler(object):
    def __init__(self,parent):
        super(FFT_handler,self).__init__()
        self.main=parent
        self.fftw=self.main.FFT_Widget
        self.toolbar=self.fftw.toolbar
        val_entered= pyqtSignal([QKeyEvent])
        self.main.fft_panel_frame.setEnabled(False)

    def initialise(self):
        self.figure=self.fftw.figure
        self.plot=self.fftw.plot
        self.axes=self.fftw.figure.add_subplot(1, 1, 1)
        self.axes.patch.set_facecolor('xkcd:black')
        self.axes.spines['bottom'].set_color('white')
        self.axes.spines['top'].set_color('white')
        self.axes.spines['right'].set_color('white')
        self.axes.spines['left'].set_color('white')
        self.axes.tick_params(axis='both', colors='white')
        #self.axes.tick_params(axis='y', colors='white')
        #self.axes.set_yticklabels([])
        self.axes.grid(which='major', axis="both", alpha=0.9, linestyle='--',color='white')
        self.axes.grid(which='minor', axis="both", alpha=0.5, linestyle='-.',color='white')
        self.axes.tick_params(which='minor', length=4)
        self.axes.yaxis.set_minor_locator(AutoMinorLocator(5))
        self.axes.xaxis.set_minor_locator(AutoMinorLocator(5))
        self.canvas=self.fftw.canvas
        self.canvas.draw()
        self.figure.tight_layout(pad=0, w_pad=None, h_pad=None)
        self.canvas.mpl_connect('draw_event',self.onCanvasDrawn)
        self.canvas.mpl_connect('motion_notify_event', self.onMouseMotion)
        self.windows=["barthann","bartlett","blackman","blackmanharris","hann",
                      "bohman","boxcar","cosine","flattop","hamming","hanning","nuttall","parzen","triang",
                      "chebwin","gaussian","kaiser","slepian","tukey"]
        
        self.main.window_type_combo.addItems(self.windows)
        
        if self.main.conf.FFT_default_window!=[None,False]:
            self.current_window=self.main.conf.FFT_default_window
        else:
            self.current_window="boxcar"
        
        self.win_indx=self.windows.index(self.current_window)###########window choice default index
        self.main.window_type_combo.setCurrentIndex(self.win_indx)
        self.view_win_params()
        self.wait_for_parameter_input=False
        
        self.main.window_type_combo.currentIndexChanged.connect(lambda: self.window_change(True,False))
        self.main.display_type_combo.currentIndexChanged.connect(lambda: self.window_change(False,False))
        #self.main.fft_refference_select_spin.valueChanged.connect(self.refference_changed)
        #self.main.fft_refference_select_unit.currentIndexChanged.connect(self.refference_changed)
        self.main.fft_ch_enable.setChecked(True)
        self.main.fft_ch_enable.toggled.connect(self.fft_CH_enable_toggled)

        
        self.disp_type_indx=1
        self.ref_=5
        self.plot_list=[]
        #self.plot_xlimits=[]
        #self.plot_ylimits=[]
        #self.ch_indx=0
        self.ch_fft_enabled_list=[]
        self.ch_window_list=[]
        self.ch_display_type_list=[]
        self.ch_window_symmetry_list=[]
        self.ch_window_param_list=[]
        
        self.plot_opacity=1
        self.get_plot_opacity(False)
        
        self.visible_plotXlim=[]
        self.visible_plotYlim=[]
        self.main.fft_refference_select_spin.val_entered.connect(self.refference_changed)
        self.main.window_params_spin.val_entered.connect(self.resume_calculate_fft)
        self.main.freq_div_spin.val_entered.connect(self.freq_div_changed)
        self.main.fft_ydiv_spin.val_entered.connect(self.fft_ydiv_changed)
        self.refference_list=[]####[value,unit_index]
        self.round_factor=2
        self.main.frequency_scale.currentIndexChanged.connect(self.frequency_scale_changed)
        self.scale_type=["linear", "symlog"]
        
        #self.default_canvas_width=837
        self.default_canvas_width=self.main.default_canvas_width
        
        xtick=self.plot.xticks()[0]
        self.freq_per_div=(xtick[1]-xtick[0])/5
        self.rescalex_Extended_bool=False
        self.rescalex_Out_ranged=False
        self.fftsmall= self.main.mplsmall_FFT
        self.define_rubberband()
        self.rubberBand_reds_notDrawn=True
        self.fftw.scrollArea.horizontalScrollBar().valueChanged.connect(self.draw_rubberbands)
        self.first_plot=False
        self.rescaled_Y=False
        self.main.reset_axes.clicked.connect(self.reset_axis_view)
        self.zoomwin=fft_zoom_(self)
        self.canvas.mpl_connect('button_press_event',  self.onMouseButtonPress)
        self.picked=False
        self.pick_con=self.canvas.mpl_connect('pick_event', self.on_pick)
        self.bounding_Box = Bounding_Box("white",QRubberBand.Rectangle, self.canvas)
        self.canvas.mpl_connect('key_press_event',self.onKeyPressed)
        self.canvas.mpl_connect('key_release_event',self.onKeyReleased)
        self.canvas.setFocusPolicy( QtCore.Qt.ClickFocus )
        self.canvas.setFocus()
        self.annotations_max=[]
        self.arrowprops = dict( color='white', arrowstyle = "->", connectionstyle = "angle, angleA = 0, angleB = 90,rad = 10") 
        self.annot_offset_x=40
        self.annot_offset_y=10
        self.freq_dial_vals=[2,4,8,20,40,80,200,400,800]
        self.y_dial_vals=[2,4,8,20,40,80,200,400,800,1200,1400,1800,2000,2400,2800,3200,3400,3800,4200,4400,4800]
        self.freqdial_valConnection=self.main.freq_dial.valueChanged.connect(self.freqdial_changed)
        
        self.main.freq_dial.sliderReleased.connect(self.freq_div_changed)
        self.main.fft_y_dial.sliderReleased.connect(self.fft_ydiv_changed)
        self.fft_y_dial_connection=self.main.fft_y_dial.valueChanged.connect(self.fft_y_changed)
        self.yspinVal_temp=[]
        self.ydial_changed=False
        self.freq_dial_changed=False
        self.freqspin_temp=[]
        self.last_width=0
        self.FFT_window_default_symmetric=False
        self.get_config()
        self.View_params_box(False)
        self.main.Window_symetric_Radio.setChecked(self.FFT_window_default_symmetric)
        self.sym_radio_connection=self.main.Window_symetric_Radio.toggled.connect(self.symmetry_changed)
        self.last_shown=[]
        ###Window_symetric_Radio for settings
    
    ######################################### EVENT Handle #####################################
    def resize_self(self,shown_flag,w,h):
        
        if shown_flag==True and self.rescalex_Extended_bool==False:
            if w>self.last_width:
                self.canvas.resize(w,h-30)
                self.fftsmall.canvas.resize(w,60)
                print("R1_1_FFT")
            else:
                self.canvas.resize(self.canvas.size().width(),(h-24))
                self.fftsmall.canvas.resize(w,60)
                print("R1_2_FFT")
        elif self.rescalex_Extended_bool==True:
            if w>self.last_width:
                self.canvas.resize(w,h-30)
                self.fftsmall.canvas.resize(w,60)
                print("R2_1_FFT")
            else:
                self.canvas.resize(self.canvas.size().width(),(h-30))
                self.fftsmall.canvas.resize(w,60)
                print("R2_2_FFT")
    
    def on_pick(self,e):
        self.picked=True
        self.artist_picked=e.artist
        
    def onKeyPressed(self,e):
        if e.key=="control":
            self.zoomwin.ctrl=True
        
    
    def onKeyReleased(self,e):
        if e.key=="control":
            self.zoomwin.ctrl=False

    def ctrl_handle(self,bool_):
        self.zoomwin.ctrl=bool_
    
    def onMouseButtonPress(self,e):
        if e.button==MouseButton.LEFT:
            xtick=self.axes.get_xticks(minor=True)
            ytick=self.axes.get_yticks(minor=True)
            freq_per_div=(xtick[1]-xtick[0])
            y_per_div=(ytick[1]-ytick[0])
            if self.picked and self.zoomwin.ctrl==True:
                self.zoomwin.zoom_history_index=1
                self.zoomwin.zoom_history_list=[]
                self.ZoomsetDrawRect(e.xdata,e.ydata,freq_per_div,y_per_div)
                self.zoomwin.show_plot(e.xdata,e.ydata,freq_per_div,y_per_div)
                self.last_shown=[e.xdata,e.ydata,freq_per_div,y_per_div]
                self.zoomwin.zoom_history_list.append([e.xdata,e.ydata,freq_per_div,y_per_div])
                self.bounding_Box.show()
                
            elif  self.picked==True:
                if self.zoomwin.keep_annotations==False:
                    self.remove_annotations()
                if self.rescalex_Extended_bool:
                    dat_x,dat_y=self.zoomwin.get_maximas(self.artist_picked,[(e.xdata-freq_per_div),(e.xdata+freq_per_div)],[(e.ydata-y_per_div),(e.ydata+y_per_div)])
                else:
                    dat_x,dat_y=self.zoomwin.get_maximas(self.artist_picked,[(e.xdata-freq_per_div/2),(e.xdata+freq_per_div/2)],[(e.ydata-y_per_div/2),(e.ydata+y_per_div)])

                dat_x,dat_y=self.zoomwin.get_max_sorted(self.zoomwin.max_pt2show,dat_x,dat_y)
                
                xlim=self.axes.get_xlim()
                ylim=self.axes.get_ylim()
                xlim=[xlim[0]+self.lim_offset_x ,xlim[1]-self.lim_offset_x]
                ylim=[ylim[0]+self.lim_offset_y,ylim[1]-self.lim_offset_y]
                
                for i in range(len(dat_x)):
                    self.check_loc_and_annotate(dat_x[i],dat_y[i],xlim,ylim,i)
                self.canvas.draw_idle()
            self.picked=False
    
    def onCanvasDrawn(self,event):
        print("FFT_DRAWN")
        if self.canvas.size().width()<self.main.tabWidget.size().width():
            self.canvas.resize(self.main.tabWidget.size().width(),self.main.tabWidget.size().height()-54)
        self.px2pt=self.axes.transData.inverted()
        self.pt2px=self.axes.transData
        xtick=self.axes.get_xticks()
        ytick=self.axes.get_yticks()
        self.freq_per_div=(xtick[1]-xtick[0])/5
        self.y_per_div=(ytick[1]-ytick[0])
        print("freq_per_div",self.freq_per_div)
        print("y_per_div",self.y_per_div)
        self.set_freq_div_dial(self.freq_per_div)
        self.set_ydiv_dial(self.y_per_div)
        self.fftsmall_pt2px=self.fftsmall.axes.transData
        self.fftsmall_px2pt=self.fftsmall.axes.transData.inverted()
        if self.first_plot:
            self.draw_rubberbands()
        if self.rescalex_Out_ranged:
            self.rubberBand_reds_notDrawn=True
        self.lim_offset_x=self.px2pt.transform((65,0))[0]-self.px2pt.transform((0,0))[0]
        self.lim_offset_y=self.px2pt.transform((0,20))[1]-self.px2pt.transform((0,0))[1]
        print("limoffsets:",self.lim_offset_x,self.lim_offset_y)
        self.last_width=self.canvas.size().width()
        
    def onMouseMotion(self,e):
        try:
            s="freq="+str(round(e.xdata,self.round_factor))+" Hz "
            if self.disp_type_indx==0:
                s=s+"Amp="+str(round(e.ydata,self.round_factor))+" mv"
            if self.disp_type_indx==1:
                s=s+"L="+str(round(e.ydata,self.round_factor))+" db"
            self.fftw.toolbar.locLabel.setText(s)
        except Exception:
            pass
    
    def fft_CH_changed(self):
        try:
            self.main.window_type_combo.currentIndexChanged.disconnect()
        except Exception:
            pass
        try:
            self.main.display_type_combo.currentIndexChanged.disconnect()
        except Exception:
            pass
        try:
            self.main.Window_symetric_Radio.toggled.disconnect(self.sym_radio_connection)
        except Exception:
            pass
        
        chIndx=self.main.fft_ch_select.currentIndex()
        print("chIndx",chIndx)
        self.main.Window_symetric_Radio.setChecked(self.ch_window_symmetry_list[chIndx])
        self.main.window_params_spin.setValue(self.ch_window_param_list[chIndx])
        if self.ch_fft_enabled_list[chIndx]:
            self.plot_list[chIndx][0].set_visible(True)
            self.main.fft_ch_enable.setChecked(True)
            self.canvas.draw_idle()
        else:
            self.main.fft_ch_enable.setChecked(False)
        
        self.disp_type_indx=self.ch_display_type_list[chIndx]
        
        if self.disp_type_indx==0:
            for i in range(self.main.fft_ydiv_unit.count()):
                self.main.fft_ydiv_unit.removeItem(0)
            self.main.fft_ydiv_unit.addItems(["mv","v"])
        elif self.disp_type_indx==1:
            for i in range(self.main.fft_ydiv_unit.count()):
                self.main.fft_ydiv_unit.removeItem(0)
            self.main.fft_ydiv_unit.addItem("db")
            
        if self.windows.index(self.ch_window_list[chIndx])>=14:
            
            self.View_params_box(True)
        else:
            self.View_params_box(False)
            
        self.main.window_type_combo.setCurrentIndex(self.windows.index(self.ch_window_list[chIndx]))
        self.main.display_type_combo.setCurrentIndex( self.ch_display_type_list[chIndx])
        self.main.fft_refference_select_spin.setValue(self.refference_list[chIndx][0])
        self.main.fft_refference_select_unit.setCurrentIndex(self.refference_list[chIndx][1])
        self.main.window_type_combo.currentIndexChanged.connect(lambda: self.window_change(True,False))
        self.main.display_type_combo.currentIndexChanged.connect(lambda: self.window_change(False,False))
        self.sym_radio_connection=self.main.Window_symetric_Radio.toggled.connect(self.symmetry_changed)
        
        #self.ch_indx=chIndx
    
    def window_change(self,winOrdisp_bool,win_param_change):
        print("window_change")
        try:
            self.main.window_type_combo.currentIndexChanged.disconnect()
        except Exception:
            pass
        try:
            self.main.display_type_combo.currentIndexChanged.disconnect()
        except Exception:
            pass
        self.win_indx=self.main.window_type_combo.currentIndex()
        self.current_window=self.windows[self.win_indx]
        chIndx=self.main.fft_ch_select.currentIndex()
        
        x=self.main.x[chIndx]
        y=self.main.y[chIndx]
        ch_col=self.main.ch_name_col_list[chIndx][1]
        
        self.view_win_params()
        
        if winOrdisp_bool:###FOR CHANGE in WIndow type
            self.main.display_type_combo.setCurrentIndex( self.ch_display_type_list[chIndx])
            self.ch_window_list[chIndx]=self.current_window
        else:###FOR CHANGE in Display type
            self.disp_type_indx= self.main.display_type_combo.currentIndex()
            self.main.window_type_combo.setCurrentIndex(self.windows.index(self.ch_window_list[chIndx]))
            self.ch_display_type_list[chIndx]=self.disp_type_indx
            if self.disp_type_indx==0:
                for i in range(self.main.fft_ydiv_unit.count()):
                    self.main.fft_ydiv_unit.removeItem(0)
                self.main.fft_ydiv_unit.addItems(["mv","v"])
            elif self.disp_type_indx==1:
                for i in range(self.main.fft_ydiv_unit.count()):
                    self.main.fft_ydiv_unit.removeItem(0)
                self.main.fft_ydiv_unit.addItem("db")
        
        if self.win_has_params==False:
            self.wait_for_parameter_input=False
            self.temp_mem=[]
            self.calculate_fft_update(chIndx,x,y,ch_col)
            self.self_enable_all_except_parameter(True)
            self.show_status(None)
        elif self.win_has_params==True and winOrdisp_bool==False and win_param_change==False:
            self.wait_for_parameter_input=False
            self.temp_mem=[]
            self.calculate_fft_update(chIndx,x,y,ch_col)
            self.self_enable_all_except_parameter(True)
            self.show_status(None)
        elif self.win_has_params==True and winOrdisp_bool==True and win_param_change==False:###expects an enter to input parameter val that is no value was previously input
            #as the window has changed and has parameter
            self.wait_for_parameter_input=True
            self.temp_mem=[chIndx,x,y,ch_col]
            self.self_enable_all_except_parameter(False)
            self.show_status("Enter Windowing parameter and press Enter")
        elif self.win_has_params==True and winOrdisp_bool==True and win_param_change==True:###parameter already shown  but value have changed 
            self.wait_for_parameter_input=False
            self.temp_mem=[]
            self.calculate_fft_update(chIndx,x,y,ch_col)
            self.self_enable_all_except_parameter(True)
            self.show_status(None)
        
        self.main.window_type_combo.currentIndexChanged.connect(lambda: self.window_change(True,False))
        self.main.display_type_combo.currentIndexChanged.connect(lambda: self.window_change(False,False))
    
    def refference_changed(self):
        print("refference changed")
        val=self.main.fft_refference_select_spin.value()
        unit_indx=self.main.fft_refference_select_unit.currentIndex()
        ref_val=self.ref_
        if unit_indx==0:
            self.ref_=val
        elif unit_indx==1:
            self.ref_=val*1000 #ref_in_mv
        chindx=self.main.fft_ch_select.currentIndex()
        self.refference_list[chindx]=[val,unit_indx]
        if ref_val!=self.ref_ and self.ch_display_type_list[chindx]==1:
            print("updating")
            self.calculate_fft_update(chindx,None,None,None)
    
    def fft_CH_enable_toggled(self):
        chIndx=self.main.fft_ch_select.currentIndex()
        
        if self.main.fft_ch_enable.isChecked():
            
            xlim=self.plot_list[chIndx][0].get_xdata()
            ylim=self.plot_list[chIndx][0].get_ydata()
            if self.plot_list[chIndx][0].get_visible()==False:
                self.visible_plotXlim.extend([min(xlim),max(xlim)])
                self.visible_plotYlim.extend([min(ylim),max(ylim)])
                self.plot_list[chIndx][0].set_visible(True)
                self.fftsmall.plot_list[chIndx][0].set_visible(True)
            self.ch_fft_enabled_list[chIndx]=True
            
            if self.zoomwin.isVisible():
                self.zoomwin.show_plot(self.last_shown[0],self.last_shown[1],self.last_shown[2],self.last_shown[3])
            
        else:
            if self.plot_list[chIndx][0].get_visible()==True:
                self.plot_list[chIndx][0].set_visible(False)
                self.fftsmall.plot_list[chIndx][0].set_visible(False)
                self.ch_fft_enabled_list[chIndx]=False
                xlim=self.plot_list[chIndx][0].get_xdata()
                ylim=self.plot_list[chIndx][0].get_ydata()
                
                try:
                    self.visible_plotXlim.remove(min(xlim))
                except Exception:
                    pass
                try:
                    self.visible_plotXlim.remove(max(xlim))
                except Exception:
                    pass
                try:
                    self.visible_plotYlim.remove(min(ylim))
                except Exception:
                    pass
                try:
                    self.visible_plotYlim.remove(max(ylim))
                except Exception:
                    pass
            if self.zoomwin.isVisible():
                self.zoomwin.show_plot(self.last_shown[0],self.last_shown[1],self.last_shown[2],self.last_shown[3])
        if self.rescalex_Extended_bool or self.rescaled_Y:
            self.resize_canvas_toDefault()
            self.axes.yaxis.set_major_locator(AutoLocator())
            self.axes.yaxis.set_minor_locator(AutoMinorLocator(5))
            self.axes.xaxis.set_major_locator(AutoLocator())
            self.axes.xaxis.set_minor_locator(AutoMinorLocator(5))
        
        if self.visible_plotXlim!=[]:
            self.axes.set_xlim([min(self.visible_plotXlim),max(self.visible_plotXlim)])
            self.axes.set_ylim([min(self.visible_plotYlim),max(self.visible_plotYlim)])
            self.fftsmall.axes.set_xlim([min(self.visible_plotXlim),max(self.visible_plotXlim)])
            self.fftsmall.axes.set_ylim([min(self.visible_plotYlim),max(self.visible_plotYlim)])
        self.canvas.draw_idle()
        self.fftsmall.plot_refresh()
    
    def frequency_scale_changed(self):
        scale_type_indx=self.main.frequency_scale.currentIndex()
        self.axes.set_xscale(self.scale_type[scale_type_indx])
        if scale_type_indx==1:
            locmin = ticker.LogLocator(base=10.0, subs=(0.1,0.2,0.4,0.6,0.8,1,2,4,6,8,10)) 
            self.axes.xaxis.set_minor_locator(locmin)
            self.axes.xaxis.set_minor_formatter(ticker.NullFormatter())
        elif scale_type_indx==0:
            self.axes.xaxis.set_minor_locator(AutoMinorLocator(5))
        redraw=True
        if self.rescalex_Out_ranged:
            self.x_limit=[min(self.visible_plotXlim),max(self.visible_plotXlim)]
            self.y_limit=[min(self.visible_plotYlim),max(self.visible_plotYlim)]
            self.resize_canvas_toDefault()
            redraw=False
        if redraw:
            self.canvas.draw_idle()

    def freq_div_changed(self):
        if self.freq_dial_changed:
            fmag=self.freqspin_temp[0]
            funit_indx=self.freqspin_temp[1]
            self.main.freq_div_spin.setValue(fmag)
            self.main.freq_div_unit.setCurrentIndex(funit_indx)
        else:
            fmag=self.main.freq_div_spin.value()
            funit_indx=self.main.freq_div_unit.currentIndex()
        
        freq_per_div_was=self.freq_per_div
        if funit_indx==0:
            self.freq_per_div=fmag
        elif funit_indx==1:
            self.freq_per_div=fmag*1000 #to Hz from kHz
        elif funit_indx==2:
            self.freq_per_div=fmag*1000000 #to Hz from kHz
        print("FREQ:",self.freq_per_div)
        print("FREQ WAS:",freq_per_div_was)
        if self.freq_per_div != freq_per_div_was:
            self.rescale_x()
        self.freq_dial_changed=False
    
    def freqdial_changed(self):
        dial_indx=self.main.freq_dial.value()
        if 0<=dial_indx<=8:
            dial_val=self.freq_dial_vals[dial_indx]
            self.freqspin_temp=[dial_val,0]
            self.main.fft_freqdisp.setText(str(dial_val)+" Hz/div (minor)")
        elif 9<=dial_indx<=17:
            dial_val=self.freq_dial_vals[dial_indx-9]
            self.freqspin_temp=[dial_val,1]
            self.main.fft_freqdisp.setText(str(dial_val)+" kHz/div (minor)")
        elif 18<=dial_indx<=26:
            dial_val=self.freq_dial_vals[dial_indx-18]
            self.freqspin_temp=[dial_val,2]
            self.main.fft_freqdisp.setText(str(dial_val)+" MHz/div (minor)")
        self.freq_dial_changed=True
    
    def fft_y_changed(self):
        yval_indx=self.main.fft_y_dial.value()
        if self.disp_type_indx==0:
            if yval_indx<=11:
                y_div=self.y_dial_vals[yval_indx]
                self.yspinVal_temp=[y_div,0]
                self.main.fft_ydisp.setText(str(y_div)+" mv/div")
            elif 12<=yval_indx<=20:
                y_div=self.y_dial_vals[yval_indx-12]
                self.yspinVal_temp=[y_div,1]
                self.main.fft_ydisp.setText(str(y_div)+" v/div")
        elif self.disp_type_indx==1:
            y_div=self.y_dial_vals[yval_indx]
            self.yspinVal_temp=[y_div,0]
            self.main.fft_ydisp.setText(str(y_div)+" db/div")
        self.ydial_changed=True

    def fft_ydiv_changed(self):
        if self.ydial_changed:
            ymag=self.yspinVal_temp[0]
            ydiv_unit_indx=self.yspinVal_temp[1]
            self.main.fft_ydiv_spin.setValue(ymag)
            self.main.fft_ydiv_unit.setCurrentIndex(ydiv_unit_indx)
        else:
            ymag=self.main.fft_ydiv_spin.value()
            ydiv_unit_indx=self.main.fft_ydiv_unit.currentIndex()
        
        self.y_per_div_was=self.y_per_div
        if ydiv_unit_indx==0:
            self.y_per_div=ymag
        elif ydiv_unit_indx==1:
            self.y_per_div=ymag*1000
        print("Ydiv:",self.y_per_div)
        print("Ydiv WAS:",self.y_per_div_was)
        if self.y_per_div != self.y_per_div_was:
            self.rescale_y()
        self.ydial_changed=False
    
    ########################################### MATH ###########################################
    
    def calculate_fft(self,xi,yi,ch_color,bool_):
        self.main.Window_symetric_Radio.toggled.disconnect(self.sym_radio_connection)
        plot_count=self.main.all_plot_count
        if bool_==True:
            if plot_count>1:
                for i in range(plot_count):
                    self.plot_list[i-1][0].set_visible(False)
                    self.fftsmall.plot_list[i-1][0].set_visible(False)
                    self.ch_fft_enabled_list[i-1]=False
        self.ch_window_symmetry_list.append(self.FFT_window_default_symmetric)
        self.main.Window_symetric_Radio.setChecked(self.FFT_window_default_symmetric)
        #self.ch_indx=plot_count-1
        N=int(len(xi))
        n=int(N/2)
        
        w=self.get_window_with_params(N)
        self.ch_window_param_list.append(self.main.window_params_spin.value())
        
        ch_fft_windowed=np.abs(fftpack.fft(yi*w)*(1/np.mean(w))*(2/N))
        tst_indx=int(N/2)
        dt=xi[tst_indx]-xi[tst_indx-1]
        freqs = fftpack.fftfreq(N,d=dt)
        self.disp_type_indx=self.main.display_type_combo.currentIndex()
        xlims=[min(freqs[:n]),max(freqs[:n])]
        #FFT_Widget.disp_type_indx=self.disp_type_indx
        if self.disp_type_indx==0:#in Amplitude
            plot=self.axes.plot(freqs[:n],ch_fft_windowed[:n],color=ch_color,alpha=self.plot_opacity,zorder=2+plot_count,picker=5)
            ylims=[min(ch_fft_windowed[:n]),max(ch_fft_windowed[:n])]
            self.axes.set_ylim(ylims)
            self.fftsmall.addplot_(freqs[:n],ch_fft_windowed[:n],ch_color,xlims,ylims)
            #self.plot_ylimits.append(ylims)
        elif self.disp_type_indx==1:####in loudness
            loud_db=20*np.log10(ch_fft_windowed/self.ref_)
            plot=self.axes.plot(freqs[:n],loud_db[:n],color=ch_color,alpha=self.plot_opacity,zorder=2+plot_count,picker=5)
            ylims=[min(loud_db[:n]),max(loud_db[:n])]
            self.axes.set_ylim(ylims)
            self.fftsmall.addplot_(freqs[:n],loud_db[:n],ch_color,xlims,ylims)
            #self.plot_ylimits.append(ylims)
        
        self.visible_plotXlim=[xlims[0],xlims[1]]
        self.visible_plotYlim=[ylims[0],ylims[1]]
        
        self.axes.set_xlim(xlims)
        self.axes.yaxis.set_major_locator(AutoLocator())
        self.axes.yaxis.set_minor_locator(AutoMinorLocator(5))
        self.axes.xaxis.set_major_locator(AutoLocator())
        self.axes.xaxis.set_minor_locator(AutoMinorLocator(5))
        if self.rescalex_Extended_bool:
            self.resize_canvas_toDefault()
        #self.plot_xlimits.append(xlims)
        self.first_plot=True
        self.canvas.draw_idle()
        self.fftsmall.plot_refresh()
        self.plot_list.append(plot)
        self.ch_fft_enabled_list.append(True)
        self.ch_window_list.append(self.current_window)
        self.ch_display_type_list.append(self.disp_type_indx)
        self.refference_list.append([5,0])
        self.x_limit=self.visible_plotXlim
        self.y_limit=self.visible_plotYlim
        self.X_lim=[min(self.x_limit),max(self.x_limit)]
        self.sym_radio_connection=self.main.Window_symetric_Radio.toggled.connect(self.symmetry_changed)
        if self.main.fft_panel_frame.isEnabled()==False:
            self.main.fft_panel_frame.setEnabled(True)
    
    def calculate_fft_update(self,ch_indx,xi,yi,ch_color):
        #self.ch_indx=ch_indx
        redraw=True
        if xi==None or yi==None or ch_color==None:
            xi=self.main.x[ch_indx]
            yi=self.main.y[ch_indx]
            ch_color=self.main.ch_name_col_list[ch_indx][1]
        
        N=int(len(xi))
        n=int(N/2)
        
        w = self.get_window_with_params(N)
        self.ch_window_param_list[ch_indx]=self.main.window_params_spin.value()
        ch_fft_windowed=np.abs(fftpack.fft(yi*w)*(1/np.mean(w))*(2/N))
        tst_indx=int(N/2)
        dt=xi[tst_indx]-xi[tst_indx-1]
        freqs = fftpack.fftfreq(N,d=dt)
        self.disp_type_indx=self.main.display_type_combo.currentIndex()
        #FFT_Widget.disp_type_indx=self.disp_type_indx
        
        if self.plot_list[ch_indx][0].get_visible():
            xdata=self.plot_list[ch_indx][0].get_xdata()
            ydata=self.plot_list[ch_indx][0].get_ydata()
            try:
                self.visible_plotXlim.remove(min(xdata))
            except Exception:
                pass
            try:
                self.visible_plotXlim.remove(max(xdata))
            except Exception:
                pass
            try:
                self.visible_plotYlim.remove(min(ydata))
            except Exception:
                pass
            try:
                self.visible_plotYlim.remove(max(ydata))
            except Exception:
                pass
        
        z_order=self.plot_list[ch_indx][0].get_zorder()
        if self.disp_type_indx==0:
            self.plot_list[ch_indx][0].remove()
            
            self.plot_list[ch_indx]=self.axes.plot(freqs[:n],ch_fft_windowed[:n],color=ch_color,alpha=self.plot_opacity,zorder=z_order,picker=5)
            ydata=ch_fft_windowed[:n]
            #self.axes.set_ylim(min(ch_fft_windowed[:n]),max(ch_fft_windowed[:n]))
        elif self.disp_type_indx==1:
            loud_db=20*np.log10(ch_fft_windowed/self.ref_)
            self.plot_list[ch_indx][0].remove()
            
            self.plot_list[ch_indx]=self.axes.plot(freqs[:n],loud_db[:n],color=ch_color,alpha=self.plot_opacity,zorder=z_order,picker=5)
            ydata=loud_db[:n]
            self.refference_list[ch_indx]=[self.main.fft_refference_select_spin.value(),self.main.fft_refference_select_unit.currentIndex()]
            #self.axes.set_ylim(min(loud_db[:n]),max(loud_db[:n]))
        
        edit_small_view=True
        if self.ch_fft_enabled_list[ch_indx]==False:
            self.plot_list[ch_indx][0].set_visible(False)
            self.fftsmall.plot_list[ch_indx][0].set_visible(False)
            edit_small_view=False
        else:
            xdata=freqs[:n]
            self.visible_plotXlim.extend([min(xdata),max(xdata)])
            self.visible_plotYlim.extend([min(ydata),max(ydata)])
            if self.rescalex_Out_ranged:
                self.axes.yaxis.set_major_locator(AutoLocator())
                self.axes.yaxis.set_minor_locator(AutoMinorLocator(5))
                self.axes.xaxis.set_major_locator(AutoLocator())
                self.axes.xaxis.set_minor_locator(AutoMinorLocator(5))
            if self.rescaled_Y:
                self.axes.yaxis.set_major_locator(AutoLocator())
                self.axes.yaxis.set_minor_locator(AutoMinorLocator(5))
                self.rescaled_Y=False
            
            self.axes.set_xlim([min(self.visible_plotXlim),max(self.visible_plotXlim)])
            self.axes.set_ylim([min(self.visible_plotYlim),max(self.visible_plotYlim)])
            
        
        self.x_limit=[min(self.visible_plotXlim),max(self.visible_plotXlim)]
        self.y_limit=[min(self.visible_plotYlim),max(self.visible_plotYlim)]
        self.X_lim=self.x_limit
        if self.rescalex_Out_ranged==True:
            self.resize_canvas_toDefault()
            redraw=False
        
        if redraw:
            print("FFTcalled_draw_idle")
            self.canvas.draw_idle()
        
        if edit_small_view:
            self.fftsmall.edit_plot(ch_indx,xdata,ydata,ch_color,self.x_limit)
        self.fftsmall.axes.set_ylim(self.y_limit)
        self.fftsmall.plot_refresh()
    
    ############################################ PLOT__STYLE #####################################
    def rem_plot_0(self):
        lines=self.axes.get_lines()
        for line in lines:
            line.remove()
        self.plot_list=[]
    
    def change_color(self,ch_indx,ch_color):
        lines=self.axes.get_lines()
        lines[ch_indx].set_color(ch_color)
        self.canvas.draw_idle()
    
    def rescale_x(self):
        freq_per_div=self.freq_per_div
        canvas_width=self.canvas.size().width()
        self.last_width=canvas_width
        major_ticks=5
        minor_ticks=5
        freq_range=max(self.visible_plotXlim)-min(self.visible_plotXlim)
        max_div_to_draw=freq_range/freq_per_div
        division_size=self.default_canvas_width/25
        max_size_needed=int(division_size*max_div_to_draw)
        max_scalable_width=32768
        
        print("Max size needed:",max_size_needed)
        
        if max_size_needed<max_scalable_width:#Scale in Range
            print("FFT Scalling in Range")
            
            xtics_step=freq_per_div*5
            
            current_scrol_area_width=self.fftw.scrollArea.size().width()
            
            if max_size_needed<current_scrol_area_width:#scale in range small
                print("FFT Scalling in Range:SMALL")
                scallable_max_x=min(self.visible_plotXlim)+xtics_step*major_ticks
                self.x_limit=[min(self.visible_plotXlim),scallable_max_x]
                self.canvas.resize(current_scrol_area_width,self.canvas.size().height())
                ticks=np.arange(self.x_limit[0],self.x_limit[1],step=xtics_step)
                
                self.rescalex_Extended_bool=False
                self.rescalex_Out_ranged=False
            else : #scale in range extended
                print("FFT Scalling in Range:EXTENDED")
                self.x_limit=self.X_lim
                self.canvas.resize(max_size_needed,self.fftw.scrollArea.size().height()-24)
                ticks=np.arange(self.x_limit[0],self.x_limit[1],step=xtics_step)
                
                self.rescalex_Extended_bool=True
                self.rescalex_Out_ranged=False
            self.axes.set_xticks(ticks)
            
            self.axes.set_xlim(self.x_limit)
            if canvas_width==self.canvas.size().width():
                self.canvas.draw_idle()
        else:
            
            print("FFT Scalling out of  Range")
            max_scallable_div=max_scalable_width/division_size###no of divisions possible to draw
            max_scallable_freq_val=max_scallable_div*freq_per_div+min(self.visible_plotXlim)##value of maximum freq limit that can be plot
            scrl_val=self.fftw.scrollArea.horizontalScrollBar().value()
            scrl_pagestep=self.fftw.scrollArea.horizontalScrollBar().pageStep()
            
            xtics_step=freq_per_div*5
            if scrl_val==0:
                self.x_limit=[min(self.visible_plotXlim),min(self.visible_plotXlim)+max_scallable_freq_val]
                
            else:###if scrollcvalue is not zero
                if self.fftsmall.rescale_done_by_selection:
                    x_mid_=self.fftsmall.reseted_mid
                    self.fftsmall.rescale_done_by_selection=False
                else:
                    x_mid_=self.px2pt.transform(((scrl_val+scrl_pagestep/2),0))[0]
                
                if (x_mid_-max_scallable_freq_val/2)<min(self.visible_plotXlim):
                    ####ATTACHED TO LEFT
                    print("FFT Scalling out of Range:ATTACHED_LEFT")
                    self.x_limit=[min(self.visible_plotXlim),min(self.visible_plotXlim)+max_scallable_freq_val]
                    
                elif (x_mid_+max_scallable_freq_val/2)>max(self.visible_plotXlim):
                    ##ATTACHED TO RIGHT
                    print("FFT Scalling out of Range:ATTACHED_RIGHT")
                    self.x_limit=[max(self.visible_plotXlim)-max_scallable_freq_val,max(self.visible_plotXlim)]
                else:
                    print("FFT Scalling out of Range:SOMEWHERE_MID")
                    self.x_limit=[x_mid_-max_scallable_freq_val/2,x_mid_+max_scallable_freq_val/2]
                    
            ticks=np.arange(self.x_limit[0],self.x_limit[1],step=xtics_step)
            self.axes.set_xlim(self.x_limit)
            self.axes.set_xticks(ticks)
            self.canvas.resize(max_scalable_width,self.fftw.scrollArea.size().height()-24)
            if canvas_width==max_scalable_width:
                self.canvas.draw_idle()
            self.rescalex_Extended_bool=True
            self.rescalex_Out_ranged=True
            self.rubberBand_reds_notDrawn=True
      
    def rescale_y(self):
        ylim=[min(self.visible_plotYlim),max(self.visible_plotYlim)]
        y_minor_per_div=self.y_per_div/5
        ytics_step=self.y_per_div
        no_of_minor_divs=25
        self.y_limit=[ylim[0],ylim[0]+no_of_minor_divs*y_minor_per_div]
        ticks=np.arange(self.y_limit[0],self.y_limit[1],step=ytics_step)
        self.axes.set_ylim(self.y_limit)
        self.axes.set_yticks(ticks)
        self.canvas.draw_idle()
        self.fftsmall.axes.set_ylim(self.y_limit)
        self.fftsmall.plot_refresh()
        self.rescaled_Y=True
        
    def set_freq_div_dial(self,freq):
        self.main.freq_dial.disconnect(self.freqdial_valConnection)
        if freq>=1000:###in kHz
            freq=freq/1000
            self.main.freq_div_spin.setValue(freq)
            self.main.freq_div_unit.setCurrentIndex(1)
            indx=self.main.get_closest_index(self.freq_dial_vals,freq)
            self.main.freq_dial.setValue(indx+9)
            self.main.fft_freqdisp.setText(str(freq)+" kHz/div (minor)")
            
            if freq>=1000:
                freq=freq/1000
                self.main.freq_div_spin.setValue(freq)
                self.main.freq_div_unit.setCurrentIndex(2)
                indx=self.main.get_closest_index(self.freq_dial_vals,freq)
                self.main.freq_dial.setValue(indx+18)
                self.main.fft_freqdisp.setText(str(freq)+" MHz/div (minor)")
        else:
            self.main.freq_div_spin.setValue(freq)
            self.main.freq_div_unit.setCurrentIndex(0)
            indx=self.main.get_closest_index(self.freq_dial_vals,freq)
            self.main.freq_dial.setValue(indx)
            self.main.fft_freqdisp.setText(str(freq)+" Hz/div (minor)")
        
        self.freqdial_valConnection=self.main.freq_dial.valueChanged.connect(self.freqdial_changed)
    
    def set_ydiv_dial(self,y_div):
        
        self.main.fft_y_dial.disconnect(self.fft_y_dial_connection)
        if self.disp_type_indx==0:
            if y_div>=1000:###in mV
                y_div=y_div/1000
                self.main.fft_ydiv_spin.setValue(y_div)
                self.main.fft_ydiv_unit.setCurrentIndex(1)
                self.main.fft_ydisp.setText(str(y_div)+" v/div")
                
                yindx=self.main.get_closest_index(self.y_dial_vals,y_div)
                if yindx<=11:
                    yindx=yindx+12
                self.main.fft_y_dial.setValue(yindx)
                
            else:
                self.main.fft_ydiv_spin.setValue(y_div)
                self.main.fft_ydiv_unit.setCurrentIndex(0)
                self.main.fft_ydisp.setText(str(y_div)+" mv/div")
                yindx=self.main.get_closest_index(self.y_dial_vals,y_div)
                if yindx>=12:
                    yindx=yindx-12
                self.main.fft_y_dial.setValue(yindx)
                
        elif self.disp_type_indx==1:
            self.main.fft_ydiv_spin.setValue(y_div)
            self.main.fft_ydiv_unit.setCurrentIndex(0)
            self.main.fft_ydisp.setText(str(y_div)+" db/div")
            yindx=self.main.get_closest_index(self.y_dial_vals,y_div)
            self.main.fft_y_dial.setValue(yindx)
            
        self.fft_y_dial_connection=self.main.fft_y_dial.valueChanged.connect(self.fft_y_changed)
    
    def resize_canvas_toDefault(self):
        self.rescalex_Out_ranged=False
        self.rescaled_Y=False
        self.rescalex_Extended_bool=False
        self.canvas.resize(self.fftw.scrollArea.size().width(),self.fftw.scrollArea.size().height()-24)
        #return redraw
    
    ###################################RUBBERBANDS#################################################
    def define_rubberband(self):
        self.rubberBand = QRubberBand(QRubberBand.Rectangle, self.fftsmall.canvas)
        self.rubberBand1 = QRubberBand(QRubberBand.Rectangle, self.fftsmall.canvas)
        self.rubberBand_red = QRubberBand(QRubberBand.Rectangle, self.fftsmall.canvas)
        self.rubberBand_red1 = QRubberBand(QRubberBand.Rectangle, self.fftsmall.canvas)
        
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
        X_lim=self.X_lim
        
        canvas_page_start=self.fftw.scrollArea.horizontalScrollBar().value()
        scroll_page_step=self.fftw.scrollArea.horizontalScrollBar().pageStep()
        small_canvas_width=self.fftsmall.canvas.size().width()
        canvas_page_end=canvas_page_start+scroll_page_step

        self.canvas_page_start_point=self.px2pt.transform((canvas_page_start,0))
        self.canvas_page_end_point=self.px2pt.transform((canvas_page_end,0))
        
        plotXlim=self.axes.get_xlim()
        
        self.CoordMin=self.fftsmall_pt2px.transform((plotXlim[0],0))[0]
        self.CoordMax=self.fftsmall_pt2px.transform((plotXlim[1],0))[0]
        self.small_view_start_pos=self.fftsmall_pt2px.transform(self.canvas_page_start_point)[0]
        self.small_view_end_pos=self.fftsmall_pt2px.transform(self.canvas_page_end_point)[0]
        
        if [plotXlim[0],plotXlim[1]]==X_lim:
            self.CoordMin=0
            self.CoordMax=small_canvas_width
            self.rubberBand_red.hide()
            self.rubberBand_red1.hide()
            
        elif self.rescalex_Out_ranged and self.rubberBand_reds_notDrawn:
            self.rubberBand_red.setGeometry(QRect(QPoint(0,0),QPoint(int(self.CoordMin),60)))
            self.rubberBand_red1.setGeometry(QRect(QPoint(int(self.CoordMax),0),QPoint(small_canvas_width,60)))
            self.rubberBand_red.show()
            self.rubberBand_red1.show()
            self.rubberBand_reds_notDrawn=False
        
        self.rubberBand.setGeometry(QRect(QPoint(int(self.CoordMin),0),QPoint(int(self.small_view_start_pos),60)))
        self.rubberBand1.setGeometry(QRect(QPoint(int(self.small_view_end_pos),0),QPoint(int(self.CoordMax),60)))
        
        self.rubberBand.show()
        self.rubberBand1.show()
    
    def ZoomsetDrawRect(self,xdata,ydata,freq_per_div,y_per_div):
        ex,ey=self.pt2px.transform((xdata,ydata))
        rect_width=self.pt2px.transform((freq_per_div,0))[0]-self.pt2px.transform((0,0))[0]
        rect_height=self.pt2px.transform((0,y_per_div))[1]-self.pt2px.transform((0,0))[1]
        rect_posX=ex-rect_width/2
        rect_posy=self.canvas.size().height()-(ey+rect_height/2)
        self.bounding_Box.setGeometry(QRect(rect_posX,rect_posy,rect_width,rect_height))
    
    ########################################### ANNOTATION ########################@############
    def remove_annotations(self):
        for i in range(len(self.annotations_max)):
            self.annotations_max[i].remove()
        self.annotations_max=[]
    
    def check_loc_and_annotate(self,dat_x,dat_y,xlim,ylim,annots):
        ###annots is a multiplier that gives a seperations between closely spaced annotations
        annot_offset_x=self.annot_offset_x+annots
        annot_offset_y=self.annot_offset_y+annots*20
        annot_loc_x=dat_x+annot_offset_x
        annot_loc_y=dat_y+annot_offset_y
        
        if xlim[0]<=annot_loc_x:####If in Left X limit
            if not annot_loc_x <=xlim[1]-1.5*self.lim_offset_x: ###But not in Right X limit
                
                annot_offset_x=-2*annot_offset_x ####that is shifted right
                
        elif not xlim[0]<=annot_loc_x:### if not in left x limit
            if annot_loc_x <=xlim[1]-1.5*self.lim_offset_x: ###But in Right X limit
                
                annot_offset_x=2*annot_offset_x####that is shifted left
                
        
        if ylim[0]<=annot_loc_y:####If in lower Y limit
            if not annot_loc_y <=ylim[1]: ###But not in higher Y limit
                
                annot_offset_y=-annot_offset_y ####that is shifted up
                
        elif not ylim[0]<=annot_loc_y:### if not lower Y limit
            if annot_loc_y <=ylim[1]: ###But in Upper  Y limit
                
                annot_offset_y=2*annot_offset_y####that is shifted down
        
        print("offsets",annot_offset_x,annot_offset_y)
        ann=self.axes.annotate('(%.1f, %.1f)'%(dat_x, dat_y),(dat_x, dat_y), 
                                        color="black",xytext =(annot_offset_x, annot_offset_y),
                                        textcoords ='offset points',  arrowprops = self.arrowprops,
                                        bbox = dict(boxstyle="round4,pad=0.3", fc="w",alpha=self.zoomwin.annot_opacity, ))
        self.annotations_max.append(ann)
    
    ################################################## RESET AXIS VIEW #####################################
    def reset_axis_view(self):
        self.rescalex_Out_ranged=False
        self.rescaled_Y=False
        self.rescalex_Extended_bool=False
        
        self.axes.yaxis.set_major_locator(AutoLocator())
        self.axes.yaxis.set_minor_locator(AutoMinorLocator(5))
        self.axes.xaxis.set_major_locator(AutoLocator())
        self.axes.xaxis.set_minor_locator(AutoMinorLocator(5))
        self.axes.set_xlim([min(self.visible_plotXlim),max(self.visible_plotXlim)])
        self.axes.set_ylim([min(self.visible_plotYlim),max(self.visible_plotYlim)])
        cs=self.canvas.size().width()
        sw=self.fftw.scrollArea.size().width()
        self.canvas.resize(sw,self.fftw.scrollArea.size().height()-24)
        if cs==sw:
            self.canvas.draw_idle()

    def get_config(self):
        if self.main.conf.FFT_zoom_multiplier!=[None,False]:
            self.zoomwin.zoom_multiplier=self.main.conf.FFT_zoom_multiplier
        
        if self.main.conf.FFT_annotation_offset!=[None,None,False]:
            print("self.main.conf.FFT_annotation_offset",self.main.conf.FFT_annotation_offset)
            self.zoomwin.annot_offset_x,self.zoomwin.annot_offset_y=self.main.conf.FFT_annotation_offset
        
        if self.main.conf.FFT_keep_annotations!=[None,False]:
            self.zoomwin.keep_annotations=self.main.conf.FFT_keep_annotations
        
        if self.main.conf.FFT_Max_points_to_show!=[None,False]:
            self.zoomwin.max_pt2show=self.main.conf.FFT_Max_points_to_show
        
        if self.main.conf.FFT_annotation_opacity!=[None,False]:
            self.zoomwin.annot_opacity=self.main.conf.FFT_annotation_opacity
            
        if self.main.conf.FFT_window_default_symmetric!=[None,False]:
            self.FFT_window_default_symmetric=self.main.conf.FFT_window_default_symmetric

    '''def get_closest_index(self,list_,c):
        temp_list=[] 
        for i in range(len(list_)):
            temp_list.append(abs(list_[i]- c))
        return temp_list.index(min(temp_list))'''
    
    def get_plot_opacity(self,bool_):
        plot_opacity=self.plot_opacity
        if self.main.conf.FFT_line_opacity!=[None,False]:
            self.plot_opacity=self.main.conf.FFT_line_opacity
        else:
            self.plot_opacity=1
        if plot_opacity!=self.plot_opacity and bool_==True:
            for i in range(len(self.plot_list)):
                self.plot_list[i][0].set_alpha(self.plot_opacity)
            self.canvas.draw_idle()
    
    def View_params_box(self,bool_):
        self.main.window_params_label.setVisible(bool_)
        self.main.window_params_spin.setVisible(bool_)
    
    def get_window_with_params(self,N):
        if 14<=self.win_indx<=len(self.windows):
            if self.current_window=="chebwin":
                
                w = signal.chebwin(N, self.main.window_params_spin.value(),self.main.Window_symetric_Radio.isChecked())
            elif self.current_window=="gaussian":
                
                w = signal.gaussian(N, self.main.window_params_spin.value(),self.main.Window_symetric_Radio.isChecked())
            elif self.current_window=="kaiser":
                
                w = signal.kaiser(N, self.main.window_params_spin.value(),self.main.Window_symetric_Radio.isChecked())
            elif self.current_window=="slepian":
                
                w = signal.slepian(N, self.main.window_params_spin.value(),self.main.Window_symetric_Radio.isChecked())
            elif self.current_window=="tukey":
               
                w = signal.tukey(N, self.main.window_params_spin.value(),self.main.Window_symetric_Radio.isChecked())
        else:
            w = get_window(self.current_window, N,self.main.Window_symetric_Radio.isChecked())
        return w
    
    def view_win_params(self):
        if 14<=self.win_indx<=len(self.windows):##############needs parameters to be shown
            self.View_params_box(True)
            self.win_has_params=True
            if self.current_window=="chebwin":
                self.main.window_params_label.setText("Attenuation")
            elif self.current_window=="gaussian":
                self.main.window_params_label.setText("std")
            elif self.current_window=="kaiser":
                self.main.window_params_label.setText("Beta")
            elif self.current_window=="slepian":
                self.main.window_params_label.setText("width")
            elif self.current_window=="tukey":
                self.main.window_params_label.setText("alpha")
        else:
            self.win_has_params=False
            self.View_params_box(False)
    
    def resume_calculate_fft(self):
        if self.wait_for_parameter_input:
            self.param=self.main.window_params_spin.value()
            chIndx,x,y,ch_col=self.temp_mem
            self.calculate_fft_update(chIndx,x,y,ch_col)
            self.show_status(None)
            self.wait_for_parameter_input=False
            self.temp_mem=[]
            self.self_enable_all_except_parameter(True)
        else:
            param=self.param
            if param!=self.main.window_params_spin.value():
                
                self.window_change(True,True)##window changed with only paramameter change
    
    def self_enable_all_except_parameter(self,bool_):
        self.main.fft_ch_enable.setEnabled(bool_)
        self.main.fft_ch_select.setEnabled(bool_)
        
        self.main.Window_symetric_Radio.setEnabled(bool_)
        self.main.Window_symetric_lab.setEnabled(bool_)
        self.main.display_type_combo.setEnabled(bool_)
        self.main.label_3.setEnabled(bool_)
        self.main.fft_refference_select_spin.setEnabled(bool_)
        self.main.fft_refference_select_unit.setEnabled(bool_)
        self.main.fft_ydiv_spin.setEnabled(bool_)
        self.main.fft_ydiv_unit.setEnabled(bool_)
        self.main.fft_y_dial.setEnabled(bool_)
        self.main.fft_ydisp.setEnabled(bool_)
        self.main.label.setEnabled(bool_)
        self.main.label_4.setEnabled(bool_)
        self.main.frequency_scale.setEnabled(bool_)
        self.main.label_70.setEnabled(bool_)
        self.main.freq_div_spin.setEnabled(bool_)
        self.main.freq_div_unit.setEnabled(bool_)
        self.main.fft_freqdisp.setEnabled(bool_)
        self.main.freq_dial.setEnabled(bool_)
        self.main.reset_axes.setEnabled(bool_)
        
    def show_status(self,text):
        if text!=None:
            self.toolbar.labelAction1.setVisible(True)
            self.toolbar.labelAction.setVisible(False)
            self.toolbar.statusLabel.setText(text)
        elif text==None:
            self.toolbar.labelAction1.setVisible(False)
            self.toolbar.labelAction.setVisible(True)
            self.toolbar.statusLabel.setText("")
    
    def symmetry_changed(self):
        chIndx=self.main.fft_ch_select.currentIndex()

        if self.main.Window_symetric_Radio.isChecked():
            self.ch_window_symmetry_list[chIndx]=True
        else:
            self.ch_window_symmetry_list[chIndx]=False
        
        self.calculate_fft_update(chIndx,None,None,None)

#bug multiplot labels
#to Default refference value in settings
#toDo measurement_win roundfactor val, ch_opacity in settings
#BUG image bug.jpeg when scalled out ranged and then in range small red doesnot vanishes
