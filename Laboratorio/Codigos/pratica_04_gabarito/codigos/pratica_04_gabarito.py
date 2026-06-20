#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pratica 04 -- Modulacao SSB (Single Sideband): Gabarito do Professor
=====================================================================
Executa o flowgraph da Pratica 04 em modo headless (sem GUI),
reproduzindo todas as etapas do enunciado e gerando:

  1. Figuras PNG de referencia (tempo + espectro) para cada cenario
  2. Dados numericos de cada medicao (picos, larguras de banda)
  3. Tabela comparativa DSB-SC vs SSB-USB vs SSB-LSB
  4. Relatorio resumo em texto

Execucao:
    /usr/bin/python3 pratica_04_gabarito.py

Saida:
    ./pratica_04_gabarito/
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
    from gnuradio import gr, analog, blocks, filter
    from gnuradio.filter import firdes
except ImportError:
    print("ERRO: GNU Radio nao encontrado.")
    print("Execute com: /usr/bin/python3 pratica_04_gabarito.py")
    sys.exit(1)

try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
except ImportError:
    print("ERRO: matplotlib nao encontrado.")
    sys.exit(1)

from scipy.signal import find_peaks, hilbert

# =====================================================================
# CONFIGURACAO
# =====================================================================
SAMP_RATE = 48000
FC = 5000           # Frequencia da portadora (Hz)
FM = 500            # Frequencia da mensagem (Hz)
AMP_C = 1.0         # Amplitude da portadora
AMP_M = 1.0         # Amplitude da mensagem
N_SAMPLES = 48000   # 1 segundo de dados
FFT_SIZE = 4096

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
class FlowgraphDSBSC(gr.top_block):
    """Gera sinal DSB-SC: m(t) * c(t)."""

    def __init__(self, fc=FC, fm=FM, amp_c=AMP_C, amp_m=AMP_M,
                 n_samples=N_SAMPLES):
        gr.top_block.__init__(self, "DSB-SC")

        # Fontes
        self.msg = analog.sig_source_f(
            SAMP_RATE, analog.GR_COS_WAVE, fm, amp_m, 0)
        self.carrier = analog.sig_source_f(
            SAMP_RATE, analog.GR_COS_WAVE, fc, amp_c, 0)

        # Multiplicador: m(t) * c(t)
        self.mult = blocks.multiply_ff()
        self.connect(self.msg, (self.mult, 0))
        self.connect(self.carrier, (self.mult, 1))

        # Head + sink
        self.head = blocks.head(gr.sizeof_float, n_samples)
        self.sink = blocks.vector_sink_f()
        self.connect(self.mult, self.head, self.sink)


class FlowgraphSSBFilter(gr.top_block):
    """Aplica filtro passa-faixa em um sinal pre-gravado."""

    def __init__(self, data, low_cutoff, high_cutoff, transition=200):
        gr.top_block.__init__(self, "SSB-Filter")

        # Fonte de vetor
        self.src = blocks.vector_source_f(data.tolist(), False)

        # Filtro BPF
        taps = firdes.band_pass(
            1.0, SAMP_RATE, low_cutoff, high_cutoff, transition)
        self.bpf = filter.fir_filter_fff(1, taps)

        # Sink
        self.sink = blocks.vector_sink_f()
        self.connect(self.src, self.bpf, self.sink)


