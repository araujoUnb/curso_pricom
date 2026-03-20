#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Pratica 07 -- Ruido em Demoduladores AM e FM: Gabarito do Professor
====================================================================
Executa flowgraphs da Pratica 07 em modo headless (sem GUI),
reproduzindo todas as etapas do enunciado e gerando:

  1. Figuras PNG de referencia (tempo + espectro) para cada cenario
  2. Dados numericos de cada medicao (SNR de saida)
  3. Tabela comparativa AM vs FM
  4. Relatorio resumo em texto

Execucao:
    /usr/bin/python3 pratica_07_gabarito.py

Saida:
    ./pratica_07_gabarito/
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
    from gnuradio import gr, analog, blocks, filter as gr_filter
    from gnuradio.filter import firdes
except ImportError:
    print("ERRO: GNU Radio nao encontrado.")
    print("Execute com: /usr/bin/python3 pratica_07_gabarito.py")
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
SAMP_RATE_AM = 48000    # taxa de amostragem para cadeia AM
SAMP_RATE_FM = 48000    # taxa de amostragem para cadeia FM (simplificada)
AUDIO_RATE = 48000
FM_MSG = 1000           # frequencia da mensagem (Hz)
FC = 10000              # frequencia da portadora AM (Hz)
MAX_DEV = 10000         # desvio maximo FM (Hz) => beta = max_dev / fm = 10
N_SAMPLES = 48000 * 2   # 2 segundos de sinal

NOISE_SIGMAS = [0, 0.05, 0.10, 0.20, 0.40, 0.70, 1.00]

BASE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "pratica_07_gabarito")
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
# FUNCOES DE ANALISE
# =====================================================================
def compute_snr(original, recovered, samp_rate, fm):
    """
    Calcula SNR de saida comparando sinal recuperado com o original.
    Pula o transiente inicial e normaliza antes de comparar.
    """
    skip = int(samp_rate * 0.05)  # pular 50 ms de transiente
    orig = original[skip:]
    rec = recovered[skip:]

    # Igualar comprimentos
    min_len = min(len(orig), len(rec))
    orig = orig[:min_len]
    rec = rec[:min_len]

    if len(orig) == 0 or np.std(rec) < 1e-12:
        return -np.inf

    # Normalizar recuperado para mesma escala do original
    rec = rec * (np.std(orig) / (np.std(rec) + 1e-12))

    # Alinhar por correlacao cruzada (compensar atraso do filtro)
    corr = np.correlate(orig, rec, mode='full')
    lag = np.argmax(np.abs(corr)) - (len(rec) - 1)
    if abs(lag) < len(orig) // 4:
        if lag > 0:
            orig = orig[lag:]
            rec = rec[:len(orig)]
        elif lag < 0:
            rec = rec[-lag:]
            orig = orig[:len(rec)]

    # Calcular SNR
    noise = orig - rec
    snr = 10 * np.log10(np.var(orig) / (np.var(noise) + 1e-12))
    return snr


