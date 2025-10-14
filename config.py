# -*- coding: utf-8 -*-
"""
Created on Fri Oct 05 13:05:12 2012

@author: Jorge C. Lucero
"""

import numpy   as np
#import os
#from   os.path import expanduser

    
class Constant(object):

    DENSITY_AIR    = 0.001112       # g/cm^3   
    SOUND_SPEED    = 35661.         # cm/s
    VISCOSITY_AIR  = 0.000192       # dyn s/cm^2
    THERMAL_AIR    = 2.7            # Thermal conductivity of air in erg/(cm s K)
    PRANDTL_AIR   =  0.715


class Param(object):
    
#    HOME            = expanduser("~")
#    RESULT_PATH     = HOME + "/Documents/Research/voiceSynth/SoundFiles"
#    HOME            = os.getcwd()
    RESULT_PATH     = "./" #HOME + "/soundfiles"
#    TRACTS_PATH     = os.getcwd() #+ "/vocaltracts"
    COMMENT         = "voice"

    AREA_VT_PARAM   = np.array([ -1.5,  2.0, 0.0, -0.5,  0.5, -0.5, 0.0 ])   
    VT_FILE         = "aa"
    VT_TYPE         = "Maeda"     # vt data type: File/Cos/Maeda


    AREA_VT = np.array([3.21, 2.77, 1.98, 1.36, 1.27, 1.71, 2.18, 2.34, 2.28,\
                        2.09, 1.84, 1.69, 1.68, 1.80, 2.02, 2.29, 2.58, 2.87,\
                        3.11, 3.21, 3.20, 3.12, 3.02, 2.99, 3.16, 3.73, 4.78,\
                        6.15, 7.53, 8.49, 8.85, 8.86, 8.71, 8.26, 7.86, 7.84,\
                        7.80, 6.16, 4.21, 3.72, 3.63])

    GRAPHICS        = False
    SAVE_SOUND      = False
    SAVE_PARAM      = False
    SAVE_SIGNAL     = False
    
    GENDER          = "Male"
    PROSODY         = False
    
    TIME_TOTAL      = 1.5                      # Total signal duration in s
    TIME_ONSET      = 0.3
    TIME_OFFSET     = 0.15
    TIME_FINAL      = 0.1

    SAMPLING_MODE   = 3      # 1: 88200 Hz, 2: 44100 Hz, 3: 44100 Hz and half-sampling for the vt

    if SAMPLING_MODE == 1:

        DECIMATE      = 2
        FS            = 88200.
        HALF_SAMPLING = "No"

    elif SAMPLING_MODE == 2:
        
        DECIMATE      = 1
        FS            = 44100.
        HALF_SAMPLING = "No"

    else: 
        
        DECIMATE      = 1
        FS            = 44100.
        HALF_SAMPLING = "Yes"
           
    DELTA_T         = 1./FS                     # s 
    SQRT_DELTA_T    = np.sqrt(DELTA_T)
    LTUBE           = Constant.SOUND_SPEED/FS   # Elementary tube length in cm
    LTUBE_TRACHEA   = LTUBE 
    
    if HALF_SAMPLING == "Yes":
        LTUBE = LTUBE/2.
            
    MAXFREQ         = 1000.                     # Max frequency for computing cycle lengths, in Hz

    LIPS_FR         = True     # Flanagan & Rabiner's (1972) model for lip reflexion/transmission
    VISC_LOSS       = False    # Acoustic losses for thermal conduction and air viscosity
    WALL_VIBR       = False   # Acoustic losses for wall vibration
    
    NVOCAL          = 3               # Number of filter elements for thermal and viscous losses   
    CORR_LOSS       = 1. #.85              # Coeficient to adjust losses
    LP              = .4              # Coeficients to compute the impedances of vocal tract walls 
    RP              = 6500. #       in cgs units, Flanagan et al. (1972)

    AREA_TRACHEA    = 2.5      # cm^2, Lous et al. (1998) 
    LENGTH_TRACHEA  = 15.      # cm
    FCUT_BRONQUI    = 500.     # Hz, Lous et al. (1998)
    LENGTH_BRONQUI  = 10.      # cm, Lous et al. (1998)
    
    REFLEXION_LUNGS        = .2  
    REFLEXION_LIPS         = - 0.95    
    REFLEXION_SUPRAGLOTTIS = 1.    
    REFLEXION_SUBGLOTTIS   = 1.    

    CORR_COUPLING  = 3.0      # Correction for coupling to the downstream vocal tract
    CORR_LIPS      = 3.0      # Correction coefficient for lip model

    if GENDER == "Male":        

        GENDER_SCALE     = 1.           
        ETA              = 500.      # Nonlinear damping coefficent, in cm^{-2}
        STIFFNESS        = 90000.   # Vocal fold stiffness per area in dyn/cm
        GLOTTAL_LENGTH   = 1.4       # cm
        GLOTTAL_DEPTH    = .3        # cm
        MASS             = 0.2       # Vocal fold mass per area in g        
        DAMPING          = 25.       # Vocal fold damping in dyn s/cm

    else:
        
        GENDER_SCALE     = .8
        ETA              = 1500.     # Nonlinear damping coefficent, in cm^{-2}
        STIFFNESS        = 185000.   # Vocal fold stiffness in dyn/com
        GLOTTAL_LENGTH   = 1.        # cm
        GLOTTAL_DEPTH    = .25       # cm
        MASS             = 0.12      # Vocal fold mass in g  
        DAMPING          = 15.       # Vocal fold damping in dyn s/cm
    
    PL                    = 5000.     # Lung pressure in dyn/cm^2
    ABDUCTION             = .08       # Initial vocal fold separation in cm

    KT                    = 1.1       # Transglottal pressure coefficient 
    TAU                   = .0008     # Time delay in s
    Q                     = 1.        # Stifness asymmtry
       
    EPS_ROUNDING          = .1        # Rounding for the glottal area at closure
        
    WOW_FREQUENCY = 1.         # Hz
    WOW_BW        = 1.         # Hz. The passband is actually 0-1.45 
    WOW_SIZE      = 1.
    
    TREMOR_FREQUENCY = 3.      # Hz
    TREMOR_BW        = 4.      # Hz
    TREMOR_SIZE      = 1.      # 

    FLUTTER_FREQUENCY = 50.    # Hz
    FLUTTER_BW        = 140.   # Hz. The passband is actually 15 - 150
    FLUTTER_SIZE      = 1.
    
    NOISE_BW = 1300.         # Hz
    FLOW  = 500.
    FHIGH = 1500.
    ASPIRATION = 1. 
    PULSATILE  = 0.
    APHONIA    = False
    FENDA      = 0. # length of glottal chink relative to the total glottal length
    REYNOLDS   = "No" # noise generation model
  
    STRAIN     = 0.
    
#   GUI

    WOW_SCALE        = 0.005
    TREMOR_SCALE     = 0.003
    FLUTTER_SCALE    = 0.0008
    ASPIRATION_SCALE = .6    


     
