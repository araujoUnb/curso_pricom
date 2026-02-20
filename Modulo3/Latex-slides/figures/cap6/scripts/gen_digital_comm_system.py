#!/usr/bin/env python3
"""
Gera figura do sistema digital de comunicação (diagrama de blocos).
Saída: ../digital_comm_system.pdf

Uso: python gen_digital_comm_system.py
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

# ---------------------------------------------------------------------------
# Configurações de estilo
# ---------------------------------------------------------------------------
plt.rcParams.update({
    'font.size': 11,
    'font.family': 'serif',
    'axes.labelsize': 12,
    'axes.titlesize': 12,
    'figure.dpi': 150,
    'text.usetex': False,
})

UNB_BLUE  = '#003B5C'
UNB_GREEN = '#006633'
UNB_GOLD  = '#F2A900'
RED       = '#C0392B'
LIGHT_BLUE = '#D6EAF8'
LIGHT_GREEN = '#D5F5E3'
LIGHT_GOLD = '#FEF9E7'
LIGHT_RED = '#FADBD8'


def gen_digital_comm_system():
    fig, ax = plt.subplots(1, 1, figsize=(12, 4))
    ax.set_xlim(-0.5, 12.5)
    ax.set_ylim(-1.5, 2.5)
    ax.axis('off')

    # Block definitions: (x, y, width, height, label, color, bg_color)
    blocks = [
        (0.0,  0.5, 1.5, 1.0, 'Fonte\nDigital',      UNB_BLUE, LIGHT_BLUE),
        (2.0,  0.5, 1.5, 1.0, 'Codificador\nde Linha', UNB_GREEN, LIGHT_GREEN),
        (4.0,  0.5, 1.5, 1.0, 'Formatação\nde Pulso',  UNB_GOLD, LIGHT_GOLD),
        (6.0,  0.5, 1.5, 1.0, 'Canal',                  RED, LIGHT_RED),
        (8.0,  0.5, 1.5, 1.0, 'Receptor\n(Filtro\nCasado)', UNB_GREEN, LIGHT_GREEN),
        (10.0, 0.5, 1.5, 1.0, 'Decisor\n(Limiar)',      UNB_BLUE, LIGHT_BLUE),
    ]

    for (x, y, w, h, label, edge_color, bg_color) in blocks:
        rect = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.1",
                              facecolor=bg_color, edgecolor=edge_color, linewidth=2)
        ax.add_patch(rect)
        ax.text(x + w/2, y + h/2, label, ha='center', va='center',
                fontsize=10, fontweight='bold', color=edge_color)

    # Arrows between blocks
    arrow_style = dict(arrowstyle='->', color='black', lw=1.8,
                       connectionstyle='arc3,rad=0')
    positions = [(1.5, 1.0), (3.5, 1.0), (5.5, 1.0), (7.5, 1.0), (9.5, 1.0)]
    labels_arrow = [r'$\{a_k\}$', r'$s(t)$', r'', r'$r(t)$', r'$\hat{a}_k$']

    for (x, y), lab in zip(positions, labels_arrow):
        ax.annotate('', xy=(x + 0.5, y), xytext=(x, y),
                    arrowprops=arrow_style)
        if lab:
            ax.text(x + 0.25, y + 0.2, lab, ha='center', fontsize=10,
                    color='black')

    # Noise arrow into channel
    ax.annotate('', xy=(6.75, 0.5), xytext=(6.75, -0.5),
                arrowprops=dict(arrowstyle='->', color=RED, lw=1.5))
    ax.text(6.75, -0.8, r'Ruído $n(t)$', ha='center', fontsize=10,
            color=RED, fontweight='bold')

    # Output
    ax.annotate('', xy=(12.0, 1.0), xytext=(11.5, 1.0),
                arrowprops=arrow_style)
    ax.text(12.2, 1.0, r'$\hat{a}_k$', fontsize=11, va='center')

    # Title
    ax.text(6.0, 2.2, 'Sistema de Comunicação Digital em Banda Base',
            ha='center', fontsize=13, fontweight='bold', color=UNB_BLUE)

    plt.tight_layout()
    plt.savefig('../digital_comm_system.pdf', bbox_inches='tight')
    plt.close()
    print("  [OK] digital_comm_system.pdf")


if __name__ == '__main__':
    print("Gerando diagrama do sistema digital...")
    gen_digital_comm_system()
    print("Concluído!\n")
