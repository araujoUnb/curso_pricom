#!/usr/bin/env python3
"""
Gera figuras de amostragem para os slides de Conversão Analógico-Digital.
Saída: ../sampling_time_domain.pdf, ../sampling_spectrum.pdf, ../aliasing_demo.pdf

Uso: python gen_sampling_figures.py
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

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

# ===========================================================================
# Figura 1: Amostragem no Domínio do Tempo
# ===========================================================================
def gen_sampling_time_domain():
    fig, axes = plt.subplots(3, 1, figsize=(8, 7))

    t = np.linspace(0, 0.5, 8000)
    g = 0.8 * np.cos(2*np.pi*7*t) + 0.45 * np.cos(2*np.pi*12*t)

    fs = 30          # Hz  (f_s > 2*12 = 24 Hz)
    Ts = 1 / fs
    t_n = np.arange(0, 0.5 + Ts/2, Ts)
    g_n = 0.8 * np.cos(2*np.pi*7*t_n) + 0.45 * np.cos(2*np.pi*12*t_n)

    # ---- Sinal original ----
    ax = axes[0]
    ax.plot(t, g, color=UNB_BLUE, linewidth=2)
    ax.set_ylabel(r'$g(t)$', fontsize=13)
    ax.set_title(r'(a) Sinal original $g(t)$  —  contínuo no tempo', fontweight='bold')
    ax.set_xlim([0, 0.5])
    ax.tick_params(labelbottom=False)

    # ---- Trem de impulsos ----
    ax = axes[1]
    for ti in t_n:
        ax.annotate('', xy=(ti, 1.0), xytext=(ti, 0),
                    arrowprops=dict(arrowstyle='->', color=UNB_GOLD, lw=2.5))
    ax.set_ylabel(r'$\delta_{T_s}(t)$', fontsize=13)
    ax.set_title(rf'(b) Trem de impulsos  ($T_s = {Ts*1000:.1f}$ ms,  $f_s = {fs}$ Hz)',
                 fontweight='bold')
    ax.set_xlim([0, 0.5])
    ax.set_ylim([0, 1.6])
    ax.tick_params(labelbottom=False)

    # ---- Sinal amostrado ----
    ax = axes[2]
    ax.plot(t, g, color=UNB_BLUE, linewidth=1, alpha=0.25, linestyle='--',
            label=r'$g(t)$ original')
    ml, sl, bl = ax.stem(t_n, g_n,
                         linefmt=UNB_GREEN, markerfmt='o', basefmt='k-',
                         label=r'$g_s(t) = g(t)\cdot\delta_{T_s}(t)$')
    plt.setp(sl, linewidth=2.0, color=UNB_GREEN)
    plt.setp(ml, color=UNB_GREEN, markersize=7)
    plt.setp(bl, linewidth=1, color='black')
    ax.set_ylabel(r'$g_s(t)$', fontsize=13)
    ax.set_xlabel('Tempo (s)', fontsize=12)
    ax.set_title(rf'(c) Sinal amostrado $g_s(t)$  ($f_s = {fs}$ Hz $> 2W$)',
                 fontweight='bold')
    ax.legend(fontsize=9, loc='upper right')
    ax.set_xlim([0, 0.5])

    plt.tight_layout()
    plt.savefig('../sampling_time_domain.pdf', bbox_inches='tight')
    plt.close()
    print("  [OK] sampling_time_domain.pdf")


# ===========================================================================
# Figura 2: Espectro — com e sem aliasing
# ===========================================================================
def gen_sampling_spectrum():

    def triangle(f, fc, W, amp=1.0):
        return amp * np.maximum(0.0, 1.0 - np.abs(f - fc) / W)

    W       = 2000   # Hz — largura de banda do sinal
    fs_ok   = 6000   # Hz — f_s > 2W (sem aliasing)
    fs_bad  = 3000   # Hz — f_s < 2W (com aliasing)
    f_max   = 1.2 * fs_ok
    f       = np.linspace(-f_max, f_max, 20000)

    fig, axes = plt.subplots(2, 1, figsize=(9, 6), sharey=True)

    # ---- Caso SEM aliasing ----
    ax = axes[0]
    palette = [UNB_BLUE, UNB_GREEN, UNB_GOLD, UNB_GREEN, UNB_BLUE]
    labels  = [r'$n=-2$', r'$n=-1$', r'$n=0$ (original)', r'$n=1$', r'$n=2$']
    for i, k in enumerate([-2, -1, 0, 1, 2]):
        y = triangle(f, k * fs_ok, W)
        ax.fill_between(f, 0, y, alpha=0.35, color=palette[i])
        ax.plot(f, y, color=palette[i], linewidth=2,
                label=labels[i] if k in [-1, 0, 1] else '_nolegend_')
    ax.axvline(-W,   color=RED, linestyle='--', linewidth=1.8,
               label=rf'$\pm W = \pm{W//1000}$ kHz')
    ax.axvline( W,   color=RED, linestyle='--', linewidth=1.8)
    ax.axvline(-fs_ok, color='gray', linestyle=':', linewidth=1)
    ax.axvline( fs_ok, color='gray', linestyle=':', linewidth=1)
    ax.set_title(
        rf'(a) Sem aliasing: $f_s = {fs_ok//1000}$ kHz $> 2W = {2*W//1000}$ kHz',
        fontweight='bold')
    ax.set_ylabel(r'$|G_s(f)|$', fontsize=13)
    ax.legend(fontsize=9, ncol=5, loc='upper center')
    ax.set_xlim([-f_max, f_max])
    ax.set_ylim([0, 1.5])
    ax.set_xticks([-fs_ok, -W, 0, W, fs_ok])
    ax.set_xticklabels([r'$-f_s$', r'$-W$', r'$0$', r'$W$', r'$f_s$'],
                       fontsize=12)
    ax.tick_params(labelbottom=False)

    # ---- Caso COM aliasing ----
    ax = axes[1]
    for i, k in enumerate([-1, 0, 1]):
        y = triangle(f, k * fs_bad, W)
        ax.fill_between(f, 0, y, alpha=0.30, color=palette[i+1])
        ax.plot(f, y, color=palette[i+1], linewidth=2)

    # Região de sobreposição (aliasing)
    f_ov_p = np.linspace(fs_bad - W, W, 2000)
    y1 = triangle(f_ov_p, 0,      W)
    y2 = triangle(f_ov_p, fs_bad, W)
    ax.fill_between(f_ov_p, 0, np.minimum(y1, y2),
                    alpha=0.85, color=RED, label='Aliasing (sobreposição)')
    f_ov_n = np.linspace(-W, -(fs_bad - W), 2000)
    y1n = triangle(f_ov_n, 0,       W)
    y2n = triangle(f_ov_n, -fs_bad, W)
    ax.fill_between(f_ov_n, 0, np.minimum(y1n, y2n),
                    alpha=0.85, color=RED)

    ax.axvline(-W,    color=RED, linestyle='--', linewidth=1.8,
               label=rf'$\pm W = \pm{W//1000}$ kHz')
    ax.axvline( W,    color=RED, linestyle='--', linewidth=1.8)
    ax.axvline(-fs_bad, color='gray', linestyle=':', linewidth=1)
    ax.axvline( fs_bad, color='gray', linestyle=':', linewidth=1)
    ax.set_title(
        rf'(b) Com aliasing: $f_s = {fs_bad//1000}$ kHz $< 2W = {2*W//1000}$ kHz',
        fontweight='bold')
    ax.set_ylabel(r'$|G_s(f)|$', fontsize=13)
    ax.set_xlabel('Frequência (Hz)', fontsize=12)
    ax.legend(fontsize=9, ncol=3, loc='upper center')
    ax.set_xlim([-f_max, f_max])
    ax.set_ylim([0, 1.5])
    ax.set_xticks([-fs_ok, -fs_bad, -W, 0, W, fs_bad, fs_ok])
    ax.set_xticklabels(
        [r'$-2f_s$', r'$-f_s$', r'$-W$', r'$0$', r'$W$', r'$f_s$', r'$2f_s$'],
        fontsize=11)

    plt.tight_layout()
    plt.savefig('../sampling_spectrum.pdf', bbox_inches='tight')
    plt.close()
    print("  [OK] sampling_spectrum.pdf")


# ===========================================================================
# Figura 3: Aliasing — demonstração numérica
# ===========================================================================
def gen_aliasing_demo():
    f_sig  = 800    # Hz — frequência do sinal
    t_fine = np.linspace(0, 0.012, 6000)
    g_true = np.cos(2*np.pi * f_sig * t_fine)

    fs_good = 2500                       # Hz — amostragem adequada
    t_good  = np.arange(0, 0.012, 1/fs_good)
    g_good  = np.cos(2*np.pi * f_sig * t_good)

    fs_bad  = 900                        # Hz — subamostragem
    t_bad   = np.arange(0, 0.012, 1/fs_bad)
    g_bad   = np.cos(2*np.pi * f_sig * t_bad)

    f_alias  = abs(f_sig - fs_bad)       # 800 - 900 = |-100| = 100 Hz
    g_alias  = np.cos(2*np.pi * f_alias * t_fine)

    fig, axes = plt.subplots(2, 1, figsize=(9, 5.5))

    # ---- Caso adequado ----
    ax = axes[0]
    ax.plot(t_fine*1000, g_true, color=UNB_BLUE, lw=1.5, alpha=0.45,
            label=rf'$g(t) = \cos(2\pi\cdot{f_sig}\,t)$')
    ml, sl, bl = ax.stem(t_good*1000, g_good,
                         linefmt=UNB_GREEN, markerfmt='o', basefmt='k-')
    plt.setp(sl, lw=2.0, color=UNB_GREEN)
    plt.setp(ml, color=UNB_GREEN, ms=7)
    plt.setp(bl, lw=1, color='k')
    ax.set_title(
        rf'(a) Amostragem adequada: $f_s={fs_good}$ Hz $> 2\cdot{f_sig}={2*f_sig}$ Hz',
        fontweight='bold')
    ax.set_ylabel('Amplitude', fontsize=12)
    ax.legend(fontsize=10)
    ax.set_xlim([0, 12])
    ax.tick_params(labelbottom=False)

    # ---- Subamostragem ----
    ax = axes[1]
    ax.plot(t_fine*1000, g_true, color=UNB_BLUE, lw=1.5, alpha=0.35,
            label=rf'$g(t) = \cos(2\pi\cdot{f_sig}\,t)$')
    ax.plot(t_fine*1000, g_alias, color=RED, lw=2.5, ls='--',
            label=rf'Alias $= \cos(2\pi\cdot{f_alias}\,t)$  ← frequência errada!')
    ml, sl, bl = ax.stem(t_bad*1000, g_bad,
                         linefmt=UNB_GOLD, markerfmt='o', basefmt='k-')
    plt.setp(sl, lw=2.0, color=UNB_GOLD)
    plt.setp(ml, color=UNB_GOLD, ms=7)
    plt.setp(bl, lw=1, color='k')
    ax.set_title(
        rf'(b) Subamostragem: $f_s={fs_bad}$ Hz $< 2\cdot{f_sig}={2*f_sig}$ Hz  →  Alias em {f_alias} Hz!',
        fontweight='bold')
    ax.set_ylabel('Amplitude', fontsize=12)
    ax.set_xlabel('Tempo (ms)', fontsize=12)
    ax.legend(fontsize=10)
    ax.set_xlim([0, 12])

    plt.tight_layout()
    plt.savefig('../aliasing_demo.pdf', bbox_inches='tight')
    plt.close()
    print("  [OK] aliasing_demo.pdf")


if __name__ == '__main__':
    print("Gerando figuras de amostragem...")
    gen_sampling_time_domain()
    gen_sampling_spectrum()
    gen_aliasing_demo()
    print("Concluído!\n")
