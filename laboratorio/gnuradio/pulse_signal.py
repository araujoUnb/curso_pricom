# this module will be imported in the into your flowgraph
import numpy as np

def sinc_gnu(freq,pulse_len):

    t = np.linspace(0,pulse_len-1,pulse_len)
    x = np.sinc(2*np.pi*freq*t)
    
    return list(x)
    
    
