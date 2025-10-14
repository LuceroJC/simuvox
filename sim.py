import config        as cfg
import tkinter       as tk
import tkinter.filedialog  as fdlg
#import os.path    
import synthesis     as syn
import numpy         as np
import spec001       as spg
import sound_output
import sounddevice   as sd
#import save_results  as svr
import spectral_par  as sp

import matplotlib.gridspec as gridspec
import gui_lam       as glam
import tkinter.ttk   as ttk
import webbrowser
from   ctypes        import windll
from  sys            import platform
#from   time          import time
from   matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from   matplotlib.figure import Figure
from   matplotlib.pyplot import setp, rcParams, style #rcParamsDefault    


class MainWindow(tk.Frame):

    def __init__(self, root, *args, **kwargs):

        style.use("seaborn-v0_8")

        self.root = root
        
        rcParams['figure.dpi'] = 100
        rcParams['axes.titlesize'] = 12
        rcParams['font.size'] = 12
        rcParams['font.family'] = 'arial'
        
        self.sound_ready = "No"
        self.w = cfg.Param.VT_FILE
        self.runwindow = False
        
        tk.Frame.__init__(self, *args, **kwargs)

#        root = tk.Tk()
        root.title("SimuVox")
        
        
#        self.menubar = tk.Menu(self)
#
#        menu = tk.Menu(self.menubar, tearoff=0)
#        self.menubar.add_command(label="About")
#        
#        root.config(menu=self.menubar)
#        
#       Frame 1: Input/output

        frame1 = ttk.LabelFrame(root, text="Vocal tract: ")
        frame1.grid(row=0, columnspan=7, sticky='NWE', padx=5, pady=5, ipadx=5, ipady=5)

#        lab_vt_file = tk.Label (frame1, text = "Vowel:")
#        lab_vt_file.grid(column=0, row=1, sticky='E', padx=5, pady=2)        

        self.var_f = tk.StringVar() 
        self.var_f.set(cfg.Param.VT_FILE)

#        name_vt_file = tk.Label(frame1, textvariable = self.var_f, anchor = 'w')
#        name_vt_file.grid(column=1, row=1, padx=2, pady=2)  



#        self.enter_vt_file = tk.Entry(frame1)
#        self.enter_vt_file.grid (column=1, row=1, columnspan=7, sticky="WE", pady=3)
#        self.enter_vt_file.insert(0,cfg.Param.VT_FILE)

#        but_vt = tk.Button(frame1, text="Browse", width = 10)
#        but_vt.grid(row=1, column=8, sticky='W', padx=5, pady=2)
#        but_vt.config (command = self._get_file) 
        
#        but_vt = tk.Button(frame1, text="Plot Area", width = 10)
#        but_vt.grid(row=1, column=2, sticky='E', padx=5, pady=2)
#        but_vt.config (command = self._plot_vt) 

#        lab_vt_file2 = tk.Label (frame1, text = "Select vowel:", width=12, anchor='e')
#        lab_vt_file2.grid(column=9, row=1, sticky='E', padx=5, pady=2)        


        but_vt = tk.Button(frame1, text="Articulatory model", width = 20)
        but_vt.grid(row=1, column=10, sticky='E', padx=5, pady=2)
        but_vt.config (command = self._run_lam) 

#        lab_loss = ttk.Label (frame1, text = "Losses:")
#        lab_loss.grid(column=0, row=2, sticky='E', padx=5, pady=2) 
#
        self.enter_visc = tk.BooleanVar()
        self.enter_visc.set(cfg.Param.VISC_LOSS)    
#        chk_visc = tk.Checkbutton(frame1, text="Viscous/thermal", variable=self.enter_visc, onvalue=True, offvalue=False)
#        chk_visc.grid(column=3, row=2, sticky='W', padx=0, pady=2)
#       
        self.enter_wall = tk.BooleanVar()
        self.enter_wall.set(cfg.Param.WALL_VIBR)    
