#!/usr/bin/env python3
"""
Script 04: Exemplo de Convolução no Tempo vs Multiplicação na Frequência
Demonstra a propriedade de convolução da Transformada de Fourier
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy import signal

plt.rcParams['font.size'] = 10
plt.rcParams['axes.grid'] = True

# Parâmetros
N = 512
dt = 0.01
t = np.arange(N) * dt

# Sinal 1: Pulso retangular
signal1 = np.zeros(N)
signal1[100:150] = 1.0

# Sinal 2: Exponencial decrescente
signal2 = np.zeros(N)
signal2[150:] = np.exp(-0.5 * np.arange(N-150) * dt)

# Convolução no tempo
conv_result = signal.convolve(signal1, signal2, mode='same') * dt

# Transformadas de Fourier
freq = np.fft.fftfreq(N, dt)
F1 = np.fft.fft(signal1)
F2 = np.fft.fft(signal2)
F_product = F1 * F2
result_freq = np.fft.ifft(F_product).real

# Criar figura
fig = plt.figure(figsize=(12, 10))
gs = fig.add_gridspec(3, 2, hspace=0.3, wspace=0.3)

# Subplot 1: Sinal 1 no tempo
ax1 = fig.add_subplot(gs[0, 0])
ax1.plot(t, signal1, 'b', linewidth=2)
ax1.set_xlabel('Tempo (s)')
ax1.set_ylabel('x₁(t)')
ax1.set_title('Sinal 1: Pulso Retangular')
ax1.set_xlim([0, N*dt])

# Subplot 2: Espectro de Sinal 1
ax2 = fig.add_subplot(gs[0, 1])
ax2.plot(freq[:N//2], np.abs(F1[:N//2]), 'b', linewidth=2)
ax2.set_xlabel('Frequência (Hz)')
ax2.set_ylabel('|X₁(f)|')
ax2.set_title('Espectro de Magnitude')
ax2.set_xlim([0, 20])

# Subplot 3: Sinal 2 no tempo
ax3 = fig.add_subplot(gs[1, 0])
ax3.plot(t, signal2, 'r', linewidth=2)
ax3.set_xlabel('Tempo (s)')
ax3.set_ylabel('x₂(t)')
ax3.set_title('Sinal 2: Exponencial Decrescente')
ax3.set_xlim([0, N*dt])

# Subplot 4: Espectro de Sinal 2
ax4 = fig.add_subplot(gs[1, 1])
ax4.plot(freq[:N//2], np.abs(F2[:N//2]), 'r', linewidth=2)
ax4.set_xlabel('Frequência (Hz)')
ax4.set_ylabel('|X₂(f)|')
ax4.set_title('Espectro de Magnitude')
ax4.set_xlim([0, 20])

# Subplot 5: Convolução no tempo
ax5 = fig.add_subplot(gs[2, 0])
ax5.plot(t, conv_result, 'g', linewidth=2)
ax5.set_xlabel('Tempo (s)')
ax5.set_ylabel('y(t) = x₁(t) * x₂(t)')
ax5.set_title('Resultado: Convolução no Tempo')
ax5.set_xlim([0, N*dt])

# Subplot 6: Produto no domínio da frequência
ax6 = fig.add_subplot(gs[2, 1])
ax6.plot(freq[:N//2], np.abs(F_product[:N//2]), 'g', linewidth=2)
ax6.set_xlabel('Frequência (Hz)')
ax6.set_ylabel('|Y(f)| = |X₁(f)·X₂(f)|')
ax6.set_title('Resultado: Produto na Frequência')
ax6.set_xlim([0, 20])

plt.suptitle('Propriedade de Convolução: x₁(t) * x₂(t) ↔ X₁(f)·X₂(f)', 
             fontsize=14, fontweight='bold')

plt.savefig('../convolution_example.pdf', bbox_inches='tight')
plt.savefig('../convolution_example.png', dpi=300, bbox_inches='tight')
print("Figura salva: convolution_example.pdf/png")
plt.close()
