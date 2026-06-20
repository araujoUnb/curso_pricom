#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pratica 08 -- Amostragem e Aliasing (Nyquist-Shannon): Gabarito do Professor
=============================================================================
Executa flowgraphs em modo headless (sem GUI), reproduzindo todas as etapas
do enunciado e gerando:

  1. Figuras PNG de referencia (tempo + espectro) para cada cenario
  2. Dados numericos (frequencias esperadas vs observadas, alias)
  3. Relatorio resumo em texto

Execucao:
    /usr/bin/python3 pratica_08_gabarito.py

Saida:
    ./pratica_08_gabarito/
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
    print("Execute com: /usr/bin/python3 pratica_08_gabarito.py")
    sys.exit(1)

try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
except ImportError:
    print("ERRO: matplotlib nao encontrado.")
    sys.exit(1)

from scipy.signal import find_peaks

# =====================================================================
# CONFIGURACAO
# =====================================================================
SAMP_RATE = 48000
N_SAMPLES = 48000  # 1 segundo de dados

# Parametros da Parte II (quantizacao PCM)
VMAX = 1.0                 # fundo de escala: faixa [-VMAX, +VMAX], Vpp = 2*VMAX
F_QUANT = 997              # senoide incomensuravel com SAMP_RATE (descorrelaciona o erro)
N_SAMPLES_Q = 1000000      # amostras para estatistica do ruido de quantizacao

# Parametros da Parte III (reconstrucao ZOH e equalizacao)
N_ZOH = 8                  # fator de upsampling do ZOH (Repeat block)
FS_LOW = SAMP_RATE // N_ZOH  # taxa antes do ZOH; SAMP_RATE = fs_high apos o ZOH
EQ_NTAPS = 201             # coeficientes do FIR equalizador inverse-sinc

from zoh_eq import design_eq  # noqa: E402  (mesmo projeto do Embedded Python Block)


class Quantizer(gr.sync_block):
    """Quantizador uniforme PCM mid-rise de n_bits na faixa [-vmax, +vmax].

    L = 2**n_bits niveis; passo Delta = 2*vmax/L;
    y[n] = Delta*(floor(x/Delta) + 0.5)  (nivel mais proximo).
    Identico ao Embedded Python Block usado em pratica_08_quantizacao_pcm.grc.
    """

    def __init__(self, n_bits=3, vmax=1.0):
        gr.sync_block.__init__(self, name="Quantizer",
                               in_sig=[np.float32], out_sig=[np.float32])
        self.n_bits = int(n_bits)
        self.vmax = float(vmax)
        self.delta = 2.0 * self.vmax / (2 ** self.n_bits)

    def work(self, input_items, output_items):
        x = np.clip(input_items[0], -self.vmax, self.vmax - 1e-9)
        output_items[0][:] = self.delta * (np.floor(x / self.delta) + 0.5)
        return len(output_items[0])

BASE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "pratica_08_gabarito")
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
class DecimationFlowgraph(gr.top_block):
    """Flowgraph: fonte cossenoidal -> [LPF] -> Keep 1 in N -> sink.
    Tambem captura o sinal original (sem decimacao) para comparacao."""

    def __init__(self, f_sinal, decim, use_filter=False,
                 n_samples=N_SAMPLES, amplitudes=None):
        gr.top_block.__init__(self, "Pratica08_Decimation")

        # --- Fonte(s) de sinal ---
        if amplitudes is None:
            # Tom unico
            self.src = analog.sig_source_f(
                SAMP_RATE, analog.GR_COS_WAVE, f_sinal, 1.0, 0)
            signal_out = self.src
        else:
            # Multiplos tons: f_sinal eh lista, amplitudes eh lista
            self._sources = []
            for f, a in zip(f_sinal, amplitudes):
                src = analog.sig_source_f(
                    SAMP_RATE, analog.GR_COS_WAVE, f, a, 0)
                self._sources.append(src)
            self.add_sig = blocks.add_ff()
            for i, src in enumerate(self._sources):
                self.connect(src, (self.add_sig, i))
            signal_out = self.add_sig

        # --- Captura do sinal original (sem decimacao) ---
        n_orig = n_samples
        self.head_orig = blocks.head(gr.sizeof_float, n_orig)
        self.sink_orig = blocks.vector_sink_f()
        self.connect(signal_out, self.head_orig, self.sink_orig)

        # --- Caminho com decimacao ---
        n_decim = n_samples // decim

        if use_filter:
            cutoff = (SAMP_RATE / decim) / 2.0 * 0.9
            transition = min(200, cutoff * 0.2)
            taps = firdes.low_pass(1, SAMP_RATE, cutoff, transition)
            self.lpf = filter.fir_filter_fff(1, taps)
            self.decim_block = blocks.keep_one_in_n(gr.sizeof_float, decim)
            self.head_dec = blocks.head(gr.sizeof_float, n_decim)
            self.sink_dec = blocks.vector_sink_f()
            self.connect(signal_out, self.lpf, self.decim_block,
                         self.head_dec, self.sink_dec)
        else:
            self.decim_block = blocks.keep_one_in_n(gr.sizeof_float, decim)
            self.head_dec = blocks.head(gr.sizeof_float, n_decim)
            self.sink_dec = blocks.vector_sink_f()
            self.connect(signal_out, self.decim_block,
                         self.head_dec, self.sink_dec)


def capture_decimated(f_sinal, decim, use_filter=False,
                      n_samples=N_SAMPLES, amplitudes=None):
    """Captura sinal original e decimado. Retorna (orig, decimated, fs_eff)."""
    tb = DecimationFlowgraph(f_sinal, decim, use_filter,
                             n_samples, amplitudes)
    tb.run()
    orig = np.array(tb.sink_orig.data())
    dec = np.array(tb.sink_dec.data())
    fs_eff = SAMP_RATE / decim
    return orig, dec, fs_eff


# =====================================================================
# FUNCOES DE ANALISE
# =====================================================================
def compute_spectrum(data, fs, fft_size=None, window='hann'):
    """Retorna (freqs_hz, magnitude_dB) usando a taxa fs."""
    if fft_size is None:
        fft_size = min(len(data), 4096)
    seg = data[-fft_size:]
    if window == 'hann':
        w = np.hanning(fft_size)
    else:
        w = np.ones(fft_size)
    X = np.fft.rfft(seg * w)
    mag = 20 * np.log10(np.abs(X) / fft_size + 1e-12)
    freqs = np.fft.rfftfreq(fft_size, 1.0 / fs)
    return freqs, mag


