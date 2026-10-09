#!/usr/bin/env python3
"""
Compara o Criterio de Nyquist do cosseno levantado para dois valores de
roll-off. Em ambos os casos a soma das replicas vale T; o que muda e
apenas a largura da faixa de transicao (alpha/T).

Saida: ../rc_nyq_alpha.pdf  -> dois paineis, alpha pequeno e alpha grande

Uso: python gen_rc_nyquist_alpha.py
"""

import numpy as np
import matplotlib.pyplot as plt

plt.rcParams.update({
    'font.size': 11,
    'font.family': 'serif',
    'axes.labelsize': 12,
    'axes.titlesize': 12,
    'xtick.labelsize': 9,
    'ytick.labelsize': 10,
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

T = 1.0


def rc_freq(f, T, alpha):
    P = np.zeros_like(f)
    fa = np.abs(f)
    if alpha <= 0:
        P[fa <= 1.0 / (2 * T)] = T
        return P
    f1 = (1 - alpha) / (2 * T)
    f2 = (1 + alpha) / (2 * T)
    flat = fa <= f1
    roll = (fa > f1) & (fa <= f2)
    P[flat] = T
    P[roll] = (T / 2.0) * (1 + np.cos((np.pi * T / alpha) * (fa[roll] - f1)))
    return P


f = np.linspace(-0.15 / T, 1.2 / T, 4000)


def draw_panel(ax, alpha):
    P0 = rc_freq(f, T, alpha)
    P1 = rc_freq(f - 1.0 / T, T, alpha)
    # soma sobre varias replicas para ficar plana em toda a janela
    Psum = sum(rc_freq(f - k / T, T, alpha) for k in range(-2, 3))
    f1 = (1 - alpha) / (2 * T)
    f2 = (1 + alpha) / (2 * T)
    fN = 1.0 / (2 * T)

    ax.axvspan(f1, f2, color=UNB_GOLD, alpha=0.18)
    ax.axvline(fN, color='0.55', ls='--', lw=1)
    ax.plot(f, P0, color=UNB_BLUE, lw=1.8, alpha=0.7, label=r'$P(f)$')
    ax.plot(f, P1, color=RED, lw=1.6, ls='--', alpha=0.7, label=r'$P(f-1/T)$')
    ax.plot(f, Psum, color=UNB_GREEN, lw=3.0, label=r'$\sum_k P(f-k/T)=T$')
    ax.axhline(T, color=UNB_GREEN, ls=':', lw=1)

    ax.set_xlim(-0.15 / T, 1.2 / T)
    ax.set_ylim(0, 1.18 * T)
    ax.set_xlabel(r'$f$  (em unidades de $1/T$)')
    ax.set_xticks([0, f1, fN, f2, 1 / T])
    ax.set_xticklabels(['0', r'$\frac{1-\alpha}{2T}$', r'$\frac{1}{2T}$',
                        r'$\frac{1+\alpha}{2T}$', r'$\frac{1}{T}$'])
    ax.set_yticks([0, T / 2, T])
    ax.set_yticklabels(['0', r'$T/2$', r'$T$'])
    ax.set_title(rf'$\alpha = {alpha:g}$' +
                 rf'   (transição $= {alpha:g}/T$)', fontsize=12)
    # seta indicando a largura da transicao
    ax.annotate('', xy=(f1, 1.08 * T), xytext=(f2, 1.08 * T),
                arrowprops=dict(arrowstyle='<->', color='#9a7d00', lw=1.3))


fig, axes = plt.subplots(1, 2, figsize=(9.2, 3.5), sharey=True)
draw_panel(axes[0], 0.25)
draw_panel(axes[1], 0.75)
axes[0].set_ylabel(r'$P(f)$')
handles, labels = axes[0].get_legend_handles_labels()
fig.legend(handles, labels, loc='lower center', ncol=3, frameon=False,
           bbox_to_anchor=(0.5, -0.04), fontsize=10)
fig.tight_layout(rect=(0, 0.06, 1, 1))
fig.savefig('../rc_nyq_alpha.pdf', bbox_inches='tight')
plt.close(fig)
print('Figura rc_nyq_alpha.pdf gerada.')
