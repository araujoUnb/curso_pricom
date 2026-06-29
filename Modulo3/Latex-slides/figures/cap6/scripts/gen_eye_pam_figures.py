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


def _build_eye_signal(seed=7, alpha=0.5, sps=100, N=16, noise=0.0):
    np.random.seed(seed)
    T = 1.0
    bits = 2 * np.random.randint(0, 2, N) - 1
    t_pulse = np.arange(-6*sps, 6*sps + 1) / sps * T
    pulse = raised_cosine_time(t_pulse, T, alpha)
    sig = np.zeros(N * sps + len(t_pulse))
    for i, b in enumerate(bits):
        sig[i*sps:i*sps + len(t_pulse)] += b * pulse
    if noise > 0:
        sig = sig + noise * np.random.randn(len(sig))
    return sig, sps


def gen_eye_construction():
    """Mostra a construcao do diagrama de olho em 4 etapas (overlay):
    1) sinal r(t); 2) cortes a cada 2T; 3) poucos trechos sobrepostos;
    4) muitos trechos -> o olho. Gera eye_build_{1..4}."""
    sig, sps = _build_eye_signal(seed=7, alpha=0.5, N=16, noise=0.0)
    seg = 2 * sps
    t_eye = np.linspace(0, 2, seg)
    kmin, kmax = 3, 13              # trechos "limpos" (longe das bordas)
    colors = [UNB_BLUE, UNB_GREEN, UNB_GOLD, RED, PURPLE, '#16A085']

    # ---- etapas 1 e 2: r(t) ao longo do tempo ----
    def plot_rt(cuts):
        fig, ax = plt.subplots(figsize=(8.8, 3.4))
        idx0, idx1 = kmin*sps, (kmax + 1)*sps
        tt = np.arange(idx0, idx1) / sps
        ax.plot(tt, sig[idx0:idx1], color=UNB_BLUE, lw=1.8)
        ax.set_xlim([kmin, kmax + 1])
        ax.set_ylim([-1.6, 1.6])
        ax.axhline(0, color='black', lw=0.5)
        ax.set_xlabel(r'Tempo ($t/T$)', fontsize=12)
        ax.set_ylabel('Amplitude', fontsize=12)
        if cuts:
            for j, k in enumerate(range(kmin, kmax + 1, 2)):
                ax.axvline(k, color=RED, lw=1.2, ls='--')
                ax.axvspan(k, k + 2, color=colors[j % len(colors)], alpha=0.10)
            ax.set_title(r'Passo 2: cortar em trechos de $2T$',
                         fontweight='bold')
        else:
            ax.set_title(r'Passo 1: sinal recebido $r(t)$', fontweight='bold')
        return fig

    fig = plot_rt(False)
    plt.tight_layout(); plt.savefig('../eye_build_1.pdf', bbox_inches='tight'); plt.close()
    fig = plot_rt(True)
    plt.tight_layout(); plt.savefig('../eye_build_2.pdf', bbox_inches='tight'); plt.close()

    # ---- etapas 3 e 4: sobreposicao dos trechos ----
    def plot_eye(ntraces, colored, title):
        fig, ax = plt.subplots(figsize=(8.8, 3.4))
        ks = list(range(kmin, kmin + ntraces))
        for j, k in enumerate(ks):
            s = k * sps          # centra a abertura em t/T = 1
            e = s + seg
            if e <= len(sig):
                if colored:
                    ax.plot(t_eye, sig[s:e], color=colors[j % len(colors)],
                            lw=1.6, alpha=0.9)
                else:
                    ax.plot(t_eye, sig[s:e], color=UNB_BLUE, lw=0.6, alpha=0.45)
        ax.set_xlim([0, 2])
        ax.set_ylim([-1.6, 1.6])
        ax.axhline(0, color='black', lw=0.5)
        ax.axvline(1.0, color=RED, lw=1.3, ls='--', alpha=0.7,
                   label='instante ótimo')
        ax.set_xlabel(r'Tempo ($t/T$)', fontsize=12)
        ax.set_ylabel('Amplitude', fontsize=12)
        ax.set_title(title, fontweight='bold')
        ax.legend(fontsize=9, loc='upper right')
        return fig

    fig = plot_eye(6, True, r'Passo 3: sobrepor os trechos (poucos)')
    plt.tight_layout(); plt.savefig('../eye_build_3.pdf', bbox_inches='tight'); plt.close()
    sig2, sps2 = _build_eye_signal(seed=7, alpha=0.5, N=160, noise=0.02)
    # reusar plot_eye com muitos tracos do sinal longo
    fig, ax = plt.subplots(figsize=(8.8, 3.4))
    for k in range(3, 150):
        s = k * sps2            # centra a abertura em t/T = 1
        e = s + 2 * sps2
        if e <= len(sig2):
            ax.plot(np.linspace(0, 2, 2*sps2), sig2[s:e],
                    color=UNB_BLUE, lw=0.4, alpha=0.35)
    ax.set_xlim([0, 2]); ax.set_ylim([-1.6, 1.6])
    ax.axhline(0, color='black', lw=0.5)
    ax.axvline(1.0, color=RED, lw=1.3, ls='--', alpha=0.7, label='instante ótimo')
    ax.set_xlabel(r'Tempo ($t/T$)', fontsize=12)
    ax.set_ylabel('Amplitude', fontsize=12)
    ax.set_title(r'Resultado: o ``olho'' formado', fontweight='bold')
    ax.legend(fontsize=9, loc='upper right')
    plt.tight_layout(); plt.savefig('../eye_build_4.pdf', bbox_inches='tight'); plt.close()
    print("  [OK] eye_build_1..4.pdf")


