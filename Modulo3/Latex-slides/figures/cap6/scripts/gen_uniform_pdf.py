#!/usr/bin/env python3
"""
Gera a figura da densidade uniforme do erro de quantizacao:
p(e_q)=1/Delta em [-Delta/2, Delta/2] e zero fora. Ilustra o ponto de
partida do calculo da potencia do ruido P_q = Delta^2/12.

Saida: ../uniform_pdf.pdf

Uso: python gen_uniform_pdf.py
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

D = 2.0            # Delta (valor visual)
h = 1.0 / D        # altura 1/Delta

fig, ax = plt.subplots(figsize=(5.6, 3.0))

# retangulo da densidade uniforme
ax.fill_between([-D / 2, D / 2], 0, h, color=UNB_BLUE, alpha=0.18, zorder=2)
ax.plot([-D / 2, D / 2], [h, h], color=UNB_BLUE, lw=2.6, zorder=4)
# arestas verticais
ax.plot([-D / 2, -D / 2], [0, h], color=UNB_BLUE, lw=2.6, zorder=4)
ax.plot([D / 2, D / 2], [0, h], color=UNB_BLUE, lw=2.6, zorder=4)
# cauda zero
ax.plot([-1.6 * D / 2 * 1.7, -D / 2], [0, 0], color=UNB_BLUE, lw=2.6, zorder=4)
ax.plot([D / 2, 1.6 * D / 2 * 1.7], [0, 0], color=UNB_BLUE, lw=2.6, zorder=4)

# eixo horizontal
ax.axhline(0, color='0.4', lw=0.9, zorder=1)
# linha tracejada da altura
ax.plot([-D / 2, 0], [h, h], color='0.7', lw=0, zorder=1)
ax.annotate(r'$\frac{1}{\Delta}$', xy=(0, h), xytext=(0.12 * D, h + 0.06 * h),
            color=UNB_BLUE, fontsize=13, ha='left', va='bottom')

# marcadores do intervalo
ax.plot([-D / 2, D / 2], [0, 0], 'o', color=RED, ms=5, zorder=5)

ax.set_xlim(-1.7 * D / 2 * 1.7, 1.7 * D / 2 * 1.7)
ax.set_ylim(-0.12 * h, 1.35 * h)
ax.set_xlabel(r'$e_q$')
ax.set_ylabel(r'$p(e_q)$')
ax.set_xticks([-D / 2, 0, D / 2])
ax.set_xticklabels([r'$-\frac{\Delta}{2}$', '0', r'$\frac{\Delta}{2}$'])
ax.set_yticks([0, h])
ax.set_yticklabels(['0', r'$1/\Delta$'])

fig.tight_layout()
fig.savefig('../uniform_pdf.pdf', bbox_inches='tight')
plt.close(fig)

print('Figura uniform_pdf.pdf gerada.')
