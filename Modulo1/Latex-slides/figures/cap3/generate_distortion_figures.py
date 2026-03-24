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
    Demonstra distorção de fase com 5 componentes.
    Canal ideal: fase linear phi(f) = -2*pi*f*td  (atraso puro)
    Canal distorcido: fase quadrática phi(f) = -beta*f^2  (dispersão)
    O aluno vê claramente: reta (ideal) vs parábola (distorcido).
    """
    print('Gerando: distorcao_fase')

    fs = 48000
    T = 0.006
    t = np.arange(0, T, 1/fs)
    freqs_sig = np.array([500, 1000, 1500, 2000, 2500])  # 5 componentes

    # Fase linear (canal ideal): phi = -2*pi*f*td
    td = 0.3e-3  # atraso de 0.3 ms
    phi_linear = -2 * np.pi * freqs_sig * td

    # Fase quadrática (dispersão): phi = -beta * f^2
    # beta escolhido para que a diferença seja bem visível
    beta = 0.4e-6
    phi_quad = -beta * (2 * np.pi * freqs_sig)**2

    # Sinal original (fase zero)
    x = np.zeros_like(t)
    for f in freqs_sig:
        x += np.cos(2 * np.pi * f * t)

    # Sinal com fase linear (canal ideal — apenas atraso)
    x_lin = np.zeros_like(t)
    for f, phi in zip(freqs_sig, phi_linear):
        x_lin += np.cos(2 * np.pi * f * t + phi)

    # Sinal com fase quadrática (canal dispersivo — distorção)
    y = np.zeros_like(t)
    for f, phi in zip(freqs_sig, phi_quad):
        y += np.cos(2 * np.pi * f * t + phi)

    fig, axes = plt.subplots(2, 1, figsize=(10, 6))

    # Tempo
    t_ms = t * 1000
    axes[0].plot(t_ms, x, 'b-', linewidth=2,
                 label='Original', alpha=0.9)
    axes[0].plot(t_ms, x_lin, 'g--', linewidth=2,
                 label=r'Canal ideal ($\phi$ linear = atraso)',
                 alpha=0.8)
    axes[0].plot(t_ms, y, 'r--', linewidth=2,
                 label=r'Canal dispersivo ($\phi$ quadrática)',
                 alpha=0.9)
    axes[0].set_xlabel('Tempo (ms)')
    axes[0].set_ylabel('Amplitude')
    axes[0].set_title(
        'Distorção de Fase — Mesmas amplitudes, '
        'fases diferentes → forma de onda alterada')
    axes[0].legend(loc='upper right', fontsize=10)
    axes[0].set_xlim([0, T*1000])

    # Espectro de magnitude (todos idênticos)
    N = len(t)
    freqs = np.fft.rfftfreq(N, 1/fs)
    X_mag = 2*np.abs(np.fft.rfft(x))/N
    Y_mag = 2*np.abs(np.fft.rfft(y))/N
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

    # --- Figura separada: espectro de fase ---
    fig2, axes2 = plt.subplots(2, 1, figsize=(10, 6))

    # Fase: reta vs parábola (plotar apenas nas frequências do sinal)
    axes2[0].plot(freqs_sig/1000, phi_linear/np.pi, 'go-',
                  linewidth=2, markersize=10,
                  label=r'Canal ideal: $\phi = -\omega t_d$ (reta)')
    axes2[0].plot(freqs_sig/1000, phi_quad/np.pi, 'r^-',
                  linewidth=2, markersize=10,
                  label=r'Canal dispersivo: $\phi = -\beta\omega^2$ (parábola)')
    axes2[0].set_xlabel('Frequência (kHz)')
    axes2[0].set_ylabel(r'$\phi(\omega)$ / $\pi$ rad')
    axes2[0].set_title(
        r'Espectro de Fase — Linear (reta) vs Não-linear (curva)')
    axes2[0].legend(loc='lower left', fontsize=10)
    axes2[0].set_xlim([0, 3])
    axes2[0].axhline(y=0, color='gray', linewidth=0.5)

    # Magnitude (referência — todos iguais)
    axes2[1].stem(freqs[mask]/1000, X_mag[mask],
                  linefmt='b-', markerfmt='bo', basefmt='b-',
                  label='Idêntico para ambos os canais')
    axes2[1].set_xlabel('Frequência (kHz)')
    axes2[1].set_ylabel('|X(f)|')
    axes2[1].set_title(
        'Espectro de Magnitude — IDÊNTICO')
    axes2[1].legend(loc='upper right')
    axes2[1].set_xlim([-0.2, 4])

    fig2.tight_layout()
    save(fig2, 'gnuradio_distorcao_fase_espectro')


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
# 5. Largura de Banda (3 dB, Absoluta e de Ruído)
# ====================================================================
def fig_largura_banda():
    """
    Ilustra as três definições de largura de banda para um filtro
    Butterworth passa-baixa de ordem 4: B_3dB, B_abs e B_n.
    """
    print('Gerando: largura_banda_sistemas')

    fs = 48000
    fc = 2000  # frequência de corte

    # Filtro Butterworth ordem 4
    sos = sig.butter(4, fc, btype='low', fs=fs, output='sos')
    freqs_hz = np.linspace(0, fs/2, 10000)
    w, H = sig.sosfreqz(sos, worN=freqs_hz, fs=fs)
    H_mag = np.abs(H)
    H_pow = H_mag**2

    freqs_khz = freqs_hz / 1000

    # --- Frequência de -3 dB ---
    threshold_3dB = 1.0 / np.sqrt(2)
    idx_3dB = np.argmin(np.abs(H_mag - threshold_3dB))
    f_3dB_khz = freqs_khz[idx_3dB]

    # --- Largura de banda absoluta (|H| cai abaixo de 0.01) ---
    above_thresh = np.where(H_mag >= 0.01)[0]
    idx_abs = above_thresh[-1]
    f_abs_khz = freqs_khz[idx_abs]

    # --- Largura de banda de ruído ---
    # B_n = integral |H(f)|^2 df  /  |H(f_max)|^2
    df = freqs_hz[1] - freqs_hz[0]
    integral_pow = np.trapezoid(H_pow, dx=df)
    H_max_pow = H_pow[0]  # máximo em f=0
    B_n_hz = integral_pow / H_max_pow
    B_n_khz = B_n_hz / 1000

    # ============================================================
    # Figura 1: Largura de Banda de 3 dB e Absoluta
    # ============================================================
    fig1, ax1 = plt.subplots(1, 1, figsize=(8, 5))
    ax1.plot(freqs_khz, H_mag, 'b-', linewidth=2, label='|H(f)|')

    # Região B_3dB (sombreamento azul claro)
    mask_3dB = freqs_khz <= f_3dB_khz
    ax1.fill_between(freqs_khz[mask_3dB], 0, H_mag[mask_3dB],
                     color='tab:blue', alpha=0.15,
                     label=f'$B_{{3dB}}$ = {f_3dB_khz:.1f} kHz')

    # Região B_abs (sombreamento vermelho claro)
    mask_abs = freqs_khz <= f_abs_khz
    ax1.fill_between(freqs_khz[mask_abs], 0, H_mag[mask_abs],
                     color='tab:red', alpha=0.07,
                     label=f'$B_{{abs}}$ = {f_abs_khz:.1f} kHz')

    # Linha horizontal em 1/sqrt(2)
    ax1.axhline(y=threshold_3dB, color='gray', linestyle='--',
                linewidth=1, alpha=0.8)
    ax1.annotate(r'$1/\sqrt{2}$ ($-3$ dB)', xy=(5.5, threshold_3dB),
                 fontsize=10, color='gray', va='bottom')

    # Linha vertical em f_3dB
    ax1.axvline(x=f_3dB_khz, color='tab:blue', linestyle='--',
                linewidth=1, alpha=0.7)
    ax1.annotate(f'$B_{{3dB}}$', xy=(f_3dB_khz, 0.85),
                 fontsize=11, color='tab:blue',
                 textcoords='offset points', xytext=(5, 0))

    # Linha vertical em f_abs
    ax1.axvline(x=f_abs_khz, color='tab:red', linestyle='--',
                linewidth=1, alpha=0.7)
    ax1.annotate(f'$B_{{abs}}$', xy=(f_abs_khz, 0.15),
                 fontsize=11, color='tab:red',
                 textcoords='offset points', xytext=(5, 0))

    ax1.set_xlabel('Frequência (kHz)')
    ax1.set_ylabel('|H(f)|')
    ax1.set_title('Largura de Banda de 3 dB e Absoluta')
    ax1.set_xlim([0, 8])
    ax1.set_ylim([0, 1.1])
    ax1.legend(loc='upper right', fontsize=10)

    fig1.tight_layout()
    save(fig1, 'largura_banda_3dB_abs')

    # ============================================================
    # Figura 2: Largura de Banda de Ruído
    # ============================================================
    fig2, ax2 = plt.subplots(1, 1, figsize=(8, 5))
    ax2.plot(freqs_khz, H_pow, 'b-', linewidth=2, label='$|H(f)|^2$')

    # Sombreamento da área sob |H(f)|^2
    ax2.fill_between(freqs_khz, 0, H_pow,
                     color='tab:green', alpha=0.2,
                     label=r'$\int |H(f)|^2\, df$')

    # Retângulo equivalente: altura = 1, largura = B_n
    rect_f = np.array([0, B_n_khz, B_n_khz, 0, 0])
    rect_h = np.array([0, 0, H_max_pow, H_max_pow, 0])
    ax2.plot(rect_f, rect_h, 'r--', linewidth=2,
             label=f'$B_n$ = {B_n_khz:.2f} kHz')

    # Anotação do retângulo
    ax2.annotate(f'$B_n$', xy=(B_n_khz / 2, H_max_pow),
                 fontsize=12, color='red', ha='center', va='bottom',
                 fontweight='bold')

    ax2.set_xlabel('Frequência (kHz)')
    ax2.set_ylabel('$|H(f)|^2$')
    ax2.set_title('Largura de Banda de Ruído')
    ax2.set_xlim([0, 8])
    ax2.set_ylim([0, 1.15])
    ax2.legend(loc='upper right', fontsize=10)

    fig2.tight_layout()
    save(fig2, 'largura_banda_ruido')


# ====================================================================
# 6. Equalização de Canal de Áudio
# ====================================================================
def fig_equalizacao_audio():
    """
    Ilustra equalização de canal de áudio em 3 figuras:
    1) Sinal original + resposta do cabo (|Hc| e sinal após cabo)
    2) Resposta do equalizador + resposta combinada Heq*Hc
    3) Comparação dos sinais no tempo: original, após cabo, equalizado
    """
    print('Gerando: equalizacao_audio')

    fs = 96000
    T = 0.005   # 5 ms
    t = np.arange(0, T, 1/fs)
    fc = 5000    # freq de corte do cabo (5 kHz — cabo longo/ruim)
    wc = 2 * np.pi * fc

    # --- Sinal original: soma de tons (simula áudio com graves e agudos) ---
    freqs_sig = [300, 1000, 3000, 8000, 15000]
    x = np.zeros_like(t)
    for f in freqs_sig:
        x += np.cos(2 * np.pi * f * t)

    # --- Canal (cabo): H_c(w) = 1/(1 + jw/wc) ---
    # Implementar como filtro RC: polo em -wc
    # H(s) = wc/(s + wc), bilinear transform
    b_c, a_c = sig.bilinear([wc], [1, wc], fs=fs)
    y_cabo = sig.lfilter(b_c, a_c, x)

    # --- Equalizador: H_eq(w) = 1 + jw/wc (inverso do cabo) ---
    # Na prática, limitar o ganho em alta frequência (para estabilidade)
    # Usar: H_eq(s) = (s + wc)/wc com polo em alta freq para causalidade
    f_polo = 40000  # polo do equalizador bem acima da faixa de áudio
    wp = 2 * np.pi * f_polo
    b_eq, a_eq = sig.bilinear([1, wc], [1, wp], fs=fs)
    # Normalizar ganho em DC para 1
    dc_gain = np.sum(b_eq) / np.sum(a_eq)
    b_eq = b_eq / dc_gain

    y_eq = sig.lfilter(b_eq, a_eq, y_cabo)

    # --- Respostas em frequência ---
    freqs_hz = np.linspace(1, fs/2, 5000)
    w_rad = 2 * np.pi * freqs_hz

    # Canal analítico
    Hc = 1.0 / (1 + 1j * w_rad / wc)
    Hc_mag = np.abs(Hc)

    # Equalizador analítico (com polo de estabilidade)
    Heq = (1 + 1j * w_rad / wc) / (1 + 1j * w_rad / (2*np.pi*f_polo))
    Heq_mag = np.abs(Heq)

    # Combinação
    Htotal_mag = Hc_mag * Heq_mag

    freqs_khz = freqs_hz / 1000

    # --- Espectros dos sinais ---
    N = len(t)
    fft_freqs = np.fft.rfftfreq(N, 1/fs)
    X_mag = 2 * np.abs(np.fft.rfft(x)) / N
    Yc_mag = 2 * np.abs(np.fft.rfft(y_cabo)) / N
    Yeq_mag = 2 * np.abs(np.fft.rfft(y_eq)) / N
    fft_khz = fft_freqs / 1000

    # =================================================================
    # Figura 1: Sinal original + Resposta do cabo + Sinal após cabo
    # =================================================================
    fig1, axes1 = plt.subplots(2, 1, figsize=(10, 6))

    # |H_c(f)|
    axes1[0].plot(freqs_khz, Hc_mag, 'r-', linewidth=2,
                  label=r'$|H_c(f)| = \frac{1}{\sqrt{1+(f/f_c)^2}}$')
    axes1[0].axvline(x=fc/1000, color='gray', linestyle=':', alpha=0.7,
                     label=f'$f_c$ = {fc//1000} kHz')
    axes1[0].axhline(y=1/np.sqrt(2), color='gray', linestyle='--',
                     alpha=0.5)
    axes1[0].annotate(r'$1/\sqrt{2}$ ($-3$ dB)', xy=(20, 1/np.sqrt(2)),
                      fontsize=10, color='gray', va='bottom')
    axes1[0].set_xlabel('Frequência (kHz)')
    axes1[0].set_ylabel('|H(f)|')
    axes1[0].set_title(r'Resposta do Cabo: $H_c(\omega) = \frac{1}{1 + j\omega/\omega_c}$')
    axes1[0].set_xlim([0, 30])
    axes1[0].set_ylim([0, 1.1])
    axes1[0].legend(loc='upper right', fontsize=10)

    # Espectros: original vs após cabo
    mask_f = fft_khz <= 25
    axes1[1].stem(fft_khz[mask_f], X_mag[mask_f],
                  linefmt='b-', markerfmt='bo', basefmt='b-',
                  label='Original')
    axes1[1].stem(fft_khz[mask_f], Yc_mag[mask_f],
                  linefmt='r-', markerfmt='r^', basefmt='r-',
                  label='Após cabo (atenuado)')
    axes1[1].set_xlabel('Frequência (kHz)')
    axes1[1].set_ylabel('|X(f)|')
    axes1[1].set_title('Espectro do Sinal — Agudos Atenuados pelo Cabo')
    axes1[1].set_xlim([-0.5, 25])
    axes1[1].legend(loc='upper right', fontsize=10)

    fig1.tight_layout()
    save(fig1, 'equalizacao_audio_cabo')

    # =================================================================
    # Figura 2: Equalizador + Resposta combinada
    # =================================================================
    fig2, axes2 = plt.subplots(2, 1, figsize=(10, 6))

    # |H_eq(f)| e |H_c(f)|
    axes2[0].plot(freqs_khz, Hc_mag, 'r-', linewidth=2,
                  label=r'Cabo: $|H_c(f)|$')
    axes2[0].plot(freqs_khz, Heq_mag, 'g-', linewidth=2,
                  label=r'Equalizador: $|H_{eq}(f)|$')
    axes2[0].axvline(x=fc/1000, color='gray', linestyle=':', alpha=0.7)
    axes2[0].set_xlabel('Frequência (kHz)')
    axes2[0].set_ylabel('|H(f)|')
    axes2[0].set_title('Cabo Atenua Agudos — Equalizador Amplifica Agudos')
    axes2[0].set_xlim([0, 30])
    axes2[0].set_ylim([0, max(Heq_mag.max(), 2) * 1.1])
    axes2[0].legend(loc='right', fontsize=10)

    # |H_total(f)| = |H_c * H_eq|
    axes2[1].plot(freqs_khz, Htotal_mag, 'b-', linewidth=2,
                  label=r'$|H_c \cdot H_{eq}| \approx 1$')
    axes2[1].axhline(y=1, color='gray', linestyle='--', alpha=0.5,
                     label='Ideal: |H| = 1')
    axes2[1].set_xlabel('Frequência (kHz)')
    axes2[1].set_ylabel('|H(f)|')
    axes2[1].set_title(r'Resposta Combinada: $H_{eq} \cdot H_c \approx 1$ (canal restaurado)')
    axes2[1].set_xlim([0, 30])
    axes2[1].set_ylim([0, 1.3])
    axes2[1].legend(loc='upper right', fontsize=10)

    fig2.tight_layout()
    save(fig2, 'equalizacao_audio_equalizador')

    # =================================================================
    # Figura 3: Sinais no domínio do tempo
    # =================================================================
    fig3, axes3 = plt.subplots(3, 1, figsize=(10, 7))
    t_ms = t * 1000
    xlim_t = [0, 2]  # mostrar 2 ms

    axes3[0].plot(t_ms, x, 'b-', linewidth=1.5)
    axes3[0].set_ylabel('Amplitude')
    axes3[0].set_title('Sinal Original')
    axes3[0].set_xlim(xlim_t)

    axes3[1].plot(t_ms, x, 'b-', linewidth=1, alpha=0.3,
                  label='Original')
    axes3[1].plot(t_ms, y_cabo, 'r-', linewidth=1.5,
                  label='Após cabo (abafado)')
    axes3[1].set_ylabel('Amplitude')
    axes3[1].set_title('Após o Cabo — Agudos Perdidos')
    axes3[1].set_xlim(xlim_t)
    axes3[1].legend(loc='upper right', fontsize=10)

    axes3[2].plot(t_ms, x, 'b-', linewidth=1, alpha=0.3,
                  label='Original')
    axes3[2].plot(t_ms, y_eq, 'g-', linewidth=1.5,
                  label='Após equalização')
    axes3[2].set_xlabel('Tempo (ms)')
    axes3[2].set_ylabel('Amplitude')
    axes3[2].set_title('Após Equalização — Sinal Restaurado')
    axes3[2].set_xlim(xlim_t)
    axes3[2].legend(loc='upper right', fontsize=10)

    fig3.tight_layout()
    save(fig3, 'equalizacao_audio_tempo')


# ====================================================================
# 7. Mapa de Larguras de Banda de Tecnologias
# ====================================================================
def fig_bandas_tecnologias():
    """
    Mapa comparativo de larguras de banda de tecnologias comuns
    em escala logarítmica.
    """
    print('Gerando: bandas_tecnologias')

    # (nome, banda em Hz, cor)
    techs = [
        ('Telefone (PSTN)',            3.4e3,    'tab:brown'),
        ('Áudio (cabo P2/RCA)',        20e3,     'tab:orange'),
        ('Áudio HD (S/PDIF)',          192e3,    'goldenrod'),
        ('Ethernet Cat5e',             100e6,    'tab:cyan'),
        ('Ethernet Cat6a',             500e6,    'darkcyan'),
        ('USB 2.0',                    480e6,    'tab:green'),
        ('USB 3.0',                    5e9,      'limegreen'),
        ('HDMI 2.0',                   18e9,     'tab:blue'),
        ('USB4 / Thunderbolt 4',       40e9,     'tab:purple'),
        ('HDMI 2.1',                   48e9,     'royalblue'),
        ('Fibra Óptica (monomodo)',    10e12,    'tab:red'),
    ]

    names  = [t[0] for t in techs]
    bandas = [t[1] for t in techs]
    cores  = [t[2] for t in techs]

    fig, ax = plt.subplots(1, 1, figsize=(12, 8))

    y_pos = range(len(techs))
    bars = ax.barh(y_pos, bandas, color=cores, edgecolor='black',
                   linewidth=0.5, height=0.7)

    ax.set_xscale('log')
    ax.set_yticks(y_pos)
    ax.set_yticklabels(names, fontsize=14)
    ax.invert_yaxis()

    # Eixo X com labels legíveis (kHz, MHz, GHz, THz)
    import matplotlib.ticker as mticker
    tick_positions = [1e3, 1e4, 1e5, 1e6, 1e7, 1e8, 1e9, 1e10, 1e11, 1e12, 1e13]
    tick_labels = ['1 kHz', '10 kHz', '100 kHz',
                   '1 MHz', '10 MHz', '100 MHz',
                   '1 GHz', '10 GHz', '100 GHz',
                   '1 THz', '10 THz']
    ax.set_xticks(tick_positions)
    ax.set_xticklabels(tick_labels, fontsize=12, rotation=45, ha='right')
    ax.xaxis.set_minor_locator(mticker.NullLocator())

    ax.set_xlabel('Largura de Banda', fontsize=14)
    ax.set_title('Largura de Banda de Tecnologias Comuns', fontsize=15)
    ax.set_xlim([5e2, 5e13])

    # Anotações com valor legível
    sufixos = {1e3: 'kHz', 1e6: 'MHz', 1e9: 'GHz', 1e12: 'THz'}
    for bar, bw in zip(bars, bandas):
        for lim, suf in sorted(sufixos.items(), reverse=True):
            if bw >= lim:
                txt = f'{bw/lim:g} {suf}'
                break
        ax.text(bw * 1.5, bar.get_y() + bar.get_height()/2,
                txt, va='center', fontsize=11, fontweight='bold')

    # Linhas de referência verticais
    for freq in [1e3, 1e6, 1e9, 1e12]:
        ax.axvline(x=freq, color='gray', linestyle=':', alpha=0.3)

    fig.tight_layout()
    save(fig, 'bandas_tecnologias')


# ====================================================================
if __name__ == '__main__':
    print('=== Gerando figuras de distorção ===')
    fig_distorcao_amplitude()
    fig_distorcao_fase()
    fig_atraso_grupo()
    fig_canal_ideal_vs_distorcido()
    fig_largura_banda()
    fig_equalizacao_audio()
    fig_bandas_tecnologias()
    print('=== Concluído! ===')
