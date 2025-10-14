# -*- coding: utf-8 -*-
"""
Created on Fri Aug 26 14:49:07 2016

@author: Jorge C. Lucero
"""

import config_lam        as cfl
import config            as cfg
import numpy             as  np
import vocal_tract       as vtm
import tkinter           as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure   import Figure

from interpolation import interp1d


def amo(p, q):

    return(np.sqrt((p[:,0] - q[:,0])*(p[:,0] - q[:,0]) + (p[:,1] - q[:,1])*(p[:,1] - q[:,1])) )

class Lam(object):
    
    def __init__(self,t):

        
#        gui_lam.MainWindow()
            
        self.ivt = np.zeros((cfl.Param.NG,2))		#  VT inside contours 
        self.evt = np.zeros((cfl.Param.NG,2))		#  VT exterior contours
        
#       Set fixed part of external wall
        
        self.fixed_wall = np.zeros((cfl.Param.NG-3,2))		#  VT exterior contours

        self.fixed_wall[:-1,:] = cfl.Param.VTOS * np.outer(cfl.Param.U_WAL,np.ones(2)) +\
                        cfl.Param.IGD
                 
#       Initialize lips
          
        self.fixed_wall[-1,0]  = cfl.Param.INCI[0]
        self.fixed_wall[-1,1]  = cfl.Param.INCI[1] + cfl.Param.INCI_LIP
        
        self.lip_hw     = np.zeros(2)
        
#       Initialize area function
        
        self.af         = np.zeros((cfl.Param.NG,2))
        
        if cfl.Param.POINTS == "Yes":

            self.xplot = np.zeros(2*cfl.Param.NG) 
            self.aplot = np.zeros(2*cfl.Param.NG)
            
        self.u = np.zeros(cfl.Param.NG)        
        self.finelength = np.linspace(0, 1, cfl.Param.NLENGTH)

#       Initialize formants

        self.res_f = np.zeros(6)
               
#       Initialize figure
        
#        t.title("Vocal tract")
#        frame5 = tk.Frame(t)
        
        self.f      = Figure(figsize=(5, 6))
        
        self.graph1 = self.f.add_subplot(211)

        self.graph1.set_title("Sagittal view")
        self.graph1.set_ylabel("Position (cm)")
        self.graph1.set_xlabel("Position (cm)")        
#        self.graph1.text(1,-3, "Lips (frontal view):")
        self.graph1.set_aspect('equal', adjustable='box') 
        self.graph1.set_ylim(-7, 4)
        self.graph1.set_xlim(-5, 6)
#        self.graph1.set_xticklabels([])
#        self.graph1.set_yticklabels([])

        self.graph2 = self.f.add_subplot(212)

        self.graph2.set_title("Area function")
        self.graph2.set_ylabel("Area (cm^2)")
        self.graph2.set_xlabel("Distance to glottis (cm)")

        self.f.subplots_adjust(bottom=.1, top=.95, hspace=.35)
        
#        self.f2     = plt.figure(2, figsize=(8, 6))
#        
#        self.graph3 = self.f2.add_subplot(111)
#
#        self.graph3.set_title("Vocal tract - Frequency response")
#        self.graph3.set_ylabel("Amplitude (dB)")
#        self.graph3.set_xlabel("Frequency (kHz)")        
#        self.graph3.set_xlim(0, 5)
        
        self.first_plot_area = 1
#        self.first_plot_form = 1

        canvas = FigureCanvasTkAgg(self.f, master=t)
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        
        toolbar = NavigationToolbar2Tk( canvas, t )
        toolbar.update()
  
        
    def compute_vectors(self,pa):
        
#       Tongue

        self.v_tng = cfl.Param.A_TNG.dot(pa[:4]) + cfl.Param.U_TNG

#       Lip 

        self.v_lip     = cfl.Param.A_LIP.dot(np.hstack((pa[0], pa[4:6]))) +\
                         cfl.Param.U_LIP

        self.v_lip[self.v_lip < 0] = 0.

#       Larynx 

        self.v_lrx     = cfl.Param.A_LRX.dot(np.hstack((pa[0], pa[6:]))) +\
                         cfl.Param.U_LRX
        
        
    def vect_projection(self):        

#       larynx back edge 
        
        self.ivt[0,:] = self.v_lrx[1:3]		# front edge
        self.evt[0,:] = self.v_lrx[3:5]		# rear edge 
        
#       Larynx, pharynx and buccal
        
        self.evt[2:-1,:] = self.fixed_wall
        
        v = np.minimum(self.v_tng, cfl.Param.U_WAL)
        
        self.ivt[2:-2,:] = cfl.Param.VTOS * np.outer(v,np.ones(2)) + cfl.Param.IGD        
        self.ivt[1,:]    = (self.ivt[2,:] + self.ivt[0,:])/2
        self.evt[1,:]    = (self.evt[2,:] + self.evt[0,:])/2
         
#       Lips

        self.ivt[-2,0] = self.evt[-2,0]
        self.ivt[-2,1] = self.evt[-2,1] - self.v_lip[2]

        self.evt[-1,0] = self.evt[-2,0] - self.v_lip[1]
        self.evt[-1,1] = self.evt[-2,1]
 
        self.ivt[-1,0] = self.evt[-1,0]
        self.ivt[-1,1] = self.ivt[-2,1]
        
