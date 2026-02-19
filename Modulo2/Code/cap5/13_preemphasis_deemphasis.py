#!/usr/bin/env python3
"""
Script 13: Resposta em frequência de pré-ênfase e pós-ênfase (FM)
H_pe(f) = 1 + j f/f0,  H_de(f) = 1/(1 + j f/f0)
"""

import numpy as np
import matplotlib.pyplot as plt

plt.rcParams['font.size'] = 10
plt.rcParams['axes.grid'] = True

# f0 típico FM broadcast ~ 2.1 kHz (tau = 75 us)
f0 = 2100  # Hz
f = np.logspace(1, 5, 500)  # 10 Hz a 100 kHz

# Pré-ênfase: H_pe = 1 + j*f/f0  -> |H_pe|^2 = 1 + (f/f0)^2
H_pe_mag = np.sqrt(1 + (f/f0)**2)
H_pe_dB = 20 * np.log10(H_pe_mag)

# Pós-ênfase (de-ênfase): H_de = 1/(1 + j*f/f0)  -> |H_de| = 1/sqrt(1+(f/f0)^2)
H_de_mag = 1 / np.sqrt(1 + (f/f0)**2)
H_de_dB = 20 * np.log10(H_de_mag)

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))

ax1.semilogx(f, H_pe_dB, 'b-', linewidth=2, label='Pré-ênfase $|H_{pe}(f)|$')
ax1.semilogx(f, H_de_dB, 'r-', linewidth=2, label='Pós-ênfase $|H_{de}(f)|$')
ax1.axvline(x=f0, color='k', linestyle='--', linewidth=1, alpha=0.7, label=f'$f_0$ = {f0} Hz')
ax1.set_xlabel('Frequência (Hz)')
ax1.set_ylabel('Magnitude (dB)')
ax1.set_title('Filtros de pré-ênfase e pós-ênfase em FM ($f_0 = 2{,}1$ kHz)')
ax1.legend()
ax1.grid(True, which='both', alpha=0.3)
ax1.set_xlim([10, 1e5])
ax1.set_ylim([-20, 25])

# Produto H_pe * H_de = 1 (resposta plana para o sinal)
ax2.semilogx(f, H_pe_dB + H_de_dB, 'g-', linewidth=2)
ax2.axhline(y=0, color='k', linestyle='-', linewidth=0.5)
ax2.set_xlabel('Frequência (Hz)')
ax2.set_ylabel('Soma (dB)')
ax2.set_title('Resposta global $|H_{pe}| \\cdot |H_{de}|$ = 1 (0 dB)')
ax2.grid(True, which='both', alpha=0.3)
ax2.set_xlim([10, 1e5])

plt.tight_layout()
plt.savefig('../preemphasis_deemphasis.pdf', bbox_inches='tight')
plt.savefig('../preemphasis_deemphasis.png', dpi=300, bbox_inches='tight')
print("Figura salva: preemphasis_deemphasis.pdf/png")
plt.close()
