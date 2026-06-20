#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pratica 05 -- Modulacao FM e Regra de Carson: Gabarito do Professor
====================================================================
Executa o flowgraph da Pratica 05 em modo headless (sem GUI),
reproduzindo todas as etapas do enunciado e gerando:

  1. Figuras PNG de referencia (espectro FM, comparacoes)
  2. Dados numericos (tabela de Carson, SNR)
  3. Relatorio resumo em texto

Execucao:
    /usr/bin/python3 pratica_05_gabarito.py

Saida:
    ./pratica_05_gabarito/
        figuras/          -- PNGs de referencia
        dados/            -- CSVs com dados brutos
        relatorio.txt     -- Relatorio completo
"""

import os
import sys
import csv
import numpy as np
from datetime import datetime

try:
    from gnuradio import gr, analog, blocks
except ImportError:
    print("ERRO: GNU Radio nao encontrado.")
    print("Execute com: /usr/bin/python3 pratica_05_gabarito.py")
    sys.exit(1)

try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
except ImportError:
    print("ERRO: matplotlib nao encontrado.")
    sys.exit(1)

# =====================================================================
# CONFIGURACAO
# =====================================================================
SAMP_RATE = 480000       # Taxa de amostragem do sinal FM (quad_rate)
AUDIO_RATE = 48000       # Taxa de amostragem do audio
INTERP = SAMP_RATE // AUDIO_RATE  # = 10
FM_FREQ = 2000           # Frequencia da mensagem (Hz)
MAX_DEV = 5000           # Desvio maximo de frequencia (Hz)
MSG_AMP = 1.0            # Amplitude da mensagem

N_SAMPLES_AUDIO = 48000  # Amostras de audio (~1 s)
N_SAMPLES_FM = N_SAMPLES_AUDIO * INTERP  # Amostras FM
FFT_SIZE = 8192

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIG_DIR = os.path.join(BASE_DIR, "figuras")
DATA_DIR = os.path.join(BASE_DIR, "dados")

for d in [BASE_DIR, FIG_DIR, DATA_DIR]:
    os.makedirs(d, exist_ok=True)

# Acumula linhas do relatorio
relatorio = []


def log(msg=""):
    """Imprime e acumula no relatorio."""
    print(msg)
    relatorio.append(msg)


# =====================================================================
# FLOWGRAPHS HEADLESS
# =====================================================================
class FMModulatorFlowgraph(gr.top_block):
    """Gera sinal FM: fonte senoidal -> modulador FM -> captura complexa."""

    def __init__(self, fm=FM_FREQ, max_dev=MAX_DEV, amp=MSG_AMP,
                 n_samples=N_SAMPLES_FM):
        gr.top_block.__init__(self, "FM_Modulator")

        sensitivity = 2 * np.pi * max_dev / SAMP_RATE

        # Fonte de mensagem na taxa de amostragem FM (para evitar
        # problemas de interpolacao)
        self.msg_source = analog.sig_source_f(
            SAMP_RATE, analog.GR_COS_WAVE, fm, amp, 0)

        # Modulador FM
        self.fm_mod = analog.frequency_modulator_fc(sensitivity)

        # Captura
        self.head = blocks.head(gr.sizeof_gr_complex, n_samples)
        self.sink = blocks.vector_sink_c()

        self.connect(self.msg_source, self.fm_mod, self.head, self.sink)


class FMTransceiverFlowgraph(gr.top_block):
    """Modula e demodula FM: fonte -> mod FM -> demod FM -> captura."""

    def __init__(self, fm=FM_FREQ, max_dev=MAX_DEV, amp=MSG_AMP,
                 noise_amp=0.0, n_samples=N_SAMPLES_FM):
        gr.top_block.__init__(self, "FM_Transceiver")

        sensitivity = 2 * np.pi * max_dev / SAMP_RATE
        demod_gain = SAMP_RATE / (2 * np.pi * max_dev)

        # Fonte de mensagem
        self.msg_source = analog.sig_source_f(
            SAMP_RATE, analog.GR_COS_WAVE, fm, amp, 0)

        # Modulador FM
        self.fm_mod = analog.frequency_modulator_fc(sensitivity)

        # Adicionar ruido complexo (se solicitado)
        if noise_amp > 0:
            self.noise = analog.noise_source_c(
                analog.GR_GAUSSIAN, noise_amp)
            self.adder = blocks.add_cc()
            self.connect(self.fm_mod, (self.adder, 0))
            self.connect(self.noise, (self.adder, 1))
            fm_out = self.adder
        else:
            fm_out = self.fm_mod

        # Demodulador FM
        self.fm_demod = analog.quadrature_demod_cf(demod_gain)

        # Captura do sinal demodulado (float)
        self.head = blocks.head(gr.sizeof_float, n_samples)
        self.sink = blocks.vector_sink_f()

        self.connect(self.msg_source, self.fm_mod)
        self.connect(fm_out, self.fm_demod, self.head, self.sink)

        # Captura da mensagem original (float) para comparacao
        self.head_orig = blocks.head(gr.sizeof_float, n_samples)
        self.sink_orig = blocks.vector_sink_f()
        self.connect(self.msg_source, self.head_orig, self.sink_orig)

        # Captura do sinal FM complexo (para analise espectral)
        self.head_fm = blocks.head(gr.sizeof_gr_complex, n_samples)
        self.sink_fm = blocks.vector_sink_c()
        self.connect(fm_out, self.head_fm, self.sink_fm)


def capture_fm(fm=FM_FREQ, max_dev=MAX_DEV, amp=MSG_AMP,
               n_samples=N_SAMPLES_FM):
    """Captura sinal FM complexo."""
    tb = FMModulatorFlowgraph(fm, max_dev, amp, n_samples)
    tb.run()
    return np.array(tb.sink.data())


def capture_fm_transceiver(fm=FM_FREQ, max_dev=MAX_DEV, amp=MSG_AMP,
                           noise_amp=0.0, n_samples=N_SAMPLES_FM):
    """Captura sinal original, FM e demodulado."""
    tb = FMTransceiverFlowgraph(fm, max_dev, amp, noise_amp, n_samples)
    tb.run()
    original = np.array(tb.sink_orig.data())
    fm_signal = np.array(tb.sink_fm.data())
    demod = np.array(tb.sink.data())
    return original, fm_signal, demod


# =====================================================================
# FUNCOES DE ANALISE
# =====================================================================
def complex_spectrum(data, fft_size=FFT_SIZE, samp_rate=SAMP_RATE):
    """Retorna (freqs_hz, magnitude_dB) para sinal complexo (centrado)."""
    w = np.hanning(fft_size)
    seg = data[-fft_size:]
    X = np.fft.fftshift(np.fft.fft(seg * w))
    mag = 20 * np.log10(np.abs(X) / fft_size + 1e-12)
    freqs = np.fft.fftshift(np.fft.fftfreq(fft_size, 1.0 / samp_rate))
    return freqs, mag


def measure_bandwidth_dB(freqs, mag, threshold_dB=-20):
    """Mede largura de banda a 'threshold_dB' abaixo do pico."""
    peak = np.max(mag)
    level = peak + threshold_dB
    above = freqs[mag >= level]
    if len(above) < 2:
        return 0.0
    return above[-1] - above[0]


def save_csv(filename, header, rows):
    """Salva dados em CSV."""
    path = os.path.join(DATA_DIR, filename)
    with open(path, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)
    return path


# =====================================================================
# ESTILO DOS PLOTS
# =====================================================================
plt.rcParams.update({
    'figure.facecolor': 'white',
    'axes.grid': True,
    'grid.alpha': 0.3,
    'font.size': 10,
})


# =====================================================================
# ETAPA 1: Modulador FM e espectro basico
# =====================================================================
def etapa1():
    log("\n" + "=" * 65)
    log("ETAPA 1: Modulador FM e espectro basico")
    log("=" * 65)

    fm_data = capture_fm(fm=FM_FREQ, max_dev=MAX_DEV)

    # --- Espectro FM ---
    freqs, mag = complex_spectrum(fm_data)

    fig, (ax_t, ax_f) = plt.subplots(1, 2, figsize=(15, 4.5))

    # Dominio do tempo (parte real do sinal FM)
    n_pts = int(2.0 * SAMP_RATE / 1000)  # 2 ms
    t = np.arange(n_pts) / SAMP_RATE * 1000
    ax_t.plot(t, np.real(fm_data[:n_pts]), linewidth=0.6, color='#1f77b4')
    ax_t.set_xlabel('Tempo (ms)')
    ax_t.set_ylabel('Amplitude')
    ax_t.set_title('Sinal FM - Dominio do Tempo (parte real)')

    # Espectro
    ax_f.plot(freqs / 1000, mag, linewidth=0.6, color='#1f77b4')
    ax_f.set_xlabel(u'Frequencia (kHz)')
    ax_f.set_ylabel('Magnitude (dB)')
    ax_f.set_title(f'Espectro FM (fm={FM_FREQ} Hz, $\\Delta f$={MAX_DEV} Hz)')
    ax_f.set_xlim([-30, 30])
    ax_f.axvline(0, color='gray', ls=':', alpha=0.5)

    # Marcar largura de Carson
    beta = MAX_DEV / FM_FREQ
    B_carson = 2 * (MAX_DEV + FM_FREQ)
    ax_f.axvline(-B_carson / 2000, color='r', ls='--', alpha=0.6,
                 label=f'Carson: B={B_carson/1000:.0f} kHz')
    ax_f.axvline(B_carson / 2000, color='r', ls='--', alpha=0.6)
    ax_f.legend(fontsize=9)

    fig.suptitle("Etapa 1: Modulacao FM em banda base",
                 fontsize=13, fontweight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, "etapa1_fm_basico.png"),
                dpi=150, bbox_inches='tight')
    plt.close()

    bw_20 = measure_bandwidth_dB(freqs, mag, -20)
    log(f"  fm = {FM_FREQ} Hz, Delta_f = {MAX_DEV} Hz")
    log(f"  beta = {beta:.2f}")
    log(f"  Largura de Carson: B = 2*(Delta_f + fm) = {B_carson} Hz")
    log(f"  Largura medida (-20 dB): {bw_20:.0f} Hz")
    log(f"  -> etapa1_fm_basico.png")

    log(f"\n  Resposta Q1: Quanto maior Delta_f, mais rapida a variacao")
    log(f"  de fase instantanea, resultando em mais cruzamentos por zero")
    log(f"  no dominio do tempo e um espectro mais largo.")


# =====================================================================
# ETAPA 2: Verificacao da Regra de Carson
# =====================================================================
def etapa2():
    log("\n" + "=" * 65)
    log("ETAPA 2: Verificacao da Regra de Carson")
    log("=" * 65)

    test_cases = [
        (1000, 2000),
        (1000, 5000),
        (2000, 2000),
        (2000, 10000),
        (4000, 4000),
        (4000, 20000),
    ]

    fig, axes = plt.subplots(2, 3, figsize=(18, 9))
    csv_rows = []

    log(f"\n  {'fm(Hz)':>7} | {'Df(Hz)':>7} | {'beta':>6} | "
        f"{'B_Carson(Hz)':>12} | {'B_med(Hz)':>10} | {'Erro(%)':>8}")
    log(f"  {'-'*7}-+-{'-'*7}-+-{'-'*6}-+-"
        f"{'-'*12}-+-{'-'*10}-+-{'-'*8}")

    for ax, (fm, delta_f) in zip(axes.flat, test_cases):
        fm_data = capture_fm(fm=fm, max_dev=delta_f)
        freqs, mag = complex_spectrum(fm_data)

        beta = delta_f / fm
        B_carson = 2 * (delta_f + fm)
        bw_measured = measure_bandwidth_dB(freqs, mag, -20)
        erro = abs(bw_measured - B_carson) / B_carson * 100

        ax.plot(freqs / 1000, mag, linewidth=0.6)
        ax.axvline(-B_carson / 2000, color='r', ls='--', alpha=0.6)
        ax.axvline(B_carson / 2000, color='r', ls='--', alpha=0.6)
        ax.set_title(f'fm={fm}, $\\Delta f$={delta_f}, '
                     f'$\\beta$={beta:.1f}')
        ax.set_xlabel(u'Frequencia (kHz)')
        ax.set_ylabel('dB')
        xlim = max(B_carson * 1.5, 10000)
        ax.set_xlim([-xlim / 1000, xlim / 1000])

        log(f"  {fm:>7} | {delta_f:>7} | {beta:>6.1f} | "
            f"{B_carson:>12} | {bw_measured:>10.0f} | {erro:>8.1f}")
        csv_rows.append([fm, delta_f, f"{beta:.2f}", B_carson,
                         f"{bw_measured:.0f}", f"{erro:.1f}"])

    plt.suptitle("Etapa 2: Regra de Carson - Verificacao",
                 fontsize=13, fontweight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, "etapa2_carson.png"),
                dpi=150, bbox_inches='tight')
    plt.close()

    save_csv("etapa2_carson.csv",
             ["fm_Hz", "delta_f_Hz", "beta", "B_Carson_Hz",
              "B_medido_Hz", "erro_percent"],
             csv_rows)

    log(f"\n  -> etapa2_carson.png")
    log(f"  -> dados/etapa2_carson.csv")
    log(f"\n  Resposta Q2: A Regra de Carson e confirmada com erro tipico")
    log(f"  de 10-20%. O erro vem do truncamento dos lobulos laterais de")
    log(f"  Bessel: a regra considera ~98% da potencia, mas as bandas")
    log(f"  laterais de ordem superior sao desprezadas.")


# =====================================================================
# ETAPA 3: Demodulacao FM
# =====================================================================
def etapa3():
    log("\n" + "=" * 65)
    log("ETAPA 3: Demodulacao FM")
    log("=" * 65)

    original, fm_signal, demod = capture_fm_transceiver(
        fm=FM_FREQ, max_dev=MAX_DEV, noise_amp=0.0)

    # Normalizar demodulado para mesma escala do original
    if np.max(np.abs(demod)) > 0:
        demod_norm = demod * (np.max(np.abs(original)) /
                              np.max(np.abs(demod)))
    else:
        demod_norm = demod

    fig, axes = plt.subplots(3, 1, figsize=(14, 10))

    # Mensagem original
    n_pts = int(5.0 * SAMP_RATE / 1000)  # 5 ms
    t = np.arange(n_pts) / SAMP_RATE * 1000

    axes[0].plot(t, original[:n_pts], linewidth=0.8, color='#1f77b4')
    axes[0].set_title('Mensagem Original')
    axes[0].set_ylabel('Amplitude')

    # Sinal FM (parte real)
    axes[1].plot(t, np.real(fm_signal[:n_pts]), linewidth=0.5,
                 color='#2ca02c')
    axes[1].set_title('Sinal FM (parte real)')
    axes[1].set_ylabel('Amplitude')

    # Sobreposicao: original vs demodulado
    axes[2].plot(t, original[:n_pts], linewidth=1.0, color='#1f77b4',
                 label='Original', alpha=0.7)
    axes[2].plot(t, demod_norm[:n_pts], linewidth=1.0, color='#d62728',
                 label='Demodulado', alpha=0.7, ls='--')
    axes[2].set_title('Comparacao: Original vs Demodulado')
    axes[2].set_xlabel('Tempo (ms)')
    axes[2].set_ylabel('Amplitude')
    axes[2].legend()

    fig.suptitle(f"Etapa 3: Demodulacao FM (fm={FM_FREQ} Hz, "
                 f"$\\Delta f$={MAX_DEV} Hz)",
                 fontsize=13, fontweight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, "etapa3_demodulacao.png"),
                dpi=150, bbox_inches='tight')
    plt.close()

    # Calcular erro RMS
    min_len = min(len(original), len(demod_norm))
    # Descartar transitorio inicial
    start = int(0.01 * SAMP_RATE)
    if start < min_len:
        err = original[start:min_len] - demod_norm[start:min_len]
        rms_err = np.sqrt(np.mean(err**2))
        rms_orig = np.sqrt(np.mean(original[start:min_len]**2))
        snr_db = 20 * np.log10(rms_orig / (rms_err + 1e-12))
    else:
        snr_db = 0

    log(f"  Demodulacao sem ruido:")
    log(f"  SNR da reconstrucao: {snr_db:.1f} dB")
    log(f"  -> etapa3_demodulacao.png")

    log(f"\n  Resposta Q3: O espectro NBFM (beta < 1) e similar ao AM,")
    log(f"  com poucas bandas laterais (tipicamente 1 par). O espectro")
    log(f"  WBFM (beta >> 1) possui muitas bandas laterais (funcoes de")
    log(f"  Bessel), ocupando largura de banda muito maior.")


# =====================================================================
# ETAPA 4: NBFM vs WBFM com ruido
# =====================================================================
def etapa4():
    log("\n" + "=" * 65)
    log("ETAPA 4: NBFM vs WBFM com ruido")
    log("=" * 65)

    fm = 2000  # Frequencia da mensagem fixa

    configs = [
        ("NBFM", 2000, 1.0),    # (nome, delta_f, beta)
        ("WBFM", 20000, 10.0),
    ]

    noise_levels = [0.0, 0.05, 0.1, 0.2, 0.5, 1.0, 2.0, 5.0]

    csv_rows = []

    log(f"\n  {'Config':>8} | {'beta':>5} | {'noise':>7} | "
        f"{'SNR(dB)':>9} | {'Qualidade':>12}")
    log(f"  {'-'*8}-+-{'-'*5}-+-{'-'*7}-+-{'-'*9}-+-{'-'*12}")

    fig, axes = plt.subplots(2, len(noise_levels), figsize=(24, 8))
    if len(noise_levels) == 1:
        axes = axes.reshape(2, 1)

    for row_idx, (name, delta_f, beta) in enumerate(configs):
        for col_idx, noise_amp in enumerate(noise_levels):
            original, fm_signal, demod = capture_fm_transceiver(
                fm=fm, max_dev=delta_f, noise_amp=noise_amp)

            # Normalizar
            if np.max(np.abs(demod)) > 0:
                demod_norm = demod * (np.max(np.abs(original)) /
                                      np.max(np.abs(demod)))
            else:
                demod_norm = demod

            # Calcular SNR
            min_len = min(len(original), len(demod_norm))
            start = int(0.01 * SAMP_RATE)
            if start < min_len:
                err = original[start:min_len] - demod_norm[start:min_len]
                rms_err = np.sqrt(np.mean(err**2))
                rms_orig = np.sqrt(np.mean(original[start:min_len]**2))
                snr_db = 20 * np.log10(rms_orig / (rms_err + 1e-12))
            else:
                snr_db = 0

            qual = ("Excelente" if snr_db > 30 else
                    "Boa" if snr_db > 20 else
                    "Razoavel" if snr_db > 10 else
                    "Ruim" if snr_db > 3 else "Inaudivel")

            log(f"  {name:>8} | {beta:>5.1f} | {noise_amp:>7.2f} | "
                f"{snr_db:>9.1f} | {qual:>12}")
            csv_rows.append([name, f"{beta:.1f}", noise_amp,
                             f"{snr_db:.1f}", qual])

            # Plot no tempo
            ax = axes[row_idx, col_idx]
            n_pts = int(3.0 * SAMP_RATE / 1000)
            t = np.arange(n_pts) / SAMP_RATE * 1000
            ax.plot(t, original[:n_pts], linewidth=0.6,
                    color='#1f77b4', alpha=0.5, label='Original')
            ax.plot(t, demod_norm[:n_pts], linewidth=0.6,
                    color='#d62728', alpha=0.7, label='Demod')
            ax.set_title(f'{name}, noise={noise_amp}',
                         fontsize=8)
            ax.set_ylim([-2, 2])
            if col_idx == 0:
                ax.set_ylabel(f'{name}\n($\\beta$={beta:.0f})')
            if row_idx == 1:
                ax.set_xlabel('Tempo (ms)')
            if row_idx == 0 and col_idx == 0:
                ax.legend(fontsize=7)

    plt.suptitle("Etapa 4: NBFM vs WBFM com ruido",
                 fontsize=13, fontweight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, "etapa4_nbfm_vs_wbfm.png"),
                dpi=150, bbox_inches='tight')
    plt.close()

    save_csv("etapa4_nbfm_vs_wbfm.csv",
             ["config", "beta", "noise_amp", "SNR_dB", "qualidade"],
             csv_rows)

    # Grafico de SNR vs noise
    fig, ax = plt.subplots(figsize=(10, 6))
    for name, delta_f, beta in configs:
        snrs = []
        for noise_amp in noise_levels:
            original, _, demod = capture_fm_transceiver(
                fm=fm, max_dev=delta_f, noise_amp=noise_amp)
            if np.max(np.abs(demod)) > 0:
                demod_norm = demod * (np.max(np.abs(original)) /
                                      np.max(np.abs(demod)))
            else:
                demod_norm = demod
            min_len = min(len(original), len(demod_norm))
            start = int(0.01 * SAMP_RATE)
            if start < min_len:
                err = original[start:min_len] - demod_norm[start:min_len]
                rms_err = np.sqrt(np.mean(err**2))
                rms_orig = np.sqrt(np.mean(original[start:min_len]**2))
                snr = 20 * np.log10(rms_orig / (rms_err + 1e-12))
            else:
                snr = 0
            snrs.append(snr)
        ax.plot(noise_levels, snrs, 'o-', linewidth=2,
                label=f'{name} ($\\beta$={beta:.0f})')

    ax.set_xlabel('Amplitude do Ruido')
    ax.set_ylabel('SNR (dB)')
    ax.set_title('SNR de Saida vs Nivel de Ruido: NBFM vs WBFM')
    ax.legend(fontsize=11)
    ax.set_ylim(bottom=0)
    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, "etapa4_snr_comparacao.png"),
                dpi=150, bbox_inches='tight')
    plt.close()

    # Espectros NBFM vs WBFM
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 5))
    for ax, (name, delta_f, beta) in zip([ax1, ax2], configs):
        fm_data = capture_fm(fm=fm, max_dev=delta_f)
        freqs, mag = complex_spectrum(fm_data)
        B_carson = 2 * (delta_f + fm)

        ax.plot(freqs / 1000, mag, linewidth=0.6)
        ax.axvline(-B_carson / 2000, color='r', ls='--', alpha=0.6,
                   label=f'Carson: {B_carson/1000:.0f} kHz')
        ax.axvline(B_carson / 2000, color='r', ls='--', alpha=0.6)
        ax.set_title(f'{name}: fm={fm} Hz, $\\Delta f$={delta_f} Hz, '
                     f'$\\beta$={beta:.0f}')
        ax.set_xlabel(u'Frequencia (kHz)')
        ax.set_ylabel('dB')
        xlim = max(B_carson * 1.8, 10000)
        ax.set_xlim([-xlim / 1000, xlim / 1000])
        ax.legend(fontsize=9)

    fig.suptitle("Etapa 4: Espectros NBFM vs WBFM",
                 fontsize=13, fontweight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, "etapa4_espectros_nbfm_wbfm.png"),
                dpi=150, bbox_inches='tight')
    plt.close()

    log(f"\n  -> etapa4_nbfm_vs_wbfm.png")
    log(f"  -> etapa4_snr_comparacao.png")
    log(f"  -> etapa4_espectros_nbfm_wbfm.png")
    log(f"  -> dados/etapa4_nbfm_vs_wbfm.csv")

    log(f"\n  Resposta Q4: FM troca largura de banda por SNR.")
    log(f"  A SNR de saida e proporcional a beta^2*(beta+1)*SNR_in.")
    log(f"  O custo e a largura de banda: B = 2*(Delta_f + fm).")

    log(f"\n  Resposta Q5: WBFM tolera mais ruido que NBFM.")
    log(f"  Quanto maior beta, melhor a imunidade ao ruido,")
    log(f"  porem maior a largura de banda ocupada. Esse e o")
    log(f"  tradeoff fundamental da modulacao FM.")


# =====================================================================
# TABELA DE PARAMETROS
# =====================================================================
def tabela_parametros():
    log("\n" + "=" * 65)
    log("TABELA DE PARAMETROS DE REFERENCIA")
    log("=" * 65)

    header = (f"  {'Parametro':<22} | {'Valor':>15}")
    log(header)
    log(f"  {'-'*22}-+-{'-'*15}")

    params = [
        ("samp_rate (Hz)",      f"{SAMP_RATE}"),
        ("audio_rate (Hz)",     f"{AUDIO_RATE}"),
        ("Interpolacao",        f"{INTERP}"),
        ("fm (Hz)",             f"{FM_FREQ}"),
        ("Delta_f (Hz)",        f"{MAX_DEV}"),
        ("Amplitude mensagem",  f"{MSG_AMP}"),
        ("beta",                f"{MAX_DEV/FM_FREQ:.2f}"),
        ("B_Carson (Hz)",       f"{2*(MAX_DEV+FM_FREQ)}"),
        ("N amostras audio",    f"{N_SAMPLES_AUDIO}"),
        ("N amostras FM",       f"{N_SAMPLES_FM}"),
        ("FFT Size",            f"{FFT_SIZE}"),
    ]

    for name, val in params:
        log(f"  {name:<22} | {val:>15}")


# =====================================================================
# MAIN
# =====================================================================
if __name__ == '__main__':
    log("=" * 65)
    log("PRATICA 05 -- MODULACAO FM E REGRA DE CARSON")
    log("GABARITO DO PROFESSOR")
    log(f"Data: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    log(f"GNU Radio: {gr.version()}")
    log(f"Sample Rate: {SAMP_RATE} Hz | Audio Rate: {AUDIO_RATE} Hz")
    log(f"Saida: {BASE_DIR}")
    log("=" * 65)

    tabela_parametros()
    etapa1()
    etapa2()
    etapa3()
    etapa4()

    log("\n" + "=" * 65)
    log("GABARITO COMPLETO GERADO COM SUCESSO")
    log("=" * 65)

    # Salvar relatorio em texto
    report_path = os.path.join(BASE_DIR, "relatorio.txt")
    with open(report_path, 'w') as f:
        f.write('\n'.join(relatorio))
    print(f"\nRelatorio salvo em: {report_path}")
