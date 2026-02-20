#!/usr/bin/env python3
"""
Gera figuras de diagrama de olho e PAM M-ário para os slides.
Saída: ../eye_diagram_clean.pdf, ../eye_diagram_isi.pdf,
       ../pam4_constellation.pdf, ../pam_ber_comparison.pdf

Uso: python gen_eye_pam_figures.py
"""

import numpy as np
import matplotlib.pyplot as plt

# ---------------------------------------------------------------------------
# Configurações de estilo
# ---------------------------------------------------------------------------
plt.rcParams.update({
    'font.size': 11,
    'font.family': 'serif',
    'axes.labelsize': 12,
    'axes.titlesize': 12,
    'xtick.labelsize': 10,
    'ytick.labelsize': 10,
    'figure.dpi': 150,
    'text.usetex': False,
    'axes.spines.top': False,
    'axes.spines.right': False,
    'axes.grid': True,
    'grid.alpha': 0.3,
})

UNB_BLUE  = '#003B5C'
UNB_GREEN = '#006633'
UNB_GOLD  = '#F2A900'
RED       = '#C0392B'
PURPLE    = '#8E44AD'
TEAL      = '#16A085'


def raised_cosine_time(t, T, alpha):
    """Raised cosine pulse p(t) in time domain."""
    p = np.zeros_like(t)
    for i, ti in enumerate(t):
        if abs(ti) < 1e-12:
            p[i] = 1.0
        elif alpha > 0 and abs(abs(ti) - T / (2 * alpha)) < 1e-12:
            p[i] = (alpha / 2.0) * np.sinc(1.0 / (2 * alpha))
        else:
            denom = 1 - (2 * alpha * ti / T)**2
            if abs(denom) < 1e-12:
                p[i] = 0.0
            else:
                p[i] = np.sinc(ti / T) * np.cos(np.pi * alpha * ti / T) / denom
    return p


# ===========================================================================
# Figura 1: Diagrama de olho — limpo (bom canal)
# ===========================================================================
def gen_eye_diagram_clean():
    np.random.seed(42)
    T = 1.0
    alpha = 0.35
    N_bits = 500
    sps = 100  # samples per symbol

    bits = 2 * np.random.randint(0, 2, N_bits) - 1  # ±1
    t_pulse = np.arange(-6*sps, 6*sps + 1) / sps * T
    pulse = raised_cosine_time(t_pulse, T, alpha)

    # Generate signal
    sig = np.zeros(N_bits * sps + len(t_pulse))
    for i, b in enumerate(bits):
        start = i * sps
        sig[start:start + len(t_pulse)] += b * pulse

    # Add small noise
    sig += 0.02 * np.random.randn(len(sig))

    # Eye diagram: overlay 2T segments
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.5))

    for ax_idx, (ax, title, noise_level) in enumerate(zip(
        axes,
        [r'(a) Canal limpo ($\alpha=0.35$)', r'(b) Com ruído ($\sigma=0.15$)'],
        [0.0, 0.15]
    )):
        if noise_level > 0:
            sig_noisy = sig + noise_level * np.random.randn(len(sig))
        else:
            sig_noisy = sig.copy()

        traces_per_eye = 150
        segment_len = 2 * sps
        t_eye = np.linspace(0, 2, segment_len)

        for k in range(10, 10 + traces_per_eye):
            start = k * sps
            end = start + segment_len
            if end < len(sig_noisy):
                ax.plot(t_eye, sig_noisy[start:end], color=UNB_BLUE,
                        linewidth=0.3, alpha=0.4)

        ax.set_title(title, fontweight='bold')
        ax.set_xlabel(r'Tempo ($t / T$)', fontsize=11)
        ax.set_ylabel('Amplitude', fontsize=11)
        ax.set_xlim([0, 2])
        ax.set_ylim([-1.6, 1.6])
        ax.axvline(1.0, color=RED, linewidth=1.5, linestyle='--',
                   alpha=0.7, label='Instante ótimo')
        if ax_idx == 0:
            ax.legend(fontsize=9)

    plt.tight_layout()
    plt.savefig('../eye_diagram_clean.pdf', bbox_inches='tight')
    plt.close()
    print("  [OK] eye_diagram_clean.pdf")


