#!/usr/bin/env python3
"""
Gera figuras de codificação de linha para os slides de Transmissão Digital.
Saída: ../line_coding_waveforms.pdf, ../line_coding_psd.pdf

Uso: python gen_line_coding_figures.py
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch

# ---------------------------------------------------------------------------
# Configurações de estilo (compatível com LaTeX)
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

# ===========================================================================
# Figura 1: Formas de onda das codificações de linha
# ===========================================================================
def gen_line_coding_waveforms():
    bits = [1, 0, 1, 1, 0, 0, 1, 0]
    Tb = 1.0  # duração de bit
    N = len(bits)
    samples_per_bit = 200
    total_samples = N * samples_per_bit
    t = np.linspace(0, N * Tb, total_samples, endpoint=False)

    def make_signal(bits, encoding):
        """Generate encoded signal."""
        sig = np.zeros(total_samples)
        if encoding == 'unipolar_nrz':
            for i, b in enumerate(bits):
                sig[i*samples_per_bit:(i+1)*samples_per_bit] = b
        elif encoding == 'polar_nrz':
            for i, b in enumerate(bits):
                sig[i*samples_per_bit:(i+1)*samples_per_bit] = 1 if b == 1 else -1
        elif encoding == 'polar_rz':
            for i, b in enumerate(bits):
                half = samples_per_bit // 2
                val = 1 if b == 1 else -1
                sig[i*samples_per_bit:i*samples_per_bit + half] = val
                # second half returns to zero
        elif encoding == 'manchester':
            for i, b in enumerate(bits):
                half = samples_per_bit // 2
                if b == 1:
                    sig[i*samples_per_bit:i*samples_per_bit + half] = 1
                    sig[i*samples_per_bit + half:(i+1)*samples_per_bit] = -1
                else:
                    sig[i*samples_per_bit:i*samples_per_bit + half] = -1
                    sig[i*samples_per_bit + half:(i+1)*samples_per_bit] = 1
        elif encoding == 'ami':
            last_pulse = -1
            for i, b in enumerate(bits):
                if b == 1:
                    last_pulse *= -1
                    sig[i*samples_per_bit:(i+1)*samples_per_bit] = last_pulse
                # zeros remain 0
        elif encoding == 'bipolar_rz':
            last_pulse = -1
            for i, b in enumerate(bits):
                half = samples_per_bit // 2
                if b == 1:
                    last_pulse *= -1
                    sig[i*samples_per_bit:i*samples_per_bit + half] = last_pulse
        return sig

    encodings = [
        ('unipolar_nrz', 'Unipolar NRZ', UNB_BLUE),
        ('polar_nrz', 'Polar NRZ', UNB_GREEN),
        ('polar_rz', 'Polar RZ', UNB_GOLD),
        ('manchester', 'Manchester (Bifase)', RED),
        ('ami', 'AMI (NRZ)', PURPLE),
        ('bipolar_rz', 'Bipolar RZ (AMI-RZ)', TEAL),
    ]

    fig, axes = plt.subplots(len(encodings) + 1, 1, figsize=(10, 10),
                              gridspec_kw={'height_ratios': [0.5] + [1]*len(encodings)})

    # ---- Bit stream header ----
    ax = axes[0]
    ax.set_xlim(0, N * Tb)
    ax.set_ylim(0, 1)
    ax.axis('off')
    for i, b in enumerate(bits):
        ax.text((i + 0.5) * Tb, 0.3, str(b), fontsize=16, fontweight='bold',
                ha='center', va='center', color=UNB_BLUE)
        ax.axvline(i * Tb, color='gray', linewidth=0.5, linestyle='--', ymin=0, ymax=1)
    ax.axvline(N * Tb, color='gray', linewidth=0.5, linestyle='--')
    ax.set_title('Sequência de bits', fontweight='bold', fontsize=13)

    # ---- Encoding waveforms ----
    for idx, (enc, label, color) in enumerate(encodings):
        ax = axes[idx + 1]
        sig = make_signal(bits, enc)
        ax.plot(t, sig, color=color, linewidth=2.0)
        ax.set_ylabel(label, fontsize=10, fontweight='bold', rotation=0,
                      labelpad=80, va='center')
        ax.set_ylim(-1.5, 1.5)
        ax.set_xlim(0, N * Tb)
        ax.set_yticks([-1, 0, 1])
        ax.axhline(0, color='black', linewidth=0.5)
        for i in range(N + 1):
            ax.axvline(i * Tb, color='gray', linewidth=0.5, linestyle='--')
        if idx < len(encodings) - 1:
            ax.tick_params(labelbottom=False)
        else:
            ax.set_xlabel(r'Tempo ($t / T_b$)', fontsize=12)
            ax.set_xticks(np.arange(0, N + 1))

    plt.tight_layout()
    plt.savefig('../line_coding_waveforms.pdf', bbox_inches='tight')
    plt.close()
    print("  [OK] line_coding_waveforms.pdf")


# ===========================================================================
# Figura 2: PSD das codificações de linha
# ===========================================================================
def gen_line_coding_psd():
    f = np.linspace(0.001, 3.0, 2000)  # f normalizado por Rb = 1/Tb
    Tb = 1.0

    def sinc2(x):
        return np.sinc(x)**2

    # Unipolar NRZ: S(f) = (Tb/4) * sinc^2(f*Tb) + (1/4)*delta(f)
    # (omit delta for plot)
    psd_unipolar = 0.25 * Tb * sinc2(f * Tb)

    # Polar NRZ: S(f) = Tb * sinc^2(f*Tb)
    psd_polar_nrz = Tb * sinc2(f * Tb)

    # Polar RZ: S(f) = (Tb/4) * sinc^2(f*Tb/2)
    psd_polar_rz = 0.25 * Tb * sinc2(f * Tb / 2)

    # Manchester: S(f) = Tb * sinc^2(f*Tb/2) * sin^2(pi*f*Tb/2)
    psd_manchester = Tb * sinc2(f * Tb / 2) * np.sin(np.pi * f * Tb / 2)**2

    # AMI: S(f) = Tb * sinc^2(f*Tb) * sin^2(pi*f*Tb)
    psd_ami = Tb * sinc2(f * Tb) * np.sin(np.pi * f * Tb)**2

    fig, ax = plt.subplots(1, 1, figsize=(9, 5))

    ax.plot(f, psd_unipolar / Tb, color=UNB_BLUE, linewidth=2.0, label='Unipolar NRZ')
    ax.plot(f, psd_polar_nrz / Tb, color=UNB_GREEN, linewidth=2.0, label='Polar NRZ')
    ax.plot(f, psd_polar_rz / Tb, color=UNB_GOLD, linewidth=2.0, label='Polar RZ')
    ax.plot(f, psd_manchester / Tb, color=RED, linewidth=2.0, label='Manchester')
    ax.plot(f, psd_ami / Tb, color=PURPLE, linewidth=2.0, label='AMI')

    ax.set_xlabel(r'Frequência normalizada ($f \cdot T_b$)', fontsize=12)
    ax.set_ylabel(r'PSD normalizada $S(f) / T_b$', fontsize=12)
    ax.set_title('Densidade Espectral de Potência — Códigos de Linha', fontweight='bold')
    ax.legend(fontsize=10, loc='upper right')
    ax.set_xlim([0, 3.0])
    ax.set_ylim([0, 1.15])

    # Mark first null positions
    ax.axvline(1.0, color='gray', linewidth=1, linestyle=':', alpha=0.6)
    ax.text(1.02, 1.05, r'$f = R_b$', fontsize=10, color='gray')
    ax.axvline(2.0, color='gray', linewidth=1, linestyle=':', alpha=0.6)
    ax.text(2.02, 1.05, r'$f = 2R_b$', fontsize=10, color='gray')

    plt.tight_layout()
    plt.savefig('../line_coding_psd.pdf', bbox_inches='tight')
    plt.close()
    print("  [OK] line_coding_psd.pdf")


if __name__ == '__main__':
    print("Gerando figuras de codificação de linha...")
    gen_line_coding_waveforms()
    gen_line_coding_psd()
    print("Concluído!\n")