def find_peak_freq(data, fs, fft_size=None):
    """Encontra a frequencia do pico espectral dominante."""
    freqs, mag = compute_spectrum(data, fs, fft_size)
    # Ignorar DC (bin 0)
    mag[0] = -200
    peak_idx = np.argmax(mag)
    return freqs[peak_idx], mag[peak_idx]


def calc_alias_freq(f_sinal, fs_eff):
    """Calcula a frequencia aparente apos amostragem a fs_eff.
    Usa a formula de folding: f_alias = |f_sinal mod fs_eff|,
    rebatido para [0, fs_eff/2]."""
    f_mod = f_sinal % fs_eff
    if f_mod > fs_eff / 2:
        f_mod = fs_eff - f_mod
    return f_mod


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


def plot_time_and_spectrum(orig, dec, fs_eff, f_sinal, decim, title,
                           filename, t_ms=5, markers=None):
    """Plota 4 subplots: tempo original, espectro original,
    tempo decimado, espectro decimado."""
    fig, axes = plt.subplots(2, 2, figsize=(15, 9))
    ax_to, ax_fo, ax_td, ax_fd = axes.flat

    # --- Sinal original: tempo ---
    n_pts = int(t_ms * SAMP_RATE / 1000)
    t_orig = np.arange(min(n_pts, len(orig))) / SAMP_RATE * 1000
    ax_to.plot(t_orig, orig[:len(t_orig)], linewidth=0.8, color='#1f77b4')
    ax_to.set_xlabel('Tempo (ms)')
    ax_to.set_ylabel('Amplitude')
    ax_to.set_title(f'Original (fs = {SAMP_RATE} Hz)')

    # --- Sinal original: espectro ---
    freqs_o, mag_o = compute_spectrum(orig, SAMP_RATE)
    ax_fo.plot(freqs_o, mag_o, linewidth=0.8, color='#1f77b4')
    ax_fo.set_xlabel(u'Frequencia (Hz)')
    ax_fo.set_ylabel('Magnitude (dB)')
    ax_fo.set_title(f'Espectro Original (fs = {SAMP_RATE} Hz)')
    ax_fo.set_xlim([0, SAMP_RATE / 2])

    # --- Sinal decimado: tempo ---
    n_pts_d = int(t_ms * fs_eff / 1000)
    t_dec = np.arange(min(n_pts_d, len(dec))) / fs_eff * 1000
    ax_td.plot(t_dec, dec[:len(t_dec)], linewidth=0.8, color='#d62728',
               marker='o', markersize=3)
    ax_td.set_xlabel('Tempo (ms)')
    ax_td.set_ylabel('Amplitude')
    ax_td.set_title(f'Decimado (fs_eff = {fs_eff:.0f} Hz, decim = {decim})')

    # --- Sinal decimado: espectro ---
    freqs_d, mag_d = compute_spectrum(dec, fs_eff)
    ax_fd.plot(freqs_d, mag_d, linewidth=0.8, color='#d62728')
    ax_fd.set_xlabel(u'Frequencia (Hz)')
    ax_fd.set_ylabel('Magnitude (dB)')
    ax_fd.set_title(f'Espectro Decimado (fs_eff = {fs_eff:.0f} Hz)')
    ax_fd.set_xlim([0, fs_eff / 2])

    if markers:
        colors = ['#2ca02c', '#ff7f0e', '#9467bd', '#8c564b']
        for i, (mf, label) in enumerate(markers):
            c = colors[i % len(colors)]
            if mf <= SAMP_RATE / 2:
                ax_fo.axvline(mf, color=c, ls='--', alpha=0.6, label=label)
            alias_f = calc_alias_freq(mf, fs_eff)
            if alias_f <= fs_eff / 2:
                ax_fd.axvline(alias_f, color=c, ls='--', alpha=0.6,
                              label=f'{label} (alias={alias_f:.0f} Hz)')
        ax_fo.legend(fontsize=8)
        ax_fd.legend(fontsize=8)

    fig.suptitle(title, fontsize=13, fontweight='bold')
    plt.tight_layout()
    path = os.path.join(FIG_DIR, filename)
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    return path


# =====================================================================
# ETAPA 1: Flowgraph base com decimacao
# =====================================================================
def etapa1():
    log("\n" + "=" * 65)
    log("ETAPA 1: Flowgraph base com decimacao")
    log("=" * 65)

    f_sinal = 1000
    decim = 4
    fs_eff = SAMP_RATE / decim

    log(f"  f_sinal = {f_sinal} Hz, decim = {decim}")
    log(f"  fs_eff = {fs_eff:.0f} Hz, Nyquist = {fs_eff/2:.0f} Hz")
    log(f"  {f_sinal} Hz < {fs_eff/2:.0f} Hz (Nyquist) -> SEM aliasing")

    orig, dec, fs_eff = capture_decimated(f_sinal, decim)

    # Verificar pico no sinal decimado
    peak_f, peak_db = find_peak_freq(dec, fs_eff)
    log(f"  Pico no sinal decimado: {peak_f:.0f} Hz @ {peak_db:.1f} dB")
    log(f"  Resultado: {'OK' if abs(peak_f - f_sinal) < 50 else 'FALHA'}")

    plot_time_and_spectrum(
        orig, dec, fs_eff, f_sinal, decim,
        f"Etapa 1: Decimacao basica (f={f_sinal} Hz, decim={decim},"
        f" fs_eff={fs_eff:.0f} Hz)",
        "etapa1_decimacao_base.png",
        markers=[(f_sinal, f'{f_sinal} Hz')])

    log(f"  -> etapa1_decimacao_base.png")


