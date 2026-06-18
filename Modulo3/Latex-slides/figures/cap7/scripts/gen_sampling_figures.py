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
def _time_domain_data():
    t = np.linspace(0, 0.5, 8000)
    g = 0.8 * np.cos(2*np.pi*7*t) + 0.45 * np.cos(2*np.pi*12*t)

    fs = 30          # Hz  (f_s > 2*12 = 24 Hz)
    Ts = 1 / fs
    t_n = np.arange(0, 0.5 + Ts/2, Ts)
    g_n = 0.8 * np.cos(2*np.pi*7*t_n) + 0.45 * np.cos(2*np.pi*12*t_n)
    return t, g, fs, Ts, t_n, g_n


def _plot_original(ax, t, g):
    ax.plot(t, g, color=UNB_BLUE, linewidth=2)
    ax.set_ylabel(r'$g(t)$', fontsize=13)
    ax.set_title(r'(a) Sinal original $g(t)$  —  contínuo no tempo', fontweight='bold')
    ax.set_xlim([0, 0.5])


def _plot_impulse_train(ax, fs, Ts, t_n):
    for ti in t_n:
        ax.annotate('', xy=(ti, 1.0), xytext=(ti, 0),
                    arrowprops=dict(arrowstyle='->', color=UNB_GOLD, lw=2.5))
    ax.set_ylabel(r'$\delta_{T_s}(t)$', fontsize=13)
    ax.set_title(rf'(b) Trem de impulsos  ($T_s = {Ts*1000:.1f}$ ms,  $f_s = {fs}$ Hz)',
                 fontweight='bold')
    ax.set_xlim([0, 0.5])
    ax.set_ylim([0, 1.6])


def _plot_sampled(ax, t, g, fs, t_n, g_n):
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


def gen_sampling_time_domain():
    # ---- Versão combinada (3 painéis) — mantida por compatibilidade ----
    t, g, fs, Ts, t_n, g_n = _time_domain_data()
    fig, axes = plt.subplots(3, 1, figsize=(8, 7))
    _plot_original(axes[0], t, g);         axes[0].tick_params(labelbottom=False)
    _plot_impulse_train(axes[1], fs, Ts, t_n); axes[1].tick_params(labelbottom=False)
    _plot_sampled(axes[2], t, g, fs, t_n, g_n)
    plt.tight_layout()
    plt.savefig('../sampling_time_domain.pdf', bbox_inches='tight')
    plt.close()
    print("  [OK] sampling_time_domain.pdf")

    # ---- Versão dividida: (a)+(b) em um slide ----
    t, g, fs, Ts, t_n, g_n = _time_domain_data()
    fig, axes = plt.subplots(2, 1, figsize=(8, 4.8))
    _plot_original(axes[0], t, g);             axes[0].tick_params(labelbottom=False)
    _plot_impulse_train(axes[1], fs, Ts, t_n); axes[1].set_xlabel('Tempo (s)', fontsize=12)
    plt.tight_layout()
    plt.savefig('../sampling_time_domain_ab.pdf', bbox_inches='tight')
    plt.close()
    print("  [OK] sampling_time_domain_ab.pdf")

    # ---- Versão dividida: (c) em outro slide ----
    t, g, fs, Ts, t_n, g_n = _time_domain_data()
    fig, ax = plt.subplots(1, 1, figsize=(8, 3.6))
    _plot_sampled(ax, t, g, fs, t_n, g_n)
    plt.tight_layout()
    plt.savefig('../sampling_time_domain_c.pdf', bbox_inches='tight')
    plt.close()
    print("  [OK] sampling_time_domain_c.pdf")


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