class FlowgraphDemod(gr.top_block):
    """Demodulacao coerente: sinal * carrier -> LPF."""

    def __init__(self, data, fc=FC, cutoff=1500, transition=200):
        gr.top_block.__init__(self, "Demod")

        n_samples = len(data)

        # Fonte do sinal SSB
        self.src = blocks.vector_source_f(data.tolist(), False)

        # Portadora local
        self.carrier = analog.sig_source_f(
            SAMP_RATE, analog.GR_COS_WAVE, fc, 2.0, 0)

        # Multiplicador
        self.mult = blocks.multiply_ff()
        self.connect(self.src, (self.mult, 0))
        self.connect(self.carrier, (self.mult, 1))

        # Head para limitar amostras da portadora
        self.head_carrier = blocks.head(gr.sizeof_float, n_samples)

        # LPF para recuperar mensagem
        lpf_taps = firdes.low_pass(1.0, SAMP_RATE, cutoff, transition)
        self.lpf = filter.fir_filter_fff(1, lpf_taps)

        # Sink
        self.sink = blocks.vector_sink_f()

        # Reconectar com head na portadora
        self.disconnect(self.carrier, (self.mult, 1))
        self.connect(self.carrier, self.head_carrier, (self.mult, 1))
        self.connect(self.mult, self.lpf, self.sink)


def capture_dsb_sc(fc=FC, fm=FM, amp_c=AMP_C, amp_m=AMP_M,
                   n_samples=N_SAMPLES):
    """Captura sinal DSB-SC."""
    tb = FlowgraphDSBSC(fc, fm, amp_c, amp_m, n_samples)
    tb.run()
    return np.array(tb.sink.data())


def apply_bpf(data, low_cutoff, high_cutoff, transition=200):
    """Aplica filtro passa-faixa via GNU Radio."""
    tb = FlowgraphSSBFilter(data, low_cutoff, high_cutoff, transition)
    tb.run()
    return np.array(tb.sink.data())


def demodulate(data, fc=FC, cutoff=1500, transition=200):
    """Demodulacao coerente via GNU Radio."""
    tb = FlowgraphDemod(data, fc, cutoff, transition)
    tb.run()
    return np.array(tb.sink.data())


def capture_message(fm=FM, amp_m=AMP_M, n_samples=N_SAMPLES):
    """Captura sinal de mensagem puro para referencia."""
    tb = gr.top_block()
    src = analog.sig_source_f(
        SAMP_RATE, analog.GR_COS_WAVE, fm, amp_m, 0)
    head = blocks.head(gr.sizeof_float, n_samples)
    sink = blocks.vector_sink_f()
    tb.connect(src, head, sink)
    tb.run()
    return np.array(sink.data())


# =====================================================================
# FUNCOES DE ANALISE
# =====================================================================
def spectrum(data, fft_size=FFT_SIZE):
    """Retorna (freqs_hz, magnitude_dB)."""
    w = np.hanning(fft_size)
    seg = data[:fft_size] if len(data) >= fft_size else np.pad(
        data, (0, fft_size - len(data)))
    X = np.fft.rfft(seg * w)
    mag = 20 * np.log10(np.abs(X) / fft_size + 1e-12)
    freqs = np.fft.rfftfreq(fft_size, 1.0 / SAMP_RATE)
    return freqs, mag


def find_spectral_peaks(freqs, mag, height=-40, distance=20):
    """Encontra picos espectrais, retorna [(freq, mag_dB), ...]."""
    idx, _ = find_peaks(mag, height=height, distance=distance)
    order = np.argsort(mag[idx])[::-1]
    return [(freqs[idx[i]], mag[idx[i]]) for i in order]


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


def plot_time_freq(data, title, filename, t_ms=5, freq_range=None,
                   markers=None, fft_size=FFT_SIZE):
    """Plota tempo e espectro lado a lado."""
    fig, (ax_t, ax_f) = plt.subplots(1, 2, figsize=(15, 4.5))

    # --- Tempo ---
    n_pts = min(int(t_ms * SAMP_RATE / 1000), len(data))
    t = np.arange(n_pts) / SAMP_RATE * 1000
    ax_t.plot(t, data[:n_pts], linewidth=0.8, color='#1f77b4')
    ax_t.set_xlabel('Tempo (ms)')
    ax_t.set_ylabel('Amplitude')
    ax_t.set_title('Dominio do Tempo')

    # --- Espectro ---
    freqs, mag = spectrum(data, fft_size)
    ax_f.plot(freqs, mag, linewidth=0.8, color='#1f77b4')
    ax_f.set_xlabel('Frequencia (Hz)')
    ax_f.set_ylabel('Magnitude (dB)')
    ax_f.set_title(f'Espectro (N={fft_size})')

    if freq_range:
        ax_f.set_xlim(freq_range)
    else:
        ax_f.set_xlim([0, SAMP_RATE / 2])

    if markers:
        colors = ['#d62728', '#2ca02c', '#ff7f0e', '#9467bd']
        for i, (mf, label) in enumerate(markers):
            c = colors[i % len(colors)]
            ax_f.axvline(mf, color=c, ls='--', alpha=0.6, label=label)
        ax_f.legend(fontsize=8)

    fig.suptitle(title, fontsize=13, fontweight='bold')
    plt.tight_layout()
    path = os.path.join(FIG_DIR, filename)
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    return path


