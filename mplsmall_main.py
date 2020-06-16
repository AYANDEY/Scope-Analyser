from PyQt5.QtWidgets import *
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5 import QtCore
import threading
from PyQt5.Qt import QPoint, QRect

class mplsmall_main(QWidget):
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
        self.axes_list=[]
        self.plot_list=[]
        self.line_list=[]
        #self.canvas.setFocusPolicy( QtCore.Qt.ClickFocus )
        #self.canvas.mpl_connect('key_press_event', self.mpEvent)
        self.canvas.mpl_connect('button_press_event', self.mouse_pressed)
        self.canvas.mpl_connect('button_release_event', self.mouse_released)
        self.canvas.mpl_connect('motion_notify_event',self.mouse_in_motion)
        self.is_clicked=False
        self.green_clicked=False
        self.rescale_done_by_selection=False
    
    #####################################events############################################
    def resizeEvent(self,event):
        QWidget.resizeEvent(self, event)
        print("small Win resized")
    
    def showEvent(self, event):
        QWidget.showEvent(self, event)
        print("shown_small")
    
    def On_Canvas_drawn(self,draw_event):
        print("Draw_evt_on small")
        pass
   
    def mouse_pressed(self, e):
        if self.main.small_view_start_pos<e.x and  e.x<self.main.small_view_end_pos:
            #print("clk_inside")
            self.click_pos=e.x
            self.Scroll_val_at_clicked=self.main.MplWidget.scrollArea.horizontalScrollBar().value()
            main_c_width=self.main.MplWidget.canvas.size().width()
            self.width_ratio=main_c_width/self.canvas.size().width()
            self.is_clicked=True
            #print("CLICKED_VAL:",self.Scroll_val_at_clicked)
        elif e.x>self.main.CoordMin and e.x<self.main.CoordMax and self.main.plotted_out_of_range:
            self.canvas_width=self.canvas.size().width()
            self.click_pos=e.x
            self.green_clicked=True
        
    
    def mouse_released(self,e):
        self.is_clicked=False
        if self.green_clicked==True:
            mid_pt=((self.main.CoordMin+self.main.CoordMax)/2)+self.change_in_pos###start_pos+(end_pos-start_pos)/2
            self.reseted_mid=self.main.mplsmall_px2pt.transform((mid_pt,0))[0]
            self.green_clicked=False
            self.rescale_done_by_selection=True
            if hasattr(self, "scale_thread")==True:
                if self.scale_thread.is_alive():
                    self.scale_thread.cancel()
            self.scale_thread=threading.Thread(target=self.main.rescale_x)
            self.scale_thread.start()
    
    def mouse_in_motion(self,e):
        if self.is_clicked==True:
            #print("CLICKED_VAL:",self.Scroll_val_at_clicked,"pos:",e.x,"change_in_pos:",(e.x-self.click_pos))
            change_in_pos=(e.x-self.click_pos)*self.width_ratio
            self.main.MplWidget.scrollArea.horizontalScrollBar().setValue(self.Scroll_val_at_clicked+change_in_pos)
        elif self.green_clicked==True:
            change_in_pos=(e.x-self.click_pos)
            if (self.main.CoordMin+change_in_pos)>0 and (self.main.CoordMax+change_in_pos)<self.canvas_width:
                self.change_in_pos=change_in_pos
                self.rubberbands_draw_shifted(self.change_in_pos)
    
    #######################################PLOT#################################################
    def addplot_(self,x_,y_,ch_color,xlimit):
        ax=self.axes.twiny()
        plot_ = ax.plot(x_,y_,color=ch_color)
        ax.set_yticklabels([])
        ax.set(xlim=xlimit,autoscale_on=False)
        i=0
        for i in range(len(self.axes_list)):
            self.axes_list[i].set(xlim=xlimit,autoscale_on=False)
            i+=1
        self.axes.set(xlim=xlimit,autoscale_on=False)
        self.axes_list.append(ax)
        self.plot_list.append(plot_)
        self.line_list.append(plot_[0])
    
    def change_color(self,lineno,col,):
        self.axes_list[lineno].get_lines()[lineno].set_color(col)
    
    def edit_plot(self,plot_num,x_,y_,ch_color,x_limit):
        self.axes_list[plot_num].clear()
        plot_=self.axes_list[plot_num].plot(x_,y_, color=ch_color)
        self.axes_list[plot_num].set_yticklabels([])
        
        if self.main.plotted_out_of_range==False:
            self.axes_list[plot_num].set_xlim(x_limit[0],x_limit[1])
            self.axes.set_xlim(x_limit[0],x_limit[1])
        else:
            self.axes_list[plot_num].set_xlim(self.axes.get_xlim())
        #print("small limit:",x_limit[0],x_limit[1])
        self.plot_list[plot_num]=plot_
        self.line_list[plot_num]=plot_[0]
        
    def rem_plot_0(self):
        self.axes_list[0].clear()
        self.axes_list=[]
        self.plot_list=[]
        self.line_list=[]

    def refresh_plot(self):
        draw_thrd=threading.Thread(target=self.canvas.draw_idle()).start()
    
    def init_fig(self,parent):
        self.main=parent
        #self.axes = self.figure.add_subplot(1, 1, 1)
        self.axes.set_in_layout(False)
        self.axes.patch.set_facecolor('xkcd:black')
        self.axes.set_yticklabels([])
        self.figure.tight_layout(pad=0, w_pad=None, h_pad=0)
        self.axes.set_ylim(self.main.main_ylim)
    
    ############################################Redraw_Rubberbands########################################
    def rubberbands_draw_shifted(self,ch_in_pos):
        self.main.rubberBand_red.hide()
        self.main.rubberBand_red1.hide()
        self.main.rubberBand.setGeometry(QRect(QPoint(int(self.main.CoordMin+self.change_in_pos),0),QPoint(int(self.main.small_view_start_pos+self.change_in_pos),60)))
        self.main.rubberBand1.setGeometry(QRect(QPoint(int(self.main.small_view_end_pos+self.change_in_pos),0),QPoint(int(self.main.CoordMax+self.change_in_pos),60)))
    
#changelog
#changed on plot rescaled to main plot when rescaled out of range which is unwanted in case of smallplot
'''def edit_plot(self,plot_num,x_,y_,ch_color,x_limit):
        self.axes_list[plot_num].clear()
        plot_=self.axes_list[plot_num].plot(x_,y_, color=ch_color)
        self.axes_list[plot_num].set_yticklabels([])
        self.axes_list[plot_num].set_xlim(x_limit[0],x_limit[1])
        
        self.axes.set_xlim(x_limit[0],x_limit[1])
        print("small limit:",x_limit[0],x_limit[1])'''