#        chk_wall = tk.Checkbutton(frame1, text="Wall vibr", variable=self.enter_wall, onvalue=True, offvalue=False)
#        chk_wall.grid(column=8, row=2, sticky='W', padx=0, pady=2)
        
        
#       Frame 2: Simulation

        frame2 = ttk.LabelFrame(root, text="Simulation: ")
        frame2.grid(row=0, rowspan=2, column= 8, columnspan=7, sticky='NWE', padx=5, pady=5, ipadx=5, ipady=5)
        
        lab_time = tk.Label (frame2, text = "Total time (s):")
        lab_time.grid(column=0, row=7, sticky='E', padx=5, pady=2)        
        self.enter_time = tk.Entry(frame2)
        self.enter_time.grid (column=1, row=7, sticky="WE", pady=3)
        self.enter_time.insert(0,str(cfg.Param.TIME_TOTAL))
        
        lab_ontime = tk.Label (frame2, text = "Onset time (s):")
        lab_ontime.grid(column=0, row=8, sticky='E', padx=5, pady=2)        
        self.enter_ontime = tk.Entry(frame2)
        self.enter_ontime.grid (column=1, row=8, sticky="WE", pady=3)
        self.enter_ontime.insert(0,str(cfg.Param.TIME_ONSET))
        
        lab_offtime = tk.Label (frame2, text = "Offset time (s):")
        lab_offtime.grid(column=0, row=9, sticky='E', padx=5, pady=2)        
        self.enter_offtime = tk.Entry(frame2)
        self.enter_offtime.grid (column=1, row=9, sticky="WE", pady=3)
        self.enter_offtime.insert(0,str(cfg.Param.TIME_OFFSET))

        self.enter_prosody = tk.BooleanVar()
        self.enter_prosody.set(cfg.Param.PROSODY)         
        chk_prosody = tk.Checkbutton(frame2, text="Pitch decr", variable=self.enter_prosody, onvalue=True, offvalue=False, anchor='w')
        chk_prosody.grid(column=0, columnspan=2, row=10, sticky='W', padx=5, pady=2)
 

#       Frame 3: Glottal parameters

        frame3 = ttk.LabelFrame(root, text="Source: ")
        frame3.grid(row=1, columnspan=7, rowspan=2, sticky='NWE', padx=5, pady=5, ipadx=5, ipady=5)

        self.gender = tk.StringVar()
        self.gender.set(cfg.Param.GENDER)

        lab_gender = tk.Label(frame3, text = "Gender:")
        lab_gender.grid(column=0, row=12, sticky='E', padx=5, pady=2) 
        
        bmale = tk.Radiobutton(frame3, text="Male", padx = 5, variable=self.gender, value="Male")
        bmale.grid(column=1, row=12, sticky='W', padx=5, pady=0)
        bmale.config(command = self._update_male)        
        
        bfemale = tk.Radiobutton(frame3, text="Female", padx = 5, variable=self.gender, value="Female")
        bfemale.grid(column=2, row=12, sticky='W', padx=5, pady=0)
        bfemale.config(command = self._update_female)
 
        lab_pl = tk.Label (frame3, text = "Lung press (Pa):")
        lab_pl.grid(column=0, row=15, sticky='E', padx=5, pady=2)        
        self.enter_pl = tk.Entry(frame3)
        self.enter_pl.grid (column=1, columnspan= 2, row=15, sticky="WE", pady=3)
        self.enter_pl.insert(0,str(cfg.Param.PL/10.))
               
        lab_mass = tk.Label (frame3, text = "Mass (g):")
        lab_mass.grid(column=0, row=16, sticky='E', padx=5, pady=2)        
        self.enter_mass = tk.Entry(frame3)
        self.enter_mass.grid (column=1,  columnspan= 2, row=16, sticky="WE", pady=3)
        self.enter_mass.insert(0,str(cfg.Param.MASS))
        
        lab_damping = tk.Label (frame3, text = "Damp (N s/m):")
        lab_damping.grid(column=0, row=17, sticky='E', padx=5, pady=2)        
        self.enter_damping = tk.Entry(frame3)
        self.enter_damping.grid (column=1,  columnspan= 2, row=17, sticky="WE", pady=3)
        self.enter_damping.insert(0,str(cfg.Param.DAMPING/1000.))
 
