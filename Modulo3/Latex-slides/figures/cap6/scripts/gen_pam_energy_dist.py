#!/usr/bin/env python3
"""
Relacao mutua entre energia media e distancia no M-PAM:

    E_s = (M^2 - 1) d^2 / 3        (energia cresce com d^2)
    d   = sqrt(3 E_s / (M^2 - 1))  (distancia cai com a ordem M)

Saida: ../pam_esd.pdf  -> E_s em funcao de d (parabolas, M = 2,4,8)
       ../pam_des.pdf  -> d em funcao de E_s (raiz), com E_s fixo

Uso: python gen_pam_energy_dist.py
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

Ms = [2, 4, 8]
mcolors = [UNB_BLUE, UNB_GREEN, UNB_GOLD]


# ===========================================================================
# E_s em funcao de d (parabolas)
# ===========================================================================
d = np.linspace(0, 1.5, 300)


def Es_of(M, d):
    return (M ** 2 - 1) / 3.0 * d ** 2


fig, ax = plt.subplots(figsize=(7.6, 4.0))
for M, c in zip(Ms, mcolors):
    coef = (M ** 2 - 1) / 3.0
    ax.plot(d, Es_of(M, d), color=c, lw=2.6, label=f'{M}-PAM')
    ax.annotate(rf'$\frac{{M^2-1}}{{3}}={coef:.0f}$',
                xy=(1.5, Es_of(M, 1.5)), xytext=(1.12, Es_of(M, 1.5) + 1.5),
                color=c, fontsize=10)
# ilustra o crescimento quadratico em M=2
d0 = 0.5
ax.plot([d0, d0], [0, Es_of(2, d0)], color='0.6', ls=':', lw=1)
ax.plot([2 * d0, 2 * d0], [0, Es_of(2, 2 * d0)], color='0.6', ls=':', lw=1)
ax.annotate(r'dobrar $d$ $\Rightarrow$ $4\times E_s$',
            xy=(2 * d0, Es_of(2, 2 * d0)), xytext=(0.55, 17),
            fontsize=10, color=UNB_BLUE,
            arrowprops=dict(arrowstyle='->', color=UNB_BLUE))
ax.set_xlim(0, 1.5)
ax.set_ylim(0, 50)
ax.set_xlabel(r'distância à origem  $d$')
ax.set_ylabel(r'energia média  $E_s$')
ax.legend(loc='upper left', frameon=False, fontsize=11)
ax.set_title(r'$E_s = \frac{M^2-1}{3}\,d^2$  (cresce com $d^2$)', fontsize=12)
fig.tight_layout()
fig.savefig('../pam_esd.pdf', bbox_inches='tight')
plt.close(fig)

# ===========================================================================
# d em funcao de E_s (raiz), com energia fixa
# ===========================================================================
Es = np.linspace(0, 30, 300)


def d_of(M, Es):
    return np.sqrt(3.0 * Es / (M ** 2 - 1))


Es_fix = 20.0
fig, ax = plt.subplots(figsize=(7.6, 4.0))
for M, c in zip(Ms, mcolors):
    ax.plot(Es, d_of(M, Es), color=c, lw=2.6, label=f'{M}-PAM')
# energia fixa: distancia encolhe com M
ax.axvline(Es_fix, color='0.5', ls='--', lw=1.2)
ax.text(Es_fix + 0.4, 4.4, r'$E_s$ fixo', color='0.4', fontsize=10)
for M, c in zip(Ms, mcolors):
    dd = d_of(M, Es_fix)
    ax.plot(Es_fix, dd, 'o', color=c, ms=9, zorder=5)
    ax.annotate(rf'$d={dd:.2f}$', xy=(Es_fix, dd),
                xytext=(Es_fix + 1.0, dd + 0.12), color=c, fontsize=10)
ax.annotate('mais níveis\n$\\Rightarrow$ menor $d$', xy=(Es_fix, d_of(8, Es_fix)),
            xytext=(9.5, 0.5), fontsize=11, color=RED,
            arrowprops=dict(arrowstyle='->', color=RED))
ax.set_xlim(0, 30)
ax.set_ylim(0, 5)
ax.set_xlabel(r'energia média  $E_s$')
ax.set_ylabel(r'distância à origem  $d$')
ax.legend(loc='upper right', frameon=False, fontsize=11)
ax.set_title(r'$d = \sqrt{\dfrac{3 E_s}{M^2-1}}$  (cai com a ordem $M$)',
             fontsize=12)
fig.tight_layout()
fig.savefig('../pam_des.pdf', bbox_inches='tight')
plt.close(fig)

print('Figuras pam_esd.pdf e pam_des.pdf geradas.')
for M in Ms:
    print(f'M={M}: d(Es=20) = {d_of(M, 20.0):.3f}')
