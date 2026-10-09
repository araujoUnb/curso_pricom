#!/usr/bin/env python3
"""
Gera a figura didatica da sobrecarga de inclinacao na modulacao delta (Q18 a):
a escada da DM sobe no maximo delta por amostra (inclinacao delta*f_s). Se a
inclinacao maxima do sinal 2*pi*f0*A exceder isso, a escada nao acompanha o
sinal -> sobrecarga de inclinacao.

Dois paineis: esquerda delta*f_s < 2*pi*f0*A (sobrecarga); direita
delta*f_s >= 2*pi*f0*A (acompanha).

Saida: ../slope_overload.pdf

Uso: python gen_slope_overload.py
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

A = 1.0
f0 = 1.0
delta = 0.15


def dm_staircase(fs, tmax):
    n = int(np.round(fs * tmax))
    tn = np.arange(n + 1) / fs
    x = A * np.cos(2 * np.pi * f0 * tn)
    y = np.zeros_like(tn)
    for k in range(1, len(tn)):
        y[k] = y[k - 1] + delta * np.sign(x[k] - y[k - 1])
    return tn, x, y


tmax = 1.15
t = np.linspace(0, tmax, 2000)
xc = A * np.cos(2 * np.pi * f0 * t)

fig, axes = plt.subplots(1, 2, figsize=(9.2, 3.3), sharey=True)

configs = [
    (18.0, r'$\delta f_s < 2\pi f_0 A$', 'sobrecarga de inclinação', RED),
    (80.0, r'$\delta f_s \geq 2\pi f_0 A$', 'a escada acompanha', UNB_GREEN),
]

for ax, (fs, cond, note, col) in zip(axes, configs):
    tn, xn, yn = dm_staircase(fs, tmax)
    ax.plot(t, xc, color=UNB_BLUE, lw=2.0, label=r'$x(t)=A\cos(2\pi f_0 t)$')
    ax.step(tn, yn, where='post', color=col, lw=1.8,
            label='escada DM')
    ax.axhline(0, color='0.6', lw=0.7)
    ax.set_title(cond, fontsize=11, color=col)
    ax.set_xlabel(r'$t$  (períodos de $f_0$)')
    ax.text(0.5, -1.28, note, transform=ax.transData, ha='center',
            va='top', color=col, fontsize=9.5)
    ax.set_ylim(-1.5, 1.5)
    ax.set_xlim(0, tmax)
    ax.legend(loc='upper right', frameon=False, fontsize=8)

# no painel de sobrecarga, marca a regiao onde a escada fica para tras
tn, xn, yn = dm_staircase(18.0, tmax)
axes[0].annotate('escada não\nsegue a descida', xy=(0.28, 0.1),
                 xytext=(0.36, 0.95), color=RED, fontsize=8.5,
                 arrowprops=dict(arrowstyle='->', color=RED, lw=1))

axes[0].set_ylabel('amplitude')
fig.tight_layout()
fig.savefig('../slope_overload.pdf', bbox_inches='tight')
plt.close(fig)

print('Figura slope_overload.pdf gerada.')
