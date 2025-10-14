# -*- coding: utf-8 -*-

"""
Created on Fri Oct 05 13:05:12 2012

@author: Jorge C. Lucero
"""

import vt_data           as vtd
import config            as cfg
import vocal_tract       as vtm
import vocal_folds       as vfm
import numpy             as np
import minjerk


class Synthesis(object):
    
    def __init__(self) :
        
        self.__nsamples     = int(cfg.Param.TIME_TOTAL*cfg.Param.FS) 
        self.t              = np.linspace(0,cfg.Param.TIME_TOTAL, self.__nsamples)

        vocaltract_obj      = vtd.MakeVT()

        self.__voice_timing = np.array([0., cfg.Param.TIME_ONSET, cfg.Param.TIME_TOTAL - 
                                       (cfg.Param.TIME_OFFSET + cfg.Param.TIME_FINAL), 
                                        cfg.Param.TIME_TOTAL - cfg.Param.TIME_FINAL, 
                                        cfg.Param.TIME_TOTAL]) 

        pl_pattern        = np.array([0., cfg.Param.PL, cfg.Param.PL, 0., 0.])
 
        abduction_pattern = np.array([cfg.Param.ABDUCTION, cfg.Param.ABDUCTION, cfg.Param.ABDUCTION, 
                                      cfg.Param.ABDUCTION, cfg.Param.ABDUCTION])                
        
        stiffness_pattern = np.array([cfg.Param.STIFFNESS, cfg.Param.STIFFNESS, cfg.Param.STIFFNESS, 
                                      cfg.Param.STIFFNESS, cfg.Param.STIFFNESS])
        
              
        if cfg.Param.PROSODY == True:
            stiffness_pattern = np.array([1., 1., 0.9, 0.9, 0.9])*stiffness_pattern
        
        self.pl             = minjerk.make_signal(self.__voice_timing, pl_pattern, self.t)       
        self.abduction      = minjerk.make_signal(self.__voice_timing, abduction_pattern, self.t)
        self.stiffness      = minjerk.make_signal(self.__voice_timing, stiffness_pattern, self.t)

 
        
        self.__downstr_obj  = vtm.DownstreamVT(vocaltract_obj.AREA)
        self.__upstr_obj    = vtm.UpstreamVT(vocaltract_obj.TRACHEA, self.pl[0])

        self.__md_obj       = vfm.VFmodel(vocaltract_obj.AREA[0], vocaltract_obj.TRACHEA[0])
 
        self.__ag           = np.zeros(self.__nsamples)
        self.__wg           = np.zeros((self.__nsamples,4))
        self.__ug           = np.zeros(self.__nsamples)
        
        self.__oq           = 0.
        self.__f0           = 0.
        self.__jitter       = 0.
        self.__jitter2      = 0.        
        self.__noise        = (1000., 1000., 1000.)        
                       
        
    
    def get_voice(self):
 
        p_vt_glot_back = 0.
        p_tr_sub_back  = 0.
        p_end          = np.zeros(self.__nsamples)
        
        nstart         = 2.*self.__voice_timing[1]*cfg.Param.FS
        nend           =    self.__voice_timing[2]*cfg.Param.FS
 
        cycles         = int((self.__voice_timing[2] - self.__voice_timing[1])*cfg.Param.MAXFREQ)       
        oqcycle        = np.zeros(cycles)                              
        iop1           = 0
        iop2           = 0
        noq            = 0        
        tcycle         = np.zeros(cycles)                      
        icycle         = 0
        
        for n in range(1,self.__nsamples):

            # Excitation

            (p_tr_sub_for, p_vt_glot_for,
             self.__wg[n,:], self.__ag[n], 
             self.__ug[n])                  = self.__md_obj.vectorfield(
                                                  p_tr_sub_back, p_vt_glot_back,
                                                  self.abduction[n], self.stiffness[n])


            if n > nstart and n < nend:
            
                # Open quotient

                if noq < cycles:                    
                    if self.__ag[n] <= .0001 and self.__ag[n-1] > .0001:
                        if iop1 > 0 and iop2 > 0:
                            oqcycle[noq]   += (n - iop2)/float(n - iop1)
                            noq            +=1
                        iop1 = n
                    if self.__ag[n] > .0001 and self.__ag[n-1] <= .0001:
                        iop2 = n  
                else:
                    print("Warning: increase MAXFREQ")
        
                # Cycle boundaries
                                
                if icycle < cycles:
                    if self.__wg[n, 0] >= 0. and self.__wg[n-1, 0] < 0.:
                        tcycle[icycle] = (self.__wg[n,0]*(n - 1) - self.__wg[n-1,0]*n)*\
                                          cfg.Param.DELTA_T/(self.__wg[n,0] - self.__wg[n-1,0])
                        icycle += 1
    
                else:
                    print("Warning: increase MAXFREQ")
    
            # Propagation in the vocal tract
        
            if cfg.Param.HALF_SAMPLING == "Yes":
                (p_end[n], p_vt_glot_back) = self.__downstr_obj.propagation_half(p_vt_glot_for)
            else:
                (p_end[n], p_vt_glot_back) = self.__downstr_obj.propagation(p_vt_glot_for)
                
            p_tr_sub_back              = self.__upstr_obj.propagation(p_tr_sub_for, self.pl[n])
     
        # Compute jitter and open quotient
    
        if icycle > 1:
            per             = tcycle[1:icycle] - tcycle[:icycle-1]    
            (self.__jitter,
             self.__f0)     = self._compute_jitter_percent(per)
        else:
            self.__jitter  = 0.
            self.__f0      = 0.

        if noq > 0:        
            self.__oq       = np.median(oqcycle[:noq])
        else:
            self.__oq = 1.
            
        # Compute noise 
    
        self.__noise    = self.__md_obj.get_flow_to_noise_ratio()

        # Vocal fold position
    
        return p_end
        
        
    def _compute_jitter_percent(self, series):

        n               = series.size
        jitter          = 0.
        average_length  = 0.
    
        running_average = (series[:-2] + series[1:-1] + series[2:])/3.    
        jitter          = np.sum(abs(running_average - series[1:-1]))
        average_length  = np.sum(series[1:-1])/float(n - 2)

        # Alternative jitter measure as in Voxmetria 
                
        # perturb = abs(series[1:-1] - running_average)/abs(running_average) 
        # jitter2 = (100./float(n-2))*np.sum(perturb)

        if average_length == 0.:
            return(-1,0)
        else:
            average_f0          = 1./average_length
            jitter              = (100./float(n - 2))*jitter/average_length
    
        return (jitter, average_f0)    
        
        
    def get_glottal(self):

        return (self.__wg[:,[0,2]], self.__ag, self.__ug)


    def get_openquotient(self):

        return self.__oq        

        
    def get_jitter(self):

        return (self.__f0, self.__jitter)        

        
    def get_noise(self):

        return self.__noise        