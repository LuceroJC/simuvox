# -*- coding: utf-8 -*-

"""
Created on Fri Oct 05 13:05:12 2012

@author: Jorge C. Lucero
"""

import config    as cfg
import numpy as np



class ViscousLosses(object):
    
    """ Acoustic losses by thermal conduction and viscosity, Abel (2003)."""
    
    def __init__(self,area):
        
        self.__area     = area
        self.__ntubes   = area.size
        self.__pf       = np.zeros((self.__ntubes,cfg.Param.NVOCAL + 1))
        self.__pb       = np.zeros((self.__ntubes,cfg.Param.NVOCAL + 1))
        self.__pfloss   = np.zeros((self.__ntubes,cfg.Param.NVOCAL + 1))
        self.__pbloss   = np.zeros((self.__ntubes,cfg.Param.NVOCAL + 1))
 
        self.__nvisq, self.__dvisq = self._mfilter()
                
    def _mfilter(self):
    
        num_visq = np.zeros((self.__ntubes, cfg.Param.NVOCAL + 1))
        den_visq = np.zeros((self.__ntubes, cfg.Param.NVOCAL + 1))    
    
        for n in range(self.__ntubes):
    
            a1, b0, b1 = self._filtercoef(1, n)

            n1 = np.array([b0, b1])
            d1 = np.array([1, a1])
            
            for i in range(2, cfg.Param.NVOCAL + 1):
                
                a1, b0, b1 = self._filtercoef(i,n)
                
                n1 = np.polymul(n1, np.array([b0, b1]))
                d1 = np.polymul(d1, np.array([1, a1]))

            num_visq[n, :] = n1
            den_visq[n, :] = d1
            
        return num_visq, den_visq


    def _filtercoef(self, i, n):
            
        gamma   = cfg.Constant.THERMAL_AIR/2.
        sqrt_pr = np.sqrt(cfg.Constant.PRANDTL_AIR)
        A_alpha = 2.*np.sqrt(gamma)
        B_alpha = (1. + (gamma - 1.)/sqrt_pr)/np.sqrt(2.)        
        ft      = ((i - .5)/cfg.Param.NVOCAL)**3
        k       = np.array(range(1, cfg.Param.NVOCAL + 1))
        den     = np.sum(np.sqrt((k - .5)/cfg.Param.NVOCAL))
        num     = np.sqrt((i - .5)/cfg.Param.NVOCAL)
        rv      = self.__area[n]/np.sqrt(cfg.Constant.VISCOSITY_AIR/(cfg.Constant.DENSITY_AIR*\
                  np.pi*cfg.Param.FS))
        alpha_a = np.pi*cfg.Param.FS/(cfg.Constant.SOUND_SPEED*rv)*(A_alpha + \
                  B_alpha*rv/cfg.Constant.THERMAL_AIR)/(1+rv/cfg.Constant.THERMAL_AIR)
        g_pi    = np.exp(-num/den*cfg.Param.LTUBE*alpha_a)
        rho     = np.sin(np.pi/2.*(ft - .5))/np.sin(np.pi/2.*(ft + .5))
    
        if g_pi == 1.:
            alfa1 = 0.
        else:
            eta   = (g_pi + 1.)/(g_pi - 1.)        
            alfa1 = eta - np.sign(eta)*np.sqrt(eta**2-1.)
        
        beta0 = (1 + g_pi)/2. + (1 - g_pi)*alfa1/2.
        beta1 = (1 - g_pi)/2. + (1 + g_pi)*alfa1/2.
     
        a1 = (rho + alfa1)/(1 + rho*alfa1)     
        b0 = (beta0 + rho*beta1)/(1 + rho*alfa1)     
        b1 = (beta1 + rho*beta0)/(1 + rho*alfa1)

        return a1, b0, b1     


    def addloss(self,p_forward,p_backward):

        self.__pf[:-1,1:]  = self.__pf[:-1,:-1]        
        self.__pf[:-1,0]   = p_forward
        
        self.__pb[:-1,1:]  = self.__pb[:-1,:-1]        
        self.__pb[:-1,0]   = p_backward

        pfloss = np.sum(self.__nvisq[:-1,:]*self.__pf[:-1,:cfg.Param.NVOCAL + 1], axis=1)\
                         - np.sum(self.__dvisq[:-1,1:]*self.__pfloss[:-1,:cfg.Param.NVOCAL], axis=1)
        pbloss = np.sum(self.__nvisq[1:,:]*self.__pb[:-1,:cfg.Param.NVOCAL + 1],axis=1)\
                         - np.sum(self.__dvisq[1:,1:]*self.__pbloss[:-1,0:cfg.Param.NVOCAL],axis=1)
        
        self.__pfloss[:-1,1:] = self.__pfloss[:-1,:-1]            
        self.__pfloss[:-1,0]  = pfloss           
        self.__pbloss[:-1,1:] = self.__pbloss[:-1,:-1]            
        self.__pbloss[:-1,0]  = pbloss            

        return pfloss,pbloss

    def addloss_half(self,p_forward,p_backward,i):

        self.__pf[i:-1:2,1:]  = self.__pf[i:-1:2,:-1]        
        self.__pf[i:-1:2,0]   = p_forward
        
        self.__pb[i+1::2,1:]  = self.__pb[i+1::2,:-1]        
        self.__pb[i+1::2,0]   = p_backward

        pfloss = np.sum(self.__nvisq[i:-1:2,:]*self.__pf[i:-1:2,:cfg.Param.NVOCAL + 1], axis=1)\
                         - np.sum(self.__dvisq[i:-1:2,1:]*self.__pfloss[i:-1:2,:cfg.Param.NVOCAL], axis=1)
        pbloss = np.sum(self.__nvisq[i+1::2,:]*self.__pb[i+1::2,:cfg.Param.NVOCAL + 1],axis=1)\
                         - np.sum(self.__dvisq[i+1::2,1:]*self.__pbloss[i+1::2,0:cfg.Param.NVOCAL],axis=1)
        
        self.__pfloss[i:-1:2,1:] = self.__pfloss[i:-1:2,:-1]            
        self.__pfloss[i:-1:2,0]  = pfloss           
        self.__pbloss[i+1::2,1:] = self.__pbloss[i+1::2,:-1]            
        self.__pbloss[i+1::2,0]  = pbloss            

        return pfloss,pbloss         

