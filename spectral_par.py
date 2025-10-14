import numpy as np
import config as cfg

    
def compute_spectral_balance(amplitude_spectrum):

    n_spectrum          = len(amplitude_spectrum)
    energy              = np.cumsum(amplitude_spectrum**2)
    spectral_balance    = 0.
    
    for i in range(0,n_spectrum):

        if energy[i] > energy[-1]/2. :
            spectral_balance = i * cfg.Param.FS / n_spectrum /2.
            break

    return spectral_balance

        
def compute_spectral_ratio(amplitude_spectrum):
    
    n_spectrum          = len(amplitude_spectrum)
    sf_d2               = 0.5*cfg.Param.FS

    n_crit              = int (n_spectrum * 1000. / sf_d2)

    energy_low = np.sum(amplitude_spectrum[:n_crit]**2)
    energy_high = np.sum(amplitude_spectrum[n_crit:]**2)

    ratio = 10. * np.log10 (energy_low / energy_high)

    return ratio

    
def compute_balance_and_ratio (any_signal) :

    n_onset          = int(cfg.Param.TIME_ONSET*cfg.Param.FS)
    n_offset         = int((cfg.Param.TIME_TOTAL - cfg.Param.TIME_OFFSET - cfg.Param.TIME_FINAL)*cfg.Param.FS)
    
    signal = any_signal[n_onset:n_offset]
    l_signal = len(signal)
    window = np.hamming(l_signal)
    
    exponent         = int(np.log(l_signal)/np.log(2.))+1
   
    spectrum = np.fft.fft(signal*window,2**exponent)
    spectrum=spectrum[range(l_signal//2)]
    amplitude_spectrum = 20*np.log10(np.abs(spectrum))          

    sb = compute_spectral_balance(amplitude_spectrum)
    sr = compute_spectral_ratio(amplitude_spectrum)
    
    return sb, sr    