#!/usr/bin/env python3
"""
Transmissao de bits com o cosseno levantado. Mostra a progressao do sinal
total (soma de pulsos) e, no instante de amostragem com pequeno erro de
temporizacao, compara a ISI do cosseno levantado com a do sinc puro.

Saida: ../rc_bits_1..6.pdf  -> progressao (1 simbolo por vez); o 6 amostra
                               em t = nT + eps e mostra ISI pequena
       ../rc_bits_isi.pdf    -> |ISI| por simbolo: sinc vs cosseno levantado

Uso: python gen_rc_bits.py
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
PURPLE    = '#8E44AD'

T = 1.0
ALPHA = 0.5
EPS = 0.15 * T          # erro de temporizacao
bits = [1, -1, 1, 1, -1]
colors = [UNB_BLUE, RED, UNB_GREEN, UNB_GOLD, PURPLE]


def rc_time(t, T, alpha):
    """Pulso cosseno levantado no tempo, com singularidades tratadas."""
    t = np.asarray(t, dtype=float)
    p = np.zeros_like(t)
    den = 1.0 - (2 * alpha * t / T) ** 2
    sing = np.abs(den) < 1e-9
    reg = ~sing
    p[reg] = (np.sinc(t[reg] / T) *
              np.cos(np.pi * alpha * t[reg] / T) / den[reg])
    if alpha > 0:
        p[sing] = (np.pi / 4.0) * np.sinc(1.0 / (2 * alpha))
    return p


def sinc_time(t, T, alpha=0.0):
    return np.sinc(np.asarray(t, dtype=float) / T)


def pulse(kind, t):
    return rc_time(t, T, ALPHA) if kind == 'rc' else sinc_time(t, T)


# ===========================================================================
# Progressao do sinal total (cosseno levantado)
# ===========================================================================
t = np.linspace(-4 * T, 8 * T, 3000)
decis = list(range(len(bits)))
xlim, ylim = [-3, 7], [-1.8, 2.15]


def sample_at(arr, n, off=0.0):
    return arr[np.argmin(np.abs(t - (n * T + off)))]


nb = len(bits)
for step in range(1, nb + 2):
    nact = min(step, nb)
    final = (step == nb + 1)
    fig, (axT, axB) = plt.subplots(2, 1, figsize=(9, 5.0))

    total = np.zeros_like(t)
    for n in range(nact):
        p = bits[n] * pulse('rc', t - n * T)
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
    axT.set_title(r'(c) Pulsos cosseno levantado ($\alpha = 0{,}5$)',
                  fontweight='bold')
    axT.tick_params(labelbottom=False)

    axB.plot(t / T, total, color='black', lw=2.5, label='Sinal total')
    for n in range(nact):
        axB.plot(n, sample_at(total, n), 'o', color=UNB_GREEN, ms=8, zorder=5)
    axB.set_xlabel(r'Tempo ($t / T$)', fontsize=12)
    axB.legend(fontsize=10, loc='upper right')

    if final:
        # amostragem com erro de temporizacao eps
        for d in decis:
            ideal = bits[d]
            act = sample_at(total, d, EPS)
            axB.plot([d - 0.18, d + 0.18], [ideal, ideal],
                     color='gray', lw=1.0)
            axB.plot(d + EPS, act, 'D', color=UNB_GREEN, ms=7, zorder=6)
            axB.annotate('', xy=(d + EPS, act), xytext=(d + EPS, ideal),
                         arrowprops=dict(arrowstyle='->', color=UNB_GREEN,
                                         lw=1.4))
        axB.axvline(EPS, color=UNB_GREEN, lw=0.0)
        axB.text(-2.9, 1.78,
                 r'amostra em $t = nT + \epsilon$: desvio pequeno  $\to$  '
                 r'ISI baixa', color=UNB_GREEN, fontsize=10,
                 fontweight='bold')

    plt.tight_layout()
    plt.savefig('../rc_bits_%d.pdf' % step, bbox_inches='tight')
    plt.close()

# ===========================================================================
# Comparacao de ISI de pior caso: sinc vs cosseno levantado (mesmo erro eps)
# Pior caso: bits vizinhos alinhados para somar |contribuicoes| construtivas.
# Mostra ISI acumulada em funcao da janela de vizinhos N.
# ===========================================================================
Nmax = 14
Ns = np.arange(1, Nmax + 1)


def worst_isi(kind, N):
    """ISI de pior caso amostrando em nT + eps, com N vizinhos de cada lado."""
    s = 0.0
    for m in range(1, N + 1):
        s += abs(pulse(kind, np.array([m * T + EPS]))[0])
        s += abs(pulse(kind, np.array([-m * T + EPS]))[0])
    return s


wc_sinc = np.array([worst_isi('sinc', N) for N in Ns])
wc_rc = np.array([worst_isi('rc', N) for N in Ns])

fig, ax = plt.subplots(figsize=(7.6, 3.4))
ax.plot(Ns, wc_sinc, 'o-', color=RED, lw=2.2, ms=5,
        label=r'sinc ($\alpha = 0$) — cresce como $\ln N$')
ax.plot(Ns, wc_rc, 's-', color=UNB_GREEN, lw=2.4, ms=5,
        label=r'cosseno levantado ($\alpha = 0{,}5$) — satura')
ax.axhline(wc_rc[-1], color=UNB_GREEN, ls=':', lw=1)
ax.annotate(f'satura em {wc_rc[-1]:.2f}', xy=(Nmax, wc_rc[-1]),
            xytext=(Nmax - 6, wc_rc[-1] + 0.12), color=UNB_GREEN, fontsize=10)
ax.annotate(f'{wc_sinc[-1]:.2f} e ainda subindo', xy=(Nmax, wc_sinc[-1]),
            xytext=(Nmax - 8.5, wc_sinc[-1] - 0.02), color=RED, fontsize=10)
ax.set_xlabel('Janela de símbolos vizinhos $N$', fontsize=12)
ax.set_ylabel(r'ISI de pior caso', fontsize=12)
ax.set_title(r'ISI acumulada com erro de temporização $\epsilon = 0{,}15\,T$',
             fontsize=12)
ax.set_xticks(Ns[::2])
ax.set_ylim(0, wc_sinc.max() * 1.15)
ax.legend(frameon=False, fontsize=10, loc='center right')
plt.tight_layout()
plt.savefig('../rc_bits_isi.pdf', bbox_inches='tight')
plt.close()

print('Figuras rc_bits_1..6.pdf e rc_bits_isi.pdf geradas.')
print('ISI pior caso sinc:', np.round(wc_sinc, 3))
print('ISI pior caso rc  :', np.round(wc_rc, 3))