class WallVibration(object):
    
    """ Reflexion coefcicients including acoustic losses by wall vibration at the vocal tract, 
        Flanagan et al. (1972)."""    
    
    def __init__(self, area):
        
        circ      = 2*np.sqrt(area*np.pi)    
        si        = cfg.Constant.DENSITY_AIR*circ*cfg.Param.LTUBE**2/cfg.Param.LP
        sr        = cfg.Constant.DENSITY_AIR*cfg.Constant.SOUND_SPEED*circ*cfg.Param.LTUBE/(cfg.Param.CORR_LOSS*cfg.Param.RP)      

        self.__rv =  (si - sr)/(si + sr) 
        
        self.__r1 = area[:-1]/(area[:-1] + area[1:] + si[:-1])
        self.__r2 = area[1:]/(area[:-1] + area[1:] + si[:-1])
        self.__r3 = si[:-1]/(area[:-1] + area[1:] + si[:-1])

        self.__r213 = self.__r2 - self.__r1 - self.__r3
        self.__r123 = self.__r1 - self.__r2 - self.__r3
        self.__r312 = self.__r3 - self.__r1 - self.__r2

        self.__p_in_loss  = np.zeros(len(area)-1)
        

#    def propagation(self,p_in_forward,p_in_backward_p1,p_in_loss):
#    
#        p_out_forward_p1 = 2.*self.__r1*p_in_forward + self.__r213*p_in_backward_p1\
#                           + 2.*self.__r3*p_in_loss
#        p_out_backward   = self.__r123*p_in_forward + 2.*self.__r2*p_in_backward_p1\
#                           + 2.*self.__r3*p_in_loss
#        p_out_loss       = 2.*self.__r1*p_in_forward + 2.*self.__r2*p_in_backward_p1\
#                           + self.__r312*p_in_loss
#        p_out_loss       = self.__rv[:-1]*p_out_loss
#
#        return p_out_forward_p1, p_out_backward, p_out_loss
# 

    def propagation(self,p_in_forward,p_in_backward_p1,p_in_loss):
    
        p_out_forward_p1 = 2.*self.__r1*p_in_forward + self.__r213*p_in_backward_p1\
                           + 2.*self.__r3*self.__p_in_loss
        p_out_backward   = self.__r123*p_in_forward + 2.*self.__r2*p_in_backward_p1\
                           + 2.*self.__r3*self.__p_in_loss
        p_out_loss       = 2.*self.__r1*p_in_forward + 2.*self.__r2*p_in_backward_p1\
                           + self.__r312*self.__p_in_loss
        self.__p_in_loss = self.__rv[:-1]*p_out_loss

        return p_out_forward_p1, p_out_backward, p_out_loss
    
    def propagation_half(self,p_in_forward,p_in_backward_p1,p_in_loss,i):
                
        p_out_forward_p1 = 2.*self.__r1[i::2]*p_in_forward + self.__r213[i::2]*p_in_backward_p1\
                           + 2.*self.__r3[i::2]*p_in_loss
        p_out_backward   = self.__r123[i::2]*p_in_forward + 2.*self.__r2[i::2]*p_in_backward_p1\
                           + 2.*self.__r3[i::2]*p_in_loss
        p_out_loss       = 2.*self.__r1[i::2]*p_in_forward + 2.*self.__r2[i::2]*p_in_backward_p1\
                           + self.__r312[i::2]*p_in_loss
        
        self.__p_in_loss = self.__rv[i:-1:2]*p_out_loss

        return p_out_forward_p1, p_out_backward, p_out_loss
        
