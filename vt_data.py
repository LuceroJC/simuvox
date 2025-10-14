# -*- coding: utf-8 -*-
"""
Created on Fri Oct 05 13:05:12 2012

@author: Jorge C. Lucero

This will be much expanded

"""
import numpy             as np
import config            as cfg
import matplotlib.pyplot as plt
#from   scipy.interpolate import splrep, splev

class MakeVT(object):

    def __init__(self) :

        if cfg.Param.VT_TYPE == "Cos":
            
            self.AREA = self._get_area_par()

        elif cfg.Param.VT_TYPE == "Maeda":
            
            self.AREA = self._get_maeda()
            
        else:

            self.AREA = self._get_area()

            
        self.TRACHEA = self._trachea()
        
        
    def _trachea(self):
        
        tubes         = int(cfg.Param.LENGTH_TRACHEA/cfg.Param.LTUBE_TRACHEA)
        area_trachea  = cfg.Param.AREA_TRACHEA*np.ones(tubes)
        alfa          = 4.*np.pi*cfg.Param.FCUT_BRONQUI/cfg.Constant.SOUND_SPEED
        x             = np.linspace(0,cfg.Param.LENGTH_BRONQUI,
                                    int(cfg.Param.LENGTH_BRONQUI/cfg.Param.LTUBE_TRACHEA))
        area_lungs   = cfg.Param.AREA_TRACHEA*np.exp(alfa*x) 
        area         = cfg.Param.GENDER_SCALE*np.hstack((area_trachea,area_lungs))
        
        return area
        
        
#    def _reducesize(self, area, scale):
#        
#        x = np.linspace(0., 1., area.size)
#        tck = splrep(x, area, s=0)
#        xnew = np.linspace(0., 1., scale*area.size)
#        ynew = splev(xnew, tck, der=0)
#        
# #       return ynew*(scale**2)        
#        return ynew    

    def _get_area(self):

        if cfg.Param.VT_FILE[-3:]== 'txt':
            area = np.loadtxt("vocaltracts/" + cfg.Param.VT_FILE)
        else:
            npzfile = np.load("vocaltracts/" + cfg.Param.VT_FILE)
            area    = npzfile['arr_0']  
        
        if cfg.Param.SAMPLING_MODE == 2:
            a = len(area)
            if (a % 2) == 1:
                a -= 1
            area = (area[:a:2] + area[1:a:2])/2.
            
        return area
        
    def _get_maeda(self):

        area    = cfg.Param.AREA_VT
        
        if cfg.Param.SAMPLING_MODE == 2:
            a = len(area)
            if (a % 2) == 1:
                a -= 1
            area = (area[:a:2] + area[1:a:2])/2.
            
        return area
        
    def _plot_vt(self):
            
        plt.ion()
                        
        fig = plt.figure(figsize=(8, 8),)
        fig.subplots_adjust(hspace = 0.3)

        plt.subplot(2,1,1)
        plt.title("Vocal tract")
        l, w = self._get_tubes(self.AREA)        
        plt.plot(l, w,'-')
        plt.ylabel("Area (cm$^2$)")
        plt.xlabel("Distance from glottis (cm)")

        plt.subplot(2,1,2)
        plt.title("Trachea and bronchi")
        l, w = self._get_tubes(self.TRACHEA)        
        plt.plot(-l, w,'-')
        plt.ylabel("Area (cm$^2$)")
        plt.xlabel("Distance from glottis (cm)")

        
        plt.show()
        plt.pause(.001)    
        

    def _get_tubes(self, area):
        
        vl      = len(area)
        l       = np.zeros(2*vl)
        l[::2]  = np.linspace(0,(vl-1)*cfg.Param.LTUBE,vl)
        l[1::2] = l[::2] + cfg.Param.LTUBE            
        w       = np.zeros(2*vl)
        w[::2]  = area
        w[1::2] = area
        
        return l, w
        
    def _get_area_par(self):

        npzfile = np.load("vocaltracts/" + cfg.Param.VT_FILE)
                
        leng      = npzfile['arr_0']
        c         = npzfile['arr_1']
        nbasis    = len(c)

        nsect     = int(round(leng/cfg.Param.LTUBE))
        newlength = np.linspace(0, 1, nsect + 1)
        B         = np.ones((nsect+1, nbasis))
    
        for i in range(1, nbasis):
            B[:, i] = np.cos(i*np.pi*newlength)/2.
    
        log_area  = B.dot(c)
        area      = np.exp(log_area)
        tube_area = (area[:-1] + area[1:])/2.
        
        if cfg.Param.GRAPHICS == True:
            self._plot_vt2(leng,c,nbasis,nsect,tube_area)
 
        return tube_area
            
            
    def _plot_vt2(self, leng, c, nbasis, nsect, tube_area):
        
        lfine   = 101 
        
        plt.figure()
           
        finelength = np.linspace(0, 1, lfine)
        B1         = np.ones((lfine, nbasis))

        for i in range(1, nbasis):
            B1[:, i] = np.cos(i*np.pi*finelength)/2.
    
        log_area1 = B1.dot(c)
        area1     = np.exp(log_area1)

        plt.plot(finelength*leng, area1)
        
        vl      = len(tube_area)
        l       = np.zeros(2*vl)
        l[::2]  = np.linspace(0,(vl-1)*(cfg.Param.LTUBE),vl)
        l[1::2] = l[::2] + cfg.Param.LTUBE           
        w       = np.zeros(2*vl)
        w[::2]  = tube_area
        w[1::2] = tube_area
        plt.plot(l, w,'r-')
        
        plt.title("Area function")
        plt.ylabel("Area (cm$^2$)")
        plt.xlabel("Distance from glottis (cm)")
        plt.show(block=False)
