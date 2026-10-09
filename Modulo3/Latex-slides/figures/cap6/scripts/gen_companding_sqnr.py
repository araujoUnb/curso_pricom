#!/usr/bin/env python3
"""
Gera a figura didatica do SQNR vs nivel do sinal (companding, Q16 bonus).
Com quantizacao uniforme o SQNR cresce ~1 dB por dB de nivel (ruido fixo,
potencia do sinal variavel): sinais fracos ficam ruins. Com companding
mu-law o SQNR fica aproximadamente constante em uma ampla faixa dinamica.

Saida: ../companding_sqnr.pdf

Uso: python gen_companding_sqnr.py
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

# nivel de entrada em dB relativo ao fundo de escala
level_db = np.linspace(-50, 0, 500)

# uniforme: SQNR cresce 1 dB por dB (ruido de quantizacao fixo)
sqnr_uniform = 50 + level_db          # em 0 dBFS chega a ~50 dB (8 bits)

# companded: aproximadamente constante em ampla faixa
sqnr_comp = 38 + 4 * (1 - np.exp((level_db) / 12.0))
sqnr_comp = np.clip(sqnr_comp, None, 40)

fig, ax = plt.subplots(figsize=(6.6, 3.6))

# faixa dinamica da voz (~40 dB)
ax.axvspan(-40, 0, color=UNB_GOLD, alpha=0.12)
ax.text(-28, 4, 'faixa dinâmica da voz $\\approx 40$ dB', ha='center',
        color='0.35', fontsize=9)

ax.plot(level_db, sqnr_uniform, color=RED, lw=2.4,
        label='quantização uniforme')
ax.plot(level_db, sqnr_comp, color=UNB_GREEN, lw=2.4,
        label=r'companding $\mu$-law')

ax.annotate('sinais fracos\nficam ruins', xy=(-40, 10),
            xytext=(-33, 30), color=RED, fontsize=9,
            arrowprops=dict(arrowstyle='->', color=RED, lw=1))
ax.annotate('SQNR $\\approx$ constante', xy=(-30, sqnr_comp[100]),
            xytext=(-30, 47), color=UNB_GREEN, fontsize=9,
            arrowprops=dict(arrowstyle='->', color=UNB_GREEN, lw=1))

ax.set_xlim(-50, 0)
ax.set_ylim(0, 55)
ax.set_xlabel('nível do sinal (dB rel. ao fundo de escala)')
ax.set_ylabel('SQNR (dB)')
ax.legend(loc='lower right', frameon=False, fontsize=9)

fig.tight_layout()
fig.savefig('../companding_sqnr.pdf', bbox_inches='tight')
plt.close(fig)

print('Figura companding_sqnr.pdf gerada.')