class ReflexionCoef(object):
        
    def __init__(self, area):
    
        self.__reflex = (area[:-1] - area[1:])/(area[:-1] + area[1:])
        self.p_out_forward_p1 = np.zeros(len(area))
        self.p_out_backward   = np.zeros(len(area)) 
        self.__ntubes = len(area)

    def propagation(self, p_in_forward, p_in_backward_p1, p_vt_glottis_for, p_lips_back):
    
        theta            = self.__reflex*(p_in_forward[:-1] - p_in_backward_p1[1:])
        self.p_out_forward_p1[1:] = p_in_forward[:-1] + theta
        self.p_out_backward[:-1]   = p_in_backward_p1[1:] + theta
        
        self.p_out_forward_p1[0] = p_vt_glottis_for
        self.p_out_backward[-1]   = p_lips_back
        
        return self.p_out_forward_p1, self.p_out_backward,
        
    def propagation_half(self, p_in_forward, p_in_backward_p1, i):
    
        theta            = self.__reflex[i::2]*(p_in_forward - p_in_backward_p1)
        p_out_forward_p1 = p_in_forward + theta
        p_out_backward   = p_in_backward_p1 + theta

        return p_out_forward_p1, p_out_backward
        
    def propagation_halfNEW(self,p_in_forward,p_in_backward_p1,p_vt_glottis_for, p_lips_back,i):
        
        theta            = self.__reflex[i::2]*(p_in_forward[i:-1:2] - p_in_backward_p1[i+1::2])
        self.p_out_forward_p1[i+1::2] = p_in_forward[i:-1:2] + theta
        self.p_out_backward[i:-1:2]   = p_in_backward_p1[i+1::2] + theta

        if i == 1:      
            self.p_out_forward_p1[0] = p_vt_glottis_for
        if (self.__ntubes % 2) == (1 - i):
            self.p_out_backward[-1]   = p_lips_back
        
        return self.p_out_forward_p1, self.p_out_backward,
    
    
            
