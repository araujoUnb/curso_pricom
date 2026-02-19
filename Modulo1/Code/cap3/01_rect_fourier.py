#!/usr/bin/env python3
"""
Script 01: Pulso Retangular e sua Transformada de Fourier
Gera: Sinal no tempo e espectro de magnitude/fase
"""

import numpy as np
import matplotlib.pyplot as plt

# Configurações
plt.rcParams['font.size'] = 12
plt.rcParams['axes.grid'] = True

# Parâmetros do pulso
A = 1.0  # Amplitude
tau = 1.0  # Duração

# Domínio do tempo
t = np.linspace(-3*tau, 3*tau, 1000)
f_t = A * np.where(np.abs(t) <= tau/2, 1, 0)

# Domínio da frequência (rad/s)
omega = np.linspace(-20/tau, 20/tau, 2000)
# Evitar divisão por zero
omega_safe = np.where(omega == 0, 1e-10, omega)
F_omega = A * tau * np.sinc(omega_safe * tau / (2*np.pi))

# Criar figura
fig, axes = plt.subplots(2, 1, figsize=(10, 8))

# Subplot 1: Sinal no tempo
axes[0].plot(t, f_t, 'b', linewidth=2)
axes[0].set_xlabel('Tempo t (s)')
axes[0].set_ylabel('f(t)')
axes[0].set_title(f'Pulso Retangular: A={A}, τ={tau}')
axes[0].set_xlim([-3*tau, 3*tau])
axes[0].set_ylim([-0.2, 1.3])
axes[0].axhline(y=0, color='k', linestyle='-', linewidth=0.5)
axes[0].axvline(x=0, color='k', linestyle='-', linewidth=0.5)

# Subplot 2: Espectro de magnitude
axes[1].plot(omega, np.abs(F_omega), 'r', linewidth=2)
axes[1].set_xlabel('Frequência angular ω (rad/s)')
axes[1].set_ylabel('|F(ω)|')
axes[1].set_title('Espectro de Magnitude (Função Sinc)')
axes[1].set_xlim([-20/tau, 20/tau])
axes[1].axhline(y=0, color='k', linestyle='-', linewidth=0.5)
axes[1].axvline(x=0, color='k', linestyle='-', linewidth=0.5)
# Marcar zeros
zeros = np.array([2*np.pi/tau, 4*np.pi/tau])
axes[1].plot(zeros, np.zeros_like(zeros), 'ro', markersize=8, label='Zeros')
axes[1].plot(-zeros, np.zeros_like(zeros), 'ro', markersize=8)
axes[1].legend()

plt.tight_layout()
plt.savefig('../rect_fourier.pdf', bbox_inches='tight')
plt.savefig('../rect_fourier.png', dpi=300, bbox_inches='tight')
print("Figura salva: rect_fourier.pdf/png")
plt.close()
