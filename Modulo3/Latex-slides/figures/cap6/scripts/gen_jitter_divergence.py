#!/usr/bin/env python3
"""
Gera a figura didatica da fragilidade do pulso sinc a jitter (Q24 c).

Painel esquerdo: com erro de sincronismo delta=eps/T, os termos de ISI valem
|sinc(k+delta)| ~ (eps/T)/|k|, isto e, decaem apenas como 1/k (envelope).
Painel direito: as somas parciais da serie harmonica sum 1/k crescem sem
limite (~ln N) -> a serie diverge, logo a ISI pode crescer sem limite.

Saida: ../jitter_divergence.pdf

Uso: python gen_jitter_divergence.py
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

# ---- Painel 1: |sinc(k+delta)| ~ 1/k ----------------------------------
delta = 0.15
k = np.arange(1, 13)
val = np.abs(np.sin(np.pi * delta) / (np.pi * (k + delta)))
env = np.abs(np.sin(np.pi * delta) / np.pi) / k

ax1.vlines(k, 0, val, color=UNB_BLUE, lw=2.0)
ax1.plot(k, val, 'o', color=UNB_BLUE, ms=5, label=r'$|\mathrm{sinc}(k+\delta)|$')
ax1.plot(k, env, '--', color=RED, lw=1.6,
         label=r'envelope $\dfrac{\epsilon/T}{k}\propto\dfrac{1}{k}$')
ax1.set_title(r'os termos caem só como $1/k$')
ax1.set_xlabel(r'$k$')
ax1.set_ylabel('amplitude do termo de ISI')
ax1.set_xticks(k[::2])
ax1.legend(loc='upper right', frameon=False, fontsize=8.5)

# ---- Painel 2: soma parcial da serie harmonica diverge ----------------
N = np.arange(1, 61)
S = np.cumsum(1.0 / N)
gamma = 0.5772156649
ax2.plot(N, S, color=UNB_GREEN, lw=2.4, label=r'$\sum_{k=1}^{N}\frac{1}{k}$')
ax2.plot(N, np.log(N) + gamma, '--', color='0.5', lw=1.4,
         label=r'$\ln N+\gamma$')
ax2.annotate(r'cresce sem limite $\to\infty$', xy=(55, S[54]),
             xytext=(20, 2.2), color=RED, fontsize=9,
             arrowprops=dict(arrowstyle='->', color=RED, lw=1))
ax2.set_title('a série harmônica diverge')
ax2.set_xlabel(r'$N$ (número de termos)')
ax2.set_ylabel('soma parcial')
ax2.set_xlim(0, 60)
ax2.set_ylim(0, 5)
ax2.legend(loc='lower right', frameon=False, fontsize=8.5)

fig.tight_layout()
fig.savefig('../jitter_divergence.pdf', bbox_inches='tight')
plt.close(fig)

print('Figura jitter_divergence.pdf gerada.')
