#!/usr/bin/env python3
"""
Gera a figura ilustrativa da reconstrucao ideal (Q1 b): o espectro amostrado
G_s(f)=f_s\\sum_k G(f-kf_s) possui replicas espacadas de f_s. Com f_s>2W as
replicas nao se sobrepoem e o filtro passa-baixa ideal
H(f)=(1/f_s) rect(f/2W) isola a replica central, recuperando G(f).

Saida: ../reconstrucao_lpf.pdf

Uso: python gen_reconstrucao_lpf.py
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


def base_spectrum(f, W):
    """Espectro de banda limitada G(f): meio cosseno suave, pico 1, banda W."""
    G = np.zeros_like(f)
    inside = np.abs(f) <= W
    G[inside] = 0.5 * (1 + np.cos(np.pi * f[inside] / W))
    return G


W = 1.0            # banda do sinal
fs = 3.0 * W       # taxa de amostragem (f_s > 2W)
peak = fs          # replicas de G_s tem pico f_s * max(G) = f_s

f = np.linspace(-2.2 * fs, 2.2 * fs, 6000)

# G_s(f) = f_s * soma das replicas de G(f - k f_s)
Gs = np.zeros_like(f)
for k in range(-3, 4):
    Gs += peak * base_spectrum(f - k * fs, W)

# replica central isolada (recuperada)
Gc = peak * base_spectrum(f, W)

fig, ax = plt.subplots(figsize=(5.6, 3.2))

# replicas laterais em cinza
ax.plot(f, Gs, color='0.55', lw=1.6, label=r'$G_s(f)=f_s\sum_k G(f-kf_s)$')
# replica central destacada
ax.fill_between(f, 0, Gc, color=UNB_BLUE, alpha=0.18)
ax.plot(f, Gc, color=UNB_BLUE, lw=2.4)

# filtro passa-baixa ideal H(f): rect de largura 2W, altura f_s (escala visual)
Hh = peak * 1.06
ax.plot([-2.2 * fs, -W], [0, 0], color=RED, lw=2.2, ls='--')
ax.plot([-W, -W], [0, Hh], color=RED, lw=2.2, ls='--')
ax.plot([-W, W], [Hh, Hh], color=RED, lw=2.2, ls='--',
        label=r'$H(f)=\frac{1}{f_s}\,\mathrm{rect}\!\left(\frac{f}{2W}\right)$')
ax.plot([W, W], [Hh, 0], color=RED, lw=2.2, ls='--')
ax.plot([W, 2.2 * fs], [0, 0], color=RED, lw=2.2, ls='--')

# marcadores de banda e taxa
for xv, lab in [(-W, r'$-W$'), (W, r'$W$'),
                (-fs, r'$-f_s$'), (fs, r'$f_s$'),
                (-2 * fs, r'$-2f_s$'), (2 * fs, r'$2f_s$')]:
    ax.axvline(xv, color='0.85', lw=0.8, zorder=0)

ax.annotate('réplica central\nisolada', xy=(0, 0.5 * peak),
            xytext=(1.5 * fs, 0.72 * peak), fontsize=9, color=UNB_BLUE,
            ha='center',
            arrowprops=dict(arrowstyle='->', color=UNB_BLUE, lw=1))

ax.set_xlim(-2.2 * fs, 2.2 * fs)
ax.set_ylim(0, 1.28 * peak)
ax.set_xlabel(r'$f$')
ax.set_yticks([])
ax.set_xticks([-2 * fs, -fs, -W, 0, W, fs, 2 * fs])
ax.set_xticklabels([r'$-2f_s$', r'$-f_s$', r'$-W$', '0',
                    r'$W$', r'$f_s$', r'$2f_s$'])
ax.spines['left'].set_visible(False)
ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.28),
          frameon=False, fontsize=8.5)

fig.tight_layout()
fig.savefig('../reconstrucao_lpf.pdf', bbox_inches='tight')
plt.close(fig)

print('Figura reconstrucao_lpf.pdf gerada.')