def gen_sinc_interpolation():
    Ts = 1.0
    n = np.arange(-1, 8)
    def sig(t):
        return 0.7*np.sin(2*np.pi*0.11*t) + 0.4*np.sin(2*np.pi*0.06*t + 1.0)
    samples = sig(n*Ts)
    t = np.linspace(-1, 7, 2500)
    recon = np.zeros_like(t)

    fig, ax = plt.subplots(figsize=(9, 3.3))
    for ni, sval in zip(n, samples):
        s = sval*np.sinc((t - ni*Ts)/Ts)
        ax.plot(t, s, color=UNB_GOLD, linewidth=0.9, alpha=0.55)
        recon += s
    ax.plot(t, recon, color=UNB_BLUE, linewidth=2.3,
            label=r'reconstrução = soma dos sincs')
    ax.vlines(n*Ts, 0, samples, color=UNB_GREEN, linewidth=1.0, alpha=0.5)
    ax.plot(n*Ts, samples, 'o', color=UNB_GREEN, markersize=7,
            label=r'amostras $g(nT_s)$', zorder=5)
    ax.axhline(0, color='black', linewidth=0.5)
    ax.set_xlim(-1, 7)
    ax.set_ylim(-1.2, 1.25)
    ax.set_xlabel(r'tempo ($t / T_s$)')
    # rotular um sinc individual
    ax.annotate(r'um $\mathrm{sinc}$ por amostra',
                xy=(2.0, 0.62), xytext=(3.5, 1.0),
                fontsize=9, color=UNB_GOLD, ha='center',
                arrowprops=dict(arrowstyle='->', color=UNB_GOLD, lw=1.3))
    ax.legend(loc='lower center', fontsize=9, ncol=2)
    plt.tight_layout()
    plt.savefig('../sinc_interpolation.pdf', bbox_inches='tight')
    plt.close()
    print("  [OK] sinc_interpolation.pdf")


def gen_zoh_effect():
    Ts = 1.0
    n = np.arange(0, 8)

    def sig(t):
        return 0.6*np.sin(2*np.pi*0.10*t) + 0.35*np.sin(2*np.pi*0.17*t + 0.5)

    samples = sig(n*Ts)
    t = np.linspace(0, 7, 2000)

    fig, axes = plt.subplots(1, 2, figsize=(10, 3.2))

    # (a) tempo: saída em escada (ZOH)
    ax = axes[0]
    ax.plot(t, sig(t), color=UNB_BLUE, linewidth=2.0, label='sinal original')
    ne = np.append(n, n[-1] + 1) * Ts
    se = np.append(samples, samples[-1])
    ax.step(ne, se, where='post', color=UNB_GREEN, linewidth=1.9,
            label='saída ZOH (escada)')
    ax.plot(n*Ts, samples, 'o', color=UNB_GREEN, markersize=6)
    ax.axhline(0, color='black', linewidth=0.5)
    ax.set_title('(a) Saída do DAC: escada (ZOH)', fontsize=11, fontweight='bold')
    ax.set_xlabel(r'tempo ($t/T_s$)')
    ax.set_xlim(0, 7)
    ax.legend(fontsize=8, loc='upper right')

    # (b) frequência: envelope sinc(f Ts)
    ax = axes[1]
    f = np.linspace(0.001, 2.5, 1200)            # f * Ts
    HdB = 20*np.log10(np.abs(np.sinc(f)))
    ax.plot(f, HdB, color=UNB_GOLD, linewidth=2.3)
    edge_dB = 20*np.log10(2/np.pi)
    ax.axvline(0.5, color='gray', linestyle='--', linewidth=1)
    ax.plot(0.5, edge_dB, 'o', color=RED, markersize=6)
    ax.annotate(r'$-3{,}9$ dB em $f=f_s/2$',
                xy=(0.5, edge_dB), xytext=(0.78, -7.5),
                fontsize=9, color=RED,
                arrowprops=dict(arrowstyle='->', color=RED, lw=1.2))
    ax.set_title(r'(b) Envelope $|H_{ZOH}|=|\mathrm{sinc}(fT_s)|$',
                 fontsize=11, fontweight='bold')
    ax.set_xlabel(r'$f \cdot T_s$')
    ax.set_ylabel('dB')
    ax.set_xlim(0, 2.5)
    ax.set_ylim(-25, 2)

    plt.tight_layout()
    plt.savefig('../zoh_effect.pdf', bbox_inches='tight')
    plt.close()
    print("  [OK] zoh_effect.pdf")


