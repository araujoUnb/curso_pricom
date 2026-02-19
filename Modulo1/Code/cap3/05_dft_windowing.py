#!/usr/bin/env python3
"""
Script 05: Efeito de Janelamento na DFT
Demonstra vazamento espectral com diferentes janelas
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy import signal as sig

plt.rcParams['font.size'] = 10
plt.rcParams['axes.grid'] = True

# Parâmetros
fs = 1000  # Taxa de amostragem (Hz)
N = 256    # Número de amostras
t = np.arange(N) / fs
f0 = 100.5  # Frequência da senoide (não múltiplo exato de fs/N!)

# Sinal: senoide
x = np.sin(2*np.pi*f0*t)

# Diferentes janelas
windows = {
    'Retangular': np.ones(N),
    'Hanning': sig.windows.hann(N),
    'Hamming': sig.windows.hamming(N),
    'Blackman': sig.windows.blackman(N)
}

# Frequências para plotagem
freqs = np.fft.fftfreq(N, 1/fs)
positive_freqs = freqs[:N//2]

# Criar figura
fig, axes = plt.subplots(2, 2, figsize=(14, 10))
axes = axes.flatten()

for idx, (name, window) in enumerate(windows.items()):
    # Aplicar janela
    x_windowed = x * window
    
    # Calcular FFT
    X = np.fft.fft(x_windowed)
    X_mag = np.abs(X[:N//2]) / N
    X_db = 20 * np.log10(X_mag + 1e-10)
    
    # Plotar
    axes[idx].plot(positive_freqs, X_db, linewidth=2)
    axes[idx].set_xlabel('Frequência (Hz)')
    axes[idx].set_ylabel('Magnitude (dB)')
    axes[idx].set_title(f'Janela: {name}')
    axes[idx].set_xlim([0, 200])
    axes[idx].set_ylim([-80, 20])
    axes[idx].axvline(x=f0, color='r', linestyle='--', linewidth=1, 
                     label=f'f₀ = {f0} Hz')
    axes[idx].legend()
    axes[idx].grid(True, alpha=0.3)

plt.suptitle(f'Efeito do Janelamento no Vazamento Espectral\n' +
             f'Senoide: {f0} Hz, fs = {fs} Hz, N = {N}',
             fontsize=14, fontweight='bold')
plt.tight_layout()

plt.savefig('../dft_windowing.pdf', bbox_inches='tight')
plt.savefig('../dft_windowing.png', dpi=300, bbox_inches='tight')
print("Figura salva: dft_windowing.pdf/png")
plt.close()