class LipsFR(object):
        
    """ Flanagan & Rabiner's (1972) model for lip reflexion/transmission """
    
    def __init__(self, mouth):
        
        self.mouth          = mouth
        self.__p_forward_mem = 0.
        self.__p_backward_mem = 0.
        self.__p_lips_mem    = 0.

        (self.nr, self.dr, self.nt, self.dt) = self.losses()
                    
    def losses(self):

        radi  = np.sqrt(self.mouth/np.pi)
        r     = 128./(9.*np.pi*np.pi) *cfg.Param.CORR_LIPS
        l     = 2.*cfg.Param.FS*(8.*radi)/(3.*np.pi*cfg.Constant.SOUND_SPEED)

        nr = np.array([-r - l + r*l, -r + l - r*l])
        dr = np.array([ r + l + r*l,  r - l - r*l])

        nt = np.array([2*r*l, -2*r*l])
        dt = np.array([r+2*l, r-2*l])

        
        return nr, dr, nt, dt

    def propagation(self, p_forward):
    
        p_backward = (self.nr[0]*p_forward + self.nr[1]*self.__p_forward_mem\
                             - self.dr[1]*self.__p_backward_mem)/self.dr[0]

        p_lips = (self.nt[0]*p_forward + self.nt[1]*self.__p_forward_mem\
                 - self.dt[1]*self.__p_lips_mem)/self.dt[0]

        self.__p_forward_mem=p_forward
        self.__p_backward_mem=p_backward        
        self.__p_lips_mem=p_lips
 
        return p_backward, p_lips


class LipsSimple(object):
    
    def propagation(self,p_forward_end,p_backward_end):
            
        p_backward_new_end = cfg.Param.REFLEXION_LIPS*p_forward_end
        p_lips = (1-cfg.Param.REFLEXION_LIPS)*p_forward_end

        return p_backward_new_end, p_lips
        

