"""
Gráfico esperado -- Prática 06: Phase-Locked Loop (PLL)
Gera 'grafico_esperado.png' com quatro subplots:
  1. Processo de lock: convergência do erro de fase para diferentes loop_bw
  2. Resposta ao degrau de frequência (mudança de frequência de entrada)
  3. Efeito do ruído: jitter de fase para loop_bw estreita vs larga
  4. Faixa de captura: erro estacionário vs desvio de frequência
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

rng = np.random.default_rng(seed=13)

# ------------------------------------------------------------------
# Simulação simplificada de PLL de 1ª ordem
# ------------------------------------------------------------------
def simulate_pll(omega_in, omega_0, loop_bw, fs, N_samp, noise_sigma=0.0):
    """
    Simula PLL de 1ª ordem discreto.
    omega_in: frequência de entrada (rad/amostra)
    omega_0:  frequência central do VCO (rad/amostra)
    loop_bw:  largura de banda do laço (rad/amostra)
    Retorna: array do erro de fase ao longo do tempo.
    """
    phi_e = np.zeros(N_samp)   # erro de fase
    phi_vco = 0.0
    phi_in = 0.0
    omega_vco = omega_0

    Kp = loop_bw    # ganho proporcional (PLL de 1ª ordem simples)

    for i in range(1, N_samp):
        phi_in += omega_in
        phi_vco += omega_vco
        err = np.sin(phi_in - phi_vco)   # saída do detector de fase
        if noise_sigma > 0:
            err += noise_sigma * rng.standard_normal()
        omega_vco = omega_0 + Kp * err
        phi_e[i] = phi_in - phi_vco

    return phi_e


fs = 32_000
T = 0.5       # 500 ms de simulação
N = int(T * fs)
t = np.arange(N) / fs * 1e3   # em ms

# Frequências (rad/amostra)
f_in = 1_000      # Hz
omega_in = 2 * np.pi * f_in / fs
omega_0 = 2 * np.pi * 1_000 / fs   # VCO centrado em 1000 Hz

# ------------------------------------------------------------------
# Figura
# ------------------------------------------------------------------
fig = plt.figure(figsize=(14, 9), constrained_layout=True)
gs = gridspec.GridSpec(2, 2, figure=fig)

# 1. Convergência do lock para diferentes loop_bw
ax1 = fig.add_subplot(gs[0, 0])
loop_bw_vals = [0.01, 0.062, 0.2, 0.5]
colors = ['C0', 'C1', 'C2', 'C3']
for lbw, color in zip(loop_bw_vals, colors):
    pe = simulate_pll(omega_in, omega_0 * 0.93, lbw, fs, N)  # leve desvio inicial
    ax1.plot(t[:int(0.2*fs)], pe[:int(0.2*fs)],
             color=color, lw=1.4, label=f'loop\_bw = {lbw}')
ax1.axhline(0, color='gray', lw=0.7, ls='--')
ax1.set_title('1 – Convergência do erro de fase (lock)', fontweight='bold')
ax1.set_xlabel('Tempo (ms)'); ax1.set_ylabel('Erro de fase (rad)')
ax1.legend(fontsize=8); ax1.grid(True, alpha=0.3)
ax1.set_xlim(0, t[int(0.2*fs)-1])

# 2. Resposta ao degrau de frequência
ax2 = fig.add_subplot(gs[0, 1])
N2 = int(0.3 * fs)
t2 = np.arange(N2) / fs * 1e3
# Frequência muda em t=100ms
idx_step = int(0.1 * fs)
for lbw, color, ls in [(0.062, 'C1', '-'), (0.2, 'C2', '--'), (0.5, 'C3', '-.')]:
    pe = np.zeros(N2)
    phi_in, phi_vco = 0.0, 0.0
    omega_vco_dyn = omega_0
    for i in range(1, N2):
        omega_i = omega_in if i < idx_step else omega_in * 1.05   # degrau de 5%
        phi_in += omega_i
        phi_vco += omega_vco_dyn
        err = np.sin(phi_in - phi_vco)
        omega_vco_dyn = omega_0 + lbw * err
        pe[i] = phi_in - phi_vco
    ax2.plot(t2, pe, color=color, lw=1.4, ls=ls, label=f'loop\_bw = {lbw}')

ax2.axvline(100, color='gray', ls=':', lw=0.8, label='Degrau de freq.')
ax2.axhline(0, color='gray', lw=0.5)
ax2.set_title('2 – Resposta ao degrau de frequência (+5%)', fontweight='bold')
ax2.set_xlabel('Tempo (ms)'); ax2.set_ylabel('Erro de fase (rad)')
ax2.legend(fontsize=8); ax2.grid(True, alpha=0.3)

# 3. Efeito do ruído: jitter de fase
ax3 = fig.add_subplot(gs[1, 0])
N3 = int(0.1 * fs)
t3 = np.arange(N3) / fs * 1e3
noise_sigma = 0.3
for lbw, color, ls in [(0.01, 'C0', '-'), (0.2, 'C2', '-.')]:
    pe_n = simulate_pll(omega_in, omega_0, lbw, fs, N3, noise_sigma=noise_sigma)
    ax3.plot(t3, pe_n, color=color, lw=1.0, ls=ls, alpha=0.85,
             label=f'loop\_bw={lbw} (jitter={np.std(pe_n[N3//4:]):.3f} rad)')
ax3.axhline(0, color='gray', lw=0.7, ls='--')
ax3.set_title(f'3 – Jitter de fase com ruído ($\\sigma={noise_sigma}$)', fontweight='bold')
ax3.set_xlabel('Tempo (ms)'); ax3.set_ylabel('Erro de fase (rad)')
ax3.legend(fontsize=8); ax3.grid(True, alpha=0.3)
ax3.set_xlim(0, t3[-1])

# 4. Faixa de captura: erro estacionário vs desvio de frequência
ax4 = fig.add_subplot(gs[1, 1])
delta_f_range = np.linspace(0, 800, 100)  # Hz
N4 = int(0.5 * fs)

for lbw, color, ls in [(0.062, 'C1', '-'), (0.2, 'C2', '--')]:
    err_ss = []
    for df in delta_f_range:
        omega_in_test = 2 * np.pi * (f_in + df) / fs
        pe4 = simulate_pll(omega_in_test, omega_0, lbw, fs, N4)
        err_ss.append(np.abs(pe4[3*N4//4:]).mean())   # erro estacionário
    ax4.plot(delta_f_range, err_ss, color=color, ls=ls, lw=1.5,
             label=f'loop\_bw = {lbw}')
ax4.axhline(np.pi / 2, color='red', ls=':', lw=1.0, label='Limite de lock ($\\pi/2$ rad)')
ax4.set_title('4 – Faixa de captura: erro vs desvio de frequência', fontweight='bold')
ax4.set_xlabel('Desvio de frequência $\\Delta f$ (Hz)'); ax4.set_ylabel('Erro estacionário (rad)')
ax4.legend(fontsize=9); ax4.grid(True, alpha=0.3)

fig.suptitle('Prática 06 – PLL: gráfico esperado',
             fontsize=13, fontweight='bold')
fig.savefig('grafico_esperado.png', dpi=180, bbox_inches='tight')
print('Salvo: grafico_esperado.png')
