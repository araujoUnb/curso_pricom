#!/usr/bin/env python3
"""
Script 14: Efeito de limiar em FM
(S/N)_o vs. (S/N)_i (gamma) mostrando a região de limiar
"""

import numpy as np
import matplotlib.pyplot as plt

plt.rcParams['font.size'] = 10
plt.rcParams['axes.grid'] = True

# gamma (SNR de entrada) em dB
gamma_dB = np.linspace(-5, 50, 300)
gamma_lin = 10**(gamma_dB / 10)

beta = 5
# Acima do limiar: (S/N)_o = 3*beta^2*gamma
snr_o_linear = 3 * beta**2 * gamma_lin

# Limiar em ~10 dB (qualitativo): abaixo disso (S/N)_o cai rapidamente
threshold_dB = 10
threshold_lin = 10**(threshold_dB / 10)

# Abaixo do limiar: curva de degradação (modelo simplificado)
# (S/N)_o proporcional a gamma^2 ou queda rápida
snr_o_plot = np.where(gamma_lin >= threshold_lin,
                      snr_o_linear,
                      snr_o_linear * (gamma_lin / threshold_lin)**2 * 0.5)
snr_o_plot = np.maximum(snr_o_plot, 0.1)

snr_o_dB = 10 * np.log10(snr_o_plot)

fig, ax = plt.subplots(figsize=(10, 6))
ax.plot(gamma_dB, snr_o_dB, 'b-', linewidth=2.5, label=f'FM $\\beta$ = {beta}')
# Linha tracejada: continuação da curva linear (sem limiar)
snr_o_ideal_dB = 10 * np.log10(snr_o_linear)
ax.plot(gamma_dB, snr_o_ideal_dB, 'b--', linewidth=1.5, alpha=0.7, label='Extrapolação linear')

ax.axvline(x=threshold_dB, color='r', linestyle='--', linewidth=2, label=f'Limiar ~{threshold_dB} dB')
ax.axvspan(-5, threshold_dB, alpha=0.15, color='red')
ax.text((threshold_dB - 5)/2, 5, 'Região de\nlimiar', ha='center', fontsize=10,
        bbox=dict(boxstyle='round', facecolor='white', alpha=0.9))

ax.set_xlabel('$(S/N)_i$ = $\\gamma$ (dB)')
ax.set_ylabel('$(S/N)_o$ (dB)')
ax.set_title('Efeito de limiar na demodulação FM')
ax.legend(loc='lower right')
ax.grid(True, alpha=0.3)
ax.set_xlim([-5, 50])
ax.set_ylim([-10, 60])

plt.tight_layout()
plt.savefig('../fm_threshold.pdf', bbox_inches='tight')
plt.savefig('../fm_threshold.png', dpi=300, bbox_inches='tight')
print("Figura salva: fm_threshold.pdf/png")
plt.close()