def spectrum(data, samp_rate, fft_size=4096, window='hann'):
    """Retorna (freqs_hz, magnitude_dB)."""
    if window == 'hann':
        w = np.hanning(fft_size)
    else:
        w = np.ones(fft_size)
    seg = data[-fft_size:]
    X = np.fft.rfft(seg * w)
    mag = 20 * np.log10(np.abs(X) / fft_size + 1e-12)
    freqs = np.fft.rfftfreq(fft_size, 1.0 / samp_rate)
    return freqs, mag


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
# FLOWGRAPH: AM DSB-SC com AWGN
# =====================================================================
class AMFlowgraph(gr.top_block):
    """
    Cadeia AM DSB-SC completa:
      msg(t) * carrier(t) --> + noise --> * local_carrier --> LPF --> sink

    Demodulacao coerente: multiplica pelo oscilador local e filtra.
    """

    def __init__(self, noise_sigma=0.0, samp_rate=SAMP_RATE_AM,
                 fm=FM_MSG, fc=FC, n_samples=N_SAMPLES):
        gr.top_block.__init__(self, "AM_DSB_SC_AWGN")

        # --- Modulador ---
        # Mensagem: cos(2*pi*fm*t)
        self.src_msg = analog.sig_source_f(
            samp_rate, analog.GR_COS_WAVE, fm, 1.0, 0)

        # Portadora: cos(2*pi*fc*t)
        self.src_carrier = analog.sig_source_f(
            samp_rate, analog.GR_COS_WAVE, fc, 1.0, 0)

        # Modulacao: msg * carrier
        self.mod_mult = blocks.multiply_ff()

        # --- Canal com ruido ---
        if noise_sigma > 0:
            self.noise = analog.noise_source_f(
                analog.GR_GAUSSIAN, noise_sigma)
            self.add_noise = blocks.add_ff()

        # --- Demodulador coerente ---
        # Oscilador local: cos(2*pi*fc*t) (sincronizado)
        self.src_local = analog.sig_source_f(
            samp_rate, analog.GR_COS_WAVE, fc, 1.0, 0)

        # Multiplicar pelo oscilador local
        self.demod_mult = blocks.multiply_ff()

        # Filtro passa-baixas (corte em 1.5 * fm)
        lpf_taps = firdes.low_pass(1, samp_rate, int(1.5 * fm), 200)
        self.lpf = gr_filter.fir_filter_fff(1, lpf_taps)

        # Sink
        self.head = blocks.head(gr.sizeof_float, n_samples)
        self.sink = blocks.vector_sink_f()

        # Tambem capturar referencia (mensagem original)
        self.head_ref = blocks.head(gr.sizeof_float, n_samples)
        self.sink_ref = blocks.vector_sink_f()

        # --- Conexoes ---
        # Modulador
        self.connect(self.src_msg, (self.mod_mult, 0))
        self.connect(self.src_carrier, (self.mod_mult, 1))

        # Canal
        if noise_sigma > 0:
            self.connect(self.mod_mult, (self.add_noise, 0))
            self.connect(self.noise, (self.add_noise, 1))
            channel_out = self.add_noise
        else:
            channel_out = self.mod_mult

        # Demodulador
        self.connect(channel_out, (self.demod_mult, 0))
        self.connect(self.src_local, (self.demod_mult, 1))
        self.connect(self.demod_mult, self.lpf, self.head, self.sink)

        # Referencia
        self.connect(self.src_msg, self.head_ref, self.sink_ref)


def capture_am(noise_sigma, n_samples=N_SAMPLES):
    """
    Captura sinal AM DSB-SC demodulado e referencia.
    Retorna (demodulado, referencia).
    """
    tb = AMFlowgraph(noise_sigma=noise_sigma, n_samples=n_samples)
    tb.run()
    demod = np.array(tb.sink.data())
    ref = np.array(tb.sink_ref.data())
    return demod, ref


# =====================================================================
# FLOWGRAPH: FM com AWGN
# =====================================================================
class FMFlowgraph(gr.top_block):
    """
    Cadeia FM completa:
      msg(t) --> FM_mod --> + noise_complexo --> FM_demod --> sink

    FM modulador: frequency_modulator_fc
    FM demodulador: quadrature_demod_cf
    """

    def __init__(self, noise_sigma=0.0, max_dev=MAX_DEV,
                 samp_rate=SAMP_RATE_FM, fm=FM_MSG,
                 n_samples=N_SAMPLES):
        gr.top_block.__init__(self, "FM_AWGN")

        sensitivity = 2 * np.pi * max_dev / samp_rate

        # --- Modulador FM ---
        # Mensagem: cos(2*pi*fm*t)
        self.src_msg = analog.sig_source_f(
            samp_rate, analog.GR_COS_WAVE, fm, 1.0, 0)

        # Modulador FM (entrada float, saida complex)
        self.fm_mod = analog.frequency_modulator_fc(sensitivity)

        # --- Canal com ruido complexo ---
        if noise_sigma > 0:
            self.noise = analog.noise_source_c(
                analog.GR_GAUSSIAN, noise_sigma)
            self.add_noise = blocks.add_cc()

        # --- Demodulador FM ---
        demod_gain = samp_rate / (2 * np.pi * max_dev)
        self.fm_demod = analog.quadrature_demod_cf(demod_gain)

        # Sink
        self.head = blocks.head(gr.sizeof_float, n_samples)
        self.sink = blocks.vector_sink_f()

        # Referencia
        self.head_ref = blocks.head(gr.sizeof_float, n_samples)
        self.sink_ref = blocks.vector_sink_f()

        # --- Conexoes ---
        self.connect(self.src_msg, self.fm_mod)

        if noise_sigma > 0:
            self.connect(self.fm_mod, (self.add_noise, 0))
            self.connect(self.noise, (self.add_noise, 1))
            channel_out = self.add_noise
        else:
            channel_out = self.fm_mod

        self.connect(channel_out, self.fm_demod, self.head, self.sink)

        # Referencia
        self.connect(self.src_msg, self.head_ref, self.sink_ref)


