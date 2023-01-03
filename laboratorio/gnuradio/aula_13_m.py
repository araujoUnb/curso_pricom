# this module will be imported in the into your flowgraph

import numpy as np


def message(B,t_max,samp_rate):
    
    nPoints = int(samp_rate*(2*t_max))
    t = np.linspace(-t_max,t_max,nPoints)
    m = np.sinc(B*np.pi*t)

    return list(m)

