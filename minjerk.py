# -*- coding: utf-8 -*-
"""
Created on Fri Mar 31 11:17:00 2017

@author: Jorge
"""

# Minimum jerk interpolation. From B. Story, JASA, 2005: "A parametric model of the vocal tract..."

import numpy as np


def make_signal(timing, ampl, time):
    
    ns = len(time)
    s  = np.zeros(ns)
    n  = len(timing)
    
    for i in range(n-1):
        
        n0 = int(timing[i]/time[-1]*(ns-1))
        nf = int(timing[i+1]/time[-1]*ns)
        tt    = np.linspace(0., 1., nf-n0)

        s[n0:nf] = ampl[i] + (ampl[i+1] - ampl[i])*(10.*tt**3 - 15.*tt**4 +6.*tt**5)
        
    return s