#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Demonstração de formatação de pulso, ISI e diagrama de olho (NumPy/Matplotlib).

Alternativa ao flowgraph do GNU Radio (demo_pulse_shaping_olho.grc), útil quando
o GNU Radio não está disponível. Reproduz a mesma cadeia: símbolos 2-PAM ->
filtro formatador RRC -> canal AWGN -> filtro casado RRC.

Dois modos de uso:

  1. Interativo com sliders (alpha, ruído, amostras por símbolo):
        python3 demo_interativo_matplotlib.py

  2. Geração das figuras dos slides (salva PDFs e encerra):
        python3 demo_interativo_matplotlib.py --salvar ../../Latex-slides/figures/cap6
"""

import argparse
import numpy as np
import matplotlib.pyplot as plt


# ------------------------------------------------------------------
# Filtro raiz de cosseno levantado (root raised cosine)
# ------------------------------------------------------------------
def rrc_taps(beta, sps, span):
    """Coeficientes do filtro RRC. span = duração em símbolos."""
    n = np.arange(-span * sps, span * sps + 1)
    t = n / sps
    taps = np.zeros_like(t, dtype=float)
    for i, ti in enumerate(t):
        if abs(ti) < 1e-8:
            taps[i] = 1.0 - beta + 4.0 * beta / np.pi
        elif beta > 0 and abs(abs(4.0 * beta * ti) - 1.0) < 1e-8:
            taps[i] = (beta / np.sqrt(2.0)) * (
                (1.0 + 2.0 / np.pi) * np.sin(np.pi / (4.0 * beta))
                + (1.0 - 2.0 / np.pi) * np.cos(np.pi / (4.0 * beta))
            )
        else:
            num = (np.sin(np.pi * ti * (1.0 - beta))
                   + 4.0 * beta * ti * np.cos(np.pi * ti * (1.0 + beta)))
            den = np.pi * ti * (1.0 - (4.0 * beta * ti) ** 2)
            taps[i] = num / den
    return taps / np.sqrt(np.sum(taps ** 2))


# ------------------------------------------------------------------
# Cadeia TX RRC -> canal AWGN -> filtro casado RRC
# ------------------------------------------------------------------
def simular(beta, sps, ruido, n_simbolos=400, span=8, seed=1):
    rng = np.random.default_rng(seed)
    simbolos = rng.integers(0, 2, n_simbolos) * 2 - 1          # 2-PAM: -1, +1

    impulsos = np.zeros(n_simbolos * sps)
    impulsos[::sps] = simbolos                                  # 1 impulso/símbolo

    taps = rrc_taps(beta, sps, span)
    tx = np.convolve(impulsos, taps, mode="same")              # formatação
    tx = tx / np.std(tx)                                       # normaliza potência

    canal = tx + ruido * rng.standard_normal(tx.shape)         # AWGN
    rx = np.convolve(canal, taps, mode="same")                 # filtro casado
    return simbolos, taps, tx, rx


def segmentos_olho(rx, sps, n_olho=160, atraso=0):
    """Recorta o sinal em janelas de 2 símbolos para o diagrama de olho."""
    win = 2 * sps
    ini = 4 * sps + atraso
    trechos = []
    i = ini
    while i + win < len(rx) and len(trechos) < n_olho:
        trechos.append(rx[i:i + win])
        i += sps
    return np.array(trechos)


# ------------------------------------------------------------------
# Figuras para os slides
# ------------------------------------------------------------------
def salvar_figuras(destino):
    import os
    os.makedirs(destino, exist_ok=True)
    sps = 8

    # (1) Formatação de pulso: trem de impulsos vs sinal formatado
    simbolos, taps, tx, rx = simular(0.35, sps, 0.0, n_simbolos=12, span=6, seed=3)
    t = np.arange(len(tx)) / sps
    fig, ax = plt.subplots(figsize=(7.2, 3.2))
    idx = np.arange(0, len(tx), sps)
    ax.stem(idx / sps, tx[idx], linefmt="C2-", markerfmt="C2o", basefmt=" ",
            label="instantes de símbolo")
    ax.plot(t, tx, "C0-", lw=1.6, label="sinal formatado (RRC)")
    ax.set_xlabel("tempo (símbolos)")
    ax.set_ylabel("amplitude")
    ax.set_title(r"Formatação de pulso RRC, $\alpha=0{,}35$")
    ax.grid(alpha=0.3)
    ax.legend(loc="upper right", fontsize=8)
    fig.tight_layout()
    fig.savefig(os.path.join(destino, "demo_gr_pulse_shaping.pdf"))
    plt.close(fig)

    # (2) Diagrama de olho: efeito do roll-off alpha
    fig, axes = plt.subplots(1, 2, figsize=(7.4, 3.1), sharey=True)
    for ax, beta in zip(axes, [0.2, 0.9]):
        _, _, _, rx = simular(beta, sps, 0.0, seed=5)
        olho = segmentos_olho(rx, sps)
        tt = np.linspace(-1, 1, 2 * sps)
        for tr in olho:
            ax.plot(tt, tr, "C0-", lw=0.5, alpha=0.35)
        ax.axvline(0, color="C3", ls="--", lw=1)
        ax.set_title(rf"$\alpha={beta:.1f}$")
        ax.set_xlabel("tempo (símbolos)")
        ax.grid(alpha=0.3)
    axes[0].set_ylabel("amplitude")
    fig.suptitle("Diagrama de olho: roll-off menor fecha a abertura horizontal")
    fig.tight_layout()
    fig.savefig(os.path.join(destino, "demo_gr_eye_alpha.pdf"))
    plt.close(fig)

    # (3) Diagrama de olho: efeito do ruído do canal
    fig, axes = plt.subplots(1, 2, figsize=(7.4, 3.1), sharey=True)
    for ax, ru in zip(axes, [0.0, 0.25]):
        _, _, _, rx = simular(0.35, sps, ru, seed=7)
        olho = segmentos_olho(rx, sps)
        tt = np.linspace(-1, 1, 2 * sps)
        for tr in olho:
            ax.plot(tt, tr, "C0-", lw=0.5, alpha=0.35)
        ax.axvline(0, color="C3", ls="--", lw=1)
        ax.set_title("sem ruído" if ru == 0.0 else f"ruído = {ru}")
        ax.set_xlabel("tempo (símbolos)")
        ax.grid(alpha=0.3)
    axes[0].set_ylabel("amplitude")
    fig.suptitle("Diagrama de olho: ruído fecha a abertura vertical")
    fig.tight_layout()
    fig.savefig(os.path.join(destino, "demo_gr_eye_ruido.pdf"))
    plt.close(fig)

    print("Figuras salvas em:", destino)


# ------------------------------------------------------------------
# Modo interativo com sliders
# ------------------------------------------------------------------
def interativo():
    from matplotlib.widgets import Slider

    sps0, beta0, ruido0 = 8, 0.35, 0.0
    fig, (ax_t, ax_e) = plt.subplots(1, 2, figsize=(11, 4.2))
    plt.subplots_adjust(bottom=0.30, wspace=0.28)

    def desenhar(beta, sps, ruido):
        ax_t.clear(); ax_e.clear()
        _, _, tx, rx = simular(beta, sps, ruido, seed=1)
        t = np.arange(300) / sps
        ax_t.plot(t, tx[:300], "C0-", lw=1.3)
        ax_t.set_title("Sinal formatado (TX)")
        ax_t.set_xlabel("tempo (símbolos)"); ax_t.set_ylabel("amplitude")
        ax_t.grid(alpha=0.3)

        olho = segmentos_olho(rx, sps)
        tt = np.linspace(-1, 1, 2 * sps)
        for tr in olho:
            ax_e.plot(tt, tr, "C0-", lw=0.5, alpha=0.35)
        ax_e.axvline(0, color="C3", ls="--", lw=1)
        ax_e.set_title("Diagrama de olho (após filtro casado)")
        ax_e.set_xlabel("tempo (símbolos)")
        ax_e.set_ylim(-2.5, 2.5); ax_e.grid(alpha=0.3)
        fig.canvas.draw_idle()

    ax_beta = plt.axes([0.12, 0.17, 0.76, 0.03])
    ax_ruido = plt.axes([0.12, 0.10, 0.76, 0.03])
    ax_sps = plt.axes([0.12, 0.03, 0.76, 0.03])
    s_beta = Slider(ax_beta, "roll-off alpha", 0.0, 1.0, valinit=beta0, valstep=0.05)
    s_ruido = Slider(ax_ruido, "ruído (AWGN)", 0.0, 0.6, valinit=ruido0, valstep=0.02)
    s_sps = Slider(ax_sps, "amostras/símbolo", 4, 16, valinit=sps0, valstep=1)

    def atualizar(_):
        desenhar(s_beta.val, int(s_sps.val), s_ruido.val)

    s_beta.on_changed(atualizar)
    s_ruido.on_changed(atualizar)
    s_sps.on_changed(atualizar)
    desenhar(beta0, sps0, ruido0)
    plt.show()


if __name__ == "__main__":
    par = argparse.ArgumentParser(description=__doc__)
    par.add_argument("--salvar", metavar="DIR",
                     help="gera as figuras dos slides no diretório indicado")
    args = par.parse_args()
    if args.salvar:
        import matplotlib
        matplotlib.use("Agg")
        salvar_figuras(args.salvar)
    else:
        interativo()
