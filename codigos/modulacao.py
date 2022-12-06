

import numpy as np
from  scipy.integrate import cumtrapz
def modulaçao_angular(t,fo,phi):
    return np.cos(2*np.pi*fo*t + phi)

def modulacao_pm(t,m_t,kp,fo=1):
    
    phi = kp*m_t
    return modulaçao_angular(t,fo,phi)

def modulacao_fm(t,m_t,kf,fo=1):
    
    phi = np.zeros(len(t))
    phi[1::] =2*np.pi*kf*cumtrapz(m_t,t)
    return modulaçao_angular(t,fo,phi)