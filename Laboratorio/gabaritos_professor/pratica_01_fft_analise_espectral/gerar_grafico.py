"""
Gráfico esperado -- Prática 01: FFT e Análise Espectral
Gera 'grafico_esperado.png' com quatro subplots:
  1. Sinal no tempo (dois tons, limpo e com ruído)
  2. Espectro (FFT) dos mesmos cenários
  3. Efeito do FFT size na resolução espectral
  4. Comparação de funções de janela (retangular vs Hann)
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

rng = np.random.default_rng(seed=42)

# ------------------------------------------------------------------
# Parâmetros
# ------------------------------------------------------------------
fs = 32_000          # taxa de amostragem
f1, f2 = 1_000, 2_500  # frequências dos tons (Hz)
A1, A2 = 0.9, 0.45   # amplitudes
noise_sigma = 0.25    # desvio padrão do ruído

N_display = 512       # amostras para exibição no tempo
N_fft = 1024          # FFT size padrão

t = np.arange(4 * N_fft) / fs

# ------------------------------------------------------------------
# Sinais
# ------------------------------------------------------------------
x_clean = A1 * np.cos(2 * np.pi * f1 * t) + A2 * np.cos(2 * np.pi * f2 * t)
x_noisy = x_clean + noise_sigma * rng.standard_normal(len(t))


def fft_mag_db(x, N, window=None):
    """Retorna (freqs positivas, magnitude em dBFS)."""
    if window is None:
        w = np.ones(N)
    else:
        w = window(N)
    seg = x[:N] * w
    spec = np.fft.rfft(seg)
    mag = np.abs(spec) / (N / 2)    # normalizado pelo número de pontos úteis
    mag[0] /= 2                      # correção do bin DC
    mag_db = 20 * np.log10(np.maximum(mag, 1e-9))
    freqs = np.fft.rfftfreq(N, d=1 / fs)
    return freqs, mag_db


# ------------------------------------------------------------------
# Figura: 2 linhas × 2 colunas
# ------------------------------------------------------------------
fig = plt.figure(figsize=(14, 9), constrained_layout=True)
gs = gridspec.GridSpec(2, 2, figure=fig)

# --- Subplot 1: sinal no tempo ---
ax1 = fig.add_subplot(gs[0, 0])
idx = slice(0, N_display)
ax1.plot(t[idx] * 1e3, x_clean[idx], label='Sem ruído', lw=1.5)
ax1.plot(t[idx] * 1e3, x_noisy[idx], label='Com ruído', alpha=0.7, lw=1.0)
ax1.set_title('1 – Sinal no tempo', fontweight='bold')
ax1.set_xlabel('Tempo (ms)')
ax1.set_ylabel('Amplitude')
ax1.legend(fontsize=9)
ax1.grid(True, alpha=0.3)
ax1.annotate(f'$f_1$ = {f1} Hz, $f_2$ = {f2} Hz', xy=(0.02, 0.92),
             xycoords='axes fraction', fontsize=8, color='gray')

# --- Subplot 2: espectro dos dois cenários ---
ax2 = fig.add_subplot(gs[0, 1])
f_c, m_c = fft_mag_db(x_clean, N_fft)
f_n, m_n = fft_mag_db(x_noisy, N_fft)
ax2.plot(f_c / 1e3, m_c, label='Sem ruído', lw=1.5)
ax2.plot(f_n / 1e3, m_n, label='Com ruído', alpha=0.75, lw=1.0)
ax2.axvline(f1 / 1e3, color='gray', ls='--', lw=0.8, alpha=0.6)
ax2.axvline(f2 / 1e3, color='gray', ls=':', lw=0.8, alpha=0.6)
ax2.set_xlim(0, 6)
ax2.set_ylim(-60, 5)
ax2.set_title('2 – Espectro de magnitude (FFT)', fontweight='bold')
ax2.set_xlabel('Frequência (kHz)')
ax2.set_ylabel('Magnitude (dBFS)')
ax2.legend(fontsize=9)
ax2.grid(True, alpha=0.3)
# anotações nos picos
ax2.annotate(f'{f1} Hz', xy=(f1 / 1e3, 0), xytext=(f1 / 1e3 + 0.2, -5),
             fontsize=8, arrowprops=dict(arrowstyle='->', color='C0'), color='C0')
ax2.annotate(f'{f2} Hz', xy=(f2 / 1e3, -7), xytext=(f2 / 1e3 + 0.2, -14),
             fontsize=8, arrowprops=dict(arrowstyle='->', color='C0'), color='C0')

# --- Subplot 3: efeito do FFT size ---
ax3 = fig.add_subplot(gs[1, 0])
for N_test, color, ls in [(128, 'C2', ':'), (512, 'C1', '--'), (2048, 'C0', '-')]:
    freq_test, mag_test = fft_mag_db(x_clean, N_test)
    ax3.plot(freq_test / 1e3, mag_test, label=f'N = {N_test}  (Δf ≈ {fs/N_test:.0f} Hz)',
             color=color, ls=ls, lw=1.5 if N_test == 2048 else 1.0)
ax3.set_xlim(0, 4)
ax3.set_ylim(-40, 5)
ax3.set_title('3 – Efeito do FFT size na resolução espectral', fontweight='bold')
ax3.set_xlabel('Frequência (kHz)')
ax3.set_ylabel('Magnitude (dBFS)')
ax3.legend(fontsize=8)
ax3.grid(True, alpha=0.3)

# --- Subplot 4: comparação de janelas ---
ax4 = fig.add_subplot(gs[1, 1])
windows = {
    'Retangular': np.ones,
    'Hann': np.hanning,
    'Hamming': np.hamming,
    'Blackman': np.blackman,
}
N_win = 1024
for wname, wfunc in windows.items():
    fw, mw = fft_mag_db(x_clean, N_win, window=wfunc)
    ax4.plot(fw / 1e3, mw, label=wname, lw=1.3)
ax4.set_xlim(0.5, 3.5)
ax4.set_ylim(-70, 5)
ax4.set_title('4 – Comparação de funções de janela', fontweight='bold')
ax4.set_xlabel('Frequência (kHz)')
ax4.set_ylabel('Magnitude (dBFS)')
ax4.legend(fontsize=8)
ax4.grid(True, alpha=0.3)

fig.suptitle('Prática 01 – FFT e Análise Espectral: gráfico esperado',
             fontsize=13, fontweight='bold')
fig.savefig('grafico_esperado.png', dpi=180, bbox_inches='tight')
print('Salvo: grafico_esperado.png')