def gen_zoh_equalization():
    # frequência normalizada à borda da banda fs/2  (borda = 1)
    x = np.linspace(0.001, 1.0, 700)
    fTs = 0.5 * x                                  # f*Ts, com fs = 2W
    droop = 20*np.log10(np.abs(np.sinc(fTs)))      # ZOH
    eq = -droop                                    # equalizador 1/sinc
    prod = np.zeros_like(x)                         # produto (plano)

    fig, ax = plt.subplots(figsize=(8.5, 3.1))
    ax.plot(x, droop, color=UNB_GREEN, linewidth=2.3,
            label=r'ZOH: $\mathrm{sinc}(fT_s)$')
    ax.plot(x, eq, color=RED, linewidth=2.3, linestyle='--',
            label=r'equalizador: $1/\mathrm{sinc}(fT_s)$')
    ax.plot(x, prod, color=UNB_BLUE, linewidth=2.6,
            label='produto (plano)')
    ax.axhline(0, color='black', linewidth=0.4)
    ax.annotate(r'$+3{,}9$ dB', xy=(1.0, 3.92), xytext=(0.66, 3.1),
                fontsize=9, color=RED)
    ax.annotate(r'$-3{,}9$ dB', xy=(1.0, -3.92), xytext=(0.66, -3.4),
                fontsize=9, color=UNB_GREEN)
    ax.set_xlabel(r'frequência normalizada  $f/(f_s/2)$')
    ax.set_ylabel('ganho (dB)')
    ax.set_xlim(0, 1)
    ax.set_ylim(-4.6, 4.6)
    ax.legend(fontsize=9, loc='upper left', framealpha=0.9)
    plt.tight_layout()
    plt.savefig('../zoh_equalization.pdf', bbox_inches='tight')
    plt.close()
    print("  [OK] zoh_equalization.pdf")


def gen_zoh_spectrum():
    # frequência em unidades de fs (fs = 1, Ts = 1)
    f = np.linspace(-2.6, 2.6, 6000)
    W = 0.32                                   # meia-banda em unidades de fs

    def tri(fc):
        return np.clip(1 - np.abs(f - fc)/W, 0, None)

    Gs = sum(tri(c) for c in (-2, -1, 0, 1, 2))   # espectro amostrado (réplicas)
    Hz = np.abs(np.sinc(f))                        # |sinc(f Ts)|, nulos em k fs
    out = Gs * Hz                                  # saída do ZOH

    fig, ax = plt.subplots(figsize=(9.2, 3.3))
    ax.fill_between(f, 0, Gs, color='gray', alpha=0.20,
                    label=r'espectro amostrado $|G_s(f)|$ (réplicas)')
    ax.plot(f, Gs, color='gray', linewidth=0.8, alpha=0.5)
    ax.plot(f, Hz, color=UNB_GOLD, linewidth=2.3,
            label=r'$|H_{ZOH}(f)| = |\mathrm{sinc}(fT_s)|$')
    ax.fill_between(f, 0, out, color=UNB_BLUE, alpha=0.55,
                    label='saída $= |G_s(f)|\\cdot|H_{ZOH}|$')
    ax.plot(f, out, color=UNB_BLUE, linewidth=1.4)
    for k in (-2, -1, 1, 2):
        ax.axvline(k, color='gray', linestyle=':', linewidth=0.8, alpha=0.5)
    ax.set_xticks([-2, -1, 0, 1, 2])
    ax.set_xticklabels([r'$-2f_s$', r'$-f_s$', r'$0$', r'$f_s$', r'$2f_s$'])
    ax.set_xlabel('frequência')
    ax.set_xlim(-2.6, 2.6)
    ax.set_ylim(0, 1.18)
    ax.legend(fontsize=8, loc='upper right')
    plt.tight_layout()
    plt.savefig('../zoh_spectrum.pdf', bbox_inches='tight')
    plt.close()
    print("  [OK] zoh_spectrum.pdf")


