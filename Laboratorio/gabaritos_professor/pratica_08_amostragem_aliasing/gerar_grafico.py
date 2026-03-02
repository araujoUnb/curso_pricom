"""
Gráfico esperado -- Prática 08: Amostragem e Aliasing
Gera 'grafico_esperado.png' com quatro subplots:
  1. Espectro: sinal 1000 Hz com fs_ef=12000 Hz (sem aliasing)
  2. Espectro: sinal 7000 Hz com fs_ef=12000 Hz (aliasing em 5000 Hz)
  3. Filtro anti-aliasing: antes e depois (cenário C)
  4. Frequência aparente vs frequência real (diagrama de dobragem)
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

# ------------------------------------------------------------------
fs_orig = 48_000   # taxa original de simulação
N = int(0.2 * fs_orig)   # 200 ms

t_orig = np.arange(N) / fs_orig


def make_signal(f_hz, amp=1.0):
    return amp * np.cos(2 * np.pi * f_hz * t_orig)


def decimate(sig, factor):
    """Subamostragem por fator 'factor' (Keep 1 in N)."""
    return sig[::factor]


def lowpass_fir(sig, cutoff_hz, fs_in, n_taps=127):
    fc_n = cutoff_hz / (fs_in / 2)
    h = np.sinc(fc_n * (np.arange(n_taps) - n_taps // 2))
    h *= np.blackman(n_taps)
    h /= h.sum()
    return np.convolve(sig, h, mode='same')


def fft_onesided(sig, fs_in, n_pts=None):
    if n_pts is None:
        n_pts = len(sig)
    spec = np.fft.rfft(sig, n=n_pts)
    freqs = np.fft.rfftfreq(n_pts, d=1 / fs_in)
    mag = np.abs(spec) / (n_pts / 2)
    return freqs, mag


# ------------------------------------------------------------------
# Cenários do enunciado
# fs_ef = fs_orig / decim
# ------------------------------------------------------------------
# Cenário A: f=1000 Hz, decim=4 → fs_ef=12000 Hz (Nyquist: ok)
# Cenário C: f=7000 Hz, decim=4 → fs_ef=12000 Hz (aliasing em 5000 Hz)

decim_A_C = 4      # fs_ef = 12000 Hz
fs_ef_AC = fs_orig / decim_A_C   # 12000 Hz

s_A = make_signal(1_000)    # Cenário A: sem aliasing
s_C = make_signal(7_000)    # Cenário C: aliasing em 5000 Hz
s_C_aa = lowpass_fir(s_C, fs_ef_AC / 2, fs_orig)   # com filtro AA

# Decimar
sd_A = decimate(s_A, decim_A_C)
sd_C = decimate(s_C, decim_A_C)
sd_C_aa = decimate(s_C_aa, decim_A_C)

# ------------------------------------------------------------------
# Figura
# ------------------------------------------------------------------
fig = plt.figure(figsize=(14, 9), constrained_layout=True)
gs = gridspec.GridSpec(2, 2, figure=fig)

# 1. Espectro cenário A (sem aliasing)
ax1 = fig.add_subplot(gs[0, 0])
f_A, m_A = fft_onesided(sd_A, fs_ef_AC)
ax1.plot(f_A, m_A, lw=1.5, label='Sinal decimado (1000 Hz)')
ax1.axvline(1_000, color='C2', ls='--', lw=1.0, label='Freq. real = 1000 Hz')
ax1.axvline(fs_ef_AC / 2, color='red', ls=':', lw=0.8, alpha=0.7,
            label=f'Nyquist = {fs_ef_AC/2:.0f} Hz')
ax1.set_xlim(0, fs_ef_AC / 2)
ax1.set_title('1 – Cenário A: 1000 Hz, $f_{s,ef}=12000$ Hz\n(Nyquist satisfeito)', fontweight='bold')
ax1.set_xlabel('Frequência (Hz)'); ax1.set_ylabel('Magnitude')
ax1.legend(fontsize=8); ax1.grid(True, alpha=0.3)

# 2. Espectro cenário C (com aliasing)
ax2 = fig.add_subplot(gs[0, 1])
f_C, m_C = fft_onesided(sd_C, fs_ef_AC)
ax2.plot(f_C, m_C, color='C1', lw=1.5, label='Sinal decimado (7000 Hz)')
alias_freq = abs(7_000 - 12_000)   # = 5000 Hz
ax2.axvline(alias_freq, color='C3', ls='--', lw=1.5,
            label=f'Aliasing em {alias_freq} Hz\n(real = 7000 Hz)')
ax2.axvline(fs_ef_AC / 2, color='red', ls=':', lw=0.8, alpha=0.7,
            label=f'Nyquist = {fs_ef_AC/2:.0f} Hz')
ax2.set_xlim(0, fs_ef_AC / 2)
ax2.set_title('2 – Cenário C: 7000 Hz, $f_{s,ef}=12000$ Hz\n(Aliasing → pico em 5000 Hz!)', fontweight='bold')
ax2.set_xlabel('Frequência (Hz)'); ax2.set_ylabel('Magnitude')
ax2.legend(fontsize=8); ax2.grid(True, alpha=0.3)

# 3. Filtro anti-aliasing: cenário C com e sem LPF
ax3 = fig.add_subplot(gs[1, 0])
f_C_aa, m_C_aa = fft_onesided(sd_C_aa, fs_ef_AC)
ax3.plot(f_C, m_C, color='C1', lw=1.5, ls='--', label='Sem filtro AA (aliasing em 5000 Hz)', alpha=0.8)
ax3.plot(f_C_aa, m_C_aa, color='C0', lw=1.5, label='Com filtro AA (sinal suprimido)')
ax3.axvline(fs_ef_AC / 2, color='red', ls=':', lw=0.8, alpha=0.7, label=f'Nyquist = {fs_ef_AC/2:.0f} Hz')
ax3.set_xlim(0, fs_ef_AC / 2)
ax3.set_title('3 – Filtro anti-aliasing: cenário C\n(7000 Hz suprimido antes da decimação)', fontweight='bold')
ax3.set_xlabel('Frequência (Hz)'); ax3.set_ylabel('Magnitude')
ax3.legend(fontsize=8); ax3.grid(True, alpha=0.3)

# 4. Diagrama de dobragem: frequência aparente vs real
ax4 = fig.add_subplot(gs[1, 1])
for fs_ef, color, ls, lbl in [(12_000, 'C0', '-', '$f_{s,ef}=12000$ Hz'),
                                (4_800, 'C1', '--', '$f_{s,ef}=4800$ Hz'),
                                (3_000, 'C2', '-.', '$f_{s,ef}=3000$ Hz')]:
    f_real = np.linspace(0, fs_ef * 1.5, 500)
    f_apparent = np.abs(((f_real + fs_ef / 2) % fs_ef) - fs_ef / 2)
    ax4.plot(f_real, f_apparent, color=color, ls=ls, lw=1.5, label=lbl)

# Linha identidade (sem aliasing)
f_id = np.linspace(0, fs_ef_AC, 300)
ax4.plot(f_id, f_id, 'k:', lw=1.0, alpha=0.5, label='Identidade (sem aliasing)')
ax4.set_title('4 – Frequência aparente vs frequência real\n(diagrama de dobragem/folding)', fontweight='bold')
ax4.set_xlabel('Frequência real $f_0$ (Hz)')
ax4.set_ylabel('Frequência aparente $f_{\\mathrm{alias}}$ (Hz)')
ax4.legend(fontsize=8); ax4.grid(True, alpha=0.3)

# Marcar os cenários A, C, E, F
cenarios = [
    (1_000, 'A', 12_000, 'C0'),
    (7_000, 'C', 12_000, 'C0'),
    (2_500, 'E', 4_800, 'C1'),
    (3_500, 'F', 4_800, 'C1'),
]
for f0, name, fs_ef_ref, color in cenarios:
    f_ap = abs(((f0 + fs_ef_ref / 2) % fs_ef_ref) - fs_ef_ref / 2)
    ax4.annotate(name, xy=(f0, f_ap), fontsize=9, fontweight='bold',
                 xytext=(f0 + 300, f_ap + 200), color=color,
                 arrowprops=dict(arrowstyle='->', color=color, lw=0.8))

fig.suptitle('Prática 08 – Amostragem e Aliasing: gráfico esperado',
             fontsize=13, fontweight='bold')
fig.savefig('grafico_esperado.png', dpi=180, bbox_inches='tight')
print('Salvo: grafico_esperado.png')
