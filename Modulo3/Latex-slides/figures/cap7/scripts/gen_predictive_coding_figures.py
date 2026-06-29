#!/usr/bin/env python3
"""
Gera figuras de codificacao preditiva (Modulacao Delta) para os slides.
Saidas:
  ../dm_tracking.pdf
  ../dm_slope_overload_{1,2,3}.pdf   (exemplo animado de sobrecarga)
  ../dm_granular_{1,2,3}.pdf         (exemplo animado de ruido granular)

Uso: python gen_predictive_coding_figures.py
"""

import numpy as np
import matplotlib.pyplot as plt

plt.rcParams.update({
    'font.size': 11,
    'font.family': 'serif',
    'axes.labelsize': 12,
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


def gen_dm_tracking():
    # sinal contInuo: x(t) = -0.85 cos(2 pi t)  (lento nos picos, rApido no meio)
    t = np.linspace(0, 1, 3000)
    x = -0.85 * np.cos(2 * np.pi * t)

    # Modulacao Delta
    fs = 32                       # taxa de amostragem (sobreamostrado)
    Ts = 1 / fs
    tk = np.arange(0, 1 + Ts / 2, Ts)
    xk = -0.85 * np.cos(2 * np.pi * tk)
    delta = 0.11                  # passo (delta/Ts = 3.52 < pico de inclinacao 5.34)

    xhat = np.zeros(len(tk))
    acc = -0.85
    for i in range(len(tk)):
        if xk[i] > acc:
            acc += delta
        else:
            acc -= delta
        xhat[i] = acc

    fig, ax = plt.subplots(figsize=(9, 3.2))
    ax.plot(t, x, color=UNB_BLUE, linewidth=2.2, label=r'sinal $x(t)$')
    ax.step(tk, xhat, where='post', color=UNB_GREEN, linewidth=1.8,
            label='aproximacao DM (escada)')
    ax.set_ylim(-1.15, 1.15)
    ax.set_xlim(0, 1)
    ax.set_xlabel(r'tempo ($t$)')
    ax.set_ylabel('amplitude')
    ax.axhline(0, color='black', linewidth=0.5)
    ax.legend(loc='lower center', fontsize=9, ncol=2)

    # anotacao: sobrecarga de inclinacao (subida ingreme ~ t=0.25)
    ax.annotate('sobrecarga de\ninclinacao',
                xy=(0.25, 0.0), xytext=(0.36, -0.65),
                fontsize=9, color=RED, ha='center',
                arrowprops=dict(arrowstyle='->', color=RED, lw=1.5))
    # anotacao: ruido granular (pico achatado ~ t=0.5)
    ax.annotate('ruido granular',
                xy=(0.52, 0.82), xytext=(0.72, 0.30),
                fontsize=9, color=UNB_GOLD, ha='center',
                arrowprops=dict(arrowstyle='->', color=UNB_GOLD, lw=1.5))

    plt.tight_layout()
    plt.savefig('../dm_tracking.pdf', bbox_inches='tight')
    plt.close()
    print("  [OK] dm_tracking.pdf")


def dm_staircase(xk, delta, x0):
    """Modulacao Delta: retorna a escada xhat para amostras xk, passo delta."""
    xhat = np.zeros(len(xk))
    acc = x0
    for i in range(len(xk)):
        acc += delta if xk[i] > acc else -delta
        xhat[i] = acc
    return xhat


def _base_axes(ylim=(-1.15, 1.15)):
    fig, ax = plt.subplots(figsize=(8.4, 3.2))
    ax.set_ylim(*ylim)
    ax.set_xlim(0, 1)
    ax.set_xlabel(r'tempo ($t$)')
    ax.set_ylabel('amplitude')
    ax.axhline(0, color='black', linewidth=0.5)
    return fig, ax


def gen_slope_overload():
    """Exemplo animado: sinal rapido + delta pequeno => sobrecarga; ajusta delta."""
    t = np.linspace(0, 1, 3000)
    x = 0.9 * np.sin(2 * np.pi * t)           # inclinacao maxima ~ 5.65
    fs = 32
    Ts = 1 / fs
    tk = np.arange(0, 1 + Ts / 2, Ts)
    xk = 0.9 * np.sin(2 * np.pi * tk)

    delta_bad = 0.05      # delta*fs = 1.6  << 5.65  => sobrecarga forte
    delta_good = 0.20     # delta*fs = 6.4   > 5.65  => acompanha
    xhat_bad = dm_staircase(xk, delta_bad, 0.0)
    xhat_good = dm_staircase(xk, delta_good, 0.0)

    def legend(ax):
        ax.legend(loc='lower center', fontsize=9, ncol=2)

    # --- etapa 1: so o sinal chegando ---
    fig, ax = _base_axes()
    ax.plot(t, x, color=UNB_BLUE, linewidth=2.2, label=r'sinal $x(t)$')
    legend(ax)
    plt.tight_layout(); plt.savefig('../dm_slope_overload_1.pdf', bbox_inches='tight'); plt.close()

    # --- etapa 2: escada com delta pequeno nao acompanha (sobrecarga) ---
    fig, ax = _base_axes()
    ax.plot(t, x, color=UNB_BLUE, linewidth=2.2, label=r'sinal $x(t)$')
    ax.step(tk, xhat_bad, where='post', color=UNB_GREEN, linewidth=1.8,
            label=r'DM, $\delta$ pequeno')
    ax.annotate('a escada nao\nconsegue subir',
                xy=(0.15, 0.5), xytext=(0.30, -0.55),
                fontsize=9, color=RED, ha='center',
                arrowprops=dict(arrowstyle='->', color=RED, lw=1.5))
    legend(ax)
    plt.tight_layout(); plt.savefig('../dm_slope_overload_2.pdf', bbox_inches='tight'); plt.close()

    # --- etapa 3: aumenta delta => acompanha ---
    fig, ax = _base_axes()
    ax.plot(t, x, color=UNB_BLUE, linewidth=2.2, label=r'sinal $x(t)$')
    ax.step(tk, xhat_good, where='post', color=UNB_GREEN, linewidth=1.8,
            label=r'DM, $\delta$ maior')
    ax.annotate(r'$\delta$ maior:'+'\nagora acompanha',
                xy=(0.15, 0.62), xytext=(0.34, -0.55),
                fontsize=9, color=UNB_GREEN, ha='center',
                arrowprops=dict(arrowstyle='->', color=UNB_GREEN, lw=1.5))
    legend(ax)
    plt.tight_layout(); plt.savefig('../dm_slope_overload_3.pdf', bbox_inches='tight'); plt.close()
    print("  [OK] dm_slope_overload_{1,2,3}.pdf")


def gen_granular():
    """Exemplo animado: sinal lento + delta grande => ruido granular; ajusta delta."""
    t = np.linspace(0, 1, 3000)
    x = 0.45 * np.sin(np.pi * t)              # meia onda lenta (quase plana no topo)
    fs = 32
    Ts = 1 / fs
    tk = np.arange(0, 1 + Ts / 2, Ts)
    xk = 0.45 * np.sin(np.pi * tk)

    delta_bad = 0.18      # passo grande => escada caca (hunting) ao redor do sinal
    delta_good = 0.05     # passo menor => cola no sinal
    xhat_bad = dm_staircase(xk, delta_bad, 0.0)
    xhat_good = dm_staircase(xk, delta_good, 0.0)

    def legend(ax):
        ax.legend(loc='lower center', fontsize=9, ncol=2)

    # --- etapa 1: so o sinal lento ---
    fig, ax = _base_axes(ylim=(-0.35, 0.75))
    ax.plot(t, x, color=UNB_BLUE, linewidth=2.2, label=r'sinal $x(t)$ (lento)')
    legend(ax)
    plt.tight_layout(); plt.savefig('../dm_granular_1.pdf', bbox_inches='tight'); plt.close()

    # --- etapa 2: delta grande => oscilacao ao redor do sinal ---
    fig, ax = _base_axes(ylim=(-0.35, 0.75))
    ax.plot(t, x, color=UNB_BLUE, linewidth=2.2, label=r'sinal $x(t)$ (lento)')
    ax.step(tk, xhat_bad, where='post', color=UNB_GREEN, linewidth=1.8,
            label=r'DM, $\delta$ grande')
    ax.annotate('a escada oscila\n$\\pm\\delta$ (granular)',
                xy=(0.5, 0.45), xytext=(0.62, -0.05),
                fontsize=9, color=UNB_GOLD, ha='center',
                arrowprops=dict(arrowstyle='->', color=UNB_GOLD, lw=1.5))
    legend(ax)
    plt.tight_layout(); plt.savefig('../dm_granular_2.pdf', bbox_inches='tight'); plt.close()

    # --- etapa 3: reduz delta => cola no sinal ---
    fig, ax = _base_axes(ylim=(-0.35, 0.75))
    ax.plot(t, x, color=UNB_BLUE, linewidth=2.2, label=r'sinal $x(t)$ (lento)')
    ax.step(tk, xhat_good, where='post', color=UNB_GREEN, linewidth=1.8,
            label=r'DM, $\delta$ menor')
    ax.annotate(r'$\delta$ menor:'+'\nruido reduzido',
                xy=(0.5, 0.45), xytext=(0.64, -0.02),
                fontsize=9, color=UNB_GREEN, ha='center',
                arrowprops=dict(arrowstyle='->', color=UNB_GREEN, lw=1.5))
    legend(ax)
    plt.tight_layout(); plt.savefig('../dm_granular_3.pdf', bbox_inches='tight'); plt.close()
    print("  [OK] dm_granular_{1,2,3}.pdf")


if __name__ == '__main__':
    print("Gerando figuras de codificacao preditiva...")
    gen_dm_tracking()
    gen_slope_overload()
    gen_granular()
    print("Concluido!\n")