def gen_aa_filter_order():
    W = 1.0

    def tri(f, c):
        return np.clip(1 - np.abs(f - c)/W, 0, None)

    def butter(f, fc, N):
        return 1.0/np.sqrt(1 + (np.abs(f)/fc)**(2*N))

    # (a) fs grande -> transição larga -> ordem baixa
    # (b) fs pequeno -> transição estreita -> ordem alta
    configs = [(4.0, 5, '(a) $f_s$ grande: transição larga'),
               (2.5, 12, '(b) $f_s$ pequeno: transição estreita')]

    fig, axes = plt.subplots(1, 2, figsize=(10, 3.4), sharey=True)
    for ax, (fs, N, title) in zip(axes, configs):
        f = np.linspace(-0.3, fs + W + 0.4, 4000)
        base = tri(f, 0)
        rep = tri(f, fs)
        ax.fill_between(f, 0, base, color=UNB_GOLD, alpha=0.30)
        ax.plot(f, base, color=UNB_GOLD, linewidth=1.4)
        ax.fill_between(f, 0, rep, color=UNB_GREEN, alpha=0.22)
        ax.plot(f, rep, color=UNB_GREEN, linewidth=1.4)
        # filtro anti-aliasing (Butterworth, corte W, ordem N)
        ax.plot(f, butter(f, W, N), color=RED, linewidth=2.0, linestyle='--',
                label=f'filtro ($N={N}$)')
        # banda de transição [W, fs-W]
        ax.axvspan(W, fs - W, color='gray', alpha=0.13)
        ax.annotate('', xy=(W, 1.12), xytext=(fs - W, 1.12),
                    arrowprops=dict(arrowstyle='<->', color='black', lw=1.1))
        ax.text((fs)/2, 1.18, 'transição', ha='center', fontsize=8.5)
        ax.set_title(title, fontsize=10.5, fontweight='bold')
        ax.set_xticks([0, W, fs - W, fs])
        ax.set_xticklabels(['0', r'$W$', r'$f_s\!-\!W$', r'$f_s$'], fontsize=9)
        ax.set_xlabel('frequência')
        ax.set_ylim(0, 1.35)
        ax.legend(fontsize=9, loc='center right')
    plt.tight_layout()
    plt.savefig('../aa_filter_order.pdf', bbox_inches='tight')
    plt.close()
    print("  [OK] aa_filter_order.pdf")


def gen_zoh_passband():
    W = 1.0
    fs = 2.0                                   # fs = 2W
    f = np.linspace(0, W, 900)
    ideal = np.ones_like(f)
    sincf = np.abs(np.sinc(f/fs))              # |sinc(f Ts)|, Ts = 1/fs

    fig, ax = plt.subplots(figsize=(8, 3.1))
    ax.fill_between(f, sincf, ideal, color=RED, alpha=0.16, label='deformação')
    ax.fill_between(f, 0, sincf, color=UNB_GREEN, alpha=0.28)
    ax.plot(f, ideal, color=UNB_BLUE, linewidth=1.8, linestyle=':',
            label=r'$|G(f)|$ desejado (plano)')
    ax.plot(f, sincf, color=UNB_GREEN, linewidth=2.4,
            label=r'após ZOH: $|G(f)|\,\mathrm{sinc}(fT_s)$')
    ax.plot(W, sincf[-1], 'o', color=RED, markersize=6)
    ax.annotate(r'$2/\pi \approx -3{,}9$ dB', xy=(W, sincf[-1]),
                xytext=(0.42, 0.50), color=RED, fontsize=10,
                arrowprops=dict(arrowstyle='->', color=RED, lw=1.2))
    ax.set_xticks([0, W])
    ax.set_xticklabels(['0', r'$W$'])
    ax.set_xlabel('frequência (banda útil)')
    ax.set_xlim(0, W)
    ax.set_ylim(0, 1.15)
    ax.legend(fontsize=9, loc='lower left')
    plt.tight_layout()
    plt.savefig('../zoh_passband.pdf', bbox_inches='tight')
    plt.close()
    print("  [OK] zoh_passband.pdf")


if __name__ == '__main__':
    print("Gerando figuras de amostragem...")
    gen_sampling_time_domain()
    gen_sinc_interpolation()
    gen_zoh_effect()
    gen_zoh_equalization()
    gen_zoh_spectrum()
    gen_aa_filter_order()
    gen_zoh_passband()
    gen_sampling_spectrum()
    gen_aliasing_demo()
    print("Concluído!\n")
