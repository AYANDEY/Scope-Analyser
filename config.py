import threading
import numpy as np
import sys

class config(object):
    def __init__(self,parent):
        super(config,self).__init__()
        self.main=parent
        self.pos=[]
        self.configs_init()
        self.pos_init()
        try:
            self.config_file=open("self.config",'r+')
            self.lines=self.config_file.readlines()
            self.parse_lines(self.lines)
            self.config_file.close()
        except Exception:
            pass
        try:
            self.config_pos_file=open("self.pos",'r+')
            self.lines_pos=self.config_pos_file.readlines()
            self.parse_lines_for_pos_and_datfolder(self.lines_pos)
            self.config_pos_file.close()
        except Exception:
            self.main.printf_(sys.exc_info())
            self.main.printf_("LINE NO:",format(sys.exc_info()[-1].tb_lineno))
            self.mainwin_pos.extend([0,"main_window_position="])
            self.infwin_pos.extend([1,"info_window_position="])
            self.mWin_pos.extend([2,"measure_window_position="])
            self.csv_dir.extend([None,3,"last_csv_directory="])
    
    def parse_lines_for_pos_and_datfolder(self,lines):
        if len(lines)==0:
            lines.append("just to run all parse_positionS Once")
        for i in range(len(lines)):
            if self.mainwin_pos[2]==False:
                self.mainwin_pos=self.parse_position("main_window_position=",lines[i],i)
            if self.infwin_pos[2]==False:
                self.infwin_pos=self.parse_position("info_window_position=",lines[i],i)
            if self.mWin_pos[2]==False:
                self.mWin_pos=self.parse_position("measure_window_position=",lines[i],i)
            if self.csv_dir[1]==False:
                self.csv_dir=self.parse_path("last_csv_directory=",lines[i],i)
        
        if self.csv_dir[1]==False:
            self.csv_dir[0]="D:\\csv_data"
    
    def parse_lines(self,lines):
        wave_volt_limit=[None,None,False]
        FFT_annotation_offset=[None,None,False]
        
        wave_plot_opacity=[None,False]
        set_time_to_base_time=[None,False]
        set_to_volt_base=[None,False]
        FFT_line_opacity=[None,False]
        FFT_zoom_multiplier=[None,False]
        FFT_keep_annotations=[None,False]
        FFT_Max_points_to_show=[None,False]
        FFT_annotation_opacity=[None,False]
        Information_Window_Opacity=[None,False]
        Measurement_Window_Opacity=[None,False]
        zeroline_visible=[None,False]
        FFT_default_window=[None,False]
        Main_Window_always_on_top=[None,False]
        Information_Window_always_on_top=[None,False]
        Measurement_Window_always_on_top=[None,False]
        FFT_window_default_symmetric=[None,False]
        debug_=[None,False]
        
        for i in range(len(lines)):
            if lines[i].startswith('#')==False:
                if wave_volt_limit[2]==False:
                    wave_volt_limit=self.parse_position("wave_volt_limit=",lines[i],i)
                if FFT_annotation_offset[2]==False:
                    FFT_annotation_offset=self.parse_position("FFT_annotation_offset=",lines[i],i)
                if wave_plot_opacity[1]==False:
                    wave_plot_opacity=self.parse_val("wave_plot_opacity=",lines[i],i) 
                if set_time_to_base_time[1]==False:
                    set_time_to_base_time=self.parse_val("set_time_to_base_time=",lines[i],i)
                if set_to_volt_base[1]==False:
                    set_to_volt_base=self.parse_val("set_to_volt_base=",lines[i],i) 
                if FFT_line_opacity[1]==False:
                    FFT_line_opacity=self.parse_val("FFT_line_opacity=",lines[i],i)
                    
                if FFT_zoom_multiplier[1]==False:
                    FFT_zoom_multiplier=self.parse_val("FFT_zoom_multiplier=",lines[i],i)
                    
                if FFT_keep_annotations[1]==False:
                    FFT_keep_annotations=self.parse_val("FFT_keep_annotations=",lines[i],i)
                    
                if FFT_Max_points_to_show[1]==False:
                    FFT_Max_points_to_show=self.parse_val("FFT_Max_points_to_show=",lines[i],i)
                    
                if FFT_annotation_opacity[1]==False:
                    FFT_annotation_opacity=self.parse_val("FFT_annotation_opacity=",lines[i],i)
                    
                if FFT_window_default_symmetric[1]==False:
                    FFT_window_default_symmetric=self.parse_val("FFT_window_default_symmetric=",lines[i],i)
                    
                if Information_Window_Opacity[1]==False:
                    Information_Window_Opacity=self.parse_val("Information_Window_Opacity=",lines[i],i)
                
                if Measurement_Window_Opacity[1]==False:
                    Measurement_Window_Opacity=self.parse_val("Measurement_Window_Opacity=",lines[i],i)
                    
                if zeroline_visible[1]==False:
                    zeroline_visible=self.parse_val("zeroline_visible=",lines[i],i)

                if FFT_default_window[1]==False:
                    FFT_default_window=self.parse_val("FFT_default_window=",lines[i],i)
                    
                if Main_Window_always_on_top[1]==False:
                    Main_Window_always_on_top=self.parse_val("Main_Window_always_on_top=",lines[i],i)
                    
                if Information_Window_always_on_top[1]==False:
                    Information_Window_always_on_top=self.parse_val("Information_Window_always_on_top=",lines[i],i)
                
                if Measurement_Window_always_on_top[1]==False:
                    Measurement_Window_always_on_top=self.parse_val("Measurement_Window_always_on_top=",lines[i],i)
                
                if debug_[1]==False:
                    debug_=self.parse_val("debug=",lines[i],i)
                
                
        if wave_volt_limit[2]:
            self.main.printf_("wave_volt_limit",wave_volt_limit)
            self.wave_volt_limit=[wave_volt_limit[0],wave_volt_limit[1]]
        else:
            self.wave_volt_limit=None
        
        if FFT_annotation_offset[2]:
            self.main.printf_("FFT_annotation_offset",FFT_annotation_offset)
            self.FFT_annotation_offset=[FFT_annotation_offset[0],FFT_annotation_offset[1]]
        else:
            self.FFT_annotation_offset=None
        
        if wave_plot_opacity[1]:
           self.main.printf_("wave_plot_opacity",wave_plot_opacity)
           self.wave_plot_opacity=float(wave_plot_opacity[0])
        else:
            self.wave_plot_opacity=None
            
        if set_time_to_base_time[1]:
            self.main.printf_("set_time_to_base_time",set_time_to_base_time)
            self.set_time_to_base_time=set_time_to_base_time[0]
        else:
            self.set_time_to_base_time=None
        
        if set_to_volt_base[1]:
            self.main.printf_("set_to_volt_base",set_to_volt_base)
            self.set_to_volt_base=self.str2bool(set_to_volt_base[0])
        else:
            self.set_to_volt_base=None
        
        if FFT_line_opacity[1]:
            self.main.printf_("FFT_line_opacity",FFT_line_opacity)
            self.FFT_line_opacity=float(FFT_line_opacity[0])
        else:
            self.FFT_line_opacity=None
            
        if FFT_zoom_multiplier[1]:
            self.main.printf_("FFT_zoom_multiplier",FFT_zoom_multiplier)
            self.FFT_zoom_multiplier=float(FFT_zoom_multiplier[0])
        else:
            self.FFT_zoom_multiplier=None
            
        if FFT_keep_annotations[1]:
            self.FFT_keep_annotations=self.str2bool(FFT_keep_annotations[0])
            self.main.printf_("FFT_keep_annotations",self.FFT_keep_annotations)
        else:
            self.FFT_keep_annotations=None
        
        if FFT_window_default_symmetric[1]:
            self.FFT_window_default_symmetric=self.str2bool(FFT_window_default_symmetric[0])
            self.main.printf_("FFT_keep_annotations",self.FFT_keep_annotations)
        else:
            self.FFT_window_default_symmetric=None
        
        if FFT_Max_points_to_show[1]:
            self.main.printf_("FFT_Max_points_to_show",FFT_Max_points_to_show)
            self.FFT_Max_points_to_show=int(FFT_Max_points_to_show[0])
        else:
            self.FFT_Max_points_to_show=None
            
        if FFT_annotation_opacity[1]:
            self.main.printf_("FFT_annotation_opacity",FFT_annotation_opacity)
            self.FFT_annotation_opacity=float(FFT_annotation_opacity[0])
        else:
            self.FFT_annotation_opacity=None
        
        if Information_Window_Opacity[1]:
            self.main.printf_("Information_Window_Opacity",Information_Window_Opacity)
            self.Information_Window_Opacity=float(Information_Window_Opacity[0])
        else:
            self.Information_Window_Opacity=None
        
        if Measurement_Window_Opacity[1]:
            self.main.printf_("Measurement_Window_Opacity",Measurement_Window_Opacity)
            self.Measurement_Window_Opacity=float(Measurement_Window_Opacity[0])
        else:
            self.Measurement_Window_Opacity=None
        
        if zeroline_visible[1]:
            self.main.printf_("zeroline_visible",zeroline_visible)
            self.zeroline_visible=self.str2bool(zeroline_visible[0])
        else:
            self.zeroline_visible=None
        
            
        if FFT_default_window[1]:
            self.main.printf_("FFT_default_window",FFT_default_window)
            self.FFT_default_window=FFT_default_window[0]
        else:
            self.FFT_default_window=None
        
        if Main_Window_always_on_top[1]:
            self.Main_Window_always_on_top=self.str2bool(Main_Window_always_on_top[0])
        else:
            self.Main_Window_always_on_top=None
            
        if Information_Window_always_on_top[1]:
            self.main.printf_("Information_Window_always_on_top",Information_Window_always_on_top)
            self.Information_Window_always_on_top=self.str2bool(Information_Window_always_on_top[0])
        else:
            self.Information_Window_always_on_top=None    
        
        if Measurement_Window_always_on_top[1]:
            self.Measurement_Window_always_on_top=self.str2bool(Measurement_Window_always_on_top[0])
        else:
            self.Measurement_Window_always_on_top=None

        if debug_[1]:
            self.debug_=self.str2bool(debug_[0])
            
        else:
            self.debug_=None
            
    def parse_val(self,argument_str,line,count):
        a_val=None
        found=False
        ret=[a_val,found]
        if argument_str in line:
            st_index=line.index(argument_str)+len(argument_str)
            stp_index=len(line)
            try:
                stp_index=line.index('\n')
            except Exception:
                stp_index=len(line)
            
            a_val=line[st_index:stp_index]
            found=True
            ret=[a_val,found]
        return ret
    
    def parse_position(self,argument_str,line,count):
        found=False
        ret=[None,None,found]
        if argument_str in line:
            st_index=line.index(argument_str)+len(argument_str)+1
            stp1=line.index(',')
            stp2=line.index(')')
            posx=line[st_index:stp1]
            posy=line[stp1+1:stp2]
            found=True
            try:
                ret=[int(posx),int(posy),found]
            except Exception:
                ret=[None,None,False]
        ret.extend([count,argument_str])
        return ret
    
    def parse_path(self,argument_str,line,count):
        found=False
        ret=[None,found,None]
        if argument_str in line:
            st_index=line.index(argument_str)+len(argument_str)
            try:
                stp_indx=line.index('\n')
            except Exception:
                stp_indx=len(line)
            path=line[st_index:stp_indx]
            found=True
            ret=[path,found,None]
        ret.extend([count,argument_str])
        return ret
    
    def get_position(self):
        try:
            infwin_pos=[self.infwin_pos[0],self.infwin_pos[1]]
            mWin_pos=[self.mWin_pos[0],self.mWin_pos[1]]
            mainwin_pos=[self.mainwin_pos[0],self.mainwin_pos[1]]
            if infwin_pos!=[None,None]:
                if self.main.screensize[0]>infwin_pos[0] and self.main.screensize[1]>infwin_pos[1]:
                    self.main.infoWin.set_pos(infwin_pos)
            else:
                self.main.printf_("halving info")
                self.main.printf_(self.main.screensize[0]/2)
                self.main.infoWin.set_pos(np.divide(np.array(self.main.screensize,dtype=int),2))
            
            if mWin_pos!=[None,None]:
                if self.main.screensize[0]>mWin_pos[0] and self.main.screensize[1]>mWin_pos[1]:
                    self.main.mWin.set_pos(mWin_pos)
            else:
                self.main.printf_("halving mwin")
                self.main.mWin.set_pos(np.divide(np.array(self.main.screensize,dtype=int),2))
            
            if mainwin_pos!=[None,None]:  
                if self.main.screensize[0]>mainwin_pos[0] and self.main.screensize[1]>mainwin_pos[1]:
                    self.main.move(mainwin_pos[0],mainwin_pos[1])
            else:
                self.main.printf_("halving main")
                self.main.move(int(self.main.screensize[0]/2),int(self.main.screensize[1]/2))
                
        except Exception:
            self.main.printf_(sys.exc_info())
            self.main.printf_("LINE NO:",format(sys.exc_info()[-1].tb_lineno))
            self.main.infoWin.set_pos([int(self.main.screensize[0]/2),int(self.main.screensize[1]/2)])
            self.main.mWin.set_pos([int(self.main.screensize[0]/2),int(self.main.screensize[1]/2)])
            self.main.move(int(self.main.screensize[0]/2),int(self.main.screensize[1]/2))
    
    def save_position(self):
        infwin_pos=self.main.infoWin.get_pos()
        mWin_pos=self.main.mWin.get_pos()
        
        self.csv_dir[0]=self.main.last_folder
        self.main.printf_("self.csv_dir",self.csv_dir,self.main.last_folder)
        self.mainwin_pos[0]=self.main.pos().x()
        self.mainwin_pos[1]=self.main.pos().y()
        if infwin_pos!=(0,0):
            self.infwin_pos[0]=infwin_pos[0]
            self.infwin_pos[1]=infwin_pos[1]
        if mWin_pos!=(0,0):
            self.mWin_pos[0]=mWin_pos[0]
            self.mWin_pos[1]=mWin_pos[1]
        self.main.printf_("SAVE:","self.mainwin_pos",self.mainwin_pos,"self.infwin_pos",self.infwin_pos,"self.csv_dir",self.csv_dir)
        self.pos.extend([self.mainwin_pos,self.infwin_pos,self.mWin_pos,self.csv_dir])
        self.write_config()

    def write_config(self):
        try:
            sorted_lines=sorted(self.pos, key = lambda x: x[3])
        except Exception:
            sorted_lines=self.pos

        lines_to_write=[]
        for i in range(len(sorted_lines)):
            
            if sorted_lines[i][2]!=None:###if not None then it must be position
                lines_to_write.append(str(sorted_lines[i][4])+"("+str(sorted_lines[i][0])+","+str(sorted_lines[i][1])+")")
            else:
                lines_to_write.append(str(sorted_lines[i][4])+str(sorted_lines[i][0]))
        
        threading.Thread(target=self.file_writer,args=([lines_to_write])).start()
    
    def file_writer(self,lines):
        config_pos_file=open("self.pos",'w+')
        for i in range(len(lines)):
            config_pos_file.write(lines[i]+'\n')
        config_pos_file.close()
        
    def configs_init(self):
        self.wave_volt_limit=[None,None,False]
        self.FFT_annotation_offset=[None,None,False]
        self.wave_plot_opacity=[None,False]
        self.set_time_to_base_time=[None,False]
        self.set_to_volt_base=[None,False]
        self.FFT_line_opacity=[None,False]
        self.FFT_zoom_multiplier=[None,False]
        self.FFT_keep_annotations=[None,False]
        self.FFT_Max_points_to_show=[None,False]
        self.FFT_annotation_opacity=[None,False]
        self.FFT_window_default_symmetric=[None,False]

        self.Information_Window_Opacity=[None,False]
        self.Measurement_Window_Opacity=[None,False]
        self.zeroline_visible=[None,False]
        self.FFT_default_window=[None,False]
        self.Main_Window_always_on_top=[None,False]
        self.Information_Window_always_on_top=[None,False]
        self.Measurement_Window_always_on_top=[None,False]
        self.debug_=[None,False]
        
    def pos_init(self):
        self.mainwin_pos=[None,None,False]
        self.infwin_pos=[None,None,False]
        self.mWin_pos=[None,None,False]
        self.csv_dir=[None,False]
    
    def load_config(self):
        self.config_file=open("self.config",'r+')
        self.configs_init()
        self.lines=self.config_file.readlines()
        self.parse_lines(self.lines)
        self.main.get_config(True)
        self.main.fftW.get_config()
        self.main.fftW.get_plot_opacity(True)
        self.main.infoWin.get_config()
        self.main.mWin.get_config()
        self.main.exmain.get_config()
        
    def str2bool(self,string):
        bool_=False
        if string=="True" or string=="true" or string=='t' or string=="1":
            bool_=True
        elif string=="False" or string=="false" or string=='f' or string=="0":
            bool_=False
        return bool_
    