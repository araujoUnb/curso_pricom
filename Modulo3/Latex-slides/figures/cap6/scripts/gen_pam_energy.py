#!/usr/bin/env python3
"""
Mostra de onde vem a energia media por simbolo do M-PAM,
E_s = (M^2 - 1) d^2 / 3, como a media dos quadrados das amplitudes dos
niveis simetricos +-d, +-3d, ..., +-(M-1)d.

Saida: ../pam_energy_1..3.pdf

Uso: python gen_pam_energy.py
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

levels = np.array([-3, -1, 1, 3])           # 4-PAM em unidades de d
lvl_colors = [UNB_BLUE, UNB_GREEN, UNB_GOLD, PURPLE]
energy = levels ** 2                         # a_m^2 = energia de cada simbolo
Es = energy.mean()                           # media = (M^2-1)/3 = 5


def base_axes():
    fig, ax = plt.subplots(figsize=(8.2, 3.6))
    ax.set_xlim(-4.2, 4.2)
    ax.set_ylim(0, 11)
    ax.set_xticks(levels)
    ax.set_xticklabels([f'${v}d$' for v in levels])
    ax.set_xlabel(r'amplitude do símbolo  $a_m$')
    ax.set_ylabel(r'energia  $a_m^{2}$')
    return fig, ax


# --- estado 1: niveis e suas amplitudes ---
fig, ax = base_axes()
for v, c in zip(levels, lvl_colors):
    ax.plot(v, 0.0, 'o', color=c, ms=13, zorder=5)
ax.set_ylim(-1.2, 11)
ax.axhline(0, color='black', lw=1)
ax.set_title(r'$M$-PAM: níveis $\pm d, \pm 3d, \dots, \pm (M-1)d$',
             fontsize=12)
fig.tight_layout()
fig.savefig('../pam_energy_1.pdf', bbox_inches='tight')
plt.close(fig)

# --- estado 2: energia de cada simbolo = a_m^2 ---
fig, ax = base_axes()
for v, c, e in zip(levels, lvl_colors, energy):
    ax.bar(v, e, width=0.7, color=c, alpha=0.85)
    ax.text(v, e + 0.3, f'${int(e)}d^2$', ha='center', fontsize=11, color=c)
ax.set_title(r'Energia de cada símbolo: $a_m^{2}$', fontsize=12)
fig.tight_layout()
fig.savefig('../pam_energy_2.pdf', bbox_inches='tight')
plt.close(fig)

# --- estado 3: media -> Es ---
fig, ax = base_axes()
for v, c, e in zip(levels, lvl_colors, energy):
    ax.bar(v, e, width=0.7, color=c, alpha=0.5)
    ax.text(v, e + 0.3, f'${int(e)}d^2$', ha='center', fontsize=10, color=c)
ax.axhline(Es, color=RED, lw=2.4, ls='--')
ax.text(-4.0, Es + 0.35,
        r'$E_s = \overline{a_m^{2}} = \frac{9+1+1+9}{4}d^2 = 5d^2$',
        fontsize=12, color=RED)
ax.annotate(r'$= \frac{M^2-1}{3}d^2$', xy=(3.2, Es),
            xytext=(2.2, Es + 2.2), fontsize=12, color=RED,
            arrowprops=dict(arrowstyle='->', color=RED))
ax.set_title(r'Média dos quadrados $\Rightarrow E_s = (M^2-1)d^2/3$',
             fontsize=12)
fig.tight_layout()
fig.savefig('../pam_energy_3.pdf', bbox_inches='tight')
plt.close(fig)

print('Figuras pam_energy_1..3.pdf geradas. Es =', Es,
      ' formula (M^2-1)/3 =', (4**2 - 1) / 3)