# =====================================================================
# ETAPA 2: Tabela de verificacao de Nyquist
# =====================================================================
def etapa2():
    log("\n" + "=" * 65)
    log("ETAPA 2: Verificacao de Nyquist - 6 cenarios")
    log("=" * 65)

    scenarios = [
        ('A', 1000, 4),
        ('B', 5000, 4),
        ('C', 7000, 4),
        ('D', 1000, 10),
        ('E', 2500, 10),
        ('F', 3500, 10),
    ]

    header_fmt = (f"  {'Cen':>3} | {'f_sinal':>7} | {'decim':>5} | "
                  f"{'fs_eff':>6} | {'Nyquist':>7} | {'Nyquist?':>8} | "
                  f"{'f_esperada':>10} | {'f_observada':>11} | {'Erro':>6}")
    log(header_fmt)
    log(f"  {'-'*3}-+-{'-'*7}-+-{'-'*5}-+-{'-'*6}-+-{'-'*7}-+-"
        f"{'-'*8}-+-{'-'*10}-+-{'-'*11}-+-{'-'*6}")

    csv_rows = []

    fig, axes = plt.subplots(3, 2, figsize=(16, 14))

    for idx, (name, f_sinal, decim) in enumerate(scenarios):
        fs_eff = SAMP_RATE / decim
        nyquist = fs_eff / 2
        nyquist_ok = f_sinal < nyquist

        # Frequencia esperada apos amostragem
        f_esperada = calc_alias_freq(f_sinal, fs_eff)

        orig, dec, fs_eff = capture_decimated(f_sinal, decim)
        f_observada, peak_db = find_peak_freq(dec, fs_eff)
        erro = abs(f_observada - f_esperada)

        status = "Sim" if nyquist_ok else "Nao (alias)"
        log(f"  {name:>3} | {f_sinal:>7} | {decim:>5} | "
            f"{fs_eff:>6.0f} | {nyquist:>7.0f} | {status:>8} | "
            f"{f_esperada:>10.0f} | {f_observada:>11.0f} | {erro:>6.0f}")

        csv_rows.append([name, f_sinal, decim, f"{fs_eff:.0f}",
                         f"{nyquist:.0f}", status,
                         f"{f_esperada:.0f}", f"{f_observada:.0f}",
                         f"{erro:.0f}"])

        # Plot do espectro decimado
        ax = axes.flat[idx]
        freqs_d, mag_d = compute_spectrum(dec, fs_eff)
        ax.plot(freqs_d, mag_d, linewidth=0.8)
        ax.axvline(f_esperada, color='r', ls='--', alpha=0.6,
                   label=f'f_esperada = {f_esperada:.0f} Hz')
        ax.set_xlim([0, fs_eff / 2])
        ax.set_xlabel(u'Frequencia (Hz)')
        ax.set_ylabel('Magnitude (dB)')
        alias_label = "" if nyquist_ok else " [ALIAS]"
        ax.set_title(f'Cenario {name}: f={f_sinal} Hz, decim={decim}, '
                     f'fs_eff={fs_eff:.0f} Hz{alias_label}')
        ax.legend(fontsize=8)

    plt.suptitle(u"Etapa 2: Verificacao de Nyquist - Espectros Decimados",
                 fontsize=13, fontweight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, "etapa2_nyquist_cenarios.png"),
                dpi=150, bbox_inches='tight')
    plt.close()

    save_csv("etapa2_nyquist_verificacao.csv",
             ["cenario", "f_sinal_Hz", "decim", "fs_eff_Hz",
              "nyquist_Hz", "nyquist_ok", "f_esperada_Hz",
              "f_observada_Hz", "erro_Hz"],
             csv_rows)

    log(f"\n  -> etapa2_nyquist_cenarios.png")
    log(f"  -> dados/etapa2_nyquist_verificacao.csv")

    # Gerar figuras individuais com tempo + espectro para cada cenario
    for name, f_sinal, decim in scenarios:
        fs_eff = SAMP_RATE / decim
        orig, dec, fs_eff = capture_decimated(f_sinal, decim)
        plot_time_and_spectrum(
            orig, dec, fs_eff, f_sinal, decim,
            f"Cenario {name}: f={f_sinal} Hz, decim={decim}, "
            f"fs_eff={fs_eff:.0f} Hz",
            f"etapa2_cenario_{name}.png",
            markers=[(f_sinal, f'f = {f_sinal} Hz')])
        log(f"  -> etapa2_cenario_{name}.png")


# =====================================================================
# ETAPA 3: Calculo da frequencia de alias
# =====================================================================
def etapa3():
    log("\n" + "=" * 65)
    log("ETAPA 3: Calculo da frequencia de alias")
    log("=" * 65)

    alias_scenarios = [
        ('C', 7000, 4),
        ('E', 2500, 10),
        ('F', 3500, 10),
    ]

    log(f"\n  Cenarios com aliasing:")
    log(f"  {'Cen':>3} | {'f_sinal':>7} | {'fs_eff':>6} | "
        f"{'Nyquist':>7} | {'f_alias (calc)':>14} | {'f_alias (obs)':>13}")
    log(f"  {'-'*3}-+-{'-'*7}-+-{'-'*6}-+-{'-'*7}-+-{'-'*14}-+-{'-'*13}")

    csv_rows = []

    fig, axes = plt.subplots(len(alias_scenarios), 2, figsize=(16, 12))

    for idx, (name, f_sinal, decim) in enumerate(alias_scenarios):
        fs_eff = SAMP_RATE / decim
        nyquist = fs_eff / 2

        # Calculo analitico do alias
        f_alias_calc = calc_alias_freq(f_sinal, fs_eff)

        orig, dec, fs_eff = capture_decimated(f_sinal, decim)
        f_alias_obs, _ = find_peak_freq(dec, fs_eff)

        log(f"  {name:>3} | {f_sinal:>7} | {fs_eff:>6.0f} | "
            f"{nyquist:>7.0f} | {f_alias_calc:>14.0f} | "
            f"{f_alias_obs:>13.0f}")

        csv_rows.append([name, f_sinal, f"{fs_eff:.0f}",
                         f"{f_alias_calc:.0f}", f"{f_alias_obs:.0f}"])

        # Espectro original
        ax_o = axes[idx, 0]
        freqs_o, mag_o = compute_spectrum(orig, SAMP_RATE)
        ax_o.plot(freqs_o, mag_o, linewidth=0.8, color='#1f77b4')
        ax_o.axvline(f_sinal, color='r', ls='--', alpha=0.6,
                     label=f'f = {f_sinal} Hz')
        ax_o.axvline(nyquist, color='orange', ls=':', alpha=0.6,
                     label=f'Nyquist = {nyquist:.0f} Hz')
        ax_o.set_xlim([0, SAMP_RATE / 2])
        ax_o.set_xlabel(u'Frequencia (Hz)')
        ax_o.set_ylabel('Magnitude (dB)')
        ax_o.set_title(f'Cenario {name} - Original (fs = {SAMP_RATE} Hz)')
        ax_o.legend(fontsize=8)

        # Espectro decimado
        ax_d = axes[idx, 1]
        freqs_d, mag_d = compute_spectrum(dec, fs_eff)
        ax_d.plot(freqs_d, mag_d, linewidth=0.8, color='#d62728')
        ax_d.axvline(f_alias_calc, color='g', ls='--', alpha=0.6,
                     label=f'f_alias = {f_alias_calc:.0f} Hz')
        ax_d.set_xlim([0, fs_eff / 2])
        ax_d.set_xlabel(u'Frequencia (Hz)')
        ax_d.set_ylabel('Magnitude (dB)')
        ax_d.set_title(f'Cenario {name} - Decimado '
                       f'(fs_eff = {fs_eff:.0f} Hz)')
        ax_d.legend(fontsize=8)

    plt.suptitle(u"Etapa 3: Frequencias de Alias - Antes e Depois da "
                 u"Decimacao",
                 fontsize=13, fontweight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, "etapa3_alias_frequencias.png"),
                dpi=150, bbox_inches='tight')
    plt.close()

    save_csv("etapa3_alias_frequencias.csv",
             ["cenario", "f_sinal_Hz", "fs_eff_Hz",
              "f_alias_calculada_Hz", "f_alias_observada_Hz"],
             csv_rows)

    log(f"\n  Calculo analitico:")
    log(f"    C: f=7000, fs_eff=12000. f_alias = fs_eff - f = "
        f"12000 - 7000 = 5000 Hz")
    log(f"    E: f=2500, fs_eff=4800.  f_alias = fs_eff - f = "
        f"4800 - 2500  = 2300 Hz")
    log(f"    F: f=3500, fs_eff=4800.  f_alias = fs_eff - f = "
        f"4800 - 3500  = 1300 Hz")
    log(f"\n  -> etapa3_alias_frequencias.png")
    log(f"  -> dados/etapa3_alias_frequencias.csv")