#        lab_vf_eta = tk.Label (frame3, text = "Nonlinearity (1/cm^2)")
#        lab_vf_eta.grid(column=0, row=17, sticky='E', padx=5, pady=2)        
#        self.enter_vf_eta = tk.Entry(frame3)
#        self.enter_vf_eta.grid (column=1, row=17, sticky="WE", pady=3)
#        self.enter_vf_eta.insert(0,str(cfg.Param.ETA))

        
        lab_stiffness = tk.Label (frame3, text = "Stiff (N/m):")
        lab_stiffness.grid(column=0, row=18, sticky='E', padx=5, pady=2)        
        self.enter_stiffness = tk.Entry(frame3)
        self.enter_stiffness.grid (column=1,  columnspan= 2, row=18, sticky="WE", pady=3)
        self.enter_stiffness.insert(0,str(cfg.Param.STIFFNESS/1000.))

        lab_tau = tk.Label (frame3, text = "Delay (ms):")
        lab_tau.grid(column=0, row=19, sticky='E', padx=5, pady=2)        
        self.enter_tau = tk.Entry(frame3)
        self.enter_tau.grid (column=1,  columnspan= 2, row=19, sticky="WE", pady=3)
        self.enter_tau.insert(0,str(cfg.Param.TAU*1000.))

        lab_abduction = tk.Label (frame3, text = "Abduction (cm):")
        lab_abduction.grid(column=0, row=20, sticky='E', padx=5, pady=2)        
        self.enter_abduction = tk.Entry(frame3)
        self.enter_abduction.grid (column=1,  columnspan= 2, row=20, sticky="WE", pady=3)
        self.enter_abduction.insert(0,str(cfg.Param.ABDUCTION))

        lab_length = tk.Label (frame3, text = "Glot length (cm):")
        lab_length.grid(column=0, row=21, sticky='E', padx=5, pady=2)        
        self.enter_length = tk.Entry(frame3)
        self.enter_length.grid (column=1,  columnspan= 2, row=21, sticky="WE", pady=3)
        self.enter_length.insert(0,str(cfg.Param.GLOTTAL_LENGTH))

        lab_depth = tk.Label (frame3, text = "Glot depth (cm):")
        lab_depth.grid(column=0, row=22, sticky='E', padx=5, pady=2)        
        self.enter_depth = tk.Entry(frame3)
        self.enter_depth.grid (column=1,  columnspan= 2, row=22, sticky="WE", pady=3)
        self.enter_depth.insert(0,str(cfg.Param.GLOTTAL_DEPTH))


#       Frame 4: Disorders

        frame4 = ttk.LabelFrame(root, text="Disorders: ")
        frame4.grid(row=2, column = 8, columnspan=4, sticky='NEWS', padx=5, pady=5, ipadx=5, ipady=5)

        lab_q = tk.Label (frame4, text = "Asymmetry:")
        lab_q.grid(column=0, row=0, sticky='E', padx=5, pady=2)  
        self.enter_q = tk.StringVar()
        self.enter_q.set(str(cfg.Param.Q))
        slider_q = ttk.Scale(frame4, from_=-1, to_=1, orient=tk.HORIZONTAL, length=200, 
                                  command=lambda s:self.enter_q.set('%0.2f' % 10.**float(s)))
        slider_q.grid(column=1, row=0, sticky='E', padx=5, pady=2)
        lab2_q = ttk.Label(frame4, textvariable=self.enter_q, width = 5)
        lab2_q.grid(column=2, row=0, padx=5, pady=2)
        
#        lab_q = tk.Label (frame4, text = "Asymmetry:")
#        lab_q.grid(column=0, row=0, sticky='E', padx=5, pady=2)        
#        self.enter_q = tk.Entry(frame4)
#        self.enter_q.grid (column=1, row=0, sticky="WE", pady=3)
#        self.enter_q.insert(0,str(cfg.Param.Q))
#        
        
        lab_wow = tk.Label (frame4, text = "Wow:")
        lab_wow.grid(column=0, row=1, sticky='E', padx=5, pady=2)  
        self.enter_wow = tk.StringVar()
        self.enter_wow.set(str(cfg.Param.WOW_SIZE))
        slider_wow = ttk.Scale(frame4, from_=0, to_=10, orient=tk.HORIZONTAL, length=200, 
                                  value=self.enter_wow.get(), 
                                  command=lambda s:self.enter_wow.set('%0.1f' % float(s)))
        slider_wow.grid(column=1, row=1, sticky='E', padx=5, pady=2)        
        lab2_wow = ttk.Label(frame4, textvariable=self.enter_wow, width = 5)
        lab2_wow.grid(column=2, row=1, padx=5, pady=2)
        
#        lab_wow = tk.Label (frame4, text = "Wow:")
#        lab_wow.grid(column=0, row=1, sticky='E', padx=5, pady=2)        
#        self.enter_wow = tk.Entry(frame4)
#        self.enter_wow.grid (column=1, row=1, sticky="WE", pady=3)
#        self.enter_wow.insert(0,str(cfg.Param.WOW_SIZE))

        lab_tremor = tk.Label (frame4, text = "Tremor:")
        lab_tremor.grid(column=0, row=2, sticky='E', padx=5, pady=2)  
        self.enter_tremor = tk.StringVar()
        self.enter_tremor.set(str(cfg.Param.TREMOR_SIZE))
        slider_tremor = ttk.Scale(frame4, from_=0, to_=10, orient=tk.HORIZONTAL, length=200, 
                                  value=self.enter_tremor.get(), 
                                  command=lambda s:self.enter_tremor.set('%0.1f' % float(s)))
        slider_tremor.grid(column=1, row=2, sticky='E', padx=5, pady=2)        
        lab2_tremor = ttk.Label(frame4, textvariable=self.enter_tremor, width = 5)
        lab2_tremor.grid(column=2, row=2, padx=5, pady=2)

