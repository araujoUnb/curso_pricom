#!/usr/bin/env python3
"""
Ilustra a decisao do receptor M-PAM e a probabilidade de erro, conectando
a figura as formulas. Tambem mostra o efeito de aumentar a SNR e a ordem
da modulacao M.

Saida:
  ../pam_decision_1..4.pdf -> regioes de decisao, ruido gaussiano e cauda Q
  ../pam_ber_1..2.pdf      -> P_s vs Eb/N0 para M = 2,4,8,16

Uso: python gen_pam_error.py
"""

import numpy as np
import matplotlib.pyplot as plt
from math import erfc

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


def Q(x):
    x = np.asarray(x, dtype=float)
    return 0.5 * np.vectorize(erfc)(x / np.sqrt(2.0))


# ===========================================================================
# Decisao M-PAM (4-PAM): regioes, ruido e cauda Q
# ===========================================================================
levels = [-3, -1, 1, 3]
lvl_colors = [UNB_BLUE, UNB_GREEN, UNB_GOLD, PURPLE]
thr = [-2, 0, 2]
d = 1.0
sigma = 0.62
peak = 0.92

x = np.linspace(-5, 5, 2000)


def gauss(mu):
    return peak * np.exp(-((x - mu) ** 2) / (2 * sigma ** 2))


def base_axes():
    fig, ax = plt.subplots(figsize=(8.4, 3.5))
    ax.set_xlim(-5, 5)
    ax.set_ylim(-0.18, 1.18)
    ax.axhline(0, color='black', lw=1)
    for tx in thr:
        ax.axvline(tx, color='0.6', ls='--', lw=1.2)
    ax.set_yticks([])
    ax.set_xticks(levels)
    ax.set_xticklabels([f'${v}$' for v in levels])
    ax.set_xlabel(r'amplitude recebida  $r(kT)$')
    ax.spines['left'].set_visible(False)
    return fig, ax


def draw_points(ax):
    for v, c in zip(levels, lvl_colors):
        ax.plot(v, 0, 'o', color=c, ms=12, zorder=5)


# --- estado 1: regioes de decisao ---
fig, ax = base_axes()
draw_points(ax)
regions = [(-5, -2, '-3'), (-2, 0, '-1'), (0, 2, '1'), (2, 5, '3')]
for a, b, lab in regions:
    ax.text((a + b) / 2, 1.04, f'decide ${lab}$', ha='center', fontsize=9,
            color='0.3')
ax.set_title('Regiões de decisão: escolhe o símbolo mais próximo', fontsize=12)
fig.tight_layout()
fig.savefig('../pam_decision_1.pdf', bbox_inches='tight')
plt.close(fig)

# --- estado 2: amostra recebida e decisao ---
fig, ax = base_axes()
draw_points(ax)
r_val = 1.55
ax.plot(r_val, 0, 'X', color=RED, ms=13, zorder=6)
ax.annotate(r'$r(kT)$', xy=(r_val, 0), xytext=(r_val + 0.15, 0.5),
            color=RED, fontsize=11,
            arrowprops=dict(arrowstyle='->', color=RED))
ax.annotate('', xy=(1, 0.0), xytext=(r_val, 0.0),
            arrowprops=dict(arrowstyle='->', color=UNB_GOLD, lw=2))
ax.text(0.0, 0.9, r'$\hat{a}_k=\arg\min_{a_m}|r(kT)-a_m|$', ha='center',
        fontsize=12, color='0.2')
ax.set_title('A amostra cai na região do símbolo $+1$', fontsize=12)
fig.tight_layout()
fig.savefig('../pam_decision_2.pdf', bbox_inches='tight')
plt.close(fig)

# --- estado 3: ruido gaussiano e cauda Q(d/sigma) ---
fig, ax = base_axes()
draw_points(ax)
g = gauss(1)
ax.plot(x, g, color=UNB_GOLD, lw=2.2)
ax.fill_between(x, 0, g, where=(x >= 2), color=RED, alpha=0.45)
# marca a distancia d entre simbolo e limiar
ax.annotate('', xy=(2, 0.5), xytext=(1, 0.5),
            arrowprops=dict(arrowstyle='<->', color='0.3', lw=1.2))
ax.text(1.5, 0.56, r'$d$', ha='center', fontsize=12, color='0.2')
ax.annotate(r'área $= Q\!\left(\frac{d}{\sigma}\right)$', xy=(2.55, 0.07),
            xytext=(3.0, 0.55), color=RED, fontsize=11,
            arrowprops=dict(arrowstyle='->', color=RED))
