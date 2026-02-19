#!/usr/bin/env python3
"""
Script 01: AM DSB-SC - Double Sideband Suppressed Carrier
Gera: Sinal modulante, portadora, sinal modulado e espectros
"""

import numpy as np
import matplotlib.pyplot as plt

plt.rcParams['font.size'] = 10
plt.rcParams['axes.grid'] = True

# Parâmetros
fm = 1000  # Frequência da mensagem (Hz)
fc = 10000  # Frequência da portadora (Hz)
Ac = 1.0  # Amplitude da portadora
Am = 0.8  # Amplitude da mensagem
fs = 100000  # Taxa de amostragem
T = 0.005  # Duração (5 ms)

# Vetores de tempo
t = np.arange(0, T, 1/fs)
N = len(t)

# Sinais no tempo
m_t = Am * np.cos(2*np.pi*fm*t)
c_t = Ac * np.cos(2*np.pi*fc*t)
s_dsb_sc = Ac * m_t * np.cos(2*np.pi*fc*t)

# Espectros (FFT)
freq = np.fft.fftfreq(N, 1/fs)
M_f = np.fft.fft(m_t)
C_f = np.fft.fft(c_t)
S_f = np.fft.fft(s_dsb_sc)

# Apenas frequências positivas
pos_freq = freq[:N//2]
M_mag = np.abs(M_f[:N//2]) / N
C_mag = np.abs(C_f[:N//2]) / N
S_mag = np.abs(S_f[:N//2]) / N

# Criar figura
fig = plt.figure(figsize=(14, 10))
gs = fig.add_gridspec(3, 2, hspace=0.35, wspace=0.3)

# Subplot 1: Mensagem no tempo
ax1 = fig.add_subplot(gs[0, 0])
ax1.plot(t*1000, m_t, 'b', linewidth=1.5)
ax1.set_xlabel('Tempo (ms)')
ax1.set_ylabel('m(t)')
ax1.set_title(f'Sinal Modulante (fm = {fm} Hz)')
ax1.set_xlim([0, 3])
ax1.grid(True, alpha=0.3)

# Subplot 2: Espectro da mensagem
ax2 = fig.add_subplot(gs[0, 1])
ax2.stem(pos_freq, M_mag, basefmt=' ', linefmt='b-', markerfmt='bo')
ax2.set_xlabel('Frequência (Hz)')
ax2.set_ylabel('|M(f)|')
ax2.set_title('Espectro da Mensagem')
ax2.set_xlim([0, 5000])
ax2.grid(True, alpha=0.3)

# Subplot 3: Portadora no tempo
ax3 = fig.add_subplot(gs[1, 0])
ax3.plot(t*1000, c_t, 'r', linewidth=1)
ax3.set_xlabel('Tempo (ms)')
ax3.set_ylabel('c(t)')
ax3.set_title(f'Portadora (fc = {fc} Hz)')
ax3.set_xlim([0, 1])
ax3.grid(True, alpha=0.3)

# Subplot 4: Espectro da portadora
ax4 = fig.add_subplot(gs[1, 1])
ax4.stem(pos_freq, C_mag, basefmt=' ', linefmt='r-', markerfmt='ro')
ax4.set_xlabel('Frequência (Hz)')
ax4.set_ylabel('|C(f)|')
ax4.set_title('Espectro da Portadora')
ax4.set_xlim([8000, 12000])
ax4.grid(True, alpha=0.3)

# Subplot 5: DSB-SC no tempo
ax5 = fig.add_subplot(gs[2, 0])
ax5.plot(t*1000, s_dsb_sc, 'g', linewidth=1)
# Envelope
envelope = Ac * np.abs(m_t)
ax5.plot(t*1000, envelope, 'k--', linewidth=1.5, label='Envelope')
ax5.plot(t*1000, -envelope, 'k--', linewidth=1.5)
ax5.set_xlabel('Tempo (ms)')
ax5.set_ylabel('s(t)')
ax5.set_title('Sinal AM DSB-SC')
ax5.set_xlim([0, 3])
ax5.legend()
ax5.grid(True, alpha=0.3)

# Subplot 6: Espectro DSB-SC
ax6 = fig.add_subplot(gs[2, 1])
ax6.stem(pos_freq, S_mag, basefmt=' ', linefmt='g-', markerfmt='go')
ax6.set_xlabel('Frequência (Hz)')
ax6.set_ylabel('|S(f)|')
ax6.set_title('Espectro AM DSB-SC')
ax6.set_xlim([8000, 12000])
ax6.axvline(x=fc, color='r', linestyle=':', alpha=0.5, label='fc')
ax6.axvline(x=fc-fm, color='b', linestyle='--', alpha=0.5, label='LSB')
ax6.axvline(x=fc+fm, color='b', linestyle='--', alpha=0.5, label='USB')
ax6.legend(fontsize=8)
ax6.grid(True, alpha=0.3)

plt.suptitle('AM DSB-SC: Double Sideband Suppressed Carrier', fontsize=14, fontweight='bold')
plt.savefig('../am_dsb_sc.pdf', bbox_inches='tight')
plt.savefig('../am_dsb_sc.png', dpi=300, bbox_inches='tight')
print("Figura salva: am_dsb_sc.pdf/png")
plt.close()