# =====================================================================
# ETAPA 4: Filtro anti-aliasing
# =====================================================================
def etapa4():
    log("\n" + "=" * 65)
    log("ETAPA 4: Filtro anti-aliasing (LPF antes da decimacao)")
    log("=" * 65)

    test_cases = [
        ('C', 7000, 4,
         "f=7000 Hz atenuado pelo LPF (fc=5400 Hz). Alias eliminado."),
        ('E', 2500, 10,
         "f=2500 Hz ~ Nyquist (2400 Hz). LPF atenua o proprio sinal!"),
    ]

    fig, axes = plt.subplots(len(test_cases), 3, figsize=(18, 10))

    for idx, (name, f_sinal, decim, descr) in enumerate(test_cases):
        fs_eff = SAMP_RATE / decim
        nyquist = fs_eff / 2
        cutoff = nyquist * 0.9

        log(f"\n  Cenario {name}: f={f_sinal} Hz, decim={decim}, "
            f"fs_eff={fs_eff:.0f} Hz")
        log(f"    LPF cutoff = {cutoff:.0f} Hz "
            f"(0.9 x Nyquist = 0.9 x {nyquist:.0f})")

        # Sem filtro
        _, dec_nofilt, _ = capture_decimated(f_sinal, decim,
                                             use_filter=False)
        f_peak_nofilt, _ = find_peak_freq(dec_nofilt, fs_eff)

        # Com filtro
        _, dec_filt, _ = capture_decimated(f_sinal, decim,
                                           use_filter=True)
        f_peak_filt, peak_db_filt = find_peak_freq(dec_filt, fs_eff)

        log(f"    Sem filtro: pico em {f_peak_nofilt:.0f} Hz")
        log(f"    Com filtro: pico em {f_peak_filt:.0f} Hz "
            f"@ {peak_db_filt:.1f} dB")
        log(f"    Interpretacao: {descr}")

        # --- Plots ---
        # Espectro original
        orig, _, _ = capture_decimated(f_sinal, decim, use_filter=False)
        freqs_o, mag_o = compute_spectrum(orig, SAMP_RATE)
        ax0 = axes[idx, 0]
        ax0.plot(freqs_o, mag_o, linewidth=0.8, color='#1f77b4')
        ax0.axvline(f_sinal, color='r', ls='--', alpha=0.6,
                    label=f'f = {f_sinal} Hz')
        ax0.axvline(cutoff, color='orange', ls=':', alpha=0.6,
                    label=f'LPF cutoff = {cutoff:.0f} Hz')
        ax0.set_xlim([0, min(f_sinal * 2, SAMP_RATE / 2)])
        ax0.set_title(f'Cen. {name} - Original')
        ax0.set_xlabel(u'Frequencia (Hz)')
        ax0.set_ylabel('dB')
        ax0.legend(fontsize=8)

        # Espectro decimado SEM filtro
        freqs_d, mag_d = compute_spectrum(dec_nofilt, fs_eff)
        ax1 = axes[idx, 1]
        ax1.plot(freqs_d, mag_d, linewidth=0.8, color='#d62728')
        ax1.set_xlim([0, fs_eff / 2])
        ax1.set_title(f'Cen. {name} - Decimado SEM filtro')
        ax1.set_xlabel(u'Frequencia (Hz)')
        ax1.set_ylabel('dB')

        # Espectro decimado COM filtro
        freqs_df, mag_df = compute_spectrum(dec_filt, fs_eff)
        ax2 = axes[idx, 2]
        ax2.plot(freqs_df, mag_df, linewidth=0.8, color='#2ca02c')
        ax2.set_xlim([0, fs_eff / 2])
        ax2.set_title(f'Cen. {name} - Decimado COM filtro AA')
        ax2.set_xlabel(u'Frequencia (Hz)')
        ax2.set_ylabel('dB')

    plt.suptitle(u"Etapa 4: Efeito do Filtro Anti-Aliasing",
                 fontsize=13, fontweight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, "etapa4_filtro_anti_aliasing.png"),
                dpi=150, bbox_inches='tight')
    plt.close()

    log(f"\n  -> etapa4_filtro_anti_aliasing.png")
    log(f"\n  Resposta Q4:")
    log(f"    Cenario C (f=7000, fs_eff=12000): o LPF com fc=5400 Hz")
    log(f"    atenua o sinal em 7000 Hz antes da decimacao, eliminando")
    log(f"    o alias em 5000 Hz.")
    log(f"    Cenario E (f=2500, fs_eff=4800): o LPF com fc=2160 Hz")
    log(f"    atenua o proprio sinal em 2500 Hz, pois ele esta acima")
    log(f"    do cutoff. O sinal desaparece (ou fica muito atenuado).")


