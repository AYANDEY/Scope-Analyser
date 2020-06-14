import numpy as np
from matplotlib.animation import ArtistAnimation
import matplotlib.pyplot as plt
from PyQt5.Qt import QGraphicsColorizeEffect, QGraphicsSimpleTextItem, QPoint, QRect, QRubberBand,QSize
from PyQt5 import QtGui
from rubberbands import *
import threading
import about

class exmain(object):
    def __init__(self,parent):
        super(exmain,self).__init__()
        self.main=parent
        self.MousePress_Event_handler=self.main.canvas.mpl_connect('button_press_event', self.onMousePress)
        
        self.picked_=False
        self.anim_run=False
        self.define_Cursors_rb()
        self.t_offset=[10,20]
        self.v_offset=[20,10]
        self.move_cursor_index=-1
        self.cursor_Enabled=False####################################Cursor initialy off
        self.main.Cursor_enable_sw.toggled.connect(self.cursor_show_all)
        self.main.Cursor_type_combo.currentIndexChanged.connect(self.cursor_show_all)
        self.main.ch_move_rad.toggled.connect(self.ch_move_enable_change)
        self.cursor_y_offset=0
        self.v_multiplier=1
        self.cursorboxsize=15
        self.get_config()
        self.aboutwin=about.messege(self)
    
    ################################################CURSORS#####################################
    def draw_cursor_tS(self,t_pos,visible):
        x_pos=t_pos
        y_pos=self.ylim_px[0]-10
        y_pt=self.CH-self.ylim_px[0]
        self.Cursor_t_boxS.setGeometry(QRect(x_pos-5,y_pt,11,20))
        self.Cursor_tS.setGeometry(QRect(QPoint(x_pos,self.CH-self.ylim_px[1]),QPoint(x_pos,y_pt)))
        if visible:
            self.Cursor_t_boxS.show()
            self.Cursor_tS.show()
        else:
            self.Cursor_t_boxS.hide()
            self.Cursor_tS.hide()
        self.tS_pos=[x_pos,y_pos]
        self.tS_dat=self.main.px2pt.transform((t_pos,0))[0]
        
    def draw_cursor_tE(self,t_pos,visible):
        x_pos=t_pos
        y_pos=self.ylim_px[0]-10
        y_pt=self.CH-self.ylim_px[0]
        self.Cursor_t_boxE.setGeometry(QRect(x_pos-5,y_pt,11,20))
        self.Cursor_tE.setGeometry(QRect(QPoint(x_pos,self.CH-self.ylim_px[1]),QPoint(x_pos,y_pt)))
        if visible:
            self.Cursor_tE.show()
            self.Cursor_t_boxE.show()
        else:
            self.Cursor_tE.hide()
            self.Cursor_t_boxE.hide()
        self.tE_pos=[x_pos,y_pos]
        self.tE_dat=self.main.px2pt.transform((t_pos,0))[0]
        
        self.main.printf_("TE_pos=",self.tE_pos)
        
    def draw_cursor_vS(self,v_pos,visible):
        x_pos=self.xlim_px[0]
        y_pos=self.CH-v_pos
        y_pt=y_pos-6
        self.Cursor_v_boxS.setGeometry(QRect(x_pos-20,y_pt,20,11))
        self.Cursor_vS.setGeometry(QRect(QPoint(x_pos,y_pos),QPoint(self.xlim_px[1],y_pos)))
        if visible:
            self.Cursor_v_boxS.show()
            self.Cursor_vS.show()
        else:
            self.Cursor_vS.hide()
            self.Cursor_v_boxS.hide()
        self.vS_pos=[x_pos,v_pos]
        self.vS_dat=self.main.px2pt.transform((0,v_pos))[1]
        self.main.printf_("VS_pos=",self.vS_dat)
        
    def draw_cursor_vE(self,v_pos,visible):
        x_pos=self.xlim_px[0]
        y_pos=self.CH-v_pos
        y_pt=y_pos-6
        self.Cursor_v_boxE.setGeometry(QRect(x_pos-20,y_pt,20,11))
        self.Cursor_vE.setGeometry(QRect(QPoint(x_pos,y_pos),QPoint(self.xlim_px[1],y_pos)))
        if visible:
            self.Cursor_v_boxE.show()
            self.Cursor_vE.show()
        else:
            self.Cursor_v_boxE.hide()
            self.Cursor_vE.hide()
        
        self.vE_pos=[x_pos,v_pos]
        self.vE_dat=self.main.px2pt.transform((0,v_pos))[1]
        self.main.printf_("VE_pos=",self.vE_pos)
    
    def hide_cursors(self):
        self.Cursor_t_boxS.hide()
        self.Cursor_tS.hide()
        self.Cursor_tE.hide()
        self.Cursor_t_boxE.hide()
        self.Cursor_vS.hide()
        self.Cursor_v_boxS.hide()
        self.Cursor_vE.hide()
        self.Cursor_v_boxE.hide()
        self.CursorTrackBox_S.hide()
        self.CursorTrackBox_E.hide()
    
    ##########################################EVENT HANDLES##############################################
    
    def on_pick(self,event):
        if self.picked_==False:
            self.main.printf_("ON_pick")
            self.line = event.artist
            ch_indx=-1
            for members in self.main.ch_name_col_list:
                ch_indx+=1
                if members[0]==self.line.get_label():
                    self.main.printf_("Picked:",members[0])
                    break
            self.ch_indx=ch_indx
            if ch_indx !=-1:
                self.x_scaled=self.main.x_scale[ch_indx]
                self.y_scaled=self.main.y_scale[ch_indx]
                self.line_in_list=self.main.mplsmall.line_list[ch_indx]
                #self.MouseRelease_Event_handler=self.main.canvas.mpl_connect('button_release_event',self.onMouseRelease)
                self.picked_=True
                self.marked=0
    
    def onMousePress(self,e):
        if self.main.Cursor_enable_sw.isChecked():
            self.check_cursor_clicked(e.x,e.y)
        if self.picked_:
            if self.main.rescalex_Extended_flag:
                    val=self.main.MplWidget.scrollArea.horizontalScrollBar().value()
                    half_page_step=self.main.MplWidget.scrollArea.horizontalScrollBar().pageStep()/2
                    self.main.set_scrl_val= int(val+half_page_step)
                    
            if self.marked<2:
                if self.marked==0:
                    try:
                        self.p=self.draw_pt_blit(e.xdata,e.ydata,self.main.axes_list[self.ch_indx])
                    except Exception:
                        pass
                    self.clicked_startx=e.xdata
                    self.clicked_starty=e.ydata
                if self.marked==1:
                    clicked_endx=e.xdata
                    clicked_endy=e.ydata
                self.marked+=1
            if self.marked==2:
                self.p.remove()
                changex=clicked_endx-self.clicked_startx
                changey=clicked_endy-self.clicked_starty
                x_scale=np.add(self.x_scaled,changex)
                y_scale=np.add(self.y_scaled,changey)
                #self.redraw_plot_blit(x_scale,y_scale,self.main.axes_list[self.ch_indx],self.line)
                if self.main.shift_t.isChecked():
                    self.line.set_xdata(x_scale)
                    self.line_in_list.set_xdata(x_scale)
                    self.main.x_scale[self.ch_indx]=x_scale
                if self.main.shift_v.isChecked():
                    self.line.set_ydata(y_scale)
                    self.line_in_list.set_ydata(y_scale)
                    self.main.y_scale[self.ch_indx]=y_scale
                    
                    if self.main.ch_volt_div_list[self.ch_indx][4]==1:
                        prev_change=self.main.ch_volt_div_list[self.ch_indx][5]
                        self.main.ch_volt_div_list[self.ch_indx][5]=prev_change+changey
                        self.cursor_y_offset=self.main.ch_volt_div_list[self.ch_indx][5]/self.v_multiplier
                    else:
                        self.main.ch_volt_div_list[self.ch_indx][4]=1
                        self.main.ch_volt_div_list[self.ch_indx][5]=changey
                        self.cursor_y_offset=self.main.ch_volt_div_list[self.ch_indx][5]/self.v_multiplier
                
                self.marked=0
                self.picked_=False
                self.main.canvas.draw_idle()
                self.main.mplsmall.refresh_plot()
    
    def onMouseMotion(self,e):
        if self.cursor_picked>0:
            if self.move_cursor_index==2:
                    self.cursor_direct_drop(e.x,e.y)
            elif self.Cursor_Type_Indx==2:
                if self.cursor_picked==1:
                    self.cursor_track(e.x,"S")
                    self.set_cursor_values(2,1)
                if self.cursor_picked==2:
                    self.cursor_track(e.x,"E")
                    self.set_cursor_values(2,2)
            elif self.cursor_picked==1:
                self.draw_cursor_tS(e.x,True)
                self.set_cursor_values(0,0)
            elif self.cursor_picked==2:
                self.draw_cursor_tE(e.x,True)
                self.set_cursor_values(0,1)
            elif self.cursor_picked==3:
                self.draw_cursor_vS(e.y,True)
                self.set_cursor_values(1,0)
            elif self.cursor_picked==4:
                self.draw_cursor_vE(e.y,True)
                self.set_cursor_values(1,1)
    
    def onMouseRelease(self,e):
        if self.cursor_picked>0:
            self.cursor_picked=-1
            try:
                self.main.canvas.mpl_disconnect(self.MouseRelease_Event_handler)
            except Exception:
                pass
            try:
                self.main.canvas.mpl_disconnect(self.MouseMotion_Event_handler)
            except Exception:
                pass
    
    ##############################################Shifting Plots############################################
    
    def ch_move_enable_change(self):
        if self.main.ch_move_rad.isChecked()==True:
            self.pick_con=self.main.canvas.mpl_connect('pick_event', self.on_pick)
        elif self.main.ch_move_rad.isChecked()==False:
            try:
                self.main.canvas.mpl_disconnect(self.pick_con)
            except Exception:
                pass
            if self.picked_==True:
                try:
                    self.picked_=False
                    self.p.remove()
                    self.main.refresh_plot()
                except Exception:
                    pass
        
    def CH_move_combo_change(self):
        self.main.printf_("run")
        zorders=[]
        for ax in self.main.axes_list:
            zorders.append(ax.get_zorder())
            self.main.printf_(ax.get_zorder())
        z_max=max(zorders)
        self.main.printf_("z_max",z_max)
        ind=self.main.CH_move_combo.currentIndex()
        self.main.axes_list[ind].set_zorder(z_max+1)
        self.main.canvas.draw_idle()

    def draw_pt_blit(self,xdata,ydata,axes):
        #background = self.main.canvas.copy_from_bbox(axes.bbox)
        artist_name,=axes.plot(xdata,ydata, 'bo')
        axes.draw_artist(artist_name)
        self.main.figure.canvas.blit(axes.bbox)
        
        #self.main.figure.canvas.restore_region(background)
        return artist_name
    
    '''
    def redraw_plot_blit(self,x_scale,y_scale,axes,artist):
        self.main.printf_("Trying blit")
        artist.set_animated(True)
        artist.set_visible(False)
        
        #self.main.canvas.draw_idle()
        background = self.main.canvas.copy_from_bbox(self.main.figure.bbox)
        artist.set_visible(True)
        self.main.canvas.restore_region(background)
        artist.set_xdata(x_scale)
        artist.set_ydata(y_scale)
        axes.draw_artist(artist)
        
        self.main.canvas.blit(self.main.figure.bbox)
    '''
    ######################################CURSOR ESSENCIALS########################################
    
    def cursor_show_all(self):
        self.hide_cursors()
        if self.main.Cursor_enable_sw.isChecked():
            self.Cursor_Type_Indx=self.main.Cursor_type_combo.currentIndex()  ###0 for time 1 for volt and 2 vor Track
            if self.Cursor_Type_Indx==0:
                bool_=True
                bool_1=True
                bool_2=False
                type_=0
                
            elif self.Cursor_Type_Indx==1:
                
                bool_=True
                bool_1=False
                bool_2=True
                type_=1
            elif self.Cursor_Type_Indx==2:
                bool_=True
                bool_1=True
                bool_2=True
                type_=2
                self.CursorTrackBox_S.show()
                self.CursorTrackBox_E.show()
            self.initial_draw_cursors(type_)
            self.move_cursor_index=-1
            self.main.Cursor_S_rad.setChecked(False)
            self.main.Cursor_S_rad.setChecked(False)
            self.main.Cursor_S_rad.toggled.connect(self.cursor_drop_init)
            self.main.Cursor_E_rad.toggled.connect(self.cursor_drop_init)
        else:
            bool_=False
            bool_1=False
            bool_2=False
            type_=-1
        ########### ON for all cursor setting type######### 
        self.main.Cursor_of.setVisible(bool_)
        self.main.CH_cursor_combo.setVisible(bool_)
        self.main.Cursor_type_combo.setVisible(bool_)
        self.main.Cursor_type_txt.setVisible(bool_)
        self.main.Cursor_S_rad.setVisible(bool_)
        self.main.Cursor_E_rad.setVisible(bool_)
        ########### ON for cursor setting type TIME and TRACK######### 
        self.main.t_S.setVisible(bool_1)
        self.main.t_E.setVisible(bool_1)
        self.main.dt_label.setVisible(bool_1)
        self.main.dt_.setVisible(bool_1)
        self.main.dt_inv_label.setVisible(bool_1)
        self.main.dt_inv_.setVisible(bool_1)
        ########### ON for cursor setting type VOLT and TRACK######### 
        self.main.v_S.setVisible(bool_2)
        self.main.v_E.setVisible(bool_2)
        self.main.dv_label.setVisible(bool_2)
        self.main.dv_.setVisible(bool_2)

        
        self.cursor_Enabled=bool_
        if type_!=-1:
            self.set_cursor_values(type_,5)
    
    def define_Cursors_rb(self):
        self.Cursor_vS=cursorTrackLine("white",QRubberBand.Line, self.main.canvas)
        self.Cursor_vE=cursorTrackLine("white",QRubberBand.Line, self.main.canvas)
        self.Cursor_tS=cursorTrackLine("white",QRubberBand.Line, self.main.canvas)
        self.Cursor_tE=cursorTrackLine("white",QRubberBand.Line, self.main.canvas)
        self.Cursor_v_boxS=cursorBox("S","white","black",QRubberBand.Rectangle, self.main.canvas)
        self.Cursor_v_boxE=cursorBox("E","white","black",QRubberBand.Rectangle, self.main.canvas)
        
        self.Cursor_t_boxS=cursorBox("S","white","black",QRubberBand.Rectangle,self.main.canvas)
        self.Cursor_t_boxE=cursorBox("E","white","black",QRubberBand.Rectangle, self.main.canvas)
        self.CursorTrackBox_S=cursorTrackBox("white",QRubberBand.Rectangle, self.main.canvas)
        self.CursorTrackBox_E=cursorTrackBox("white",QRubberBand.Rectangle, self.main.canvas)
        
        self.cursor_picked=-1
        
        #self.hide_cursors()
    
    def refresh_bounds(self):
        plotXlim=self.main.plot_axes.get_xlim()
        self.CH=self.main.canvas.size().height()
        self.xlim_px=[self.main.pt2px.transform((plotXlim[0],0))[0],self.main.pt2px.transform((plotXlim[1],0))[0]]
        plotYlim=self.main.plot_axes.get_ylim()
        self.ylim_px=[self.main.pt2px.transform((0,plotYlim[0]))[1],self.main.pt2px.transform((0,plotYlim[1]))[1]]
    
    def check_cursor_clicked(self,x,y):
        
        if self.move_cursor_index>-1:
            self.cursor_direct_drop(x,y)
        self.cursor_picked=-1
        Cursor_Type_Indx=self.Cursor_Type_Indx
        if Cursor_Type_Indx==0 or Cursor_Type_Indx==2:
            if abs(x-self.tS_pos[0])<self.t_offset[0] and  abs(y-self.tS_pos[1])<self.t_offset[1]:
                self.cursor_picked=1
                self.main.printf_("TS picked")
            elif abs(x-self.tE_pos[0])<self.t_offset[0] and abs(y-self.tE_pos[1])<self.t_offset[1]:
                self.cursor_picked=2
                self.main.printf_("TE picked")
        elif Cursor_Type_Indx==1 or Cursor_Type_Indx==2:
            if abs(x-self.vS_pos[0])<self.v_offset[0] and abs(y-self.vS_pos[1])<self.v_offset[1]:
                self.cursor_picked=3
                self.main.printf_("VS picked")
            elif abs(x-self.vE_pos[0])<self.v_offset[0] and abs(y-self.vE_pos[1])<self.v_offset[1]:
                self.cursor_picked=4
                self.main.printf_("VE picked")
        if self.cursor_picked>0:
            self.MouseMotion_Event_handler=self.main.canvas.mpl_connect('motion_notify_event', self.onMouseMotion)
            self.MouseRelease_Event_handler=self.main.canvas.mpl_connect('button_release_event', self.onMouseRelease)
    
    def set_cursor_values(self,type_,selection):
        if type_==0:
            tS_=self.tS_dat
            tE_=self.tE_dat
            dt_=abs(tS_-tE_)
            if dt_!=0:
                dt_inv = 1/dt_
            else:
                dt_inv= np.inf
            if selection==0:
                self.main.t_S.setText(self.get_t_in_unit(tS_))
            elif selection==1:
                self.main.t_E.setText(self.get_t_in_unit(tE_))
            elif selection==5:###############set_both S and E
                self.main.t_S.setText(self.get_t_in_unit(tS_))
                self.main.t_E.setText(self.get_t_in_unit(tE_))
            
            self.main.dt_.setText(self.get_t_in_unit(dt_))
            self.main.dt_inv_.setText(self.get_dt_in_unit(dt_inv))
            
        elif type_==1:##############CURSOR SET TO Volt
            vS_=(self.vS_dat-self.cursor_y_offset)*self.v_multiplier
            vE_=(self.vE_dat-self.cursor_y_offset)*self.v_multiplier
            dv_=abs(vS_-vE_)
            
            if selection==0:
                self.main.v_S.setText(self.get_v_in_unit(vS_))
            elif selection==1:
                self.main.v_E.setText(self.get_v_in_unit(vE_))
            elif selection==5:###############set_both S and E
                self.main.v_S.setText(self.get_v_in_unit(vS_))
                self.main.v_E.setText(self.get_v_in_unit(vE_))
            
            self.main.dv_.setText(self.get_v_in_unit(dv_))
            
        elif type_==2:##############CURSOR SET TO Track
            
            vS_=(self.vS_dat-self.cursor_y_offset)*self.v_multiplier
            vE_=(self.vE_dat-self.cursor_y_offset)*self.v_multiplier
            dv_=abs(vS_-vE_)
            
            tS_=self.tS_dat
            tE_=self.tE_dat
            dt_=abs(tS_-tE_)
            if dt_!=0:
                dt_inv = 1/dt_
            else:
                dt_inv=np.inf
            if selection==5:
                self.main.v_S.setText(self.get_v_in_unit(vS_))
                self.main.v_E.setText(self.get_v_in_unit(vE_))
                self.main.t_S.setText(self.get_t_in_unit(tS_))
                self.main.t_E.setText(self.get_t_in_unit(tE_))
                
            elif selection==1:
                self.main.v_S.setText(self.get_v_in_unit(vS_))
                self.main.t_S.setText(self.get_t_in_unit(tS_))
                
            elif selection==2:
                self.main.v_E.setText(self.get_v_in_unit(vE_))
                self.main.t_E.setText(self.get_t_in_unit(tE_))
            
            self.main.dv_.setText(self.get_v_in_unit(dv_))
            self.main.dt_.setText(self.get_t_in_unit(dt_))
            self.main.dt_inv_.setText(self.get_dt_in_unit(dt_inv))
    
    def get_t_in_unit(self,t):
        t=t*1e9
        if abs(t)>1000:
            t=t/1000 ##in micros
            if abs(t)>1000:
                t=t/1000 #in millis
                if abs(t)>1000:
                    t=t/1000 # in sec
                    t=format(t, '.4f')
                    return (str(t)+" s")
                else:
                    t=format(t, '.4f')
                    return (str(t)+" ms") #in millis
            else:
                
                t=format(t, '.4f')
                return (str(t)+" us") #in micros      
        else:
            
            t=format(t, '.4f')
            return (str(t)+" ns")#in nanos
    
    def get_dt_in_unit(self,t):
        if t>1000:
            t=t/1000 #in KHz
            t=format(t, '.4f')
            return (str(t)+" KHz")#in nanos
        else:
            t=format(t, '.4f')
            return (str(t)+" Hz")
    
    def get_v_in_unit(self,v):

        if abs(v)>1000:
            v=v/1000
            v=format(v, '.5f')
            return (str(v)+" V") #in volts
        else:
            v=format(v, '.5f')
            return (str(v)+" mV")
    
    def initial_draw_cursors(self,type_):
        
        if self.main.rescalex_Extended_flag==1:
            canvas_page_start=self.main.MplWidget.scrollArea.horizontalScrollBar().value()
            scroll_page_step=self.main.MplWidget.scrollArea.horizontalScrollBar().pageStep()
            mid_point=canvas_page_start+scroll_page_step/2
            mid_point1=(mid_point+canvas_page_start)/2  ############ mid_point1 Leftmid pt
            mid_point2=(canvas_page_start+scroll_page_step+mid_point)/2  ############ mid_point2 rightmid pt
        else:
            mid_point1=self.main.MplWidget.canvas.size().width()/4
            mid_point2=self.main.MplWidget.canvas.size().width()*3/4 
        if type_==0:
            self.draw_cursor_tS(mid_point2,True)
            self.draw_cursor_tE(mid_point1,True)
        elif type_==1:
            CH=self.main.canvas.size().height()
            ymid_point1=CH/4
            ymid_point2=CH*3/4
            
            self.draw_cursor_vS(ymid_point2,True)
            self.draw_cursor_vE(ymid_point1,True)
        elif type_==2:
            self.cursor_track(mid_point2,"S")
            self.cursor_track(mid_point1,"E")
            
    def cursor_direct_drop(self,x,y):
        move_cursor=self.move_cursor_index
        Cursor_Type_Indx=self.Cursor_Type_Indx
        if Cursor_Type_Indx==0:
            if move_cursor==0:
                self.draw_cursor_tS(x,True)
                self.set_cursor_values(0,0)
            elif move_cursor==1:
                self.draw_cursor_tE(x,True)
                self.set_cursor_values(0,1)
            elif move_cursor==2:
                dt_pos=self.tS_pos[0]-self.tE_pos[0]##differennce in time position
                self.draw_cursor_tS(x,True)
                
                if dt_pos!=0:
                    self.draw_cursor_tE(x-dt_pos,True)
                else:
                    self.draw_cursor_tE(x-20,True)
                
                self.set_cursor_values(0,5)
        elif Cursor_Type_Indx==1:############################direct drop Volt Cursor
            if move_cursor==0:
                self.draw_cursor_vS(y,True)
                self.set_cursor_values(1,0)
                
            if move_cursor==1:
                self.draw_cursor_vE(y,True)
                self.set_cursor_values(1,1)
                
            if move_cursor==2:
                dv_pos=self.vS_pos[1]-self.vE_pos[1]
                self.draw_cursor_vS(y,True)
                if dv_pos!=0:
                    self.draw_cursor_vE(y-dv_pos,True)
                else:
                    self.draw_cursor_vE(y-20,True)
                self.set_cursor_values(1,5)
        
        elif Cursor_Type_Indx==2:
            if move_cursor==0:
                self.cursor_track(x,"S")
                self.set_cursor_values(2,1)
            if move_cursor==1:
                self.cursor_track(x,"E")
                self.set_cursor_values(2,2)
            if move_cursor==2:
                self.cursor_track(x,"both")
                self.set_cursor_values(2,5)
    
    def cursor_drop_init(self):
        S=self.main.Cursor_S_rad.isChecked()
        E=self.main.Cursor_E_rad.isChecked()
        if S and E:
            self.move_cursor_index=2
        elif S:
            self.move_cursor_index=0
        elif E:
            self.move_cursor_index=1
        else:
            self.move_cursor_index=-1
    
    def cursor_refresh_on_redraw(self):
        if self.main.Cursor_enable_sw.isChecked():
            Cursor_Type_Indx=self.main.Cursor_type_combo.currentIndex()
            if Cursor_Type_Indx==0:
                self.draw_cursor_tS(self.tS_pos[0],True)
                self.draw_cursor_tE(self.tE_pos[0],True)
                self.set_cursor_values(0,5)
            elif Cursor_Type_Indx==1:
                self.draw_cursor_vS(self.vS_pos[1],True)
                self.draw_cursor_vE(self.vE_pos[1],True)
                self.set_cursor_values(1,5)
            elif Cursor_Type_Indx==2:
                self.cursor_track(self.tS_pos[0],"S")
                self.cursor_track(self.tE_pos[0],"E")
                self.set_cursor_values(2,5)
    
    def CH_cursor_combo_change(self):
        self.main.printf_("CH_cursor_combo_change")
        curr_plot_indx=self.main.CH_cursor_combo.currentIndex()
        col=QtGui.QColor(self.main.ch_name_col_list[curr_plot_indx][1])
        col.setAlpha(160)
        stylesheet="background-color:"+col.name(1)
        self.main.CH_cursor_combo.setStyleSheet(stylesheet)##ERROR:QBasicTimer::start: QBasicTimer can only be used with threads started with QThread
        vdiv=self.main.ch_volt_div_list[curr_plot_indx][1]
        v_unit_indx=self.main.ch_volt_div_list[curr_plot_indx][2]
        self.curr_plot_indx=curr_plot_indx
        ######the cursor reading must be leveled i.e for a given position the val of cursor must be scalled to v/div
        # if v/div increases yscale is scalled to a lower value but cursor being fixed in its position must show a higher value
        if v_unit_indx==1:
            self.v_multiplier=vdiv/self.main.ydiv
        if v_unit_indx==2:
            self.v_multiplier=vdiv/(self.main.ydiv/1000)
        
        if self.main.ch_volt_div_list[curr_plot_indx][4]==1:
            self.cursor_y_offset=self.main.ch_volt_div_list[self.ch_indx][5]//self.v_multiplier #offset saved per unit and multiplied while calculating cursor value
        elif self.main.ch_volt_div_list[curr_plot_indx][4]==0:
            self.cursor_y_offset=0
        
        self.cursor_refresh_on_redraw() ###############refresh cursor values if different cursor selected
    
    def cursor_track(self,x,SorE):
        cbSize=self.cursorboxsize
        current_plot=self.curr_plot_indx
        array_x=self.main.x_scale[current_plot]
        x_=self.main.px2pt.transform((x,0))[0]
        indx = np.searchsorted(array_x, x_)
        if indx==len(array_x):
            indx=indx-1
        dat_x=array_x[indx]
        dat_y=self.main.y_scale[current_plot][indx]
        pos_=self.main.pt2px.transform((dat_x,dat_y))
        
        if SorE == "both":
            dt_pos=self.tS_pos[0]-self.tE_pos[0]
            self.draw_cursor_tS(pos_[0],True)
            self.draw_cursor_vS(pos_[1],True)
            self.CursorTrackBox_S.setGeometry(QRect(QPoint(pos_[0]-cbSize/2,self.CH-pos_[1]-cbSize/2),QSize(cbSize,cbSize)))
            dt_x=self.main.px2pt.transform((x-dt_pos,0))[0]
            indx_dt = np.searchsorted(array_x, dt_x)
            dat_xdt=array_x[indx_dt]
            dat_ydt=self.main.y_scale[current_plot][indx_dt]
            pos_=self.main.pt2px.transform((dat_xdt,dat_ydt))
            self.draw_cursor_tE(pos_[0],True)
            self.draw_cursor_vE(pos_[1],True)
            self.CursorTrackBox_E.setGeometry(QRect(QPoint(pos_[0]-cbSize/2,self.CH-pos_[1]-cbSize/2),QSize(cbSize,cbSize)))
        elif SorE =="S":
            self.draw_cursor_tS(pos_[0],True)
            self.draw_cursor_vS(pos_[1],True)
            self.CursorTrackBox_S.setGeometry(QRect(QPoint(pos_[0]-cbSize/2,self.CH-pos_[1]-cbSize/2),QSize(cbSize,cbSize)))
            
        elif SorE =="E":
            self.draw_cursor_tE(pos_[0],True)
            self.draw_cursor_vE(pos_[1],True)
            self.CursorTrackBox_E.setGeometry(QRect(QPoint(pos_[0]-cbSize/2,self.CH-pos_[1]-cbSize/2),QSize(cbSize,cbSize)))
    
    ###############################################DYNAMIC RUBBERBAND###########################
    def def_zeroline(self,indx,col):
        ch_zeroline=Zeroline(col,QRubberBand.Line, self.main.canvas)
        ch_zlineBox=Zeroline_Box(str(indx),col,QRubberBand.Line, self.main.canvas)
        return ch_zeroline,ch_zlineBox
    
    def draw_zeroline(self,ch_indx,visible):
        zeroline,zeroline_Box=self.main.zeroline_list[ch_indx]
        v_pos=self.main.pt2px.transform((0,self.main.ch_volt_div_list[ch_indx][5]))[1]
        x_pos=self.xlim_px[0]
        y_pos=self.CH-v_pos
        y_pt=y_pos-6
        zeroline.setGeometry(QRect(QPoint(x_pos,y_pos),QPoint(self.xlim_px[1],y_pos)))
        zeroline_Box.setGeometry(QRect(x_pos-20,y_pt,20,11))
        
        if visible:
            zeroline.show()
            zeroline_Box.show()
        else:
            zeroline.hide()
            zeroline_Box.hide()
    
    def hide_zeroline(self,ch_indx):
        self.main.zeroline_list[ch_indx][0].hide()
        self.main.zeroline_list[ch_indx][1].hide()
    
    def get_config(self):
        if self.main.conf.zeroline_visible!=[None,False]:
            self.zeroline_default_enabled=self.main.conf.zeroline_visible
        else:
            self.zeroline_default_enabled=True

    ############################################################################################
    
    def show_about(self):
        self.aboutwin.activateWindow()
        self.aboutwin.show()
        self.main.printf_("show_about")
        
