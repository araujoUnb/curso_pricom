#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Prática 01 – FFT e Análise Espectral: Gabarito do Professor
=============================================================
Reproduz em modo headless todas as etapas do enunciado e gera os valores
de referência das cinco tabelas quantitativas.

O espectro é calculado exatamente como o QT GUI Frequency Sink o exibe:

    mag_dB[k] = 10 log10( E{ |X[k]|^2 } / N^2 )

com as mesmas janelas do GNU Radio e sem normalização de potência de janela,
que é o padrão do bloco. A esperança é estimada pela média das potências de
blocos consecutivos, o que corresponde ao ajuste "Average: High" do painel de
controle usado pelo aluno durante as medições.

Execução:
    /usr/bin/python3 pratica_01_gabarito.py

Saída (na pasta pai deste script):
    figuras/          — PNGs de referência
    dados/            — CSVs com os valores de cada tabela
    relatorio.txt     — Gabarito completo em texto
"""

import os
import sys
import csv
import numpy as np
from datetime import datetime

try:
    from gnuradio import gr, analog, blocks
    from gnuradio.fft import window as gr_window
except ImportError:
    print("ERRO: GNU Radio não encontrado.")
    print("Execute com: /usr/bin/python3 pratica_01_gabarito.py")
    sys.exit(1)

try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
except ImportError:
    print("ERRO: matplotlib não encontrado.")
    sys.exit(1)

# =====================================================================
# CONFIGURAÇÃO — espelha os valores do enunciado
# =====================================================================
SAMP_RATE = 32000
N_SAMPLES = 262144          # blocos suficientes para a média de potência
FFT_DEFAULT = 1024

# Critérios numéricos definidos no enunciado
CRIT_VALE_DB = 3.0          # dois tons resolvidos se D >= 3 dB
CRIT_VISIVEL_DB = 6.0       # tom visível se SNR_disp >= 6 dB

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIG_DIR = os.path.join(BASE_DIR, "figuras")
DATA_DIR = os.path.join(BASE_DIR, "dados")

for d in [BASE_DIR, FIG_DIR, DATA_DIR]:
    os.makedirs(d, exist_ok=True)

relatorio = []


def log(msg=""):
    print(msg)
    relatorio.append(msg)


# =====================================================================
# FLOWGRAPH HEADLESS — mesma topologia do .grc da prática
# =====================================================================
class FlowgraphBase(gr.top_block):
    """sig_source(freq1, amp1) + sig_source(freq2, amp2) + ruído -> sink"""

    def __init__(self, sources, noise_amp=0.0, n_samples=N_SAMPLES):
        gr.top_block.__init__(self, "Pratica01")

        self._sources = [
            analog.sig_source_f(SAMP_RATE, analog.GR_COS_WAVE, f, a, 0)
            for f, a in sources
        ]

        if len(self._sources) == 1:
            signal_out = self._sources[0]
        else:
            self.add_sig = blocks.add_ff()
            for i, src in enumerate(self._sources):
                self.connect(src, (self.add_sig, i))
            signal_out = self.add_sig

        if noise_amp > 0:
            self.noise = analog.noise_source_f(analog.GR_GAUSSIAN, noise_amp)
            self.add_noise = blocks.add_ff()
            self.connect(signal_out, (self.add_noise, 0))
            self.connect(self.noise, (self.add_noise, 1))
            final_out = self.add_noise
        else:
            final_out = signal_out

        self.head = blocks.head(gr.sizeof_float, n_samples)
        self.sink = blocks.vector_sink_f()
        self.connect(final_out, self.head, self.sink)


def capture(sources, noise_amp=0.0, n_samples=N_SAMPLES):
    tb = FlowgraphBase(sources, noise_amp, n_samples)
    tb.run()
    return np.array(tb.sink.data())


# =====================================================================
# ESPECTRO — idêntico ao exibido pelo QT GUI Frequency Sink
# =====================================================================
WINDOWS = {
    'Rectangular': gr_window.rectangular,
    'Hann': gr_window.hann,
    'Hamming': gr_window.hamming,
    'Blackman-harris': gr_window.blackman_harris,
}


def spectrum(data, fft_size, wname='Hann'):
    """Média de potência sobre blocos consecutivos, em dB.

    Retorna (freqs_Hz, mag_dB) apenas para a faixa 0..fs/2, que é o que o
    bloco exibe com Spectrum Width = Half.
    """
    w = np.array(WINDOWS[wname](fft_size))
    nblocks = max(1, len(data) // fft_size)
    acc = np.zeros(fft_size // 2 + 1)
    for b in range(nblocks):
        seg = data[b * fft_size:(b + 1) * fft_size]
        acc += np.abs(np.fft.rfft(seg * w)) ** 2
    acc /= nblocks
    mag = 10 * np.log10(acc / fft_size ** 2 + 1e-30)
    freqs = np.fft.rfftfreq(fft_size, 1.0 / SAMP_RATE)
    return freqs, mag


def nivel_em(freqs, mag, f_hz):
    """Nível em dB no índice espectral mais próximo de f_hz."""
    return float(mag[np.argmin(np.abs(freqs - f_hz))])


def freq_do_pico(freqs, mag, f_alvo, janela_hz=400):
    """Frequência e nível do máximo local em torno de f_alvo."""
    sel = np.abs(freqs - f_alvo) <= janela_hz
    idx = np.where(sel)[0]
    j = idx[np.argmax(mag[idx])]
    return float(freqs[j]), float(mag[j])


def piso_de_ruido(freqs, mag, tons, margem=400, f_min=4000, f_max=15000):
    """Nível mediano do piso em uma região livre de tons."""
    mask = (freqs >= f_min) & (freqs <= f_max)
    for f in tons:
        mask &= np.abs(freqs - f) > margem
    return float(np.median(mag[mask])) if np.any(mask) else float('nan')


def metricas_do_vale(freqs, mag, f1, f2):
    """A_min, V e D = A_min - V entre os dois picos, conforme o enunciado."""
    _, a1 = freq_do_pico(freqs, mag, f1, janela_hz=abs(f2 - f1) / 2)
    _, a2 = freq_do_pico(freqs, mag, f2, janela_hz=abs(f2 - f1) / 2)
    a_min = min(a1, a2)

    i1 = int(np.argmin(np.abs(freqs - f1)))
    i2 = int(np.argmin(np.abs(freqs - f2)))
    if i2 - i1 < 2:
        # picos fundidos em um único lóbulo: não existe vale
        return a_min, a_min, 0.0
    v = float(np.min(mag[i1:i2 + 1]))
    return a_min, v, a_min - v


def largura_3db(freqs, mag, i_pico):
    """Largura do lóbulo principal a -3 dB, com interpolação linear em dB."""
    alvo = mag[i_pico] - 3.0

    def cruzamento(passo):
        i = i_pico
        while 0 < i < len(mag) - 1 and mag[i] > alvo:
            i += passo
        if mag[i] > alvo:
            return float(freqs[i])
        # interpola entre i e i - passo
        f_a, m_a = freqs[i - passo], mag[i - passo]
        f_b, m_b = freqs[i], mag[i]
        t = (alvo - m_a) / (m_b - m_a)
        return float(f_a + t * (f_b - f_a))

    return cruzamento(+1) - cruzamento(-1)


# Faixa excluída em torno do tom para a leitura do maior lóbulo lateral.
# Com N = 1024 e fs = 32 kHz, 300 Hz correspondem a 9,6 índices, o que deixa
# de fora o lóbulo principal de todas as janelas comparadas, inclusive a
# Blackman-harris, cujo lóbulo principal ocupa cerca de 8 índices.
EXCLUSAO_LOBULO_HZ = 300.0


def maior_lobulo_lateral(freqs, mag, f_tom):
    """Maior nível fora da faixa f_tom +- EXCLUSAO_LOBULO_HZ.

    O espectro amostrado de um tom que não cai sobre um índice não apresenta
    mínimos locais junto ao lóbulo principal, porque os nulos da janela ficam
    entre as amostras. Por isso a fronteira do lóbulo principal é definida por
    uma faixa fixa, que é também a regra de leitura dada ao aluno.
    """
    fora = np.abs(freqs - f_tom) > EXCLUSAO_LOBULO_HZ
    return float(np.max(mag[fora])) if np.any(fora) else float('nan')


def snr_banda_larga(amp, sigma):
    """SNR de banda larga da equação do enunciado, em dB."""
    if sigma <= 0:
        return float('inf')
    return 10 * np.log10((amp ** 2 / 2.0) / sigma ** 2)


def save_csv(filename, header, rows):
    path = os.path.join(DATA_DIR, filename)
    with open(path, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)
    return path


plt.rcParams.update({
    'figure.facecolor': 'white',
    'axes.grid': True,
    'grid.alpha': 0.3,
    'font.size': 10,
})


def plot_tempo_espectro(data, fft_size, title, filename,
                        wname='Hann', t_ms=5, marcadores=None):
    fig, (ax_t, ax_f) = plt.subplots(1, 2, figsize=(15, 4.5))

    n_pts = int(t_ms * SAMP_RATE / 1000)
    t = np.arange(n_pts) / SAMP_RATE * 1000
    ax_t.plot(t, data[:n_pts], linewidth=0.8, color='#1f77b4')
    ax_t.set_xlabel('Tempo (ms)')
    ax_t.set_ylabel('Amplitude')
    ax_t.set_title('Domínio do tempo')

    freqs, mag = spectrum(data, fft_size, wname)
    ax_f.plot(freqs, mag, linewidth=0.8, color='#1f77b4')
    ax_f.set_xlabel('Frequência (Hz)')
    ax_f.set_ylabel('Magnitude (dB)')
    ax_f.set_title(f'Espectro (N={fft_size}, {wname})')
    ax_f.set_xlim([0, SAMP_RATE / 2])
    ax_f.set_ylim([-140, 10])

    if marcadores:
        cores = ['#d62728', '#2ca02c', '#ff7f0e', '#9467bd']
        for i, (mf, rotulo) in enumerate(marcadores):
            ax_f.axvline(mf, color=cores[i % len(cores)], ls='--',
                         alpha=0.6, label=rotulo)
        ax_f.legend(fontsize=8)

    fig.suptitle(title, fontsize=13, fontweight='bold')
    plt.tight_layout()
    path = os.path.join(FIG_DIR, filename)
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    return path


# =====================================================================
# ETAPA 1
# =====================================================================
def etapa1():
    log("\n" + "=" * 70)
    log("ETAPA 1: Configuração inicial — tom único de 1 kHz")
    log("=" * 70)

    data = capture([(1000, 1.0)])
    plot_tempo_espectro(data, FFT_DEFAULT,
                        "Etapa 1: tom único de 1 kHz",
                        "etapa1_tom_1kHz.png",
                        marcadores=[(1000, '1 kHz')])

    freqs, mag = spectrum(data, FFT_DEFAULT)
    f_pico, a_pico = freq_do_pico(freqs, mag, 1000)
    log(f"  Pico em {f_pico:.1f} Hz com nível {a_pico:.1f} dB")
    log(f"  Nível previsto para amp1 = 1,0 com janela Hann: "
        f"20 log10(amp1 * sum(w) / 2N) = -12,0 dB")
    log(f"  Resultado: {'OK' if abs(f_pico - 1000) < 32 else 'FALHA'}")
    log("  -> figuras/etapa1_tom_1kHz.png")
    return data


# =====================================================================
# ETAPA 2 — Tabela 3 do enunciado
# =====================================================================
def etapa2():
    log("\n" + "=" * 70)
    log("ETAPA 2: Tom único e posição do pico")
    log("=" * 70)

    freqs_teste = [500, 1000, 2000, 4000]
    fig, axes = plt.subplots(2, 2, figsize=(15, 9))
    linhas = []

    log(f"\n  {'f1 (Hz)':>8} | {'k = f1*N/fs':>12} | {'fk (Hz)':>9} | "
        f"{'pico lido (Hz)':>15} | {'nivel (dB)':>11}")
    log(f"  {'-'*8}-+-{'-'*12}-+-{'-'*9}-+-{'-'*15}-+-{'-'*11}")

    for ax, f1 in zip(axes.flat, freqs_teste):
        data = capture([(f1, 1.0)])
        fr, mag = spectrum(data, FFT_DEFAULT)

        k = f1 * FFT_DEFAULT / SAMP_RATE
        fk = round(k) * SAMP_RATE / FFT_DEFAULT
        f_pico, a_pico = freq_do_pico(fr, mag, f1)

        log(f"  {f1:>8} | {k:>12.1f} | {fk:>9.1f} | {f_pico:>15.1f} | "
            f"{a_pico:>11.1f}")
        linhas.append([f1, f"{k:.1f}", f"{fk:.1f}", f"{f_pico:.1f}",
                       f"{a_pico:.1f}"])

        ax.plot(fr, mag, linewidth=0.8)
        ax.axvline(f1, color='r', ls='--', alpha=0.5)
        ax.set_title(f'f1 = {f1} Hz  ->  k = {k:.0f}, pico em {f_pico:.0f} Hz')
        ax.set_xlabel('Frequência (Hz)')
        ax.set_ylabel('dB')
        ax.set_xlim([0, SAMP_RATE / 2])
        ax.set_ylim([-140, 10])

    plt.suptitle("Etapa 2: posição do pico em função da frequência",
                 fontsize=13, fontweight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, "etapa2_variacao_freq.png"),
                dpi=150, bbox_inches='tight')
    plt.close()

    save_csv("etapa2_freq_vs_bin.csv",
             ["f1_Hz", "k_calculado", "fk_Hz", "pico_lido_Hz", "nivel_dB"],
             linhas)

    log("\n  -> figuras/etapa2_variacao_freq.png")
    log("  -> dados/etapa2_freq_vs_bin.csv")
    log("\n  Q1: as quatro frequências são múltiplos exatos de "
        f"Δf = {SAMP_RATE/FFT_DEFAULT:.2f} Hz, portanto k é inteiro e o pico")
    log("  lido coincide com f1. Uma frequência que não seja múltipla de Δf")
    log("  aparece no índice mais próximo, com erro de leitura de até Δf/2 = "
        f"{SAMP_RATE/FFT_DEFAULT/2:.2f} Hz.")


# =====================================================================
# ETAPA 3
# =====================================================================
def etapa3():
    log("\n" + "=" * 70)
    log("ETAPA 3: Sinal com dois tons — 1000 Hz e 2500 Hz")
    log("=" * 70)

    amp1, amp2 = 1.0, 0.5
    data = capture([(1000, amp1), (2500, amp2)])
    plot_tempo_espectro(data, FFT_DEFAULT,
                        "Etapa 3: dois tons, amp1 = 1,0 e amp2 = 0,5",
                        "etapa3_dois_tons.png",
                        marcadores=[(1000, 'f1 = 1 kHz'),
                                    (2500, 'f2 = 2,5 kHz')])

    freqs, mag = spectrum(data, FFT_DEFAULT)
    a1 = nivel_em(freqs, mag, 1000)
    a2 = nivel_em(freqs, mag, 2500)
    previsto = 20 * np.log10(amp1 / amp2)

    log(f"  Tom 1: 1000 Hz, amp1 = {amp1} -> {a1:.1f} dB")
    log(f"  Tom 2: 2500 Hz, amp2 = {amp2} -> {a2:.1f} dB")
    log(f"  Diferença medida: {a1 - a2:.1f} dB")
    log(f"  Diferença prevista por 20 log10(amp1/amp2): {previsto:.1f} dB")

    save_csv("etapa3_dois_tons.csv",
             ["f_Hz", "amplitude", "nivel_dB"],
             [[1000, amp1, f"{a1:.1f}"], [2500, amp2, f"{a2:.1f}"]])

    log("  -> figuras/etapa3_dois_tons.png")
    log("  -> dados/etapa3_dois_tons.csv")
    log("\n  Q3: a transformada é linear, logo X[k] = X1[k] + X2[k]. Como as")
    log("  duas frequências caem em índices distintos, cada pico conserva o")
    log("  nível que teria isoladamente e a diferença entre eles reproduz")
    log("  20 log10(amp1/amp2). Um elemento não linear no caminho geraria")
    log("  harmônicos e produtos de intermodulação em 1500 Hz, 3500 Hz e")
    log("  outras combinações de f1 e f2, que não aparecem aqui.")
    return data


# =====================================================================
# ETAPA 4 — Tabela 4 do enunciado, critério D >= 3 dB
# =====================================================================
def etapa4():
    log("\n" + "=" * 70)
    log("ETAPA 4: Resolução espectral — critério da profundidade do vale")
    log("=" * 70)

    f1, f2 = 1000.0, 1200.0
    data = capture([(f1, 1.0), (f2, 1.0)])

    fft_sizes = [256, 512, 1024, 2048, 4096]
    fig, axes = plt.subplots(len(fft_sizes), 1,
                             figsize=(12, 2.9 * len(fft_sizes)))
    linhas = []

    log(f"\n  Tons em {f1:.0f} Hz e {f2:.0f} Hz com amplitudes iguais, "
        f"janela Hann, sem ruído")
    log(f"  Critério: resolvidos se D = A_min - V >= {CRIT_VALE_DB:.0f} dB\n")
    log(f"  {'N':>6} | {'Δf (Hz)':>8} | {'Δk':>6} | {'A_min (dB)':>11} | "
        f"{'V (dB)':>9} | {'D (dB)':>8} | {'D>=3 dB':>8}")
    log(f"  {'-'*6}-+-{'-'*8}-+-{'-'*6}-+-{'-'*11}-+-{'-'*9}-+-{'-'*8}-+-"
        f"{'-'*8}")

    for ax, N in zip(axes, fft_sizes):
        df = SAMP_RATE / N
        dk = abs(f2 - f1) / df
        fr, mag = spectrum(data, N)
        a_min, v, d = metricas_do_vale(fr, mag, f1, f2)
        resolvido = "Sim" if d >= CRIT_VALE_DB else "Não"

        log(f"  {N:>6} | {df:>8.2f} | {dk:>6.2f} | {a_min:>11.1f} | "
            f"{v:>9.1f} | {d:>8.1f} | {resolvido:>8}")
        linhas.append([N, f"{df:.2f}", f"{dk:.2f}", f"{a_min:.1f}",
                       f"{v:.1f}", f"{d:.1f}", resolvido])

        ax.plot(fr, mag, linewidth=0.9)
        ax.axvline(f1, color='r', ls='--', alpha=0.4)
        ax.axvline(f2, color='g', ls='--', alpha=0.4)
        ax.axhline(a_min, color='k', ls=':', alpha=0.5)
        ax.axhline(v, color='m', ls=':', alpha=0.5)
        ax.set_xlim([700, 1500])
        ax.set_ylim([-140, 10])
        ax.set_title(f'N = {N}   Δf = {df:.2f} Hz   Δk = {dk:.2f}   '
                     f'D = {d:.1f} dB   resolvidos: {resolvido}')
        ax.set_ylabel('dB')

    axes[-1].set_xlabel('Frequência (Hz)')
    plt.suptitle("Etapa 4: resolução espectral — tons de 1000 e 1200 Hz",
                 fontsize=13, fontweight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, "etapa4_resolucao_fft.png"),
                dpi=150, bbox_inches='tight')
    plt.close()

    save_csv("etapa4_resolucao.csv",
             ["N", "delta_f_Hz", "delta_k", "A_min_dB", "V_dB", "D_dB",
              "resolvido"],
             linhas)

    log("\n  -> figuras/etapa4_resolucao_fft.png")
    log("  -> dados/etapa4_resolucao.csv")

    # Menor N que satisfaz o critério e o Δk correspondente
    n_ok = next((int(r[0]) for r in linhas if r[6] == "Sim"), None)
    dk_ok = next((float(r[2]) for r in linhas if r[6] == "Sim"), None)

    log("\n  Q2:")
    log(f"  Menor N que satisfaz D >= {CRIT_VALE_DB:.0f} dB: N = {n_ok}, "
        f"com Δk = {dk_ok:.2f}.")
    log(f"  Com N = 256 tem-se Δk = {linhas[0][2]}, ou seja, os dois tons caem")
    log("  dentro do mesmo lóbulo principal da janela Hann, cuja largura é de")
    log("  aproximadamente 4 índices. Por isso o vale não atinge 3 dB.")
    log(f"  Para tons separados de 100 Hz, exigir o mesmo Δk = {dk_ok:.2f} dá")
    n_100 = SAMP_RATE * dk_ok / 100.0
    log(f"    N >= Δk * fs / 100 = {dk_ok:.2f} * {SAMP_RATE} / 100 = "
        f"{n_100:.0f}  ->  N = 1024 como potência de 2.")
    log("  O limite ingênuo Δf <= 100 Hz daria N >= 320, ou seja N = 512, que")
    log("  é insuficiente: ele garante um índice de separação, mas não a")
    log("  profundidade de vale exigida pelo critério.")
    return linhas


# =====================================================================
# ETAPA 5 — Tabela 5 do enunciado
# =====================================================================
def etapa5():
    log("\n" + "=" * 70)
    log("ETAPA 5: Efeito do ruído gaussiano")
    log("=" * 70)

    amp1, amp2 = 1.0, 0.5
    f1, f2 = 1000.0, 2500.0
    sigmas = [0.5, 1.0, 2.0, 5.0, 10.0]

    fig, axes = plt.subplots(2, 3, figsize=(17, 9))
    linhas = []

    log(f"\n  f1 = {f1:.0f} Hz com amp1 = {amp1}, "
        f"f2 = {f2:.0f} Hz com amp2 = {amp2}, N = {FFT_DEFAULT}, janela Hann")
    log(f"  Critério de visibilidade: SNR_disp >= {CRIT_VISIVEL_DB:.0f} dB\n")
    log(f"  {'sigma':>6} | {'SNR1 (dB)':>10} | {'SNR2 (dB)':>10} | "
        f"{'P (dB)':>8} | {'A2 (dB)':>8} | {'A2-P (dB)':>10} | "
        f"{'tom 2':>10}")
    log(f"  {'-'*6}-+-{'-'*10}-+-{'-'*10}-+-{'-'*8}-+-{'-'*8}-+-{'-'*10}-+-"
        f"{'-'*10}")

    # painel extra sem ruído para referência visual
    dados_ref = capture([(f1, amp1), (f2, amp2)], noise_amp=0.0)
    fr, mag = spectrum(dados_ref, FFT_DEFAULT)
    axes.flat[0].plot(fr, mag, linewidth=0.6)
    axes.flat[0].set_title('noise_amp = 0 (referência)')
    axes.flat[0].set_xlim([0, SAMP_RATE / 2])
    axes.flat[0].set_ylim([-140, 10])
    axes.flat[0].set_xlabel('Frequência (Hz)')
    axes.flat[0].set_ylabel('dB')

    for ax, sigma in zip(list(axes.flat)[1:], sigmas):
        data = capture([(f1, amp1), (f2, amp2)], noise_amp=sigma)
        fr, mag = spectrum(data, FFT_DEFAULT)

        snr1 = snr_banda_larga(amp1, sigma)
        snr2 = snr_banda_larga(amp2, sigma)
        p = piso_de_ruido(fr, mag, [f1, f2])
        a2 = nivel_em(fr, mag, f2)
        snr_disp2 = a2 - p
        visivel = "visível" if snr_disp2 >= CRIT_VISIVEL_DB else "MASCARADO"

        log(f"  {sigma:>6.1f} | {snr1:>10.1f} | {snr2:>10.1f} | "
            f"{p:>8.1f} | {a2:>8.1f} | {snr_disp2:>10.1f} | {visivel:>10}")
        linhas.append([sigma, f"{snr1:.1f}", f"{snr2:.1f}", f"{p:.1f}",
                       f"{a2:.1f}", f"{snr_disp2:.1f}", visivel])

        ax.plot(fr, mag, linewidth=0.6)
        ax.axvline(f1, color='r', ls='--', alpha=0.3)
        ax.axvline(f2, color='g', ls='--', alpha=0.3)
        ax.axhline(p, color='k', ls=':', alpha=0.6)
        ax.set_title(f'noise_amp = {sigma}   A2 - P = {snr_disp2:.1f} dB')
        ax.set_xlabel('Frequência (Hz)')
        ax.set_ylabel('dB')
        ax.set_xlim([0, SAMP_RATE / 2])
        ax.set_ylim([-140, 10])

    plt.suptitle("Etapa 5: efeito do ruído gaussiano sobre o segundo tom",
                 fontsize=13, fontweight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, "etapa5_ruido.png"),
                dpi=150, bbox_inches='tight')
    plt.close()

    save_csv("etapa5_ruido.csv",
             ["sigma", "SNR1_dB", "SNR2_dB", "piso_P_dB", "A2_dB",
              "SNR_disp2_dB", "tom2"],
             linhas)

    log("\n  -> figuras/etapa5_ruido.png")
    log("  -> dados/etapa5_ruido.csv")

    # limiar de sigma em que o tom 2 cruza o critério
    sig_ref = 1.0
    ref = next(r for r in linhas if float(r[0]) == sig_ref)
    snr_disp_ref = float(ref[5])
    sigma_limite = sig_ref * 10 ** ((snr_disp_ref - CRIT_VISIVEL_DB) / 20.0)
    ganho_proc = snr_disp_ref - float(ref[2])

    log("\n  Q4:")
    log(f"  O tom 2 satisfaz o critério até sigma = 2,0 e o perde em "
        f"sigma = 5,0.")
    log(f"  Como A2 - P cai 20 log10(sigma), o limiar exato é "
        f"sigma = {sigma_limite:.1f}.")
    log(f"  Em sigma = 1,0 a SNR de banda larga do tom 2 vale "
        f"{float(ref[2]):.1f} dB, enquanto")
    log(f"  a SNR do display vale {snr_disp_ref:.1f} dB. A diferença de "
        f"{ganho_proc:.1f} dB é o ganho")
    log("  de processamento da FFT: o tom se concentra em um único índice,")
    log("  enquanto o ruído se distribui pelos N/2 índices da faixa exibida.")
    log("  Dobrar o FFT Size reduz o piso em 3 dB e aumenta a SNR do display")
    log("  em 3 dB, sem alterar a SNR de banda larga.")
    return linhas


# =====================================================================
# ETAPA 6 — Tabela 6 do enunciado
# =====================================================================
def etapa6():
    log("\n" + "=" * 70)
    log("ETAPA 6: Funções de janela e vazamento espectral")
    log("=" * 70)

    f_off = 1050.0    # não coincide com nenhum índice para N = 1024
    f_on = 1000.0     # coincide com o índice k = 32
    df = SAMP_RATE / FFT_DEFAULT

    dados_off = capture([(f_off, 1.0)])
    dados_on = capture([(f_on, 1.0)])

    # Demonstração de que 1000 Hz não produz vazamento com janela retangular
    fr_on, mag_on = spectrum(dados_on, FFT_DEFAULT, 'Rectangular')
    i_on = int(np.argmax(mag_on))
    l_on = maior_lobulo_lateral(fr_on, mag_on, f_on)
    fr_off, mag_off = spectrum(dados_off, FFT_DEFAULT, 'Rectangular')
    i_off = int(np.argmax(mag_off))
    l_off = maior_lobulo_lateral(fr_off, mag_off, f_off)

    log(f"\n  Δf = {df:.2f} Hz para N = {FFT_DEFAULT}")
    log(f"  f = {f_on:.0f} Hz  ->  k = {f_on/df:.1f}, índice exato. "
        f"Com janela retangular o vazamento")
    log(f"    cai para {l_on:.1f} dB, valor que corresponde ao piso numérico "
        f"do cálculo e fica")
    log(f"    muito abaixo do piso do gráfico: na prática não há vazamento.")
    log(f"  f = {f_off:.0f} Hz  ->  k = {f_off/df:.1f}, entre dois índices. "
        f"O maior lóbulo lateral")
    log(f"    sobe para {l_off:.1f} dB, a apenas "
        f"{mag_off[i_off]-l_off:.1f} dB do pico.")
    log("  É por isso que a Etapa 6 usa 1050 Hz e não 1000 Hz.")

    fig, axes = plt.subplots(2, 2, figsize=(15, 9))
    linhas = []

    log(f"\n  Tom em {f_off:.0f} Hz, N = {FFT_DEFAULT}, sem ruído\n")
    log(f"  {'Janela':>16} | {'A_pico (dB)':>12} | {'L (dB)':>9} | "
        f"{'S (dB)':>8} | {'larg -3 dB (Hz)':>16}")
    log(f"  {'-'*16}-+-{'-'*12}-+-{'-'*9}-+-{'-'*8}-+-{'-'*16}")

    for ax, wname in zip(axes.flat, WINDOWS.keys()):
        fr, mag = spectrum(dados_off, FFT_DEFAULT, wname)
        i_pico = int(np.argmax(mag))
        a_pico = float(mag[i_pico])
        l = maior_lobulo_lateral(fr, mag, f_off)
        s = a_pico - l
        larg = largura_3db(fr, mag, i_pico)

        log(f"  {wname:>16} | {a_pico:>12.1f} | {l:>9.1f} | {s:>8.1f} | "
            f"{larg:>16.1f}")
        linhas.append([wname, f"{a_pico:.1f}", f"{l:.1f}", f"{s:.1f}",
                       f"{larg:.1f}"])

        ax.plot(fr, mag, linewidth=0.8)
        ax.axhline(a_pico, color='k', ls=':', alpha=0.5)
        ax.axhline(l, color='m', ls=':', alpha=0.5)
        ax.set_title(f'{wname}:  S = {s:.1f} dB,  '
                     f'largura a -3 dB = {larg:.1f} Hz')
        ax.set_xlabel('Frequência (Hz)')
        ax.set_ylabel('dB')
        ax.set_xlim([0, 4000])
        ax.set_ylim([-140, 10])

    plt.suptitle("Etapa 6: funções de janela — tom em 1050 Hz, fora do índice",
                 fontsize=13, fontweight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, "etapa6_janelas.png"),
                dpi=150, bbox_inches='tight')
    plt.close()

    save_csv("etapa6_janelas.csv",
             ["janela", "A_pico_dB", "L_dB", "S_dB", "largura_3dB_Hz"],
             linhas)

    log("\n  -> figuras/etapa6_janelas.png")
    log("  -> dados/etapa6_janelas.csv")

    por_s = sorted(linhas, key=lambda r: float(r[3]), reverse=True)
    por_larg = sorted(linhas, key=lambda r: float(r[4]))
    maior_pico = max(linhas, key=lambda r: float(r[1]))

    log("\n  Q5:")
    log("  Ordem por supressão S, do maior para o menor: "
        + " > ".join(f"{r[0]} ({float(r[3]):.0f} dB)" for r in por_s))
    log("  Ordem por largura do lóbulo principal, da menor para a maior: "
        + " < ".join(f"{r[0]} ({float(r[4]):.0f} Hz)" for r in por_larg))
    log(f"  Maior nível de pico: {maior_pico[0]} com "
        f"{float(maior_pico[1]):.1f} dB.")
    log("  As duas propriedades são opostas porque suprimir lóbulos laterais")
    log("  exige suavizar as bordas do bloco, o que reduz a energia efetiva")
    log("  da janela e alarga o lóbulo principal. A janela retangular tem o")
    log("  lóbulo mais estreito e o pico mais alto, mas a pior supressão; a")
    log("  Blackman-harris faz o oposto. Hann e Hamming ficam entre as duas.")
    return linhas


# =====================================================================
# TABELA DE PARÂMETROS — três cenários
# =====================================================================
def tabela_parametros():
    log("\n" + "=" * 70)
    log("TABELA DE PARÂMETROS — três cenários de referência")
    log("=" * 70)

    linhas = [
        ("freq1 (Hz)",     "1000",  "1000",  "1000"),
        ("freq2 (Hz)",     "—",     "2500",  "2500"),
        ("amp1",           "1,0",   "1,0",   "1,0"),
        ("amp2",           "0",     "0,5",   "0,5"),
        ("samp_rate (Hz)", "32000", "32000", "32000"),
        ("FFT Size",       "1024",  "1024",  "1024"),
        ("noise_amp",      "0",     "0",     "5,0"),
        ("FFT Window",     "Hann",  "Hann",  "Hann"),
    ]

    log(f"  {'Parâmetro':<18} | {'Cenário A':>10} | {'Cenário B':>10} | "
        f"{'Cenário C':>10}")
    log(f"  {'-'*18}-+-{'-'*10}-+-{'-'*10}-+-{'-'*10}")
    for nome, a, b, c in linhas:
        log(f"  {nome:<18} | {a:>10} | {b:>10} | {c:>10}")

    save_csv("tabela_parametros.csv",
             ["parametro", "cenario_A", "cenario_B", "cenario_C"],
             [list(r) for r in linhas])

    cenarios = [
        ("Cenário A: tom único", [(1000, 1.0)], 0.0,
         "cenario_A_tom_unico.png", [(1000, 'f1')]),
        ("Cenário B: dois tons sem ruído", [(1000, 1.0), (2500, 0.5)], 0.0,
         "cenario_B_dois_tons.png", [(1000, 'f1'), (2500, 'f2')]),
        ("Cenário C: dois tons com ruído, noise_amp = 5,0",
         [(1000, 1.0), (2500, 0.5)], 5.0,
         "cenario_C_dois_tons_ruido.png", [(1000, 'f1'), (2500, 'f2')]),
    ]

    for titulo, fontes, na, arquivo, marcadores in cenarios:
        data = capture(fontes, noise_amp=na)
        plot_tempo_espectro(data, FFT_DEFAULT, titulo, arquivo,
                            marcadores=marcadores)
        log(f"  -> figuras/{arquivo}")


# =====================================================================
# MAIN
# =====================================================================
if __name__ == '__main__':
    log("=" * 70)
    log("PRÁTICA 01 — FFT E ANÁLISE ESPECTRAL")
    log("GABARITO DO PROFESSOR")
    log(f"Data: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    log(f"GNU Radio: {gr.version()}")
    log(f"Taxa de amostragem: {SAMP_RATE} Hz | amostras por captura: "
        f"{N_SAMPLES}")
    log(f"Espectro: média de potência entre blocos, equivalente a "
        f"Average = High")
    log(f"Saída: {BASE_DIR}")
    log("=" * 70)

    etapa1()
    etapa2()
    etapa3()
    etapa4()
    etapa5()
    etapa6()
    tabela_parametros()

    log("\n" + "=" * 70)
    log("GABARITO COMPLETO GERADO COM SUCESSO")
    log("=" * 70)

    report_path = os.path.join(BASE_DIR, "relatorio.txt")
    with open(report_path, 'w') as f:
        f.write('\n'.join(relatorio) + '\n')
    print(f"\nRelatório salvo em: {report_path}")
