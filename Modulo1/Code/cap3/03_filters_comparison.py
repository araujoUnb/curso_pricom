#!/usr/bin/env python3
"""
Script 03: Comparação de Filtros (Butterworth vs Chebyshev vs Bessel)
Gera: Respostas em frequência de diferentes aproximações de filtros
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy import signal

plt.rcParams['font.size'] = 11
plt.rcParams['axes.grid'] = True

# Parâmetros
order = 4  # Ordem dos filtros
wc = 1.0   # Frequência de corte normalizada (rad/s)

# Frequência para plotagem
w = np.linspace(0, 3, 1000)

# Projetar filtros
# Butterworth
b_butter, a_butter = signal.butter(order, wc, analog=True)
w_butter, h_butter = signal.freqs(b_butter, a_butter, w)

# Chebyshev Tipo I (0.5 dB ripple)
b_cheby, a_cheby = signal.cheby1(order, 0.5, wc, analog=True)
w_cheby, h_cheby = signal.freqs(b_cheby, a_cheby, w)

# Bessel
b_bessel, a_bessel = signal.bessel(order, wc, analog=True, norm='mag')
w_bessel, h_bessel = signal.freqs(b_bessel, a_bessel, w)

# Criar figura
fig, axes = plt.subplots(2, 1, figsize=(10, 10))

# Subplot 1: Magnitude (dB)
axes[0].plot(w_butter, 20*np.log10(np.abs(h_butter)), 'b-', linewidth=2, label='Butterworth')
axes[0].plot(w_cheby, 20*np.log10(np.abs(h_cheby)), 'r--', linewidth=2, label='Chebyshev I (0.5dB ripple)')
axes[0].plot(w_bessel, 20*np.log10(np.abs(h_bessel)), 'g-.', linewidth=2, label='Bessel')
axes[0].set_xlabel('Frequência normalizada ω/ωc')
axes[0].set_ylabel('Magnitude (dB)')
axes[0].set_title(f'Comparação de Filtros Passa-Baixas (Ordem {order})')
axes[0].set_xlim([0, 3])
axes[0].set_ylim([-60, 5])
axes[0].axhline(y=-3, color='k', linestyle=':', linewidth=1, alpha=0.5)
axes[0].axvline(x=1, color='k', linestyle=':', linewidth=1, alpha=0.5)
axes[0].legend(loc='upper right')
axes[0].grid(True, which='both', alpha=0.3)

# Subplot 2: Fase
phase_butter = np.unwrap(np.angle(h_butter))
phase_cheby = np.unwrap(np.angle(h_cheby))
phase_bessel = np.unwrap(np.angle(h_bessel))

axes[1].plot(w_butter, phase_butter*180/np.pi, 'b-', linewidth=2, label='Butterworth')
axes[1].plot(w_cheby, phase_cheby*180/np.pi, 'r--', linewidth=2, label='Chebyshev I')
axes[1].plot(w_bessel, phase_bessel*180/np.pi, 'g-.', linewidth=2, label='Bessel')
axes[1].set_xlabel('Frequência normalizada ω/ωc')
axes[1].set_ylabel('Fase (graus)')
axes[1].set_title('Resposta de Fase')
axes[1].set_xlim([0, 3])
axes[1].axvline(x=1, color='k', linestyle=':', linewidth=1, alpha=0.5)
axes[1].legend(loc='lower left')
axes[1].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('../filters_comparison.pdf', bbox_inches='tight')
plt.savefig('../filters_comparison.png', dpi=300, bbox_inches='tight')
print("Figura salva: filters_comparison.pdf/png")
plt.close()
