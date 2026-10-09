#!/usr/bin/env python3
"""
Gera a figura didatica da faixa dinamica da voz (companding). A amplitude da
fala varia de trechos fortes a trechos fracos numa razao ~100:1, ou seja
20*log10(100) = 40 dB. Um quantizador uniforme dimensionado para o pico
deixa os trechos fracos com pouquissimos niveis -> baixa qualidade.

Saida: ../voice_dynamic_range.pdf

Uso: python gen_voice_dynamic_range.py
"""

import numpy as np
import matplotlib.pyplot as plt

plt.rcParams.update({
    'font.size': 11,
    'font.family': 'serif',
    'axes.labelsize': 11,
    'axes.titlesize': 11,
    'xtick.labelsize': 9,
    'ytick.labelsize': 9,
    'figure.dpi': 150,
    'text.usetex': False,
    'axes.spines.top': False,
    'axes.spines.right': False,
})

UNB_BLUE  = '#003B5C'
UNB_GREEN = '#006633'
UNB_GOLD  = '#F2A900'
RED       = '#C0392B'

# eixo de tempo
t = np.linspace(0, 3.0, 6000)

# envelope: trecho forte (grito) e trecho fraco (sussurro), razao 100:1
env = np.zeros_like(t)
strong = (t > 0.3) & (t < 1.2)
weak = (t > 1.8) & (t < 2.7)
env[strong] = 1.0 * np.sin(np.pi * (t[strong] - 0.3) / 0.9)
env[weak] = 0.01 * np.sin(np.pi * (t[weak] - 1.8) / 0.9)

# portadora "vozeada": mistura de harmonicos
carrier = (np.sin(2 * np.pi * 18 * t)
           + 0.5 * np.sin(2 * np.pi * 36 * t)
           + 0.3 * np.sin(2 * np.pi * 54 * t))
carrier /= np.max(np.abs(carrier))
sig = env * carrier

fig, ax = plt.subplots(figsize=(8.2, 3.4))

# niveis de um quantizador uniforme (dimensionado para o pico)
for lv in np.linspace(-1, 1, 9):
    ax.axhline(lv, color='0.85', lw=0.7, zorder=0)

ax.plot(t, sig, color=UNB_BLUE, lw=0.9, zorder=3)

# marcadores de amplitude
Amax, Amin = 1.0, 0.01
ax.annotate('', xy=(0.75, Amax), xytext=(0.75, -Amax),
            arrowprops=dict(arrowstyle='<->', color=RED, lw=1.3))
ax.text(0.80, 0.55, r'$A_{\max}$', color=RED, fontsize=10)
ax.text(2.25, 0.14, r'$A_{\min}$', color=UNB_GREEN, fontsize=10, ha='center')

ax.text(0.75, 1.18, 'voz forte', ha='center', color=UNB_BLUE, fontsize=9.5)
ax.text(2.25, 1.18, 'voz fraca', ha='center', color=UNB_GREEN, fontsize=9.5)

# caixa com o calculo dos 40 dB
txt = (r'$\mathrm{FD}=20\log_{10}\dfrac{A_{\max}}{A_{\min}}'
       r'=20\log_{10}(100)\approx 40$ dB')
ax.text(1.5, -1.62, txt, ha='center', va='top', fontsize=11, color='0.15',
        bbox=dict(boxstyle='round,pad=0.35', fc=UNB_GOLD, ec='0.5',
                  alpha=0.25))

ax.set_xlim(0, 3.0)
ax.set_ylim(-1.35, 1.35)
ax.set_xlabel(r'$t$')
ax.set_ylabel('amplitude')
ax.set_yticks([-1, 0, 1])
ax.set_xticks([])

fig.tight_layout()
fig.savefig('../voice_dynamic_range.pdf', bbox_inches='tight')
plt.close(fig)

print('Figura voice_dynamic_range.pdf gerada.')
