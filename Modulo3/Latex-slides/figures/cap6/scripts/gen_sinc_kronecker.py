#!/usr/bin/env python3
"""
Gera a figura do nucleo de interpolacao sinc(m-n) avaliado nos inteiros:
sinc(0)=1 e sinc(k)=0 para todo inteiro k != 0, isto e, sinc(m-n)=delta[m-n].

Mostra a curva continua sinc(u) com os cruzamentos por zero nos inteiros
nao nulos destacados e a amostra unitaria em u=0.

Saida: ../sinc_kronecker.pdf

Uso: python gen_sinc_kronecker.py
"""

import numpy as np
import matplotlib.pyplot as plt

plt.rcParams.update({
    'font.size': 11,
    'font.family': 'serif',
    'axes.labelsize': 12,
    'axes.titlesize': 12,
    'xtick.labelsize': 10,
    'ytick.labelsize': 10,
    'figure.dpi': 150,
    'text.usetex': False,
    'axes.spines.top': False,
    'axes.spines.right': False,
    'axes.grid': False,
})

UNB_BLUE  = '#003B5C'
UNB_GREEN = '#006633'
UNB_GOLD  = '#F2A900'
RED       = '#C0392B'


def sinc(u):
    return np.sinc(u)   # np.sinc(u) = sin(pi u)/(pi u)


K = 5
u = np.linspace(-K - 0.4, K + 0.4, 4000)
y = sinc(u)

fig, ax = plt.subplots(figsize=(6.4, 3.0))

# curva continua
ax.plot(u, y, color=UNB_BLUE, lw=2.2, zorder=3)

# eixos
ax.axhline(0, color='0.4', lw=0.9, zorder=1)
ax.axhline(1, color='0.85', lw=0.8, ls=':', zorder=1)

# amostras nos inteiros: 1 em 0, 0 nos demais
ints = np.arange(-K, K + 1)
vals = sinc(ints)
# linhas de haste (stem) para enfatizar os valores amostrados
for k, v in zip(ints, vals):
    ax.plot([k, k], [0, v], color='0.75', lw=1.0, zorder=2)

# zeros nos inteiros nao nulos
nz = ints[ints != 0]
ax.plot(nz, sinc(nz), 'o', color=RED, ms=6, zorder=4,
        label=r'$\mathrm{sinc}(k)=0,\ k\neq 0$')
# amostra unitaria em 0
ax.plot(0, 1, 'o', color=UNB_GREEN, ms=8, zorder=5,
        label=r'$\mathrm{sinc}(0)=1$')

ax.annotate(r'$\mathrm{sinc}(m-n)=\delta[m-n]$', xy=(0, 1),
            xytext=(2.1, 0.82), fontsize=11, color=UNB_GREEN, ha='left',
            arrowprops=dict(arrowstyle='->', color=UNB_GREEN, lw=1))

ax.set_xlim(-K - 0.4, K + 0.4)
ax.set_ylim(-0.32, 1.18)
ax.set_xlabel(r'$u=m-n$')
ax.set_xticks(ints)
ax.set_yticks([0, 1])
ax.legend(loc='lower right', frameon=False, fontsize=9)

fig.tight_layout()
fig.savefig('../sinc_kronecker.pdf', bbox_inches='tight')
plt.close(fig)

print('Figura sinc_kronecker.pdf gerada.')
