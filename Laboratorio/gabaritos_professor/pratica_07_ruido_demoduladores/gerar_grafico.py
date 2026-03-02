"""
Gráfico esperado -- Prática 07: Ruído em Demoduladores AM e FM
Gera 'grafico_esperado.png' com quatro subplots:
  1. Sinal AM recuperado para três níveis de ruído
  2. Sinal FM recuperado para três níveis de ruído
  3. Qualidade relativa AM vs FM em função do SNR (curvas teóricas)
  4. Demonstração do limiar de FM (FM threshold)
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

rng = np.random.default_rng(seed=99)

# ------------------------------------------------------------------
# Parâmetros
# ------------------------------------------------------------------
fs_audio = 48_000
fm = 1_000
fc_am = 10_000
N = int(0.010 * fs_audio)   # 10 ms
t = np.arange(N) / fs_audio

# Mensagem
msg = np.cos(2 * np.pi * fm * t)

# Modulação AM DSB-SC
carrier = np.cos(2 * np.pi * fc_am * t)
am_sig = msg * carrier


def lowpass_fir(sig, cutoff_hz, fs_in, n_taps=65):
    """LPF de fase linear simples via convolução."""
    fc_n = cutoff_hz / (fs_in / 2)
    h = np.sinc(fc_n * (np.arange(n_taps) - n_taps // 2))
    h *= np.hanning(n_taps)
    h /= h.sum()
    return np.convolve(sig, h, mode='same')


def demod_am(received, fc_in, fs_in):
    lo = np.cos(2 * np.pi * fc_in * np.arange(len(received)) / fs_in)
    mixed = received * lo
    return lowpass_fir(mixed, 1500, fs_in)


def fm_modulate(message, delta_f, fs_in):
    phase = 2 * np.pi * delta_f * np.cumsum(message) / fs_in
    return np.cos(phase)


def fm_demodulate(s, fs_in):
    """Demodulador FM por diferença de fase instantânea."""
    analytic = np.zeros(len(s), dtype=complex)
    analytic.real = s
    # Hilbert via FFT simples
    S = np.fft.fft(s)
    h_filt = np.zeros(len(S))
    h_filt[0] = 1
    if len(S) % 2 == 0:
        h_filt[1:len(S)//2] = 2
        h_filt[len(S)//2] = 1
    else:
        h_filt[1:(len(S)+1)//2] = 2
    analytic = np.fft.ifft(S * h_filt)
    # Frequência instantânea = derivada da fase
    phase = np.unwrap(np.angle(analytic))
    inst_freq = np.diff(phase) * fs_in / (2 * np.pi)
    return np.append(inst_freq, inst_freq[-1]) / (delta_f)  # normalizado


# ------------------------------------------------------------------
# Figura
# ------------------------------------------------------------------
fig = plt.figure(figsize=(14, 9), constrained_layout=True)
gs = gridspec.GridSpec(2, 2, figure=fig)

noise_levels = [0.0, 0.15, 0.5]
colors_noise = ['C0', 'C1', 'C2']
labels_noise = ['Sem ruído', 'Ruído moderado\n(σ=0.15)', 'Ruído elevado\n(σ=0.5)']

# FM params
delta_f_fm = 10_000
fm_sig_base = fm_modulate(msg, delta_f_fm, fs_audio)

# 1. AM: sinal recuperado para 3 níveis de ruído
ax1 = fig.add_subplot(gs[0, 0])
n_show = int(0.006 * fs_audio)   # 6 ms
ax1.plot(t[:n_show]*1e3, msg[:n_show], 'k--', lw=1.2, label='Original', alpha=0.7, zorder=5)
for sigma, color, label in zip(noise_levels, colors_noise, labels_noise):
    noise = sigma * rng.standard_normal(N)
    rx_am = am_sig + noise
    rec = demod_am(rx_am, fc_am, fs_audio) * 2
    ax1.plot(t[:n_show]*1e3, rec[:n_show], color=color, lw=1.3, alpha=0.85, label=label)
ax1.set_title('1 – Sinal AM recuperado: diferentes níveis de ruído', fontweight='bold')
ax1.set_xlabel('Tempo (ms)'); ax1.set_ylabel('Amplitude')
ax1.legend(fontsize=8); ax1.grid(True, alpha=0.3)

# 2. FM: sinal recuperado para 3 níveis de ruído
ax2 = fig.add_subplot(gs[0, 1])
ax2.plot(t[:n_show]*1e3, msg[:n_show], 'k--', lw=1.2, label='Original', alpha=0.7, zorder=5)
for sigma, color, label in zip(noise_levels, colors_noise, labels_noise):
    noise = sigma * rng.standard_normal(N)
    rx_fm = fm_sig_base + noise
    rec_fm = fm_demodulate(rx_fm, fs_audio)
    rec_fm_lp = lowpass_fir(rec_fm, 1500, fs_audio)
    ax2.plot(t[:n_show]*1e3, rec_fm_lp[:n_show], color=color, lw=1.3, alpha=0.85, label=label)
ax2.set_title('2 – Sinal FM recuperado ($\\beta=10$): mesmos níveis de ruído', fontweight='bold')
ax2.set_xlabel('Tempo (ms)'); ax2.set_ylabel('Amplitude')
ax2.legend(fontsize=8); ax2.grid(True, alpha=0.3)

# 3. Curvas teóricas de SNR: AM vs FM
ax3 = fig.add_subplot(gs[1, 0])
snr_in_db = np.linspace(-5, 25, 300)
snr_in_lin = 10 ** (snr_in_db / 10)

# AM DSB-SC: SNR_out = SNR_in (demodulação coerente ideal)
snr_out_am_db = snr_in_db.copy()

# FM com diferentes beta
beta_list = [(1, 'FM $\\beta=1$', 'C1', '--'),
             (5, 'FM $\\beta=5$', 'C2', '-.'),
             (10, 'FM $\\beta=10$', 'C3', ':')]

ax3.plot(snr_in_db, snr_out_am_db, 'C0-', lw=2, label='AM DSB-SC')
for beta, lbl, color, ls in beta_list:
    gain = 3 * beta**2 * (beta + 1)
    snr_out_fm = 10 * np.log10(gain * snr_in_lin)
    # Simular limiar de FM: abaixo de ~10 dB, colapso
    threshold = 10  # dB
    mask = snr_in_db < threshold
    snr_out_fm[mask] = snr_in_db[mask] - 8 * (threshold - snr_in_db[mask]) / threshold
    ax3.plot(snr_in_db, snr_out_fm, color=color, ls=ls, lw=1.8, label=lbl)

ax3.axvline(10, color='gray', ls=':', lw=1.0, alpha=0.7, label='Limiar FM (≈10 dB)')
ax3.set_title('3 – SNR saída vs SNR entrada (teórico)', fontweight='bold')
ax3.set_xlabel('$\\mathrm{SNR}_i$ (dB)'); ax3.set_ylabel('$\\mathrm{SNR}_o$ (dB)')
ax3.legend(fontsize=8); ax3.grid(True, alpha=0.3)
ax3.set_xlim(-5, 25); ax3.set_ylim(-15, 55)

# 4. Demonstração do limiar de FM: sinal demodulado perto do threshold
ax4 = fig.add_subplot(gs[1, 1])
noise_near_threshold = 0.85   # ruído alto, perto do limiar
ax4.plot(t[:n_show]*1e3, msg[:n_show], 'k--', lw=1.5, label='Original', alpha=0.8, zorder=5)
for beta_demo, color, lbl in [(10, 'C2', 'FM $\\beta=10$ (acima limiar)'),
                               (1, 'C1', 'FM $\\beta=1$ (abaixo limiar)')]:
    fm_demo = fm_modulate(msg, beta_demo * fm, fs_audio)
    noise_demo = noise_near_threshold * rng.standard_normal(N)
    rx_demo = fm_demo + noise_demo
    rec_demo = fm_demodulate(rx_demo, fs_audio)
    rec_demo_lp = lowpass_fir(rec_demo, 1500, fs_audio)
    # Clip para visualização
    rec_demo_lp = np.clip(rec_demo_lp, -3, 3)
    ax4.plot(t[:n_show]*1e3, rec_demo_lp[:n_show], color=color, lw=1.2, alpha=0.85, label=lbl)
ax4.set_title(f'4 – Limiar de FM: mesmo ruído ($\\sigma={noise_near_threshold}$)', fontweight='bold')
ax4.set_xlabel('Tempo (ms)'); ax4.set_ylabel('Amplitude')
ax4.legend(fontsize=9); ax4.grid(True, alpha=0.3)

fig.suptitle('Prática 07 – Ruído em Demoduladores AM e FM: gráfico esperado',
             fontsize=13, fontweight='bold')
fig.savefig('grafico_esperado.png', dpi=180, bbox_inches='tight')
print('Salvo: grafico_esperado.png')