def plot_comparison(signals, titles, suptitle, filename, t_ms=4,
                    freq_range=None, fft_size=FFT_SIZE):
    """Plota multiplos sinais em subplots para comparacao."""
    n = len(signals)
    fig, axes = plt.subplots(n, 2, figsize=(15, 3.5 * n))
    if n == 1:
        axes = axes.reshape(1, 2)

    for i, (data, ttl) in enumerate(zip(signals, titles)):
        # Tempo
        n_pts = min(int(t_ms * SAMP_RATE / 1000), len(data))
        t = np.arange(n_pts) / SAMP_RATE * 1000
        axes[i, 0].plot(t, data[:n_pts], linewidth=0.8)
        axes[i, 0].set_ylabel('Amplitude')
        axes[i, 0].set_title(f'{ttl} - Tempo')
        if i == n - 1:
            axes[i, 0].set_xlabel('Tempo (ms)')

        # Espectro
        freqs, mag = spectrum(data, fft_size)
        axes[i, 1].plot(freqs, mag, linewidth=0.8)
        axes[i, 1].set_ylabel('dB')
        axes[i, 1].set_title(f'{ttl} - Espectro')
        if freq_range:
            axes[i, 1].set_xlim(freq_range)
        else:
            axes[i, 1].set_xlim([0, SAMP_RATE / 2])
        if i == n - 1:
            axes[i, 1].set_xlabel('Frequencia (Hz)')

    fig.suptitle(suptitle, fontsize=13, fontweight='bold')
    plt.tight_layout()
    path = os.path.join(FIG_DIR, filename)
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    return path


# =====================================================================
# ETAPA 1: Geracao DSB-SC e identificacao das bandas laterais
# =====================================================================
def etapa1():
    log("\n" + "=" * 65)
    log("ETAPA 1: Geracao DSB-SC e identificacao das bandas laterais")
    log("=" * 65)

    dsb = capture_dsb_sc()

    freq_usb = FC + FM
    freq_lsb = FC - FM

    plot_time_freq(dsb,
                   f"Etapa 1: DSB-SC  |  fc={FC} Hz, fm={FM} Hz",
                   "etapa1_dsb_sc.png",
                   t_ms=5,
                   freq_range=[0, 12000],
                   markers=[(freq_usb, f'USB = {freq_usb} Hz'),
                            (freq_lsb, f'LSB = {freq_lsb} Hz'),
                            (FC, f'fc = {FC} Hz')])

    freqs, mag = spectrum(dsb)
    peaks = find_spectral_peaks(freqs, mag, height=-50, distance=30)

    log(f"  Portadora: fc = {FC} Hz")
    log(f"  Mensagem:  fm = {FM} Hz")
    log(f"  USB esperada: fc + fm = {freq_usb} Hz")
    log(f"  LSB esperada: fc - fm = {freq_lsb} Hz")
    log(f"\n  Picos encontrados:")
    for pf, pm in peaks[:5]:
        log(f"    {pf:.0f} Hz @ {pm:.1f} dB")

    # Verificar presenca das bandas
    mag_usb = mag[np.argmin(np.abs(freqs - freq_usb))]
    mag_lsb = mag[np.argmin(np.abs(freqs - freq_lsb))]
    log(f"\n  USB ({freq_usb} Hz): {mag_usb:.1f} dB")
    log(f"  LSB ({freq_lsb} Hz): {mag_lsb:.1f} dB")

    log(f"\n  Resposta Q1: A USB aparece em fc+fm = {freq_usb} Hz e a "
        f"LSB em fc-fm = {freq_lsb} Hz.")
    log(f"  Sao identificadas pela posicao relativa a portadora: "
        f"acima (USB) ou abaixo (LSB).")
    log(f"  -> etapa1_dsb_sc.png")

    save_csv("etapa1_picos_dsb.csv",
             ["freq_Hz", "mag_dB"],
             [[f"{pf:.1f}", f"{pm:.1f}"] for pf, pm in peaks[:5]])

    return dsb


