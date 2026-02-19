#!/usr/bin/env python3
"""
Script 15: Densidade espectral de ruído térmico
PSD N0/2 e potência em banda W
"""

import numpy as np
import matplotlib.pyplot as plt

plt.rcParams['font.size'] = 10
plt.rcParams['axes.grid'] = True

# PSD bilateral N0/2 (constante)
N0_over_2 = 2e-21  # W/Hz (exemplo: N0 = 4e-21)
W = 4e3  # Hz (4 kHz)
f = np.linspace(-2*W, 2*W, 500)

# PSD: constante N0/2 em [-B, B] para algum B > W (banda do sistema)
B = 1.5 * W
psd = np.where(np.abs(f) <= B, N0_over_2, 0)

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 7))

ax1.fill_between(f/1000, 0, psd, alpha=0.6, color='blue')
ax1.axhline(y=N0_over_2, color='b', linestyle='-', linewidth=2, label='$N_0/2$')
ax1.axvline(x=W/1000, color='r', linestyle='--', linewidth=2, label=f'Banda $W$ = {W/1e3:.0f} kHz')
ax1.axvline(x=-W/1000, color='r', linestyle='--', linewidth=2)
ax1.set_xlabel('Frequência (kHz)')
ax1.set_ylabel('PSD (W/Hz)')
ax1.set_title('Densidade espectral de potência do ruído térmico (bilateral)')
ax1.legend()
ax1.grid(True, alpha=0.3)
ax1.set_ylim([0, N0_over_2 * 1.5])
ax1.set_xlim([-2*W/1000, 2*W/1000])

# Potência em banda W: N = N0*W
N_power = N0_over_2 * 2 * W  # integral de -W a W
ax2.bar([0], [N_power], width=0.3, color='green', edgecolor='black', label=f'$N = N_0 W$ = {N_power:.2e} W')
ax2.set_ylabel('Potência de ruído (W)')
ax2.set_title(f'Potência de ruído em banda $W$ = {W/1e3:.0f} kHz')
ax2.set_xticks([0])
ax2.set_xticklabels(['$N_0 W$'])
ax2.legend()
ax2.grid(True, axis='y', alpha=0.3)

plt.tight_layout()
plt.savefig('../thermal_noise_psd.pdf', bbox_inches='tight')
plt.savefig('../thermal_noise_psd.png', dpi=300, bbox_inches='tight')
print("Figura salva: thermal_noise_psd.pdf/png")
plt.close()
