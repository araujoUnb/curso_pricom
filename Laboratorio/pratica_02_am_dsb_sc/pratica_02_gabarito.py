#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pratica 02 -- Modulacao AM DSB-SC: Gabarito do Professor
=========================================================
Executa flowgraphs da Pratica 02 em modo headless (sem GUI),
reproduzindo todas as etapas do enunciado e gerando:

  1. Figuras PNG de referencia (tempo + espectro) para cada cenario
  2. Dados numericos de cada medicao (bandas laterais, atenuacao)
  3. CSVs com resultados tabulados
  4. Relatorio resumo em texto

Execucao:
    /usr/bin/python3 pratica_02_gabarito.py

Saida:
    ./pratica_02_gabarito/
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
except ImportError:
    print("ERRO: GNU Radio nao encontrado.")
    print("Execute com: /usr/bin/python3 pratica_02_gabarito.py")
    sys.exit(1)

try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
except ImportError:
    print("ERRO: matplotlib nao encontrado.")
    sys.exit(1)

from gnuradio.filter import firdes

# =====================================================================
# CONFIGURACAO
# =====================================================================
SAMP_RATE = 48000
FC = 5000          # Frequencia da portadora (Hz)
FM = 500           # Frequencia da mensagem (Hz)
AMP_C = 1.0        # Amplitude da portadora
AMP_M = 1.0        # Amplitude da mensagem
N_SAMPLES = 48000  # 1 segundo de dados

BASE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "pratica_02_gabarito")
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
class DSBSCModulator(gr.top_block):
    """Flowgraph: mensagem x portadora -> DSB-SC."""

    def __init__(self, fm=FM, fc=FC, amp_m=AMP_M, amp_c=AMP_C,
                 n_samples=N_SAMPLES):
        gr.top_block.__init__(self, "DSB-SC Modulator")

        # Fontes
        self.msg_src = analog.sig_source_f(
            SAMP_RATE, analog.GR_COS_WAVE, fm, amp_m, 0)
        self.carrier_src = analog.sig_source_f(
            SAMP_RATE, analog.GR_COS_WAVE, fc, amp_c, 0)

        # Multiplicador -> DSB-SC
        self.multiply = blocks.multiply_ff()

        # Captura
        self.head_mod = blocks.head(gr.sizeof_float, n_samples)
        self.sink_mod = blocks.vector_sink_f()

        # Captura da mensagem original
        self.head_msg = blocks.head(gr.sizeof_float, n_samples)
        self.sink_msg = blocks.vector_sink_f()

        # Conexoes
        self.connect(self.msg_src, (self.multiply, 0))
        self.connect(self.carrier_src, (self.multiply, 1))
        self.connect(self.multiply, self.head_mod, self.sink_mod)
        self.connect(self.msg_src, self.head_msg, self.sink_msg)