# ===========================================================================
# Figura 2: Diagrama de olho — efeito do roll-off
# ===========================================================================
def gen_eye_diagram_rolloff():
    np.random.seed(42)
    T = 1.0
    N_bits = 500
    sps = 100

    bits = 2 * np.random.randint(0, 2, N_bits) - 1
    alphas = [0.0, 0.25, 0.5, 1.0]
    colors = [UNB_BLUE, UNB_GREEN, UNB_GOLD, RED]

    fig, axes = plt.subplots(1, 4, figsize=(14, 3.5), sharey=True)

    for ax, alpha, col in zip(axes, alphas, colors):
        t_pulse = np.arange(-6*sps, 6*sps + 1) / sps * T
        pulse = raised_cosine_time(t_pulse, T, alpha)

        sig = np.zeros(N_bits * sps + len(t_pulse))
        for i, b in enumerate(bits):
            start = i * sps
            sig[start:start + len(t_pulse)] += b * pulse

        sig += 0.03 * np.random.randn(len(sig))

        traces = 120
        segment_len = 2 * sps
        t_eye = np.linspace(0, 2, segment_len)

        for k in range(10, 10 + traces):
            start = k * sps
            end = start + segment_len
            if end < len(sig):
                ax.plot(t_eye, sig[start:end], color=col,
                        linewidth=0.3, alpha=0.4)

        ax.set_title(rf'$\alpha = {alpha}$', fontweight='bold')
        ax.set_xlabel(r'$t / T$', fontsize=11)
        ax.set_xlim([0, 2])
        ax.set_ylim([-1.6, 1.6])
        ax.axvline(1.0, color='black', linewidth=1, linestyle='--', alpha=0.5)

    axes[0].set_ylabel('Amplitude', fontsize=11)
    plt.tight_layout()
    plt.savefig('../eye_diagram_rolloff.pdf', bbox_inches='tight')
    plt.close()
    print("  [OK] eye_diagram_rolloff.pdf")


# ===========================================================================
# Figura 3: Constelação PAM M-ário
# ===========================================================================
def gen_pam_constellation():
    fig, axes = plt.subplots(4, 1, figsize=(9, 6),
                              gridspec_kw={'height_ratios': [1, 1, 1, 1]})

    pam_orders = [2, 4, 8, 16]
    colors = [UNB_BLUE, UNB_GREEN, RED, PURPLE]

    for ax, M, col in zip(axes, pam_orders, colors):
        levels = np.linspace(-(M-1), M-1, M)
        ax.scatter(levels, np.zeros(M), color=col, s=120, zorder=5,
                   edgecolors='black', linewidth=0.8)
        for lev in levels:
            ax.annotate(f'{int(lev)}', (lev, 0), textcoords="offset points",
                       xytext=(0, 12), ha='center', fontsize=9, fontweight='bold')
        ax.axhline(0, color='gray', linewidth=0.5)
        ax.set_xlim([-(M-1)-2, (M-1)+2])
        ax.set_ylim([-0.5, 0.5])
        ax.set_yticks([])
        ax.set_title(rf'{M}-PAM  ($M={M}$, $\log_2 M = {int(np.log2(M))}$ bits/símbolo)',
                     fontsize=11, fontweight='bold')
        ax.spines['left'].set_visible(False)

        # Draw decision boundaries
        if M > 2:
            for i in range(M - 1):
                boundary = (levels[i] + levels[i+1]) / 2
                ax.axvline(boundary, color=col, linewidth=0.8, linestyle='--', alpha=0.4)

    axes[-1].set_xlabel('Nível de amplitude', fontsize=12)

    plt.tight_layout()
    plt.savefig('../pam_constellation.pdf', bbox_inches='tight')
    plt.close()
    print("  [OK] pam_constellation.pdf")


