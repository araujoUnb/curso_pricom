#!/usr/bin/env python3
"""
Gera a figura didatica da inclinacao da escada da modulacao delta (Q18 a):
a cada amostra (intervalo T_s) a escada sobe um passo delta. Logo sua
inclinacao maxima e o "cateto vertical" delta sobre o "cateto horizontal"
T_s, isto e, delta/T_s = delta*f_s.

Saida: ../staircase_slope.pdf

Uso: python gen_staircase_slope.py
"""

import numpy as np
import matplotlib.pyplot as plt

plt.rcParams.update({
    'font.size': 11,
    'font.family': 'serif',
    'axes.labelsize': 11,
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

Ts = 1.0
delta = 1.0
N = 5

# escada subindo delta por amostra
xk = np.arange(N + 1) * Ts
yk = np.arange(N + 1) * delta

fig, ax = plt.subplots(figsize=(6.4, 3.4))

# reta de inclinacao media delta/Ts (a rampa que a escada aproxima)
ax.plot([0, N * Ts], [0, N * delta], color='0.6', lw=1.4, ls='--',
        label=r'inclinação $\delta/T_s=\delta f_s$')

# escada
ax.step(xk, yk, where='post', color=UNB_BLUE, lw=2.4, label='escada DM')

# destaca um degrau (o segundo)
i = 2
x0, y0 = i * Ts, i * delta
# cateto horizontal T_s
ax.annotate('', xy=(x0, y0), xytext=(x0 + Ts, y0),
            arrowprops=dict(arrowstyle='<->', color=RED, lw=1.4))
ax.text(x0 + Ts / 2, y0 - 0.22, r'$T_s=1/f_s$', color=RED, ha='center',
        va='top', fontsize=10)
# cateto vertical delta
ax.annotate('', xy=(x0 + Ts, y0), xytext=(x0 + Ts, y0 + delta),
            arrowprops=dict(arrowstyle='<->', color=UNB_GREEN, lw=1.4))
ax.text(x0 + Ts + 0.08, y0 + delta / 2, r'$\delta$', color=UNB_GREEN,
        ha='left', va='center', fontsize=12)

# triangulo de inclinacao sombreado
ax.fill([x0, x0 + Ts, x0 + Ts], [y0, y0, y0 + delta], color=UNB_GOLD,
        alpha=0.25, zorder=0)

ax.text(2.6, 4.4, r'inclinação $=\dfrac{\text{sobe }\delta}{\text{em }T_s}'
        r'=\dfrac{\delta}{T_s}=\delta f_s$', fontsize=11, color='0.15',
        ha='center',
        bbox=dict(boxstyle='round,pad=0.35', fc='white', ec='0.6'))

ax.set_xlim(0, N * Ts + 0.3)
ax.set_ylim(0, N * delta + 0.5)
ax.set_xlabel(r'$t$')
ax.set_ylabel('saída da escada')
ax.set_xticks(xk)
ax.set_xticklabels(['0', r'$T_s$', r'$2T_s$', r'$3T_s$', r'$4T_s$', r'$5T_s$'])
ax.set_yticks(yk)
ax.set_yticklabels(['0', r'$\delta$', r'$2\delta$', r'$3\delta$', r'$4\delta$',
                    r'$5\delta$'])
ax.legend(loc='lower right', frameon=False, fontsize=9)

fig.tight_layout()
fig.savefig('../staircase_slope.pdf', bbox_inches='tight')
plt.close(fig)

print('Figura staircase_slope.pdf gerada.')