class DSBSCDemodulator(gr.top_block):
    """Flowgraph: DSB-SC -> multiplicar por portadora local -> LPF."""

    def __init__(self, fm=FM, fc=FC, phase_error_deg=0.0,
                 lpf_cutoff=None, lpf_transition=200,
                 n_samples=N_SAMPLES):
        gr.top_block.__init__(self, "DSB-SC Demodulator")

        if lpf_cutoff is None:
            lpf_cutoff = 1.5 * fm

        phase_rad = np.deg2rad(phase_error_deg)

        # Fonte mensagem
        self.msg_src = analog.sig_source_f(
            SAMP_RATE, analog.GR_COS_WAVE, fm, AMP_M, 0)

        # Portadora do modulador
        self.carrier_tx = analog.sig_source_f(
            SAMP_RATE, analog.GR_COS_WAVE, fc, AMP_C, 0)

        # Modulador DSB-SC
        self.mod_mult = blocks.multiply_ff()
        self.connect(self.msg_src, (self.mod_mult, 0))
        self.connect(self.carrier_tx, (self.mod_mult, 1))

        # Portadora local do demodulador (com erro de fase)
        self.carrier_rx = analog.sig_source_f(
            SAMP_RATE, analog.GR_COS_WAVE, fc, 1.0, 0,
            phase_rad)

        # Demodulador: multiplicar por portadora local
        self.demod_mult = blocks.multiply_ff()
        self.connect(self.mod_mult, (self.demod_mult, 0))
        self.connect(self.carrier_rx, (self.demod_mult, 1))

        # Filtro passa-baixa
        lpf_taps = firdes.low_pass(1, SAMP_RATE, lpf_cutoff,
                                   lpf_transition)
        self.lpf = filter.fir_filter_fff(1, lpf_taps)
        self.connect(self.demod_mult, self.lpf)

        # Captura saida demodulada
        self.head_out = blocks.head(gr.sizeof_float, n_samples)
        self.sink_out = blocks.vector_sink_f()
        self.connect(self.lpf, self.head_out, self.sink_out)

        # Captura mensagem original
        self.head_msg = blocks.head(gr.sizeof_float, n_samples)
        self.sink_msg = blocks.vector_sink_f()
        self.connect(self.msg_src, self.head_msg, self.sink_msg)

        # Captura sinal DSB-SC
        self.head_mod = blocks.head(gr.sizeof_float, n_samples)
        self.sink_mod = blocks.vector_sink_f()
        self.connect(self.mod_mult, self.head_mod, self.sink_mod)


# =====================================================================
# FUNCOES DE ANALISE
# =====================================================================
def spectrum(data, fft_size=4096):
    """Retorna (freqs_hz, magnitude_dB) usando janela Hann."""
    w = np.hanning(fft_size)
    seg = data[:fft_size] if len(data) >= fft_size else data
    if len(seg) < fft_size:
        seg = np.pad(seg, (0, fft_size - len(seg)))
    X = np.fft.rfft(seg * w)
    mag = 20 * np.log10(np.abs(X) / fft_size + 1e-12)
    freqs = np.fft.rfftfreq(fft_size, 1.0 / SAMP_RATE)
    return freqs, mag


