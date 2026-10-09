#!/usr/bin/env python3
"""
Gera o desenho ilustrativo do quadro E1 (Q12 c): 32 intervalos de tempo (TS)
por quadro de 125 us. TS0 = sincronismo/alinhamento, TS16 = sinalizacao,
os 30 restantes = canais de voz, cada TS a 64 kb/s.

Saida: ../e1_frame.pdf

Uso: python gen_e1_frame.py
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

plt.rcParams.update({
    'font.size': 11,
    'font.family': 'serif',
    'text.usetex': False,
})

UNB_BLUE  = '#003B5C'
UNB_GREEN = '#006633'
UNB_GOLD  = '#F2A900'
RED       = '#C0392B'

fig, ax = plt.subplots(figsize=(9.2, 2.1))

N = 32
w = 1.0
h = 1.0

for ts in range(N):
    x = ts * w
    if ts == 0:
        fc, ec, tc = UNB_GOLD, '0.25', 'black'
    elif ts == 16:
        fc, ec, tc = RED, '0.25', 'white'
    else:
        fc, ec, tc = UNB_BLUE, '0.85', 'white'
    ax.add_patch(Rectangle((x, 0), w, h, facecolor=fc, edgecolor=ec, lw=1.0,
                           alpha=0.92, zorder=2))
    ax.text(x + w / 2, h / 2, str(ts), ha='center', va='center',
            color=tc, fontsize=7.5, zorder=3)

# chaves indicando os grupos de canais de voz
def brace(x0, x1, y, label, color):
    ax.annotate('', xy=(x0 + 0.05, y), xytext=(x1 - 0.05, y),
                arrowprops=dict(arrowstyle='<->', color=color, lw=1.2))
    ax.text((x0 + x1) / 2, y - 0.28, label, ha='center', va='top',
            color=color, fontsize=9)

brace(1, 16, -0.15, '15 canais de voz', UNB_BLUE)
brace(17, 32, -0.15, '15 canais de voz', UNB_BLUE)

# rotulos dos TS especiais
ax.annotate('TS0\nsincronismo', xy=(0.5, h), xytext=(0.5, h + 0.55),
            ha='center', va='bottom', color='0.15', fontsize=8.5,
            arrowprops=dict(arrowstyle='->', color='0.4', lw=1))
ax.annotate('TS16\nsinalização', xy=(16.5, h), xytext=(16.5, h + 0.55),
            ha='center', va='bottom', color=RED, fontsize=8.5,
            arrowprops=dict(arrowstyle='->', color=RED, lw=1))

# rotulo do quadro completo
ax.annotate('', xy=(0, -0.95), xytext=(N, -0.95),
            arrowprops=dict(arrowstyle='<->', color='0.3', lw=1.2))
ax.text(N / 2, -1.15, r'1 quadro = 32 TS $\times$ 8 bits = 125 $\mu$s'
        '   (cada TS a 64 kb/s)', ha='center', va='top',
        color='0.2', fontsize=9)

ax.set_xlim(-0.5, N + 0.5)
ax.set_ylim(-1.7, h + 1.35)
ax.axis('off')

fig.tight_layout()
fig.savefig('../e1_frame.pdf', bbox_inches='tight')
plt.close(fig)

print('Figura e1_frame.pdf gerada.')
