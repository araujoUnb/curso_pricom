#!/usr/bin/env python3
"""
Gera o desenho de contexto do tronco E1 (Q12 c): multiplos canais de voz de
64 kb/s sao combinados por multiplexacao por divisao de tempo (TDM) em um
unico tronco E1 a 2,048 Mb/s, e demultiplexados no destino.

Ajuda o aluno a entender o que e o "tronco E1" antes da derivacao numerica.

Saida: ../e1_trunk.pdf

Uso: python gen_e1_trunk.py
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Polygon, FancyArrowPatch

plt.rcParams.update({
    'font.size': 11,
    'font.family': 'serif',
    'text.usetex': False,
})

UNB_BLUE  = '#003B5C'
UNB_GREEN = '#006633'
UNB_GOLD  = '#F2A900'
RED       = '#C0392B'

fig, ax = plt.subplots(figsize=(9.0, 4.0))

# ---- canais de entrada (esquerda) ---------------------------------------
labels = ['Canal 1', 'Canal 2', r'$\vdots$', 'Canal 30', 'sinaliz./sincr.']
ys = [3.4, 2.6, 1.9, 1.2, 0.4]
colors = [UNB_BLUE, UNB_BLUE, None, UNB_BLUE, UNB_GOLD]
x_ch = 0.2
for lab, y, c in zip(labels, ys, colors):
    if lab == r'$\vdots$':
        ax.text(x_ch + 0.6, y, lab, ha='center', va='center', fontsize=13,
                color='0.4')
        continue
    ax.add_patch(Rectangle((x_ch, y - 0.28), 1.5, 0.56, facecolor=c,
                           edgecolor='0.3', lw=1.0, alpha=0.9))
    tcol = 'black' if c == UNB_GOLD else 'white'
    ax.text(x_ch + 0.75, y, lab, ha='center', va='center', color=tcol,
            fontsize=8.5)
    # setas para o MUX
    ax.add_patch(FancyArrowPatch((x_ch + 1.5, y), (3.5, 2.0),
                 arrowstyle='->', mutation_scale=11, color='0.45', lw=1.0))

ax.text(x_ch + 0.75, 3.95, r'30 canais $\times$ 64 kb/s', ha='center',
        va='bottom', fontsize=9, color=UNB_BLUE)

# ---- MUX (trapezio) ------------------------------------------------------
mux = Polygon([(3.5, 0.4), (4.4, 1.1), (4.4, 2.9), (3.5, 3.6)],
              closed=True, facecolor=UNB_GREEN, edgecolor='0.2', alpha=0.9)
ax.add_patch(mux)
ax.text(3.95, 2.0, 'MUX\nTDM', ha='center', va='center', color='white',
        fontsize=9)

# ---- tronco E1 ----------------------------------------------------------
ax.add_patch(FancyArrowPatch((4.4, 2.0), (6.6, 2.0), arrowstyle='-',
             mutation_scale=1, color=RED, lw=3.2))
ax.text(5.5, 2.32, 'Tronco E1', ha='center', va='bottom', color=RED,
        fontsize=11)
ax.text(5.5, 1.68, r'$2{,}048$ Mb/s', ha='center', va='top', color=RED,
        fontsize=10)

# ---- DEMUX (trapezio) ---------------------------------------------------
demux = Polygon([(6.6, 1.1), (7.5, 0.4), (7.5, 3.6), (6.6, 2.9)],
                closed=True, facecolor=UNB_GREEN, edgecolor='0.2', alpha=0.9)
ax.add_patch(demux)
ax.text(7.05, 2.0, 'DEMUX', ha='center', va='center', color='white',
        fontsize=8.5)

# ---- saidas (direita) ---------------------------------------------------
for y in ys:
    if abs(y - 1.9) < 0.05:
        ax.text(8.4, y, r'$\vdots$', ha='center', va='center', fontsize=13,
                color='0.4')
        continue
    ax.add_patch(FancyArrowPatch((7.5, 2.0), (8.0, y), arrowstyle='->',
                 mutation_scale=11, color='0.45', lw=1.0))
    ax.add_patch(Rectangle((8.0, y - 0.28), 0.8, 0.56, facecolor='0.85',
                           edgecolor='0.4', lw=1.0))

ax.text(8.4, 3.95, '30 canais\nrecuperados', ha='center', va='bottom',
        fontsize=8.5, color='0.3')

ax.set_xlim(0, 9.0)
ax.set_ylim(-0.1, 4.5)
ax.axis('off')

fig.tight_layout()
fig.savefig('../e1_trunk.pdf', bbox_inches='tight')
plt.close(fig)

print('Figura e1_trunk.pdf gerada.')