# =====================================================================
# ETAPA 2: Filtragem USB (SSB-USB)
# =====================================================================
def etapa2(dsb):
    log("\n" + "=" * 65)
    log("ETAPA 2: Filtragem USB (SSB-USB)")
    log("=" * 65)

    low_cut = FC
    high_cut = FC + 2 * FM
    log(f"  BPF: {low_cut} Hz - {high_cut} Hz (transicao = 200 Hz)")

    ssb_usb = apply_bpf(dsb, low_cut, high_cut, transition=200)

    freq_usb = FC + FM

    plot_time_freq(ssb_usb,
                   f"Etapa 2: SSB-USB  |  BPF [{low_cut}-{high_cut}] Hz",
                   "etapa2_ssb_usb.png",
                   t_ms=5,
                   freq_range=[0, 12000],
                   markers=[(freq_usb, f'USB = {freq_usb} Hz'),
                            (FC, f'fc = {FC} Hz')])

    freqs, mag = spectrum(ssb_usb)
    peaks = find_spectral_peaks(freqs, mag, height=-50, distance=30)

    log(f"\n  Picos encontrados apos filtragem USB:")
    for pf, pm in peaks[:5]:
        log(f"    {pf:.0f} Hz @ {pm:.1f} dB")

    # Verificar supressao da LSB
    freq_lsb = FC - FM
    mag_lsb = mag[np.argmin(np.abs(freqs - freq_lsb))]
    mag_usb = mag[np.argmin(np.abs(freqs - freq_usb))]
    supressao = mag_usb - mag_lsb

    log(f"\n  USB ({freq_usb} Hz): {mag_usb:.1f} dB")
    log(f"  LSB ({freq_lsb} Hz): {mag_lsb:.1f} dB (suprimida)")
    log(f"  Supressao da LSB: {supressao:.1f} dB")
    log(f"  -> etapa2_ssb_usb.png")

    save_csv("etapa2_ssb_usb.csv",
             ["freq_Hz", "mag_dB"],
             [[f"{pf:.1f}", f"{pm:.1f}"] for pf, pm in peaks[:5]])

    return ssb_usb