ax.set_title(r'Ruído gaussiano: ultrapassar o limiar $\to$ erro', fontsize=12)
fig.tight_layout()
fig.savefig('../pam_decision_3.pdf', bbox_inches='tight')
plt.close(fig)

# --- estado 4: dois vizinhos (ponto interior) e fator 2(1-1/M) ---
fig, ax = base_axes()
draw_points(ax)
g = gauss(1)
ax.plot(x, g, color=UNB_GOLD, lw=2.2)
ax.fill_between(x, 0, g, where=(x >= 2), color=RED, alpha=0.45)
ax.fill_between(x, 0, g, where=(x <= 0), color=RED, alpha=0.45)
# ponto de borda: so uma cauda
ge = gauss(3)
ax.plot(x, ge, color=PURPLE, lw=1.6, ls='--', alpha=0.7)
ax.fill_between(x, 0, ge, where=(x <= 2), color=RED, alpha=0.20)
ax.text(0.0, 1.06, 'interior: 2 vizinhos', ha='center', fontsize=9, color=RED)
ax.text(3.6, 1.06, 'borda: 1 vizinho', ha='center', fontsize=9,
        color=PURPLE)
ax.text(-2.6, 0.85,
        r'$P_s = 2\left(1-\frac{1}{M}\right)Q\!\left(\frac{d}{\sigma}\right)$',
        ha='left', fontsize=13, color='0.15')
ax.set_title('Média sobre os símbolos dá o fator $2(1-1/M)$', fontsize=12)
fig.tight_layout()
fig.savefig('../pam_decision_4.pdf', bbox_inches='tight')
plt.close(fig)

# ===========================================================================
# P_s vs Eb/N0 para varias ordens M
# ===========================================================================
EbN0_dB = np.linspace(0, 18, 200)
EbN0 = 10 ** (EbN0_dB / 10)
Ms = [2, 4, 8, 16]
mcolors = [UNB_BLUE, UNB_GREEN, UNB_GOLD, PURPLE]


def Ps_of(M):
    arg = np.sqrt((3 * np.log2(M) / (M ** 2 - 1)) * 2 * EbN0)
    return 2 * (1 - 1 / M) * Q(arg)


def ber_axes():
    fig, ax = plt.subplots(figsize=(7.8, 4.0))
    ax.set_yscale('log')
    ax.set_xlim(0, 18)
    ax.set_ylim(1e-6, 1)
    ax.set_xlabel(r'$E_b/N_0$  (dB)')
    ax.set_ylabel(r'$P_s$  (probabilidade de erro de símbolo)')
    ax.grid(True, which='both', alpha=0.3)
    return fig, ax


# --- estado 1: so M = 2, efeito da SNR ---
fig, ax = ber_axes()
ax.plot(EbN0_dB, Ps_of(2), color=mcolors[0], lw=2.4, label='2-PAM')
ax.annotate('aumentar $E_b/N_0$\n$\\Rightarrow$ menor $P_s$',
            xy=(12, Ps_of(2)[np.argmin(np.abs(EbN0_dB - 12))]),
            xytext=(11.5, 5e-2), fontsize=11, color=UNB_BLUE,
            arrowprops=dict(arrowstyle='->', color=UNB_BLUE, lw=1.5))
ax.legend(loc='lower left', frameon=False, fontsize=11)
ax.set_title('Efeito da relação sinal-ruído', fontsize=12)
fig.tight_layout()
fig.savefig('../pam_ber_1.pdf', bbox_inches='tight')
plt.close(fig)

# --- estado 2: todas as ordens, efeito de M ---
fig, ax = ber_axes()
for M, c in zip(Ms, mcolors):
    ax.plot(EbN0_dB, Ps_of(M), color=c, lw=2.4, label=f'{M}-PAM')
ax.annotate('aumentar $M$\n$\\Rightarrow$ curva desloca à direita',
            xy=(12.5, 1e-3), xytext=(2.3, 3e-5), fontsize=11, color='0.2',
            arrowprops=dict(arrowstyle='->', color='0.3', lw=1.5))
# linha de Ps alvo
ax.axhline(1e-4, color='0.5', ls=':', lw=1)
ax.text(0.2, 1.4e-4, r'$P_s$ alvo', fontsize=9, color='0.4')
ax.legend(loc='lower left', frameon=False, fontsize=11, ncol=2)
ax.set_title('Mais níveis exigem mais $E_b/N_0$ para a mesma $P_s$',
             fontsize=12)
fig.tight_layout()
fig.savefig('../pam_ber_2.pdf', bbox_inches='tight')
plt.close(fig)

print('Figuras pam_decision_1..4.pdf e pam_ber_1..2.pdf geradas.')
