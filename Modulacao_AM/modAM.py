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


def mod_dsbsc_am(m_t,t,A_c,fc):
    c_t = A_c*np.cos(2*np.pi*fc*t)
    return m_t*c_t


def demod_dsbsc_am(u_t,t,A_c,fc,cutoff,fs):

    c_t = A_c*np.cos(2*np.pi*fc*t)
    r_t = u_t*c_t                   # Sinal na saída do multiplicador
    g_t = butter_lowpass_filter(r_t,cutoff,fs)
    return g_t, r_t



