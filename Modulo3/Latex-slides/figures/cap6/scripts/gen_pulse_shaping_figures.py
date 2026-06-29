#!/usr/bin/env python3
"""
Gera figuras de formatação de pulso para os slides de Transmissão Digital.
Saída: ../pulse_shaping_isi.pdf, ../raised_cosine_time.pdf,
       ../raised_cosine_freq.pdf, ../pulse_shaping_comparison.pdf

Uso: python gen_pulse_shaping_figures.py
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

# ===========================================================================
# Raised cosine pulse (time domain)
# ===========================================================================
def raised_cosine_time(t, T, alpha):
    """Raised cosine pulse p(t) in time domain."""
    p = np.zeros_like(t)
    for i, ti in enumerate(t):
        if abs(ti) < 1e-12:
            p[i] = 1.0
        elif alpha > 0 and abs(abs(ti) - T / (2 * alpha)) < 1e-12:
            p[i] = (alpha / 2.0) * np.sinc(1.0 / (2 * alpha))
        else:
            p[i] = np.sinc(ti / T) * np.cos(np.pi * alpha * ti / T) / \
                   (1 - (2 * alpha * ti / T)**2 + 1e-30)
    return p


def raised_cosine_freq(f, T, alpha):
    """Raised cosine spectrum P(f)."""
    P = np.zeros_like(f)
    for i, fi in enumerate(f):
        fi_abs = abs(fi)
        if fi_abs <= (1 - alpha) / (2 * T):
            P[i] = T
        elif fi_abs <= (1 + alpha) / (2 * T):
            P[i] = T / 2.0 * (1 + np.cos(np.pi * T / alpha *
                    (fi_abs - (1 - alpha) / (2 * T))))
        else:
            P[i] = 0.0
    return P


# ===========================================================================
# Figura 1: ISI illustration
# ===========================================================================
def gen_isi_illustration():
    T = 1.0
    t = np.linspace(-4*T, 8*T, 3000)
    bits = [1, -1, 1, 1, -1]

    fig, axes = plt.subplots(2, 1, figsize=(9, 5.5))

    # (a) Without ISI: ideal sinc pulses
    ax = axes[0]
    total = np.zeros_like(t)
    colors = [UNB_BLUE, RED, UNB_GREEN, UNB_GOLD, PURPLE]
    for k, (b, c) in enumerate(zip(bits, colors)):
        pulse = b * np.sinc((t - k*T) / T)
        ax.plot(t/T, pulse, color=c, linewidth=1.0, alpha=0.5, linestyle='--')
        total += pulse
    ax.plot(t/T, total, color='black', linewidth=2.5, label='Sinal total')
    for k, b in enumerate(bits):
        ax.plot(k, b, 'o', color=colors[k], markersize=8, zorder=5)
    ax.set_title(r'(a) Pulsos sinc ideais — sem ISI (zeros nos instantes $t = nT$)',
                 fontweight='bold')
    ax.set_ylabel('Amplitude', fontsize=12)
    ax.set_xlim([-3, 7])
    ax.set_ylim([-1.8, 1.8])
    ax.legend(fontsize=10)
    ax.tick_params(labelbottom=False)
    ax.axhline(0, color='black', linewidth=0.5)

    # (b) With ISI: rectangular pulses wider than T
    ax = axes[1]
    total2 = np.zeros_like(t)
    for k, (b, c) in enumerate(zip(bits, colors)):
        # Wider-than-T pulse causes ISI
        pulse = b * np.exp(-((t - k*T) / (0.8*T))**2)
        ax.plot(t/T, pulse, color=c, linewidth=1.0, alpha=0.5, linestyle='--')
        total2 += pulse
    ax.plot(t/T, total2, color='black', linewidth=2.5, label='Sinal total (com ISI)')
    for k, b in enumerate(bits):
        ax.plot(k, total2[np.argmin(np.abs(t - k*T))], 's', color=RED,
                markersize=8, zorder=5)
    ax.set_title(r'(b) Pulsos gaussianos — ISI presente (valores amostrados deslocados)',
                 fontweight='bold')
    ax.set_ylabel('Amplitude', fontsize=12)
    ax.set_xlabel(r'Tempo ($t / T$)', fontsize=12)
    ax.set_xlim([-3, 7])
    ax.set_ylim([-1.8, 1.8])
    ax.legend(fontsize=10)
    ax.axhline(0, color='black', linewidth=0.5)

    plt.tight_layout()
    plt.savefig('../pulse_shaping_isi.pdf', bbox_inches='tight')
    plt.close()
    print("  [OK] pulse_shaping_isi.pdf")


# ===========================================================================
# Figura 2: Raised Cosine — domínio do tempo
# ===========================================================================
def gen_raised_cosine_time():
    T = 1.0
    t = np.linspace(-5*T, 5*T, 5000)
    alphas = [0.0, 0.25, 0.5, 0.75, 1.0]
    colors = [UNB_BLUE, UNB_GREEN, UNB_GOLD, RED, PURPLE]

    fig, ax = plt.subplots(1, 1, figsize=(9, 5))

    for alpha, color in zip(alphas, colors):
        p = raised_cosine_time(t, T, alpha)
        ax.plot(t/T, p, color=color, linewidth=2.0,
                label=rf'$\alpha = {alpha}$')

    # Mark zero crossings at nT
    for n in range(-4, 5):
        if n != 0:
            ax.axvline(n, color='gray', linewidth=0.3, linestyle=':')
            ax.plot(n, 0, 'k.', markersize=4)

    ax.set_xlabel(r'Tempo normalizado ($t / T$)', fontsize=12)
    ax.set_ylabel(r'$p(t)$', fontsize=13)
    ax.set_title('Pulso Cosseno Levantado — Domínio do Tempo', fontweight='bold')
    ax.legend(fontsize=10, loc='upper right')
    ax.set_xlim([-5, 5])
    ax.set_ylim([-0.35, 1.15])
    ax.axhline(0, color='black', linewidth=0.5)

    plt.tight_layout()
    plt.savefig('../raised_cosine_time.pdf', bbox_inches='tight')
    plt.close()
    print("  [OK] raised_cosine_time.pdf")


# ===========================================================================
# Figura 3: Raised Cosine — domínio da frequência
# ===========================================================================
def gen_raised_cosine_freq():
    T = 1.0
    f = np.linspace(-1.5/T, 1.5/T, 5000)
    alphas = [0.0, 0.25, 0.5, 0.75, 1.0]
    colors = [UNB_BLUE, UNB_GREEN, UNB_GOLD, RED, PURPLE]

    fig, ax = plt.subplots(1, 1, figsize=(9, 5))

    for alpha, color in zip(alphas, colors):
        P = raised_cosine_freq(f, T, alpha)
        ax.plot(f * T, P / T, color=color, linewidth=2.0,
                label=rf'$\alpha = {alpha}$')

    ax.set_xlabel(r'Frequência normalizada ($f \cdot T$)', fontsize=12)
    ax.set_ylabel(r'$P(f) / T$', fontsize=13)
    ax.set_title('Espectro do Cosseno Levantado — Domínio da Frequência',
                 fontweight='bold')
    ax.legend(fontsize=10, loc='upper right')
    ax.set_xlim([-1.5, 1.5])
    ax.set_ylim([-0.05, 1.15])
    ax.axhline(0, color='black', linewidth=0.5)

    # Mark key frequencies
    ax.axvline(0.5, color='gray', linewidth=1, linestyle=':', alpha=0.6)
    ax.text(0.52, 1.05, r'$\frac{1}{2T}$', fontsize=11, color='gray')
    ax.axvline(-0.5, color='gray', linewidth=1, linestyle=':', alpha=0.6)

    plt.tight_layout()
    plt.savefig('../raised_cosine_freq.pdf', bbox_inches='tight')
    plt.close()
    print("  [OK] raised_cosine_freq.pdf")


# ===========================================================================
# Figura 4: Comparação de formas de pulso
# ===========================================================================
def gen_pulse_comparison():
    T = 1.0
    t = np.linspace(-4*T, 8*T, 5000)
    bits = [1, -1, 1, 1, -1, 1, -1, -1]

    fig, axes = plt.subplots(3, 1, figsize=(10, 7))

    labels = [
        (r'(a) Pulso Retangular (largura $T$)', 'rect'),
        (r'(b) Pulso Sinc (sem roll-off, $\alpha=0$)', 'sinc'),
        (r'(c) Cosseno Levantado ($\alpha=0.5$)', 'rc'),
    ]
    colors_sig = [UNB_BLUE, UNB_GREEN, RED]

    for idx, ((title, ptype), col) in enumerate(zip(labels, colors_sig)):
        ax = axes[idx]
        total = np.zeros_like(t)
        for k, b in enumerate(bits):
            if ptype == 'rect':
                pulse = b * ((t >= k*T) & (t < (k+1)*T)).astype(float)
            elif ptype == 'sinc':
                pulse = b * np.sinc((t - k*T) / T)
            else:
                pulse = b * raised_cosine_time(t - k*T, T, 0.5)
            total += pulse

        ax.plot(t/T, total, color=col, linewidth=2.0)
        # Sample points
        for k, b in enumerate(bits):
            ts = k * T
            idx_t = np.argmin(np.abs(t - ts))
            ax.plot(k, total[idx_t], 'ko', markersize=5, zorder=5)
        ax.set_title(title, fontweight='bold')
        ax.set_ylabel('Amplitude')
        ax.set_xlim([-2, 9])
        ax.set_ylim([-2.0, 2.0])
        ax.axhline(0, color='black', linewidth=0.5)
        for n in range(len(bits)):
            ax.axvline(n, color='gray', linewidth=0.3, linestyle=':')
        if idx < 2:
            ax.tick_params(labelbottom=False)
        else:
            ax.set_xlabel(r'Tempo ($t / T$)', fontsize=12)

    plt.tight_layout()
    plt.savefig('../pulse_shaping_comparison.pdf', bbox_inches='tight')
    plt.close()
    print("  [OK] pulse_shaping_comparison.pdf")


def gen_isi_sequences():
    """Sequencias animadas (1 simbolo por vez) para overlay: topo = pulsos
    individuais, base = sinal total em preto; etapa final com setas nos
    instantes de decisao. Gera isi_sinc_{1..6} e isi_gauss_{1..6}."""
    T = 1.0
    t = np.linspace(-4*T, 8*T, 3000)
    bits = [1, -1, 1, 1, -1]
    colors = [UNB_BLUE, RED, UNB_GREEN, UNB_GOLD, PURPLE]
    decis = list(range(len(bits)))            # instantes t/T = 0..4
    xlim, ylim = [-3, 7], [-1.8, 2.15]

    def pulse_of(kind, k, b):
        if kind == 'sinc':
            return b * np.sinc((t - k*T) / T)
        return b * np.exp(-((t - k*T) / (0.8*T))**2)

    def sample_at(arr, n):
        return arr[np.argmin(np.abs(t - n*T))]

    def make(kind, prefix, title_top):
        nb = len(bits)
        for step in range(1, nb + 2):          # 1..5 constroi, 6 = anotado
            nact = min(step, nb)
            final = (step == nb + 1)
            fig, (axT, axB) = plt.subplots(2, 1, figsize=(9, 5.0))

            total = np.zeros_like(t)
            for n in range(nact):
                p = pulse_of(kind, n, bits[n])
                total += p
                axT.plot(t / T, p, color=colors[n], lw=1.1, alpha=0.65, ls='--')
                axT.plot(n, bits[n], 'o', color=colors[n], ms=8, zorder=5)

            for axx in (axT, axB):
                for d in decis:
                    axx.axvline(d, color='gray', lw=0.3, ls=':')
                axx.axhline(0, color='black', lw=0.5)
                axx.set_xlim(xlim)
                axx.set_ylim(ylim)
                axx.set_ylabel('Amplitude', fontsize=12)
            axT.set_title(title_top, fontweight='bold')
            axT.tick_params(labelbottom=False)

            axB.plot(t / T, total, color='black', lw=2.5, label='Sinal total')
            mk = 'o' if kind == 'sinc' else 's'
            mc = UNB_GREEN if kind == 'sinc' else RED
            for n in range(nact):
                axB.plot(n, sample_at(total, n), mk, color=mc, ms=8, zorder=5)
            axB.set_xlabel(r'Tempo ($t / T$)', fontsize=12)
            axB.legend(fontsize=10, loc='upper right')

            if final:
                if kind == 'sinc':
                    for d in decis:
                        sv = sample_at(total, d)
                        off = 0.45 if sv >= 0 else -0.45
                        axB.annotate('', xy=(d, sv), xytext=(d, sv + off),
                                     arrowprops=dict(arrowstyle='->',
                                                     color=UNB_GREEN, lw=1.6))
                    axB.text(-2.9, 1.78, 'nos instantes t = nT: amostra = simbolo  '
                             '(sem ISI)', color=UNB_GREEN, fontsize=10,
                             fontweight='bold')
                else:
                    for n in decis:
                        ideal, act = bits[n], sample_at(total, n)
                        axB.plot([n - 0.18, n + 0.18], [ideal, ideal],
                                 color='gray', lw=1.0, ls='-')
                        axB.annotate('', xy=(n, act), xytext=(n, ideal),
                                     arrowprops=dict(arrowstyle='->',
                                                     color=RED, lw=1.6))
                    axB.text(-2.9, 1.78, 'amostra deslocada do simbolo (cinza)  '
                             '->  ISI', color=RED, fontsize=10, fontweight='bold')

            plt.tight_layout()
            plt.savefig('../%s_%d.pdf' % (prefix, step), bbox_inches='tight')
            plt.close()
        print("  [OK] %s_1..%d.pdf" % (prefix, nb + 1))

    make('sinc', 'isi_sinc', r'(a) Pulsos sinc ideais — um pulso por simbolo')
    make('gauss', 'isi_gauss', r'(b) Pulsos gaussianos — mais largos que $T$')


def gen_sinc_timing():
    """Ilustra por que o sinc puro e fragil a erro de temporizacao:
    amostra ideal (t=0) vs amostra com erro (t=eps), e a divergencia da
    serie harmonica (pior caso de ISI). Gera sinc_timing_{1,2} e
    sinc_harmonic."""
    T = 1.0
    eps = 0.25
    t = np.linspace(-4.6, 4.6, 4000)
    ks = list(range(-4, 5))            # vizinhos -4..4, todos +1 (pior caso)
    pulses = [np.sinc((t - k) / T) for k in ks]
    total = np.sum(pulses, axis=0)

    def at(tt):
        return np.sum([np.sinc((tt - k) / T) for k in ks])

    def base(offset_sample):
        fig, ax = plt.subplots(figsize=(8.6, 3.6))
        for p in pulses:
            ax.plot(t, p, color=UNB_BLUE, lw=0.8, alpha=0.30, ls='--')
        ax.plot(t, total, color='black', lw=2.3, label='sinal (todos $+1$)')
        for k in ks:
            ax.axvline(k, color='gray', lw=0.3, ls=':')
        ax.axhline(0, color='black', lw=0.5)
        ax.set_xlim([-4.6, 4.6])
        ax.set_ylim([-0.7, 1.9])
        ax.set_xlabel(r'Tempo ($t/T$)', fontsize=12)
        ax.set_ylabel('Amplitude', fontsize=12)
        return fig, ax

    # --- (1) amostragem ideal em t=0 ---
    fig, ax = base(False)
    ax.plot(0, at(0), 'o', color=UNB_GREEN, ms=10, zorder=6)
    ax.annotate('amostra ideal em $t=0$:\nso o pulso central conta',
                xy=(0, at(0)), xytext=(1.1, 1.55),
                color=UNB_GREEN, fontsize=10, fontweight='bold',
                arrowprops=dict(arrowstyle='->', color=UNB_GREEN, lw=1.4))
    ax.legend(fontsize=9, loc='upper left')
    plt.tight_layout(); plt.savefig('../sinc_timing_1.pdf', bbox_inches='tight'); plt.close()

    # --- (2) amostragem com erro t=eps ---
    fig, ax = base(True)
    ax.axvline(eps, color=RED, lw=1.0, ls='-', alpha=0.7)
    ax.plot(eps, at(eps), 's', color=RED, ms=10, zorder=6)
    # contribuicoes dos vizinhos em t=eps (setas curtas)
    for k in ks:
        if k == 0:
            continue
        v = np.sinc((eps - k) / T)
        ax.annotate('', xy=(eps, v), xytext=(eps, 0),
                    arrowprops=dict(arrowstyle='->', color=RED, lw=1.0, alpha=0.7))
    ax.annotate('amostra em $t=\\epsilon$:\nvizinhos ja nao valem 0',
                xy=(eps, at(eps)), xytext=(1.2, 1.55),
                color=RED, fontsize=10, fontweight='bold',
                arrowprops=dict(arrowstyle='->', color=RED, lw=1.4))
    ax.legend(fontsize=9, loc='upper left')
    plt.tight_layout(); plt.savefig('../sinc_timing_2.pdf', bbox_inches='tight'); plt.close()

    # --- (3) serie harmonica: contribuicao ~1/k e soma parcial diverge ---
    N = 16
    kk = np.arange(1, N + 1)
    contrib = 1.0 / kk
    Hn = np.cumsum(contrib)
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(8.8, 3.4))
    a1.bar(kk, contrib, color=UNB_BLUE, alpha=0.8)
    a1.set_title(r'Contribuicao de ISI por vizinho $\sim 1/k$', fontweight='bold')
    a1.set_xlabel(r'vizinho $k$', fontsize=11)
    a1.set_ylabel(r'$|$ISI$_k| / (\epsilon/T)$', fontsize=11)
    a2.plot(kk, Hn, 'o-', color=RED, lw=1.8, ms=4, label=r'$\sum_{k=1}^{N} 1/k$')
    a2.plot(kk, np.log(kk) + 0.5772, '--', color='gray', lw=1.2,
            label=r'$\ln N + \gamma$')
    a2.set_title('Soma parcial cresce sem limite (diverge)', fontweight='bold')
    a2.set_xlabel(r'$N$ vizinhos somados', fontsize=11)
    a2.set_ylabel('ISI pior caso acumulada', fontsize=11)
    a2.legend(fontsize=10, loc='upper left')
    plt.tight_layout(); plt.savefig('../sinc_harmonic.pdf', bbox_inches='tight'); plt.close()
    print("  [OK] sinc_timing_{1,2}.pdf, sinc_harmonic.pdf")


if __name__ == '__main__':
    print("Gerando figuras de formatação de pulso...")
    gen_isi_illustration()
    gen_isi_sequences()
    gen_sinc_timing()
    gen_raised_cosine_time()
    gen_raised_cosine_freq()
    gen_pulse_comparison()
    print("Concluído!\n")
