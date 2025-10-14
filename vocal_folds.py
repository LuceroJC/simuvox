# -*- coding: utf-8 -*-

"""
Created on Fri Oct 05 13:05:12 2012

@author: Jorge C. Lucero
"""

import config as cfg
import numpy  as np


import modulation_noise_2ndorder  as m2


import triangle
import extrema as re


class VFmodel(object):
    
     def __init__(self,asupra,asub):
  
        self.dW = np.sqrt(cfg.Param.DELTA_T)
        
        self.__asupra = asupra
        self.__asub   = asub
        aw            = cfg.Param.CORR_COUPLING*asupra
        self.__aefect = asub*aw/(asub + aw)    
        
        self.__energ_clean            = 0.
        self.__energ_noise            = 1.e-12
        self.__energ_pulsatile        = 1.e-12
        self.__energ_aspiration       = 1.e-12

        self.__triangle               = triangle.Cos2Triangle()        
        self.__extrema                = re.RegularizedExtremum(cfg.Param.EPS_ROUNDING,
                                                               cfg.Param.EPS_ROUNDING) 

        self.__physio_tremor_obj      = m2.ModulationNoise(cfg.Param.WOW_FREQUENCY,
                                            cfg.Param.WOW_BW, cfg.Param.FS, 'reson')

        self.__neuro_tremor_obj       = m2.ModulationNoise(cfg.Param.TREMOR_FREQUENCY,
                                            cfg.Param.TREMOR_BW, cfg.Param.FS, 'reson')

        self.__muscle_jitter_obj      = m2.ModulationNoise(cfg.Param.FLUTTER_FREQUENCY,
                                            cfg.Param.FLUTTER_BW, cfg.Param.FS, 'reson_z')


        self.__noise_obj              = m2.ModulationNoise(0.,1200.,
                                            cfg.Param.FS, 'reson')


        self.__wvector                = np.array([0., 1, 0., 0.])
        

        self.__medial_area            = cfg.Param.GLOTTAL_LENGTH*cfg.Param.GLOTTAL_DEPTH
        self.__mass_per_area          = cfg.Param.MASS/self.__medial_area        
        self.__damping_per_area       = cfg.Param.DAMPING/self.__medial_area  


        self.__c1 = cfg.Constant.SOUND_SPEED/cfg.Param.KT
        self.__c2 = 2.*cfg.Param.KT/cfg.Constant.SOUND_SPEED**2./cfg.Constant.DENSITY_AIR
        self.__c3 = cfg.Constant.SOUND_SPEED*cfg.Constant.DENSITY_AIR/asub
        self.__c4 = cfg.Constant.SOUND_SPEED*cfg.Constant.DENSITY_AIR/aw
        self.__c5 = 2.*cfg.Param.TAU/cfg.Param.KT

        if cfg.Param.REYNOLDS == "Yes":                 
            self.__c6 = (cfg.Constant.DENSITY_AIR/cfg.Param.GLOTTAL_LENGTH/cfg.Constant.VISCOSITY_AIR)**2

        self.c_wow        = cfg.Param.WOW_SIZE*cfg.Param.WOW_SCALE
        self.c_tremor     = cfg.Param.TREMOR_SIZE*cfg.Param.TREMOR_SCALE
        self.c_flutter    = cfg.Param.FLUTTER_SIZE*cfg.Param.FLUTTER_SCALE
        self.c_aspiration = cfg.Param.ASPIRATION*cfg.Param.ASPIRATION_SCALE
             
        self.noise_scale = np.sqrt(cfg.Param.FS)/100000.
        
     def _flow(self, ag,  w, sep,  ps_in, pi_in):
        
       
        ag += cfg.Param.FENDA*cfg.Param.GLOTTAL_LENGTH*sep 
        
        if ag > 0. :
            
            rs = (self.__asub - ag)/(self.__asub + ag)
            ri = (self.__asupra - ag)/(self.__asupra + ag)
            
            aratio = ag/self.__aefect
            
            delta_p = (1. + rs)*ps_in - (1. + ri)*pi_in        
            
            if delta_p >= 0:
                ug_clean = ag*self.__c1*(-aratio +
                             np.sqrt(aratio*aratio + self.__c2*delta_p))
            else:
                ug_clean = -ag*self.__c1*(-aratio +
                             np.sqrt(aratio*aratio - self.__c2*delta_p))
                           
     
        else:
 
            rs = 1.
            ri = 1.
            delta_p = 2.*(ps_in - pi_in)                
            ug_clean = 0.            


        add_noise               = self.noise_scale*self.__noise_obj.get_filtered_noise_sample()