def gen_eye_overlay_build():
    """Animação trecho a trecho: cada passo destaca um trecho de 2T no sinal
    r(t) (painel de cima) e o acrescenta, na mesma cor, ao diagrama de olho
    (painel de baixo). Gera eye_overlay_{1..7}.pdf  (6 trechos + olho cheio)."""
    sig, sps = _build_eye_signal(seed=7, alpha=0.5, N=16, noise=0.0)
    seg = 2 * sps
    t_eye = np.linspace(0, 2, seg)
    starts = list(range(3, 15, 2))            # inícios dos trechos: 3,5,7,9,11,13
    colors = [UNB_BLUE, UNB_GREEN, UNB_GOLD, RED, PURPLE, TEAL]
    nseg = len(starts)
    t0, t1 = starts[0], starts[-1] + 2        # janela de tempo exibida em cima

    # sinal "longo" para o passo final (muitos trechos -> olho cheio)
    sig_long, sps_long = _build_eye_signal(seed=7, alpha=0.5, N=160, noise=0.02)

    def desenhar(step):
        fig, (ax_t, ax_e) = plt.subplots(
            2, 1, figsize=(8.8, 5.4),
            gridspec_kw={'height_ratios': [1.0, 1.05]})
        n_done = min(step, nseg)              # quantos trechos já entraram

        # ---------- painel de cima: r(t) com o trecho atual destacado ----------
        i0, i1 = int(t0 * sps), int(t1 * sps)
        tt = np.arange(i0, i1) / sps
        ax_t.plot(tt, sig[i0:i1], color='0.6', lw=1.2)          # sinal de fundo
        for j in range(n_done):
            k = starts[j]
            ax_t.axvspan(k, k + 2, color=colors[j], alpha=0.12)  # faixa do trecho
        if step <= nseg:                       # destaca o trecho que entra agora
            k = starts[step - 1]
            si, ei = int(k * sps), int((k + 2) * sps)
            ax_t.plot(np.arange(si, ei) / sps, sig[si:ei],
                      color=colors[step - 1], lw=2.6)
            ax_t.axvspan(k, k + 2, color=colors[step - 1], alpha=0.22)
        ax_t.set_xlim([t0, t1]); ax_t.set_ylim([-1.6, 1.6])
        ax_t.axhline(0, color='black', lw=0.5)
        ax_t.set_xlabel(r'Tempo ($t/T$)', fontsize=11)
        ax_t.set_ylabel('Amplitude', fontsize=11)
        ax_t.set_title(r'Sinal $r(t)$ — trecho de $2T$ selecionado',
                       fontweight='bold')

        # ---------- painel de baixo: diagrama de olho acumulando ----------
        if step > nseg:                        # passo final: muitos trechos
            for k in range(3, 150):
                s = k * sps_long
                e = s + 2 * sps_long
                if e <= len(sig_long):
                    ax_e.plot(np.linspace(0, 2, 2 * sps_long), sig_long[s:e],
                              color=UNB_BLUE, lw=0.4, alpha=0.30)
            ax_e.set_title(r'Muitos trechos sobrepostos $\rightarrow$ o ``olho''',
                           fontweight='bold')
        else:
            for j in range(n_done):
                k = starts[j]
                si = int(k * sps); ei = si + seg
                lw = 2.6 if j == step - 1 else 1.6
                al = 1.0 if j == step - 1 else 0.85
                ax_e.plot(t_eye, sig[si:ei], color=colors[j], lw=lw, alpha=al)
            ax_e.set_title(r'Diagrama de olho: %d trecho(s) sobreposto(s)'
                           % n_done, fontweight='bold')
        ax_e.set_xlim([0, 2]); ax_e.set_ylim([-1.6, 1.6])
        ax_e.axhline(0, color='black', lw=0.5)
        ax_e.axvline(1.0, color=RED, lw=1.3, ls='--', alpha=0.7,
                     label='instante ótimo')
        ax_e.set_xlabel(r'Tempo ($t/T$)', fontsize=11)
        ax_e.set_ylabel('Amplitude', fontsize=11)
        ax_e.legend(fontsize=9, loc='upper right')

        plt.tight_layout()
        plt.savefig('../eye_overlay_%d.pdf' % step, bbox_inches='tight')
        plt.close()

    for step in range(1, nseg + 2):            # 1..6 trechos + passo 7 (olho)
        desenhar(step)
    print("  [OK] eye_overlay_1..%d.pdf" % (nseg + 1))


