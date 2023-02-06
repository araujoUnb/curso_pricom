import numpy as np

def sinc(B,T,fs):

    t = np.linspace(0,T,int(fs*T))
    x = np.sinc(B*t)

    return list(x)
