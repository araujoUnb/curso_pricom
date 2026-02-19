#!/usr/bin/env python3
"""
Script 07: Análise de Largura de Banda FM
Gera: Regra de Carson, comparação NBFM/WBFM
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.special import jv

plt.rcParams['font.size'] = 10
plt.rcParams['axes.grid'] = True

# Gráfico 1: Regra de Carson
fig1, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

beta_range = np.linspace(0.1, 20, 100)

# Largura de banda pela regra de Carson
B_carson = 2 * (beta_range + 1)  # Normalizada por fm

# Largura de banda precisa (98% da potência)
B_precise = []
for beta in beta_range:
    # Encontrar n tal que soma de Jn^2 >= 0.98
    power_sum = 0
    n = 0
    while power_sum < 0.98 and n < 100:
        power_sum += jv(n, beta)**2 + (jv(-n, beta)**2 if n > 0 else 0)
        n += 1
    B_precise.append(2*n)

# Plot 1: Comparação regra de Carson vs precisa
ax1.plot(beta_range, B_carson, 'b-', linewidth=2.5, label='Regra de Carson: B ≈ 2(β+1)fₘ')
ax1.plot(beta_range, B_precise, 'r--', linewidth=2, label='Largura precisa (98% potência)')
ax1.set_xlabel('Índice de Modulação β')
ax1.set_ylabel('Largura de Banda (normalizada por fₘ)')
ax1.set_title('Regra de Carson vs Largura de Banda Precisa')
ax1.legend()
ax1.grid(True, alpha=0.3)
ax1.set_xlim([0, 20])

# Marcar regiões NBFM e WBFM
ax1.axvspan(0, 1, alpha=0.15, color='green', label='NBFM')
ax1.axvspan(1, 20, alpha=0.15, color='blue', label='WBFM')
ax1.text(0.5, max(B_carson)*0.9, 'NBFM\n(β < 1)', ha='center', fontsize=10, 
        bbox=dict(boxstyle='round', facecolor='lightgreen'))
ax1.text(10, max(B_carson)*0.9, 'WBFM\n(β >> 1)', ha='center', fontsize=10,
        bbox=dict(boxstyle='round', facecolor='lightblue'))

# Plot 2: Erro relativo
erro = (np.array(B_precise) - B_carson) / B_carson * 100
ax2.plot(beta_range, erro, 'g-', linewidth=2)
ax2.set_xlabel('Índice de Modulação β')
ax2.set_ylabel('Erro Relativo (%)')
ax2.set_title('Erro da Regra de Carson')
ax2.grid(True, alpha=0.3)
ax2.axhline(y=0, color='k', linestyle='--', linewidth=1)
ax2.set_xlim([0, 20])

plt.suptitle('Análise da Largura de Banda FM', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig('../fm_carson_rule.pdf', bbox_inches='tight')
plt.savefig('../fm_carson_rule.png', dpi=300, bbox_inches='tight')
print("Figura salva: fm_carson_rule.pdf/png")
plt.close()

# Gráfico 2: NBFM vs WBFM com sinais de exemplo
fig2 = plt.figure(figsize=(14, 10))
gs = fig2.add_gridspec(3, 2, hspace=0.35, wspace=0.3)

# Parâmetros de simulação
fm = 1000  # Hz
fc = 20000  # Hz
Ac = 1.0
fs = 200000
T = 0.005

t = np.arange(0, T, 1/fs)
m_t = np.cos(2*np.pi*fm*t)

# NBFM: β = 0.5
beta_nb = 0.5
delta_f_nb = beta_nb * fm
s_nbfm = Ac * np.cos(2*np.pi*fc*t + beta_nb*np.sin(2*np.pi*fm*t))

# WBFM: β = 5
beta_wb = 5.0
delta_f_wb = beta_wb * fm
s_wbfm = Ac * np.cos(2*np.pi*fc*t + beta_wb*np.sin(2*np.pi*fm*t))

# Espectros
N = len(t)
freq = np.fft.fftfreq(N, 1/fs)
pos_freq = freq[:N//2]

NBFM_f = np.abs(np.fft.fft(s_nbfm)[:N//2]) / N
WBFM_f = np.abs(np.fft.fft(s_wbfm)[:N//2]) / N

# Subplot 1: Mensagem
ax1 = fig2.add_subplot(gs[0, :])
ax1.plot(t*1000, m_t, 'b-', linewidth=2)
ax1.set_xlabel('Tempo (ms)')
ax1.set_ylabel('m(t)')
ax1.set_title(f'Sinal Modulante (fₘ = {fm} Hz)')
ax1.grid(True, alpha=0.3)
ax1.set_xlim([0, 3])

# Subplot 2: NBFM no tempo
ax2 = fig2.add_subplot(gs[1, 0])
ax2.plot(t*1000, s_nbfm, 'g-', linewidth=1)
ax2.set_xlabel('Tempo (ms)')
ax2.set_ylabel('s(t)')
ax2.set_title(f'NBFM: β = {beta_nb}, Δf = {delta_f_nb} Hz')
ax2.grid(True, alpha=0.3)
ax2.set_xlim([0, 1])

# Subplot 3: NBFM espectro
ax3 = fig2.add_subplot(gs[1, 1])
ax3.plot(pos_freq/1000, NBFM_f, 'g-', linewidth=1.5)
ax3.set_xlabel('Frequência (kHz)')
ax3.set_ylabel('Magnitude')
ax3.set_title(f'Espectro NBFM: B ≈ {2*(beta_nb+1)*fm} Hz')
ax3.set_xlim([fc/1000-3, fc/1000+3])
ax3.axvline(x=fc/1000, color='r', linestyle='--', alpha=0.5)
ax3.grid(True, alpha=0.3)

# Subplot 4: WBFM no tempo
ax4 = fig2.add_subplot(gs[2, 0])
ax4.plot(t*1000, s_wbfm, 'b-', linewidth=1)
ax4.set_xlabel('Tempo (ms)')
ax4.set_ylabel('s(t)')
ax4.set_title(f'WBFM: β = {beta_wb}, Δf = {delta_f_wb} Hz')
ax4.grid(True, alpha=0.3)
ax4.set_xlim([0, 1])

# Subplot 5: WBFM espectro
ax5 = fig2.add_subplot(gs[2, 1])
ax5.plot(pos_freq/1000, WBFM_f, 'b-', linewidth=1.5)
ax5.set_xlabel('Frequência (kHz)')
ax5.set_ylabel('Magnitude')
ax5.set_title(f'Espectro WBFM: B ≈ {2*(beta_wb+1)*fm} Hz')
ax5.set_xlim([fc/1000-7, fc/1000+7])
ax5.axvline(x=fc/1000, color='r', linestyle='--', alpha=0.5)
ax5.grid(True, alpha=0.3)

plt.suptitle('NBFM vs WBFM: Comparação Temporal e Espectral', 
            fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig('../fm_nbfm_vs_wbfm.pdf', bbox_inches='tight')
plt.savefig('../fm_nbfm_vs_wbfm.png', dpi=300, bbox_inches='tight')
print("Figura salva: fm_nbfm_vs_wbfm.pdf/png")
plt.close()

# Gráfico 3: Exemplo prático FM broadcast
fig3, ax = plt.subplots(figsize=(10, 6))

# Parâmetros FM broadcast
delta_f_max = 75000  # Hz
f_audio_max = 15000  # Hz
beta_fm = delta_f_max / f_audio_max

# Calcular largura de banda para diferentes frequências de áudio
f_audio = np.linspace(100, 15000, 100)
beta_values = delta_f_max / f_audio
B_carson_values = 2 * (delta_f_max + f_audio)

ax.plot(f_audio/1000, B_carson_values/1000, 'b-', linewidth=2.5)
ax.set_xlabel('Frequência de Áudio (kHz)')
ax.set_ylabel('Largura de Banda FM (kHz)')
ax.set_title(f'Largura de Banda FM Broadcast (Δf = {delta_f_max/1000} kHz)')
ax.grid(True, alpha=0.3)
ax.axhline(y=200, color='r', linestyle='--', linewidth=2, label='Alocação de canal (200 kHz)')
ax.legend()

# Marcar ponto de interesse
ax.plot([15], [2*(75+15)], 'ro', markersize=10)
ax.annotate(f'fₘ=15kHz: B={2*(75+15)} kHz', xy=(15, 180), xytext=(10, 150),
           arrowprops=dict(arrowstyle='->', color='red'), fontsize=10,
           bbox=dict(boxstyle='round', facecolor='wheat'))

plt.tight_layout()
plt.savefig('../fm_broadcast_bandwidth.pdf', bbox_inches='tight')
plt.savefig('../fm_broadcast_bandwidth.png', dpi=300, bbox_inches='tight')
print("Figura salva: fm_broadcast_bandwidth.pdf/png")
plt.close()
