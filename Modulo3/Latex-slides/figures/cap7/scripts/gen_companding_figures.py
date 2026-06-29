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
    m1   = np.abs(y) <  1 / (1 + lA)   # limiar correto da região linear em y
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
def _plot_curve(ax, x, y, label, color):
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

    ax.set_xlabel('Entrada normalizada $x$', fontsize=13)
    ax.set_ylabel('Saída comprimida $y$',     fontsize=13)
    ax.set_title(f'Curva de Compressão: {label}', fontweight='bold')
    ax.legend(fontsize=11)
    ax.set_aspect('equal')
    ax.axhline(0, color='k', lw=0.5)
    ax.axvline(0, color='k', lw=0.5)


def _plot_signals(ax, law_compress, color):
    """Mostra a compressão no tempo: entrada x(t) vs. saída y(t)=C(x(t))."""
    tt   = np.linspace(0, 1, 2000)
    xin  = 0.7 * np.sin(2 * np.pi * tt)     # entrada com amplitudes pequenas e grandes
    yout = law_compress(xin)

    ax.plot(tt, xin,  color='gray', lw=2.0, ls='--', label=r'Entrada $x(t)$')
    ax.plot(tt, yout, color=color,  lw=2.6,           label=r'Saída $y(t)$ (comprimida)')

    # destaca o ganho perto de zero e o achatamento no pico
    ax.annotate('picos\nachatados', xy=(0.25, yout[np.argmin(np.abs(tt-0.25))]),
                xytext=(0.30, 0.45), fontsize=9, ha='center', color=RED,
                arrowprops=dict(arrowstyle='->', color=RED, lw=1.3))
    ax.annotate('subida rápida\n(pequenos sinais\namplificados)',
                xy=(0.02, yout[5]), xytext=(0.55, -0.55), fontsize=9, ha='center',
                color=UNB_GOLD,
                arrowprops=dict(arrowstyle='->', color=UNB_GOLD, lw=1.3))

    ax.set_xlabel('tempo (normalizado)', fontsize=13)
    ax.set_ylabel('amplitude',           fontsize=13)
    ax.set_title('Compressão no tempo: entrada vs. saída', fontweight='bold',
                 fontsize=12)
    ax.set_ylim(-1.05, 1.05)
    ax.legend(fontsize=10, loc='upper right')
    ax.axhline(0, color='k', lw=0.5)


def gen_companding_curves():
    x = np.linspace(-1, 1, 2000)
    y_mu = mu_law_compress(x)
    y_a  = a_law_compress(x)

    # Figura combinada (mantida para compatibilidade)
    fig, axes = plt.subplots(1, 2, figsize=(10, 5))
    _plot_curve(axes[0], x, y_mu, r'$\mu$-law  ($\mu = 255$)', UNB_BLUE)
    _plot_curve(axes[1], x, y_a,  'A-law  ($A = 87{,}6$)',     UNB_GREEN)
    plt.tight_layout()
    plt.savefig('../companding_curves.pdf', bbox_inches='tight')
    plt.close()
    print("  [OK] companding_curves.pdf")

    # Figuras separadas (um gráfico por slide): curva + sinais entrada/saída
    for law_c, y, label, color, fname in [
        (mu_law_compress, y_mu, r'$\mu$-law  ($\mu = 255$)', UNB_BLUE,
         'companding_curve_mulaw.pdf'),
        (a_law_compress,  y_a,  'A-law  ($A = 87{,}6$)',     UNB_GREEN,
         'companding_curve_alaw.pdf'),
    ]:
        fig, (ax_c, ax_s) = plt.subplots(2, 1, figsize=(6.4, 8.4),
                                         gridspec_kw={'height_ratios': [1.25, 1]})
        _plot_curve(ax_c, x, y, label, color)
        _plot_signals(ax_s, law_c, color)
        plt.tight_layout()
        plt.savefig('../' + fname, bbox_inches='tight')
        plt.close()
        print(f"  [OK] {fname}")

    # Terceira figura: as duas curvas sobrepostas no mesmo gráfico
    fig, ax = plt.subplots(figsize=(7.2, 6.6))
    ax.plot(x, x,   color='gray',  lw=1.5, ls='--', alpha=0.7,
            label='Linear (sem compressão)')
    ax.plot(x, y_mu, color=UNB_BLUE,  lw=2.8,           label=r'$\mu$-law  ($\mu = 255$)')
    ax.plot(x, y_a,  color=UNB_GREEN, lw=2.8, ls='-.',  label='A-law  ($A = 87{,}6$)')
    ax.set_xlabel('Entrada normalizada $x$', fontsize=13)
    ax.set_ylabel('Saída comprimida $y$',     fontsize=13)
    ax.set_title(r'Curvas de Compressão: $\mu$-law vs. A-law', fontweight='bold')
    ax.legend(fontsize=11)
    ax.set_aspect('equal')
    ax.axhline(0, color='k', lw=0.5)
    ax.axvline(0, color='k', lw=0.5)
    plt.tight_layout()
    plt.savefig('../companding_curves_combined.pdf', bbox_inches='tight')
    plt.close()
    print("  [OK] companding_curves_combined.pdf")


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
    sqnr_a       = []

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

        # --- A-law companding ---
        g_qa    = a_law_expand(quantize_uniform(a_law_compress(g), n_bits))
        P_q_a   = np.mean((g_qa - g)**2)
        sqnr_a.append(10 * np.log10(P_s / (P_q_a + 1e-30)))

    fig, ax = plt.subplots(figsize=(9.5, 6.0))

    ax.plot(power_dBFS, sqnr_uniform, color=UNB_BLUE,  lw=2.5,
            label=f'Uniforme  ($n = {n_bits}$ bits)')
    ax.plot(power_dBFS, sqnr_mu,      color=RED,        lw=2.5, ls='--',
            label=fr'$\mu$-law  ($\mu = 255$)')
    ax.plot(power_dBFS, sqnr_a,       color=UNB_GREEN,  lw=2.5, ls='-.',
            label=r'A-law  ($A = 87{,}6$)')

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


# ===========================================================================
# Tabela: erro médio (MSE) e SNR por método, para os slides
# ===========================================================================
def print_snr_table(n_bits=8):
    t = np.linspace(0, 200, 2_000_000)
    print(f"\n  Tabela MSE / SNR  (n = {n_bits} bits, senoide)")
    for p_dBFS in (-20, -6):
        amp = 10**(p_dBFS / 20)
        g   = amp * np.sin(2*np.pi*t)
        P_s = np.mean(g**2)
        e_u = np.mean((quantize_uniform(g, n_bits) - g)**2)
        e_m = np.mean((mu_law_expand(quantize_uniform(mu_law_compress(g), n_bits)) - g)**2)
        e_a = np.mean((a_law_expand(quantize_uniform(a_law_compress(g), n_bits)) - g)**2)
        print(f"  --- sinal a {p_dBFS} dBFS  (P_s = {P_s:.3e}) ---")
        for name, e in (('Uniforme', e_u), ('mu-law', e_m), ('A-law', e_a)):
            print(f"    {name:9s}  MSE = {e:.3e}   SNR = {10*np.log10(P_s/e):6.2f} dB")


if __name__ == '__main__':
    print("Gerando figuras de companding...")
    gen_companding_curves()
    gen_companding_sqnr_comparison()
    print_snr_table()
    print("Concluído!\n")
