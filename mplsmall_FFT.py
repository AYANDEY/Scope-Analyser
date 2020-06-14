from PyQt5.QtWidgets import *
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5 import QtCore
import threading
from PyQt5.Qt import QPoint, QRect

class mplsmall_FFT(QWidget):
    def __init__(self,parent=None):
        QWidget.__init__(self)
        self.setMaximumHeight(60)
        self.verticalLayout = QVBoxLayout(self)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setSpacing(0)
        self.scrollArea = QScrollArea(self)
        self.scrollArea.setWidgetResizable(False)
        self.scrollArea.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.scrollArea.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.figure = plt.figure() #QWidget  //FigureCanvas//Figure// subplot
        self.axes = self.figure.add_subplot(1, 1, 1)
        self.canvas = FigureCanvas(self.figure)  # FigureCanvas//Figure// called canvas
        self.figure.set_facecolor("black")
        self.scrollArea.setSizePolicy(QSizePolicy.Minimum,QSizePolicy.Maximum)
        self.scrollArea.setContentsMargins(0, 0, 0, 0)
        self.scrollArea.setStyleSheet("border:0px;padding:0px")
        self.scrollArea.setWidget(self.canvas)
        self.verticalLayout.addWidget(self.scrollArea)
        self.canvas.mpl_connect('draw_event',self.On_Canvas_drawn)
        self.plot_list=[]
        self.line_list=[]
        self.canvas.setFocusPolicy( QtCore.Qt.ClickFocus )
        #self.canvas.mpl_connect('key_press_event', self.mpEvent)
        self.canvas.mpl_connect('button_press_event', self.mouse_pressed)
        self.canvas.mpl_connect('button_release_event', self.mouse_released)
        self.canvas.mpl_connect('motion_notify_event',self.mouse_in_motion)
        self.is_clicked=False
        self.green_clicked=False
        self.rescale_done_by_selection=False
    
    def init_fig(self,parent):
        self.main=parent
        #self.axes = self.figure.add_subplot(1, 1, 1)
        self.axes.set_in_layout(False)
        self.axes.patch.set_facecolor('xkcd:black')
        self.axes.set_yticklabels([])
        self.figure.tight_layout(pad=0, w_pad=None, h_pad=None)
        self.fft_zoomwin=self.main.fftW.zoomwin
    
    #####################################events############################################
    
    def resizeEvent(self,event):
        QWidget.resizeEvent(self, event)
        self.main.printf_("small Win resized")
        
    def showEvent(self, event):
        QWidget.showEvent(self, event)
        self.main.printf_("shown_small")
        
    def On_Canvas_drawn(self,draw_event):
        self.main.printf_("Draw_evt_on FFT_small")
        
    def mouse_pressed(self, e):
        self.main.printf_("pressed")

    #######################################PLOT#################################################

    def addplot_(self,x_,y_,ch_color,xlimit,ylimit):
        plot_ = self.axes.plot(x_,y_,color=ch_color)
        self.axes.set_yticklabels([])
        self.axes.set(xlim=xlimit,ylim=ylimit,autoscale_on=False)
        self.plot_list.append(plot_)
        self.line_list.append(plot_[0])
        self.fft_zoomwin.addplot_(x_,y_,ch_color,xlimit)
        
    
    def plot_refresh(self):
        draw_thrd=threading.Thread(target=self.canvas.draw_idle()).start()
        self.fft_zoomwin.plot_refresh()
   
    def rem_plot_0(self):
        self.plot_list[0][0].remove()
        self.plot_list=[]
        self.line_list=[]
        self.fft_zoomwin.rem_plot_0()
        
    def edit_plot(self,plot_num,x_,y_,ch_color,x_limit):
        self.plot_list[plot_num][0].remove()
        plot_=self.axes.plot(x_,y_, color=ch_color)
        self.plot_list[plot_num]=plot_
        self.line_list[plot_num]=plot_[0]
        self.axes.set_xlim(x_limit[0],x_limit[1])
        self.main.printf_("small limit:",x_limit[0],x_limit[1])
        self.fft_zoomwin.edit_plot(plot_num,x_,y_,ch_color,x_limit)
    
    def change_color(self,lineno,col):
        self.axes.get_lines()[lineno].set_color(col)
        self.fft_zoomwin.change_color(lineno,col)
        
    def mouse_pressed(self, e):
        if self.main.fftW.small_view_start_pos<e.x and  e.x<self.main.fftW.small_view_end_pos:
            self.main.printf_("clk_inside")
            self.click_pos=e.x
            self.Scroll_val_at_clicked=self.main.FFT_Widget.scrollArea.horizontalScrollBar().value()
            main_c_width=self.main.FFT_Widget.canvas.size().width()
            self.width_ratio=main_c_width/self.canvas.size().width()
            self.is_clicked=True
            self.main.printf_("CLICKED_VAL:",self.Scroll_val_at_clicked)
        elif e.x>self.main.fftW.CoordMin and e.x<self.main.fftW.CoordMax and self.main.fftW.rescalex_Out_ranged:
            self.canvas_width=self.canvas.size().width()
            self.click_pos=e.x
            self.green_clicked=True
        self.main.printf_("pressed")
    
    def mouse_released(self,e):
        self.is_clicked=False
        if self.green_clicked==True:
            mid_pt=((self.main.fftW.CoordMin+self.main.fftW.CoordMax)/2)+self.change_in_pos###start_pos+(end_pos-start_pos)/2
            self.reseted_mid=self.main.fftW.fftsmall_px2pt.transform((mid_pt,0))[0]
            self.green_clicked=False
            self.rescale_done_by_selection=True
            if hasattr(self, "scale_thread")==True:
                if self.scale_thread.is_alive():
                    self.scale_thread.cancel()
            self.scale_thread=threading.Thread(target=self.main.fftW.rescale_x)
            self.scale_thread.start()
    
    def mouse_in_motion(self,e):
        if self.is_clicked==True:
            self.main.printf_("CLICKED_VAL:",self.Scroll_val_at_clicked,"pos:",e.x,"change_in_pos:",(e.x-self.click_pos))
            change_in_pos=(e.x-self.click_pos)*self.width_ratio
            self.main.FFT_Widget.scrollArea.horizontalScrollBar().setValue(self.Scroll_val_at_clicked+change_in_pos)
        elif self.green_clicked==True:
            change_in_pos=(e.x-self.click_pos)
            if (self.main.fftW.CoordMin+change_in_pos)>0 and (self.main.fftW.CoordMax+change_in_pos)<self.canvas_width:
                self.change_in_pos=change_in_pos
                self.rubberbands_draw_shifted(self.change_in_pos)
    
    ############################################Redraw_Rubberbands########################################
    def rubberbands_draw_shifted(self,ch_in_pos):
        self.main.fftW.rubberBand_red.hide()
        self.main.fftW.rubberBand_red1.hide()
        self.main.fftW.rubberBand.setGeometry(QRect(QPoint(int(self.main.fftW.CoordMin+self.change_in_pos),0),QPoint(int(self.main.fftW.small_view_start_pos+self.change_in_pos),60)))
        self.main.fftW.rubberBand1.setGeometry(QRect(QPoint(int(self.main.fftW.small_view_end_pos+self.change_in_pos),0),QPoint(int(self.main.fftW.CoordMax+self.change_in_pos),60)))
        

#changelog
#changed on plot rescaled to main plot when rescaled out of range which is unwanted in case of smallplot
