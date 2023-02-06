# this module will be imported in the into your flowgraph

import numpy as np

def sinc(B,T,fs):

    t = np.linspace(-T/2,T/2,int(fs*T))
    x = np.sinc(B*t)

    return list(x)
