"""
Gráfico esperado -- Prática 05: Modulação FM
Gera 'grafico_esperado.png' com quatro subplots:
  1. Espectro FM para diferentes beta (NBFM vs WBFM)
  2. Largura de banda medida vs Regra de Carson
  3. Sinal FM no tempo (NBFM vs WBFM)
  4. Impacto do ruído: NBFM vs WBFM
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

rng = np.random.default_rng(seed=7)

# ------------------------------------------------------------------
fs = 480_000;  fm = 2_000;  fc = 0   # banda base (fc=0 para WBFM Transmit)
Am = 1.0

N = int(0.05 * fs)   # 50 ms
t = np.arange(N) / fs
msg = Am * np.cos(2 * np.pi * fm * t)

# Integrar mensagem para FM
msg_integral = np.cumsum(msg) / fs   # integral numérica


def fm_signal(delta_f):
    beta = delta_f / fm
    phi = 2 * np.pi * delta_f * msg_integral
    return np.cos(phi)   # banda base: fc=0


def fft_onesided_db(sig, fs_in, N_fft=None):
    if N_fft is None:
        N_fft = len(sig)
    seg = sig[:N_fft]
    spec = np.fft.rfft(seg, n=N_fft)
    freqs = np.fft.rfftfreq(N_fft, d=1 / fs_in)
    mag = np.abs(spec) / (N_fft / 2)
    mag_db = 20 * np.log10(np.maximum(mag, 1e-10))
    return freqs, mag_db


# Configurações de teste
configs = [
    (1_000, 'NBFM $\\beta=0.5$', 'C0', '-'),
    (2_000, 'FM $\\beta=1.0$', 'C1', '--'),
    (10_000, 'WBFM $\\beta=5.0$', 'C2', '-.'),
    (20_000, 'WBFM $\\beta=10.0$', 'C3', ':'),
]

N_fft = 4 * 4096

fig = plt.figure(figsize=(14, 9), constrained_layout=True)
gs = gridspec.GridSpec(2, 2, figure=fig)

# 1. Espectros FM
ax1 = fig.add_subplot(gs[0, 0])
for delta_f, label, color, ls in configs:
    s = fm_signal(delta_f)
    fr, md = fft_onesided_db(s, fs, N_fft=N_fft)
    # Mostrar apenas em torno de fc=0
    mask = fr <= 60_000
    ax1.plot(fr[mask] / 1e3, md[mask], color=color, ls=ls, lw=1.3, label=label)
# Regra de Carson: marcas verticais
for delta_f, label, color, ls in configs:
    bt = (delta_f + fm) * 2
    ax1.axvline(bt / 2 / 1e3, color=color, lw=0.7, alpha=0.4)
ax1.set_xlim(0, 50)
ax1.set_ylim(-60, 5)
ax1.set_title('1 – Espectro FM: efeito de $\\beta$', fontweight='bold')
ax1.set_xlabel('Frequência (kHz)')
ax1.set_ylabel('Magnitude (dBFS)')
ax1.legend(fontsize=8); ax1.grid(True, alpha=0.3)

# 2. Carson: previsto vs medido (usando -20 dB como critério de BW)
ax2 = fig.add_subplot(gs[0, 1])
delta_f_range = np.array([500, 1000, 2000, 5000, 10000, 15000, 20000])
bw_carson = 2 * (delta_f_range + fm)
bw_measured = []
for df in delta_f_range:
    s = fm_signal(df)
    fr, md = fft_onesided_db(s, fs, N_fft=N_fft)
    # BW como faixa onde potência > -20 dB do máximo
    threshold = md.max() - 20
    mask_bw = (md > threshold) & (fr <= fs / 2)
    if mask_bw.any():
        bw_meas = fr[mask_bw].max() * 2   # simétrico
    else:
        bw_meas = 2 * df
    bw_measured.append(bw_meas)
bw_measured = np.array(bw_measured)

beta_range = delta_f_range / fm
ax2.plot(beta_range, bw_carson / 1e3, 'o-', label='Regra de Carson', lw=2, ms=7)
ax2.plot(beta_range, bw_measured / 1e3, 's--', label='Medida (-20 dB)', lw=1.5, ms=7)
ax2.set_title('2 – Largura de banda: Carson vs Medida', fontweight='bold')
ax2.set_xlabel('Índice de modulação $\\beta = \\Delta f / f_m$')
ax2.set_ylabel('Largura de banda (kHz)')
ax2.legend(fontsize=9); ax2.grid(True, alpha=0.3)

# 3. Sinal no tempo
ax3 = fig.add_subplot(gs[1, 0])
n_show = int(0.003 * fs)   # 3 ms
for delta_f, label, color, ls in [(1_000, 'NBFM $\\beta=0.5$', 'C0', '-'),
                                    (10_000, 'WBFM $\\beta=5.0$', 'C2', '-.')]:
    s = fm_signal(delta_f)
    ax3.plot(t[:n_show] * 1e3, s[:n_show], color=color, ls=ls, lw=1.3, label=label, alpha=0.9)
ax3.plot(t[:n_show] * 1e3, msg[:n_show], 'k--', lw=1.0, label='Mensagem', alpha=0.5)
ax3.set_title('3 – Sinal FM no tempo', fontweight='bold')
ax3.set_xlabel('Tempo (ms)'); ax3.set_ylabel('Amplitude')
ax3.legend(fontsize=9); ax3.grid(True, alpha=0.3)

# 4. SNR de saída: NBFM vs WBFM (curvas teóricas)
ax4 = fig.add_subplot(gs[1, 1])
snr_in_db = np.linspace(-5, 25, 200)
snr_in_lin = 10 ** (snr_in_db / 10)

for beta_i, color, ls in [(0.5, 'C0', '-'), (1.0, 'C1', '--'),
                            (5.0, 'C2', '-.'), (10.0, 'C3', ':')]:
    # Acima do limiar: SNR_out = 3*beta^2*(beta+1)*SNR_in
    gain = 3 * beta_i**2 * (beta_i + 1)
    snr_out = 10 * np.log10(gain * snr_in_lin)
    # Abaixo do limiar (~10 dB): degradação abrupta
    threshold_idx = snr_in_db < 10
    snr_out[threshold_idx] = snr_in_db[threshold_idx] - 5   # degradação artificial
    ax4.plot(snr_in_db, snr_out, color=color, ls=ls, lw=1.5, label=f'FM $\\beta={beta_i}$')

# AM (referência): SNR_out ≈ SNR_in (para DSB-SC)
ax4.plot(snr_in_db, snr_in_db, 'k--', lw=1.5, label='AM DSB-SC (referência)')
ax4.axvline(10, color='gray', ls=':', lw=0.8, alpha=0.6, label='Limiar FM (≈10 dB)')
ax4.set_title('4 – SNR saída vs SNR entrada (teórico)', fontweight='bold')
ax4.set_xlabel('SNR entrada (dB)'); ax4.set_ylabel('SNR saída (dB)')
ax4.legend(fontsize=8); ax4.grid(True, alpha=0.3)
ax4.set_xlim(-5, 25); ax4.set_ylim(-10, 50)

fig.suptitle('Prática 05 – Modulação FM: gráfico esperado',
             fontsize=13, fontweight='bold')
fig.savefig('grafico_esperado.png', dpi=180, bbox_inches='tight')
print('Salvo: grafico_esperado.png')
