#!/usr/bin/env python3
"""
Script 10: Receptor Superheterodino
Gera: Conversão de frequência e espectros em cada estágio
"""

import numpy as np
import matplotlib.pyplot as plt

plt.rcParams['font.size'] = 10
plt.rcParams['axes.grid'] = True

# Gráfico 1: Conversão de frequência - princípio
fig1, axes = plt.subplots(2, 2, figsize=(14, 10))

# Parâmetros
f_rf = 100  # MHz (estação desejada)
f_lo = 110.7  # MHz (oscilador local)
f_if = 10.7  # MHz (frequência intermediária)
BW = 0.2  # MHz (largura de banda do sinal)

# Subplot 1: Espectro RF (entrada)
ax1 = axes[0, 0]
freq_rf = np.array([f_rf - BW/2, f_rf, f_rf + BW/2])
mag_rf = np.array([0.5, 1.0, 0.5])

ax1.stem(freq_rf, mag_rf, basefmt=' ', linefmt='b-', markerfmt='bo')
ax1.set_xlabel('Frequência (MHz)')
ax1.set_ylabel('Magnitude')
ax1.set_title(f'Sinal RF (fRF = {f_rf} MHz)')
ax1.set_xlim([f_rf-5, f_rf+5])
ax1.grid(True, alpha=0.3)
ax1.text(f_rf, 1.1, f'{f_rf} MHz', ha='center', fontweight='bold',
        bbox=dict(boxstyle='round', facecolor='lightblue'))

# Subplot 2: Oscilador Local
ax2 = axes[0, 1]
ax2.stem([f_lo], [1.0], basefmt=' ', linefmt='r-', markerfmt='ro')
ax2.set_xlabel('Frequência (MHz)')
ax2.set_ylabel('Magnitude')
ax2.set_title(f'Oscilador Local (fLO = {f_lo} MHz)')
ax2.set_xlim([f_lo-5, f_lo+5])
ax2.grid(True, alpha=0.3)
ax2.text(f_lo, 1.1, f'{f_lo} MHz', ha='center', fontweight='bold',
        bbox=dict(boxstyle='round', facecolor='lightcoral'))

# Subplot 3: Produtos de mistura
ax3 = axes[1, 0]
# Soma: f_rf + f_lo
freq_sum = np.array([f_rf + f_lo - BW/2, f_rf + f_lo, f_rf + f_lo + BW/2])
mag_sum = np.array([0.25, 0.5, 0.25])
# Diferença: |f_rf - f_lo| = f_if
freq_diff = np.array([f_if - BW/2, f_if, f_if + BW/2])
mag_diff = np.array([0.25, 0.5, 0.25])

ax3.stem(freq_sum, mag_sum, basefmt=' ', linefmt='m-', markerfmt='ms', label='Soma (rejeitada)')
ax3.stem(freq_diff, mag_diff, basefmt=' ', linefmt='g-', markerfmt='go', label='Diferença (IF)')
ax3.set_xlabel('Frequência (MHz)')
ax3.set_ylabel('Magnitude')
ax3.set_title('Produtos de Mistura')
ax3.set_xlim([0, 220])
ax3.legend()
ax3.grid(True, alpha=0.3)

# Marcar regiões
ax3.axvspan(f_if-1, f_if+1, alpha=0.2, color='green')
ax3.text(f_if, 0.6, f'IF\n{f_if} MHz', ha='center',
        bbox=dict(boxstyle='round', facecolor='lightgreen'))
ax3.text(f_rf + f_lo, 0.6, f'Soma\n{f_rf + f_lo:.1f} MHz', ha='center',
        bbox=dict(boxstyle='round', facecolor='pink'))

# Subplot 4: Saída IF após filtragem
ax4 = axes[1, 1]
ax4.stem(freq_diff, mag_diff, basefmt=' ', linefmt='g-', markerfmt='go')
ax4.set_xlabel('Frequência (MHz)')
ax4.set_ylabel('Magnitude')
ax4.set_title(f'Sinal IF após Filtragem ({f_if} MHz)')
ax4.set_xlim([f_if-5, f_if+5])
ax4.grid(True, alpha=0.3)
ax4.axvspan(f_if - BW, f_if + BW, alpha=0.2, color='green')
ax4.text(f_if, 0.6, f'BW = {BW} MHz', ha='center',
        bbox=dict(boxstyle='round', facecolor='lightgreen'))

