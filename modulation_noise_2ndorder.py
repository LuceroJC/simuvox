

import numpy             as np
import reson2order       as r2


class ModulationNoise(object):
    
    def __init__(self, fp, bw, fs, tipo) :
   
        if tipo == "reson":
            self.__reson_obj    = r2.TwoPoles(fp, bw, fs)
        if tipo == "reson_z":
            self.__reson_obj    = r2.TwoPolesZeros(fp, bw, fs)         

    def get_filtered_noise_sample(self):
        
        dW     = np.random.standard_normal()
        sample = self.__reson_obj.get_sample(dW)

        return sample


if __name__ == "__main__":

    import matplotlib.pyplot as plt
    import config            as cfg
    
    fp   = 50.
    bw   = 140.

    noise_obj = ModulationNoise(fp, bw, cfg.Param.FS, 'reson')

    n     = int(cfg.Param.TIME_TOTAL*cfg.Param.FS) 
    t     = np.linspace(0,cfg.Param.TIME_TOTAL, n)

    noise          = np.zeros(n)
    filtered_noise = np.zeros(n)

    sd = np.sqrt(cfg.Param.DELTA_T)

    for i in range(0, n) :

        noise[i] = sd*np.random.standard_normal()
        filtered_noise[i] = noise_obj.get_filtered_noise_sample()

    plt.figure()
    p1 = plt.subplot(2,1,1)
    plt.plot(t,noise)
    plt.subplot(2,1,2, sharex=p1)
    plt.plot(t,filtered_noise)
 