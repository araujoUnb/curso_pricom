import numpy as np



def message(B,t_max,sample_rate):

    nPoints = int(2*t_max*sample_rate)
    t = np.linspace(-t_max,t_max,nPoints)
    m = np.sinc(B*np.pi*t)
    return list(m)# this module will be imported in the into your flowgraph