#        lab_tremor = tk.Label (frame4, text = "Tremor:")
#        lab_tremor.grid(column=0, row=2, sticky='E', padx=5, pady=2)        
#        self.enter_tremor = tk.Entry(frame4)
#        self.enter_tremor.grid (column=1, row=2, sticky="WE", pady=3)
#        self.enter_tremor.insert(0,str(cfg.Param.TREMOR_SIZE))

        lab_jitter = tk.Label (frame4, text = "Jitter:")
        lab_jitter.grid(column=0, row=3, sticky='E', padx=5, pady=2)  
        self.enter_jitter = tk.StringVar()
        self.enter_jitter.set(str(cfg.Param.FLUTTER_SIZE))
        slider_jitter = ttk.Scale(frame4, from_=0, to_=10, orient=tk.HORIZONTAL, length=200, 
                                  value=self.enter_jitter.get(), 
                                  command=lambda s:self.enter_jitter.set('%0.1f' % float(s)))
        slider_jitter.grid(column=1, row=3, sticky='E', padx=5, pady=2)        
        lab2_jitter = ttk.Label(frame4, textvariable=self.enter_jitter, width = 5)
        lab2_jitter.grid(column=2, row=3, padx=5, pady=2)

#        lab_jitter = tk.Label (frame4, text = "Jitter:")
#        lab_jitter.grid(column=0, row=3, sticky='E', padx=5, pady=2)        
#        self.enter_jitter = tk.Entry(frame4)
#        self.enter_jitter.grid (column=1, row=3, sticky="WE", pady=3)
#        self.enter_jitter.insert(0,str(cfg.Param.FLUTTER_SIZE))

#        lab_noise = tk.Label (frame4, text = "Pulsatile noise:")
#        lab_noise.grid(column=0, row=4, sticky='E', padx=5, pady=2)        
#        self.enter_pulse = tk.Entry(frame4)
#        self.enter_pulse.grid (column=1, row=4, sticky="WE", pady=3)
#        self.enter_pulse.insert(0,str(cfg.Param.PULSATILE))

        lab_aspire= tk.Label (frame4, text = "Asp noise:")
        lab_aspire.grid(column=0, row=4, sticky='E', padx=5, pady=2)  
        self.enter_aspire = tk.StringVar()
        self.enter_aspire.set(str(cfg.Param.ASPIRATION))
        slider_aspire = ttk.Scale(frame4, from_=0, to_=10, orient=tk.HORIZONTAL, length=200, 
                                  value=self.enter_aspire.get(), 
                                  command=lambda s:self.enter_aspire.set('%0.1f' % float(s)))
        slider_aspire.grid(column=1, row=4, sticky='E', padx=5, pady=2)        
        lab2_aspire = ttk.Label(frame4, textvariable=self.enter_aspire, width = 5)
        lab2_aspire.grid(column=2, row=4, padx=5, pady=2)
        
#        lab_noise = tk.Label (frame4, text = "Aspiration noise:")
#        lab_noise.grid(column=0, row=5, sticky='E', padx=5, pady=2)        
#        self.enter_aspire = tk.Entry(frame4)
#        self.enter_aspire.grid (column=1, row=5, sticky="WE", pady=3)
#        self.enter_aspire.insert(0,str(cfg.Param.ASPIRATION))
 
#        lab_fenda= tk.Label (frame4, text = "Glot chink:")
#        lab_fenda.grid(column=0, row=5, sticky='E', padx=5, pady=2)  
#        self.enter_fenda = tk.StringVar()
#        self.enter_fenda.set(str(cfg.Param.FENDA))
#        slider_fenda = ttk.Scale(frame4, from_=0, to_=1, orient=tk.HORIZONTAL, length=200, 
#                                  value=self.enter_fenda.get(), 
#                                  command=lambda s:self.enter_fenda.set('%0.1f' % float(s)))
#        slider_fenda.grid(column=1, row=5, sticky='E', padx=5, pady=2)        
#        lab2_fenda = ttk.Label(frame4, textvariable=self.enter_fenda, width = 5)
#        lab2_fenda.grid(column=2, row=5, padx=5, pady=2)
        
