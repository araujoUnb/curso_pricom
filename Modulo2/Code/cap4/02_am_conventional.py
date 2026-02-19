#!/usr/bin/env python3
"""
Script 02: AM Convencional - Diferentes índices de modulação
Gera: Comparação de envelopes para μ = 0.5, 1.0 e 1.5 (supermodulação)
"""

import numpy as np
import matplotlib.pyplot as plt

plt.rcParams['font.size'] = 10
plt.rcParams['axes.grid'] = True

# Parâmetros
fm = 1000  # Frequência da mensagem (Hz)
fc = 10000  # Frequência da portadora (Hz)
Ac = 1.0  # Amplitude da portadora
fs = 100000  # Taxa de amostragem
T = 0.003  # Duração (3 ms)

# Vetores de tempo
t = np.arange(0, T, 1/fs)

# Mensagem normalizada
m_n = np.cos(2*np.pi*fm*t)

# Diferentes índices de modulação
modulation_indices = [0.5, 1.0, 1.5]
colors = ['blue', 'green', 'red']
labels = ['μ = 0.5 (50%)', 'μ = 1.0 (100%)', 'μ = 1.5 (Supermodulação)']

# Criar figura
fig, axes = plt.subplots(3, 2, figsize=(14, 10))

for idx, (mu, color, label) in enumerate(zip(modulation_indices, colors, labels)):
    # Sinal AM
    s_am = Ac * (1 + mu * m_n) * np.cos(2*np.pi*fc*t)
    envelope_pos = Ac * (1 + mu * m_n)
    envelope_neg = -envelope_pos
    
    # Subplot: Sinal no tempo
    ax_time = axes[idx, 0]
    ax_time.plot(t*1000, s_am, color, linewidth=1, alpha=0.7)
    ax_time.plot(t*1000, envelope_pos, 'k--', linewidth=2, label='Envelope')
    ax_time.plot(t*1000, envelope_neg, 'k--', linewidth=2)
    ax_time.axhline(y=0, color='k', linestyle='-', linewidth=0.5)
    ax_time.set_xlabel('Tempo (ms)')
    ax_time.set_ylabel('s(t)')
    ax_time.set_title(f'Sinal AM - {label}')
    ax_time.set_xlim([0, 3])
    ax_time.legend()
    ax_time.grid(True, alpha=0.3)
    
    # Destacar supermodulação
    if mu > 1.0:
        # Marcar regiões de envelope negativo
        negative_regions = envelope_pos < 0
        if np.any(negative_regions):
            ax_time.fill_between(t*1000, -1.5, 1.5, where=negative_regions, 
                                alpha=0.2, color='red', label='Envelope negativo')
    
    # Subplot: Espectro
    ax_freq = axes[idx, 1]
    S_f = np.fft.fft(s_am)
    N = len(t)
    freq = np.fft.fftfreq(N, 1/fs)
    pos_freq = freq[:N//2]
    S_mag = np.abs(S_f[:N//2]) / N
    
    color_code = color[0]
    ax_freq.stem(pos_freq, S_mag, basefmt=' ', linefmt=color_code+'-', markerfmt=color_code+'o')
    ax_freq.set_xlabel('Frequência (Hz)')
    ax_freq.set_ylabel('|S(f)|')
    ax_freq.set_title(f'Espectro - {label}')
    ax_freq.set_xlim([8000, 12000])
    ax_freq.axvline(x=fc, color='k', linestyle=':', alpha=0.5, linewidth=1.5)
    ax_freq.grid(True, alpha=0.3)

plt.suptitle('AM Convencional: Efeito do Índice de Modulação μ', 
             fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig('../am_conventional.pdf', bbox_inches='tight')
plt.savefig('../am_conventional.png', dpi=300, bbox_inches='tight')
print("Figura salva: am_conventional.pdf/png")
plt.close()

# Gráfico de eficiência vs μ
fig2, ax = plt.subplots(figsize=(10, 6))
mu_range = np.linspace(0, 1.5, 100)
efficiency = mu_range**2 / (2 + mu_range**2)

ax.plot(mu_range, efficiency * 100, 'b-', linewidth=2)
ax.set_xlabel('Índice de Modulação μ')
ax.set_ylabel('Eficiência de Potência (%)')
ax.set_title('Eficiência de Potência do AM Convencional (Tom Único)')
ax.grid(True, alpha=0.3)
ax.axhline(y=33.33, color='r', linestyle='--', linewidth=1.5, 
          label='Máximo teórico (33.3% em μ=1)')
ax.axvline(x=1.0, color='r', linestyle='--', linewidth=1.5, alpha=0.5)
ax.set_xlim([0, 1.5])
ax.set_ylim([0, 50])
ax.legend()

# Marcar pontos importantes
ax.plot([0.5, 1.0], [efficiency[50]*100, 33.33], 'ro', markersize=10)
ax.text(0.5, efficiency[50]*100 + 2, f'{efficiency[50]*100:.1f}%', ha='center')
ax.text(1.0, 35, '33.3%', ha='center')

plt.tight_layout()
plt.savefig('../am_efficiency.pdf', bbox_inches='tight')
plt.savefig('../am_efficiency.png', dpi=300, bbox_inches='tight')
print("Figura salva: am_efficiency.pdf/png")
plt.close()
