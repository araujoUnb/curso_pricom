import numpy as np
from scipy.signal import butter, lfilter

def butter_lowpass(cutoff, fs, order=6):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    return b, a

def butter_lowpass_filter(data, cutoff, fs, order=6):
    b, a = butter_lowpass(cutoff, fs, order=order)
    y = lfilter(b, a, data)
    return y

def retificador(u_t):
    nSamples = len(u_t)
    r_t = []
    for ii in range(nSamples):
        if u_t[ii]>=0:
            r_t.append(u_t[ii])
        else:
            r_t.append(0)

    return np.array(r_t)



def mod_AM_convencional(m_t,t,A_c,fc,a):

    c_t = np.cos(2*np.pi*fc*t)
    m_n  = m_t/np.max(m_t)
    return A_c*(1+a*m_n)*c_t

def demod_AM_convecional(u_t,cutoff,fs):

    r_t = retificador(u_t)
    g_t = butter_lowpass_filter(r_t,cutoff,fs)
    return g_t, r_t


   
    


def mod_dsbsc_am(m_t,t,A_c,fc,phi):
    c_t = A_c*np.cos(2*np.pi*fc*t + phi)
    return m_t*c_t


def demod_dsbsc_am(u_t,t,A_c,fc,cutoff,fs):

    c_t = A_c*np.cos(2*np.pi*fc*t)
    r_t = u_t*c_t                   # Sinal na saída do multiplicador
    g_t = butter_lowpass_filter(r_t,cutoff,fs)
    return g_t, r_t