# =====================================================================
# ETAPA 5: Aliasing com multiplos tons
# =====================================================================
def etapa5():
    log("\n" + "=" * 65)
    log("ETAPA 5: Aliasing com multiplos tons")
    log("=" * 65)

    f1, f2 = 1000, 7000
    decim = 4
    fs_eff = SAMP_RATE / decim
    nyquist = fs_eff / 2

    log(f"  Dois tons: f1={f1} Hz + f2={f2} Hz")
    log(f"  decim={decim}, fs_eff={fs_eff:.0f} Hz, "
        f"Nyquist={nyquist:.0f} Hz")
    log(f"  f1={f1} Hz < {nyquist:.0f} Hz -> preservado")
    log(f"  f2={f2} Hz > {nyquist:.0f} Hz -> alias em "
        f"{calc_alias_freq(f2, fs_eff):.0f} Hz")

    fig, axes = plt.subplots(2, 2, figsize=(16, 10))

    # --- Sem filtro ---
    orig_nf, dec_nf, _ = capture_decimated(
        [f1, f2], decim, use_filter=False,
        amplitudes=[1.0, 1.0])

    # Espectro original
    freqs_o, mag_o = compute_spectrum(orig_nf, SAMP_RATE)
    axes[0, 0].plot(freqs_o, mag_o, linewidth=0.8, color='#1f77b4')
    axes[0, 0].axvline(f1, color='r', ls='--', alpha=0.6,
                       label=f'f1 = {f1} Hz')
    axes[0, 0].axvline(f2, color='g', ls='--', alpha=0.6,
                       label=f'f2 = {f2} Hz')
    axes[0, 0].axvline(nyquist, color='orange', ls=':', alpha=0.6,
                       label=f'Nyquist = {nyquist:.0f} Hz')
    axes[0, 0].set_xlim([0, SAMP_RATE / 2])
    axes[0, 0].set_title('Original (ambos os tons)')
    axes[0, 0].set_xlabel(u'Frequencia (Hz)')
    axes[0, 0].set_ylabel('dB')
    axes[0, 0].legend(fontsize=8)

    # Espectro decimado SEM filtro
    freqs_d, mag_d = compute_spectrum(dec_nf, fs_eff)
    f_alias_f2 = calc_alias_freq(f2, fs_eff)
    axes[0, 1].plot(freqs_d, mag_d, linewidth=0.8, color='#d62728')
    axes[0, 1].axvline(f1, color='r', ls='--', alpha=0.6,
                       label=f'f1 = {f1} Hz (preservado)')
    axes[0, 1].axvline(f_alias_f2, color='g', ls='--', alpha=0.6,
                       label=f'f2 alias = {f_alias_f2:.0f} Hz')
    axes[0, 1].set_xlim([0, fs_eff / 2])
    axes[0, 1].set_title('Decimado SEM filtro AA')
    axes[0, 1].set_xlabel(u'Frequencia (Hz)')
    axes[0, 1].set_ylabel('dB')
    axes[0, 1].legend(fontsize=8)

    log(f"\n  SEM filtro AA:")
    # Encontrar picos
    freqs_d, mag_d = compute_spectrum(dec_nf, fs_eff)
    mag_d_copy = mag_d.copy()
    mag_d_copy[0] = -200
    peaks_idx, _ = find_peaks(mag_d_copy, height=-30, distance=5)
    peaks_sorted = sorted(peaks_idx, key=lambda i: mag_d_copy[i],
                          reverse=True)
    for pi in peaks_sorted[:4]:
        log(f"    Pico em {freqs_d[pi]:.0f} Hz @ {mag_d[pi]:.1f} dB")

    # --- Com filtro ---
    orig_f, dec_f, _ = capture_decimated(
        [f1, f2], decim, use_filter=True,
        amplitudes=[1.0, 1.0])

    # Espectro original com indicacao do filtro
    cutoff = nyquist * 0.9
    freqs_of, mag_of = compute_spectrum(orig_f, SAMP_RATE)
    axes[1, 0].plot(freqs_of, mag_of, linewidth=0.8, color='#1f77b4')
    axes[1, 0].axvline(f1, color='r', ls='--', alpha=0.6,
                       label=f'f1 = {f1} Hz')
    axes[1, 0].axvline(f2, color='g', ls='--', alpha=0.6,
                       label=f'f2 = {f2} Hz')
    axes[1, 0].axvline(cutoff, color='purple', ls=':', alpha=0.6,
                       label=f'LPF cutoff = {cutoff:.0f} Hz')
    axes[1, 0].set_xlim([0, SAMP_RATE / 2])
    axes[1, 0].set_title('Original (com indicacao do LPF)')
    axes[1, 0].set_xlabel(u'Frequencia (Hz)')
    axes[1, 0].set_ylabel('dB')
    axes[1, 0].legend(fontsize=8)

    # Espectro decimado COM filtro
    freqs_df, mag_df = compute_spectrum(dec_f, fs_eff)
    axes[1, 1].plot(freqs_df, mag_df, linewidth=0.8, color='#2ca02c')
    axes[1, 1].axvline(f1, color='r', ls='--', alpha=0.6,
                       label=f'f1 = {f1} Hz (preservado)')
    axes[1, 1].set_xlim([0, fs_eff / 2])
    axes[1, 1].set_title('Decimado COM filtro AA')
    axes[1, 1].set_xlabel(u'Frequencia (Hz)')
    axes[1, 1].set_ylabel('dB')
    axes[1, 1].legend(fontsize=8)

    log(f"\n  COM filtro AA (cutoff = {cutoff:.0f} Hz):")
    mag_df_copy = mag_df.copy()
    mag_df_copy[0] = -200
    peaks_idx_f, _ = find_peaks(mag_df_copy, height=-30, distance=5)
    peaks_sorted_f = sorted(peaks_idx_f, key=lambda i: mag_df_copy[i],
                            reverse=True)
    for pi in peaks_sorted_f[:4]:
        log(f"    Pico em {freqs_df[pi]:.0f} Hz @ {mag_df[pi]:.1f} dB")

    if len(peaks_sorted_f) == 0:
        log(f"    Apenas f1 = {f1} Hz preservado; f2 = {f2} Hz "
            f"totalmente eliminado pelo LPF.")

    plt.suptitle(u"Etapa 5: Aliasing com Multiplos Tons "
                 u"(f1=1000 Hz + f2=7000 Hz, decim=4)",
                 fontsize=13, fontweight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, "etapa5_multiplos_tons.png"),
                dpi=150, bbox_inches='tight')
    plt.close()

    log(f"\n  -> etapa5_multiplos_tons.png")
    log(f"\n  Resultado:")
    log(f"    Sem filtro: ambos os tons aparecem no espectro decimado.")
    log(f"    f1=1000 Hz preservado, f2=7000 Hz aparece como alias "
        f"em {f_alias_f2:.0f} Hz.")
    log(f"    Os dois picos sao indistinguiveis de dois tons reais.")
    log(f"    Com filtro AA: f2=7000 Hz eh atenuado pelo LPF antes da")
    log(f"    decimacao. Apenas f1=1000 Hz aparece no espectro.")


