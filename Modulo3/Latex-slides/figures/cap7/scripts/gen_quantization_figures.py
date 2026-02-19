#!/usr/bin/env python3
"""
Gera figuras de quantização para os slides de Conversão Analógico-Digital.
Saída: ../quantization_*.pdf,  ../sqnr_vs_bits.pdf

Uso: python gen_quantization_figures.py
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

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
# Quantizador Uniforme
# ---------------------------------------------------------------------------
def quantize_uniform(x, n_bits, v_min=-1.0, v_max=1.0):
    """Quantizador uniforme — saída = ponto médio do intervalo."""
    L     = 2**n_bits
    delta = (v_max - v_min) / L
    x_c   = np.clip(x, v_min, v_max - 1e-12)
    idx   = np.floor((x_c - v_min) / delta).astype(int)
    idx   = np.clip(idx, 0, L - 1)
    return v_min + (idx + 0.5) * delta


# ===========================================================================
# Figura 1: Característica do quantizador + sinal quantizado
# ===========================================================================
def gen_quantization_illustration():
    n_bits = 3
    L      = 2**n_bits
    v_min, v_max = -1.0, 1.0
    delta  = (v_max - v_min) / L

    fig, axes = plt.subplots(1, 2, figsize=(11, 5))

    # ---- (a) Característica I/O (função escada) ----
    ax = axes[0]
    x_in  = np.linspace(v_min - 0.05, v_max + 0.05, 4000)
    x_out = quantize_uniform(x_in, n_bits)

    ax.plot(x_in, x_in,  color='gray',    lw=1.5, ls='--', alpha=0.6,
            label='Ideal (linear)')
    ax.plot(x_in, x_out, color=UNB_BLUE,  lw=2.5, label=f'Quantizador ({n_bits} bits)')

    # Linhas de grade nos níveis
    levels = v_min + (np.arange(L) + 0.5) * delta
    for lv in levels:
        ax.axhline(lv, color='gray', ls=':', lw=0.7, alpha=0.5)
    # Bordas dos intervalos
    boundaries = [v_min + k*delta for k in range(L + 1)]
    for b in boundaries:
        ax.axvline(b, color='gray', ls=':', lw=0.7, alpha=0.5)

    # Anotação do passo Δ
    lv0 = levels[L//2]
    lv1 = levels[L//2 + 1]
    ax.annotate('', xy=(0.6, lv1), xytext=(0.6, lv0),
                arrowprops=dict(arrowstyle='<->', color=RED, lw=2))
    ax.text(0.65, (lv0 + lv1)/2, r'$\Delta$', fontsize=14, color=RED, va='center')

    ax.set_xlabel(r'Entrada $g[n]$',  fontsize=12)
    ax.set_ylabel(r'Saída $\hat{g}[n]$', fontsize=12)
    ax.set_title(f'(a) Característica do Quantizador\n($n={n_bits}$ bits, $L={L}$ níveis)',
                 fontweight='bold')
    ax.legend(fontsize=10)
    ax.set_xlim([v_min - 0.1, v_max + 0.1])
    ax.set_ylim([v_min - 0.1, v_max + 0.1])
    ax.set_aspect('equal')

    # ---- (b) Sinal original vs. quantizado ----
    ax = axes[1]
    t_cont = np.linspace(0, 1, 2000)
    t_samp = np.linspace(0, 1, 60)
    g_c    = 0.85 * np.sin(2*np.pi*2.5*t_cont)
    g_s    = 0.85 * np.sin(2*np.pi*2.5*t_samp)
    g_q    = quantize_uniform(g_s, n_bits)

    ax.plot(t_cont, g_c, color=UNB_BLUE, lw=1.5, alpha=0.4, label='Original $g(t)$')
    ax.step(t_samp, g_q, color=UNB_GREEN, lw=2.5, where='mid',
            label=r'Quantizado $\hat{g}[n]$')
    for k in range(len(t_samp)):
        ax.plot([t_samp[k], t_samp[k]], [g_s[k], g_q[k]],
                'm-', lw=0.9, alpha=0.5)

    # Linhas de nível
    for lv in levels:
        ax.axhline(lv, color='gray', ls=':', lw=0.7, alpha=0.35)

    ax.set_xlabel('Tempo (s)', fontsize=12)
    ax.set_ylabel('Amplitude',  fontsize=12)
    ax.set_title(f'(b) Sinal Original vs. Quantizado\n($n={n_bits}$ bits, erro indicado em roxo)',
                 fontweight='bold')
    ax.legend(fontsize=10)
    ax.set_xlim([0, 1])

    plt.tight_layout()
    plt.savefig('../quantization_illustration.pdf', bbox_inches='tight')
    plt.close()
    print("  [OK] quantization_illustration.pdf")


# ===========================================================================
# Figura 2: PDF do erro de quantização
# ===========================================================================
def gen_quantization_error_pdf():
    fig, ax = plt.subplots(figsize=(7, 4))

    delta = 1.0        # normalizado
    e     = np.linspace(-delta, delta, 2000)
    pdf   = np.where(np.abs(e) <= delta/2, 1/delta, 0.0)

    ax.fill_between(e, 0, pdf, where=(np.abs(e) <= delta/2),
                    alpha=0.35, color=UNB_BLUE)
    ax.plot(e, pdf, color=UNB_BLUE, lw=3, label=r'$p(e_q) = 1/\Delta$')

    # Seta indicando largura Δ
    ax.annotate('', xy=(delta/2, -0.12), xytext=(-delta/2, -0.12),
                arrowprops=dict(arrowstyle='<->', color=UNB_GREEN, lw=2.5),
                annotation_clip=False)
    ax.text(0, -0.20, r'$\Delta$', ha='center', fontsize=15, color=UNB_GREEN,
            clip_on=False)

    # Seta indicando altura 1/Δ
    ax.annotate('', xy=(0.62, 1/delta), xytext=(0.62, 0),
                arrowprops=dict(arrowstyle='<->', color=RED, lw=2.5))
    ax.text(0.68, 0.5/delta, r'$\dfrac{1}{\Delta}$', ha='left', fontsize=14,
            color=RED, va='center')

    ax.axvline(-delta/2, color='gray', ls='--', lw=1.5, alpha=0.8)
    ax.axvline( delta/2, color='gray', ls='--', lw=1.5, alpha=0.8)
    ax.text(-delta/2, 1.1/delta, r'$-\Delta/2$', ha='center', fontsize=11)
    ax.text( delta/2, 1.1/delta, r'$+\Delta/2$', ha='center', fontsize=11)

    ax.axhline(0, color='k', lw=0.8)
    ax.set_xlabel(r'Erro de Quantização $e_q$', fontsize=13)
    ax.set_ylabel(r'$p(e_q)$',                 fontsize=13)
    ax.set_title('PDF do Erro de Quantização  —  Distribuição Uniforme',
                 fontweight='bold')
    ax.set_ylim([-0.3, 1.5/delta])
    ax.set_xlim([-1.1*delta, 1.1*delta])
    ax.legend(fontsize=12)

    plt.tight_layout()
    plt.savefig('../quantization_error_pdf.pdf', bbox_inches='tight')
    plt.close()
    print("  [OK] quantization_error_pdf.pdf")


# ===========================================================================
# Figura 3: SQNR vs. número de bits
# ===========================================================================
def gen_sqnr_vs_bits():
    t = np.linspace(0, 100, 500_000)
    g = np.sin(2*np.pi*t)   # senoide de amplitude 1

    n_vals      = np.arange(1, 17)
    sqnr_theory = 1.76 + 6.02 * n_vals
    sqnr_sim    = []

    for n in n_vals:
        g_q  = quantize_uniform(g, int(n))
        P_s  = np.mean(g**2)
        P_q  = np.mean((g_q - g)**2)
        sqnr_sim.append(10 * np.log10(P_s / P_q))

    fig, ax = plt.subplots(figsize=(9, 5.5))

    ax.plot(n_vals, sqnr_theory, color=RED,      lw=2.5, ls='--',
            marker='s', ms=6, label=r'Teoria:  $1{,}76 + 6{,}02\,n$ dB')
    ax.plot(n_vals, sqnr_sim,    color=UNB_BLUE, lw=2.5,
            marker='o', ms=6, label='Simulação (senoide em faixa cheia)')

    # Marcações práticas
    ax.axvline(x=8,  color=UNB_GOLD,  ls=':',  lw=2,
               label='Telefonia PCM  (8 bits,  ~50 dB)')
    ax.axvline(x=16, color=UNB_GREEN, ls=':',  lw=2,
               label='CD de áudio  (16 bits, ~98 dB)')
    ax.text(8.2,  5, '8 bits',  color=UNB_GOLD,  fontsize=10)
    ax.text(16.2, 5, '16 bits', color=UNB_GREEN, fontsize=10)

    # Anotação: 6 dB/bit
    n0 = 7
    ax.annotate(r'$\Delta$SQNR $\approx$ 6 dB/bit',
                xy=(n0+1, sqnr_theory[n0]),
                xytext=(n0-2, sqnr_theory[n0]-18),
                arrowprops=dict(arrowstyle='->', color='black', lw=1.5),
                fontsize=11, ha='center')

    ax.set_xlabel('Número de bits $n$', fontsize=13)
    ax.set_ylabel('SQNR (dB)',           fontsize=13)
    ax.set_title('SQNR vs. Número de Bits  —  Quantização Uniforme (Senoide)',
                 fontweight='bold')
    ax.legend(fontsize=10)
    ax.set_xticks(n_vals)
    ax.set_xlim([0.5, 16.5])

    plt.tight_layout()
    plt.savefig('../sqnr_vs_bits.pdf', bbox_inches='tight')
    plt.close()
    print("  [OK] sqnr_vs_bits.pdf")


# ===========================================================================
# Figura 4: Comparação visual com diferentes resoluções
# ===========================================================================
def gen_quantization_resolution():
    fig, axes = plt.subplots(1, 3, figsize=(13, 4.5), sharey=True)

    t_cont = np.linspace(0, 1, 3000)
    t_samp = np.linspace(0, 1, 120)
    g_cont = 0.9 * np.sin(2*np.pi*2*t_cont) + 0.35*np.sin(2*np.pi*5*t_cont)
    g_samp = 0.9 * np.sin(2*np.pi*2*t_samp) + 0.35*np.sin(2*np.pi*5*t_samp)

    for ax, n in zip(axes, [2, 4, 8]):
        g_q   = quantize_uniform(g_samp, n)
        P_s   = np.mean(g_samp**2)
        P_q   = np.mean((g_q - g_samp)**2)
        sqnr  = 10*np.log10(P_s / P_q)
        L     = 2**n

        ax.plot(t_cont, g_cont, color=UNB_BLUE, lw=1.5, alpha=0.4,
                label='Original')
        ax.step(t_samp, g_q, color=UNB_GREEN, lw=2, where='mid',
                label='Quantizado')
        ax.set_title(f'$n = {n}$ bits,  $L = {L}$ níveis\nSQNR = {sqnr:.1f} dB',
                     fontweight='bold')
        ax.set_xlabel('Tempo (s)', fontsize=11)
        ax.legend(fontsize=9)

    axes[0].set_ylabel('Amplitude', fontsize=12)
    plt.suptitle('Efeito do Número de Bits na Qualidade da Quantização',
                 fontsize=13, fontweight='bold', y=1.01)
    plt.tight_layout()
    plt.savefig('../quantization_resolution.pdf', bbox_inches='tight')
    plt.close()
    print("  [OK] quantization_resolution.pdf")


if __name__ == '__main__':
    print("Gerando figuras de quantização...")
    gen_quantization_illustration()
    gen_quantization_error_pdf()
    gen_sqnr_vs_bits()
    gen_quantization_resolution()
    print("Concluído!\n")
