# this module will be imported in the into your flowgraph
import numpy as np


def sinc_gnu(freq,Tmax,pulse_len):

    t = np.linspace(-Tmax,Tmax,int(pulse_len))
    x = np.sinc(2*np.pi*freq*t)
    return list(x)
    
    
    
