import wave
import random
import config as cfg


def normalize(x):

    """ normalize float signal so that it is comprised between -2.**15 and +2.**15 """

    max_x = x[0]

    for item in x :
        max_x = max (max_x,abs(item))

    if abs(max_x) < 1.e-10 : max_x = 1.

    ratio = ((2.**15)-1.) / max_x

    for i in range(0,len(x)):
        x[i] = x[i] * ratio

    max_x = x[0]
    min_x = x[0]

    for item in x :
        max_x = max (max_x,item)
        min_x = min (min_x,item)


    assert max_x <= 2.**15
    assert min_x >= -(2.**15)
    
    return x

def quantize_and_code(x):

    """ creates quantized signal """
    
#    signal = "".join(wave.struct.pack('h',item) for item in x)
    
    signal = x.astype('int16').tostring()

    return signal

def dither(x):

    """ adds small amount of noise to signal """

    quantization_step = 1. / (2.**15)

    for i in range(0,len(x)):
        x[i] = x[i] + quantization_step * random.triangular(low = -1., high = +1., mode = 0.)

    return x
    
def save_wavfile(x,fs,name):
    
    """ sampling width = number of bytes """

    nchannels = 1
    sampwidth = 2
    framerate = int(fs)
    nframes   = len(x)
    comptype  = "NONE"
    compname  = "not compressed"

    wav_file = wave.open(name,"w")
    wav_file.setparams((nchannels,sampwidth,framerate,nframes,comptype,compname))

    wav_file.writeframes (x)

    wav_file.close()

def get_sound_file(x):
    
    if cfg.Param.DECIMATE > 1 :
        #from scipy.signal import decimate
        #x = decimate(x, cfg.Param.DECIMATE)
        x = x[::2]
    """ normalizes, dithers, quantizes and outputs in that order """
    
    x = normalize(x)
    x = dither(x)
    x = quantize_and_code(x)
    
    return x






    
