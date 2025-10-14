import config_lam   as cfl
import tkinter      as tk
import numpy        as np
import lam
import tkinter.ttk   as ttk
import config
#import tkFileDialog as fdlg


class MainWindow(tk.Frame):

    def __init__(self, root, w, *args, **kwargs):
         
        self.w = w
        self.root = root
        
        tk.Frame.__init__(self, *args, **kwargs)
        
        self.vowels   = ["Neutral"] + cfl.Param.VOWELCODE

        self.lv  = len(self.vowels)
        self.lp  = 7 # cfl.Param.JAW + cfl.Param.TNG + cfl.Param.LIP + cfl.Param.LRX
        self.vc = self.vowels[cfl.Param.INITVW]
        self.pa  = config.Param.AREA_VT_PARAM  #np.zeros(self.lp)
        
#        t = tk.Toplevel(root)
#        self.art = lam.Lam(t)        

#        self.art.get_vt(self.pa, True)

        root.title("Articulatory Model")
          
#       Frame 1: Controls

        frame1 = ttk.LabelFrame(root, text="Controls")
        
        frame1.grid(row=0, column=1, columnspan=2, sticky='WEN', padx=5, pady=5, ipadx=5, ipady=5)
        
        label_var1     = []
        label_var2     = []
        self.enter_var = []
        self.slide_var = []
        
        for i in range(self.lp):
        
            label_var1.append( ttk.Label (frame1, text = cfl.Param.CONTROLS[i]) )
            label_var1[i].grid(column=0, row=i, sticky='E', padx=5, pady=2) 
            
            self.enter_var.append( tk.StringVar() )
            self.enter_var[i].set('%4.1f' % float(self.pa[i]))
            
            self.slide_var.append(ttk.Scale (frame1, from_=-3, to_=3, orient=tk.HORIZONTAL, 
                                  length=200, value = self.pa[i], 
                                  command = self.scale_callback_factory(i)) )
            self.slide_var[i].grid(column=1, row=i, sticky='E', padx=5, pady=2)
    
            label_var2.append(ttk.Label(frame1, textvariable=self.enter_var[i], width = 4) )
            label_var2[i].grid(column=2, row=i, padx=5, pady=2)

#       Frame 2: Gender

        frame2 = ttk.LabelFrame(root, text="Size")
        frame2.grid(row=1, column =1, columnspan=2, sticky='NWE', padx=5, pady=5, ipadx=5, ipady=5)

        self.gender = tk.StringVar()
        self.gender.set("Male")

#        label_gender = ttk.Label(frame2, text = "Gender:")
#        label_gender.grid(column=0, row=12, sticky='E', padx=5, pady=2) 
        
        bmale = ttk.Radiobutton(frame2, text="Male", width=10, variable=self.gender, value="Male")
        bmale.grid(column=1, row=12, sticky='W', padx=5, pady=0)
        bmale.config(command = self._update_gender)        
        
        bfemale = ttk.Radiobutton(frame2, text="Female", width=10, variable=self.gender, value="Female")
        bfemale.grid(column=2, row=12, sticky='W', padx=5, pady=0)
        bfemale.config(command = self._update_gender)
        
#       Frame 3: Presets

        frame3 = ttk.LabelFrame(root, text="Presets")
        frame3.grid(row=2, column=1, columnspan=2, sticky='WEN', padx=5, pady=5, 
                    ipadx=5, ipady=5)

        self.vowel = tk.IntVar()
        self.vowel.set(cfl.Param.INITVW)

        label_vowel = tk.Label(frame3, text = "Vowel:")
        label_vowel.grid(column=0, row=0, sticky='E', padx=5, pady=2) 
  
        button_vowel = []

        for i in range(self.lv):
            
            ic = i//4
            ir = i%4
                
            button_vowel.append(ttk.Radiobutton(frame3, text=self.vowels[i], width=10,
                                                variable=self.vowel, value=i,
                                                command = self._update_vowel))
            button_vowel[i].grid(column=ic, row=ir, sticky='WE', padx=5, pady=0)


