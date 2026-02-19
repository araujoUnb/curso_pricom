#!/usr/bin/env python3
"""
Script 02: Exponencial Decrescente e sua Transformada de Fourier
Gera: Sinal causal exponencial e espectro Lorentziano
"""

import numpy as np
import matplotlib.pyplot as plt

plt.rcParams['font.size'] = 12
plt.rcParams['axes.grid'] = True

# Parâmetros
a = 2.0  # Constante de decaimento

# Domínio do tempo
t = np.linspace(-1, 5, 1000)
f_t = np.where(t >= 0, np.exp(-a*t), 0)

# Domínio da frequência
omega = np.linspace(-10, 10, 1000)
# Magnitude e fase
H_mag = 1 / np.sqrt(a**2 + omega**2)
H_phase = -np.arctan(omega/a)

# Criar figura
fig, axes = plt.subplots(3, 1, figsize=(10, 10))

# Subplot 1: Sinal no tempo
axes[0].plot(t, f_t, 'b', linewidth=2)
axes[0].set_xlabel('Tempo t (s)')
axes[0].set_ylabel('f(t)')
axes[0].set_title(f'Exponencial Decrescente: f(t) = exp(-{a}t)u(t)')
axes[0].set_xlim([-1, 5])
axes[0].set_ylim([0, 1.1])
axes[0].axhline(y=0, color='k', linestyle='-', linewidth=0.5)
axes[0].axvline(x=0, color='k', linestyle='-', linewidth=0.5)

# Subplot 2: Espectro de magnitude
axes[1].plot(omega, H_mag, 'r', linewidth=2)
axes[1].set_xlabel('Frequência angular ω (rad/s)')
axes[1].set_ylabel('|H(ω)|')
axes[1].set_title('Espectro de Magnitude (Lorentziana)')
axes[1].set_xlim([-10, 10])
axes[1].axhline(y=0, color='k', linestyle='-', linewidth=0.5)
axes[1].axvline(x=0, color='k', linestyle='-', linewidth=0.5)
# Marcar ponto de 3dB
axes[1].plot([a, -a], [1/(a*np.sqrt(2)), 1/(a*np.sqrt(2))], 'ro', markersize=8, 
             label=f'ω = ±a = ±{a} rad/s (3 dB)')
axes[1].legend()

# Subplot 3: Fase
axes[2].plot(omega, H_phase * 180/np.pi, 'g', linewidth=2)
axes[2].set_xlabel('Frequência angular ω (rad/s)')
axes[2].set_ylabel('Fase (graus)')
axes[2].set_title('Espectro de Fase')
axes[2].set_xlim([-10, 10])
axes[2].set_ylim([-100, 100])
axes[2].axhline(y=0, color='k', linestyle='-', linewidth=0.5)
axes[2].axvline(x=0, color='k', linestyle='-', linewidth=0.5)

plt.tight_layout()
plt.savefig('../exponential_fourier.pdf', bbox_inches='tight')
plt.savefig('../exponential_fourier.png', dpi=300, bbox_inches='tight')
print("Figura salva: exponential_fourier.pdf/png")
plt.close()
