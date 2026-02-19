#!/usr/bin/env python3
"""
Gera figuras de companding (μ-law e A-law) para os slides.
Saída: ../companding_curves.pdf, ../companding_sqnr_comparison.pdf

Uso: python gen_companding_figures.py
"""

import numpy as np
import matplotlib.pyplot as plt

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


# ---------------------------------------------------------------------------
# Leis de compressão
# ---------------------------------------------------------------------------
def mu_law_compress(x, mu=255):
    return np.sign(x) * np.log(1 + mu * np.abs(x)) / np.log(1 + mu)

def mu_law_expand(y, mu=255):
    return np.sign(y) * (1/mu) * ((1 + mu)**np.abs(y) - 1)

def a_law_compress(x, A=87.6):
    y    = np.zeros_like(x, dtype=float)
    m1   = np.abs(x) <  1/A
    m2   = np.abs(x) >= 1/A
    y[m1] = np.sign(x[m1]) * A * np.abs(x[m1]) / (1 + np.log(A))
    y[m2] = np.sign(x[m2]) * (1 + np.log(A * np.abs(x[m2]))) / (1 + np.log(A))
    return y

def a_law_expand(y, A=87.6):
    x    = np.zeros_like(y, dtype=float)
    lA   = np.log(A)
    m1   = np.abs(y) <  A / (1 + lA)
    m2   = ~m1
    x[m1] = np.sign(y[m1]) * np.abs(y[m1]) * (1 + lA) / A
    x[m2] = np.sign(y[m2]) * np.exp(np.abs(y[m2]) * (1 + lA) - 1) / A
    return x

def quantize_uniform(x, n_bits, v_min=-1.0, v_max=1.0):
    L     = 2**n_bits
    delta = (v_max - v_min) / L
    x_c   = np.clip(x, v_min, v_max - 1e-12)
    idx   = np.floor((x_c - v_min) / delta).astype(int)
    idx   = np.clip(idx, 0, L - 1)
    return v_min + (idx + 0.5) * delta


# ===========================================================================
# Figura 1: Curvas de compressão μ-law e A-law
# ===========================================================================
def gen_companding_curves():
    x = np.linspace(-1, 1, 2000)
    y_mu = mu_law_compress(x)
    y_a  = a_law_compress(x)

    fig, axes = plt.subplots(1, 2, figsize=(10, 5))

    for ax, y, label, color, tag in [
        (axes[0], y_mu, r'$\mu$-law  ($\mu = 255$)', UNB_BLUE,  'mu_law'),
        (axes[1], y_a,  'A-law  ($A = 87{,}6$)',     UNB_GREEN, 'a_law'),
    ]:
        ax.plot(x, x, color='gray', lw=1.5, ls='--', alpha=0.7,
                label='Linear (sem compressão)')
        ax.plot(x, y, color=color,  lw=2.8, label=label)

        # Destaque: mais resolução perto de zero
        ax.annotate('Passos\nmenores\n(mais resolução)',
                    xy=(0.12, y[np.argmin(np.abs(x - 0.12))]),
                    xytext=(0.45, 0.12),
                    arrowprops=dict(arrowstyle='->', color=RED, lw=1.5),
                    fontsize=9.5, ha='center', color=RED)
        ax.annotate('Passos\nmaiores\n(menos resolução)',
                    xy=(0.75, y[np.argmin(np.abs(x - 0.75))]),
                    xytext=(0.35, 0.78),
                    arrowprops=dict(arrowstyle='->', color=UNB_GOLD, lw=1.5),
                    fontsize=9.5, ha='center', color=UNB_GOLD)

        ax.set_xlabel('Entrada normalizada $x$',   fontsize=12)
        ax.set_ylabel('Saída comprimida $y$',       fontsize=12)
        ax.set_title(f'Curva de Compressão: {label}', fontweight='bold')
        ax.legend(fontsize=10)
        ax.set_aspect('equal')
        ax.axhline(0, color='k', lw=0.5)
        ax.axvline(0, color='k', lw=0.5)

    plt.tight_layout()
    plt.savefig('../companding_curves.pdf', bbox_inches='tight')
    plt.close()
    print("  [OK] companding_curves.pdf")


# ===========================================================================
# Figura 2: SQNR — Uniforme vs μ-law
# ===========================================================================
def gen_companding_sqnr_comparison():
    n_bits = 8
    t = np.linspace(0, 200, 1_000_000)

    # Variar nível do sinal de -40 dBFS a 0 dBFS
    power_dBFS   = np.linspace(-40, 0, 50)
    sqnr_uniform = []
    sqnr_mu      = []

    for p_dBFS in power_dBFS:
        amp   = 10**(p_dBFS / 20)         # amplitude RMS fracional
        g     = amp * np.sin(2*np.pi*t)    # sinal senoidal

        # --- Quantização uniforme ---
        g_q_u = quantize_uniform(g, n_bits)
        P_s   = np.mean(g**2)
        P_q_u = np.mean((g_q_u - g)**2)
        sqnr_uniform.append(10 * np.log10(P_s / (P_q_u + 1e-30)))

        # --- μ-law companding ---
        g_comp  = mu_law_compress(g)        # compressão
        g_q_c   = quantize_uniform(g_comp, n_bits)  # quantização uniforme
        g_exp   = mu_law_expand(g_q_c)      # expansão
        P_q_m   = np.mean((g_exp - g)**2)
        sqnr_mu.append(10 * np.log10(P_s / (P_q_m + 1e-30)))

    fig, ax = plt.subplots(figsize=(9, 5.5))

    ax.plot(power_dBFS, sqnr_uniform, color=UNB_BLUE,  lw=2.5,
            label=f'Uniforme  ($n = {n_bits}$ bits)')
    ax.plot(power_dBFS, sqnr_mu,      color=RED,        lw=2.5, ls='--',
            label=fr'$\mu$-law  ($\mu = 255$,  $n = {n_bits}$ bits)')

    ax.axhline(y=30, color='gray', ls=':', lw=1.8,
               label='SQNR mínimo aceitável (~30 dB)')

    # Anotação: companding mantém SQNR constante
    idx_low = np.argmin(np.abs(power_dBFS - (-25)))
    ax.annotate('Companding: SQNR\nquase constante',
                xy=(-25, sqnr_mu[idx_low]),
                xytext=(-20, sqnr_mu[idx_low] + 12),
                arrowprops=dict(arrowstyle='->', color=RED, lw=1.5),
                fontsize=10, ha='center', color=RED)

    ax.set_xlabel('Nível do Sinal de Entrada (dBFS)', fontsize=13)
    ax.set_ylabel('SQNR (dB)',                        fontsize=13)
    ax.set_title(r'SQNR: Quantização Uniforme vs. $\mu$-law' +
                 f'  ($n = {n_bits}$ bits)', fontweight='bold')
    ax.legend(fontsize=10)
    ax.set_xlim([power_dBFS[0], 0])

    plt.tight_layout()
    plt.savefig('../companding_sqnr_comparison.pdf', bbox_inches='tight')
    plt.close()
    print("  [OK] companding_sqnr_comparison.pdf")


if __name__ == '__main__':
    print("Gerando figuras de companding...")
    gen_companding_curves()
    gen_companding_sqnr_comparison()
    print("Concluído!\n")