#        lab_noise = tk.Label (frame4, text = "Chink (cm^2):")
#        lab_noise.grid(column=0, row=6, sticky='E', padx=5, pady=2)        
#        self.enter_fenda = tk.Entry(frame4)
#        self.enter_fenda.grid (column=1, row=6, sticky="WE", pady=3)
#        self.enter_fenda.insert(0,str(cfg.Param.FENDA))
 
#        self.enter_aphonia = tk.BooleanVar()
#        self.enter_aphonia.set(cfg.Param.APHONIA)         
#        chk_aphonia = tk.Checkbutton(frame4, text="Aphonia", variable=self.enter_aphonia, onvalue=True, offvalue=False)
#        chk_aphonia.grid(column=1, row=7, sticky='W', padx=0, pady=2)
 
  
       #       Frame 5: Etc

#        frame5 = ttk.LabelFrame(root, text="Info: ")
#        frame5.grid(row=2, column = 8, columnspan=4, rowspan=1, sticky='NSEW', padx=5, pady=5, ipadx=5, ipady=5)
#
##        msg = tk.Message(frame5, text="All units in cm-g-s\n\n", width=200, anchor='e')        
##        msg.grid(column=9, columnspan=2, row=1, sticky='WES', padx=5, pady=2)        
#
#        msg = tk.Message(frame5, text="Version July 2017\nJorge C. Lucero", width = 180, anchor='e')        
#        msg.grid(column=9, columnspan=2, row=2, sticky='W', padx=5, pady=2)        
#
#        link = tk.Label(frame5, text="http://lucero.mat.unb.br/", fg="blue", cursor="hand2")
#        link.grid(column=9, columnspan=2, row=3, sticky='NW', padx=10, pady=2)   
#        link.bind("<Button-1>", self.callback)

        frame6 = ttk.Frame(root)
        frame6.grid(row=3, column = 0, columnspan=1, sticky='W', padx=5, pady=5)
        
        self.msg_1 = tk.Label(frame6, text="Ready", anchor='w')        
        self.msg_1.grid(column=0, row=3, sticky='WES', padx=5, pady=5)  

        frame7 = ttk.Frame(root)
        frame7.grid(row=3, column = 8, columnspan=4, sticky='E', padx=5, pady=5)
        
        but0 = tk.Button (frame7,text = "Run", width = 10)
        but0.grid (column = 10, row = 3, sticky='ES', padx=5, pady=10)
        but0.config (command = self._run)  

        but1 = tk.Button (frame7,text = "Exit", width = 10)
        but1.grid (column = 11, row = 3, sticky='ES', padx=5, pady=10)
        but1.config (command = root.destroy)

        but1 = tk.Button (frame7,text = "About", width = 10)
        but1.grid (column = 12, row = 3, sticky='ES', padx=5, pady=10)
        but1.config (command = self.about)

#        root.mainloop ()

    def about(self):
        
        t = tk.Toplevel(self.root)         
        t.title("About")
        
#       Frame 0: Plots
        
        frame0 = tk.Frame(t)
        frame0.grid(row=0, column=0, padx=50, pady=50)
        
        msg = tk.Message(frame0, text="SimuVox", font="Helvetica 16 bold", fg='red', width = 500)        
        msg.grid(column=0, row=0)        

        msg = tk.Message(frame0, text="A factory of voices", font="Helvetica 10 italic", width = 500)        
        msg.grid(column=0, row=1)        

        link = tk.Label(frame0, text="simuvox.wordpress.com", fg="blue", cursor="hand2")
        link.grid(column=0, row=4)   
        link.bind("<Button-1>", self.callback)
        
        msg = tk.Message(frame0, text="\n\nVersion 0.1.0", font="Helvetica 10", width = 500)        
        msg.grid(column=0, row=6, padx=5, pady=5)        

      
        msg = tk.Message(frame0, text=u"Copyright \u00A9 2017 by Jorge C. Lucero", font="Helvetica 8", width = 500)        
        msg.grid(column=0, row=11, padx=5, pady=5)        



    def _acquire_data(self):

#        cfg.Param.COMMENT   = self.enter_comment.get()
        cfg.Param.VT_FILE = self.var_f.get()