# =====================================================================
# PARTE II -- QUANTIZACAO PCM
# =====================================================================
class QuantFlowgraph(gr.top_block):
    """Senoide de fundo de escala -> Quantizador -> captura.
    Tambem captura o sinal original para calcular o erro e o SQNR."""

    def __init__(self, n_bits, vmax=VMAX, f=F_QUANT, n_samples=N_SAMPLES_Q):
        gr.top_block.__init__(self, "Pratica08_Quant")
        self.src = analog.sig_source_f(SAMP_RATE, analog.GR_COS_WAVE, f, vmax, 0)
        self.head_o = blocks.head(gr.sizeof_float, n_samples)
        self.sink_o = blocks.vector_sink_f()
        self.connect(self.src, self.head_o, self.sink_o)

        self.src2 = analog.sig_source_f(SAMP_RATE, analog.GR_COS_WAVE, f, vmax, 0)
        self.quant = Quantizer(n_bits, vmax)
        self.head_q = blocks.head(gr.sizeof_float, n_samples)
        self.sink_q = blocks.vector_sink_f()
        self.connect(self.src2, self.quant, self.head_q, self.sink_q)


def measure_sqnr(n_bits, vmax=VMAX, f=F_QUANT, n_samples=N_SAMPLES_Q):
    """Roda o flowgraph e retorna (orig, quant, sqnr_dB)."""
    tb = QuantFlowgraph(n_bits, vmax, f, n_samples)
    tb.run()
    orig = np.array(tb.sink_o.data())
    quant = np.array(tb.sink_q.data())
    m = min(len(orig), len(quant))
    orig, quant = orig[:m], quant[:m]
    err = quant - orig
    Ps = np.mean(orig ** 2)
    Pq = np.mean(err ** 2)
    sqnr = 10 * np.log10(Ps / Pq)
    return orig, quant, sqnr


def etapa6():
    """SQNR x numero de bits: valida a regra dos 6 dB/bit no GNU Radio."""
    log("\n" + "=" * 65)
    log("ETAPA 6: Quantizacao PCM -- SQNR x numero de bits")
    log("=" * 65)
    log(f"  Senoide de fundo de escala: f = {F_QUANT} Hz, amplitude = {VMAX} V")
    log(f"  Faixa do quantizador: [-{VMAX}, +{VMAX}] V  =>  Vpp = {2*VMAX} V")
    log(f"  Amostras por medicao: {N_SAMPLES_Q}")
    log("")

    bits_list = [2, 3, 4, 6, 8, 10, 12, 16]
    vpp = 2 * VMAX

    log(f"  {'n':>3} | {'L':>6} | {'Delta(mV)':>9} | {'Pq(V^2)':>11} | "
        f"{'SQNR_teo':>8} | {'SQNR_med':>8} | {'erro(dB)':>8}")
    log(f"  {'-'*3}-+-{'-'*6}-+-{'-'*9}-+-{'-'*11}-+-{'-'*8}-+-{'-'*8}-+-{'-'*8}")

    csv_rows = []
    sqnr_meas = []
    sqnr_theo = []
    for n in bits_list:
        L = 2 ** n
        delta = vpp / L
        Pq = delta ** 2 / 12.0
        theo = 1.76 + 6.02 * n
        _, _, meas = measure_sqnr(n)
        erro = meas - theo
        sqnr_meas.append(meas)
        sqnr_theo.append(theo)
        log(f"  {n:>3} | {L:>6} | {delta*1000:>9.4f} | {Pq:>11.3e} | "
            f"{theo:>8.2f} | {meas:>8.2f} | {erro:>+8.2f}")
        csv_rows.append([n, L, f"{delta*1000:.4f}", f"{Pq:.4e}",
                         f"{theo:.2f}", f"{meas:.2f}", f"{erro:+.2f}"])

    save_csv("etapa6_sqnr_vs_bits.csv",
             ["n_bits", "L_niveis", "Delta_mV", "Pq_V2",
              "SQNR_teorico_dB", "SQNR_medido_dB", "erro_dB"], csv_rows)

    # Figura 1: SQNR x bits (medido vs teoria)
    fig, ax = plt.subplots(figsize=(9, 6))
    ax.plot(bits_list, sqnr_theo, 'o-', color='#1f77b4',
            label='Teoria: 1,76 + 6,02 n')
    ax.plot(bits_list, sqnr_meas, 's--', color='#d62728',
            label='Medido (GNU Radio)')
    ax.set_xlabel('Numero de bits n')
    ax.set_ylabel('SQNR (dB)')
    ax.set_title('Etapa 6: SQNR x numero de bits (senoide de fundo de escala)')
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, "etapa6_sqnr_vs_bits.png"),
                dpi=150, bbox_inches='tight')
    plt.close()

    # Figura 2: forma de onda original vs quantizada para n = 2, 3, 8
    fig, axes = plt.subplots(3, 1, figsize=(11, 9), sharex=True)
    for ax, n in zip(axes, [2, 3, 8]):
        orig, quant, meas = measure_sqnr(n, n_samples=4000)
        n_pts = int(3 * SAMP_RATE / F_QUANT)  # ~3 periodos
        t = np.arange(n_pts) / SAMP_RATE * 1000
        ax.plot(t, orig[:n_pts], color='#1f77b4', lw=1.2, label='Original')
        ax.step(t, quant[:n_pts], color='#d62728', lw=1.0, where='mid',
                label=f'Quantizado (n={n}, SQNR={meas:.1f} dB)')
        ax.set_ylabel('Amplitude (V)')
        ax.legend(loc='upper right', fontsize=9)
        ax.grid(True, alpha=0.3)
    axes[-1].set_xlabel('Tempo (ms)')
    axes[0].set_title('Etapa 6: efeito da resolucao na forma de onda')
    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, "etapa6_formas_de_onda.png"),
                dpi=150, bbox_inches='tight')
    plt.close()

    log(f"\n  -> etapa6_sqnr_vs_bits.png")
    log(f"  -> etapa6_formas_de_onda.png")
    log(f"  -> dados/etapa6_sqnr_vs_bits.csv")