def find_peak_near(freqs, mag, target_freq, margin=100):
    """Encontra pico espectral proximo a target_freq."""
    mask = np.abs(freqs - target_freq) < margin
    if not np.any(mask):
        return target_freq, -100.0
    idx = np.where(mask)[0]
    best = idx[np.argmax(mag[idx])]
    return freqs[best], mag[best]


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
# ETAPA 1: Modulador DSB-SC
# =====================================================================
def etapa1():
    log("\n" + "=" * 65)
    log("ETAPA 1: Modulador DSB-SC")
    log("=" * 65)

    tb = DSBSCModulator(fm=FM, fc=FC)
    tb.run()
    msg_data = np.array(tb.sink_msg.data())
    mod_data = np.array(tb.sink_mod.data())

    # --- Plots ---
    fig, axes = plt.subplots(2, 2, figsize=(15, 9))

    # Tempo - mensagem
    n_pts = int(5 * SAMP_RATE / 1000)  # 5 ms
    t = np.arange(n_pts) / SAMP_RATE * 1000
    axes[0, 0].plot(t, msg_data[:n_pts], linewidth=0.8, color='#1f77b4')
    axes[0, 0].set_xlabel('Tempo (ms)')
    axes[0, 0].set_ylabel('Amplitude')
    axes[0, 0].set_title(f'Mensagem: cos(2pi {FM} t)')

    # Tempo - DSB-SC
    axes[0, 1].plot(t, mod_data[:n_pts], linewidth=0.8, color='#d62728')
    axes[0, 1].set_xlabel('Tempo (ms)')
    axes[0, 1].set_ylabel('Amplitude')
    axes[0, 1].set_title('Sinal DSB-SC')

    # Espectro - mensagem
    freqs, mag = spectrum(msg_data)
    axes[1, 0].plot(freqs, mag, linewidth=0.8, color='#1f77b4')
    axes[1, 0].set_xlabel('Frequencia (Hz)')
    axes[1, 0].set_ylabel('Magnitude (dB)')
    axes[1, 0].set_title('Espectro da Mensagem')
    axes[1, 0].set_xlim([0, SAMP_RATE / 2])
    axes[1, 0].axvline(FM, color='r', ls='--', alpha=0.5, label=f'{FM} Hz')
    axes[1, 0].legend(fontsize=8)

    # Espectro - DSB-SC
    freqs_m, mag_m = spectrum(mod_data)
    axes[1, 1].plot(freqs_m, mag_m, linewidth=0.8, color='#d62728')
    axes[1, 1].set_xlabel('Frequencia (Hz)')
    axes[1, 1].set_ylabel('Magnitude (dB)')
    axes[1, 1].set_title('Espectro DSB-SC')
    axes[1, 1].set_xlim([0, SAMP_RATE / 2])
    axes[1, 1].axvline(FC - FM, color='#2ca02c', ls='--', alpha=0.6,
                        label=f'fc-fm = {FC - FM} Hz')
    axes[1, 1].axvline(FC + FM, color='#ff7f0e', ls='--', alpha=0.6,
                        label=f'fc+fm = {FC + FM} Hz')
    axes[1, 1].axvline(FC, color='gray', ls=':', alpha=0.5,
                        label=f'fc = {FC} Hz (suprimida)')
    axes[1, 1].legend(fontsize=8)

    fig.suptitle("Etapa 1: Modulador DSB-SC", fontsize=13, fontweight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, "etapa1_dsbsc_modulador.png"),
                dpi=150, bbox_inches='tight')
    plt.close()

    # Verificar bandas laterais e ausencia de portadora
    _, mag_lsb = find_peak_near(freqs_m, mag_m, FC - FM)
    _, mag_usb = find_peak_near(freqs_m, mag_m, FC + FM)
    _, mag_carrier = find_peak_near(freqs_m, mag_m, FC, margin=50)

    log(f"  Banda lateral inferior (fc-fm = {FC - FM} Hz): {mag_lsb:.1f} dB")
    log(f"  Banda lateral superior (fc+fm = {FC + FM} Hz): {mag_usb:.1f} dB")
    log(f"  Portadora (fc = {FC} Hz): {mag_carrier:.1f} dB")
    log(f"  Supressao da portadora: {max(mag_lsb, mag_usb) - mag_carrier:.1f} dB")
    log(f"  -> etapa1_dsbsc_modulador.png")
    log(f"\n  Resposta Q1: Nao ha portadora no espectro DSB-SC.")
    log(f"  A multiplicacao cos(fm)cos(fc) = (1/2)[cos(fc-fm) + cos(fc+fm)]")
    log(f"  gera apenas as bandas laterais, sem componente em fc.")


