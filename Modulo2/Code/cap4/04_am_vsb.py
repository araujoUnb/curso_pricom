#!/usr/bin/env python3
"""
Script 04: AM VSB - Vestigial Sideband
Gera: Filtro VSB e comparação espectral DSB/SSB/VSB
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy import signal

plt.rcParams['font.size'] = 10
plt.rcParams['axes.grid'] = True

# Parâmetros
W = 4200  # Largura de banda da mensagem (Hz) - típico de vídeo
fc = 50000  # Frequência da portadora (Hz)
f_vest = 1250  # Largura do vestígio (Hz)
fs = 200000  # Taxa de amostragem
N = 2048

# Frequências
freq = np.fft.fftfreq(N, 1/fs)
pos_freq = freq[:N//2]

# Criar filtro VSB ideal
H_vsb = np.zeros(N, dtype=complex)
for i, f in enumerate(freq):
    f_abs = np.abs(f)
    if f_abs < fc - W:
        H_vsb[i] = 0
    elif fc - W <= f_abs < fc - f_vest:
        # Transição linear (vestígio)
        H_vsb[i] = (f_abs - (fc - W)) / (W - f_vest)
    elif fc - f_vest <= f_abs < fc + W:
        H_vsb[i] = 1
    else:
        H_vsb[i] = 0

# Filtros para comparação
H_dsb = np.where((pos_freq >= fc - W) & (pos_freq <= fc + W), 1, 0)
H_ssb = np.where((pos_freq >= fc) & (pos_freq <= fc + W), 1, 0)
H_vsb_pos = np.abs(H_vsb[:N//2])

# Criar figura
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# Subplot 1: Filtro VSB detalhado
ax1 = axes[0, 0]
ax1.plot(pos_freq/1000, H_vsb_pos, 'b-', linewidth=2)
ax1.axvline(x=fc/1000, color='r', linestyle='--', linewidth=1.5, label='fc')
ax1.axvline(x=(fc-W)/1000, color='g', linestyle=':', alpha=0.7, label='fc-W')
ax1.axvline(x=(fc+W)/1000, color='g', linestyle=':', alpha=0.7, label='fc+W')
ax1.axvline(x=(fc-f_vest)/1000, color='m', linestyle='-.', alpha=0.7, 
           label=f'Início vestígio')
ax1.set_xlabel('Frequência (kHz)')
ax1.set_ylabel('|H_VSB(f)|')
ax1.set_title('Característica do Filtro VSB')
ax1.set_xlim([40, 60])
ax1.set_ylim([-0.1, 1.2])
ax1.legend(fontsize=8)
ax1.grid(True, alpha=0.3)

# Marcar região de vestígio
vest_region = (pos_freq >= fc - W) & (pos_freq < fc - f_vest)
ax1.fill_between(pos_freq[vest_region]/1000, 0, H_vsb_pos[vest_region], 
                alpha=0.3, color='orange', label='Vestígio')

# Subplot 2: Comparação de filtros
ax2 = axes[0, 1]
ax2.plot(pos_freq/1000, H_dsb, 'b-', linewidth=2, alpha=0.7, label='DSB')
ax2.plot(pos_freq/1000, H_ssb, 'r-', linewidth=2, alpha=0.7, label='SSB-USB')
ax2.plot(pos_freq/1000, H_vsb_pos, 'g-', linewidth=2, alpha=0.7, label='VSB')
ax2.axvline(x=fc/1000, color='k', linestyle=':', alpha=0.5)
ax2.set_xlabel('Frequência (kHz)')
ax2.set_ylabel('|H(f)|')
ax2.set_title('Comparação: DSB vs SSB vs VSB')
ax2.set_xlim([40, 60])
ax2.set_ylim([-0.1, 1.2])
ax2.legend()
ax2.grid(True, alpha=0.3)

# Subplot 3: Simetria vestigial
ax3 = axes[1, 0]
# Zoom na região de transição
zoom_range = (pos_freq >= fc - 2*f_vest) & (pos_freq <= fc + 2*f_vest)
f_zoom = pos_freq[zoom_range] - fc
H_zoom = H_vsb_pos[zoom_range]

ax3.plot(f_zoom/1000, H_zoom, 'b-', linewidth=2)
ax3.axvline(x=0, color='r', linestyle='--', linewidth=1.5, label='fc')
ax3.axhline(y=0.5, color='k', linestyle=':', alpha=0.5)
ax3.set_xlabel('Frequência relativa a fc (kHz)')
ax3.set_ylabel('|H_VSB(f)|')
ax3.set_title('Simetria Vestigial em torno de fc')
ax3.grid(True, alpha=0.3)
ax3.legend()

# Verificar simetria: H(fc+f) + H(fc-f) = constante
f_check = np.linspace(0, f_vest, 50)
symmetry_sum = []
for f in f_check:
    idx_pos = np.argmin(np.abs(pos_freq - (fc + f)))
    idx_neg = np.argmin(np.abs(pos_freq - (fc - f)))
    symmetry_sum.append(H_vsb_pos[idx_pos] + H_vsb_pos[idx_neg])

ax3_twin = ax3.twinx()
ax3_twin.plot(f_check/1000, symmetry_sum, 'r--', linewidth=1.5, alpha=0.7, 
             label='H(fc+f) + H(fc-f)')
ax3_twin.set_ylabel('Soma (deve ser constante)', color='r')
ax3_twin.tick_params(axis='y', labelcolor='r')
ax3_twin.legend(loc='upper right')

# Subplot 4: Largura de banda comparativa
ax4 = axes[1, 1]
tipos = ['DSB', 'VSB', 'SSB']
larguras = [2*W, W + f_vest, W]
cores = ['blue', 'green', 'red']

bars = ax4.bar(tipos, np.array(larguras)/1000, color=cores, alpha=0.7, edgecolor='black')
ax4.set_ylabel('Largura de Banda (kHz)')
ax4.set_title(f'Comparação de Largura de Banda (W = {W/1000} kHz)')
ax4.grid(True, axis='y', alpha=0.3)

# Adicionar valores nas barras
for bar, largura in zip(bars, larguras):
    height = bar.get_height()
    ax4.text(bar.get_x() + bar.get_width()/2., height,
            f'{largura/1000:.1f} kHz',
            ha='center', va='bottom', fontweight='bold')

# Adicionar linha de referência para W
ax4.axhline(y=W/1000, color='black', linestyle='--', linewidth=1, alpha=0.5, label=f'W = {W/1000} kHz')
ax4.legend()

plt.suptitle('AM VSB: Vestigial Sideband', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig('../am_vsb.pdf', bbox_inches='tight')
plt.savefig('../am_vsb.png', dpi=300, bbox_inches='tight')
print("Figura salva: am_vsb.pdf/png")
plt.close()