def capture_fm(noise_sigma, max_dev=MAX_DEV, n_samples=N_SAMPLES):
    """
    Captura sinal FM demodulado e referencia.
    Retorna (demodulado, referencia).
    """
    tb = FMFlowgraph(noise_sigma=noise_sigma, max_dev=max_dev,
                     n_samples=n_samples)
    tb.run()
    demod = np.array(tb.sink.data())
    ref = np.array(tb.sink_ref.data())
    return demod, ref


# =====================================================================
# ETAPA 1: Cadeia AM DSB-SC com AWGN
# =====================================================================
def etapa1():
    log("\n" + "=" * 65)
    log("ETAPA 1: Cadeia AM DSB-SC com AWGN")
    log("=" * 65)
    log(f"  Parametros: fc={FC} Hz, fm={FM_MSG} Hz, samp_rate={SAMP_RATE_AM} Hz")
    log(f"  Demodulacao coerente: multiplicar por oscilador local + LPF")
    log(f"  Niveis de ruido (sigma): {NOISE_SIGMAS}")

    fig, axes = plt.subplots(len(NOISE_SIGMAS), 2, figsize=(16, 4 * len(NOISE_SIGMAS)))
    csv_rows = []

    log(f"\n  {'sigma':>7} | {'SNR_saida(dB)':>14} | {'Qualidade':>14}")
    log(f"  {'-'*7}-+-{'-'*14}-+-{'-'*14}")

    for i, sigma in enumerate(NOISE_SIGMAS):
        demod, ref = capture_am(sigma)

        # Calcular SNR de saida
        if sigma == 0:
            snr_out = np.inf
        else:
            snr_out = compute_snr(ref, demod, SAMP_RATE_AM, FM_MSG)

        # Classificar qualidade
        if snr_out == np.inf or snr_out > 30:
            qualidade = "Excelente"
        elif snr_out > 20:
            qualidade = "Bom"
        elif snr_out > 10:
            qualidade = "Razoavel"
        elif snr_out > 0:
            qualidade = "Ruim"
        else:
            qualidade = "Ininteligivel"

        snr_str = f"{snr_out:.1f}" if np.isfinite(snr_out) else "inf"
        log(f"  {sigma:>7.2f} | {snr_str:>14} | {qualidade:>14}")
        csv_rows.append([sigma, snr_str, qualidade])

        # --- Subplot: tempo ---
        n_pts = int(4 * SAMP_RATE_AM / FM_MSG)
        t_ms = np.arange(n_pts) / SAMP_RATE_AM * 1000

        ax_t = axes[i, 0]
        ax_t.plot(t_ms, ref[:n_pts], 'g-', linewidth=1.0, alpha=0.7,
                  label='Original')
        ax_t.plot(t_ms, demod[:n_pts], 'b-', linewidth=0.6, alpha=0.8,
                  label='Demodulado')
        ax_t.set_xlabel('Tempo (ms)')
        ax_t.set_ylabel('Amplitude')
        ax_t.set_title(f'AM DSB-SC: sigma={sigma} | SNR={snr_str} dB')
        ax_t.legend(fontsize=7)

        # --- Subplot: espectro do sinal demodulado ---
        ax_f = axes[i, 1]
        freqs, mag = spectrum(demod, SAMP_RATE_AM)
        ax_f.plot(freqs, mag, linewidth=0.6, color='#1f77b4')
        ax_f.axvline(FM_MSG, color='r', ls='--', alpha=0.5,
                     label=f'{FM_MSG} Hz')
        ax_f.set_xlabel('Frequencia (Hz)')
        ax_f.set_ylabel('Magnitude (dB)')
        ax_f.set_title(f'Espectro demodulado (sigma={sigma})')
        ax_f.set_xlim([0, 5 * FM_MSG])
        ax_f.legend(fontsize=7)

    plt.suptitle("Etapa 1: AM DSB-SC com AWGN - Efeito do Ruido",
                 fontsize=13, fontweight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, "etapa1_am_dsbsc_ruido.png"),
                dpi=150, bbox_inches='tight')
    plt.close()

    save_csv("etapa1_am_snr.csv",
             ["noise_sigma", "SNR_saida_dB", "qualidade"],
             csv_rows)

    log(f"\n  Resposta Q1: SNR de saida medido comparando o sinal")
    log(f"    demodulado com a mensagem original. SNR = 10*log10(Ps/Pn)")
    log(f"    onde Ps = variancia do sinal e Pn = variancia do erro.")
    log(f"  Resposta Q2: AM degrada de forma aproximadamente linear")
    log(f"    (graceful degradation): o ruido de saida cresce")
    log(f"    proporcionalmente ao ruido de entrada.")

    log(f"\n  -> etapa1_am_dsbsc_ruido.png")
    log(f"  -> dados/etapa1_am_snr.csv")