# =====================================================================
# ETAPA 3: Filtragem LSB (SSB-LSB)
# =====================================================================
def etapa3(dsb):
    log("\n" + "=" * 65)
    log("ETAPA 3: Filtragem LSB (SSB-LSB)")
    log("=" * 65)

    low_cut = FC - 2 * FM
    high_cut = FC
    log(f"  BPF: {low_cut} Hz - {high_cut} Hz (transicao = 200 Hz)")

    ssb_lsb = apply_bpf(dsb, low_cut, high_cut, transition=200)

    freq_lsb = FC - FM

    plot_time_freq(ssb_lsb,
                   f"Etapa 3: SSB-LSB  |  BPF [{low_cut}-{high_cut}] Hz",
                   "etapa3_ssb_lsb.png",
                   t_ms=5,
                   freq_range=[0, 12000],
                   markers=[(freq_lsb, f'LSB = {freq_lsb} Hz'),
                            (FC, f'fc = {FC} Hz')])

    freqs, mag = spectrum(ssb_lsb)
    peaks = find_spectral_peaks(freqs, mag, height=-50, distance=30)

    log(f"\n  Picos encontrados apos filtragem LSB:")
    for pf, pm in peaks[:5]:
        log(f"    {pf:.0f} Hz @ {pm:.1f} dB")

    # Verificar supressao da USB
    freq_usb = FC + FM
    mag_usb = mag[np.argmin(np.abs(freqs - freq_usb))]
    mag_lsb = mag[np.argmin(np.abs(freqs - freq_lsb))]
    supressao = mag_lsb - mag_usb

    log(f"\n  LSB ({freq_lsb} Hz): {mag_lsb:.1f} dB")
    log(f"  USB ({freq_usb} Hz): {mag_usb:.1f} dB (suprimida)")
    log(f"  Supressao da USB: {supressao:.1f} dB")
    log(f"  -> etapa3_ssb_lsb.png")

    save_csv("etapa3_ssb_lsb.csv",
             ["freq_Hz", "mag_dB"],
             [[f"{pf:.1f}", f"{pm:.1f}"] for pf, pm in peaks[:5]])

    return ssb_lsb


# =====================================================================
# ETAPA 4: Demodulacao SSB
# =====================================================================
def etapa4(ssb_usb, ssb_lsb):
    log("\n" + "=" * 65)
    log("ETAPA 4: Demodulacao SSB coerente")
    log("=" * 65)

    # Mensagem original para comparacao
    msg_ref = capture_message()

    # Demodular USB
    log(f"\n  Demodulando SSB-USB: s(t) * 2cos(2*pi*fc*t) -> LPF")
    demod_usb = demodulate(ssb_usb, fc=FC, cutoff=2 * FM, transition=200)

    # Demodular LSB
    log(f"  Demodulando SSB-LSB: s(t) * 2cos(2*pi*fc*t) -> LPF")
    demod_lsb = demodulate(ssb_lsb, fc=FC, cutoff=2 * FM, transition=200)

    # Ajustar comprimentos para comparacao
    min_len = min(len(msg_ref), len(demod_usb), len(demod_lsb))
    msg_ref = msg_ref[:min_len]
    demod_usb = demod_usb[:min_len]
    demod_lsb = demod_lsb[:min_len]

    # Normalizar para comparacao (ignorar transitorio do filtro)
    skip = 2000  # amostras de transitorio
    if min_len > skip + 1000:
        norm_usb = np.max(np.abs(demod_usb[skip:])) + 1e-12
        norm_lsb = np.max(np.abs(demod_lsb[skip:])) + 1e-12
        demod_usb_n = demod_usb / norm_usb
        demod_lsb_n = demod_lsb / norm_lsb
        msg_ref_n = msg_ref / (np.max(np.abs(msg_ref[skip:])) + 1e-12)
    else:
        demod_usb_n = demod_usb
        demod_lsb_n = demod_lsb
        msg_ref_n = msg_ref

    # Plot comparativo
    plot_comparison(
        [msg_ref_n, demod_usb_n, demod_lsb_n],
        ['Mensagem original', 'Demodulada USB', 'Demodulada LSB'],
        "Etapa 4: Demodulacao SSB coerente",
        "etapa4_demodulacao.png",
        t_ms=8,
        freq_range=[0, 3000])

    # Espectros das demoduladas
    freqs_u, mag_u = spectrum(demod_usb)
    freqs_l, mag_l = spectrum(demod_lsb)

    peaks_u = find_spectral_peaks(freqs_u, mag_u, height=-50, distance=30)
    peaks_l = find_spectral_peaks(freqs_l, mag_l, height=-50, distance=30)

    log(f"\n  Picos na demodulada USB:")
    for pf, pm in peaks_u[:3]:
        log(f"    {pf:.0f} Hz @ {pm:.1f} dB")

    log(f"\n  Picos na demodulada LSB:")
    for pf, pm in peaks_l[:3]:
        log(f"    {pf:.0f} Hz @ {pm:.1f} dB")

    # Correlacao com referencia
    if min_len > skip + 1000:
        corr_usb = np.corrcoef(
            msg_ref_n[skip:], demod_usb_n[skip:])[0, 1]
        corr_lsb = np.corrcoef(
            msg_ref_n[skip:], demod_lsb_n[skip:])[0, 1]
        log(f"\n  Correlacao USB vs original: {corr_usb:.4f}")
        log(f"  Correlacao LSB vs original: {corr_lsb:.4f}")

    log(f"  -> etapa4_demodulacao.png")

    save_csv("etapa4_demodulacao.csv",
             ["sinal", "pico_freq_Hz", "pico_mag_dB"],
             [["USB", f"{peaks_u[0][0]:.1f}" if peaks_u else "N/A",
               f"{peaks_u[0][1]:.1f}" if peaks_u else "N/A"],
              ["LSB", f"{peaks_l[0][0]:.1f}" if peaks_l else "N/A",
               f"{peaks_l[0][1]:.1f}" if peaks_l else "N/A"]])

    return demod_usb, demod_lsb