#        cfg.Param.GRAPHICS = self.enter_graphics.get()
#        cfg.Param.SAVE_SOUND = self.enter_sound.get()
#        cfg.Param.SAVE_PARAM = self.enter_param.get()        
#        cfg.Param.SAVE_SIGNAL = self.enter_signal.get()
         
        cfg.Param.TIME_TOTAL = float(self.enter_time.get())
        cfg.Param.TIME_ONSET = float(self.enter_ontime.get())
        cfg.Param.TIME_OFFSET = float(self.enter_offtime.get())
        cfg.Param.PROSODY =  self.enter_prosody.get()
        cfg.Param.VISC_LOSS =  self.enter_visc.get()
        cfg.Param.WALL_VIBR =  self.enter_wall.get()

        cfg.Param.GENDER = self.gender.get()

        if cfg.Param.GENDER == "Male":
            cfg.Param.GENDER_SCALE = 1.
        else:
            cfg.Param.GENDER_SCALE = .8
            
        cfg.Param.MASS = float(self.enter_mass.get())
        cfg.Param.DAMPING = 1000.*float(self.enter_damping.get())
#        cfg.Param.ETA = float(self.enter_vf_eta.get())
        cfg.Param.STIFFNESS = 1000.*float(self.enter_stiffness.get())
        cfg.Param.PL = 10.*float(self.enter_pl.get())
        cfg.Param.TAU = .001*float(self.enter_tau.get())
        cfg.Param.ABDUCTION = float(self.enter_abduction.get())
        cfg.Param.GLOTTAL_LENGTH = float(self.enter_length.get())
        cfg.Param.GLOTTAL_DEPTH = float(self.enter_depth.get())
        cfg.Param.Q = float(self.enter_q.get())
        cfg.Param.WOW_SIZE = float(self.enter_wow.get())
        cfg.Param.TREMOR_SIZE = float(self.enter_tremor.get())
        cfg.Param.FLUTTER_SIZE = float(self.enter_jitter.get())
#        cfg.Param.PULSATILE = float(self.enter_pulse.get())
        cfg.Param.ASPIRATION = float(self.enter_aspire.get())        
#        cfg.Param.FENDA = float(self.enter_fenda.get())
#        cfg.Param.APHONIA =  self.enter_aphonia.get()

        
#    def _get_file(self):
#        
#        file = fdlg.askopenfilename(initialdir=cfg.Param.TRACTS_PATH,
#                                     filetypes =[("All files","*.*")],
#                                     title='Choose a file')
#        if file != None:
##            head, tail = os.path.split(file)
#            tail = os.path.relpath(file,cfg.Param.TRACTS_PATH)
#            print(file,cfg.Param.TRACTS_PATH,tail)
#            self.enter_vt_file.delete(0,tk.END)             
#            self.enter_vt_file.insert(0,tail)
#
#        cfg.Param.VT_TYPE         = "File" 

        
    def _update_male(self):
        
#        self.enter_vf_eta.delete(0,tk.END)             
#        self.enter_vf_eta.insert(0,500.)
        
        cfg.Param.ETA = 500
        
        self.enter_mass.delete(0,tk.END)          
        self.enter_mass.insert(0,.2)

        self.enter_damping.delete(0,tk.END)          
        self.enter_damping.insert(0,.025)

        self.enter_stiffness.delete(0,tk.END)          
        self.enter_stiffness.insert(0,90.)

        self.enter_length.delete(0,tk.END)          
        self.enter_length.insert(0,1.4)

        self.enter_depth.delete(0,tk.END)          
        self.enter_depth.insert(0,.3)

    def _update_female(self):
                
#        self.enter_vf_eta.delete(0,tk.END)             
#        self.enter_vf_eta.insert(0,1500.)
        
        cfg.Param.ETA = 1500
                
        self.enter_mass.delete(0,tk.END)          
        self.enter_mass.insert(0,.12)

        self.enter_damping.delete(0,tk.END)          
        self.enter_damping.insert(0,.015)

        self.enter_stiffness.delete(0,tk.END)          
        self.enter_stiffness.insert(0,185.)

        self.enter_length.delete(0,tk.END)          
        self.enter_length.insert(0,1.)

        self.enter_depth.delete(0,tk.END)          
        self.enter_depth.insert(0,.25)

    def _plot_vt(self):
        
#        areafile =  self.enter_vt_file.get()
#        
#        if areafile[-3:]== 'txt':
#            area = np.loadtxt("vocaltracts/" + areafile)
#        else:
#            npzfile = np.load("vocaltracts/" + areafile)
#            area    = npzfile['arr_0']  

        area = cfg.Param.AREA_VT
        
        if cfg.Param.SAMPLING_MODE == 2:
            a = len(area)
            if (a % 2) == 1:
                a -= 1
            area = (area[:a:2] + area[1:a:2])/2.
            
        vl      = len(area)
        l       = np.zeros(2*vl)
        l[::2]  = np.linspace(0,(vl-1)*cfg.Param.LTUBE,vl)
        l[1::2] = l[::2] + cfg.Param.LTUBE            
        w       = np.zeros(2*vl)
        w[::2]  = area
        w[1::2] = area
        
        t = tk.Toplevel(self.root)
        t.title("Vocal tract")

        f = Figure(figsize=(6,4))
        a = f.add_subplot(111)
        f.subplots_adjust(bottom=.15)
        a.plot(l, w,'-')
        a.set_ylabel("Area (cm$^2$)") 
        a.set_xlabel("Distance from glottis (cm)")
        a.set_title("Area function")

        canvas = FigureCanvasTkAgg(f, master=t)
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        
        toolbar = NavigationToolbar2TkAgg( canvas, t )
        toolbar.update()
        