#       Frame 4: Formants

        frame4 = ttk.LabelFrame(root, text="Formants")
        frame4.grid(row=3, column=1, columnspan=2, sticky='WEN', padx=5, pady=5, 
                    ipadx=5, ipady=5)
        
        self.enter_showf = tk.BooleanVar()
        self.enter_showf.set(False)    
        chk_showf = tk.Checkbutton(frame4, text="Show (Hz)", variable=self.enter_showf, onvalue=True,
                                   offvalue=False, command= self._shoformants)
        chk_showf.grid(column=0, row=0, columnspan= 3, sticky='W', padx=0, pady=2)
               
        label_f1 = []
        label_f2 = []
        self.var_f = []
        
        for i in range(6):
            
            ic = 2*(i//2)
            ir = i%2
            
            label_f1.append( tk.Label(frame4, text = "F"+str(i+1)+":", anchor = 'e'))
            label_f1[i].grid(column=ic, row=ir+1, padx=2, pady=2) 
             
            self.var_f.append( tk.StringVar() )

            if self.enter_showf.get() == True: 
                self.art.get_formants()
                self.var_f[i].set('%d' % int(self.art.res_f[i]))
            else:
                self.var_f[i].set('')
          
            label_f2.append( tk.Label(frame4, textvariable = self.var_f[i], width =5))
            label_f2[i].grid(column=ic+1, row=ir+1, padx=2, pady=2)  

        
#       Frame 5: Run

        frame5 = ttk.Frame(root)
        frame5.grid(row=4, column=1, columnspan=2, sticky='EN', padx=5, pady=5, 
                    ipadx=5, ipady=5)
        
        but0 = tk.Button (frame5, text = "Apply", width=10)
        but0.grid (column = 1, row = 0, padx=5, pady=5, sticky="E")
        but0.config (command = self._put_tubes)  

        but1 = tk.Button (frame5, text = "Close", width=10)
        but1.grid (column = 2, row = 0, padx=5, pady=5, sticky="E")
        but1.config (command = root.destroy)

#       Frame 6: Save
        
#        but_save = tk.Button(root, text="Save", width=10)
#        but_save.grid(row=2, column=0, sticky='W', padx=5, pady=2)
#        but_save.config (command = self._save_file)     
        
#       Frame 7
        
        frame7 = ttk.LabelFrame(root, text="Vocal tract")
        frame7.grid(row=0, column=0, columnspan=1,  rowspan=5, sticky='N', padx=5, pady=5, 
                    ipadx=5, ipady=5)

        self.art = lam.Lam(frame7)        
        self.art.get_vt(self.pa, True)

        
    def _save_file(self):
        
        file = fdlg.asksaveasfilename(initialfile= "Untitled.txt", initialdir=config.Param.TRACTS_PATH, 
                                     defaultextension=".txt",
                                     filetypes =[("Audio","*.txt"),("All files","*.*")],
                                     title='Save vocal tract')
        if file != None:

            np.savetxt(file,self.art.tubes,fmt = "%5.2f") 
            np.savetxt(file[:-4] + "_par.txt",self.pa,fmt = "%5.2f") 

    def _shoformants(self):
            
        for i in range(6):

            if self.enter_showf.get() == True:  
                    self.art.get_formants()
                    self.var_f[i].set('%d' % int(self.art.res_f[i]))
            else:
                    self.var_f[i].set('')
                
                
    def scale_callback_factory(self, i):

        return lambda c:self.update(c, i)
    
    
    def update(self,c,i):
                            
        self.enter_var[i].set('%4.1f' % float(c))
        self.pa[i]   = float(c)                   # The scale for PA is -3 to 3
        self._get_vt()
        
    def _update_gender(self):

        cfl.Param.GENDER = self.gender.get()
        self._get_vt()


    def _update_vowel(self):
        
        c = self.vowel.get() 
        
        if c == 0:        
            self.pa[:] = np.zeros(self.lp)
        else:
            self.pa[:] = cfl.Param.VOWELPAR[c - 1,:]
        
        self.vc = self.vowels[c] 
        
        for i in range(self.lp):
            self.enter_var[i].set('%4.1f' % float(self.pa[i]))
            self.slide_var[i].set(self.pa[i])

        
    def _get_vt(self):

        self.art.get_vt(self.pa, self.enter_showf.get())            
        for i in range(6):

            if self.enter_showf.get() == True:  
                self.var_f[i].set('%d' % int(self.art.res_f[i]))
            else:
                self.var_f[i].set('')

    def _put_tubes(self):
        
        self._get_vt()
        config.Param.AREA_VT = self.art.tubes
        config.Param.AREA_VT_PARAM = self.pa
        config.Param.VT_FILE = self.vc
        config.Param.VT_TYPE = "Maeda"

        self.w.set(self.vc)
#        print(self.vc)
#        self.root.destroy()
        
if __name__ == "__main__":
    
    root = tk.Tk()
    main = MainWindow(root,'aa')
    root.mainloop()