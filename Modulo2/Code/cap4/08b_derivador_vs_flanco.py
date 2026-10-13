#!/usr/bin/env python3
"""
Script 08b: derivador puro versus flanco de um circuito ressonante
Gera: derivador_vs_flanco.pdf/png

Com f_c muito maior que o desvio, |H_d(f)| = 2*pi*f é quase constante na
banda do FM e o envelope do sinal derivado varia muito pouco. Colocando f_c
no flanco de um ressonante de Q alto, a mesma excursão de frequência produz
uma variação de envelope muito maior.
"""

import sys
import numpy as np
import matplotlib.pyplot as plt
from scipy import signal

saida = sys.argv[1] if len(sys.argv) > 1 else '../../Latex-slides/FM/figures/cap4'

plt.rcParams['font.size'] = 12
plt.rcParams['axes.grid'] = True

# Parâmetros
fm = 1000       # Hz (mensagem)
fc = 200e3      # Hz (portadora)
kf = 5000       # Hz/V
Am = 0.8        # V, desvio de pico 4 kHz
f0 = fc + 6e3   # Hz (ressonância do tanque, acima de f_c)
Q = 20
fs = 8e6
T = 4e-3

t = np.arange(0, T, 1/fs)
m_t = Am * np.cos(2*np.pi*fm*t)
s_fm = np.cos(2*np.pi*fc*t + 2*np.pi*kf*np.cumsum(m_t)/fs)
df = kf * Am

# Derivador puro, envelope normalizado pelo valor em f_c
env_d = np.abs(signal.hilbert(np.gradient(s_fm, 1/fs))) / (2*np.pi*fc)

# Flanco do ressonante, envelope normalizado por |H(f_c)|
b, a = signal.iirpeak(f0, Q, fs=fs)
y = signal.lfilter(b, a, s_fm)
_, Hc = signal.freqz(b, a, worN=[fc], fs=fs)
env_r = np.abs(signal.hilbert(y)) / np.abs(Hc[0])

# Recorte longe das bordas: transitório do filtro e da transformada de Hilbert
sel = (t >= 0.8e-3) & (t <= 3.8e-3)
tm = (t[sel] - 0.8e-3) * 1e3
env_d, env_r = env_d[sel], env_r[sel]

# Respostas em frequência, normalizadas em f_c
f = np.linspace(fc - 30e3, fc + 30e3, 600)
Hd = f / fc
_, Hr = signal.freqz(b, a, worN=f, fs=fs)
Hr = np.abs(Hr) / np.abs(Hc[0])

def var_pct(e):
    return 100 * (e.max() - e.min()) / 2

azul, verm, cinza = '#003B5C', '#B03A2E', '#787878'
fig, ax = plt.subplots(2, 2, figsize=(12, 6.6))

for k, (H, nome, cor) in enumerate([(Hd, r'Derivador: $|H_d(f)| = 2\pi f$', azul),
                                     (Hr, f'Ressonante: $f_0$ = {f0/1e3:.0f} kHz, Q = {Q}', verm)]):
    a_ = ax[0, k]
    a_.axvspan((fc - df)/1e3, (fc + df)/1e3, color=cor, alpha=0.12, label='excursão de $f_i(t)$')
    a_.plot(f/1e3, H, color=cor, lw=2.2)
    a_.axvline(fc/1e3, color=cinza, ls='--', lw=1.2)
    a_.set_ylim(0, 1.8)
    a_.set_xlim(f[0]/1e3, f[-1]/1e3)
    a_.set_title(nome)
    a_.set_xlabel('Frequência (kHz)')
    a_.set_ylabel('Ganho normalizado em $f_c$')
    a_.legend(loc='upper left', fontsize=10)

for k, (e, cor) in enumerate([(env_d, azul), (env_r, verm)]):
    a_ = ax[1, k]
    a_.plot(tm, e, color=cor, lw=2.2)
    a_.axhline(1, color=cinza, ls='--', lw=1.2)
    a_.set_ylim(0, 1.8)
    a_.set_xlim(0, 3)
    a_.set_xlabel('Tempo (ms)')
    a_.set_ylabel('Envelope normalizado')
    a_.text(0.5, 0.9, f'variação de pico ≈ ±{var_pct(e):.0f} %' if var_pct(e) >= 10
            else f'variação de pico ≈ ±{var_pct(e):.1f} %',
            transform=a_.transAxes, ha='center', va='top', color=cor, fontsize=12,
            bbox=dict(boxstyle='round', fc='white', ec=cor))
ax[1, 0].set_title('Envelope após o derivador')
ax[1, 1].set_title('Envelope após o flanco')

fig.tight_layout()
fig.savefig(f'{saida}/derivador_vs_flanco.pdf', bbox_inches='tight')
fig.savefig(f'{saida}/derivador_vs_flanco.png', dpi=200, bbox_inches='tight')
print(f'derivador: ±{var_pct(env_d):.2f} %   flanco: ±{var_pct(env_r):.1f} %')