def gen_eye_analise_base():
    """Olho cheio SEM eixos nem margens, para receber anotações TikZ por cima
    nos slides (mapeamento exato: t/T em [0,2] -> x em [0,1], amplitude em
    [-1.5,1.5] -> y em [0,1]). Gera eye_analise_base.pdf."""
    sig, sps = _build_eye_signal(seed=7, alpha=0.5, N=160, noise=0.05)
    seg = 2 * sps
    t_eye = np.linspace(0, 2, seg)
    fig = plt.figure(figsize=(7.2, 4.2))
    ax = fig.add_axes([0, 0, 1, 1])        # eixo preenche toda a figura
    ax.set_axis_off()
    ax.set_xlim(0, 2); ax.set_ylim(-1.5, 1.5)
    for k in range(3, 150):
        s = k * sps             # centra a abertura em t/T = 1
        e = s + seg
        if e <= len(sig):
            ax.plot(t_eye, sig[s:e], color=UNB_BLUE, lw=0.5, alpha=0.32)
    fig.savefig('../eye_analise_base.pdf')  # sem bbox_inches: preserva o mapa
    plt.close()
    print("  [OK] eye_analise_base.pdf")


def gen_eye_reading():
    """Anota o diagrama de olho com cada caracteristica de leitura, de forma
    cumulativa (overlay): abertura vertical, horizontal, espessura e
    cruzamentos. Gera eye_read_{1..4}."""
    sig, sps = _build_eye_signal(seed=7, alpha=0.5, N=160, noise=0.06)
    seg = 2 * sps
    t_eye = np.linspace(0, 2, seg)

    def base_eye(ax):
        for k in range(3, 150):
            s = k * sps          # centra a abertura em t/T = 1
            e = s + seg
            if e <= len(sig):
                ax.plot(t_eye, sig[s:e], color=UNB_BLUE, lw=0.4, alpha=0.30)
        ax.set_xlim([0, 2]); ax.set_ylim([-1.7, 1.7])
        ax.axhline(0, color='black', lw=0.5)
        ax.set_xlabel(r'Tempo ($t/T$)', fontsize=12)
        ax.set_ylabel('Amplitude', fontsize=12)

    feats = [
        ('vert',  r'Leitura: abertura vertical'),
        ('horiz', r'Leitura: + abertura horizontal'),
        ('thick', r'Leitura: + espessura das trilhas'),
        ('cross', r'Leitura: + cruzamentos (jitter)'),
    ]
    for step in range(1, 5):
        fig, ax = plt.subplots(figsize=(8.6, 4.0))
        base_eye(ax)
        active = [f[0] for f in feats[:step]]
        if 'vert' in active:
            ax.annotate('', xy=(1.0, 0.78), xytext=(1.0, -0.78),
                        arrowprops=dict(arrowstyle='<->', color=RED, lw=2.0))
            ax.text(1.04, 0.0, 'abertura\nvertical\n(margem de ruído)',
                    color=RED, fontsize=9, fontweight='bold', va='center')
        if 'horiz' in active:
            ax.annotate('', xy=(0.72, 0.0), xytext=(1.28, 0.0),
                        arrowprops=dict(arrowstyle='<->', color=UNB_GREEN, lw=2.0))
            ax.text(1.0, 0.16, 'abertura horizontal\n(margem de temporização)',
                    color=UNB_GREEN, fontsize=9, fontweight='bold', ha='center')
        if 'thick' in active:
            ax.annotate('trilhas espessas =\nISI + ruído', xy=(0.5, 0.95),
                        xytext=(0.12, 1.35), color=PURPLE, fontsize=9,
                        fontweight='bold',
                        arrowprops=dict(arrowstyle='->', color=PURPLE, lw=1.5))
        if 'cross' in active:
            ax.scatter([0.5, 1.5], [0, 0], s=160, facecolors='none',
                       edgecolors=UNB_GOLD, linewidths=2.0, zorder=6)
            ax.annotate('cruzamentos\nespalhados = jitter', xy=(0.5, 0.0),
                        xytext=(0.55, -1.45), color=UNB_GOLD, fontsize=9,
                        fontweight='bold',
                        arrowprops=dict(arrowstyle='->', color=UNB_GOLD, lw=1.5))
        ax.set_title(feats[step-1][1], fontweight='bold')
        plt.tight_layout()
        plt.savefig('../eye_read_%d.pdf' % step, bbox_inches='tight')
        plt.close()
    print("  [OK] eye_read_1..4.pdf")