# ===========================================================================
# Figura 4: PAM — formas de onda 2-PAM vs 4-PAM
# ===========================================================================
def gen_pam_waveforms():
    T = 1.0
    sps = 200

    # 8 bits of data
    bit_seq = [1, 0, 1, 1, 0, 0, 1, 0]

    fig, axes = plt.subplots(2, 1, figsize=(10, 5))

    # (a) 2-PAM: each bit → one symbol
    ax = axes[0]
    symbols_2pam = [2*b - 1 for b in bit_seq]  # map 0→-1, 1→+1
    t_total = np.linspace(0, len(symbols_2pam)*T, len(symbols_2pam)*sps, endpoint=False)
    sig_2pam = np.zeros_like(t_total)
    for i, s in enumerate(symbols_2pam):
        sig_2pam[i*sps:(i+1)*sps] = s

    ax.plot(t_total/T, sig_2pam, color=UNB_BLUE, linewidth=2.0)
    ax.set_title(r'(a) 2-PAM: cada bit $\rightarrow$ 1 símbolo ($R_s = R_b$)',
                 fontweight='bold')
    ax.set_ylabel('Amplitude')
    ax.set_xlim([0, len(symbols_2pam)])
    ax.set_ylim([-2.0, 2.0])
    ax.set_yticks([-1, 0, 1])
    ax.axhline(0, color='black', linewidth=0.5)
    for i in range(len(symbols_2pam)+1):
        ax.axvline(i, color='gray', linewidth=0.3, linestyle=':')
    # Annotate bits
    for i, b in enumerate(bit_seq):
        ax.text(i + 0.5, 1.6, str(b), ha='center', fontsize=11,
                fontweight='bold', color=UNB_BLUE)
    ax.tick_params(labelbottom=False)

    # (b) 4-PAM: 2 bits → one symbol
    ax = axes[1]
    mapping_4pam = {(0,0): -3, (0,1): -1, (1,0): 1, (1,1): 3}
    symbols_4pam = []
    for i in range(0, len(bit_seq), 2):
        pair = (bit_seq[i], bit_seq[i+1])
        symbols_4pam.append(mapping_4pam[pair])

    t_total_4 = np.linspace(0, len(symbols_4pam)*T, len(symbols_4pam)*sps, endpoint=False)
    sig_4pam = np.zeros_like(t_total_4)
    for i, s in enumerate(symbols_4pam):
        sig_4pam[i*sps:(i+1)*sps] = s

    ax.plot(t_total_4/T, sig_4pam, color=RED, linewidth=2.0)
    ax.set_title(r'(b) 4-PAM: 2 bits $\rightarrow$ 1 símbolo ($R_s = R_b/2$, metade da banda)',
                 fontweight='bold')
    ax.set_ylabel('Amplitude')
    ax.set_xlabel(r'Tempo ($t / T_s$)', fontsize=12)
    ax.set_xlim([0, len(symbols_4pam)])
    ax.set_ylim([-4.5, 4.5])
    ax.set_yticks([-3, -1, 0, 1, 3])
    ax.axhline(0, color='black', linewidth=0.5)
    for i in range(len(symbols_4pam)+1):
        ax.axvline(i, color='gray', linewidth=0.3, linestyle=':')
    # Annotate bit pairs
    for i in range(0, len(bit_seq), 2):
        pair_str = f'{bit_seq[i]}{bit_seq[i+1]}'
        ax.text(i//2 + 0.5, 3.8, pair_str, ha='center', fontsize=11,
                fontweight='bold', color=RED)

    plt.tight_layout()
    plt.savefig('../pam_waveforms.pdf', bbox_inches='tight')
    plt.close()
    print("  [OK] pam_waveforms.pdf")


# ===========================================================================
# Figura 5: Diagrama de olho para 4-PAM
# ===========================================================================
def gen_eye_diagram_4pam():
    np.random.seed(123)
    T = 1.0
    alpha = 0.35
    N_syms = 500
    sps = 100
    M = 4
    levels = np.array([-3, -1, 1, 3])

    symbols = levels[np.random.randint(0, M, N_syms)]
    t_pulse = np.arange(-6*sps, 6*sps + 1) / sps * T
    pulse = raised_cosine_time(t_pulse, T, alpha)

    sig = np.zeros(N_syms * sps + len(t_pulse))
    for i, s in enumerate(symbols):
        start = i * sps
        sig[start:start + len(t_pulse)] += s * pulse

    fig, axes = plt.subplots(1, 2, figsize=(10, 4.5))

    for ax, noise_level, title in zip(
        axes,
        [0.05, 0.25],
        [r'(a) 4-PAM, pouco ruído', r'(b) 4-PAM, mais ruído ($\sigma=0.25$)']
    ):
        sig_noisy = sig + noise_level * np.random.randn(len(sig))
        traces = 150
        segment_len = 2 * sps
        t_eye = np.linspace(0, 2, segment_len)

        for k in range(10, 10 + traces):
            start = k * sps
            end = start + segment_len
            if end < len(sig_noisy):
                ax.plot(t_eye, sig_noisy[start:end], color=PURPLE,
                        linewidth=0.3, alpha=0.35)

        ax.set_title(title, fontweight='bold')
        ax.set_xlabel(r'$t / T$', fontsize=11)
        ax.set_xlim([0, 2])
        ax.set_ylim([-4.5, 4.5])
        ax.axvline(1.0, color=RED, linewidth=1.5, linestyle='--', alpha=0.7)
        # Decision levels
        for lev in [-2, 0, 2]:
            ax.axhline(lev, color=UNB_GOLD, linewidth=1.0, linestyle=':', alpha=0.6)

    axes[0].set_ylabel('Amplitude', fontsize=11)
    plt.tight_layout()
    plt.savefig('../eye_diagram_4pam.pdf', bbox_inches='tight')
    plt.close()
    print("  [OK] eye_diagram_4pam.pdf")


if __name__ == '__main__':
    print("Gerando figuras de diagrama de olho e PAM...")
    gen_eye_diagram_clean()
    gen_eye_diagram_rolloff()
    gen_pam_constellation()
    gen_pam_waveforms()
    gen_eye_diagram_4pam()
    print("Concluído!\n")
