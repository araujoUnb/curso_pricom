"""
Gráfico esperado -- Prática 02: Modulação AM DSB-SC
Gera 'grafico_esperado.png' com quatro subplots:
  1. Sinal modulado DSB-SC no tempo
  2. Espectro do DSB-SC (sem portadora)
  3. Comparação do sinal demodulado: erro de fase 0° vs 90°
  4. Espectro para diferentes frequências de mensagem
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

# ------------------------------------------------------------------
# Parâmetros
# ------------------------------------------------------------------
fs = 48_000
fc = 5_000
fm_vals = [500, 1_000, 2_000, 4_000]   # Hz
fm_default = 1_000
Am = 1.0
Ac = 1.0

N = int(0.05 * fs)    # 50 ms de sinal
t = np.arange(N) / fs


def fft_onesided(sig, fs_in):
    spec = np.fft.rfft(sig)
    freqs = np.fft.rfftfreq(len(sig), d=1 / fs_in)
    mag = np.abs(spec) / (len(sig) / 2)
    return freqs, mag


# ------------------------------------------------------------------
# Gerar sinais
# ------------------------------------------------------------------
msg = Am * np.cos(2 * np.pi * fm_default * t)
carrier = Ac * np.cos(2 * np.pi * fc * t)
dsb_sc = msg * carrier

# Demodulação coerente com diferentes erros de fase
NTAPS = 385          # mesma ordem do LPF do fluxograma (transicao de 300 Hz)
FIR_DELAY = NTAPS // 2


def demodulate(s, fc_in, fs_in, phase_rad, cutoff=1500):
    from scipy.signal import firwin, lfilter
    local_osc = np.cos(2 * np.pi * fc_in * np.arange(len(s)) / fs_in + phase_rad)
    mixed = s * local_osc
    h = firwin(NTAPS, cutoff / (fs_in / 2), window='hamming')
    return lfilter(h, [1.0], mixed)

try:
    demod_0 = demodulate(dsb_sc, fc, fs, 0.0)
    demod_90 = demodulate(dsb_sc, fc, fs, np.pi / 2)
except ImportError:
    # Se scipy não disponível, usa convolução manual simples
    N_taps = NTAPS
    cutoff_n = 1500.0 / (fs / 2)
    h = np.sinc(cutoff_n * (np.arange(N_taps) - N_taps // 2)) * np.hanning(N_taps)
    h /= h.sum()
    def demod_simple(s, phase_rad):
        lo = np.cos(2 * np.pi * fc * np.arange(len(s)) / fs + phase_rad)
        return np.convolve(s * lo, h, mode='same')
    demod_0 = demod_simple(dsb_sc, 0.0)
    demod_90 = demod_simple(dsb_sc, np.pi / 2)

# ------------------------------------------------------------------
# Figura
# ------------------------------------------------------------------
fig = plt.figure(figsize=(14, 9), constrained_layout=True)
gs = gridspec.GridSpec(2, 2, figure=fig)

# --- 1. Sinal no tempo ---
ax1 = fig.add_subplot(gs[0, 0])
n_show = int(0.006 * fs)   # 6 ms
ax1.plot(t[:n_show] * 1e3, msg[:n_show], label='Mensagem $m(t)$', lw=1.5, ls='--')
ax1.plot(t[:n_show] * 1e3, dsb_sc[:n_show], label='DSB-SC $s(t)$', lw=1.2, alpha=0.85)
ax1.set_title('1 – DSB-SC no tempo ($f_m=1000$ Hz)', fontweight='bold')
ax1.set_xlabel('Tempo (ms)')
ax1.set_ylabel('Amplitude')
ax1.legend(fontsize=9)
ax1.grid(True, alpha=0.3)

# --- 2. Espectro DSB-SC ---
ax2 = fig.add_subplot(gs[0, 1])
f_sig, m_sig = fft_onesided(dsb_sc, fs)
ax2.plot(f_sig / 1e3, m_sig, lw=1.5)
ax2.axvline((fc - fm_default) / 1e3, color='C1', ls='--', lw=1.0,
            label=f'$f_c - f_m$ = {(fc-fm_default)/1000:.1f} kHz')
ax2.axvline((fc + fm_default) / 1e3, color='C2', ls='--', lw=1.0,
            label=f'$f_c + f_m$ = {(fc+fm_default)/1000:.1f} kHz')
ax2.axvline(fc / 1e3, color='red', ls=':', lw=0.8, alpha=0.6,
            label=f'$f_c$ = {fc/1000:.0f} kHz, sem componente')
ax2.set_xlim(2, 8)
ax2.set_title('2 – Espectro DSB-SC (sem portadora)', fontweight='bold')
ax2.set_xlabel('Frequência (kHz)')
ax2.set_ylabel('Magnitude')
ax2.legend(fontsize=8)
ax2.grid(True, alpha=0.3)

# --- 3. Demodulação com erro de fase ---
ax3 = fig.add_subplot(gs[1, 0])
# A amostra demod[n] corresponde a msg[n - FIR_DELAY]; o recorte abaixo
# compensa esse atraso de grupo e comeca depois do transitorio do filtro.
ini = NTAPS
sl_d = slice(ini, ini + n_show)
sl_m = slice(ini - FIR_DELAY, ini - FIR_DELAY + n_show)
ax3.plot(t[:n_show] * 1e3, msg[sl_m],
         label='Original', lw=2.0, ls='--', alpha=0.55)
ax3.plot(t[:n_show] * 1e3, demod_0[sl_d] * 2,
         label='Demodulado (0°, ×2)', lw=1.5)
ax3.plot(t[:n_show] * 1e3, demod_90[sl_d] * 2,
         label='Demodulado (90°, ×2)', lw=1.2, ls='-.', alpha=0.85)
ax3.set_title('3 – Demodulação coerente: fase 0° vs 90°', fontweight='bold')
ax3.set_xlabel('Tempo (ms)')
ax3.set_ylabel('Amplitude')
ax3.legend(fontsize=9)
ax3.grid(True, alpha=0.3)

# --- 4. Espectro para diferentes fm ---
ax4 = fig.add_subplot(gs[1, 1])
colors = ['C0', 'C1', 'C2', 'C3']
for fm_i, color in zip(fm_vals, colors):
    dsb_i = Am * np.cos(2 * np.pi * fm_i * t) * carrier
    f_i, m_i = fft_onesided(dsb_i, fs)
    ax4.plot(f_i / 1e3, m_i, color=color, lw=1.3,
             label=f'$f_m$ = {fm_i} Hz → BLs em {fc-fm_i}/{fc+fm_i} Hz')
ax4.axvline(fc / 1e3, color='red', ls=':', lw=0.8, alpha=0.5,
            label='$f_c$, sem componente')
ax4.set_xlim(0, 11)
ax4.set_title('4 – Espectro para diferentes $f_m$', fontweight='bold')
ax4.set_xlabel('Frequência (kHz)')
ax4.set_ylabel('Magnitude')
ax4.legend(fontsize=7.5)
ax4.grid(True, alpha=0.3)

fig.suptitle('Prática 02 – AM DSB-SC: gráfico esperado',
             fontsize=13, fontweight='bold')
fig.savefig('grafico_esperado.png', dpi=180, bbox_inches='tight')
print('Salvo: grafico_esperado.png')
