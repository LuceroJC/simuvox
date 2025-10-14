

import numpy             as np


# According to K. Steiglitz, "A Digital Signal Processing Primer", 
# Addison-Wesley, 1996, and J. O. Smith, Introduction to Digital Filters",
# https://ccrma.stanford.edu/~jos/filters/filters.html

# See also K. Steiglitz, "A note on constant-gain digital resonators", 
# Computer Music Journal 18, 8-10, 1994.
   
class TwoPoles(object) :
    
    def __init__(self, fp, bw, fs) :
               
        self.__y_m1 = 0.
        self.__y_m2 = 0.
        self.__fs   = fs

        psi         = 2 * np.pi * fp / fs
        b           = 2 * np.pi * bw / fs
        R           = np.exp(- b / 2.) 
        cos_teta    = ((2. * R) / (1. + R * R)) * np.cos(psi)
        A_0         = (1. - R * R) * np.sqrt(1. - cos_teta * cos_teta)

        self.a      = A_0
        self.b      = 2. * R * cos_teta
        self.c      = - R * R

 
    def get_sample(self, x) :
        
        y           = self.a * x + self.b * self.__y_m1 + self.c * self.__y_m2

        self.__y_m2 = self.__y_m1
        self.__y_m1 = y
        
        return y
        
        
    def plot_ftransfer(self):
        
        import matplotlib.pyplot as plt
        import numpy             as np
        
        n         = 1000
        theta     = np.linspace(0, 2* np.pi * 200 / self.__fs, n)
        buff      = theta * (0. - 1.j)
        z         = np.exp(buff)
        
        h_zero    = self.a * z * z
        h_pole    = 1. /(z * z - self.b * z - self.c)
        H         = abs(h_pole * h_zero)
    
        x_axis    = theta * fs / (np.pi * 2.)
        
        plt.figure()
        plt.plot(x_axis,20 * np.log10(np.abs(H)))
        plt.show()


class TwoPolesZeros(object):

    def __init__(self,fp, bw, fs):

        self.__y_m1  = 0.
        self.__y_m2  = 0.
        self.__x_m1  = 0.
        self.__x_m2  = 0.
        self.__fs   = fs

        
        psi          = 2. * np.pi * fp / fs
        b            = 2. * np.pi * bw / fs

        R            = np.exp(- b / 2.)
        cos_teta     = ( (1. + R * R) / (2. * R) ) * np.cos(psi)
        A_0          = (1. - R * R)/ 2.
        
        self.a       = A_0
        self.b       = 2. * R * cos_teta
        self.c       = - R * R
        self.d       = - A_0


    def get_sample(self, x):
        
        y     = self.a * x + self.b * self.__y_m1 + self.c * self.__y_m2 + \
                self.d * self.__x_m2

        self.__y_m2 = self.__y_m1
        self.__y_m1 = y
        self.__x_m2 = self.__x_m1
        self.__x_m1 = x
        
        return y


    def plot_ftransfer(self):
        
        import matplotlib.pyplot as plt
        import numpy             as np
        
        n         = 1000
        theta     = np.linspace(0, 2* np.pi * 200 / self.__fs, n)
        buff      = theta * (0. - 1.j)
        z         = np.exp(buff)
        
        h_zero    = self.a * z * z + self.d
        h_pole    = 1. /(z * z - self.b * z - self.c)
        H         = abs(h_pole * h_zero)
    
        x_axis    = theta * fs / (np.pi * 2.)
        
        plt.figure()
        plt.plot(x_axis,20 * np.log10(np.abs(H)))
        plt.show()


if __name__ == "__main__":


    fs = 88200.    
    fp = 50.
    bw = 140.

    filter1 = TwoPoles(fp, bw, fs)
    filter1.plot_ftransfer()
    
    filter2 = TwoPolesZeros(fp, bw, fs)
    filter2.plot_ftransfer()
    



