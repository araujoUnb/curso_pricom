#!/usr/bin/env python3
"""
Gera figuras ilustrativas (parte 2) para o capítulo 3:
Parseval, DEE, PSD, ruído, DFT/janelamento, aliasing, banda básica/passante,
down-conversion, transformada de Hilbert e envelope AM.
Curso de Princípios de Comunicação - UnB.
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy import signal as sig
import os

# ---------- estilo global ----------
plt.rcParams.update({
    'text.usetex': False,
    'font.size': 12,
    'axes.labelsize': 14,
    'axes.titlesize': 14,
    'xtick.labelsize': 11,
    'ytick.labelsize': 11,
    'axes.grid': True,
    'grid.linestyle': '--',
    'grid.alpha': 0.4,
    'figure.facecolor': 'white',
    'axes.facecolor': 'white',
    'savefig.facecolor': 'white',
    'savefig.bbox': 'tight',
    'savefig.dpi': 150,
})

OUTDIR = os.path.dirname(os.path.abspath(__file__))


def save(fig, name):
    base = os.path.join(OUTDIR, name)
    fig.savefig(base + '.pdf')
    fig.savefig(base + '.png', dpi=150)
    plt.close(fig)
    print(f'  -> {name}.pdf / .png')


# ====================================================================
# 1. Parseval – Energia no Tempo = Energia na Frequência
# ====================================================================
def fig_parseval_energia_demo():
    T = 1e-3          # largura do pulso (s)
    A = 2.0
    N = 4096
    t = np.linspace(-3*T, 3*T, N)
    dt = t[1] - t[0]

    # pulso retangular
    x = np.where(np.abs(t) <= T/2, A, 0.0)

    # energia no tempo
    E_time = np.trapezoid(x**2, t)

    # espectro
    f = np.fft.fftshift(np.fft.fftfreq(N, d=dt))
    X = np.fft.fftshift(np.fft.fft(x)) * dt
    DEE = np.abs(X)**2

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    # --- tempo ---
    ax = axes[0]
    ax.plot(t*1e3, x, 'C0', lw=2, label='$x(t)$')
    ax.fill_between(t*1e3, 0, x**2, alpha=0.3, color='C1', label='$x^2(t)$')
    ax.set_xlabel('Tempo (ms)')
    ax.set_ylabel('Amplitude')
    ax.set_title(f'Domínio do Tempo — $E = {E_time:.4f}$ J')
    ax.legend()

    # --- frequência ---
    ax = axes[1]
    ax.plot(f*1e-3, DEE*1e3, 'C2', lw=2, label='$|X(f)|^2$')
    ax.fill_between(f*1e-3, 0, DEE*1e3, alpha=0.3, color='C3')
    ax.set_xlabel('Frequência (kHz)')
    ax.set_ylabel('DEE (×$10^{-3}$)')
    ax.set_title('Domínio da Frequência — mesma energia via Parseval')
    ax.set_xlim([-5, 5])
    ax.legend()

    fig.suptitle('Teorema de Parseval: Energia no Tempo = Energia na Frequência',
                 fontsize=14, fontweight='bold', y=1.02)
    fig.tight_layout()
    save(fig, 'parseval_energia_demo')


# ====================================================================
# 2. Densidade Espectral de Energia (DEE) para diferentes sinais
# ====================================================================
def fig_densidade_espectral_energia():
    N = 8192
    T = 2e-3
    t = np.linspace(-4*T, 4*T, N)
    dt = t[1] - t[0]

    # Sinais com mesma energia
    # 1) Pulso retangular
    A1 = 1.0
    x1 = np.where(np.abs(t) <= T/2, A1, 0.0)
    E1 = np.trapezoid(x1**2, t)

    # 2) Exponencial decaimento (causal)
    alpha = 1.0 / T
    x2_raw = np.where(t >= 0, np.exp(-alpha * t), 0.0)
    E2_raw = np.trapezoid(x2_raw**2, t)
    x2 = x2_raw * np.sqrt(E1 / E2_raw)

    # 3) Gaussiana
    sigma = T / 3
    x3_raw = np.exp(-t**2 / (2 * sigma**2))
    E3_raw = np.trapezoid(x3_raw**2, t)
    x3 = x3_raw * np.sqrt(E1 / E3_raw)

    # espectros
    f = np.fft.fftshift(np.fft.fftfreq(N, d=dt))
    def dee(x):
        X = np.fft.fftshift(np.fft.fft(x)) * dt
        return np.abs(X)**2

    DEE1, DEE2, DEE3 = dee(x1), dee(x2), dee(x3)

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    ax = axes[0]
    ax.plot(t*1e3, x1, 'C0', lw=2, label='Retangular')
    ax.plot(t*1e3, x2, 'C1', lw=2, label='Exponencial')
    ax.plot(t*1e3, x3, 'C2', lw=2, label='Gaussiana')
    ax.set_xlabel('Tempo (ms)')
    ax.set_ylabel('Amplitude')
    ax.set_title('Sinais com mesma energia')
    ax.legend()

    ax = axes[1]
    fk = f * 1e-3
    ax.plot(fk, DEE1*1e3, 'C0', lw=2, label='Retangular')
    ax.plot(fk, DEE2*1e3, 'C1', lw=2, label='Exponencial')
    ax.plot(fk, DEE3*1e3, 'C2', lw=2, label='Gaussiana')
    ax.set_xlabel('Frequência (kHz)')
    ax.set_ylabel('DEE (×$10^{-3}$)')
    ax.set_title('Densidade Espectral de Energia $|X(f)|^2$')
    ax.set_xlim([-3, 3])
    ax.legend()

    fig.tight_layout()
    save(fig, 'densidade_espectral_energia')


# ====================================================================
# 3. PSD de uma senóide
# ====================================================================
def fig_psd_senoide():
    f0 = 1000   # Hz
    A = 2.0
    t = np.linspace(0, 5e-3, 2000)

    x = A * np.cos(2 * np.pi * f0 * t)

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    ax = axes[0]
    ax.plot(t*1e3, x, 'C0', lw=2)
    ax.set_xlabel('Tempo (ms)')
    ax.set_ylabel('Amplitude')
    ax.set_title(f'$x(t) = {A}\\cos(2\\pi \\cdot {f0}\\,t)$')

    ax = axes[1]
    freqs = np.array([-f0, f0])
    psd_vals = np.array([A**2/4, A**2/4])
    markerline, stemlines, baseline = ax.stem(freqs*1e-3, psd_vals, linefmt='C1-', markerfmt='C1o', basefmt='k-')
    stemlines.set_linewidth(2)
    markerline.set_markersize(8)
    ax.set_xlabel('Frequência (kHz)')
    ax.set_ylabel('PSD')
    ax.set_title(f'PSD: impulsos $A^2/4 = {A**2/4:.1f}$ em $\\pm f_0$')
    ax.set_xlim([-3, 3])
    ax.set_ylim([0, A**2/4 * 1.3])
    ax.annotate(f'$A^2/4={A**2/4:.0f}$', xy=(f0*1e-3, A**2/4),
                xytext=(f0*1e-3+0.5, A**2/4+0.15), fontsize=11,
                arrowprops=dict(arrowstyle='->', color='C1'))

    fig.tight_layout()
    save(fig, 'psd_senoide')


# ====================================================================
# 4. Ruído branco filtrado
# ====================================================================
def fig_ruido_branco_filtrado():
    fs = 48000
    N = 48000  # 1 segundo
    np.random.seed(42)
    noise = np.random.randn(N)
    t = np.arange(N) / fs

    # Filtro Butterworth passa-baixa fc=2kHz, ordem 4
    fc = 2000
    sos = sig.butter(4, fc, btype='low', fs=fs, output='sos')
    filtered = sig.sosfilt(sos, noise)

    # PSDs via Welch
    f_w, Pxx_white = sig.welch(noise, fs, nperseg=1024)
    f_f, Pxx_filt = sig.welch(filtered, fs, nperseg=1024)

    fig, axes = plt.subplots(2, 2, figsize=(13, 6))

    # branco – tempo
    ax = axes[0, 0]
    ax.plot(t[:2000]*1e3, noise[:2000], 'C0', lw=0.5)
    ax.set_xlabel('Tempo (ms)')
    ax.set_ylabel('Amplitude')
    ax.set_title('Ruído branco — domínio do tempo')

    # branco – PSD
    ax = axes[0, 1]
    ax.semilogy(f_w*1e-3, Pxx_white, 'C0', lw=1.5)
    ax.axhline(y=np.mean(Pxx_white), color='C3', ls='--', lw=1.5, label='$N_0/2$ (média)')
    ax.set_xlabel('Frequência (kHz)')
    ax.set_ylabel('PSD (V²/Hz)')
    ax.set_title('PSD — ruído branco (plano)')
    ax.legend()

    # filtrado – tempo
    ax = axes[1, 0]
    ax.plot(t[:2000]*1e3, filtered[:2000], 'C1', lw=0.5)
    ax.set_xlabel('Tempo (ms)')
    ax.set_ylabel('Amplitude')
    ax.set_title('Ruído filtrado (LPF 2 kHz) — domínio do tempo')

    # filtrado – PSD
    ax = axes[1, 1]
    ax.semilogy(f_f*1e-3, Pxx_filt, 'C1', lw=1.5)
    ax.axvline(x=fc*1e-3, color='C3', ls='--', lw=1.5, label=f'$f_c = {fc/1e3:.0f}$ kHz')
    ax.set_xlabel('Frequência (kHz)')
    ax.set_ylabel('PSD (V²/Hz)')
    ax.set_title('PSD — ruído filtrado por $|H(f)|^2$')
    ax.legend()

    fig.tight_layout()
    save(fig, 'ruido_branco_filtrado')


# ====================================================================
# 5. DFT e Janelamento (vazamento espectral)
# ====================================================================
def fig_dft_janelamento():
    fs = 48000
    f0 = 1000
    N = 1024
    n = np.arange(N)
    x = np.cos(2 * np.pi * f0 * n / fs)

    windows = {
        'Retangular': sig.windows.boxcar(N),
        'Hamming': sig.windows.hamming(N),
        'Hann': sig.windows.hann(N),
        'Blackman-Harris': sig.windows.blackmanharris(N),
    }

    fig, axes = plt.subplots(2, 2, figsize=(13, 6))
    positions = [(0, 0), (0, 1), (1, 0), (1, 1)]

    for (name, w), pos in zip(windows.items(), positions):
        ax = axes[pos]
        xw = x * w
        Xw = np.fft.fft(xw, n=4*N)
        freqs = np.fft.fftfreq(4*N, 1/fs)
        idx = freqs >= 0
        mag_dB = 20 * np.log10(np.abs(Xw[idx]) / np.max(np.abs(Xw[idx])) + 1e-12)
        ax.plot(freqs[idx]*1e-3, mag_dB, lw=1.5)
        ax.set_xlim([0, 5])
        ax.set_ylim([-120, 5])
        ax.set_xlabel('Frequência (kHz)')
        ax.set_ylabel('Magnitude (dB)')
        ax.set_title(f'Janela {name}')

    fig.suptitle('Efeito do janelamento na DFT — vazamento espectral (spectral leakage)',
                 fontsize=13, fontweight='bold', y=1.02)
    fig.tight_layout()
    save(fig, 'dft_janelamento')


# ====================================================================
# 6. Aliasing (Teorema de Nyquist)
# ====================================================================
def fig_aliasing_demo():
    # sinal analógico: 500 Hz + 3000 Hz
    t_cont = np.linspace(0, 4e-3, 10000)
    x_cont = np.cos(2*np.pi*500*t_cont) + 0.5*np.cos(2*np.pi*3000*t_cont)

    fig, axes = plt.subplots(3, 1, figsize=(12, 6), sharex=True)

    # --- sinal original ---
    ax = axes[0]
    ax.plot(t_cont*1e3, x_cont, 'C0', lw=1.5)
    ax.set_ylabel('Amplitude')
    ax.set_title('Sinal original: $\\cos(2\\pi 500t) + 0{,}5\\cos(2\\pi 3000t)$')

    # --- amostragem correta (fs=8000) ---
    fs1 = 8000
    n1 = np.arange(0, 4e-3, 1/fs1)
    x1 = np.cos(2*np.pi*500*n1) + 0.5*np.cos(2*np.pi*3000*n1)
    # reconstrução via sinc
    t_recon = t_cont
    x_recon1 = np.zeros_like(t_recon)
    for k in range(len(n1)):
        x_recon1 += x1[k] * np.sinc((t_recon - n1[k]) * fs1)

    ax = axes[1]
    ax.plot(t_recon*1e3, x_recon1, 'C2', lw=1.5, label=f'Reconstruído ($f_s={fs1}$ Hz)')
    ax.stem(n1*1e3, x1, linefmt='C1-', markerfmt='C1o', basefmt=' ')
    ax.set_ylabel('Amplitude')
    ax.set_title(f'Amostragem a $f_s = {fs1}$ Hz (acima de Nyquist) — sem aliasing')
    ax.legend(fontsize=10)

    # --- amostragem com aliasing (fs=4000) ---
    fs2 = 4000
    n2 = np.arange(0, 4e-3, 1/fs2)
    x2 = np.cos(2*np.pi*500*n2) + 0.5*np.cos(2*np.pi*3000*n2)
    x_recon2 = np.zeros_like(t_recon)
    for k in range(len(n2)):
        x_recon2 += x2[k] * np.sinc((t_recon - n2[k]) * fs2)

    ax = axes[2]
    ax.plot(t_recon*1e3, x_recon2, 'C3', lw=1.5, label=f'Reconstruído ($f_s={fs2}$ Hz)')
    ax.stem(n2*1e3, x2, linefmt='C1-', markerfmt='C1o', basefmt=' ')
    ax.set_xlabel('Tempo (ms)')
    ax.set_ylabel('Amplitude')
    ax.set_title(f'Amostragem a $f_s = {fs2}$ Hz (abaixo de Nyquist para 3 kHz) — aliasing!')
    ax.legend(fontsize=10)

    fig.suptitle('Teorema de Nyquist: $f_s \\geq 2 f_{\\max}$ para evitar aliasing',
                 fontsize=13, fontweight='bold', y=1.02)
    fig.tight_layout()
    save(fig, 'aliasing_demo')


# ====================================================================
# 7. Banda básica vs. banda passante
# ====================================================================
def fig_banda_basica_vs_passante():
    fs = 100000
    dur = 0.02   # 20 ms
    t = np.arange(0, dur, 1/fs)
    N = len(t)

    # banda básica
    m = (np.cos(2*np.pi*100*t) + 0.7*np.cos(2*np.pi*300*t)
         + 0.5*np.cos(2*np.pi*500*t))

    # portadora
    fc = 5000
    c = np.cos(2*np.pi*fc*t)

    # sinal AM (DSB-SC)
    s = m * c

    # espectros
    freqs = np.fft.fftshift(np.fft.fftfreq(N, 1/fs))
    def mag(x):
        return np.abs(np.fft.fftshift(np.fft.fft(x))) / N

    M = mag(m)
    C = mag(c)
    S = mag(s)

    fig, axes = plt.subplots(3, 2, figsize=(13, 7))
    t_ms = t * 1e3
    f_kHz = freqs * 1e-3
    t_show = 10  # ms

    # linha 1: m(t) e |M(f)|
    axes[0, 0].plot(t_ms, m, 'C0', lw=1.2)
    axes[0, 0].set_xlim([0, t_show])
    axes[0, 0].set_ylabel('$m(t)$')
    axes[0, 0].set_title('Sinal em banda básica $m(t)$')

    axes[0, 1].plot(f_kHz, M, 'C0', lw=1.5)
    axes[0, 1].set_xlim([-2, 2])
    axes[0, 1].set_ylabel('$|M(f)|$')
    axes[0, 1].set_title('Espectro $|M(f)|$ — largura de faixa $W=500$ Hz')

    # linha 2: c(t) e |C(f)|
    axes[1, 0].plot(t_ms, c, 'C1', lw=0.8)
    axes[1, 0].set_xlim([0, 2])
    axes[1, 0].set_ylabel('$c(t)$')
    axes[1, 0].set_title(f'Portadora $c(t) = \\cos(2\\pi \\cdot {fc/1e3:.0f}\\,\\mathrm{{kHz}}\\cdot t)$')

    axes[1, 1].plot(f_kHz, C, 'C1', lw=1.5)
    axes[1, 1].set_xlim([-8, 8])
    axes[1, 1].set_ylabel('$|C(f)|$')
    axes[1, 1].set_title('Espectro da portadora — impulsos em $\\pm f_c$')

    # linha 3: s(t) e |S(f)|
    axes[2, 0].plot(t_ms, s, 'C2', lw=0.8)
    axes[2, 0].set_xlim([0, t_show])
    axes[2, 0].set_xlabel('Tempo (ms)')
    axes[2, 0].set_ylabel('$s(t)$')
    axes[2, 0].set_title('Sinal em banda passante $s(t) = m(t)\\,c(t)$')

    axes[2, 1].plot(f_kHz, S, 'C2', lw=1.5)
    axes[2, 1].set_xlim([-8, 8])
    axes[2, 1].set_xlabel('Frequência (kHz)')
    axes[2, 1].set_ylabel('$|S(f)|$')
    axes[2, 1].set_title('Espectro $|S(f)|$ — deslocado para $\\pm f_c$')

    fig.tight_layout()
    save(fig, 'banda_basica_vs_passante')


# ====================================================================
# 8. Down-conversion básica
# ====================================================================
def fig_downconversion_basica():
    fs = 100000
    dur = 0.02
    t = np.arange(0, dur, 1/fs)
    N = len(t)

    fc = 5000
    m = (np.cos(2*np.pi*100*t) + 0.7*np.cos(2*np.pi*300*t)
         + 0.5*np.cos(2*np.pi*500*t))

    # banda passante
    s = m * np.cos(2*np.pi*fc*t)

    # multiplicação pela portadora novamente
    v = s * np.cos(2*np.pi*fc*t)   # = m/2 + m*cos(4π fc t)/2

    # filtro passa-baixa (recuperar m/2)
    sos = sig.butter(6, 1500, btype='low', fs=fs, output='sos')
    r = sig.sosfilt(sos, v)

    freqs = np.fft.fftshift(np.fft.fftfreq(N, 1/fs))
    f_kHz = freqs * 1e-3
    def mag(x):
        return np.abs(np.fft.fftshift(np.fft.fft(x))) / N

    S, V, R = mag(s), mag(v), mag(r)

    fig, axes = plt.subplots(3, 2, figsize=(13, 7))
    t_ms = t * 1e3
    t_show = 10

    # linha 1: s(t) passante
    axes[0, 0].plot(t_ms, s, 'C0', lw=0.8)
    axes[0, 0].set_xlim([0, t_show])
    axes[0, 0].set_ylabel('$s(t)$')
    axes[0, 0].set_title('Sinal em banda passante')
    axes[0, 1].plot(f_kHz, S, 'C0', lw=1.5)
    axes[0, 1].set_xlim([-12, 12])
    axes[0, 1].set_ylabel('$|S(f)|$')
    axes[0, 1].set_title('Espectro de $s(t)$ — centrado em $\\pm f_c$')

    # linha 2: v(t) = s(t)*cos(...)
    axes[1, 0].plot(t_ms, v, 'C1', lw=0.8)
    axes[1, 0].set_xlim([0, t_show])
    axes[1, 0].set_ylabel('$v(t)$')
    axes[1, 0].set_title('Após multiplicação por $\\cos(2\\pi f_c t)$')
    axes[1, 1].plot(f_kHz, V, 'C1', lw=1.5)
    axes[1, 1].set_xlim([-12, 12])
    axes[1, 1].set_ylabel('$|V(f)|$')
    axes[1, 1].set_title('Espectro: componentes em $0$ e $\\pm 2f_c$')

    # linha 3: r(t) após LPF
    axes[2, 0].plot(t_ms, r, 'C2', lw=1.5, label='Recuperado')
    axes[2, 0].plot(t_ms, m/2, 'C3', lw=1.5, ls='--', alpha=0.7, label='$m(t)/2$ (referência)')
    axes[2, 0].set_xlim([2, t_show])  # skip transient
    axes[2, 0].set_xlabel('Tempo (ms)')
    axes[2, 0].set_ylabel('Amplitude')
    axes[2, 0].set_title('Após LPF — sinal recuperado $\\approx m(t)/2$')
    axes[2, 0].legend(fontsize=10)

    axes[2, 1].plot(f_kHz, R, 'C2', lw=1.5)
    axes[2, 1].set_xlim([-3, 3])
    axes[2, 1].set_xlabel('Frequência (kHz)')
    axes[2, 1].set_ylabel('$|R(f)|$')
    axes[2, 1].set_title('Espectro recuperado — banda básica')

    fig.tight_layout()
    save(fig, 'downconversion_basica')


# ====================================================================
# 9. Transformada de Hilbert
# ====================================================================
def fig_hilbert_transform():
    fs = 48000
    dur = 0.01
    t = np.arange(0, dur, 1/fs)
    N = len(t)
    f0 = 500

    x = np.cos(2*np.pi*f0*t)
    z = sig.hilbert(x)         # sinal analítico
    x_hat = np.imag(z)         # transformada de Hilbert

    freqs = np.fft.fftshift(np.fft.fftfreq(N, 1/fs))
    f_kHz = freqs * 1e-3
    def spec(s):
        return np.fft.fftshift(np.fft.fft(s)) / N

    X = spec(x)
    Xh = spec(x_hat)
    Z = spec(z)

    fig, axes = plt.subplots(4, 2, figsize=(13, 8))
    t_ms = t * 1e3

    # linha 1: x(t) e X(f)
    axes[0, 0].plot(t_ms, x, 'C0', lw=2)
    axes[0, 0].set_ylabel('$x(t)$')
    axes[0, 0].set_title('Sinal original $x(t) = \\cos(2\\pi 500t)$')
    axes[0, 1].plot(f_kHz, np.abs(X), 'C0', lw=1.5)
    axes[0, 1].set_xlim([-2, 2])
    axes[0, 1].set_ylabel('$|X(f)|$')
    axes[0, 1].set_title('Espectro $X(f)$')

    # linha 2: x̂(t) e seu espectro
    axes[1, 0].plot(t_ms, x_hat, 'C1', lw=2)
    axes[1, 0].set_ylabel('$\\hat{x}(t)$')
    axes[1, 0].set_title('Transformada de Hilbert $\\hat{x}(t) = \\sin(2\\pi 500t)$')
    axes[1, 1].plot(f_kHz, np.abs(Xh), 'C1', lw=1.5)
    axes[1, 1].set_xlim([-2, 2])
    axes[1, 1].set_ylabel('$|\\hat{X}(f)|$')
    axes[1, 1].set_title('Espectro $\\hat{X}(f) = -j\\,\\mathrm{sgn}(f)\\,X(f)$')

    # linha 3: sinal analítico |z(t)|, Re, Im
    axes[2, 0].plot(t_ms, np.real(z), 'C0', lw=1.5, alpha=0.7, label='Re $z(t)$')
    axes[2, 0].plot(t_ms, np.imag(z), 'C1', lw=1.5, alpha=0.7, label='Im $z(t)$')
    axes[2, 0].plot(t_ms, np.abs(z), 'C3', lw=2, ls='--', label='$|z(t)|$ (envelope)')
    axes[2, 0].set_ylabel('Amplitude')
    axes[2, 0].set_title('Sinal analítico $z(t) = x(t) + j\\hat{x}(t)$')
    axes[2, 0].legend(fontsize=9)

    axes[2, 1].plot(f_kHz, np.abs(Z), 'C2', lw=1.5)
    axes[2, 1].set_xlim([-2, 2])
    axes[2, 1].set_ylabel('$|Z(f)|$')
    axes[2, 1].set_title('Espectro $Z(f)$ — unilateral (freq. positivas)')

    # linha 4: fase do sinal analítico
    phase = np.unwrap(np.angle(z))
    axes[3, 0].plot(t_ms, phase, 'C4', lw=2)
    axes[3, 0].set_xlabel('Tempo (ms)')
    axes[3, 0].set_ylabel('Fase (rad)')
    axes[3, 0].set_title('Fase instantânea $\\phi(t)$ do sinal analítico')

    axes[3, 1].plot(f_kHz, np.angle(Z), 'C4', lw=1.5)
    axes[3, 1].set_xlim([-2, 2])
    axes[3, 1].set_xlabel('Frequência (kHz)')
    axes[3, 1].set_ylabel('Fase (rad)')
    axes[3, 1].set_title('Fase de $Z(f)$')

    fig.tight_layout()
    save(fig, 'hilbert_transform')


# ====================================================================
# 10. Envelope AM via Hilbert
# ====================================================================
def fig_envelope_am():
    fs = 48000
    dur = 0.02
    t = np.arange(0, dur, 1/fs)

    m_idx = 0.8     # índice de modulação
    fm = 200        # Hz
    fc = 3000       # Hz

    mod = 1 + m_idx * np.cos(2*np.pi*fm*t)   # envelope teórico
    s = mod * np.cos(2*np.pi*fc*t)            # sinal AM

    # envelope via Hilbert
    z = sig.hilbert(s)
    envelope = np.abs(z)

    fig, axes = plt.subplots(2, 1, figsize=(12, 6), sharex=True)
    t_ms = t * 1e3

    ax = axes[0]
    ax.plot(t_ms, s, 'C0', lw=0.8, label='$s(t)$ — sinal AM')
    ax.plot(t_ms, envelope, 'C3', lw=2, label='Envelope $|z(t)|$ (Hilbert)')
    ax.plot(t_ms, -envelope, 'C3', lw=2, alpha=0.5)
    ax.set_ylabel('Amplitude')
    ax.set_title(f'AM: $s(t) = [1 + {m_idx}\\cos(2\\pi {fm}t)]\\cos(2\\pi {fc}t)$')
    ax.legend(fontsize=10)

    ax = axes[1]
    ax.plot(t_ms, mod, 'C1', lw=2, label='Envelope original $1 + m\\cos(2\\pi f_m t)$')
    ax.plot(t_ms, envelope, 'C3', lw=2, ls='--', label='Envelope extraído $|z(t)|$')
    ax.set_xlabel('Tempo (ms)')
    ax.set_ylabel('Amplitude')
    ax.set_title('Comparação: envelope original vs. extraído via transformada de Hilbert')
    ax.legend(fontsize=10)

    fig.tight_layout()
    save(fig, 'envelope_am')


# ====================================================================
# main
# ====================================================================
if __name__ == '__main__':
    print('Gerando figuras parte 2 (cap. 3)…')
    fig_parseval_energia_demo()
    fig_densidade_espectral_energia()
    fig_psd_senoide()
    fig_ruido_branco_filtrado()
    fig_dft_janelamento()
    fig_aliasing_demo()
    fig_banda_basica_vs_passante()
    fig_downconversion_basica()
    fig_hilbert_transform()
    fig_envelope_am()
    print('Concluído!')
