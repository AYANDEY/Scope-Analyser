from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QHBoxLayout, QLabel, QPushButton, QVBoxLayout
from PyQt5.QtCore import QPoint, Qt
from matplotlib import pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.Qt import QScrollArea, QSizePolicy
import numpy as np
import threading

from matplotlib.ticker import AutoLocator, AutoMinorLocator
import sys
from matplotlib.backend_bases import MouseButton
from scipy.signal import argrelextrema

class fft_zoom_(QtWidgets.QWidget):
    def __init__(self,parent):
        super(fft_zoom_,self).__init__()
        self.fft_widget_=parent
        self.verticalLayout = QVBoxLayout(self)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setSpacing(0)
        self.figure = plt.figure() #QWidget  //FigureCanvas//Figure// subplot
        self.plot=plt
        self.canvas = FigureCanvas(self.figure)  # FigureCanvas//Figure// called canvas
        self.figure.set_facecolor("black")
        self.axes=self.figure.add_subplot(1,1,1)
        self.verticalLayout.addWidget(self.canvas)
        self.shown=False
        self.plot_list=[]
        self.xdata=[]
        self.ydata=[]
        self.axes.set_in_layout(True)
        self.axes.patch.set_facecolor('xkcd:black')
        self.figure.tight_layout(pad=1.5, w_pad=None, h_pad=None)
        
        #self.zoomwin_maxsize=[382,220]
        self.resize(self.fft_widget_.main.zoomsize[0],self.fft_widget_.main.zoomsize[1])
        self.axes.grid(which='major', axis="both", alpha=0.9, linestyle='--',color='white')
        self.axes.grid(b=False,which='minor',axis="both")

        self.axes.patch.set_facecolor('xkcd:black')
        self.axes.spines['bottom'].set_color('white')
        self.axes.spines['top'].set_color('white')
        self.axes.spines['right'].set_color('white')
        self.axes.spines['left'].set_color('white')
        self.axes.tick_params(axis='x', colors='white')
        self.axes.tick_params(axis='y', colors='white')
        self.setWindowFlags(QtCore.Qt.WindowFlags(QtCore.Qt.WindowStaysOnTopHint))
        self.setWindowTitle("Zoomed FFT")
        self.ctrl=False
        self.canvas.setFocusPolicy( QtCore.Qt.ClickFocus )
        self.canvas.setFocus()
        self.leftclick=False
        self.rightclick=False
        self.zoom_history_list=[]
        self.canvas.mpl_connect('key_press_event',self.onKeyPressed)
        self.canvas.mpl_connect('key_release_event',self.onKeyReleased)
        self.canvas.mpl_connect('button_press_event',self.onMouseButtonPress)
        self.canvas.mpl_connect('button_release_event',self.onMouseButtonRelease)
        self.canvas.mpl_connect('motion_notify_event',self.onMouseMotion)
        self.canvas.mpl_connect('pick_event', self.onPick)
        self.picked=False
        
        self.zoom_history_index=1
        self.prev_back=False
        self.artist_picked=None
        self.extremums=[]
        self.arrowprops = dict( color='white', arrowstyle = "->", connectionstyle = "angle, angleA = 0, angleB = 90,rad = 10") 
        self.annotations_max=[]
        self.annotations_min=[]
        self.ctrl=False
        self.canvas.mpl_connect("draw_event",self.onCanvasDrawn)
        
        self.zoom_multiplier=1#settings
        self.annot_offset_x=20#settings
        self.annot_offset_y=10#settings
        self.keep_annotations=False#settings
        self.max_pt2show=3##settings
        self.annot_opacity=0.8#settings
        self.x_Offset=50
        self.y_Offset=20
        
    def onCanvasDrawn(self,e):
        self.px2pt=self.axes.transData.inverted()
        self.lim_offset_x=self.px2pt.transform((self.x_Offset,0))[0]-self.px2pt.transform((0,0))[0]
        self.lim_offset_y=self.px2pt.transform((0,self.y_Offset))[1]-self.px2pt.transform((0,0))[1]
        
    def onMouseMotion(self,e):
        self.fft_widget_.onMouseMotion(e)
    
    def onPick(self,e):
        self.picked=True
        self.artist_picked=e.artist
            
    def onKeyPressed(self,e):
        if e.key=="control":
            self.ctrl=True
        
    def onKeyReleased(self,e):
        if e.key=="control":
            self.ctrl=False
            self.picked=False
    
    def onMouseButtonPress(self,e):
        if self.keep_annotations==False:
                self.remove_annotations()
        if e.button==MouseButton.LEFT:
            self.leftclick=True
            self.rightclick=False
        elif e.button==MouseButton.RIGHT:
            self.rightclick=True
            self.leftclick=False
        
        if self.ctrl==True and self.leftclick==True and self.picked==True:####IF ctrl+lftclick on plot zoom in
            xtick=self.axes.get_xticks()
            ytick=self.axes.get_yticks()
            freq_per_div=(xtick[1]-xtick[0])/self.zoom_multiplier
            
            y_per_div=(ytick[1]-ytick[0])/self.zoom_multiplier
            self.show_plot(e.xdata,e.ydata,freq_per_div,y_per_div)
            self.fft_widget_.ZoomsetDrawRect(e.xdata,e.ydata,freq_per_div,y_per_div)
            if self.prev_back:
                chist_indx=len(self.zoom_history_list)-self.zoom_history_index+1
                print("popST",chist_indx,"ZHI:",self.zoom_history_index)
                for i in range(chist_indx,len(self.zoom_history_list)):
                    self.zoom_history_list.pop(chist_indx)
                    
                print("AFT_del:",self.zoom_history_list)
            self.zoom_history_index=1
            self.zoom_history_list.append([e.xdata,e.ydata,freq_per_div,y_per_div])
            self.prev_back=False
            self.picked=False
        
        elif self.ctrl==True and self.rightclick==True:####IF ctrl+rightclick on plot zoomback history
            self.zoom_history_index+=1
            print("INDX",self.zoom_history_index)
            hist_indx=len(self.zoom_history_list)-self.zoom_history_index
            if hist_indx>=0:
                e.xdata,e.ydata,freq_per_div,y_per_div=self.zoom_history_list[hist_indx]
                print("showing:",self.zoom_history_list[hist_indx])
                self.show_plot(e.xdata,e.ydata,freq_per_div,y_per_div)
                self.fft_widget_.ZoomsetDrawRect(e.xdata,e.ydata,freq_per_div,y_per_div)###zoom area rectangle updated 
                self.prev_back=True
            else:
                self.zoom_history_index-=1
                self.prev_back=True
        
        elif self.leftclick==True and self.picked==True:
            if self.keep_annotations==False:
                self.remove_annotations()
            self.annotate_maximas(e.xdata,e.ydata)
            
    def onMouseButtonRelease(self,e):
        if e.button=="MouseButton.LEFT":
            self.leftclick=False
        elif e.button=="MouseButton.RIGHT":
            self.rightclick=False
        self.picked=False
        
    def resizeEvent(self,e):
        QtWidgets.QWidget.resizeEvent(self, e)
        
    def showEvent(self, event):
        self.shown=True
        print("SHOWN_____zoom")
        QtWidgets.QWidget.showEvent(self, event)
    
    def closeEvent(self,e):
        self.shown=False
        self.fft_widget_.bounding_Box.hide()
        QtWidgets.QWidget.closeEvent(self, e)
    
    def show_plot(self,xdata,ydata,x_range,y_range):
        self.axes.set_xlim(xdata -x_range/2, xdata + x_range/2)
        self.axes.set_ylim(ydata - y_range/2, ydata + y_range/2)
        for i in range(len(self.fft_widget_.ch_fft_enabled_list)):
            self.plot_list[i][0].set_visible(self.fft_widget_.ch_fft_enabled_list[i])
        self.canvas.draw_idle()
        self.show()
    
    def addplot_(self,x_,y_,ch_color,xlimit):
        plot_ = self.axes.plot(x_,y_,color=ch_color,picker=5)
        self.plot_list.append(plot_)
        
    def plot_refresh(self):
        draw_thrd=threading.Thread(target=self.canvas.draw_idle()).start()
        
    def rem_plot_0(self):
        self.plot_list[0][0].remove()
        self.plot_list=[]
        
    def edit_plot(self,plot_num,x_,y_,ch_color,x_limit):
        self.plot_list[plot_num][0].remove()
        plot_=self.axes.plot(x_,y_, color=ch_color,picker=5)
        self.plot_list[plot_num]=plot_
    
    def change_color(self,lineno,col,):
        self.axes.get_lines()[lineno].set_color(col)
    
    def annotate_maximas(self,xdata,ydata):
        xtick=self.axes.get_xticks()
        ytick=self.axes.get_yticks()
        freq_per_div=(xtick[1]-xtick[0])
        y_per_div=(ytick[1]-ytick[0])
        if self.keep_annotations==False:
            self.remove_annotations()
        dat_x,dat_y=self.get_maximas(self.artist_picked,[(xdata-freq_per_div/4),(xdata+freq_per_div/4)],[(ydata-y_per_div/4),(ydata+y_per_div/4)])
        dat_x,dat_y=self.get_max_sorted(self.max_pt2show,dat_x,dat_y)
        xlim=self.axes.get_xlim()
        ylim=self.axes.get_ylim()
        xlim=[xlim[0]+self.lim_offset_x ,xlim[1]-self.lim_offset_x]
        ylim=[ylim[0]+self.lim_offset_y,ylim[1]-self.lim_offset_y]
        for i in range(len(dat_x)):
            self.check_loc_and_annotate(dat_x[i],dat_y[i],xlim,ylim,i)
        self.canvas.draw_idle()
    
    def get_maximas(self,line,xlim,ylim):
        indices=[]
        ydata_=np.array([])
        xdata_=np.array([])
        dat_high=[]
        dat_high_x=[]
        dat_low=[]
        dat_low_x=[]
        xdata=line.get_xdata()
        ydata=line.get_ydata()
        
        xStart=np.searchsorted(xdata,xlim[0])## get start and stop index of limited data
        xStop=np.searchsorted(xdata,xlim[1])##
        xdat_=xdata[xStart:xStop]
        ydat_=ydata[xStart:xStop]
        if len(xdat_)<5:
            if xStop!=len(xdata)-3:###if stop index in data set is like [...,*, dat ,dat,]  len(xdata)-1 is the last data in the set
                xStop=xStop+2
            if xStart>=2:
                xStart=xStart-2
            xdat_=xdata[xStart:xStop]
            ydat_=ydata[xStart:xStop]
        
        maximas=argrelextrema(ydat_, np.greater)
        #print("ydat",ydat_)
        for i in range(len(maximas[0])):
            y__=ydat_[maximas[0][i]]
            
            if y__>=ylim[0] and y__<=ylim[1]:
                dat_high.append(y__)
                dat_high_x.append(xdat_[maximas[0][i]])
                
        dat_high=np.array(dat_high)
        dat_high_x=np.array(dat_high_x)
        return dat_high_x,dat_high

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
                                        bbox = dict(boxstyle="round4,pad=0.3", fc="w",alpha=0.8, ))
        self.annotations_max.append(ann)
        
    def get_max_sorted(self,count_,xdats,ydats):
        max_list_x=[]
        max_list_y=[]
        
        if len(ydats)>3:
            for i in range(count_):
                ymax1=np.amax(ydats)
                ymax1_indx=np.where(ydats==ymax1)
                max_list_y.append(ymax1)
                max_list_x.append(xdats[ymax1_indx][0])
                ydats=np.delete(ydats,ymax1_indx)
                xdats=np.delete(xdats,ymax1_indx)
        else:
            max_list_y=ydats
            max_list_x=xdats
        return max_list_x,max_list_y
'''
app = QtWidgets.QApplication(sys.argv)

ui = fft_zoom_(None)
ui.show()
sys.exit(app.exec_())
'''
    ###TO DO ANNOTATION
    ##TO DO SHOW BOX on the Area Zoomed
    #if Zoom is clicked annotate max or mins

            
    