# =====================================================================
# ETAPA 5: Tabela comparativa
# =====================================================================
def etapa5(dsb, ssb_usb, ssb_lsb):
    log("\n" + "=" * 65)
    log("ETAPA 5: Tabela comparativa DSB-SC vs SSB-USB vs SSB-LSB")
    log("=" * 65)

    results = []
    for name, data in [("DSB-SC", dsb),
                       ("SSB-USB", ssb_usb),
                       ("SSB-LSB", ssb_lsb)]:
        freqs, mag = spectrum(data)
        peaks = find_spectral_peaks(freqs, mag, height=-50, distance=30)

        # Contar picos significativos
        n_peaks = len([p for p in peaks if p[1] > -40])

        # Frequencias dos picos
        peak_freqs = [f"{p[0]:.0f}" for p in peaks[:3]]

        # Largura de banda estimada (entre picos extremos)
        if len(peaks) >= 2:
            peak_f_vals = sorted([p[0] for p in peaks if p[1] > -40])
            bw = peak_f_vals[-1] - peak_f_vals[0] if len(peak_f_vals) >= 2 else FM
        else:
            bw = FM

        # Amplitudes dos picos
        peak_amps = [f"{p[1]:.1f}" for p in peaks[:3]]

        results.append({
            'name': name,
            'n_peaks': n_peaks,
            'peak_freqs': ", ".join(peak_freqs),
            'bw': bw,
            'peak_amps': ", ".join(peak_amps),
        })

    # Formatar tabela
    header = (f"  {'Parametro':<22} | {'DSB-SC':>14} | "
              f"{'SSB-USB':>14} | {'SSB-LSB':>14}")
    log(f"\n{header}")
    log(f"  {'-'*22}-+-{'-'*14}-+-{'-'*14}-+-{'-'*14}")

    r = results
    rows_table = [
        ("Num. picos",
         str(r[0]['n_peaks']), str(r[1]['n_peaks']), str(r[2]['n_peaks'])),
        ("Frequencias (Hz)",
         r[0]['peak_freqs'], r[1]['peak_freqs'], r[2]['peak_freqs']),
        ("Largura de banda (Hz)",
         f"{r[0]['bw']:.0f}", f"{r[1]['bw']:.0f}", f"{r[2]['bw']:.0f}"),
        ("Amplitudes (dB)",
         r[0]['peak_amps'], r[1]['peak_amps'], r[2]['peak_amps']),
        ("B = W (teoria)",
         f"2*fm = {2*FM}", f"fm = {FM}", f"fm = {FM}"),
    ]

    csv_rows = []
    for name, a, b, c in rows_table:
        log(f"  {name:<22} | {a:>14} | {b:>14} | {c:>14}")
        csv_rows.append([name, a, b, c])

    save_csv("etapa5_comparacao.csv",
             ["Parametro", "DSB-SC", "SSB-USB", "SSB-LSB"],
             csv_rows)

    log(f"\n  Resposta Q2: B_SSB = W = fm = {FM} Hz; "
        f"B_DSB = 2W = 2*fm = {2*FM} Hz.")
    log(f"  SSB reduz a largura de banda pela metade.")
    log(f"\n  Resposta Q3:")
    log(f"    Vantagens SSB: eficiencia de banda, economia de potencia.")
    log(f"    Desvantagens: receptor mais complexo, necessita deteccao "
        f"coerente.")
    log(f"\n  Resposta Q4: SSB e menos sensivel a erros de fase que "
        f"DSB-SC.")
    log(f"    Em DSB-SC, erro de 90 graus anula completamente o sinal.")
    log(f"    Em SSB, erro de fase causa apenas distorcao, "
        f"nao anulamento.")
    log(f"  -> dados/etapa5_comparacao.csv")

    # Plot comparativo dos 3 espectros
    plot_comparison(
        [dsb, ssb_usb, ssb_lsb],
        ['DSB-SC', 'SSB-USB', 'SSB-LSB'],
        "Etapa 5: Comparacao DSB-SC vs SSB-USB vs SSB-LSB",
        "etapa5_comparacao.png",
        t_ms=5,
        freq_range=[0, 12000])
    log(f"  -> etapa5_comparacao.png")