class DownstreamVT:
    
    def __init__(self, area):
        

        self.__ntubes         = area.size
        self.__p_forward       = np.zeros(self.__ntubes)
        self.__p_backward      = np.zeros(self.__ntubes)    
        self.__p_forward_new   = np.zeros(self.__ntubes)
        self.__p_backward_new  = np.zeros(self.__ntubes)    

        if cfg.Param.VISC_LOSS == True:
            self.__vlosses = ViscousLosses(area)
            
        if cfg.Param.WALL_VIBR == True:
            self.__p_loss  = np.zeros(self.__ntubes)   
            self.__junct   = WallVibration(area)
        else:
            self.__junct   = ReflexionCoef(area)            
        
        if cfg.Param.LIPS_FR == True:
            self.__liptr   = LipsFR(area[-1])
        else:
            self.__liptr   = LipsSimple()            

        self.__p_vt_glottis_back = 0.
        self.__p_vt_lips_back = 0.
    
    def propagation(self, p_vt_glottis_for):
                                                        
        p_in_forward      = self.__p_forward[:-1].copy()
        p_in_backward_p1  = self.__p_backward[1:].copy()                
 
        if cfg.Param.VISC_LOSS == True:                    
            (p_in_forward, 
             p_in_backward_p1) = self.__vlosses.addloss(p_in_forward, p_in_backward_p1)
           
        if cfg.Param.WALL_VIBR == True:
            p_in_loss           = self.__p_loss[:-1].copy()
            (p_out_forward_p1, 
             p_out_backward, 
             p_out_loss)        = self.__junct.propagation(p_in_forward, p_in_backward_p1,
                                                           p_in_loss)
            self.__p_loss[:-1]  = p_out_loss
        else:
            (p_out_forward_p1, 
             p_out_backward)    = self.__junct.propagation(p_in_forward, p_in_backward_p1)
                    
        self.__p_forward_new[1:]   = p_out_forward_p1
        self.__p_backward_new[:-1] = p_out_backward
       
        (self.__p_backward_new[-1],
         p_end)                    = self.__liptr.propagation(self.__p_forward[-1])
  
        self.__p_forward_new[0] = p_vt_glottis_for
        
        self.__p_forward   = self.__p_forward_new.copy()
        self.__p_backward  = self.__p_backward_new.copy()
        
    
        return p_end, self.__p_backward[0]
        
    def propagation_half(self, p_vt_glottis_for):
        
        for i in range(2):                                

            p_in_forward      = self.__p_forward[i:-1:2].copy()
            p_in_backward_p1  = self.__p_backward[i+1::2].copy()                
                
            if cfg.Param.VISC_LOSS == True:                    
                (p_in_forward, 
                 p_in_backward_p1) = self.__vlosses.addloss_half(p_in_forward, p_in_backward_p1,i)
               
            if cfg.Param.WALL_VIBR == True:
                p_in_loss           = self.__p_loss[i:-1:2].copy()
                (p_out_forward_p1, 
                 p_out_backward, 
                 p_out_loss)        = self.__junct.propagation_half(p_in_forward, p_in_backward_p1,
                                                               p_in_loss,i)
                self.__p_loss[i:-1:2]  = p_out_loss
            else:
                (p_out_forward_p1, 
                 p_out_backward)    = self.__junct.propagation_half(p_in_forward, p_in_backward_p1,i)
                        
            self.__p_forward_new[i+1::2]  = p_out_forward_p1
            self.__p_backward_new[i:-1:2] = p_out_backward
           
            
            if (self.__ntubes % 2) == (1 - i):   
                (self.__p_backward_new[-1],
                 p_end)                    = self.__liptr.propagation(self.__p_forward[-1])
            if i == 1:      
                self.__p_forward_new[0] = p_vt_glottis_for
            
            self.__p_forward   = self.__p_forward_new.copy()
            self.__p_backward  = self.__p_backward_new.copy()
        
    
        return p_end, self.__p_backward[0]

    def propagation_halfNEW(self,p_vt_glottis_for):
             
        for i in range(2):                                

            if (self.__ntubes % 2) == (1 - i):
                (p_lips_back, p_end)       = self.__liptr.propagation(self.__p_forward[-1])
            else:
                p_lips_back = 0.
                
            (p_forward_new, 
                 p_backward_new)    = self.__junct.propagation_half(self.__p_forward, self.__p_backward, 
                                        p_vt_glottis_for, p_lips_back,i)
       
            self.__p_forward   = p_forward_new.copy()
            self.__p_backward  = p_backward_new.copy()

#            if i == 1:      
#                self.__p_forward_new[0] = p_vt_glottis_for
            
    
        return p_end, self.__p_backward[0]

class UpstreamVT:
    
    def __init__(self, area, pl):
        
        self.__ntubes          = area.size
        self.__p_forward       = np.zeros(self.__ntubes)
        self.__p_backward      = np.zeros(self.__ntubes)
        self.__p_forward_new   = np.zeros(self.__ntubes)
        self.__p_backward_new  = np.zeros(self.__ntubes)    

        self.__junct = ReflexionCoef(area)       
            
        self.__p_tr_lungs_back = pl
    
        
    def propagation(self, p_tr_subglottis_for, pl):
        
        p_forward_new, p_backward_new = \
                   self.__junct.propagation(self.__p_forward,self.__p_backward,p_tr_subglottis_for,self.__p_tr_lungs_back)
                       
       
        self.__p_forward   = p_forward_new.copy()
        self.__p_backward  = p_backward_new.copy()
                
        self.__p_tr_lungs_back = pl - cfg.Param.REFLEXION_LUNGS*self.__p_forward[-1]            
         
        return self.__p_backward[0]
        