"""
Gráfico esperado -- Prática 04: Modulação SSB
Gera 'grafico_esperado.png' com quatro subplots:
  1. DSB-SC no espectro (dois picos)
  2. SSB-USB e SSB-LSB no espectro (um pico cada)
  3. Sinal DSB-SC vs SSB no tempo
  4. Comparação de largura de banda DSB vs SSB
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

# ------------------------------------------------------------------
fs = 48_000;  fc = 12_000;  fm = 2_000
Am = 1.0;  Ac = 1.0
N = int(0.010 * fs)   # 10 ms
t = np.arange(N) / fs

msg = Am * np.cos(2 * np.pi * fm * t)
carrier = Ac * np.cos(2 * np.pi * fc * t)
dsb_sc = msg * carrier

# SSB via método de fase (Hilbert)
# SSB-USB = I*cos - Q*sin  (I = msg, Q = Hilbert(msg))
msg_hilbert = np.imag(np.fft.ifft(
    np.fft.fft(msg) * (-1j * np.sign(np.fft.fftfreq(N)))
))
carrier_sin = Ac * np.sin(2 * np.pi * fc * t)
ssb_usb = msg * carrier - msg_hilbert * carrier_sin
ssb_lsb = msg * carrier + msg_hilbert * carrier_sin


def fft_onesided(sig, fs_in):
    spec = np.fft.rfft(sig)
    freqs = np.fft.rfftfreq(len(sig), d=1 / fs_in)
    mag = np.abs(spec) / (len(sig) / 2)
    return freqs, mag


fig = plt.figure(figsize=(14, 9), constrained_layout=True)
gs = gridspec.GridSpec(2, 2, figure=fig)

# 1. Espectro DSB-SC
ax1 = fig.add_subplot(gs[0, 0])
f_d, m_d = fft_onesided(dsb_sc, fs)
ax1.plot(f_d / 1e3, m_d, lw=1.5, label='DSB-SC')
ax1.axvline((fc - fm) / 1e3, color='C1', ls='--', lw=1.0, label=f'LSB = {(fc-fm)//1000} kHz')
ax1.axvline((fc + fm) / 1e3, color='C2', ls='--', lw=1.0, label=f'USB = {(fc+fm)//1000} kHz')
ax1.axvline(fc / 1e3, color='red', ls=':', lw=0.8, alpha=0.5, label=f'$f_c$ = {fc//1000} kHz (sem pico)')
ax1.set_xlim(8, 16); ax1.set_ylim(0, None)
ax1.set_title('1 – DSB-SC: dois picos (LSB e USB)', fontweight='bold')
ax1.set_xlabel('Frequência (kHz)'); ax1.set_ylabel('Magnitude')
ax1.legend(fontsize=8); ax1.grid(True, alpha=0.3)

# Anotação de largura de banda
ymax = m_d.max() * 0.8
ax1.annotate('', xy=((fc+fm)/1e3, ymax), xytext=((fc-fm)/1e3, ymax),
             arrowprops=dict(arrowstyle='<->', color='black', lw=1.5))
ax1.text(fc / 1e3, ymax * 1.05, f'$B_{{DSB}} = 2f_m = {2*fm//1000}$ kHz', ha='center', fontsize=8)

# 2. SSB-USB e SSB-LSB
ax2 = fig.add_subplot(gs[0, 1])
f_u, m_u = fft_onesided(ssb_usb, fs)
f_l, m_l = fft_onesided(ssb_lsb, fs)
ax2.plot(f_u / 1e3, m_u, lw=1.5, label='SSB-USB', color='C2')
ax2.plot(f_l / 1e3, m_l, lw=1.5, ls='--', label='SSB-LSB', color='C1')
ax2.axvline(fc / 1e3, color='red', ls=':', lw=0.8, alpha=0.5)
ax2.set_xlim(8, 16); ax2.set_ylim(0, None)
ax2.set_title('2 – SSB: apenas uma banda lateral', fontweight='bold')
ax2.set_xlabel('Frequência (kHz)'); ax2.set_ylabel('Magnitude')
ax2.legend(fontsize=9); ax2.grid(True, alpha=0.3)
ymax2 = m_u.max() * 0.85
ax2.annotate('', xy=((fc+fm)/1e3, ymax2), xytext=(fc/1e3, ymax2),
             arrowprops=dict(arrowstyle='<->', color='C2', lw=1.5))
ax2.text((fc+fm/2)/1e3, ymax2*1.05, f'$B_{{SSB}}\\!=\\!f_m$', ha='center', fontsize=8, color='C2')

# 3. Sinal no tempo: DSB-SC vs SSB-USB
ax3 = fig.add_subplot(gs[1, 0])
n_show = int(0.004 * fs)   # 4 ms
ax3.plot(t[:n_show] * 1e3, msg[:n_show], 'k--', lw=1.2, label='Mensagem $m(t)$', alpha=0.7)
ax3.plot(t[:n_show] * 1e3, dsb_sc[:n_show], lw=1.2, label='DSB-SC', alpha=0.9)
ax3.plot(t[:n_show] * 1e3, ssb_usb[:n_show], lw=1.2, ls='-.', label='SSB-USB', alpha=0.9)
ax3.set_title('3 – Sinal no tempo: DSB-SC vs SSB-USB', fontweight='bold')
ax3.set_xlabel('Tempo (ms)'); ax3.set_ylabel('Amplitude')
ax3.legend(fontsize=9); ax3.grid(True, alpha=0.3)

# 4. Comparação de larguras de banda
ax4 = fig.add_subplot(gs[1, 1])
bw_types = ['DSB-SC\n(Ambas BLs)', 'SSB-USB\n(Só USB)', 'SSB-LSB\n(Só LSB)', 'AM +C\n(μ=1)']
bw_vals = [2 * fm, fm, fm, 2 * fm]
colors_bar = ['C0', 'C2', 'C1', 'C3']
bars = ax4.bar(bw_types, bw_vals, color=colors_bar, edgecolor='black', linewidth=0.8, width=0.5)
ax4.set_title('4 – Comparação de largura de banda', fontweight='bold')
ax4.set_ylabel('Largura de banda (Hz)')
for bar, val in zip(bars, bw_vals):
    ax4.text(bar.get_x() + bar.get_width() / 2, val + 50, f'{val} Hz',
             ha='center', va='bottom', fontsize=9)
ax4.set_ylim(0, bw_vals[0] * 1.3)
ax4.grid(True, axis='y', alpha=0.3)

fig.suptitle('Prática 04 – Modulação SSB: gráfico esperado',
             fontsize=13, fontweight='bold')
fig.savefig('grafico_esperado.png', dpi=180, bbox_inches='tight')
print('Salvo: grafico_esperado.png')
