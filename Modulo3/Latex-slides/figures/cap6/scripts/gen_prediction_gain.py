#!/usr/bin/env python3
"""
Gera a figura do ganho de predicao do DPCM de 1a ordem (Q20):
G_p = 1/(1 - rho^2), em dB, versus o coeficiente de correlacao rho.
Marca os casos rho=0,9 e rho=0,95 usados nos itens (b) e (c).

Saida: ../prediction_gain.pdf

Uso: python gen_prediction_gain.py
"""

import numpy as np
import matplotlib.pyplot as plt

plt.rcParams.update({
    'font.size': 11,
    'font.family': 'serif',
    'axes.labelsize': 11,
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

rho = np.linspace(0, 0.985, 500)
Gp_db = 10 * np.log10(1.0 / (1.0 - rho**2))

fig, ax = plt.subplots(figsize=(6.2, 3.4))

ax.plot(rho, Gp_db, color=UNB_BLUE, lw=2.6)

for r, col in [(0.9, UNB_GREEN), (0.95, RED)]:
    g = 10 * np.log10(1.0 / (1.0 - r**2))
    ax.plot([r, r], [0, g], color=col, lw=1.2, ls='--')
    ax.plot([0, r], [g, g], color=col, lw=1.2, ls='--')
    ax.plot(r, g, 'o', color=col, ms=6)
    ax.annotate(rf'$\rho={r}$: $G_p\approx{g:.1f}$ dB',
                xy=(r, g), xytext=(0.12, g + 0.4), color=col, fontsize=9)

ax.text(0.05, 13.5, r'$G_p=\dfrac{1}{1-\rho^{2}}$', fontsize=13,
        color=UNB_BLUE)

ax.set_xlim(0, 1.0)
ax.set_ylim(0, 16)
ax.set_xlabel(r'coeficiente de correlação  $\rho$')
ax.set_ylabel(r'ganho de predição  $G_p$ (dB)')

# eixo secundario: bits economizados = G_p[dB] / 6,02
ax2 = ax.twinx()
ax2.set_ylim(0, 16 / 6.02)
ax2.set_ylabel(r'bits economizados $=G_p[\mathrm{dB}]/6{,}02$', color='0.35')
ax2.tick_params(axis='y', labelcolor='0.35')
ax2.spines['top'].set_visible(False)

fig.tight_layout()
fig.savefig('../prediction_gain.pdf', bbox_inches='tight')
plt.close(fig)

print('Figura prediction_gain.pdf gerada.')