#       Lip shape (ellipse)
        
        self.lips_hw = self.v_lip[2:4]/2.        

#       Gender correction

        if cfl.Param.GENDER == "Male":

            self.ivt     = cfl.Param.SIZE_CORR*self.ivt        
            self.evt     = cfl.Param.SIZE_CORR*self.evt        
            self.lips_hw = cfl.Param.SIZE_CORR*self.lips_hw        


    def plot_sagittal(self):
        
        ivt = self.ivt
        evt = self.evt

#       Plot points

        if cfl.Param.POINTS == "Yes" :

            if self.first_plot_area == 1:
                
                self.plot_i2, = self.graph1.plot(-ivt[:,0], ivt[:,1],'o')
                self.plot_e2, = self.graph1.plot(-evt[:,0], evt[:,1],'o')
                                
            else:
    
                self.plot_i2.set_data(-ivt[:,0], ivt[:,1])
                self.plot_e2.set_data(-evt[:,0], evt[:,1])
                self.plot_i2.set_marker('o')
                self.plot_e2.set_marker('o')
           

#       Interpolating spline
        
        self.u[1:] = np.sqrt((ivt[1:,0] - ivt[:-1,0])*(ivt[1:,0] - ivt[:-1,0]) +
                             (ivt[1:,1] - ivt[:-1,1])*(ivt[1:,1] - ivt[:-1,1]))            

        p_arc = np.cumsum(self.u)
        
        xnew_i = interp1d(p_arc,ivt[:,0],self.finelength*p_arc[-1])
        ynew_i = interp1d(p_arc,ivt[:,1],self.finelength*p_arc[-1])

        self.u[1:] = np.sqrt((evt[1:,0] - evt[:-1,0])*(evt[1:,0] - evt[:-1,0]) +
                             (evt[1:,1] - evt[:-1,1])*(evt[1:,1] - evt[:-1,1]))            

        p_arc = np.cumsum(self.u)
        
        xnew_e = interp1d(p_arc,evt[:,0],self.finelength*p_arc[-1])
        ynew_e = interp1d(p_arc,evt[:,1],self.finelength*p_arc[-1])

#       Plot 
        
        if self.first_plot_area == 1:
            
            self.plot_i, = self.graph1.plot(-xnew_i,ynew_i,'b',linewidth=1.0)
            self.plot_e, = self.graph1.plot(-xnew_e,ynew_e,'b',linewidth=1.0)
#            self.plot_i, = self.graph1.plot(-xnew_i,ynew_i)
#            self.plot_e, = self.graph1.plot(-xnew_e,ynew_e)
 
             
        else:

            self.plot_i.set_data(-xnew_i,ynew_i)
            self.plot_e.set_data(-xnew_e,ynew_e)
            
#       Plot lips
           
#        theta       = 2.*np.pi/(20)*np.arange(21)
#        lip_ellipse = np.vstack((self.lips_hw[1]*np.cos(theta), self.lips_hw[0]*np.sin(theta)))
#
#        if self.first_plot_area == 1:
#      
#            self.plot_lip, = self.graph1.plot(lip_ellipse[0,:] + 3, lip_ellipse[1,:] -4)
#        
#        else:
#
#            self.plot_lip.set_data(lip_ellipse[0,:] + 3, lip_ellipse[1,:] -4)


    def sagittal_to_area(self):
            
        ivt = self.ivt
        evt = self.evt
        af  = self.af

#       Larynx to buccal
        
        p  = amo(ivt[1:-1], ivt[0:-2])
        q  = amo(evt[1:-1], evt[0:-2])
        r  = amo(ivt[0:-2], evt[0:-2])
        s  = amo(evt[1:-1], ivt[1:-1])
        t  = amo(evt[1:-1], ivt[0:-2])
        
        a1 = 0.5*(p + s + t)
        a2 = 0.5*(q + r + t)
        
        s1 = np.sqrt(a1*(a1 - p)*(a1 - s)*(a1 - t))
        s2 = np.sqrt(a2*(a2 - q)*(a2 - r)*(a2 - t))
        
        xy = ivt[0:-2,:] + evt[0:-2,:] - ivt[1:-1,:] - evt[1:-1,:]
        d  = 0.5*np.sqrt(xy[:,0]*xy[:,0] + xy[:,1]*xy[:,1])

        w  = (s1 + s2)/d
        w[w < .0001] = .0001

        af[0:-2,0] = d
        af[0:-2,1] = 1.4*cfl.Param.ALPHA*pow(w,cfl.Param.BETA)  #  40% ad hoc increase
            
#       Lips (2 sections with equal length)
        
        af[-2,1] = np.pi * self.lips_hw[0] * self.lips_hw[1]
        af[-1,1] = af[-2,1]
        af[-2,0] = 0.5 * (ivt[-2,0] - ivt[-1,0])
        af[-1,0] = af[-2,0]
        