plt.suptitle('Receptor Superheterodino: Conversão de Frequência', 
            fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig('../superheterodyne_conversion.pdf', bbox_inches='tight')
plt.savefig('../superheterodyne_conversion.png', dpi=300, bbox_inches='tight')
print("Figura salva: superheterodyne_conversion.pdf/png")
plt.close()

# Gráfico 2: Problema da frequência imagem
fig2, axes = plt.subplots(2, 1, figsize=(14, 8))

# Parâmetros
f_desired = 100  # MHz
f_image = f_lo + f_if  # MHz = 121.4

# Subplot 1: Espectro de entrada (com sinal desejado e imagem)
ax1 = axes[0]
signals = [
    (f_desired, 'Sinal Desejado', 'blue'),
    (f_image, 'Frequência Imagem', 'red')
]

for f, label, color in signals:
    freq = np.array([f - BW/2, f, f + BW/2])
    mag = np.array([0.5, 1.0, 0.5])
    ax1.stem(freq, mag, basefmt=' ', linefmt=f'{color[0]}-', 
            markerfmt=f'{color[0]}o', label=label)

ax1.axvline(x=f_lo, color='green', linestyle='--', linewidth=2, 
           label=f'fLO = {f_lo} MHz')
ax1.set_xlabel('Frequência (MHz)')
ax1.set_ylabel('Magnitude')
ax1.set_title('Problema da Frequência Imagem')
ax1.set_xlim([95, 125])
ax1.legend()
ax1.grid(True, alpha=0.3)

# Marcar conversões
ax1.annotate('', xy=(f_if, 0.3), xytext=(f_desired, 0.3),
            arrowprops=dict(arrowstyle='<->', color='blue', lw=2))
ax1.text((f_desired + f_if)/2, 0.35, f'{f_lo - f_desired} MHz', ha='center')

ax1.annotate('', xy=(f_image, 0.2), xytext=(f_lo, 0.2),
            arrowprops=dict(arrowstyle='<->', color='red', lw=2))
ax1.text((f_image + f_lo)/2, 0.25, f'{f_image - f_lo} MHz', ha='center')

# Subplot 2: Espectro IF (ambos sinais convertidos para IF)
ax2 = axes[1]
freq_if = np.array([f_if - BW/2, f_if, f_if + BW/2])
mag_desired = np.array([0.5, 1.0, 0.5])
mag_image = np.array([0.3, 0.6, 0.3])

# Sinal combinado
mag_combined = mag_desired + mag_image

ax2.stem(freq_if, mag_desired, basefmt=' ', linefmt='b-', 
        markerfmt='bo', label='Do sinal desejado')
ax2.stem(freq_if, mag_combined, basefmt=' ', linefmt='r-', 
        markerfmt='ro', label='Com interferência da imagem')
ax2.set_xlabel('Frequência (MHz)')
ax2.set_ylabel('Magnitude')
ax2.set_title('Sinal IF: Interferência da Frequência Imagem')
ax2.set_xlim([f_if-5, f_if+5])
ax2.legend()
ax2.grid(True, alpha=0.3)
ax2.text(f_if, max(mag_combined)*1.1, 'Interferência!\nFiltro RF necessário', ha='center',
        bbox=dict(boxstyle='round', facecolor='yellow'))

plt.suptitle('Problema da Frequência Imagem no Superheterodino', 
            fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig('../superheterodyne_image.pdf', bbox_inches='tight')
plt.savefig('../superheterodyne_image.png', dpi=300, bbox_inches='tight')
print("Figura salva: superheterodyne_image.pdf/png")
plt.close()

# Gráfico 3: Resposta do filtro de imagem
fig3, ax = plt.subplots(figsize=(12, 6))

# Frequências
freq = np.linspace(85, 125, 1000)

# Filtro RF (passa-faixa centrado em f_desired)
Q = 50  # Fator de qualidade
f0 = f_desired
BW_filter = f0 / Q

# Resposta do filtro (aproximação Butterworth)
H_rf = 1 / np.sqrt(1 + ((freq - f0) / (BW_filter/2))**(2*4))  # 4ª ordem

ax.plot(freq, H_rf, 'b-', linewidth=2.5, label='Filtro RF (passa-faixa)')
ax.axvline(x=f_desired, color='green', linestyle='--', linewidth=2, label=f'Sinal desejado ({f_desired} MHz)')
ax.axvline(x=f_image, color='red', linestyle='--', linewidth=2, label=f'Frequência imagem ({f_image:.1f} MHz)')
ax.set_xlabel('Frequência (MHz)')
ax.set_ylabel('Resposta do Filtro')
ax.set_title('Filtro RF para Rejeição da Frequência Imagem')
ax.grid(True, alpha=0.3)
ax.legend()

# Marcar rejeição
rejection = H_rf[np.argmin(np.abs(freq - f_image))]
ax.plot([f_image], [rejection], 'ro', markersize=10)
ax.annotate(f'Rejeição: {-20*np.log10(rejection):.1f} dB',
           xy=(f_image, rejection), xytext=(f_image+5, rejection+0.2),
           arrowprops=dict(arrowstyle='->', color='red'),
           bbox=dict(boxstyle='round', facecolor='yellow'))

plt.tight_layout()
plt.savefig('../superheterodyne_filter.pdf', bbox_inches='tight')
plt.savefig('../superheterodyne_filter.png', dpi=300, bbox_inches='tight')
print("Figura salva: superheterodyne_filter.pdf/png")
plt.close()

print("\nTodos os scripts FM foram criados com sucesso!")