# =====================================================================
# ETAPA 2: Cadeia FM com AWGN
# =====================================================================
def etapa2():
    log("\n" + "=" * 65)
    log("ETAPA 2: Cadeia FM com AWGN")
    log("=" * 65)
    log(f"  Parametros: fm={FM_MSG} Hz, max_dev={MAX_DEV} Hz, "
        f"beta={MAX_DEV/FM_MSG:.0f}")
    log(f"  samp_rate={SAMP_RATE_FM} Hz")
    log(f"  Niveis de ruido (sigma): {NOISE_SIGMAS}")

    fig, axes = plt.subplots(len(NOISE_SIGMAS), 2, figsize=(16, 4 * len(NOISE_SIGMAS)))
    csv_rows = []

    log(f"\n  {'sigma':>7} | {'SNR_saida(dB)':>14} | {'Qualidade':>14}")
    log(f"  {'-'*7}-+-{'-'*14}-+-{'-'*14}")

    for i, sigma in enumerate(NOISE_SIGMAS):
        demod, ref = capture_fm(sigma)

        # Calcular SNR de saida
        if sigma == 0:
            snr_out = np.inf
        else:
            snr_out = compute_snr(ref, demod, SAMP_RATE_FM, FM_MSG)

        # Classificar qualidade
        if snr_out == np.inf or snr_out > 30:
            qualidade = "Excelente"
        elif snr_out > 20:
            qualidade = "Bom"
        elif snr_out > 10:
            qualidade = "Razoavel"
        elif snr_out > 0:
            qualidade = "Ruim"
        else:
            qualidade = "Ininteligivel"

        snr_str = f"{snr_out:.1f}" if np.isfinite(snr_out) else "inf"
        log(f"  {sigma:>7.2f} | {snr_str:>14} | {qualidade:>14}")
        csv_rows.append([sigma, snr_str, qualidade])

        # --- Subplot: tempo ---
        n_pts = int(4 * SAMP_RATE_FM / FM_MSG)
        t_ms = np.arange(n_pts) / SAMP_RATE_FM * 1000

        ax_t = axes[i, 0]
        ax_t.plot(t_ms, ref[:n_pts], 'g-', linewidth=1.0, alpha=0.7,
                  label='Original')
        ax_t.plot(t_ms, demod[:n_pts], 'b-', linewidth=0.6, alpha=0.8,
                  label='Demodulado')
        ax_t.set_xlabel('Tempo (ms)')
        ax_t.set_ylabel('Amplitude')
        ax_t.set_title(f'FM: sigma={sigma} | SNR={snr_str} dB')
        ax_t.legend(fontsize=7)

        # --- Subplot: espectro do sinal demodulado ---
        ax_f = axes[i, 1]
        freqs, mag = spectrum(demod, SAMP_RATE_FM)
        ax_f.plot(freqs, mag, linewidth=0.6, color='#1f77b4')
        ax_f.axvline(FM_MSG, color='r', ls='--', alpha=0.5,
                     label=f'{FM_MSG} Hz')
        ax_f.set_xlabel('Frequencia (Hz)')
        ax_f.set_ylabel('Magnitude (dB)')
        ax_f.set_title(f'Espectro demodulado (sigma={sigma})')
        ax_f.set_xlim([0, 5 * FM_MSG])
        ax_f.legend(fontsize=7)

    plt.suptitle("Etapa 2: FM com AWGN - Efeito do Ruido",
                 fontsize=13, fontweight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, "etapa2_fm_ruido.png"),
                dpi=150, bbox_inches='tight')
    plt.close()

    save_csv("etapa2_fm_snr.csv",
             ["noise_sigma", "SNR_saida_dB", "qualidade"],
             csv_rows)

    log(f"\n  Resposta Q3: FM degrada lentamente acima do limiar,")
    log(f"    mas abaixo do limiar a degradacao e catastrofica")
    log(f"    (aparecem 'clicks' de ruido impulsivo).")

    log(f"\n  -> etapa2_fm_ruido.png")
    log(f"  -> dados/etapa2_fm_snr.csv")