def etapa7():
    """Projeto PCM: bits necessarios para um SQNR-alvo e taxa de bits."""
    log("\n" + "=" * 65)
    log("ETAPA 7: Projeto PCM -- bits necessarios e taxa de bits")
    log("=" * 65)

    log("\n  (a) Numero minimo de bits: n >= (SQNR - 1,76)/6,02")
    for alvo in [50, 60, 70, 90]:
        n_min = (alvo - 1.76) / 6.02
        log(f"      SQNR >= {alvo:>3} dB  ->  n >= {n_min:5.2f}  ->  "
            f"{int(np.ceil(n_min))} bits")

    log("\n  (b) Taxa de bits PCM: R = fs * n * (n_canais)")
    casos = [
        ("Voz VoIP wideband (HD Voice)", 16000, 16, 1),
        ("Audio de alta resolucao (Hi-Res)", 96000, 24, 2),
    ]
    for nome, fs, n, ch in casos:
        R = fs * n * ch
        log(f"      {nome:<33}: fs={fs} Hz, n={n} bits, canais={ch}  ->  "
            f"R = {R} bps = {R/1000:.1f} kbps = {R/1e6:.3f} Mbps")

    log("\n  (c) Passo e ruido de quantizacao (Vpp = 2 V):")
    log(f"      {'n':>3} | {'L':>6} | {'Delta':>12} | {'Pq=Delta^2/12':>14}")
    for n in [2, 4, 8, 16]:
        L = 2 ** n
        delta = 2.0 / L
        Pq = delta ** 2 / 12.0
        log(f"      {n:>3} | {L:>6} | {delta*1000:>9.4f} mV | {Pq:>14.4e}")


# =====================================================================
# PARTE III -- RECONSTRUCAO ZOH E EQUALIZACAO
# =====================================================================
def zoh_noise_psd(use_eq=False, nsamp=4000000):
    """PSD de ruido branco passado pelo ZOH (Repeat) e, opcionalmente,
    pelo equalizador. Revela a forma |sinc(f/fs_low)|^2 em toda a banda."""
    tb = gr.top_block()
    src = analog.noise_source_f(analog.GR_GAUSSIAN, 1.0, 42)
    rep = blocks.repeat(gr.sizeof_float, N_ZOH)
    head = blocks.head(gr.sizeof_float, nsamp)
    snk = blocks.vector_sink_f()
    if use_eq:
        taps = design_eq(FS_LOW, SAMP_RATE, EQ_NTAPS)
        eq = filter.fir_filter_fff(1, taps.tolist())
        tb.connect(src, rep, eq, head, snk)
    else:
        tb.connect(src, rep, head, snk)
    tb.run()
    x = np.array(snk.data())
    L = 4096
    w = np.hanning(L)
    acc = np.zeros(L // 2 + 1)
    cnt = 0
    for i in range(0, len(x) - L, L):
        X = np.fft.rfft(x[i:i + L] * w)
        acc += np.abs(X) ** 2
        cnt += 1
    psd = acc / cnt
    freqs = np.fft.rfftfreq(L, 1.0 / SAMP_RATE)
    return freqs, 10 * np.log10(psd / psd[1] + 1e-18)


def zoh_tone(f0, use_eq=False, nsamp=4000):
    """Sinal reconstruido por ZOH no tempo, para a figura da escada."""
    tb = gr.top_block()
    src = analog.sig_source_f(FS_LOW, analog.GR_COS_WAVE, f0, 1.0, 0)
    rep = blocks.repeat(gr.sizeof_float, N_ZOH)
    head = blocks.head(gr.sizeof_float, nsamp)
    snk = blocks.vector_sink_f()
    if use_eq:
        taps = design_eq(FS_LOW, SAMP_RATE, EQ_NTAPS)
        eq = filter.fir_filter_fff(1, taps.tolist())
        tb.connect(src, rep, eq, head, snk)
    else:
        tb.connect(src, rep, head, snk)
    tb.run()
    return np.array(snk.data())


def etapa8():
    """Reconstrucao ZOH: droop sinc e equalizacao inverse-sinc."""
    log("\n" + "=" * 65)
    log("ETAPA 8: Reconstrucao ZOH e equalizacao")
    log("=" * 65)
    log(f"  fs_low = {FS_LOW} Hz, N_ZOH = {N_ZOH}, "
        f"fs_high = {SAMP_RATE} Hz, borda da banda = {FS_LOW/2:.0f} Hz")
    log(f"  H_ZOH(f) = sinc(f/fs_low); droop na borda = "
        f"20log10(sinc 0,5) = {20*np.log10(np.sinc(0.5)):.2f} dB")
    log("")

    freqs0, psd0 = zoh_noise_psd(use_eq=False)
    freqs1, psd1 = zoh_noise_psd(use_eq=True)

    def at(fr, p, f):
        return p[np.argmin(np.abs(fr - f))]

    log(f"  {'f(Hz)':>6} | {'sinc^2 teo(dB)':>14} | {'ZOH med(dB)':>11} | "
        f"{'equaliz med(dB)':>15}")
    log(f"  {'-'*6}-+-{'-'*14}-+-{'-'*11}-+-{'-'*15}")
    csv_rows = []
    for f in [300, 1500, 2400, 2700, 3000]:
        teo = 20 * np.log10(np.sinc(f / FS_LOW))
        z = at(freqs0, psd0, f)
        e = at(freqs1, psd1, f)
        log(f"  {f:>6} | {teo:>14.2f} | {z:>11.2f} | {e:>15.2f}")
        csv_rows.append([f, f"{teo:.2f}", f"{z:.2f}", f"{e:.2f}"])
    save_csv("etapa8_zoh_droop.csv",
             ["f_Hz", "sinc2_teorico_dB", "ZOH_medido_dB",
              "equalizado_medido_dB"], csv_rows)

    # atenuacao das imagens em torno de fs_low
    log("\n  Imagens espectrais (nulos do sinc em k*fs_low):")
    for f in [FS_LOW - 600, FS_LOW, FS_LOW + 600]:
        log(f"    f={f:.0f} Hz: ZOH={at(freqs0,psd0,f):.1f} dB, "
            f"equalizado={at(freqs1,psd1,f):.1f} dB")

    # Figura 1: espectro ZOH vs sinc^2 vs equalizado
    fig, ax = plt.subplots(figsize=(11, 6))
    ax.plot(freqs0, psd0, color='#d62728', lw=1.0, label='ZOH (medido)')
    sinc2 = 20 * np.log10(np.abs(np.sinc(freqs0 / FS_LOW)) + 1e-9)
    ax.plot(freqs0, sinc2, color='#1f77b4', lw=1.2, ls='--',
            label='|sinc(f/fs_low)|^2 (teoria)')
    ax.plot(freqs1, psd1, color='#2ca02c', lw=1.0, label='Equalizado (medido)')
    ax.axvline(FS_LOW / 2, color='gray', ls=':',
               label=f'borda fs_low/2 = {FS_LOW/2:.0f} Hz')
    ax.set_xlim([0, SAMP_RATE / 2])
    ax.set_ylim([-60, 10])
    ax.set_xlabel('Frequencia (Hz)')
    ax.set_ylabel('Magnitude (dB)')
    ax.set_title('Etapa 8: ZOH (droop sinc + imagens) e equalizacao inverse-sinc')
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, "etapa8_zoh_espectro.png"),
                dpi=150, bbox_inches='tight')
    plt.close()

    # Figura 2: escada no tempo
    f0 = 750
    zoh = zoh_tone(f0, use_eq=False)
    n_pts = int(2.5 * SAMP_RATE / f0)
    t = np.arange(n_pts) / SAMP_RATE * 1000
    low = zoh[:n_pts:N_ZOH]
    t_low = np.arange(len(low)) * N_ZOH / SAMP_RATE * 1000
    fig, ax = plt.subplots(figsize=(11, 5))
    ax.step(t, zoh[:n_pts], where='post', color='#d62728', lw=1.2,
            label='Saida ZOH (escada)')
    ax.plot(t_low, low, 'o', color='#1f77b4', ms=6,
            label=f'Amostras a fs_low = {FS_LOW} Hz')
    ax.set_xlabel('Tempo (ms)')
    ax.set_ylabel('Amplitude')
    ax.set_title(f'Etapa 8: saida do ZOH no tempo (tom de {f0} Hz)')
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, "etapa8_zoh_escada.png"),
                dpi=150, bbox_inches='tight')
    plt.close()

    log(f"\n  -> etapa8_zoh_espectro.png")
    log(f"  -> etapa8_zoh_escada.png")
    log(f"  -> dados/etapa8_zoh_droop.csv")


