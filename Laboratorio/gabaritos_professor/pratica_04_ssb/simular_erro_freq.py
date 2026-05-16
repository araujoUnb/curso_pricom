"""
Simulacao Q4 (Pratica 04 SSB): efeito de erro de frequencia Df no LO
para DSB-SC vs SSB-USB.

Verifica:
  DSB-SC com Df:  y(t) = m(t) cos(2 pi Df t)
                  Y(f) = (1/2)[M(f-Df) + M(f+Df)]   -> duplicacao espectral (batimento)

  SSB-USB com Df: y(t) = m(t) cos(2 pi Df t) + mh(t) sin(2 pi Df t)
                  = Re{ m_+(t) exp(-j 2 pi Df t) }
                  -> translacao rigida do espectro por -Df ("Donald Duck")

Gera figura comparativa salva em grafico_erro_freq_lo.png.
"""

import numpy as np
import matplotlib.pyplot as plt

def hilbert(x):
    """Transformada de Hilbert via FFT (sem dependencia de scipy)."""
    N = len(x)
    X = np.fft.fft(x)
    H = np.zeros(N)
    if N % 2 == 0:
        H[0] = H[N//2] = 1
        H[1:N//2] = 2
    else:
        H[0] = 1
        H[1:(N+1)//2] = 2
    return np.fft.ifft(X * H)

# Parametros (mesmos da pratica)
samp_rate = 48000        # Hz
fc = 12000               # portadora
T  = 0.5                 # 0.5 s -> resolucao espectral de 2 Hz
N  = int(samp_rate * T)
t  = np.arange(N) / samp_rate

# Mensagem multi-tom (simula voz: 3 tons harmonicos)
f1, f2, f3 = 300.0, 600.0, 900.0   # f0 + 2f0 + 3f0
m = (np.cos(2*np.pi*f1*t)
     + 0.7*np.cos(2*np.pi*f2*t)
     + 0.5*np.cos(2*np.pi*f3*t))

# Hilbert para SSB
m_hat = np.imag(hilbert(m))

# Geracao
s_dsb = m * np.cos(2*np.pi*fc*t)
s_usb = m * np.cos(2*np.pi*fc*t) - m_hat * np.sin(2*np.pi*fc*t)

# Erro de frequencia no LO
Df_list = [0.0, 50.0, 200.0]  # Hz

def lpf(x, fcut, fs):
    """LPF FFT simples para filtrar componentes em 2fc."""
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1/fs)
    X[f > fcut] = 0
    return np.fft.irfft(X, n=len(x))

def demod(s, fc, Df, fs):
    lo = 2 * np.cos(2*np.pi*(fc + Df)*t)
    return lpf(s * lo, fcut=2000.0, fs=fs)

fig, axes = plt.subplots(2, 3, figsize=(13, 6.5))
fig.suptitle("Erro de frequencia Df no LO: DSB-SC vs SSB-USB\n"
             "mensagem com tons em 300/600/900 Hz",
             fontsize=12)

freqs = np.fft.rfftfreq(N, 1/samp_rate)

for col, Df in enumerate(Df_list):
    y_dsb = demod(s_dsb, fc, Df, samp_rate)
    y_ssb = demod(s_usb, fc, Df, samp_rate)

    Yd = np.abs(np.fft.rfft(y_dsb)) / N * 2
    Ys = np.abs(np.fft.rfft(y_ssb)) / N * 2

    ax = axes[0, col]
    ax.plot(freqs, 20*np.log10(Yd + 1e-12), color='C0', lw=1.2)
    ax.set_xlim(0, 1500)
    ax.set_ylim(-60, 5)
    ax.set_title(f"DSB-SC  Df = {Df:.0f} Hz")
    ax.set_xlabel("f (Hz)"); ax.set_ylabel("|Y(f)| (dB)")
    ax.grid(alpha=0.3)
    for f0 in (f1, f2, f3):
        ax.axvline(f0, color='gray', lw=0.4, ls=':')

    ax = axes[1, col]
    ax.plot(freqs, 20*np.log10(Ys + 1e-12), color='C3', lw=1.2)
    ax.set_xlim(0, 1500)
    ax.set_ylim(-60, 5)
    ax.set_title(f"SSB-USB  Df = {Df:.0f} Hz")
    ax.set_xlabel("f (Hz)"); ax.set_ylabel("|Y(f)| (dB)")
    ax.grid(alpha=0.3)
    for f0 in (f1, f2, f3):
        ax.axvline(f0, color='gray', lw=0.4, ls=':')

plt.tight_layout(rect=(0, 0, 1, 0.95))
out = "grafico_erro_freq_lo.png"
plt.savefig(out, dpi=140, bbox_inches='tight')
print(f"Figura salva: {out}")

# Numeros chave para o gabarito
print("\n=== Medidas chave (picos espectrais por componente da mensagem) ===")
for Df in Df_list:
    y_dsb = demod(s_dsb, fc, Df, samp_rate)
    y_ssb = demod(s_usb, fc, Df, samp_rate)
    Yd = np.abs(np.fft.rfft(y_dsb)) / N * 2
    Ys = np.abs(np.fft.rfft(y_ssb)) / N * 2

    print(f"\nDf = {Df:.0f} Hz")
    print("  DSB-SC  expected peaks at f_k +/- Df:")
    for f0 in (f1, f2, f3):
        for sign in (-1, 1):
            f_peak = f0 + sign*Df
            if f_peak > 0:
                i = int(round(f_peak * T))
                print(f"    f={f_peak:6.1f} Hz  |Y| = {Yd[i]:.3f}")
    print("  SSB-USB expected peaks at f_k - Df  (shift uniforme):")
    for f0 in (f1, f2, f3):
        f_peak = f0 - Df
        if f_peak > 0:
            i = int(round(f_peak * T))
            print(f"    f={f_peak:6.1f} Hz  |Y| = {Ys[i]:.3f}")