# =====================================================================
# ETAPA 3: Comparacao AM vs FM
# =====================================================================
def etapa3():
    log("\n" + "=" * 65)
    log("ETAPA 3: Comparacao AM vs FM")
    log("=" * 65)

    csv_rows = []
    snr_am_list = []
    snr_fm_list = []

    log(f"\n  {'sigma':>7} | {'SNR_AM(dB)':>11} | {'SNR_FM(dB)':>11} | "
        f"{'Vantagem FM(dB)':>16} | {'Melhor':>8}")
    log(f"  {'-'*7}-+-{'-'*11}-+-{'-'*11}-+-{'-'*16}-+-{'-'*8}")

    for sigma in NOISE_SIGMAS:
        demod_am, ref_am = capture_am(sigma)
        demod_fm, ref_fm = capture_fm(sigma)

        if sigma == 0:
            snr_am = np.inf
            snr_fm = np.inf
        else:
            snr_am = compute_snr(ref_am, demod_am, SAMP_RATE_AM, FM_MSG)
            snr_fm = compute_snr(ref_fm, demod_fm, SAMP_RATE_FM, FM_MSG)

        snr_am_list.append(snr_am)
        snr_fm_list.append(snr_fm)

        snr_am_str = f"{snr_am:.1f}" if np.isfinite(snr_am) else "inf"
        snr_fm_str = f"{snr_fm:.1f}" if np.isfinite(snr_fm) else "inf"

        if np.isfinite(snr_am) and np.isfinite(snr_fm):
            vantagem = snr_fm - snr_am
            vant_str = f"{vantagem:.1f}"
            melhor = "FM" if vantagem > 0 else "AM"
        else:
            vant_str = "---"
            melhor = "---"

        log(f"  {sigma:>7.2f} | {snr_am_str:>11} | {snr_fm_str:>11} | "
            f"{vant_str:>16} | {melhor:>8}")
        csv_rows.append([sigma, snr_am_str, snr_fm_str, vant_str, melhor])

    save_csv("etapa3_comparacao_am_fm.csv",
             ["noise_sigma", "SNR_AM_dB", "SNR_FM_dB",
              "vantagem_FM_dB", "melhor"],
             csv_rows)

    # --- Grafico comparativo ---
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 5.5))

    sigmas_plot = [s for s in NOISE_SIGMAS if s > 0]
    snr_am_plot = [snr_am_list[i] for i, s in enumerate(NOISE_SIGMAS) if s > 0]
    snr_fm_plot = [snr_fm_list[i] for i, s in enumerate(NOISE_SIGMAS) if s > 0]

    ax1.plot(sigmas_plot, snr_am_plot, 'bo-', linewidth=2,
             markersize=8, label='AM DSB-SC')
    ax1.plot(sigmas_plot, snr_fm_plot, 'rs-', linewidth=2,
             markersize=8, label=f'FM (beta={MAX_DEV/FM_MSG:.0f})')
    ax1.set_xlabel('Sigma do ruido')
    ax1.set_ylabel('SNR de saida (dB)')
    ax1.set_title('SNR de Saida: AM vs FM')
    ax1.legend(fontsize=10)

    # Identificar limiar FM
    for i, (s, snr) in enumerate(zip(sigmas_plot, snr_fm_plot)):
        if i > 0 and np.isfinite(snr) and np.isfinite(snr_fm_plot[i-1]):
            queda = snr_fm_plot[i-1] - snr
            if queda > 15:  # queda abrupta => limiar
                ax1.axvline(s, color='red', ls=':', alpha=0.7,
                            label=f'Limiar FM (~sigma={s})')
                ax1.legend(fontsize=10)
                break

    # Comparacao visual para sigma medio
    sigma_demo = 0.20
    demod_am_demo, ref_am_demo = capture_am(sigma_demo)
    demod_fm_demo, ref_fm_demo = capture_fm(sigma_demo)

    n_pts = int(4 * AUDIO_RATE / FM_MSG)
    t_ms = np.arange(n_pts) / AUDIO_RATE * 1000

    ax2.plot(t_ms, ref_am_demo[:n_pts], 'g-', linewidth=1.5,
             alpha=0.5, label='Original')
    ax2.plot(t_ms, demod_am_demo[:n_pts], 'b-', linewidth=0.8,
             alpha=0.7, label='AM demod')
    ax2.plot(t_ms, demod_fm_demo[:n_pts], 'r-', linewidth=0.8,
             alpha=0.7, label='FM demod')
    ax2.set_xlabel('Tempo (ms)')
    ax2.set_ylabel('Amplitude')
    ax2.set_title(f'Comparacao temporal (sigma={sigma_demo})')
    ax2.legend(fontsize=9)

    plt.suptitle("Etapa 3: Comparacao AM vs FM sob Ruido",
                 fontsize=13, fontweight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, "etapa3_comparacao_am_fm.png"),
                dpi=150, bbox_inches='tight')
    plt.close()

    log(f"\n  Resposta Q4: FM apresenta vantagem sobre AM acima do")
    log(f"    limiar (threshold). O custo e largura de banda:")
    log(f"    B_FM = 2*(beta+1)*fm >> B_AM = 2*fm.")
    log(f"    Para beta={MAX_DEV/FM_MSG:.0f}: B_FM = "
        f"{2*(MAX_DEV/FM_MSG+1)*FM_MSG/1000:.0f} kHz vs "
        f"B_AM = {2*FM_MSG/1000:.0f} kHz.")
    log(f"  Resposta Q5: Para comparacao justa, deve-se usar mesma")
    log(f"    potencia transmitida, mesma mensagem e mesmo N0.")

    log(f"\n  -> etapa3_comparacao_am_fm.png")
    log(f"  -> dados/etapa3_comparacao_am_fm.csv")