# =====================================================================
# ETAPA 2: Variacao da frequencia da mensagem
# =====================================================================
def etapa2():
    log("\n" + "=" * 65)
    log("ETAPA 2: Variacao da frequencia da mensagem")
    log("=" * 65)

    test_freqs = [200, 500, 1000, 2000]
    fig, axes = plt.subplots(2, 2, figsize=(15, 9))
    csv_rows = []

    log(f"\n  {'fm (Hz)':>8} | {'LSB (Hz)':>10} | {'USB (Hz)':>10} | "
        f"{'LSB (dB)':>10} | {'USB (dB)':>10}")
    log(f"  {'-'*8}-+-{'-'*10}-+-{'-'*10}-+-{'-'*10}-+-{'-'*10}")

    for ax, fm in zip(axes.flat, test_freqs):
        tb = DSBSCModulator(fm=fm, fc=FC)
        tb.run()
        mod_data = np.array(tb.sink_mod.data())

        freqs, mag = spectrum(mod_data)

        lsb_freq, lsb_mag = find_peak_near(freqs, mag, FC - fm)
        usb_freq, usb_mag = find_peak_near(freqs, mag, FC + fm)

        ax.plot(freqs, mag, linewidth=0.8)
        ax.axvline(FC - fm, color='#2ca02c', ls='--', alpha=0.6,
                   label=f'fc-fm={FC - fm}')
        ax.axvline(FC + fm, color='#ff7f0e', ls='--', alpha=0.6,
                   label=f'fc+fm={FC + fm}')
        ax.axvline(FC, color='gray', ls=':', alpha=0.4)
        ax.set_title(f'fm = {fm} Hz')
        ax.set_xlabel('Frequencia (Hz)')
        ax.set_ylabel('dB')
        ax.set_xlim([0, min(FC + fm + 2000, SAMP_RATE / 2)])
        ax.legend(fontsize=7)

        log(f"  {fm:>8} | {lsb_freq:>10.0f} | {usb_freq:>10.0f} | "
            f"{lsb_mag:>10.1f} | {usb_mag:>10.1f}")
        csv_rows.append([fm, FC - fm, FC + fm, f"{lsb_mag:.1f}",
                         f"{usb_mag:.1f}"])

    plt.suptitle("Etapa 2: Variacao da Frequencia da Mensagem",
                 fontsize=13, fontweight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, "etapa2_variacao_fm.png"),
                dpi=150, bbox_inches='tight')
    plt.close()

    save_csv("etapa2_bandas_laterais.csv",
             ["fm_Hz", "LSB_Hz", "USB_Hz", "LSB_dB", "USB_dB"],
             csv_rows)

    log(f"\n  -> etapa2_variacao_fm.png")
    log(f"  -> dados/etapa2_bandas_laterais.csv")
    log(f"\n  Resposta Q2: As bandas laterais aparecem em fc +/- fm.")
    log(f"  Ao aumentar fm, as bandas se afastam simetricamente de fc.")
    log(f"  A largura de banda do sinal DSB-SC e 2*fm.")


