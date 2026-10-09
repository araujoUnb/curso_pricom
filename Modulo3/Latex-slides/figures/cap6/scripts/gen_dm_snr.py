#!/usr/bin/env python3
"""
Gera a figura didatica da SNR da modulacao delta (Q18 c).

Painel esquerdo: o ruido granular tem potencia total ~delta^2/3 espalhada
(branca) em [0, f_s/2]. Aumentar f_s espalha o ruido numa banda maior, logo
a densidade cai e a parcela que passa pelo filtro de saida (corte W) diminui:
N_q = (delta^2/3)(2W/f_s).

Painel direito: combinando com o limite de sobrecarga (delta ~ 1/f_s), a SNR
cresce com f_s^3, ou seja +9 dB por oitava de sobreamostragem.

Saida: ../dm_snr.pdf

Uso: python gen_dm_snr.py
"""

import numpy as np
import matplotlib.pyplot as plt

plt.rcParams.update({
    'font.size': 11,
    'font.family': 'serif',
    'axes.labelsize': 10,
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

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9.4, 3.4))

# ---- Painel 1: espalhamento do ruido de quantizacao --------------------
W = 1.0
noise_power = 1.0        # delta^2/3 (referencia)

# dois valores de f_s
for fs, col, lab, alpha in [(3.0, RED, r'$f_s$', 0.30),
                            (6.0, UNB_GREEN, r'$2f_s$', 0.18)]:
    height = noise_power / (fs / 2.0)   # densidade branca em [0, fs/2]
    ax1.plot([0, fs / 2, fs / 2], [height, height, 0], color=col, lw=2.0,
             label=f'PSD do ruído a {lab}')

# banda do filtro de saida
ax1.axvspan(0, W, color=UNB_GOLD, alpha=0.25)
ax1.axvline(W, color='0.4', ls=':', lw=1)
ax1.text(W, 0.72, r'$W$', color='0.3', ha='center', fontsize=10)
ax1.annotate('só a parcela\nem $[0,W]$ passa', xy=(0.5, 0.15),
             xytext=(1.5, 0.5), color='0.25', fontsize=9,
             arrowprops=dict(arrowstyle='->', color='0.5', lw=1))

ax1.set_title('o ruído se espalha em $[0,f_s/2]$')
ax1.set_xlabel('frequência')
ax1.set_ylabel('densidade de ruído')
ax1.set_xlim(0, 3.3)
ax1.set_ylim(0, 0.8)
ax1.set_yticks([])
ax1.set_xticks([0, W])
ax1.set_xticklabels(['0', r'$W$'])
ax1.legend(loc='upper right', frameon=False, fontsize=8)

# ---- Painel 2: SNR ~ fs^3 -> +9 dB/oitava ------------------------------
fs = np.logspace(np.log10(2), np.log10(64), 200)
snr_db = 30 * np.log10(fs / 2)   # 10*log10(fs^3) = 30 log10 fs -> +9 dB/oitava

ax2.semilogx(fs, snr_db, color=UNB_BLUE, lw=2.6, base=2)
# marca uma oitava = +9 dB
f_a, f_b = 8.0, 16.0
s_a = 30 * np.log10(f_a / 2)
s_b = 30 * np.log10(f_b / 2)
ax2.plot([f_a, f_b], [s_a, s_a], color=RED, lw=1.2, ls='--')
ax2.plot([f_b, f_b], [s_a, s_b], color=RED, lw=1.2, ls='--')
ax2.text(f_b * 1.05, (s_a + s_b) / 2, '+9 dB', color=RED, fontsize=9,
         va='center')
ax2.text(np.sqrt(f_a * f_b), s_a - 4, '1 oitava', color=RED, fontsize=9,
         ha='center', va='top')

ax2.set_title(r'$\mathrm{SNR}\propto f_s^{3}$')
ax2.set_xlabel(r'$f_s$ (oitavas, escala log)')
ax2.set_ylabel('SNR (dB)')
ax2.set_xticks([2, 4, 8, 16, 32, 64])
ax2.set_xticklabels(['2', '4', '8', '16', '32', '64'])
ax2.set_ylim(0, 55)

fig.tight_layout()
fig.savefig('../dm_snr.pdf', bbox_inches='tight')
plt.close(fig)

print('Figura dm_snr.pdf gerada.')
