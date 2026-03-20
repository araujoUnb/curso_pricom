#!/usr/bin/env python3
"""
Gera figuras ilustrativas para o capítulo de Transformada de Fourier.
Curso de Princípios de Comunicação - UnB.
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch
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
# 1. Exponencial bilateral
# ====================================================================
def fig_bilateral_exponential():
    t = np.linspace(-5, 5, 1000)
    w = np.linspace(-10, 10, 1000)

    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    for a, color in [(1, 'C0'), (2, 'C1')]:
        ft = np.exp(-a * np.abs(t))
        Fw = 2 * a / (a**2 + w**2)
        axes[0].plot(t, ft, color=color, lw=2, label=f'$a={a}$')
        axes[1].plot(w, Fw, color=color, lw=2, label=f'$a={a}$')

    axes[0].set_xlabel('$t$')
    axes[0].set_ylabel('$f(t)$')
    axes[0].set_title(r'$f(t)=e^{-a|t|}$')
    axes[0].legend()

    axes[1].set_xlabel(r'$\omega$ (rad/s)')
    axes[1].set_ylabel(r'$F(\omega)$')
    axes[1].set_title(r'$F(\omega)=\frac{2a}{a^2+\omega^2}$')
    axes[1].legend()

    fig.tight_layout()
    save(fig, 'bilateral_exponential')


# ====================================================================
# 2. Delta e constante (dualidade)
# ====================================================================
def fig_delta_and_constant():
    fig, axes = plt.subplots(2, 2, figsize=(10, 6))
    t = np.linspace(-3, 3, 500)
    w = np.linspace(-3, 3, 500)

    # (a) delta(t) -> 1
    ax = axes[0, 0]
    ax.annotate('', xy=(0, 1), xytext=(0, 0),
                arrowprops=dict(arrowstyle='->', color='C0', lw=2))
    ax.plot(0, 1, 'o', color='C0', ms=8)
    ax.set_xlim(-3, 3); ax.set_ylim(-0.2, 1.3)
    ax.set_xlabel('$t$'); ax.set_ylabel('$f(t)$')
    ax.set_title(r'$f(t)=\delta(t)$')

    ax = axes[0, 1]
    ax.axhline(1, color='C0', lw=2)
    ax.set_xlim(-3, 3); ax.set_ylim(-0.2, 1.5)
    ax.set_xlabel(r'$\omega$'); ax.set_ylabel(r'$F(\omega)$')
    ax.set_title(r'$F(\omega)=1$')

    # (b) 1 -> 2 pi delta(w)
    ax = axes[1, 0]
    ax.axhline(1, color='C1', lw=2)
    ax.set_xlim(-3, 3); ax.set_ylim(-0.2, 1.5)
    ax.set_xlabel('$t$'); ax.set_ylabel('$f(t)$')
    ax.set_title('$f(t)=1$')

    ax = axes[1, 1]
    ax.annotate('', xy=(0, 1), xytext=(0, 0),
                arrowprops=dict(arrowstyle='->', color='C1', lw=2))
    ax.plot(0, 1, 'o', color='C1', ms=8)
    ax.set_xlim(-3, 3); ax.set_ylim(-0.2, 1.3)
    ax.set_xlabel(r'$\omega$'); ax.set_ylabel(r'$F(\omega)$')
    ax.set_title(r'$F(\omega)=2\pi\,\delta(\omega)$')

    fig.tight_layout()
    save(fig, 'delta_and_constant')


# ====================================================================
# 3. Dualidade rect / sinc
# ====================================================================
def fig_sinc_rect_duality():
    fig, axes = plt.subplots(2, 2, figsize=(10, 6))
    t = np.linspace(-3, 3, 1000)
    w = np.linspace(-30, 30, 2000)

    for row, tau, color in [(0, 1, 'C0'), (1, 0.5, 'C1')]:
        rect = np.where(np.abs(t) <= tau / 2, 1.0, 0.0)
        Fw = tau * np.sinc(w * tau / (2 * np.pi))  # np.sinc(x)=sin(pi x)/(pi x)

        axes[row, 0].plot(t, rect, color=color, lw=2)
        axes[row, 0].set_xlabel('$t$')
        axes[row, 0].set_ylabel('$f(t)$')
        axes[row, 0].set_title(rf'$\mathrm{{rect}}(t/\tau),\;\tau={tau}$')
        axes[row, 0].set_ylim(-0.2, 1.4)

        axes[row, 1].plot(w, Fw, color=color, lw=2)
        axes[row, 1].set_xlabel(r'$\omega$ (rad/s)')
        axes[row, 1].set_ylabel(r'$F(\omega)$')
        axes[row, 1].set_title(rf'$\tau\,\mathrm{{sinc}}(\omega\tau/2\pi),\;\tau={tau}$')

    fig.tight_layout()
    save(fig, 'sinc_rect_duality')


# ====================================================================
# 2b. Comparação Rect vs Tri (tempo e frequência)
# ====================================================================
def fig_rect_vs_tri():
    T = 1.0  # mesmo período de símbolo
    t = np.linspace(-2, 2, 2000)
    w = np.linspace(-40, 40, 4000)

    # Pulso retangular de duração T
    rect = np.where(np.abs(t) <= T / 2, 1.0, 0.0)
    F_rect = T * np.sinc(w * T / (2 * np.pi))

    # Pulso triangular de duração T (base T, τ = T/2)
    tau_tri = T / 2
    tri = np.where(np.abs(t) <= tau_tri, 1 - np.abs(t) / tau_tri, 0.0)
    F_tri = tau_tri * np.sinc(w * tau_tri / (2 * np.pi))**2

    fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))

    # --- Domínio do tempo ---
    axes[0].plot(t, rect, 'C0', lw=2.5, label=f'rect$(t/T)$, duração $T={T}$')
    axes[0].plot(t, tri, 'C1', lw=2.5, label=f'tri$(t/\\tau)$, duração $T={T}$')
    axes[0].set_xlabel('$t$')
    axes[0].set_ylabel('$f(t)$')
    axes[0].set_title('Domínio do Tempo')
    axes[0].legend(fontsize=10)
    axes[0].set_ylim(-0.15, 1.3)
    axes[0].set_xlim(-1.5, 1.5)

    # --- Domínio da frequência (dB) ---
    eps = 1e-15
    F_rect_dB = 20 * np.log10(np.abs(F_rect) + eps)
    F_tri_dB = 20 * np.log10(np.abs(F_tri) + eps)

    # Normalizar pelo máximo de cada um para comparar forma
    F_rect_dB -= F_rect_dB.max()
    F_tri_dB -= F_tri_dB.max()

    axes[1].plot(w, F_rect_dB, 'C0', lw=2, label=r'$|F_{\mathrm{rect}}(\omega)|$')
    axes[1].plot(w, F_tri_dB, 'C1', lw=2, label=r'$|F_{\mathrm{tri}}(\omega)|$')
    axes[1].set_xlabel(r'$\omega$ (rad/s)')
    axes[1].set_ylabel('Magnitude normalizada (dB)')
    axes[1].set_title('Espectro de Magnitude')
    axes[1].legend(fontsize=10)
    axes[1].set_ylim(-60, 5)
    axes[1].set_xlim(-40, 40)

    # Marcar primeiros nulos
    null_rect = 2 * np.pi / T
    null_tri = 2 * np.pi / tau_tri
    for ax_val, color, lbl in [(null_rect, 'C0', r'$2\pi/T$'),
                                (null_tri, 'C1', r'$2\pi/\tau$')]:
        axes[1].axvline(ax_val, color=color, ls='--', alpha=0.6, lw=1.2)
        axes[1].axvline(-ax_val, color=color, ls='--', alpha=0.6, lw=1.2)

    fig.suptitle(r'Comparação: Pulso Retangular vs. Triangular (mesma duração $T$)',
                 fontsize=13, y=1.02)
    fig.tight_layout()
    save(fig, 'rect_vs_tri_comparison')


# ====================================================================
# 4. Propriedade do deslocamento no tempo
# ====================================================================
def fig_time_shift_property():
    t = np.linspace(-5, 5, 1000)
    w = np.linspace(-10, 10, 1000)
    t0 = 2.0
    sigma = 0.8
    ft = np.exp(-t**2 / (2 * sigma**2))
    ft_shifted = np.exp(-(t - t0)**2 / (2 * sigma**2))
    Fw_mag = sigma * np.sqrt(2 * np.pi) * np.exp(-sigma**2 * w**2 / 2)
    phase_original = np.zeros_like(w)
    phase_shifted = -w * t0

    fig, axes = plt.subplots(3, 2, figsize=(10, 8))

    axes[0, 0].plot(t, ft, 'C0', lw=2)
    axes[0, 0].set_title('$f(t)$ — Gaussiana original')
    axes[0, 0].set_xlabel('$t$'); axes[0, 0].set_ylabel('$f(t)$')

    axes[0, 1].plot(w, Fw_mag, 'C0', lw=2)
    axes[0, 1].set_title(r'$|F(\omega)|$')
    axes[0, 1].set_xlabel(r'$\omega$'); axes[0, 1].set_ylabel(r'$|F(\omega)|$')

    axes[1, 0].plot(t, ft_shifted, 'C1', lw=2)
    axes[1, 0].set_title(rf'$f(t-t_0),\; t_0={t0}$')
    axes[1, 0].set_xlabel('$t$'); axes[1, 0].set_ylabel('$f(t-t_0)$')

    axes[1, 1].plot(w, Fw_mag, 'C1', lw=2)
    axes[1, 1].set_title(r'$|F(\omega)|$ inalterado')
    axes[1, 1].set_xlabel(r'$\omega$'); axes[1, 1].set_ylabel(r'$|F(\omega)|$')

    axes[2, 0].plot(w, phase_original, 'C0', lw=2, label='Original')
    axes[2, 0].plot(w, phase_shifted, 'C1', lw=2, label='Deslocado')
    axes[2, 0].set_title(r'Fase $\angle F(\omega)$')
    axes[2, 0].set_xlabel(r'$\omega$'); axes[2, 0].set_ylabel('Fase (rad)')
    axes[2, 0].legend()

    axes[2, 1].axis('off')
    axes[2, 1].text(0.5, 0.5,
                    r'$f(t-t_0) \leftrightarrow F(\omega)\,e^{-j\omega t_0}$'
                    '\n\nMagnitude preservada\nFase linear adicionada',
                    ha='center', va='center', fontsize=14,
                    bbox=dict(boxstyle='round', fc='lightyellow'))

    fig.tight_layout()
    save(fig, 'time_shift_property')


# ====================================================================
# 5. Propriedade da modulação
# ====================================================================
def fig_modulation_property():
    t = np.linspace(-3, 3, 2000)
    w = np.linspace(-60, 60, 4000)
    tau = 1.0
    w0 = 20.0

    ft = np.where(np.abs(t) <= tau / 2, 1.0, 0.0)
    mod = ft * np.cos(w0 * t)
    Fw = tau * np.sinc(w * tau / (2 * np.pi))
    Fw_mod = 0.5 * (tau * np.sinc((w - w0) * tau / (2 * np.pi)) +
                     tau * np.sinc((w + w0) * tau / (2 * np.pi)))

    fig, axes = plt.subplots(3, 1, figsize=(10, 8))

    axes[0].plot(t, ft, 'C0', lw=2)
    axes[0].set_title(r'Sinal banda-base $f(t)=\mathrm{rect}(t/\tau)$')
    axes[0].set_xlabel('$t$ (s)'); axes[0].set_ylabel('$f(t)$')
    axes[0].set_ylim(-0.3, 1.4)

    axes[1].plot(t, mod, 'C1', lw=2)
    axes[1].set_title(r'Sinal modulado $f(t)\cos(\omega_0 t)$')
    axes[1].set_xlabel('$t$ (s)'); axes[1].set_ylabel('Amplitude')

    axes[2].plot(w, Fw, 'C0', lw=1.5, alpha=0.4, label=r'$F(\omega)$')
    axes[2].plot(w, Fw_mod, 'C1', lw=2, label=r'$\frac{1}{2}[F(\omega-\omega_0)+F(\omega+\omega_0)]$')
    axes[2].set_title('Espectro')
    axes[2].set_xlabel(r'$\omega$ (rad/s)'); axes[2].set_ylabel('Amplitude')
    axes[2].legend(fontsize=11)

    fig.tight_layout()
    save(fig, 'modulation_property')


# ====================================================================
# 6. Teorema da convolução
# ====================================================================
def fig_convolution_time_freq():
    t = np.linspace(-5, 10, 2000)
    dt = t[1] - t[0]
    w = np.linspace(-10, 10, 2000)
    tau = 2.0
    a = 1.0

    f1 = np.where((t >= 0) & (t <= tau), 1.0, 0.0)
    f2 = np.where(t >= 0, np.exp(-a * t), 0.0)
    conv = np.convolve(f1, f2, mode='full')[:len(t)] * dt

    F1 = tau * np.sinc(w * tau / (2 * np.pi)) * np.exp(-1j * w * tau / 2)
    F2 = 1.0 / (a + 1j * w)
    F1F2 = F1 * F2

    fig, axes = plt.subplots(2, 3, figsize=(12, 6))

    axes[0, 0].plot(t, f1, 'C0', lw=2)
    axes[0, 0].set_title(r'$f_1(t)=\mathrm{rect}$'); axes[0, 0].set_xlabel('$t$')

    axes[0, 1].plot(t, f2, 'C1', lw=2)
    axes[0, 1].set_title(r'$f_2(t)=e^{-at}u(t)$'); axes[0, 1].set_xlabel('$t$')

    axes[0, 2].plot(t, conv, 'C2', lw=2)
    axes[0, 2].set_title(r'$f_1 * f_2$ (convolução)'); axes[0, 2].set_xlabel('$t$')

    axes[1, 0].plot(w, np.abs(F1), 'C0', lw=2)
    axes[1, 0].set_title(r'$|F_1(\omega)|$'); axes[1, 0].set_xlabel(r'$\omega$')

    axes[1, 1].plot(w, np.abs(F2), 'C1', lw=2)
    axes[1, 1].set_title(r'$|F_2(\omega)|$'); axes[1, 1].set_xlabel(r'$\omega$')

    axes[1, 2].plot(w, np.abs(F1F2), 'C2', lw=2)
    axes[1, 2].set_title(r'$|F_1 \cdot F_2|$ (produto)'); axes[1, 2].set_xlabel(r'$\omega$')

    fig.tight_layout()
    save(fig, 'convolution_time_freq')


# ====================================================================
# 7. Teorema de Parseval — energia
# ====================================================================
def fig_parseval_energy():
    t = np.linspace(-5, 5, 1000)
    w = np.linspace(-10, 10, 1000)
    sigma = 1.0
    ft = np.exp(-t**2 / (2 * sigma**2))
    Fw = sigma * np.sqrt(2 * np.pi) * np.exp(-sigma**2 * w**2 / 2)

    fig, axes = plt.subplots(1, 2, figsize=(10, 4))

    axes[0].plot(t, ft**2, 'C0', lw=2)
    axes[0].fill_between(t, ft**2, alpha=0.3, color='C0')
    E_t = np.trapezoid(ft**2, t)
    axes[0].set_title(rf'$|f(t)|^2$ — Energia $E={E_t:.2f}$')
    axes[0].set_xlabel('$t$'); axes[0].set_ylabel('$|f(t)|^2$')

    Fw2 = Fw**2 / (2 * np.pi)
    E_w = np.trapezoid(Fw2, w)
    axes[1].plot(w, Fw2, 'C1', lw=2)
    axes[1].fill_between(w, Fw2, alpha=0.3, color='C1')
    axes[1].set_title(rf'$|F(\omega)|^2/2\pi$ — Energia $E={E_w:.2f}$')
    axes[1].set_xlabel(r'$\omega$'); axes[1].set_ylabel(r'$|F(\omega)|^2/2\pi$')

    fig.tight_layout()
    save(fig, 'parseval_energy')


# ====================================================================
# 8. Resposta de sistema LTI
# ====================================================================
def fig_lti_system_response():
    w = np.linspace(-20, 20, 2000)
    # Sinal de entrada: banda larga (Gaussiana larga em freq)
    Xw = np.exp(-w**2 / (2 * 8**2))
    # Filtro passa-baixas ideal-ish (butterworth)
    wc = 5.0
    order = 6
    Hw = 1.0 / (1 + (w / wc)**(2 * order))
    Yw = Xw * Hw

    fig, axes = plt.subplots(3, 1, figsize=(10, 7))

    axes[0].plot(w, Xw, 'C0', lw=2)
    axes[0].set_title(r'Espectro de entrada $|X(\omega)|$')
    axes[0].set_ylabel('Amplitude')

    axes[1].plot(w, Hw, 'C1', lw=2)
    axes[1].axvline(wc, color='gray', ls=':', lw=1)
    axes[1].axvline(-wc, color='gray', ls=':', lw=1)
    axes[1].set_title(r'Resposta em frequência $|H(\omega)|$ — filtro passa-baixas')
    axes[1].set_ylabel('Amplitude')
    axes[1].annotate(rf'$\omega_c={wc}$', xy=(wc, 0.5), fontsize=12,
                     xytext=(wc + 3, 0.6),
                     arrowprops=dict(arrowstyle='->', color='gray'))

    axes[2].fill_between(w, Yw, alpha=0.3, color='C2')
    axes[2].plot(w, Yw, 'C2', lw=2)
    axes[2].set_title(r'Saída $|Y(\omega)|=|H(\omega)|\,|X(\omega)|$')
    axes[2].set_xlabel(r'$\omega$ (rad/s)'); axes[2].set_ylabel('Amplitude')

    fig.tight_layout()
    save(fig, 'lti_system_response')


# ====================================================================
# 9. Distorção de sinal
# ====================================================================
def fig_signal_distortion():
    w = np.linspace(-20, 20, 2000)
    t = np.linspace(-3, 3, 1000)

    # Pulso de entrada (Gaussiana)
    sigma = 0.5
    pulse = np.exp(-t**2 / (2 * sigma**2))

    fig, axes = plt.subplots(3, 2, figsize=(10, 8))

    # Ideal
    axes[0, 0].axhline(1, color='C0', lw=2)
    axes[0, 0].set_title('Magnitude ideal (plana)')
    axes[0, 0].set_ylabel(r'$|H(\omega)|$'); axes[0, 0].set_ylim(0, 1.5)

    axes[1, 0].plot(w, -0.5 * w, 'C0', lw=2)
    axes[1, 0].set_title('Fase ideal (linear)')
    axes[1, 0].set_ylabel(r'$\angle H(\omega)$')

    axes[2, 0].plot(t, pulse, 'C0', lw=2)
    axes[2, 0].set_title('Saída ideal (sem distorção)')
    axes[2, 0].set_xlabel('$t$'); axes[2, 0].set_ylabel('Amplitude')

    # Distorcido
    mag_dist = 1 + 0.3 * np.cos(w * 0.8)
    axes[0, 1].plot(w, mag_dist, 'C1', lw=2)
    axes[0, 1].set_title('Magnitude distorcida')
    axes[0, 1].set_ylabel(r'$|H(\omega)|$')

    phase_dist = -0.5 * w + 0.4 * np.sin(w * 0.6)
    axes[1, 1].plot(w, phase_dist, 'C1', lw=2)
    axes[1, 1].plot(w, -0.5 * w, 'C0', lw=1, ls='--', alpha=0.5)
    axes[1, 1].set_title('Fase distorcida (não linear)')
    axes[1, 1].set_ylabel(r'$\angle H(\omega)$')

    # Saída distorcida — simular via IFFT
    N = 2048
    ww = np.linspace(-40, 40, N)
    H_dist = (1 + 0.3 * np.cos(ww * 0.8)) * np.exp(1j * (-0.5 * ww + 0.4 * np.sin(ww * 0.6)))
    Xw = sigma * np.sqrt(2 * np.pi) * np.exp(-sigma**2 * ww**2 / 2)
    Yw = Xw * H_dist
    yt = np.fft.fftshift(np.fft.ifft(np.fft.ifftshift(Yw))).real
    tt = np.linspace(-3, 3, N)
    yt = yt / np.max(np.abs(yt)) * np.max(pulse)

    axes[2, 1].plot(tt, yt, 'C1', lw=2)
    axes[2, 1].set_title('Saída distorcida')
    axes[2, 1].set_xlabel('$t$'); axes[2, 1].set_ylabel('Amplitude')

    for ax_row in axes:
        for ax in ax_row:
            ax.set_xlim(-3, 3) if 't' in ax.get_xlabel() else None

    fig.tight_layout()
    save(fig, 'signal_distortion')


# ====================================================================
# 10. PSD de ruído
# ====================================================================
def fig_psd_noise():
    w = np.linspace(-20, 20, 2000)
    N0 = 1.0
    RC = 0.3

    Sw_white = N0 / 2 * np.ones_like(w)
    Hw2 = 1.0 / (1 + (w * RC)**2)
    Sw_filtered = (N0 / 2) * Hw2

    fig, axes = plt.subplots(1, 2, figsize=(10, 4))

    axes[0].plot(w, Sw_white, 'C0', lw=2)
    axes[0].set_title(r'PSD do ruído branco $S(\omega)=N_0/2$')
    axes[0].set_xlabel(r'$\omega$ (rad/s)'); axes[0].set_ylabel(r'$S(\omega)$')
    axes[0].set_ylim(0, 1.2)

    axes[1].plot(w, Sw_filtered, 'C1', lw=2)
    axes[1].fill_between(w, Sw_filtered, alpha=0.25, color='C1')
    axes[1].set_title(r'PSD após filtro RC: $S_y=\frac{N_0/2}{1+(\omega RC)^2}$')
    axes[1].set_xlabel(r'$\omega$ (rad/s)'); axes[1].set_ylabel(r'$S_y(\omega)$')

    fig.tight_layout()
    save(fig, 'psd_noise')


# ====================================================================
# 11. Amostragem e aliasing
# ====================================================================
def fig_sampling_aliasing():
    w = np.linspace(-60, 60, 4000)
    W = 10  # banda do sinal

    def triangle_spec(w, W):
        return np.where(np.abs(w) <= W, 1 - np.abs(w) / W, 0.0)

    X = triangle_spec(w, W)

    fig, axes = plt.subplots(3, 1, figsize=(10, 7))

    # Original
    axes[0].plot(w, X, 'C0', lw=2)
    axes[0].fill_between(w, X, alpha=0.2, color='C0')
    axes[0].set_title(r'Espectro original $X(\omega)$, banda $W$')
    axes[0].set_ylabel('Amplitude')
    axes[0].axvline(W, ls=':', color='gray'); axes[0].axvline(-W, ls=':', color='gray')
    axes[0].annotate('$W$', xy=(W, 0), fontsize=13, ha='center', va='top')

    # Sem aliasing  fs > 2W  =>  ws = 2pi*fs > 2*2pi*W  =>  ws > 2W in rad
    ws_good = 3.0 * W  # > 2W
    spec_sum = np.zeros_like(w)
    for k in range(-4, 5):
        spec_sum += triangle_spec(w - k * ws_good, W)
    axes[1].plot(w, spec_sum, 'C0', lw=2)
    axes[1].fill_between(w, spec_sum, alpha=0.15, color='C0')
    axes[1].set_title(rf'Amostrado com $\omega_s={ws_good:.0f}$ rad/s ($>\,2W$) — sem aliasing')
    axes[1].set_ylabel('Amplitude')

    # Com aliasing  fs < 2W
    ws_bad = 1.4 * W
    spec_sum2 = np.zeros_like(w)
    for k in range(-6, 7):
        spec_sum2 += triangle_spec(w - k * ws_bad, W)
    # Mostrar sobreposição
    # réplica central
    central = triangle_spec(w, W)
    overlap = spec_sum2 - central
    axes[2].fill_between(w, spec_sum2, alpha=0.15, color='C0')
    axes[2].plot(w, spec_sum2, 'C0', lw=1.5)
    # pintar região de aliasing (onde overlap > 0 e central > 0)
    alias_mask = (central > 0) & (overlap > 0)
    axes[2].fill_between(w, 0, spec_sum2, where=alias_mask, alpha=0.4, color='red',
                         label='Aliasing')
    axes[2].set_title(rf'Amostrado com $\omega_s={ws_bad:.0f}$ rad/s ($<\,2W$) — aliasing')
    axes[2].set_xlabel(r'$\omega$ (rad/s)'); axes[2].set_ylabel('Amplitude')
    axes[2].legend()

    fig.tight_layout()
    save(fig, 'sampling_aliasing')


# ====================================================================
# 12. Gaussiana e sua transformada
# ====================================================================
def fig_gaussian_fourier():
    t = np.linspace(-5, 5, 1000)
    w = np.linspace(-10, 10, 1000)

    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    for alpha, color, ls in [(1, 'C0', '-'), (2, 'C1', '-')]:
        ft = np.exp(-alpha * t**2)
        Fw = np.sqrt(np.pi / alpha) * np.exp(-w**2 / (4 * alpha))
        axes[0].plot(t, ft, color=color, lw=2, ls=ls, label=rf'$\alpha={alpha}$')
        axes[1].plot(w, Fw, color=color, lw=2, ls=ls, label=rf'$\alpha={alpha}$')

    axes[0].set_xlabel('$t$'); axes[0].set_ylabel('$f(t)$')
    axes[0].set_title(r'$f(t)=e^{-\alpha t^2}$')
    axes[0].legend()

    axes[1].set_xlabel(r'$\omega$ (rad/s)'); axes[1].set_ylabel(r'$F(\omega)$')
    axes[1].set_title(r'$F(\omega)=\sqrt{\pi/\alpha}\;e^{-\omega^2/4\alpha}$')
    axes[1].legend()

    fig.suptitle('Princípio da incerteza: estreito no tempo → largo na frequência',
                 fontsize=13, y=1.02)
    fig.tight_layout()
    save(fig, 'gaussian_fourier')


# ====================================================================
# MAIN
# ====================================================================
if __name__ == '__main__':
    print('Gerando figuras do capítulo 3 (Transformada de Fourier)...')
    fig_bilateral_exponential()
    fig_delta_and_constant()
    fig_sinc_rect_duality()
    fig_rect_vs_tri()
    fig_time_shift_property()
    fig_modulation_property()
    fig_convolution_time_freq()
    fig_parseval_energy()
    fig_lti_system_response()
    fig_signal_distortion()
    fig_psd_noise()
    fig_sampling_aliasing()
    fig_gaussian_fourier()
    print('Concluído!')
