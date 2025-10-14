# -*- coding: utf-8 -*-
"""
Created on Fri Mar 31 11:17:00 2017

@author: Jorge
"""


import numpy as np


def interp1d(xp,yp,x):

    window_len = 5
    y= np.interp(x, xp, yp)
    s= np.r_[y[window_len-1:0:-1],y,y[-2:-window_len-1:-1]]
    w = np.ones(window_len,'d')
    yy = np.convolve(w/w.sum(),s,mode='valid')

    return yy[2:-2]