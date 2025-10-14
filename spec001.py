import numpy             as np
import config            as cfg
import matplotlib.pyplot as plt
from   numpy.lib         import stride_tricks
#from   scipy.signal      import gaussian

def plotstft(signal, window_length = 0.05, overlap = 0.5, colormap="gray_r", 
             dynamic_r = 50):
    
    nsignal    = len(signal)
    frame_size = int(cfg.Param.FS*window_length)
    step       = int(frame_size - np.floor(overlap * frame_size))
    signal     = np.append(np.zeros(int(np.floor(frame_size/2.0))), signal)    
    cols       = int(np.ceil( (nsignal - frame_size) / float(step)) + 1)
    signal     = np.append(signal, np.zeros(frame_size))   
    frames     = stride_tricks.as_strided(signal, shape=(cols, frame_size), 
                   strides=(signal.strides[0]*step, signal.strides[0])).copy()
    frames    *= gaussian(frame_size, 0.4*(frame_size-1)/2.)
     
    f = np.fft.rfftfreq(frame_size,cfg.Param.DELTA_T)
    s = np.fft.rfft(frames)
    
    ims = 20.*np.log10(np.abs(s))
    
    timebins, freqbins = np.shape(ims)
    
    plt.figure(figsize=(12, 6))
    plt.imshow(np.transpose(ims), origin="lower", aspect="auto", cmap=colormap, 
               extent=[0, cfg.Param.TIME_TOTAL, 0, f[-1]], vmax = np.max(ims), 
               vmin = np.max(ims) - dynamic_r)

    plt.title("Spectrogram")
    plt.xlabel("Time (s)")
    plt.ylabel("Frequency (Hz)")
    plt.xlim([0, cfg.Param.TIME_TOTAL])
    plt.ylim([0, 5000])


    plt.show(block=False)    
    
def get_ims( signal, window_length = 0.05, overlap = 0.5, dynamic_r = 50.):
        
    nsignal    = len(signal)
    frame_size = int(cfg.Param.FS*window_length)
    step       = int(frame_size - np.floor(overlap * frame_size))
    signal     = np.append(np.zeros(int(np.floor(frame_size/2.0))), signal)    
    cols       = int(np.ceil( (nsignal - frame_size) / float(step)) + 1)
    signal     = np.append(signal, np.zeros(frame_size))   
    frames     = stride_tricks.as_strided(signal, shape=(cols, frame_size), 
                   strides=(signal.strides[0]*step, signal.strides[0])).copy()
    sigma      = 0.4*(frame_size-1)/2.
    n          = np.arange(0,frame_size)-int(frame_size/2.)
    window     = np.exp(-n*n/sigma/sigma/2.)
#    frames    *= gaussian(frame_size, 0.4*(frame_size-1)/2.)
    frames    *= window/np.max(window)
    
    f = np.fft.rfftfreq(frame_size,cfg.Param.DELTA_T)
    s = np.fft.rfft(frames)
    
    ims = 20.*np.log10(np.abs(s))
    
    return ims, f[-1]

    