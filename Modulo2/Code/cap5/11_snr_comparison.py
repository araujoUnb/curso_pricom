#!/usr/bin/env python3
"""
Script 11: Comparação de SNR para sistemas analógicos
(S/N)_o vs. gamma para banda base, DSB-SC, SSB, AM convencional, FM
"""

import numpy as np
import matplotlib.pyplot as plt

plt.rcParams['font.size'] = 10
plt.rcParams['axes.grid'] = True

# gamma em dB (SNR de entrada)
gamma_dB = np.linspace(-10, 50, 200)
gamma_lin = 10**(gamma_dB / 10)

# Banda base: (S/N)_o = gamma
snr_base = gamma_lin

# DSB-SC: (S/N)_o = 2*gamma
snr_dsb = 2 * gamma_lin

# SSB: (S/N)_o = gamma
snr_ssb = gamma_lin

# AM convencional: (S/N)_o = eta*gamma, eta = mu^2/(2+mu^2), mu=0.8
mu = 0.8
eta = mu**2 / (2 + mu**2)
snr_am = eta * gamma_lin

# FM: (S/N)_o = 3*beta^2*gamma (acima do limiar)
beta_fm = 5
snr_fm = 3 * beta_fm**2 * gamma_lin

# Limiar FM (qualitativo): abaixo de gamma ~ 10 dB degradação
# Para gamma < 10 dB, FM cai (simplificado: linear em log até um piso)
snr_fm_plot = np.where(gamma_dB >= 10, 3 * beta_fm**2 * gamma_lin,
                       np.maximum(3 * beta_fm**2 * 10 * (gamma_lin / 10)**2, 0.1))

fig, ax = plt.subplots(figsize=(10, 7))
ax.semilogy(gamma_dB, snr_base, 'k-', linewidth=2, label='Banda base')
ax.semilogy(gamma_dB, snr_dsb, 'b-', linewidth=2, label='DSB-SC (coerente)')
ax.semilogy(gamma_dB, snr_ssb, 'g--', linewidth=2, label='SSB (coerente)')
ax.semilogy(gamma_dB, snr_am, 'r-.', linewidth=2, label=f'AM convencional ($\\mu$={mu})')
ax.semilogy(gamma_dB, snr_fm_plot, 'm-', linewidth=2, label=f'FM ($\\beta$={beta_fm})')

ax.set_xlabel('$\\gamma$ = $P_r/(N_0 W)$ (dB)')
ax.set_ylabel('$(S/N)_o$ (linear)')
ax.set_title('Comparação de SNR na saída: $(S/N)_o$ vs. $\\gamma$')
ax.legend(loc='lower right')
ax.set_xlim([-10, 50])
ax.set_ylim([1e-2, 1e6])
ax.grid(True, which='both', alpha=0.3)

# Marcar região de limiar FM
ax.axvspan(-10, 10, alpha=0.1, color='magenta')
ax.text(0, 2e4, 'Região de limiar FM', ha='center', fontsize=9,
        bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

plt.tight_layout()
plt.savefig('../snr_comparison.pdf', bbox_inches='tight')
plt.savefig('../snr_comparison.png', dpi=300, bbox_inches='tight')
print("Figura salva: snr_comparison.pdf/png")
plt.close()
