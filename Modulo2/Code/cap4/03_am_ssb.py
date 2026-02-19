#!/usr/bin/env python3
"""
Script 03: AM SSB - Single Sideband
Gera: Transformada de Hilbert e comparação DSB vs SSB
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import hilbert

plt.rcParams['font.size'] = 10
plt.rcParams['axes.grid'] = True

# Parâmetros
fm = 1000  # Frequência da mensagem (Hz)
fc = 10000  # Frequência da portadora (Hz)
Ac = 1.0
fs = 100000
T = 0.005

# Vetores de tempo
t = np.arange(0, T, 1/fs)
N = len(t)

# Sinal modulante
m_t = np.cos(2*np.pi*fm*t)

# Transformada de Hilbert
m_t_analytic = hilbert(m_t)
m_hat = np.imag(m_t_analytic)  # Parte imaginária é a transformada de Hilbert

# Portadoras em fase e quadratura
c_I = np.cos(2*np.pi*fc*t)
c_Q = np.sin(2*np.pi*fc*t)

# Sinais modulados
s_dsb = Ac * m_t * c_I  # DSB-SC
s_usb = (Ac/2) * (m_t * c_I - m_hat * c_Q)  # SSB-USB
s_lsb = (Ac/2) * (m_t * c_I + m_hat * c_Q)  # SSB-LSB

# Espectros
freq = np.fft.fftfreq(N, 1/fs)
pos_freq = freq[:N//2]

DSB_f = np.fft.fft(s_dsb)
USB_f = np.fft.fft(s_usb)
LSB_f = np.fft.fft(s_lsb)

DSB_mag = np.abs(DSB_f[:N//2]) / N
USB_mag = np.abs(USB_f[:N//2]) / N
LSB_mag = np.abs(LSB_f[:N//2]) / N

# Criar figura
fig = plt.figure(figsize=(14, 10))
gs = fig.add_gridspec(3, 2, hspace=0.35, wspace=0.3)

# Subplot 1: Mensagem e Hilbert no tempo
ax1 = fig.add_subplot(gs[0, :])
ax1.plot(t*1000, m_t, 'b-', linewidth=2, label='m(t) = cos(2πfₘt)')
ax1.plot(t*1000, m_hat, 'r--', linewidth=2, label='m̂(t) = sin(2πfₘt) [Hilbert]')
ax1.set_xlabel('Tempo (ms)')
ax1.set_ylabel('Amplitude')
ax1.set_title('Sinal Modulante e sua Transformada de Hilbert')
ax1.set_xlim([0, 3])
ax1.legend()
ax1.grid(True, alpha=0.3)

# Subplot 2: DSB-SC
ax2 = fig.add_subplot(gs[1, 0])
ax2.plot(t*1000, s_dsb, 'b', linewidth=1)
ax2.set_xlabel('Tempo (ms)')
ax2.set_ylabel('s(t)')
ax2.set_title('AM DSB-SC')
ax2.set_xlim([0, 3])
ax2.grid(True, alpha=0.3)

# Subplot 3: Espectro DSB
ax3 = fig.add_subplot(gs[1, 1])
ax3.stem(pos_freq, DSB_mag, basefmt=' ', linefmt='b-', markerfmt='bo')
ax3.set_xlabel('Frequência (Hz)')
ax3.set_ylabel('|S(f)|')
ax3.set_title('Espectro DSB-SC')
ax3.set_xlim([8000, 12000])
ax3.axvline(x=fc, color='k', linestyle=':', alpha=0.5)
ax3.text(fc-fm, max(DSB_mag)*0.9, 'LSB', ha='center', fontsize=9)
ax3.text(fc+fm, max(DSB_mag)*0.9, 'USB', ha='center', fontsize=9)
ax3.grid(True, alpha=0.3)

# Subplot 4: SSB-USB
ax4 = fig.add_subplot(gs[2, 0])
ax4.plot(t*1000, s_usb, 'g', linewidth=1)
ax4.set_xlabel('Tempo (ms)')
ax4.set_ylabel('s(t)')
ax4.set_title('AM SSB-USB')
ax4.set_xlim([0, 3])
ax4.grid(True, alpha=0.3)

# Subplot 5: Espectro SSB comparado
ax5 = fig.add_subplot(gs[2, 1])
ax5.stem(pos_freq, USB_mag, basefmt=' ', linefmt='g-', markerfmt='go', label='SSB-USB')
ax5.stem(pos_freq, LSB_mag, basefmt=' ', linefmt='m-', markerfmt='ms', label='SSB-LSB')
ax5.set_xlabel('Frequência (Hz)')
ax5.set_ylabel('|S(f)|')
ax5.set_title('Espectro SSB (USB e LSB)')
ax5.set_xlim([8000, 12000])
ax5.axvline(x=fc, color='k', linestyle=':', alpha=0.5)
ax5.legend()
ax5.grid(True, alpha=0.3)

plt.suptitle('AM SSB: Single Sideband usando Transformada de Hilbert', 
             fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig('../am_ssb.pdf', bbox_inches='tight')
plt.savefig('../am_ssb.png', dpi=300, bbox_inches='tight')
print("Figura salva: am_ssb.pdf/png")
plt.close()