# =====================================================================
# ETAPA 6: Metodo de Hilbert (opcional)
# =====================================================================
def etapa6():
    log("\n" + "=" * 65)
    log("ETAPA 6: Geracao SSB via transformada de Hilbert (opcional)")
    log("=" * 65)

    # Gerar mensagem e portadora como arrays numpy
    t = np.arange(N_SAMPLES) / SAMP_RATE
    m_t = AMP_M * np.cos(2 * np.pi * FM * t)
    c_cos = AMP_C * np.cos(2 * np.pi * FC * t)
    c_sin = AMP_C * np.sin(2 * np.pi * FC * t)

    # Transformada de Hilbert da mensagem
    m_analytic = hilbert(m_t)
    m_hat = np.imag(m_analytic)  # parte imaginaria = Hilbert de m(t)

    # SSB-USB via Hilbert: s_USB(t) = m(t)cos(wc*t) - m_hat(t)sin(wc*t)
    ssb_usb_hilbert = m_t * c_cos - m_hat * c_sin

    # SSB-LSB via Hilbert: s_LSB(t) = m(t)cos(wc*t) + m_hat(t)sin(wc*t)
    ssb_lsb_hilbert = m_t * c_cos + m_hat * c_sin

    # SSB-USB via filtro para comparacao
    dsb = capture_dsb_sc()
    ssb_usb_filter = apply_bpf(dsb, FC, FC + 2 * FM, transition=200)

    # Ajustar comprimentos
    min_len = min(len(ssb_usb_hilbert), len(ssb_usb_filter))
    ssb_usb_hilbert = ssb_usb_hilbert[:min_len]
    ssb_usb_filter = ssb_usb_filter[:min_len]

    # Plot comparativo
    plot_comparison(
        [ssb_usb_hilbert, ssb_usb_filter],
        ['SSB-USB (Hilbert)', 'SSB-USB (Filtro BPF)'],
        "Etapa 6: Comparacao Hilbert vs Filtro",
        "etapa6_hilbert_vs_filtro.png",
        t_ms=5,
        freq_range=[0, 12000])

    # Analisar espectros
    freqs_h, mag_h = spectrum(ssb_usb_hilbert)
    freqs_f, mag_f = spectrum(ssb_usb_filter)

    peaks_h = find_spectral_peaks(freqs_h, mag_h, height=-50, distance=30)
    peaks_f = find_spectral_peaks(freqs_f, mag_f, height=-50, distance=30)

    log(f"\n  Metodo Hilbert:")
    log(f"    s_USB(t) = m(t)cos(2*pi*fc*t) - m_hat(t)sin(2*pi*fc*t)")
    log(f"    m_hat(t) = Hilbert[m(t)] via scipy.signal.hilbert")

    log(f"\n  Picos SSB-USB (Hilbert):")
    for pf, pm in peaks_h[:3]:
        log(f"    {pf:.0f} Hz @ {pm:.1f} dB")

    log(f"\n  Picos SSB-USB (Filtro):")
    for pf, pm in peaks_f[:3]:
        log(f"    {pf:.0f} Hz @ {pm:.1f} dB")

    # Supressao da banda indesejada
    freq_lsb = FC - FM
    sup_hilbert = mag_h[np.argmin(np.abs(freqs_h - (FC + FM)))] - \
                  mag_h[np.argmin(np.abs(freqs_h - freq_lsb))]
    sup_filter = mag_f[np.argmin(np.abs(freqs_f - (FC + FM)))] - \
                 mag_f[np.argmin(np.abs(freqs_f - freq_lsb))]

    log(f"\n  Supressao LSB (Hilbert): {sup_hilbert:.1f} dB")
    log(f"  Supressao LSB (Filtro):  {sup_filter:.1f} dB")

    log(f"\n  Resposta Q5:")
    log(f"    Metodo por filtro: mais simples de implementar, mas "
        f"limitado pela seletividade do filtro.")
    log(f"    Metodo por Hilbert: teoricamente exato (supressao total "
        f"da banda indesejada),")
    log(f"    mas computacionalmente mais pesado e requer "
        f"processamento em bloco.")
    log(f"  -> etapa6_hilbert_vs_filtro.png")

    # Plotar tambem o LSB via Hilbert
    plot_time_freq(ssb_lsb_hilbert,
                   "Etapa 6: SSB-LSB via Hilbert",
                   "etapa6_ssb_lsb_hilbert.png",
                   t_ms=5,
                   freq_range=[0, 12000],
                   markers=[(FC - FM, f'LSB = {FC - FM} Hz')])
    log(f"  -> etapa6_ssb_lsb_hilbert.png")

    save_csv("etapa6_hilbert.csv",
             ["metodo", "supressao_LSB_dB"],
             [["Hilbert", f"{sup_hilbert:.1f}"],
              ["Filtro", f"{sup_filter:.1f}"]])