# =====================================================================
# ETAPA 3: Demodulacao coerente
# =====================================================================
def etapa3():
    log("\n" + "=" * 65)
    log("ETAPA 3: Demodulacao coerente")
    log("=" * 65)

    tb = DSBSCDemodulator(fm=FM, fc=FC, phase_error_deg=0.0,
                          lpf_cutoff=1.5 * FM, lpf_transition=200)
    tb.run()

    msg_data = np.array(tb.sink_msg.data())
    mod_data = np.array(tb.sink_mod.data())
    demod_data = np.array(tb.sink_out.data())

    # Compensar atraso do filtro FIR
    lpf_taps = firdes.low_pass(1, SAMP_RATE, 1.5 * FM, 200)
    fir_delay = len(lpf_taps) // 2

    # Normalizar para comparacao
    # A saida teorica e (1/2)cos(2pi fm t) -> amplitude 0.5
    # Alinhar no tempo e normalizar
    demod_aligned = demod_data[fir_delay:]
    msg_aligned = msg_data[:len(demod_aligned)]

    # Medir amplitude do sinal demodulado (regime permanente)
    steady_start = max(fir_delay, SAMP_RATE // 10)  # apos transiente
    if steady_start < len(demod_data):
        demod_amp = np.max(np.abs(demod_data[steady_start:])) if \
            steady_start < len(demod_data) else 0
    else:
        demod_amp = np.max(np.abs(demod_data))

    # --- Plots ---
    fig, axes = plt.subplots(3, 1, figsize=(15, 10))

    n_pts = int(10 * SAMP_RATE / 1000)  # 10 ms
    t = np.arange(n_pts) / SAMP_RATE * 1000

    # Mensagem original
    axes[0].plot(t, msg_data[:n_pts], linewidth=0.8, color='#1f77b4',
                 label='Mensagem original')
    axes[0].set_ylabel('Amplitude')
    axes[0].set_title('Mensagem original: cos(2pi fm t)')
    axes[0].legend(fontsize=8)

    # Sinal DSB-SC
    axes[1].plot(t, mod_data[:n_pts], linewidth=0.8, color='#d62728',
                 label='DSB-SC')
    axes[1].set_ylabel('Amplitude')
    axes[1].set_title('Sinal DSB-SC modulado')
    axes[1].legend(fontsize=8)

    # Sinal demodulado vs original (escalado)
    t_demod = np.arange(n_pts) / SAMP_RATE * 1000
    axes[2].plot(t_demod, msg_data[:n_pts] * 0.5, linewidth=0.8,
                 color='#1f77b4', alpha=0.5, label='Mensagem (x0.5)')
    if fir_delay < n_pts:
        n_show = min(n_pts, len(demod_data))
        t_d = np.arange(n_show) / SAMP_RATE * 1000
        axes[2].plot(t_d, demod_data[:n_show], linewidth=0.8,
                     color='#2ca02c', label='Demodulado')
    axes[2].set_xlabel('Tempo (ms)')
    axes[2].set_ylabel('Amplitude')
    axes[2].set_title('Sinal demodulado (apos LPF)')
    axes[2].legend(fontsize=8)

    fig.suptitle("Etapa 3: Demodulacao Coerente DSB-SC",
                 fontsize=13, fontweight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, "etapa3_demodulacao.png"),
                dpi=150, bbox_inches='tight')
    plt.close()

    log(f"  Atraso do filtro FIR: {fir_delay} amostras "
        f"({fir_delay / SAMP_RATE * 1000:.2f} ms)")
    log(f"  Amplitude demodulada (regime permanente): {demod_amp:.4f}")
    log(f"  Amplitude teorica: 0.5000 (identidade trigonometrica)")
    log(f"  -> etapa3_demodulacao.png")
    log(f"\n  Resposta Q5: A amplitude de saida e metade da original.")
    log(f"  cos(2pi fm t) * cos(2pi fc t) * cos(2pi fc t)")
    log(f"  = cos(2pi fm t) * (1/2)[1 + cos(2pi 2fc t)]")
    log(f"  = (1/2)cos(2pi fm t) + (1/2)cos(2pi fm t)cos(2pi 2fc t)")
    log(f"  Apos LPF: (1/2)cos(2pi fm t)")