#        add_noise               = self.__noise_obj.get_filtered_noise_sample()
        pulsatile_noise         = add_noise * cfg.Param.PULSATILE * ug_clean      

        if cfg.Param.REYNOLDS == "Yes":  
            re_numbersq = ug_clean*ug_clean*self.__c6    
            aspiration_noise        = add_noise * self.c_aspiration*max(0., re_numbersq 
                                                                       - 1440000.)/100.
        else:
            aspiration_noise        = add_noise * self.c_aspiration*max(0., delta_p 
                                                                       - 8000.)
    
        noise = pulsatile_noise + aspiration_noise

            
        if cfg.Param.APHONIA == True:
            ug_clean = 0.
            
        ug    = ug_clean + noise
        
        
        self.__energ_clean        += ug_clean*ug_clean
        self.__energ_noise        += noise*noise
        self.__energ_aspiration   += aspiration_noise*aspiration_noise
        self.__energ_pulsatile    += pulsatile_noise*pulsatile_noise
        
        ps_out = rs*ps_in - self.__c3*ug
        pi_out = ri*pi_in + self.__c4*ug

        ps = ps_out + ps_in
        pi = pi_out + pi_in        
        
        if ag > 0. :
            pg = pi + self.__c5*(ps-pi)*(w[1] + w[3])/sep   
        else:
            pg = pi


        
        return ug, pg, ps_out, pi_out


     def _perturb(self):        
        
        wow    = self.c_wow*self.dW*self.__physio_tremor_obj.get_filtered_noise_sample()        
        tremor = self.c_tremor *self.dW*self.__neuro_tremor_obj.get_filtered_noise_sample()  
        jitter = self.c_flutter *self.dW*self.__muscle_jitter_obj.get_filtered_noise_sample()
      
        return wow, tremor, jitter 


     def vectorfield(self, ps_in, pi_in, sep, stiffness):
         
        k      = stiffness/self.__medial_area          
        
        w  = self.__wvector
        q  = cfg.Param.Q
        
        ag = (1. - cfg.Param.FENDA)*cfg.Param.GLOTTAL_LENGTH*(sep + w[0] + w[2])
        ag = self.__extrema.get_regularized_max(ag, 0.) 
        ag = self.__triangle.get_triangle(ag)

        ug, pg, ps_out, pi_out = self._flow(ag, w, sep, ps_in, pi_in)
        

        e_force1 = k*w[0]
        e_force2 = q*k*w[2]
        
        if ag <= 0.:
             
             e_force1 = e_force1 + k/(1 + q)*(w[0] + w[2] + sep)   
             e_force2 = e_force2 + q*k*q/(1 + q)*(w[0] + w[2] + sep)        
             
#       Compute jitter

        wow_1, tremor_1, jitter_1 = self._perturb()        
        wow_2, tremor_2, jitter_2 = self._perturb()        
  
#       Vector field
        
        f = np.array([w[1],\
                      (-self.__damping_per_area*(1 + cfg.Param.ETA*w[0]*w[0])*w[1]\
                      - e_force1 + pg)/self.__mass_per_area,\
                      w[3],\
                      (-self.__damping_per_area*(1 + cfg.Param.ETA*w[2]*w[2])*w[3]\
                      - e_force2 + pg)/self.__mass_per_area]) 
             
        g = np.array([0.,\
                      -(wow_1 + tremor_1 + jitter_1)*e_force1/self.__mass_per_area,\
                      0.,\
                      -(wow_2 + tremor_2 + jitter_2)*e_force2/self.__mass_per_area])
        
        self.__wvector = w + cfg.Param.DELTA_T*f + g

        return ps_out, pi_out, self.__wvector, ag, ug

         
     def get_flow_to_noise_ratio(self):

        yop1 = 10.*np.log10(self.__energ_clean/self.__energ_aspiration)
        yop2 = 10.*np.log10(self.__energ_clean/self.__energ_pulsatile)
        yop3 = 10.*np.log10(self.__energ_clean/self.__energ_noise)

        return (yop1, yop2, yop3)
     
