#!/usr/bin/env python3
"""
Script 05: Comparação Completa de Tipos de AM
Gera: Espectros lado a lado e gráfico comparativo de características
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import hilbert

plt.rcParams['font.size'] = 10
plt.rcParams['axes.grid'] = True

# Parâmetros
fm = 1000
fc = 10000
Ac = 1.0
mu = 0.8
fs = 100000
T = 0.005

t = np.arange(0, T, 1/fs)
N = len(t)

# Sinal modulante
m_t = np.cos(2*np.pi*fm*t)
m_hat = np.imag(hilbert(m_t))

# Diferentes sinais AM
s_dsb_sc = Ac * m_t * np.cos(2*np.pi*fc*t)
s_am_conv = Ac * (1 + mu * m_t) * np.cos(2*np.pi*fc*t)
s_ssb_usb = (Ac/2) * (m_t * np.cos(2*np.pi*fc*t) - m_hat * np.sin(2*np.pi*fc*t))

# Espectros
freq = np.fft.fftfreq(N, 1/fs)
pos_freq = freq[:N//2]

DSB_SC_f = np.abs(np.fft.fft(s_dsb_sc)[:N//2]) / N
AM_Conv_f = np.abs(np.fft.fft(s_am_conv)[:N//2]) / N
SSB_USB_f = np.abs(np.fft.fft(s_ssb_usb)[:N//2]) / N

# Figura principal: Espectros comparativos
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# DSB-SC
ax1 = axes[0, 0]
ax1.stem(pos_freq, DSB_SC_f, basefmt=' ', linefmt='b-', markerfmt='bo')
ax1.set_title('DSB-SC: Portadora Suprimida')
ax1.set_xlabel('Frequência (Hz)')
ax1.set_ylabel('Magnitude')
ax1.set_xlim([8000, 12000])
ax1.axvline(x=fc, color='r', linestyle=':', label='fc', alpha=0.7)
ax1.text(fc-fm, max(DSB_SC_f)*0.85, 'LSB', ha='center', bbox=dict(boxstyle='round', facecolor='wheat'))
ax1.text(fc+fm, max(DSB_SC_f)*0.85, 'USB', ha='center', bbox=dict(boxstyle='round', facecolor='wheat'))
ax1.grid(True, alpha=0.3)
ax1.legend()

# AM Convencional
ax2 = axes[0, 1]
ax2.stem(pos_freq, AM_Conv_f, basefmt=' ', linefmt='g-', markerfmt='go')
ax2.set_title(f'AM Convencional (μ = {mu})')
ax2.set_xlabel('Frequência (Hz)')
ax2.set_ylabel('Magnitude')
ax2.set_xlim([8000, 12000])
ax2.axvline(x=fc, color='r', linestyle=':', label='fc', alpha=0.7)
ax2.text(fc, max(AM_Conv_f)*0.9, 'Portadora', ha='center', 
        bbox=dict(boxstyle='round', facecolor='lightcoral'))
ax2.grid(True, alpha=0.3)
ax2.legend()

# SSB-USB
ax3 = axes[1, 0]
ax3.stem(pos_freq, SSB_USB_f, basefmt=' ', linefmt='m-', markerfmt='mo')
ax3.set_title('SSB-USB: Banda Lateral Superior')
ax3.set_xlabel('Frequência (Hz)')
ax3.set_ylabel('Magnitude')
ax3.set_xlim([8000, 12000])
ax3.axvline(x=fc, color='r', linestyle=':', label='fc', alpha=0.7)
ax3.text(fc+fm, max(SSB_USB_f)*0.85, 'USB apenas', ha='center', 
        bbox=dict(boxstyle='round', facecolor='lightgreen'))
ax3.grid(True, alpha=0.3)
ax3.legend()

# Comparação sobreposta
ax4 = axes[1, 1]
ax4.plot(pos_freq, DSB_SC_f, 'b-', linewidth=1.5, alpha=0.6, label='DSB-SC')
ax4.plot(pos_freq, AM_Conv_f, 'g-', linewidth=1.5, alpha=0.6, label='AM Conv.')
ax4.plot(pos_freq, SSB_USB_f, 'm-', linewidth=1.5, alpha=0.6, label='SSB-USB')
ax4.set_title('Comparação Direta dos Espectros')
ax4.set_xlabel('Frequência (Hz)')
ax4.set_ylabel('Magnitude')
ax4.set_xlim([8000, 12000])
ax4.axvline(x=fc, color='r', linestyle=':', alpha=0.5)
ax4.legend()
ax4.grid(True, alpha=0.3)

plt.suptitle('Comparação Espectral: DSB-SC vs AM Convencional vs SSB', 
             fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig('../am_comparison.pdf', bbox_inches='tight')
plt.savefig('../am_comparison.png', dpi=300, bbox_inches='tight')
print("Figura salva: am_comparison.pdf/png")
plt.close()

# Gráfico de características (radar plot)
categories = ['Eficiência\nBanda', 'Eficiência\nPotência', 'Simplicidade\nTX', 
              'Simplicidade\nRX', 'Robustez']
N_cat = len(categories)

# Valores normalizados (0-1, maior é melhor)
dsb_sc_vals = [0.5, 0.9, 0.9, 0.5, 0.7]  # DSB-SC
am_conv_vals = [0.5, 0.3, 1.0, 1.0, 0.6]  # AM Convencional
ssb_vals = [1.0, 1.0, 0.3, 0.3, 0.4]  # SSB
vsb_vals = [0.7, 0.7, 0.5, 0.5, 0.6]  # VSB

angles = np.linspace(0, 2*np.pi, N_cat, endpoint=False).tolist()
dsb_sc_vals += dsb_sc_vals[:1]
am_conv_vals += am_conv_vals[:1]
ssb_vals += ssb_vals[:1]
vsb_vals += vsb_vals[:1]
angles += angles[:1]

fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection='polar'))
ax.plot(angles, dsb_sc_vals, 'o-', linewidth=2, label='DSB-SC', color='blue')
ax.fill(angles, dsb_sc_vals, alpha=0.15, color='blue')
ax.plot(angles, am_conv_vals, 's-', linewidth=2, label='AM Conv.', color='green')
ax.fill(angles, am_conv_vals, alpha=0.15, color='green')
ax.plot(angles, ssb_vals, '^-', linewidth=2, label='SSB', color='red')
ax.fill(angles, ssb_vals, alpha=0.15, color='red')
ax.plot(angles, vsb_vals, 'd-', linewidth=2, label='VSB', color='orange')
ax.fill(angles, vsb_vals, alpha=0.15, color='orange')

ax.set_xticks(angles[:-1])
ax.set_xticklabels(categories)
ax.set_ylim(0, 1)
ax.set_yticks([0.2, 0.4, 0.6, 0.8, 1.0])
ax.set_yticklabels(['20%', '40%', '60%', '80%', '100%'])
ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))
ax.set_title('Comparação de Características das Variantes AM\n(Maior = Melhor)', 
            pad=20, fontsize=12, fontweight='bold')
ax.grid(True)

plt.tight_layout()
plt.savefig('../am_radar_comparison.pdf', bbox_inches='tight')
plt.savefig('../am_radar_comparison.png', dpi=300, bbox_inches='tight')
print("Figura salva: am_radar_comparison.pdf/png")
plt.close()
