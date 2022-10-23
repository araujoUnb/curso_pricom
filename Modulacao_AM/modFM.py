
import numpy as np
from scipy.integrate import cumulative_trapezoid

def pm_phi_t(kp,m_t):
    return kp*m_t

def fm_phi_t(kf,m_t,t):
    return 2*np.pi*kf*cumulative_trapezoid(m_t,t)


def modFM(fc,m_t,kf,t):
    phi_t = fm_phi_t(kf,m_t,t)
    return np.cos(2*np.pi*fc*t[0:-1] + phi_t)

def modPM(fc,m_t,kp,t):
    phi_t = pm_phi_t(kp,m_t)
    return np.cos(2*np.pi*fc*t + phi_t)

