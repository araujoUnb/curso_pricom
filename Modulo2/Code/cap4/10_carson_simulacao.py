#!/usr/bin/env python3
"""
Script 10: banda de Carson numa simulação
Gera, em Latex-slides/FM/dados/:
  psd_tom.dat     f_kHz psd_dB   FM com tom, f_m = 1 kHz, Delta f = 5 kHz (beta = 5)
  psd_ruido.dat   f_kHz psd_dB   FM com mensagem aleatória de banda W = 1 kHz, mesmo pico de desvio
e imprime a fração da potência dentro da banda de Carson em cada caso.
"""

import os
import sys
import numpy as np
from scipy import signal

saida = sys.argv[1] if len(sys.argv) > 1 else '../../Latex-slides/FM/dados'
os.makedirs(saida, exist_ok=True)
rng = np.random.default_rng(7)

fs = 200e3
T = 4.0
t = np.arange(0, T, 1/fs)
W = 1e3
df = 5e3

def envoltoria(m):
    # FM em banda básica: g(t) = exp(j 2 pi k_f int m)
    return np.exp(1j * 2*np.pi * df * np.cumsum(m) / fs)

def psd(g):
    f, P = signal.welch(g, fs=fs, nperseg=2**15, return_onesided=False, scaling='spectrum', window='blackmanharris')
    i = np.argsort(f)
    return f[i], P[i]

def salva(nome, f, P):
    sel = np.abs(f) <= 15e3
    PdB = 10*np.log10(P[sel] / P.max())
    # reduz pontos para o pgfplots: máximo em blocos de 4
    fk, Pk = f[sel] / 1e3, PdB
    n = len(fk) // 4 * 4
    fk = fk[:n].reshape(-1, 4).mean(1); Pk = Pk[:n].reshape(-1, 4).max(1)
    np.savetxt(f'{saida}/{nome}', np.column_stack([fk, np.maximum(Pk, -70)]), header='f P', comments='', fmt='%.4f')

def fracao(f, P, B):
    return P[np.abs(f) <= B/2].sum() / P.sum()

# tom
m_tom = np.cos(2*np.pi*W*t)
f1, P1 = psd(envoltoria(m_tom))
salva('psd_tom.dat', f1, P1)

# mensagem aleatória limitada em W, normalizada para pico 1
b, a = signal.butter(8, W, fs=fs)
m_r = signal.filtfilt(b, a, rng.standard_normal(len(t)))
m_r /= np.max(np.abs(m_r))
f2, P2 = psd(envoltoria(m_r))
salva('psd_ruido.dat', f2, P2)

Bc = 2*(df + W)
print(f'Carson: {Bc/1e3:.0f} kHz')
print(f'tom: {100*fracao(f1, P1, Bc):.1f} % da potência dentro de Carson')
print(f'aleatória: {100*fracao(f2, P2, Bc):.1f} % da potência dentro de Carson, valor RMS de m = {np.sqrt(np.mean(m_r**2)):.2f}')
for nome, (f, P) in {'tom': (f1, P1), 'aleatória': (f2, P2)}.items():
    c = np.cumsum(P) / P.sum()
    lo, hi = f[np.searchsorted(c, 0.005)], f[np.searchsorted(c, 0.995)]
    print(f'{nome}: banda de 99 % = {(hi - lo)/1e3:.1f} kHz')