# =====================================================================
# ETAPA 4: FM com diferentes valores de beta
# =====================================================================
def etapa4():
    log("\n" + "=" * 65)
    log("ETAPA 4: FM com diferentes valores de beta")
    log("=" * 65)

    betas = [
        (2, 2000),     # beta=2, max_dev=2000
        (10, 10000),   # beta=10, max_dev=10000
        (25, 25000),   # beta=25, max_dev=25000 (precisa samp_rate > 2*B)
    ]

    csv_rows = []

    log(f"\n  Comparacao de desempenho FM para diferentes beta:")
    log(f"  (fm={FM_MSG} Hz, samp_rate={SAMP_RATE_FM} Hz)")
    header_line = f"  {'sigma':>7}"
    for beta, md in betas:
        header_line += f" | SNR b={beta:<2} (dB)"
    log(header_line)
    log(f"  {'-'*7}" + "".join([f"-+-{'-'*16}" for _ in betas]))

    snr_data = {beta: [] for beta, _ in betas}

    for sigma in NOISE_SIGMAS:
        row = [sigma]
        line = f"  {sigma:>7.2f}"
        for beta, max_dev in betas:
            # Ajustar samp_rate se necessario (Nyquist para FM)
            # B_FM = 2*(beta+1)*fm
            bw_fm = 2 * (beta + 1) * FM_MSG
            sr = max(SAMP_RATE_FM, int(2.5 * bw_fm))
            # Arredondar para multiplo de audio_rate
            sr = max(sr, AUDIO_RATE)

            if sigma == 0:
                snr_out = np.inf
            else:
                try:
                    demod, ref = capture_fm(sigma, max_dev=max_dev,
                                            n_samples=int(sr * 2))
                    snr_out = compute_snr(ref, demod, sr, FM_MSG)
                except Exception:
                    snr_out = -np.inf

            snr_data[beta].append(snr_out)
            snr_str = f"{snr_out:.1f}" if np.isfinite(snr_out) else (
                "inf" if snr_out > 0 else "-inf")
            line += f" | {snr_str:>16}"
            row.append(snr_str)

        log(line)
        csv_rows.append(row)

    save_csv("etapa4_fm_betas.csv",
             ["noise_sigma"] + [f"SNR_beta_{b}_dB" for b, _ in betas],
             csv_rows)

    # --- Grafico comparativo ---
    fig, ax = plt.subplots(1, 1, figsize=(10, 6))

    sigmas_plot = [s for s in NOISE_SIGMAS if s > 0]
    colors = ['#1f77b4', '#d62728', '#2ca02c']
    markers = ['o', 's', '^']

    for idx, (beta, max_dev) in enumerate(betas):
        snr_plot = [snr_data[beta][i] for i, s in enumerate(NOISE_SIGMAS)
                    if s > 0]
        # Filtrar infinitos para plot
        snr_finite = [s if np.isfinite(s) else np.nan for s in snr_plot]
        bw_fm = 2 * (beta + 1) * FM_MSG
        ax.plot(sigmas_plot, snr_finite, color=colors[idx],
                marker=markers[idx], linewidth=2, markersize=8,
                label=f'beta={beta} (B={bw_fm/1000:.0f} kHz)')

    ax.set_xlabel('Sigma do ruido')
    ax.set_ylabel('SNR de saida (dB)')
    ax.set_title('FM: Efeito do Indice de Modulacao (beta)')
    ax.legend(fontsize=10)

    plt.suptitle("Etapa 4: FM com Diferentes beta",
                 fontsize=13, fontweight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, "etapa4_fm_betas.png"),
                dpi=150, bbox_inches='tight')
    plt.close()

    # --- Sinais no tempo para comparacao visual ---
    fig, axes = plt.subplots(len(betas), 1, figsize=(14, 4 * len(betas)))
    sigma_demo = 0.40

    for idx, (beta, max_dev) in enumerate(betas):
        bw_fm = 2 * (beta + 1) * FM_MSG
        sr = max(SAMP_RATE_FM, int(2.5 * bw_fm))
        sr = max(sr, AUDIO_RATE)

        try:
            demod, ref = capture_fm(sigma_demo, max_dev=max_dev,
                                    n_samples=int(sr * 2))
            snr = compute_snr(ref, demod, sr, FM_MSG)
        except Exception:
            demod = np.zeros(int(sr * 2))
            ref = np.zeros(int(sr * 2))
            snr = -np.inf

        n_pts = int(4 * sr / FM_MSG)
        t_ms = np.arange(n_pts) / sr * 1000

        ax = axes[idx]
        ax.plot(t_ms, ref[:n_pts], 'g-', linewidth=1.5, alpha=0.5,
                label='Original')
        ax.plot(t_ms, demod[:n_pts], 'b-', linewidth=0.8, alpha=0.8,
                label='Demodulado')
        snr_str = f"{snr:.1f}" if np.isfinite(snr) else "-inf"
        ax.set_title(f'beta={beta} (max_dev={max_dev} Hz, '
                     f'B={bw_fm/1000:.0f} kHz) | '
                     f'sigma={sigma_demo} | SNR={snr_str} dB')
        ax.set_xlabel('Tempo (ms)')
        ax.set_ylabel('Amplitude')
        ax.legend(fontsize=8)

    plt.suptitle(f"Etapa 4: FM - Comparacao de beta (sigma={sigma_demo})",
                 fontsize=13, fontweight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, "etapa4_fm_betas_tempo.png"),
                dpi=150, bbox_inches='tight')
    plt.close()

    log(f"\n  Analise: maior beta => maior ganho de SNR acima do limiar,")
    log(f"    porem o limiar tambem se desloca (exige SNR de entrada")
    log(f"    maior para operar). Tradeoff: ganho FM vs largura de banda.")
    log(f"    B_FM = 2*(beta+1)*fm (regra de Carson).")

    log(f"\n  -> etapa4_fm_betas.png")
    log(f"  -> etapa4_fm_betas_tempo.png")
    log(f"  -> dados/etapa4_fm_betas.csv")


# =====================================================================
# MAIN
# =====================================================================
if __name__ == '__main__':
    log("=" * 65)
    log("PRATICA 07 -- RUIDO EM DEMODULADORES AM E FM")
    log("GABARITO DO PROFESSOR")
    log(f"Data: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    log(f"GNU Radio: {gr.version()}")
    log(f"AM: samp_rate={SAMP_RATE_AM} Hz | fc={FC} Hz | fm={FM_MSG} Hz")
    log(f"FM: samp_rate={SAMP_RATE_FM} Hz | max_dev={MAX_DEV} Hz | "
        f"beta={MAX_DEV/FM_MSG:.0f}")
    log(f"Niveis de ruido: {NOISE_SIGMAS}")
    log(f"Amostras: {N_SAMPLES} ({N_SAMPLES/AUDIO_RATE:.1f} s)")
    log(f"Saida: {BASE_DIR}")
    log("=" * 65)

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
