#!/usr/bin/env python3
"""
Gera a curva do compressor mu-law (companding, Q16 bonus). O compressor
logaritmico y=C(x) tem grande inclinacao para |x| pequeno (amplifica sinais
fracos) e pequena inclinacao para |x| grande. Depois um quantizador uniforme
em y equivale a passos finos para sinais fracos e grossos para fortes.

Saida: ../mulaw_curve.pdf

Uso: python gen_mulaw_curve.py
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


def mulaw(x, mu):
    return np.sign(x) * np.log1p(mu * np.abs(x)) / np.log1p(mu)


x = np.linspace(-1, 1, 2000)

fig, ax = plt.subplots(figsize=(5.4, 4.4))

# identidade (sem companding)
ax.plot(x, x, color='0.6', lw=1.3, ls='--', label='sem companding')
# mu-law
for mu, col in [(255, UNB_BLUE)]:
    ax.plot(x, mulaw(x, mu), color=col, lw=2.6, label=r'$\mu$-law ($\mu=255$)')

# niveis uniformes de saida projetados no eixo x
ylev = np.linspace(-1, 1, 17)
# inverso aproximado: acha x tal que C(x)=ylev
xr = np.linspace(-1, 1, 20000)
yr = mulaw(xr, 255)
xlev = np.interp(ylev, yr, xr)
ax.hlines(ylev, -1, xlev, color='0.85', lw=0.6, zorder=0)
ax.vlines(xlev, -1, ylev, color='0.85', lw=0.6, zorder=0)

ax.annotate('sinais fracos:\ngrande inclinação\n(passos finos)',
            xy=(0.06, mulaw(0.06, 255)), xytext=(0.28, -0.35),
            color=UNB_GREEN, fontsize=9,
            arrowprops=dict(arrowstyle='->', color=UNB_GREEN, lw=1))
ax.annotate('sinais fortes:\npequena inclinação\n(passos grossos)',
            xy=(0.8, mulaw(0.8, 255)), xytext=(-0.9, 0.55),
            color=RED, fontsize=9,
            arrowprops=dict(arrowstyle='->', color=RED, lw=1))

ax.set_xlim(-1, 1)
ax.set_ylim(-1.05, 1.05)
ax.set_xlabel(r'entrada  $x$')
ax.set_ylabel(r'saída  $y=C(x)$')
ax.axhline(0, color='0.6', lw=0.7)
ax.axvline(0, color='0.6', lw=0.7)
ax.legend(loc='lower right', frameon=False, fontsize=9)

fig.tight_layout()
fig.savefig('../mulaw_curve.pdf', bbox_inches='tight')
plt.close(fig)

print('Figura mulaw_curve.pdf gerada.')