def gen_rc_timing():
    """Robustez ao erro de temporizacao do cosseno levantado, um conjunto por
    alpha. No instante exato a ISI e nula (Nyquist) para qualquer alpha, mas a
    margem de temporizacao (abertura horizontal do olho) cresce com alpha.
    Gera rc_sync_{0,1,2}_{1,2}.pdf  (alpha = 0, 0.5, 1)."""
    alphas = [0.0, 0.5, 1.0]
    sps = 100
    seg = 2 * sps
    t_eye = np.linspace(0, 2, seg)
    center = seg // 2

    for idx, alpha in enumerate(alphas):
        sig, _ = _build_eye_signal(seed=7, alpha=max(alpha, 1e-6),
                                   sps=sps, N=220, noise=0.0)
        traces = []
        for k in range(3, 200):
            s = k * sps
            e = s + seg
            if e <= len(sig):
                traces.append(sig[s:e])
        traces = np.array(traces)
        pos = traces[traces[:, center] > 0]
        neg = traces[traces[:, center] < 0]
        eye_top = pos.min(axis=0)
        eye_bot = neg.max(axis=0)
        opening = eye_top - eye_bot
        mask = opening > 0.4 * opening[center]      # eye "bem aberto"
        ts = t_eye[mask]
        h0, h1 = (ts.min(), ts.max()) if len(ts) else (1.0, 1.0)
        tail = r'caudas $\sim 1/t$' if alpha == 0 else r'caudas $\sim 1/t^3$'

        def draw(step):
            fig, ax = plt.subplots(figsize=(8.6, 3.9))
            for tr in traces:
                ax.plot(t_eye, tr, color=UNB_BLUE, lw=0.4, alpha=0.30)
            ax.set_xlim([0, 2]); ax.set_ylim([-1.7, 1.7])
            ax.axhline(0, color='black', lw=0.5)
            ax.axvline(1.0, color=RED, lw=1.2, ls='--', alpha=0.7)
            ax.set_xlabel(r'Tempo ($t/T$)', fontsize=12)
            ax.set_ylabel('Amplitude', fontsize=12)
            ax.set_title(r'$\alpha = %.1f$  (%s)' % (alpha, tail.replace('$', '')),
                         fontweight='bold')
            # passo 1: abertura vertical no instante exato (ISI nula)
            ax.annotate('', xy=(1.0, eye_top[center]), xytext=(1.0, eye_bot[center]),
                        arrowprops=dict(arrowstyle='<->', color=RED, lw=2.0))
            ax.text(1.03, 0.0, 'em $t=T$:\nISI nula', color=RED, fontsize=9,
                    fontweight='bold', va='center')
            if step >= 2:
                ax.axvspan(h0, h1, color=UNB_GREEN, alpha=0.12)
                ax.annotate('', xy=(h0, 0.0), xytext=(h1, 0.0),
                            arrowprops=dict(arrowstyle='<->', color=UNB_GREEN, lw=2.2))
                ax.text(1.0, 0.92, 'margem de temporizacao\n(largura = %.2f T)'
                        % (h1 - h0), color=UNB_GREEN, fontsize=9,
                        fontweight='bold', ha='center')
            plt.tight_layout()
            plt.savefig('../rc_sync_%d_%d.pdf' % (idx, step), bbox_inches='tight')
            plt.close()

        draw(1)
        draw(2)
    print("  [OK] rc_sync_{0,1,2}_{1,2}.pdf")


if __name__ == '__main__':
    print("Gerando figuras de diagrama de olho e PAM...")
    gen_eye_diagram_clean()
    gen_eye_construction()
    gen_eye_overlay_build()
    gen_eye_analise_base()
    gen_eye_reading()
    gen_rc_timing()
    gen_eye_diagram_rolloff()
    gen_pam_constellation()
    gen_pam_waveforms()
    gen_eye_diagram_4pam()
    print("Concluído!\n")