# =====================================================================
# ETAPA 4: Erro de fase na demodulacao
# =====================================================================
def etapa4():
    log("\n" + "=" * 65)
    log("ETAPA 4: Erro de fase na demodulacao")
    log("=" * 65)

    phase_errors = [0, 15, 30, 45, 60, 90]
    fig, axes = plt.subplots(2, 3, figsize=(17, 9))
    csv_rows = []

    log(f"\n  {'Fase (graus)':>14} | {'Amp. medida':>12} | "
        f"{'Amp. teorica':>13} | {'cos(phi)':>10} | {'Erro (%)':>10}")
    log(f"  {'-'*14}-+-{'-'*12}-+-{'-'*13}-+-{'-'*10}-+-{'-'*10}")

    for ax, phase_deg in zip(axes.flat, phase_errors):
        tb = DSBSCDemodulator(fm=FM, fc=FC, phase_error_deg=phase_deg,
                              lpf_cutoff=1.5 * FM, lpf_transition=200)
        tb.run()

        msg_data = np.array(tb.sink_msg.data())
        demod_data = np.array(tb.sink_out.data())

        # Medir amplitude em regime permanente
        lpf_taps = firdes.low_pass(1, SAMP_RATE, 1.5 * FM, 200)
        fir_delay = len(lpf_taps) // 2
        steady_start = max(fir_delay + SAMP_RATE // 10,
                           len(demod_data) // 4)
        if steady_start < len(demod_data):
            measured_amp = np.max(np.abs(demod_data[steady_start:]))
        else:
            measured_amp = np.max(np.abs(demod_data))

        # Valor teorico: (1/2) * cos(phase_error)
        theoretical_amp = 0.5 * np.cos(np.deg2rad(phase_deg))
        cos_phi = np.cos(np.deg2rad(phase_deg))

        if theoretical_amp > 0.01:
            error_pct = abs(measured_amp - theoretical_amp) / \
                theoretical_amp * 100
        else:
            error_pct = measured_amp * 100  # deve ser proximo de 0

        log(f"  {phase_deg:>14} | {measured_amp:>12.4f} | "
            f"{theoretical_amp:>13.4f} | {cos_phi:>10.4f} | "
            f"{error_pct:>10.2f}")
        csv_rows.append([phase_deg, f"{measured_amp:.4f}",
                         f"{theoretical_amp:.4f}", f"{cos_phi:.4f}",
                         f"{error_pct:.2f}"])

        # Plot
        n_pts = int(10 * SAMP_RATE / 1000)
        t = np.arange(n_pts) / SAMP_RATE * 1000

        ax.plot(t, msg_data[:n_pts] * 0.5, linewidth=0.8,
                color='#1f77b4', alpha=0.4, label='Ref (x0.5)')
        n_show = min(n_pts, len(demod_data))
        ax.plot(np.arange(n_show) / SAMP_RATE * 1000,
                demod_data[:n_show], linewidth=0.8,
                color='#2ca02c', label='Demodulado')
        ax.set_title(f'phi = {phase_deg} graus (cos={cos_phi:.2f})')
        ax.set_xlabel('Tempo (ms)')
        ax.set_ylabel('Amplitude')
        ax.set_ylim([-0.7, 0.7])
        ax.legend(fontsize=7)

    plt.suptitle("Etapa 4: Erro de Fase na Demodulacao DSB-SC",
                 fontsize=13, fontweight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, "etapa4_erro_fase.png"),
                dpi=150, bbox_inches='tight')
    plt.close()

    save_csv("etapa4_fase_vs_amplitude.csv",
             ["fase_graus", "amp_medida", "amp_teorica", "cos_phi",
              "erro_pct"],
             csv_rows)

    log(f"\n  -> etapa4_erro_fase.png")
    log(f"  -> dados/etapa4_fase_vs_amplitude.csv")
    log(f"\n  Resposta Q3: O erro de fase causa atenuacao por cos(phi).")
    log(f"  A 90 graus, cos(90) = 0: nulo de quadratura (sinal zerado).")
    log(f"  Isso demonstra a necessidade de sincronismo de fase no")
    log(f"  receptor para demodulacao coerente DSB-SC.")


