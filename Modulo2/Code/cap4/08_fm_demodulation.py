#!/usr/bin/env python3
"""
Script 08: Demodulação FM - Discriminador e PLL
Gera: Princípio do discriminador, resposta do detector
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy import signal

plt.rcParams['font.size'] = 10
plt.rcParams['axes.grid'] = True

# Parâmetros
fm = 1000  # Hz (mensagem)
fc = 20000  # Hz (portadora)
kf = 5000  # Hz/V (sensibilidade FM)
Ac = 1.0
fs = 200000
T = 0.01

t = np.arange(0, T, 1/fs)

# Sinal modulante
m_t = 0.8 * np.cos(2*np.pi*fm*t)

# Sinal FM
phi_t = 2*np.pi*kf*np.cumsum(m_t)/fs  # Integração discreta
s_fm = Ac * np.cos(2*np.pi*fc*t + phi_t)

# Frequência instantânea
f_inst = fc + kf * m_t

# Gráfico 1: Princípio do discriminador
fig1 = plt.figure(figsize=(14, 10))
gs = fig1.add_gridspec(4, 2, hspace=0.35, wspace=0.3)

# Subplot 1: Mensagem original
ax1 = fig1.add_subplot(gs[0, :])
ax1.plot(t*1000, m_t, 'b-', linewidth=2)
ax1.set_xlabel('Tempo (ms)')
ax1.set_ylabel('m(t)')
ax1.set_title('Sinal Modulante Original')
ax1.grid(True, alpha=0.3)
ax1.set_xlim([0, 5])

# Subplot 2: Sinal FM
ax2 = fig1.add_subplot(gs[1, 0])
ax2.plot(t*1000, s_fm, 'g-', linewidth=1)
ax2.set_xlabel('Tempo (ms)')
ax2.set_ylabel('s_FM(t)')
ax2.set_title('Sinal FM (amplitude constante)')
ax2.grid(True, alpha=0.3)
ax2.set_xlim([0, 3])

# Subplot 3: Frequência instantânea
ax3 = fig1.add_subplot(gs[1, 1])
ax3.plot(t*1000, f_inst/1000, 'g-', linewidth=2)
ax3.axhline(y=fc/1000, color='r', linestyle='--', linewidth=1.5, label='fc')
ax3.fill_between(t*1000, fc/1000, f_inst/1000, alpha=0.3, color='green')
ax3.set_xlabel('Tempo (ms)')
ax3.set_ylabel('Frequência Instantânea (kHz)')
ax3.set_title('fi(t) = fc + kf·m(t)')
ax3.legend()
ax3.grid(True, alpha=0.3)
ax3.set_xlim([0, 5])

# Subplot 4: Derivada do sinal FM
s_fm_derivative = np.diff(s_fm, prepend=s_fm[0]) * fs
ax4 = fig1.add_subplot(gs[2, 0])
ax4.plot(t*1000, s_fm_derivative, 'r-', linewidth=0.8, alpha=0.7)
ax4.set_xlabel('Tempo (ms)')
ax4.set_ylabel('ds_FM/dt')
ax4.set_title('Sinal Derivado (conversão FM → AM)')
ax4.grid(True, alpha=0.3)
ax4.set_xlim([0, 3])

# Subplot 5: Envelope do sinal derivado
envelope = np.abs(signal.hilbert(s_fm_derivative))
ax5 = fig1.add_subplot(gs[2, 1])
ax5.plot(t*1000, envelope, 'r-', linewidth=2)
ax5.set_xlabel('Tempo (ms)')
ax5.set_ylabel('Envelope')
ax5.set_title('Envelope do Sinal Derivado (proporcional a fi(t))')
ax5.grid(True, alpha=0.3)
ax5.set_xlim([0, 5])

# Subplot 6: Comparação mensagem recuperada vs original
# Detector de envelope simples (valor absoluto + filtro)
b, a = signal.butter(4, 2*fm/fs*2, btype='low')
detected = signal.filtfilt(b, a, envelope)
# Remover DC e normalizar
detected = detected - np.mean(detected)
detected = detected / np.max(np.abs(detected)) * np.max(np.abs(m_t))

ax6 = fig1.add_subplot(gs[3, :])
ax6.plot(t*1000, m_t, 'b-', linewidth=2, label='m(t) original', alpha=0.7)
ax6.plot(t*1000, detected, 'r--', linewidth=2, label='m(t) recuperado', alpha=0.7)
ax6.set_xlabel('Tempo (ms)')
ax6.set_ylabel('Amplitude')
ax6.set_title('Comparação: Mensagem Original vs Recuperada')
ax6.legend()
ax6.grid(True, alpha=0.3)
ax6.set_xlim([0, 5])

plt.suptitle('Discriminador de Frequência: Conversão FM → AM → Detecção', 
            fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig('../fm_discriminator.pdf', bbox_inches='tight')
plt.savefig('../fm_discriminator.png', dpi=300, bbox_inches='tight')
print("Figura salva: fm_discriminator.pdf/png")
plt.close()

# Gráfico 2: Característica de transferência do discriminador
fig2, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

# Resposta linear ideal
f_range = np.linspace(fc-10000, fc+10000, 100)
v_out_ideal = (f_range - fc) / kf

ax1.plot((f_range-fc)/1000, v_out_ideal, 'b-', linewidth=2.5, label='Ideal (linear)')
ax1.set_xlabel('Desvio de Frequência (kHz)')
ax1.set_ylabel('Tensão de Saída (V)')
ax1.set_title('Característica de Transferência Ideal')
ax1.grid(True, alpha=0.3)
ax1.axhline(y=0, color='k', linestyle='-', linewidth=0.5)
ax1.axvline(x=0, color='k', linestyle='-', linewidth=0.5)
ax1.legend()

# Marcar região linear
delta_f_max = kf * 0.8
ax1.axvspan(-delta_f_max/1000, delta_f_max/1000, alpha=0.2, color='green')
ax1.text(0, max(v_out_ideal)*0.9, 'Região Linear', ha='center',
        bbox=dict(boxstyle='round', facecolor='lightgreen'))

# Resposta real (com não-linearidades)
v_out_real = np.tanh((f_range - fc) / (kf*1.2))

ax2.plot((f_range-fc)/1000, v_out_ideal, 'b--', linewidth=2, label='Ideal', alpha=0.7)
ax2.plot((f_range-fc)/1000, v_out_real, 'r-', linewidth=2.5, label='Real (com saturação)')
ax2.set_xlabel('Desvio de Frequência (kHz)')
ax2.set_ylabel('Tensão de Saída (normalizada)')
ax2.set_title('Característica Real vs Ideal')
ax2.grid(True, alpha=0.3)
ax2.axhline(y=0, color='k', linestyle='-', linewidth=0.5)
ax2.axvline(x=0, color='k', linestyle='-', linewidth=0.5)
ax2.legend()

plt.suptitle('Característica de Transferência do Discriminador FM', 
            fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig('../fm_discriminator_response.pdf', bbox_inches='tight')
plt.savefig('../fm_discriminator_response.png', dpi=300, bbox_inches='tight')
print("Figura salva: fm_discriminator_response.pdf/png")
plt.close()
