#!/usr/bin/env python3
"""
Gera a figura ilustrativa do Criterio de Nyquist: replicas do espectro
P(f) espacadas de 1/T somam-se a uma constante T (zero ISI).

Saida: ../nyquist_fold_1.pdf  -> espectro P(f) (uma replica)
       ../nyquist_fold_2.pdf  -> replicas vizinhas k = -1, 0, +1
       ../nyquist_fold_3.pdf  -> soma das replicas = T (constante)

Uso: python gen_nyquist_fold_figures.py
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
    'axes.grid': True,
    'grid.alpha': 0.3,
})

UNB_BLUE  = '#003B5C'
UNB_GREEN = '#006633'
UNB_GOLD  = '#F2A900'
RED       = '#C0392B'
PURPLE    = '#8E44AD'
TEAL      = '#16A085'


def raised_cosine_freq(f, T, alpha):
    """Espectro do cosseno levantado P(f), com pico T."""
    P = np.zeros_like(f)
    fa = np.abs(f)
    f1 = (1 - alpha) / (2 * T)
    f2 = (1 + alpha) / (2 * T)
    flat = fa <= f1
    roll = (fa > f1) & (fa <= f2)
    P[flat] = T
    P[roll] = (T / 2.0) * (1 + np.cos((np.pi * T / alpha) * (fa[roll] - f1)))
    return P


T = 1.0
alpha = 0.5
f = np.linspace(-2.2 / T, 2.2 / T, 4000)
P0 = raised_cosine_freq(f, T, alpha)

# replicas vizinhas
Pm1 = raised_cosine_freq(f + 1.0 / T, T, alpha)
Pp1 = raised_cosine_freq(f - 1.0 / T, T, alpha)
Pm2 = raised_cosine_freq(f + 2.0 / T, T, alpha)
Pp2 = raised_cosine_freq(f - 2.0 / T, T, alpha)
Psum = Pm2 + Pm1 + P0 + Pp1 + Pp2

f1 = (1 - alpha) / (2 * T)
f2 = (1 + alpha) / (2 * T)


def base_axes():
    fig, ax = plt.subplots(figsize=(7.2, 3.4))
    ax.set_xlabel(r'$f$  (em unidades de $1/T$)')
    ax.set_ylabel(r'$P(f)$')
    ax.set_xlim(-2.2 / T, 2.2 / T)
    ax.set_ylim(0, 1.35 * T)
    ax.set_xticks([-2/T, -1/T, -1/(2*T), 0, 1/(2*T), 1/T, 2/T])
    ax.set_xticklabels([r'$-2/T$', r'$-1/T$', r'$-\frac{1}{2T}$', '0',
                        r'$\frac{1}{2T}$', r'$1/T$', r'$2/T$'])
    ax.set_yticks([0, T])
    ax.set_yticklabels(['0', r'$T$'])
    return fig, ax


# ---------------------------------------------------------------------------
# Figura 1: uma replica
# ---------------------------------------------------------------------------
fig, ax = base_axes()
ax.plot(f, P0, color=UNB_BLUE, lw=2.4, label=r'$P(f)$')
ax.axvline(f2, color='0.6', ls=':', lw=1)
ax.axvline(-f2, color='0.6', ls=':', lw=1)
ax.annotate(r'$\frac{1+\alpha}{2T}$', xy=(f2, 0), xytext=(f2 + 0.06, 0.12 * T),
            color='0.4', fontsize=10)
ax.legend(loc='upper right', frameon=False)
fig.tight_layout()
fig.savefig('../nyquist_fold_1.pdf', bbox_inches='tight')
plt.close(fig)

# ---------------------------------------------------------------------------
# Figura 2: replicas vizinhas espacadas de 1/T
# ---------------------------------------------------------------------------
fig, ax = base_axes()
ax.plot(f, P0, color=UNB_BLUE, lw=2.4, label=r'$P(f)$')
ax.plot(f, Pp1, color=RED, lw=1.8, ls='--', label=r'$P(f \mp 1/T)$')
ax.plot(f, Pm1, color=RED, lw=1.8, ls='--')
ax.plot(f, Pp2, color='0.6', lw=1.2, ls='--')
ax.plot(f, Pm2, color='0.6', lw=1.2, ls='--')
# regiao de superposicao
ax.axvspan(f1, f2, color=UNB_GOLD, alpha=0.18)
ax.axvspan(-f2, -f1, color=UNB_GOLD, alpha=0.18)
ax.annotate('superposição', xy=(0.5 / T, 0.5 * T),
            xytext=(0.62 / T, 1.05 * T), color='0.35', fontsize=10,
            arrowprops=dict(arrowstyle='->', color='0.5', lw=1))
ax.legend(loc='upper right', frameon=False)
fig.tight_layout()
fig.savefig('../nyquist_fold_2.pdf', bbox_inches='tight')
plt.close(fig)

# ---------------------------------------------------------------------------
# Figura 3: soma das replicas = T (constante)
# ---------------------------------------------------------------------------
fig, ax = base_axes()
ax.plot(f, P0, color=UNB_BLUE, lw=1.6, alpha=0.55)
ax.plot(f, Pp1, color=RED, lw=1.2, ls='--', alpha=0.55)
ax.plot(f, Pm1, color=RED, lw=1.2, ls='--', alpha=0.55)
ax.plot(f, Pp2, color='0.6', lw=1.0, ls='--', alpha=0.5)
ax.plot(f, Pm2, color='0.6', lw=1.0, ls='--', alpha=0.5)
ax.plot(f, Psum, color=UNB_GREEN, lw=3.0,
        label=r'$\sum_k P(f - k/T) = T$')
ax.axhline(T, color=UNB_GREEN, ls=':', lw=1)
ax.legend(loc='upper right', frameon=False)
fig.tight_layout()
fig.savefig('../nyquist_fold_3.pdf', bbox_inches='tight')
plt.close(fig)

print('Figuras nyquist_fold_1/2/3.pdf geradas.')