# =====================================================================
# RESPOSTAS
# =====================================================================
def respostas():
    log("\n" + "=" * 65)
    log("RESPOSTAS ESPERADAS")
    log("=" * 65)

    log("\n  Q1: Tabela de Nyquist (fs/2 = Nyquist; alias = |f0 - n*fs|):")
    log("      A (1000, fs=12000): Nyquist OK (1000 < 6000); sem alias.")
    log("      B (5000, fs=12000): Nyquist OK (5000 < 6000); sem alias.")
    log("      C (7000, fs=12000): VIOLA; f_alias = |7000-12000| = 5000 Hz.")
    log("      D (1000, fs=4800):  Nyquist OK (1000 < 2400); sem alias.")
    log("      E (2500, fs=4800):  VIOLA; f_alias = |2500-4800| = 2300 Hz.")
    log("      F (3500, fs=4800):  VIOLA; f_alias = |3500-4800| = 1300 Hz.")

    log("\n  Q2: Cenario C: f_aparente = 5000 Hz. Em 1 ms o sinal decimado")
    log("      aparenta 5 ciclos (5000 Hz * 1 ms), enquanto o original de")
    log("      7000 Hz teria 7 ciclos. As amostras sao identicas as de 5000 Hz.")

    log("\n  Q3: Vpp = 2 V; L = 2^n; Delta = 2/L; Pq = Delta^2/12:")
    log("      n=2 : L=4    Delta=500,0000 mV  Pq=2,083e-02 V^2")
    log("      n=4 : L=16   Delta=125,0000 mV  Pq=1,302e-03 V^2")
    log("      n=8 : L=256  Delta=  7,8125 mV  Pq=5,086e-06 V^2")
    log("      n=16: L=65536 Delta=0,030518 mV Pq=7,761e-11 V^2")

    log("\n  Q4: SQNR_teorico = 1,76 + 6,02 n  (ver tabela da Etapa 6):")
    log("      n=4 -> 25,84 dB | n=8 -> 49,92 dB | n=12 -> 74,00 dB |")
    log("      n=16 -> 98,08 dB. O medido no GNU Radio coincide (erro < 1 dB).")

    log("\n  Q5: n >= (SQNR - 1,76)/6,02:")
    log("      SQNR >= 60 dB -> n >= 9,67  -> 10 bits.")
    log("      SQNR >= 90 dB -> n >= 14,66 -> 15 bits.")

    log("\n  Q6: R = fs * n * canais:")
    log("      Voz VoIP wideband (16000 Hz, 16 bits, 1 canal)")
    log("        -> 256000 bps = 256 kbps = 0,256 Mbps.")
    log("      Audio Hi-Res streaming (96000 Hz, 24 bits, 2 canais)")
    log("        -> 4608000 bps = 4608 kbps = 4,608 Mbps.")

    log("\n  Q7: Atenuacao do ZOH = 20log10|sinc(f/fs_low)|, fs_low=6000 Hz:")
    log("      f=1500 Hz -> -0,91 dB | f=2400 Hz -> -2,42 dB |")
    log("      f=3000 Hz -> -3,92 dB. Coincide com o piso de PSD medido.")

    log("\n  Q8: Na borda f=fs_low/2=3000 Hz o droop do ZOH e -3,92 dB.")
    log("      O equalizador inverse-sinc achata a banda de passagem para")
    log("      menos de ~0,5 dB ate ~0,4 fs_low e ainda atenua as imagens")
    log("      espectrais em torno de fs_low de ~-19 dB para abaixo de -80 dB.")


# =====================================================================
# MAIN
# =====================================================================
if __name__ == '__main__':
    log("=" * 65)
    log(u"PRATICA 08 -- CONVERSAO A/D: AMOSTRAGEM, ALIASING E QUANTIZACAO PCM")
    log("GABARITO DO PROFESSOR")
    log(f"Data: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    log(f"GNU Radio: {gr.version()}")
    log(f"Sample Rate: {SAMP_RATE} Hz | Amostras: {N_SAMPLES}")
    log(f"Saida: {BASE_DIR}")
    log("=" * 65)

    # Parte I -- Amostragem e Aliasing
    etapa1()
    etapa2()
    etapa3()
    etapa4()
    etapa5()
    # Parte II -- Quantizacao PCM
    etapa6()
    etapa7()
    # Parte III -- Reconstrucao ZOH e equalizacao
    etapa8()
    respostas()

    log("\n" + "=" * 65)
    log("GABARITO COMPLETO GERADO COM SUCESSO")
    log("=" * 65)

    # Salvar relatorio em texto
    report_path = os.path.join(BASE_DIR, "relatorio.txt")
    with open(report_path, 'w') as f:
        f.write('\n'.join(relatorio))
    print(f"\nRelatorio salvo em: {report_path}")
