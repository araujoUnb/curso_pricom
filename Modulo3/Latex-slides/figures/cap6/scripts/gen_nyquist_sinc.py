#!/usr/bin/env python3
"""
Gera a figura do pulso sinc de Nyquist (Q24 b), conectando tempo e frequencia.

Painel esquerdo: p(t)=sinc(t/T) tem cruzamentos por zero em t=nT (n!=0): ISI
nula nos instantes de amostragem.
Painel direito: P(f)=T*rect(fT) e suas replicas espacadas de 1/T se encaixam
(brick-wall) e somam a constante T -> satisfaz o criterio de Nyquist. Banda
W=1/(2T).

Saida: ../nyquist_sinc.pdf

Uso: python gen_nyquist_sinc.py
"""

import numpy as np
import matplotlib.pyplot as plt

plt.rcParams.update({
    'font.size': 11,
    'font.family': 'serif',
    'axes.labelsize': 10,
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

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9.4, 3.4))

# ---- Painel 1: p(t)=sinc(t/T) -----------------------------------------
t = np.linspace(-4, 4, 2000)
p = np.sinc(t)               # np.sinc(t)=sin(pi t)/(pi t) = sinc(t/T), T=1
ax1.axhline(0, color='0.6', lw=0.7)
ax1.plot(t, p, color=UNB_BLUE, lw=2.2)
n = np.arange(-4, 5)
ax1.plot(n[n != 0], np.zeros_like(n[n != 0]), 'o', color=RED, ms=6, zorder=5)
ax1.plot(0, 1, 'o', color=UNB_GREEN, ms=7, zorder=5)
ax1.annotate('ISI nula:\n$p(nT)=0,\\ n\\neq0$', xy=(2, 0), xytext=(1.2, 0.55),
             color=RED, fontsize=9,
             arrowprops=dict(arrowstyle='->', color=RED, lw=1))
ax1.set_title(r'$p(t)=\mathrm{sinc}(t/T)$')
ax1.set_xlabel(r'$t/T$')
ax1.set_xticks(np.arange(-4, 5, 2))
ax1.set_yticks([0, 1])
ax1.set_ylim(-0.35, 1.15)

# ---- Painel 2: P(f)=T rect(fT) e replicas somam T ---------------------
T = 1.0
f = np.linspace(-2.6, 2.6, 4000)


def rect(x):
    return (np.abs(x) < 0.5).astype(float)


total = np.zeros_like(f)
for k in range(-3, 4):
    rep = T * rect((f - k / T) * T)
    total += rep
    col = UNB_BLUE if k == 0 else '0.6'
    lw = 2.4 if k == 0 else 1.2
    ax2.plot(f, rep + (0.0 if k == 0 else 0.0), color=col, lw=lw,
             ls='-' if k == 0 else '--')

ax2.plot(f, total, color=UNB_GREEN, lw=1.6)
ax2.axhline(T, color=UNB_GREEN, ls=':', lw=1)
ax2.text(0, 1.16 * T, r'$\sum_k P(f-k/T)=T$', color=UNB_GREEN, ha='center',
         fontsize=9)
# banda W=1/(2T)
ax2.axvline(1 / (2 * T), color='0.5', ls=':', lw=1)
ax2.annotate(r'$W=\frac{1}{2T}$', xy=(1 / (2 * T), 0),
             xytext=(1.25, 0.42 * T), color='0.3', ha='left', fontsize=9,
             arrowprops=dict(arrowstyle='->', color='0.5', lw=0.9))

ax2.set_title(r'$P(f)=T\,\mathrm{rect}(fT)$ e réplicas')
ax2.set_xlabel(r'$f$ (em $1/T$)')
ax2.set_xticks([-2, -1, 0, 1, 2])
ax2.set_xticklabels([r'$-2/T$', r'$-1/T$', '0', r'$1/T$', r'$2/T$'])
ax2.set_yticks([0, T])
ax2.set_yticklabels(['0', r'$T$'])
ax2.set_ylim(0, 1.35 * T)

fig.tight_layout()
fig.savefig('../nyquist_sinc.pdf', bbox_inches='tight')
plt.close(fig)

print('Figura nyquist_sinc.pdf gerada.')