#       Check areas
        	
        af[:,0] = af[:,0].clip(0.01)
        af[:,1] = af[:,1].clip(0.0001)
        	
        self.af = af
    
    
    def make_tubes(self):
        
        self.log_area  = np.log(self.af[:,1])
        self.length_vt = np.sum(self.af[:,0])
        self.darea     = np.cumsum(self.af[:,0]) - self.af[:,0]/2.       

#       Improve epylarynx interpolation

        cm  = (self.log_area[0] - self.log_area[1])/(self.darea[1] - self.darea[0])
        x0  = self.darea[0]/2.
        dy  = cm*x0
        
        self.darea     = np.hstack((x0, 3.*x0, self.darea[1:]))
        self.log_area  = np.hstack((self.log_area[0] + .25*dy,
                                    self.log_area[0] - .5*dy,
                                    self.log_area[1:]))

#       Improve lip interpolation 

        dy  = self.log_area[-3] -self.log_area[-2]

        self.darea     = np.hstack((self.darea, self.length_vt))
        self.log_area  = np.hstack((self.log_area[:-2],
                                    self.log_area[-2] + .1*dy,
                                    self.log_area[-1] + .01*dy,
                                    self.log_area[-1])) 

#       Interpolate with pchip
        
        ntubes    = int(self.length_vt/cfg.Param.LTUBE)
        xnew      = np.linspace(0, self.length_vt, ntubes + 1)

        new_log_area     = interp1d(self.darea,self.log_area,xnew)
        new_area         = np.exp(new_log_area)

        self.tubes       = (new_area[:-1] + new_area[1:])/2.
        
        
    def plot_area(self):
         
        if cfl.Param.POINTS == "Yes":
            
            xplot = self.xplot
            aplot = self.aplot
            
            xplot[1::2]   = np.cumsum(self.af[:,0])
            xplot[2:-1:2] = xplot[1:-2:2]
            
            aplot[:-1:2]  = self.af[:,1]
            aplot[1::2]   = self.af[:,1]
             
            area_max = max(aplot)
            
            if self.first_plot_area == 1:
                
                self.plot_a2, = self.graph2.plot(xplot,aplot) 
                        
            else:
            
                self.plot_a2.set_data(xplot,aplot)

        xnew      = self.finelength*self.length_vt
 
        log_area_smooth  = interp1d(self.darea,self.log_area,xnew)
        area_smooth = np.exp(log_area_smooth)
        
        if self.first_plot_area == 1:
                
            self.plot_a, = self.graph2.plot(xnew,area_smooth,'b',linewidth=1.0)             
            self.first_plot_area = 0
                
        else:
            
            self.plot_a.set_data(xnew,area_smooth)

        area_max = max(area_smooth)
        self.graph2.set_ylim(0, 1.1*area_max)

        self.f.canvas.draw()

    


    def get_formants(self):

        nsamples            = int(.1*cfg.Param.FS) 
        downstr_obj         = vtm.DownstreamVT(self.tubes)
     
        p_vt_glot_back      = 0.
        p_end               = np.zeros(nsamples)
        
        In    = np.zeros(nsamples)
        In[0] = -200.
        
        for n in range(nsamples):
    
            pin = In[n] + cfg.Param.REFLEXION_SUPRAGLOTTIS*p_vt_glot_back
#            (p_end[n], p_vt_glot_back) = downstr_obj.propagation(pin)
                 
            if cfg.Param.HALF_SAMPLING == "Yes":
                (p_end[n], p_vt_glot_back) = downstr_obj.propagation_half(pin)
            else:
                (p_end[n], p_vt_glot_back) = downstr_obj.propagation(pin)
           
        h     = np.fft.fft(p_end)
        f     = np.fft.fftfreq(nsamples,1/cfg.Param.FS)
        h     = h[range(int(nsamples/2))]
        f     = f[range(int(nsamples/2))]
        yaxis = 20*np.log10(np.abs(h))
                
        nres = (np.diff(np.sign(np.diff(yaxis))) < 0).nonzero()[0] + 1 # local max
     
        for i in range(6):
            icw = np.arange(nres[i]-5,nres[i]+6)
            c=np.polyfit(f[icw],1./np.abs(h[icw])**2,2)
            self.res_f[i]=-c[1]/2./c[0]

#        if self.first_plot_form == 1:
#                
#            self.plot_formants, = self.graph3.plot(f/1000,yaxis)             
#            self.first_plot_form = 0
#                
#        else:
#            
#            self.plot_formants.set_data(f/1000,yaxis)
#
#        self.f2.canvas.draw()
#        plt.show()
        
    def get_vt(self,pa,showf = False):

        self.compute_vectors(pa)
        self.vect_projection()
        self.plot_sagittal()
        self.sagittal_to_area()
        self.make_tubes()
        self.plot_area()
        if showf == True:
            self.get_formants()

        
if __name__ == "__main__":
     
#    for i in range(11):
#        plt.close("all")  
#        art = Lam()
#        af  = art.get_vt(cfl.Param.VOWELPAR[i,:])
#        plt.savefig(cfl.Param.VOWELCODE[i]+'.png', bbox_inches='tight')


    art = Lam()
    af  = art.get_vt(np.zeros(7))