#        t.mainloop()
        

    def _run(self):
        
        self.msg_1.config(text = "Running...")
        self.msg_1.update_idletasks()

        self.sound_ready = "No"
        
        self._acquire_data()
 
        synthesis_obj   = syn.Synthesis()

#        start_time = time()
        self.p_end = synthesis_obj.get_voice()

        self.oq              = synthesis_obj.get_openquotient()
        self.f0, self.j      = synthesis_obj.get_jitter()
        self.total_noise     = synthesis_obj.get_noise()
        (self.xg, self.ag, self.ug) = synthesis_obj.get_glottal()
        self.sb, self.sr = sp.compute_balance_and_ratio(self.ug)
                        
        y1 = - synthesis_obj.abduction/2.- self.xg[:,0]
        y2 = synthesis_obj.abduction/2.+ self.xg[:,1]
        
        for i in range(len(y1)):
            if y2[i] < y1[i]:
                y1[i] = (y1[i]+y2[i])/2.
                y2[i] = y1[i]

        
        if self.runwindow == True:
            self.t_runwindow.destroy()
            
        t = tk.Toplevel(self.root)         
        t.title("Results")
        
        self.t_runwindow = t
        self.runwindow = True
        
#       Frame 0: Plots
        
        frame0 = tk.Frame(t)
        
        f1 = Figure(figsize=(11,6))

        gs = gridspec.GridSpec(3, 2)
        
        a1 = f1.add_subplot(gs[0,0])
        a1.plot(synthesis_obj.t,y1, 'C0')
        a1.plot(synthesis_obj.t,y2, 'C1')
        a1.set_ylabel("VF displ (cm)") 
        setp(a1.get_xticklabels(), visible=False)
        a1.set_title("Glottal waveforms")

        a2 = f1.add_subplot(gs[1,0], sharex=a1)    
        a2.plot(synthesis_obj.t, self.ag)
        a2.set_ylabel("Area (cm$^2$)")
        setp(a2.get_xticklabels(), visible=False)
        
        a3 = f1.add_subplot(gs[2,0], sharex=a1)    
        a3.plot(synthesis_obj.t, self.ug/1000)
        a3.set_ylabel("Flow (dm$^3$/s)")
        a3.set_xlabel("Time (s)")

        a4 = f1.add_subplot(gs[0,1])
        a4.plot(synthesis_obj.t, self.p_end/10.)
        a4.set_ylabel("Pressure (Pa)")
        a4.set_title("Acoustic output")
        setp(a4.get_xticklabels(), visible=False)
        
        ims, fm1 = spg.get_ims(self.p_end)
        
        vv = np.max(ims)
        ims = ims.clip(min=vv-50.)       
        a5 = f1.add_subplot(gs[1:,1], sharex=a4)
#        a5.imshow(np.transpose(ims), origin="lower", aspect="auto", cmap="gray_r", 
#               extent=[0, cfg.Param.TIME_TOTAL, 0, fm1/1000], vmax = np.max(ims), 
#               vmin = np.max(ims) - 50)

        a5.imshow(np.transpose(ims), origin="lower", aspect="auto", cmap="gray_r", 
               extent=[0, cfg.Param.TIME_TOTAL, 0, fm1/1000], interpolation='bilinear', resample=False)


        a5.set_xlabel("Time (s)")
        a5.set_ylabel("Frequency (kHz)")
#        a5.set_xlim([0, cfg.Param.TIME_TOTAL])
        a5.set_ylim([0, 3])

        
        f1.subplots_adjust(bottom=.1, top=.9, hspace=.1, wspace=.2, left=.1, right=.97)
                
        canvas = FigureCanvasTkAgg(f1, master=t)        
        toolbar = NavigationToolbar2Tk( canvas, frame0)

        frame0.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1, padx=5, pady=5)

        toolbar.update()                