# =====================================================================
# ETAPA 5: Efeito do corte do LPF
# =====================================================================
def etapa5():
    log("\n" + "=" * 65)
    log("ETAPA 5: Efeito do corte do filtro passa-baixa")
    log("=" * 65)

    cutoff_factors = [0.5, 1.0, 1.5, 2.0, 3.0]
    n_plots = len(cutoff_factors)
    fig, axes = plt.subplots(n_plots, 1, figsize=(15, 3.5 * n_plots))
    csv_rows = []

    log(f"\n  {'Corte':>10} | {'fc_lpf (Hz)':>12} | {'Amp. saida':>12} | "
        f"{'Qualidade':>12}")
    log(f"  {'-'*10}-+-{'-'*12}-+-{'-'*12}-+-{'-'*12}")

    for ax, factor in zip(axes, cutoff_factors):
        cutoff = factor * FM

        tb = DSBSCDemodulator(fm=FM, fc=FC, phase_error_deg=0.0,
                              lpf_cutoff=cutoff, lpf_transition=200)
        tb.run()

        msg_data = np.array(tb.sink_msg.data())
        demod_data = np.array(tb.sink_out.data())

        # Medir amplitude e distorcao
        lpf_taps = firdes.low_pass(1, SAMP_RATE, cutoff, 200)
        fir_delay = len(lpf_taps) // 2
        steady_start = max(fir_delay + SAMP_RATE // 10,
                           len(demod_data) // 4)
        if steady_start < len(demod_data):
            measured_amp = np.max(np.abs(demod_data[steady_start:]))
        else:
            measured_amp = np.max(np.abs(demod_data))

        # Classificar qualidade
        if cutoff < FM:
            quality = "Atenuado"
        elif cutoff < 1.2 * FM:
            quality = "Limiar"
        else:
            quality = "Bom"

        log(f"  {factor:>8.1f}xfm | {cutoff:>12.0f} | "
            f"{measured_amp:>12.4f} | {quality:>12}")
        csv_rows.append([f"{factor}xfm", cutoff, f"{measured_amp:.4f}",
                         quality])

        # Plot
        n_pts = int(10 * SAMP_RATE / 1000)
        t = np.arange(n_pts) / SAMP_RATE * 1000

        ax.plot(t, msg_data[:n_pts] * 0.5, linewidth=0.8,
                color='#1f77b4', alpha=0.4, label='Ref (x0.5)')
        n_show = min(n_pts, len(demod_data))
        ax.plot(np.arange(n_show) / SAMP_RATE * 1000,
                demod_data[:n_show], linewidth=0.8,
                color='#2ca02c', label='Demodulado')
        ax.set_title(f'LPF cutoff = {factor}xfm = {cutoff:.0f} Hz '
                     f'({quality})')
        ax.set_xlabel('Tempo (ms)')
        ax.set_ylabel('Amplitude')
        ax.set_ylim([-0.7, 0.7])
        ax.legend(fontsize=7)

    plt.suptitle("Etapa 5: Efeito do Corte do Filtro Passa-Baixa",
                 fontsize=13, fontweight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, "etapa5_lpf_cutoff.png"),
                dpi=150, bbox_inches='tight')
    plt.close()

    save_csv("etapa5_lpf_cutoff.csv",
             ["fator_corte", "cutoff_Hz", "amp_saida", "qualidade"],
             csv_rows)

    log(f"\n  -> etapa5_lpf_cutoff.png")
    log(f"  -> dados/etapa5_lpf_cutoff.csv")
    log(f"\n  Resposta Q4: O corte do LPF deve ser > fm para passar")
    log(f"  a mensagem, mas < 2fc - fm para rejeitar o termo de")
    log(f"  frequencia dupla (em torno de 2fc).")
    log(f"  Com corte < fm, a mensagem e atenuada/distorcida.")
    log(f"  Com corte muito alto, componentes de alta frequencia")
    log(f"  (produto da multiplicacao) vazam para a saida.")


# =====================================================================
# MAIN
# =====================================================================
if __name__ == '__main__':
    log("=" * 65)
    log("PRATICA 02 -- MODULACAO AM DSB-SC")
    log("GABARITO DO PROFESSOR")
    log(f"Data: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    log(f"GNU Radio: {gr.version()}")
    log(f"Sample Rate: {SAMP_RATE} Hz | Amostras: {N_SAMPLES}")
    log(f"Portadora: fc = {FC} Hz | Mensagem: fm = {FM} Hz")
    log(f"Saida: {BASE_DIR}")
    log("=" * 65)

    etapa1()
    etapa2()
    etapa3()
    etapa4()
    etapa5()

    log("\n" + "=" * 65)
    log("GABARITO COMPLETO GERADO COM SUCESSO")
    log("=" * 65)

    # Salvar relatorio em texto
    report_path = os.path.join(BASE_DIR, "relatorio.txt")
    with open(report_path, 'w') as f:
        f.write('\n'.join(relatorio))
    print(f"\nRelatorio salvo em: {report_path}")
