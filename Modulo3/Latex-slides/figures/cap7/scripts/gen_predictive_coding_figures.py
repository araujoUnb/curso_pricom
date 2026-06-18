#!/usr/bin/env python3
"""
Gera figuras de codificacao preditiva (Modulacao Delta) para os slides.
Saida: ../dm_tracking.pdf

Uso: python gen_predictive_coding_figures.py
"""

import numpy as np
import matplotlib.pyplot as plt

plt.rcParams.update({
    'font.size': 11,
    'font.family': 'serif',
    'axes.labelsize': 12,
    'figure.dpi': 150,
    'text.usetex': False,
    'axes.spines.top': False,
    'axes.spines.right': False,
    'axes.grid': True,
    'grid.alpha': 0.3,
})

UNB_BLUE  = '#003B5C'
UNB_GREEN = '#006633'
UNB_GOLD  = '#F2A900'
RED       = '#C0392B'


def gen_dm_tracking():
    # sinal contInuo: x(t) = -0.85 cos(2 pi t)  (lento nos picos, rApido no meio)
    t = np.linspace(0, 1, 3000)
    x = -0.85 * np.cos(2 * np.pi * t)

    # Modulacao Delta
    fs = 32                       # taxa de amostragem (sobreamostrado)
    Ts = 1 / fs
    tk = np.arange(0, 1 + Ts / 2, Ts)
    xk = -0.85 * np.cos(2 * np.pi * tk)
    delta = 0.11                  # passo (delta/Ts = 3.52 < pico de inclinacao 5.34)

    xhat = np.zeros(len(tk))
    acc = -0.85
    for i in range(len(tk)):
        if xk[i] > acc:
            acc += delta
        else:
            acc -= delta
        xhat[i] = acc

    fig, ax = plt.subplots(figsize=(9, 3.2))
    ax.plot(t, x, color=UNB_BLUE, linewidth=2.2, label=r'sinal $x(t)$')
    ax.step(tk, xhat, where='post', color=UNB_GREEN, linewidth=1.8,
            label='aproximacao DM (escada)')
    ax.set_ylim(-1.15, 1.15)
    ax.set_xlim(0, 1)
    ax.set_xlabel(r'tempo ($t$)')
    ax.set_ylabel('amplitude')
    ax.axhline(0, color='black', linewidth=0.5)
    ax.legend(loc='lower center', fontsize=9, ncol=2)

    # anotacao: sobrecarga de inclinacao (subida ingreme ~ t=0.25)
    ax.annotate('sobrecarga de\ninclinacao',
                xy=(0.25, 0.0), xytext=(0.36, -0.65),
                fontsize=9, color=RED, ha='center',
                arrowprops=dict(arrowstyle='->', color=RED, lw=1.5))
    # anotacao: ruido granular (pico achatado ~ t=0.5)
    ax.annotate('ruido granular',
                xy=(0.52, 0.82), xytext=(0.72, 0.30),
                fontsize=9, color=UNB_GOLD, ha='center',
                arrowprops=dict(arrowstyle='->', color=UNB_GOLD, lw=1.5))

    plt.tight_layout()
    plt.savefig('../dm_tracking.pdf', bbox_inches='tight')
    plt.close()
    print("  [OK] dm_tracking.pdf")


if __name__ == '__main__':
    print("Gerando figuras de codificacao preditiva...")
    gen_dm_tracking()
    print("Concluido!\n")
