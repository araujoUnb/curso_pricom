#!/usr/bin/env python3
"""
Script 09: PLL (Phase-Locked Loop) - Análise e Resposta
Gera: Diagrama de resposta, captura e lock
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy import signal

plt.rcParams['font.size'] = 10
plt.rcParams['axes.grid'] = True

# Gráfico 1: Detector de fase - característica
fig1, axes = plt.subplots(2, 2, figsize=(14, 10))

# Subplot 1: Característica do detector de fase
ax1 = axes[0, 0]
phase_error = np.linspace(-2*np.pi, 2*np.pi, 500)
detector_output = np.sin(phase_error)

ax1.plot(phase_error*180/np.pi, detector_output, 'b-', linewidth=2.5)
ax1.set_xlabel('Erro de Fase (graus)')
ax1.set_ylabel('Saída do Detector (normalizada)')
ax1.set_title('Característica do Detector de Fase')
ax1.grid(True, alpha=0.3)
ax1.axhline(y=0, color='k', linestyle='-', linewidth=0.5)
ax1.axvline(x=0, color='k', linestyle='-', linewidth=0.5)

# Marcar região linear
linear_range = 30  # graus
ax1.axvspan(-linear_range, linear_range, alpha=0.2, color='green')
ax1.text(0, 0.9, 'Região Linear\n(pequenos erros)', ha='center',
        bbox=dict(boxstyle='round', facecolor='lightgreen'))

# Subplot 2: Resposta em frequência do PLL
ax2 = axes[0, 1]

# PLL de 1ª ordem
wn = 2*np.pi*1000  # Frequência natural (rad/s)
sys_1st = signal.TransferFunction([wn], [1, wn])
w, h_1st = signal.freqresp(sys_1st, w=np.logspace(1, 5, 500))

# PLL de 2ª ordem
zeta = 0.707  # Amortecimento crítico
sys_2nd = signal.TransferFunction([wn**2], [1, 2*zeta*wn, wn**2])
w, h_2nd = signal.freqresp(sys_2nd, w=np.logspace(1, 5, 500))

ax2.semilogx(w/(2*np.pi), 20*np.log10(np.abs(h_1st)), 'b-', linewidth=2, label='1ª ordem')
ax2.semilogx(w/(2*np.pi), 20*np.log10(np.abs(h_2nd)), 'r-', linewidth=2, label='2ª ordem (ζ=0.707)')
ax2.set_xlabel('Frequência (Hz)')
ax2.set_ylabel('Magnitude (dB)')
ax2.set_title('Resposta em Frequência do PLL')
ax2.grid(True, which='both', alpha=0.3)
ax2.legend()
ax2.axhline(y=-3, color='g', linestyle='--', linewidth=1, label='3dB')
ax2.set_ylim([-40, 5])

# Subplot 3: Resposta ao degrau
ax3 = axes[1, 0]

t_step = np.linspace(0, 0.005, 1000)
t_1st, y_1st = signal.step(sys_1st, T=t_step)
t_2nd, y_2nd = signal.step(sys_2nd, T=t_step)

ax3.plot(t_1st*1000, y_1st, 'b-', linewidth=2, label='1ª ordem')
ax3.plot(t_2nd*1000, y_2nd, 'r-', linewidth=2, label='2ª ordem (ζ=0.707)')
ax3.axhline(y=1, color='k', linestyle='--', linewidth=1, alpha=0.5)
ax3.set_xlabel('Tempo (ms)')
ax3.set_ylabel('Resposta Normalizada')
ax3.set_title('Resposta ao Degrau de Fase')
ax3.grid(True, alpha=0.3)
ax3.legend()

# Subplot 4: Faixa de captura e lock
ax4 = axes[1, 1]

# Parâmetros típicos
Kd = 1.0  # Ganho do detector de fase (V/rad)
Kv = 10000  # Ganho do VCO (Hz/V)
wn_values = 2*np.pi*np.logspace(2, 4, 50)  # Diferentes frequências naturais

# Faixas de captura e lock
f_lock = Kd * Kv / (2*np.pi) * np.ones_like(wn_values)  # Aproximação
f_capture = np.sqrt(2 * Kd * Kv) / (2*np.pi) * np.ones_like(wn_values)  # Aproximação

ax4.semilogx(wn_values/(2*np.pi), f_lock/1000, 'b-', linewidth=2.5, label='Lock Range')
ax4.semilogx(wn_values/(2*np.pi), f_capture/1000, 'r-', linewidth=2.5, label='Capture Range')
ax4.fill_between(wn_values/(2*np.pi), 0, f_capture/1000, alpha=0.2, color='red')
ax4.set_xlabel('Frequência Natural do Loop (Hz)')
ax4.set_ylabel('Faixa de Frequência (kHz)')
ax4.set_title('Faixas de Captura e Lock do PLL')
ax4.grid(True, which='both', alpha=0.3)
ax4.legend()

plt.suptitle('PLL: Análise de Características e Desempenho', 
            fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig('../pll_analysis.pdf', bbox_inches='tight')
plt.savefig('../pll_analysis.png', dpi=300, bbox_inches='tight')
print("Figura salva: pll_analysis.pdf/png")
plt.close()

# Gráfico 2: Simulação de PLL travando no sinal
fig2, axes = plt.subplots(3, 1, figsize=(14, 10))

# Parâmetros de simulação
fc_in = 20000  # Hz
fm = 500  # Hz
kf_in = 2000  # Hz/V
Ac = 1.0
fs = 200000
T_sim = 0.02

t = np.arange(0, T_sim, 1/fs)

# Sinal de entrada (FM com degrau na mensagem)
m_t = np.zeros_like(t)
m_t[t > 0.005] = 0.5  # Degrau em t=5ms

phi_in = 2*np.pi*kf_in*np.cumsum(m_t)/fs
s_in = Ac * np.cos(2*np.pi*fc_in*t + phi_in)
f_in = fc_in + kf_in * m_t

# Simulação simplificada do PLL
# VCO frequência segue entrada com atraso
tau_pll = 0.001  # Constante de tempo do PLL (1 ms)
alpha = 1 - np.exp(-1/(fs*tau_pll))
f_vco = np.zeros_like(t)
f_vco[0] = fc_in

for i in range(1, len(t)):
    # VCO tenta seguir frequência de entrada
    f_vco[i] = f_vco[i-1] + alpha * (f_in[i] - f_vco[i-1])

error = f_in - f_vco

# Plot 1: Frequência de entrada
axes[0].plot(t*1000, f_in/1000, 'b-', linewidth=2, label='Frequência entrada')
axes[0].set_ylabel('Frequência (kHz)')
axes[0].set_title('Frequência do Sinal de Entrada (FM)')
axes[0].grid(True, alpha=0.3)
axes[0].legend()
axes[0].set_xlim([0, T_sim*1000])

# Plot 2: Frequência do VCO
axes[1].plot(t*1000, f_vco/1000, 'r-', linewidth=2, label='Frequência VCO')
axes[1].plot(t*1000, f_in/1000, 'b--', linewidth=1, alpha=0.5, label='Referência (entrada)')
axes[1].set_ylabel('Frequência (kHz)')
axes[1].set_title('Frequência do VCO (seguindo entrada)')
axes[1].grid(True, alpha=0.3)
axes[1].legend()
axes[1].set_xlim([0, T_sim*1000])

# Plot 3: Erro de frequência
axes[2].plot(t*1000, error, 'g-', linewidth=2)
axes[2].set_xlabel('Tempo (ms)')
axes[2].set_ylabel('Erro (Hz)')
axes[2].set_title('Erro de Frequência (Entrada - VCO)')
axes[2].grid(True, alpha=0.3)
axes[2].axhline(y=0, color='k', linestyle='--', linewidth=1)
axes[2].set_xlim([0, T_sim*1000])

# Marcar região de lock
lock_threshold = 50  # Hz
locked = np.abs(error) < lock_threshold
if np.any(locked):
    lock_time = t[np.where(locked)[0][0]] * 1000
    axes[2].axvspan(lock_time, T_sim*1000, alpha=0.2, color='green')
    axes[2].text(T_sim*1000/2, max(error)*0.8, 'PLL Locked', ha='center',
                bbox=dict(boxstyle='round', facecolor='lightgreen'))

plt.suptitle('PLL: Processo de Travamento (Lock) em Sinal FM', 
            fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig('../pll_locking.pdf', bbox_inches='tight')
plt.savefig('../pll_locking.png', dpi=300, bbox_inches='tight')
print("Figura salva: pll_locking.pdf/png")
plt.close()