#       Frame 1: Info

        frame1 = ttk.LabelFrame(t)
        frame1.pack(side=tk.BOTTOM, fill=tk.X, expand=0, padx=5, pady=5)
        
#        textmssg = "Running time \t= %4.2f seconds\n" +\
#                   "F0 \t\t= %5.1f Hz\n" +\
#                   "Open qotient \t= %5.2f\n" +\
#                   "Jitter \t\t= %5.2f %%\n" +\
#                   "snr \t\t= %5.1f dB\n"+\
#                   "Spec balance \t= %5.2f kHz\n" +\
#                   "Spec ratio   \t= %5.2f dB"
#                                          
#        msg1 = tk.Message(frame1, text=textmssg % ((time() - start_time), 
#                                            self.f0, self.oq, self.j, self.total_noise[2], self.sb/1000., self.sr), 
#                                            width=250)        
        textmssg =  "F0 \t\t= %5.1f Hz\n" +\
                   "Open qotient \t= %5.2f\n" +\
                   "Jitter \t\t= %5.2f %%\n" +\
                   "snr \t\t= %5.1f dB\n"+\
                   "Spec balance \t= %5.2f kHz\n" +\
                   "Spec ratio   \t= %5.2f dB"
                                          
        msg1 = tk.Message(frame1, text=textmssg % (self.f0, self.oq, 
                          self.j, self.total_noise[2], self.sb/1000., self.sr), 
                                            width=250) 

        msg1.pack(side = tk.LEFT) 

#        self.enter_signal = tk.BooleanVar()
#        self.enter_signal.set(cfg.Param.SAVE_SIGNAL)         
#        chk_signal = tk.Checkbutton(frame1, text="Save signals", variable=self.enter_signal, 
#                                     onvalue=True, offvalue=False)
#        chk_signal.pack(side=tk.TOP, anchor=tk.E)
        
        but2 = tk.Button (frame1, text = " Close ", width = 10)
        but2.pack (side=tk.RIGHT, anchor = tk.S, padx=5, pady=5)
        but2.config (command = self.rundestroy)   

        but1 = tk.Button (frame1, text = " Save ", width = 10)
        but1.pack (side=tk.RIGHT, anchor = tk.S, padx=5, pady=5)
        but1.config (command = self._save_results)   

        but0 = tk.Button (frame1, text = " Play ", width = 10)
        but0.pack (side = tk.RIGHT, anchor = tk.S, padx=5, pady=5)
        but0.config (command = self._play_sound)  

#        self.msg_1 = tk.Label(text="Ready", anchor='w')        
#        self.msg_1.grid(column=0, row=3, sticky='WES', padx=10, pady=10)  
                
        self.msg_1.config(text = "Ready")
        
        t.mainloop()

    def rundestroy(self):
        
        self.t_runwindow.destroy()
        self.runwindow = False
        

    def _save_results(self):
        
        file = fdlg.asksaveasfilename(initialfile= "Untitled.wav", initialdir=cfg.Param.RESULT_PATH, 
                                     defaultextension=".wav",
                                     filetypes =[("Audio","*.wav"),("All files","*.*")],
                                     title='Save wav')
        if file != None and file !='':

            if self.sound_ready == "No":
                self.sound_out = sound_output.get_sound_file(self.p_end)
                self.sound_ready = "Yes"
                
            sound_output.save_wavfile(self.sound_out, 44100., file)

#            if self.enter_signal.get() == True:
#                np.savez(file[:-3] + "npz", self.xg, self.ug, self.ag, self.p_end)

#            svr.save_parameters(file[:-4], self.oq, self.f0, self.j, self.total_noise, self.sb, self.sr)
    
#        cfg.Param.SAVE_SIGNAL =  self.enter_signal.get()
        
            
    def _play_sound(self):

        if self.sound_ready == "No":
                self.sound_out = sound_output.get_sound_file(self.p_end)
                self.sound_ready = "Yes"

        sd.play(np.fromstring(self.sound_out, dtype='int16'), 
                int(cfg.Param.FS/cfg.Param.DECIMATE), blocking=True)
        
            
    def _run_lam(self):

#        self.enter_vt_file.delete(0,tk.END) 
#        self.enter_vt_file.insert(0,"Vowel?") #cfg.Param.VT_FILE)
        t1 = tk.Toplevel(self.root)
        glam.MainWindow(t1,self.var_f)

    def callback(self,event):

        webbrowser.open_new(r"http://lucero.mat.unb.br")


if __name__ == "__main__":
    
    if 'win' in platform:
        windll.shcore.SetProcessDpiAwareness(1)
    root = tk.Tk()
    main = MainWindow(root)
    root.mainloop()
