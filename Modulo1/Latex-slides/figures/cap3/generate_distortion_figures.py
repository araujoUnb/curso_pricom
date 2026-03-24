#!/usr/bin/env python3
"""
Gera figuras de distorção de amplitude, fase e atraso de grupo.
Simula os exemplos do GNU Radio para inclusão nos slides.
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
    'xtick.labelsize': 12,
    'ytick.labelsize': 12,
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
# 1. Distorção de Amplitude
# ====================================================================
def fig_distorcao_amplitude():
    """
    Soma de dois cossenos (500 Hz + 4000 Hz) passa por LPF (fc=2000 Hz).
    A componente de 4 kHz é atenuada.
    """
    print('Gerando: distorcao_amplitude')

    fs = 48000
    T = 0.01  # 10 ms de sinal
    t = np.arange(0, T, 1/fs)
    f1, f2 = 500, 4000

    # Sinal original
    x = np.cos(2*np.pi*f1*t) + np.cos(2*np.pi*f2*t)

    # Filtro passa-baixa (Butterworth ordem 5, fc=2000 Hz)
    sos = sig.butter(5, 2000, btype='low', fs=fs, output='sos')
    y = sig.sosfilt(sos, x)

    # Espectros
    N = len(t)
    freqs = np.fft.rfftfreq(N, 1/fs)
    X_mag = 2*np.abs(np.fft.rfft(x))/N
    Y_mag = 2*np.abs(np.fft.rfft(y))/N

    fig, axes = plt.subplots(2, 1, figsize=(10, 6))

    # Tempo
    t_ms = t * 1000
    axes[0].plot(t_ms, x, 'b-', linewidth=1.5, label='Original', alpha=0.8)
    axes[0].plot(t_ms, y, 'r-', linewidth=1.5, label='Após canal (LPF)', alpha=0.8)
    axes[0].set_xlabel('Tempo (ms)')
    axes[0].set_ylabel('Amplitude')
    axes[0].set_title('Distorção de Amplitude — Domínio do Tempo')
    axes[0].legend(loc='upper right')
    axes[0].set_xlim([0, 5])

    # Frequência
    axes[1].stem(freqs[freqs <= 6000]/1000, X_mag[freqs <= 6000],
                 linefmt='b-', markerfmt='bo', basefmt='b-',
                 label='Original')
    axes[1].stem(freqs[freqs <= 6000]/1000, Y_mag[freqs <= 6000],
                 linefmt='r-', markerfmt='r^', basefmt='r-',
                 label='Após canal (LPF)')
    axes[1].set_xlabel('Frequência (kHz)')
    axes[1].set_ylabel('|X(f)|')
    axes[1].set_title('Distorção de Amplitude — Domínio da Frequência')
    axes[1].legend(loc='upper right')
    axes[1].set_xlim([-0.2, 6])
    axes[1].axvline(x=2, color='gray', linestyle=':', alpha=0.7, label='fc = 2 kHz')

    fig.tight_layout()
    save(fig, 'gnuradio_distorcao_amplitude')


# ====================================================================
# 2. Distorção de Fase
# ====================================================================
def fig_distorcao_fase():
    """
    Demonstra distorção de fase: mesmas amplitudes, fases diferentes.
    Usa construção direta: o sinal distorcido tem as mesmas componentes
    mas com fases não-proporcionais a w (fase não-linear).
    """
    print('Gerando: distorcao_fase')

    fs = 48000
    T = 0.006
    t = np.arange(0, T, 1/fs)
    f1, f2, f3 = 500, 1500, 2500

    # Sinal original: 3 cossenos em fase
    x = (np.cos(2*np.pi*f1*t)
         + np.cos(2*np.pi*f2*t)
         + np.cos(2*np.pi*f3*t))

    # Sinal com distorção de fase: mesmas amplitudes,
    # mas fases não-lineares (não proporcionais a w)
    # Fase linear seria phi(w) = -w*td => phi1=-w1*td, phi2=-w2*td, ...
    # Fase distorcida: cada componente com fase arbitrária
    y = (np.cos(2*np.pi*f1*t + 0.0)       # sem atraso
         + np.cos(2*np.pi*f2*t + np.pi/2)  # +90 graus
         + np.cos(2*np.pi*f3*t + np.pi))    # +180 graus

    # Espectros
    N = len(t)
    freqs = np.fft.rfftfreq(N, 1/fs)
    X_mag = 2*np.abs(np.fft.rfft(x))/N
    Y_mag = 2*np.abs(np.fft.rfft(y))/N

    fig, axes = plt.subplots(2, 1, figsize=(10, 6))

    # Tempo
    t_ms = t * 1000
    axes[0].plot(t_ms, x, 'b-', linewidth=2,
                 label='Original (fases iguais)', alpha=0.9)
    axes[0].plot(t_ms, y, 'r--', linewidth=2,
                 label=r'Distorcido ($\phi$ não-linear)',
                 alpha=0.9)
    axes[0].set_xlabel('Tempo (ms)')
    axes[0].set_ylabel('Amplitude')
    axes[0].set_title(
        'Distorção de Fase — Mesmas amplitudes, '
        'fases diferentes → forma de onda alterada')
    axes[0].legend(loc='upper right')
    axes[0].set_xlim([0, T*1000])

    # Frequência
    mask = freqs <= 4000
    axes[1].stem(freqs[mask]/1000, X_mag[mask],
                 linefmt='b-', markerfmt='bo', basefmt='b-',
                 label='Original')
    axes[1].stem(freqs[mask]/1000, Y_mag[mask],
                 linefmt='r-', markerfmt='r^', basefmt='r-',
                 label='Distorcido')
    axes[1].set_xlabel('Frequência (kHz)')
    axes[1].set_ylabel('|X(f)|')
    axes[1].set_title(
        'Espectro de Magnitude — IDÊNTICO! '
        '(distorção é apenas na fase)')
    axes[1].legend(loc='upper right')
    axes[1].set_xlim([-0.2, 4])

    fig.tight_layout()
    save(fig, 'gnuradio_distorcao_fase')


# ====================================================================
# 3. Atraso de Grupo
# ====================================================================
def fig_atraso_grupo():
    """
    Demonstra atraso de grupo usando filtro Chebyshev tipo I de ordem alta.
    O Chebyshev tem atraso de grupo fortemente variável perto de fc,
    produzindo efeito bem visível.
    """
    print('Gerando: atraso_grupo')

    fs = 48000
    T = 0.015
    t = np.arange(0, T, 1/fs)
    f1, f2, f3 = 500, 2000, 3800
    fc = 4000  # freq de corte do Chebyshev

    # Sinal original: 3 cossenos
    x = (np.cos(2*np.pi*f1*t)
         + np.cos(2*np.pi*f2*t)
         + np.cos(2*np.pi*f3*t))

    # Filtro Chebyshev tipo I, ordem 8 (atraso de grupo muito variável)
    sos = sig.cheby1(8, 1, fc, btype='low', fs=fs, output='sos')
    y = sig.sosfilt(sos, x)

    # Atraso de grupo do filtro
    b, a_coef = sig.cheby1(8, 1, fc, btype='low', fs=fs)
    w_gd, gd = sig.group_delay((b, a_coef), fs=fs)
    gd_ms = gd / fs * 1000  # converter amostras -> ms

    fig, axes = plt.subplots(2, 1, figsize=(10, 6))

    # Tempo
    t_ms = t * 1000
    axes[0].plot(t_ms, x, 'b-', linewidth=1.5,
                 label='Original', alpha=0.8)
    axes[0].plot(t_ms, y, 'r-', linewidth=1.5,
                 label='Após Chebyshev (τg variável)', alpha=0.8)
    axes[0].set_xlabel('Tempo (ms)')
    axes[0].set_ylabel('Amplitude')
    axes[0].set_title('Efeito do Atraso de Grupo — Domínio do Tempo')
    axes[0].legend(loc='upper right')
    axes[0].set_xlim([1, 10])

    # Atraso de grupo
    mask_gd = w_gd <= 6000
    axes[1].plot(w_gd[mask_gd]/1000, gd_ms[mask_gd],
                 'g-', linewidth=2)
    axes[1].set_xlabel('Frequência (kHz)')
    axes[1].set_ylabel(r'$\tau_g$ (ms)')
    axes[1].set_title(
        r'Atraso de Grupo $\tau_g(\omega) = -d\phi/d\omega$'
        ' — Não constante!')
    axes[1].set_xlim([0, 6])

    # Marcar frequências dos cossenos
    for fi, lbl in [(f1, f'{f1} Hz'), (f2, f'{f2} Hz'),
                    (f3, f'{f3} Hz')]:
        idx = np.argmin(np.abs(w_gd - fi))
        axes[1].axvline(x=fi/1000, color='gray',
                        linestyle=':', alpha=0.5)
        axes[1].plot(fi/1000, gd_ms[idx], 'ro', markersize=8)
        axes[1].annotate(
            lbl, (fi/1000, gd_ms[idx]),
            textcoords="offset points", xytext=(10, 5),
            fontsize=10, color='red')

    # Linha pontilhada mostrando τg constante ideal
    axes[1].axhline(y=gd_ms[np.argmin(np.abs(w_gd - f1))],
                    color='blue', linestyle='--', alpha=0.4,
                    label=r'$\tau_g$ constante (ideal)')
    axes[1].legend(fontsize=10)

    fig.tight_layout()
    save(fig, 'gnuradio_atraso_grupo')


# ====================================================================
# 4. Comparação: Canal Ideal vs Distorcido
# ====================================================================
def fig_canal_ideal_vs_distorcido():
    """
    Visão geral: sinal original, canal ideal (K*delay) e canal distorcido.
    """
    print('Gerando: canal_ideal_vs_distorcido')

    fs = 48000
    T = 0.01
    t = np.arange(0, T, 1/fs)

    # Sinal: soma de 3 cossenos
    x = np.cos(2*np.pi*500*t) + 0.7*np.cos(2*np.pi*2000*t) + 0.5*np.cos(2*np.pi*4000*t)

    # Canal ideal: H(w) = K * e^(-jw*td)  => ganho + atraso puro
    K = 0.8
    delay_samples = 20
    y_ideal = np.zeros_like(x)
    y_ideal[delay_samples:] = K * x[:-delay_samples]

    # Canal distorcido: LPF (atenua 4 kHz)
    sos = sig.butter(4, 2500, btype='low', fs=fs, output='sos')
    y_dist = sig.sosfilt(sos, x)

    # Espectros
    N = len(t)
    freqs = np.fft.rfftfreq(N, 1/fs)
    X_mag = 2*np.abs(np.fft.rfft(x))/N
    Yi_mag = 2*np.abs(np.fft.rfft(y_ideal))/N
    Yd_mag = 2*np.abs(np.fft.rfft(y_dist))/N
    fmask = freqs <= 7000

    # Resposta em frequência do filtro LPF
    w_h, h_resp = sig.sosfreqz(sos, worN=2048, fs=fs)

    fig, axes = plt.subplots(3, 3, figsize=(14, 9))
    t_ms = t * 1000
    xlim = [0.5, 5]

    # --- Linha 1: domínio do tempo ---
    axes[0, 0].plot(t_ms, x, 'b-', linewidth=1.5)
    axes[0, 0].set_title('Original')
    axes[0, 0].set_ylabel('Amplitude')
    axes[0, 0].set_xlim(xlim)

    axes[0, 1].plot(t_ms, x, 'b-', linewidth=1, alpha=0.3)
    axes[0, 1].plot(t_ms, y_ideal, 'g-', linewidth=1.5,
                    label=f'K={K}, atraso={delay_samples} amostras')
    axes[0, 1].set_title(r'Canal Ideal: $H = Ke^{-j\omega t_d}$')
    axes[0, 1].legend(loc='upper right', fontsize=9)
    axes[0, 1].set_xlim(xlim)

    axes[0, 2].plot(t_ms, x, 'b-', linewidth=1, alpha=0.3)
    axes[0, 2].plot(t_ms, y_dist, 'r-', linewidth=1.5,
                    label='Canal distorcido (LPF)')
    axes[0, 2].set_title(r'Canal Distorcido: $|H(\omega)| \neq K$')
    axes[0, 2].legend(loc='upper right', fontsize=9)
    axes[0, 2].set_xlim(xlim)

    # --- Linha 2: espectros ---
    axes[1, 0].stem(freqs[fmask]/1000, X_mag[fmask],
                    linefmt='b-', markerfmt='bo', basefmt='b-')
    axes[1, 0].set_title('Espectro Original')
    axes[1, 0].set_ylabel('|X(f)|')
    axes[1, 0].set_xlim([-0.2, 7])

    axes[1, 1].stem(freqs[fmask]/1000, Yi_mag[fmask],
                    linefmt='g-', markerfmt='go', basefmt='g-')
    axes[1, 1].set_title('Espectro — Canal Ideal')
    axes[1, 1].set_xlim([-0.2, 7])

    axes[1, 2].stem(freqs[fmask]/1000, Yd_mag[fmask],
                    linefmt='r-', markerfmt='ro', basefmt='r-')
    axes[1, 2].set_title('Espectro — Canal Distorcido')
    axes[1, 2].set_xlim([-0.2, 7])

    ymax_spec = max(X_mag[fmask].max(), Yi_mag[fmask].max(),
                    Yd_mag[fmask].max()) * 1.15
    for ax in axes[1, :]:
        ax.set_ylim([0, ymax_spec])

    # --- Linha 3: resposta do filtro ---
    # Canal ideal: |H| = K (constante)
    axes[2, 0].set_visible(False)

    axes[2, 1].axhline(y=K, color='g', linewidth=2,
                       label=f'|H(f)| = {K} (constante)')
    axes[2, 1].set_title(r'$|H(\omega)|$ — Canal Ideal')
    axes[2, 1].set_ylabel('|H(f)|')
    axes[2, 1].set_xlabel('Frequência (kHz)')
    axes[2, 1].set_xlim([-0.2, 7])
    axes[2, 1].set_ylim([0, 1.2])
    axes[2, 1].legend(fontsize=9)

    axes[2, 2].plot(w_h/1000, np.abs(h_resp), 'r-', linewidth=2,
                    label='|H(f)| do LPF')
    axes[2, 2].axvline(x=2.5, color='gray', linestyle=':',
                       alpha=0.7, label='fc = 2.5 kHz')
    axes[2, 2].set_title(r'$|H(\omega)|$ — Canal Distorcido')
    axes[2, 2].set_ylabel('|H(f)|')
    axes[2, 2].set_xlabel('Frequência (kHz)')
    axes[2, 2].set_xlim([-0.2, 7])
    axes[2, 2].set_ylim([0, 1.2])
    axes[2, 2].legend(fontsize=9)

    fig.tight_layout()
    save(fig, 'gnuradio_canal_ideal_vs_distorcido')


# ====================================================================
if __name__ == '__main__':
    print('=== Gerando figuras de distorção ===')
    fig_distorcao_amplitude()
    fig_distorcao_fase()
    fig_atraso_grupo()
    fig_canal_ideal_vs_distorcido()
    print('=== Concluído! ===')
