#!/usr/bin/env python3
"""
Explica de onde vem o fator 2(M-1) na probabilidade de erro do M-PAM:
ha M-1 limiares de decisao e cada um pode ser cruzado em 2 sentidos, logo
2(M-1) eventos de erro, cada um com probabilidade Q(d/sigma).

Saida: ../pam_count_1..4.pdf

Uso: python gen_pam_count.py
"""

import matplotlib.pyplot as plt

plt.rcParams.update({
    'font.size': 11,
    'font.family': 'serif',
    'axes.labelsize': 12,
    'axes.titlesize': 12,
    'xtick.labelsize': 10,
    'figure.dpi': 150,
    'text.usetex': False,
    'axes.spines.top': False,
    'axes.spines.right': False,
    'axes.spines.left': False,
    'axes.grid': False,
})

UNB_BLUE  = '#003B5C'
UNB_GREEN = '#006633'
UNB_GOLD  = '#F2A900'
RED       = '#C0392B'
PURPLE    = '#8E44AD'

levels = [-3, -1, 1, 3]
lvl_colors = [UNB_BLUE, UNB_GREEN, UNB_GOLD, PURPLE]
thr = [-2, 0, 2]


def base_axes():
    fig, ax = plt.subplots(figsize=(8.4, 3.3))
    ax.set_xlim(-4.4, 4.4)
    ax.set_ylim(-1.25, 1.35)
    ax.axhline(0, color='black', lw=1.2)
    ax.set_yticks([])
    ax.set_xticks(levels)
    ax.set_xticklabels([f'${v}d$' for v in levels])
    ax.set_xlabel(r'amplitude recebida  $r(kT)$')
    for v, c in zip(levels, lvl_colors):
        ax.plot(v, 0, 'o', color=c, ms=13, zorder=5)
    return fig, ax


def draw_thr(ax, highlight=None):
    for j, tx in enumerate(thr):
        col = RED if (highlight is not None and j == highlight) else '0.55'
        lw = 2.2 if (highlight is not None and j == highlight) else 1.2
        ax.axvline(tx, color=col, ls='--', lw=lw)


def cross_arrows(ax, tx, color=RED):
    """Duas setas cruzando o limiar tx, uma em cada sentido."""
    ax.annotate('', xy=(tx + 0.55, 0.42), xytext=(tx - 0.55, 0.42),
                arrowprops=dict(arrowstyle='->', color=color, lw=2,
                                connectionstyle='arc3,rad=-0.3'))
    ax.annotate('', xy=(tx - 0.55, -0.42), xytext=(tx + 0.55, -0.42),
                arrowprops=dict(arrowstyle='->', color=color, lw=2,
                                connectionstyle='arc3,rad=-0.3'))


# --- estado 1: M pontos e M-1 limiares ---
fig, ax = base_axes()
draw_thr(ax)
for tx in thr:
    ax.text(tx, 1.12, 'limiar', ha='center', fontsize=9, color='0.4')
ax.set_title(r'$M=4$ símbolos $\Rightarrow$ $M-1=3$ limiares de decisão',
             fontsize=12)
fig.tight_layout()
fig.savefig('../pam_count_1.pdf', bbox_inches='tight')
plt.close(fig)

# --- estado 2: um limiar, dois sentidos ---
fig, ax = base_axes()
draw_thr(ax, highlight=1)
cross_arrows(ax, 0)
ax.text(0, 0.72, '2 erros por limiar', ha='center', fontsize=11, color=RED)
ax.text(-1, -0.7, r'$-1d \to +1d$', ha='center', fontsize=9, color=RED)
ax.text(1, 0.16, r'$+1d \to -1d$', ha='center', fontsize=9, color=RED)
ax.set_title('Cada limiar pode ser cruzado em dois sentidos', fontsize=12)
fig.tight_layout()
fig.savefig('../pam_count_2.pdf', bbox_inches='tight')
plt.close(fig)

# --- estado 3: todos os limiares, contagem ---
fig, ax = base_axes()
draw_thr(ax)
for tx in thr:
    cross_arrows(ax, tx)
ax.text(0, 1.12,
        r'$2 \times (M-1) = 2 \times 3 = 6$ eventos de erro',
        ha='center', fontsize=12, color=RED)
ax.set_title(r'$M-1$ limiares $\times$ 2 sentidos $= 2(M-1)$', fontsize=12)
fig.tight_layout()
fig.savefig('../pam_count_3.pdf', bbox_inches='tight')
plt.close(fig)

# --- estado 4: cada evento vale Q(d/sigma), media sobre M simbolos ---
fig, ax = base_axes()
draw_thr(ax)
for tx in thr:
    cross_arrows(ax, tx)
ax.text(0, 1.12, r'cada evento: probabilidade $Q(d/\sigma)$',
        ha='center', fontsize=11, color=RED)
ax.text(0, -1.02,
        r'$P_s = \frac{1}{M}\cdot 2(M-1)\cdot Q(d/\sigma)'
        r' = 2(1-\frac{1}{M})\,Q(d/\sigma)$',
        ha='center', fontsize=13, color='0.15')
ax.set_title('Média por símbolo dá o fator $2(1-1/M)$', fontsize=12)
fig.tight_layout()
fig.savefig('../pam_count_4.pdf', bbox_inches='tight')
plt.close(fig)

print('Figuras pam_count_1..4.pdf geradas.')