# =====================================================================
# MAIN
# =====================================================================
if __name__ == '__main__':
    log("=" * 65)
    log("PRATICA 04 -- MODULACAO SSB (SINGLE SIDEBAND)")
    log("GABARITO DO PROFESSOR")
    log(f"Data: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    log(f"GNU Radio: {gr.version()}")
    log(f"Sample Rate: {SAMP_RATE} Hz | Amostras: {N_SAMPLES}")
    log(f"Portadora: fc = {FC} Hz | Mensagem: fm = {FM} Hz")
    log(f"Saida: {BASE_DIR}")
    log("=" * 65)

    # Etapa 1: Geracao DSB-SC
    dsb = etapa1()

    # Etapa 2: Filtragem USB
    ssb_usb = etapa2(dsb)

    # Etapa 3: Filtragem LSB
    ssb_lsb = etapa3(dsb)

    # Etapa 4: Demodulacao
    etapa4(ssb_usb, ssb_lsb)

    # Etapa 5: Tabela comparativa
    etapa5(dsb, ssb_usb, ssb_lsb)

    # Etapa 6: Hilbert (opcional)
    etapa6()

    log("\n" + "=" * 65)
    log("GABARITO COMPLETO GERADO COM SUCESSO")
    log("=" * 65)

    # Salvar relatorio em texto
    report_path = os.path.join(BASE_DIR, "relatorio.txt")
    with open(report_path, 'w') as f:
        f.write('\n'.join(relatorio))
    print(f"\nRelatorio salvo em: {report_path}")
