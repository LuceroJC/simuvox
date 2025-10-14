

import numpy              as np


class Cos2Triangle(object) :


    
    def __init__(self) :

 
        
        ctt      = +8. / (np.pi * np.pi)

        ##### computation of correction, because harmonics are missing #####

        i    = 5
        corr = 0.

        while i < 1000 :
            bffr = ctt / (i*i)
            corr = corr + bffr
            i    = i + 2

        ##### computation of correction because of decreased harmonics owing to Fejer #####

        
        fej_1 = 4./5.
        fej_3 = 2./5.
        fej_5 = 0.

        missing = (1. - fej_1) * ctt + (1. - fej_3) * ctt / 9. + (1. - fej_5) * ctt / 25.

        ctt       = ctt + corr + missing
        self.a_1  = fej_1 * ctt
        self.a_3  = fej_3 * ctt / 9.
        self.a_5  = fej_5 * ctt / 25.


    def get_triangle(self, x) :

        
        T_0  = 1.
        T_1  = x
        T_2  = 2. * x * T_1  - T_0
        T_3  = 2. * x * T_2  - T_1
        T_4  = 2. * x * T_3  - T_2
        T_5  = 2. * x * T_4  - T_3

        return self.a_1 * T_1 + self.a_3 * T_3 + self.a_5 * T_5 
