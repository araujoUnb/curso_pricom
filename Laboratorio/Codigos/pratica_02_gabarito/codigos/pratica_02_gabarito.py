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

Correspondencia com o enunciado:
  script etapa1 -> enunciado Etapa 1 (modulador DSB-SC)
  script etapa2 -> enunciado Etapa 2 (variacao de fm)
  script etapa3 -> enunciado Etapa 3, parte 1 (demodulacao coerente)
  script etapa4 -> enunciado Etapa 3, parte 2 (erro de fase)
  script etapa5 -> enunciado Etapa 4 (ajuste do LPF)

O oscilador local e construido como
    cos(2*pi*fc*t + theta) = cos(theta)*cos(2*pi*fc*t) - sin(theta)*sin(2*pi*fc*t)
que e exatamente a estrutura do flowgraph .grc entregue aos alunos.
Essa forma preserva a coerencia com a portadora de transmissao quando
theta e alterado em tempo de execucao, o que nao ocorre se o erro de
fase for aplicado no campo Phase Offset do bloco Signal Source.

Execucao:
    /usr/bin/python3 pratica_02_gabarito.py

Saida:
    ../figuras/          -- PNGs de referencia
    ../dados/            -- CSVs com dados brutos
    ../relatorio.txt     -- Relatorio completo
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
# CONFIGURACAO (identica a do enunciado e do flowgraph .grc)
# =====================================================================
SAMP_RATE = 48000
FC = 5000           # Frequencia da portadora (Hz)
FM = 1000           # Frequencia da mensagem (Hz)
AMP_C = 1.0         # Amplitude da portadora
AMP_M = 1.0         # Amplitude da mensagem
N_SAMPLES = 48000   # 1 segundo de dados

LPF_CUTOFF = 1.5 * FM   # Corte nominal do LPF de demodulacao (Hz)
LPF_WIDTH = 300         # Largura de transicao do LPF (Hz)

# Valores varridos em cada etapa (espelham as tabelas do enunciado)
FM_SWEEP = [500, 1000, 2000, 4000]
PHASE_SWEEP = [0, 15, 30, 45, 60, 90]
CUTOFF_SWEEP = [500, 1500, 3000, 9500, 12000]

# 7680 pontos dao df = 6,25 Hz: todas as frequencias de interesse
# (multiplos de 500 Hz) caem exatamente sobre um bin, o que elimina a
# perda de scalloping da janela e permite ler a amplitude diretamente.
FFT_SIZE = 7680

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
    """Flowgraph: DSB-SC -> oscilador local com erro de fase -> LPF.

    O oscilador local usa a decomposicao em quadratura
    cos(w t + theta) = cos(theta) cos(w t) - sin(theta) sin(w t),
    de modo que theta e um ganho e nao a fase inicial de um NCO.
    """

    def __init__(self, fm=FM, fc=FC, phase_error_deg=0.0,
                 lpf_cutoff=None, lpf_transition=LPF_WIDTH,
                 n_samples=N_SAMPLES):
        gr.top_block.__init__(self, "DSB-SC Demodulator")

        if lpf_cutoff is None:
            lpf_cutoff = LPF_CUTOFF

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

        # Oscilador local em quadratura, sempre coerente com carrier_tx
        self.lo_cos = analog.sig_source_f(
            SAMP_RATE, analog.GR_COS_WAVE, fc, 1.0, 0)
        self.lo_sin = analog.sig_source_f(
            SAMP_RATE, analog.GR_SIN_WAVE, fc, 1.0, 0)
        self.gain_i = blocks.multiply_const_ff(float(np.cos(phase_rad)))
        self.gain_q = blocks.multiply_const_ff(float(-np.sin(phase_rad)))
        self.lo_sum = blocks.add_ff()
        self.connect(self.lo_cos, self.gain_i, (self.lo_sum, 0))
        self.connect(self.lo_sin, self.gain_q, (self.lo_sum, 1))

        # Demodulador: multiplicar pelo oscilador local
        self.demod_mult = blocks.multiply_ff()
        self.connect(self.mod_mult, (self.demod_mult, 0))
        self.connect(self.lo_sum, (self.demod_mult, 1))

        # Filtro passa-baixa
        self.lpf_taps = firdes.low_pass(1, SAMP_RATE, lpf_cutoff,
                                        lpf_transition)
        self.fir_delay = (len(self.lpf_taps) - 1) // 2
        self.lpf = filter.fir_filter_fff(1, self.lpf_taps)
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

    def run_and_collect(self):
        """Executa e devolve (mensagem, dsbsc, demodulado)."""
        self.run()
        return (np.array(self.sink_msg.data()),
                np.array(self.sink_mod.data()),
                np.array(self.sink_out.data()))


# =====================================================================
# FUNCOES DE ANALISE
# =====================================================================
def spectrum(data, fft_size=FFT_SIZE, start=0):
    """Retorna (freqs_hz, magnitude_dB) com janela Hann.

    A magnitude e compensada pelo ganho coerente da janela: uma
    senoide de amplitude A aparece com 20*log10(A) dB.
    """
    w = np.hanning(fft_size)
    seg = np.asarray(data[start:start + fft_size], dtype=float)
    if len(seg) < fft_size:
        seg = np.pad(seg, (0, fft_size - len(seg)))
    X = np.fft.rfft(seg * w)
    scale = 2.0 / (fft_size * np.mean(w))
    mag = 20 * np.log10(np.abs(X) * scale + 1e-15)
    freqs = np.fft.rfftfreq(fft_size, 1.0 / SAMP_RATE)
    return freqs, mag


def find_peak_near(freqs, mag, target_freq, margin=100):
    """Encontra pico espectral proximo a target_freq."""
    mask = np.abs(freqs - target_freq) < margin
    if not np.any(mask):
        return target_freq, -200.0
    idx = np.where(mask)[0]
    best = idx[np.argmax(mag[idx])]
    return freqs[best], mag[best]


def amp_at(data, freq, start=0, fft_size=FFT_SIZE):
    """Amplitude linear da componente em freq, em regime permanente."""
    freqs, mag = spectrum(data, fft_size=fft_size, start=start)
    _, peak_db = find_peak_near(freqs, mag, freq, margin=60)
    return 10 ** (peak_db / 20.0)


def steady_start(fir_delay):
    """Primeira amostra livre do transitorio do FIR."""
    return 2 * fir_delay + SAMP_RATE // 20


def aligned_window(demod, msg, fir_delay, n_pts):
    """Recorta saida e referencia ja compensando o atraso de grupo.

    A amostra demod[n] corresponde a entrada msg[n - fir_delay];
    o recorte devolve os dois vetores sobre o mesmo eixo de tempo,
    depois do transitorio do filtro.
    """
    s = steady_start(fir_delay)
    n = min(n_pts, len(demod) - s, len(msg) - (s - fir_delay))
    if n <= 0:
        return np.array([]), np.array([]), np.array([])
    t = np.arange(n) / SAMP_RATE * 1000.0
    return t, demod[s:s + n], msg[s - fir_delay:s - fir_delay + n]


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
# VERIFICACAO PREVIA: coerencia do oscilador local
# =====================================================================
def verificar_oscilador():
    """Confere que a lei cos(theta) e reproduzida pelo flowgraph."""
    log("\n" + "=" * 65)
    log("VERIFICACAO: coerencia do oscilador local em quadratura")
    log("=" * 65)

    pior = 0.0
    for phase_deg in PHASE_SWEEP:
        tb = DSBSCDemodulator(phase_error_deg=phase_deg)
        _, _, demod = tb.run_and_collect()
        medido = amp_at(demod, FM, start=steady_start(tb.fir_delay))
        teorico = 0.5 * np.cos(np.deg2rad(phase_deg))
        pior = max(pior, abs(medido - teorico))

    log(f"  Maior desvio |medido - 0.5 cos(theta)|: {pior:.5f}")
    if pior < 5e-3:
        log("  OK: oscilador local coerente com a portadora de transmissao.")
    else:
        log("  ATENCAO: desvio acima do esperado, verificar o flowgraph.")
    return pior


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
    axes[1, 0].set_xlim([0, 2 * (FC + FM)])
    axes[1, 0].set_ylim([-120, 10])
    axes[1, 0].axvline(FM, color='r', ls='--', alpha=0.5, label=f'{FM} Hz')
    axes[1, 0].legend(fontsize=8)

    # Espectro - DSB-SC
    freqs_m, mag_m = spectrum(mod_data)
    axes[1, 1].plot(freqs_m, mag_m, linewidth=0.8, color='#d62728')
    axes[1, 1].set_xlabel('Frequencia (Hz)')
    axes[1, 1].set_ylabel('Magnitude (dB)')
    axes[1, 1].set_title('Espectro DSB-SC')
    axes[1, 1].set_xlim([0, 2 * (FC + FM)])
    axes[1, 1].set_ylim([-120, 10])
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
    _, mag_carrier = find_peak_near(freqs_m, mag_m, FC, margin=60)

    log(f"  Banda lateral inferior (fc-fm = {FC - FM} Hz): {mag_lsb:.1f} dB")
    log(f"  Banda lateral superior (fc+fm = {FC + FM} Hz): {mag_usb:.1f} dB")
    log(f"  Amplitude de cada banda lateral: {10 ** (mag_lsb / 20):.4f} "
        f"(teorico Am/2 = {AMP_M / 2:.4f})")
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

    fig, axes = plt.subplots(2, 2, figsize=(15, 9))
    csv_rows = []

    log(f"\n  {'fm (Hz)':>8} | {'LSB teor.':>10} | {'LSB med.':>10} | "
        f"{'USB teor.':>10} | {'USB med.':>10} | {'LSB (dB)':>9} | "
        f"{'USB (dB)':>9}")
    log(f"  {'-'*8}-+-{'-'*10}-+-{'-'*10}-+-{'-'*10}-+-{'-'*10}-+-"
        f"{'-'*9}-+-{'-'*9}")

    for ax, fm in zip(axes.flat, FM_SWEEP):
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
        ax.axvline(FC, color='gray', ls=':', alpha=0.4, label=f'fc={FC}')
        ax.set_title(f'fm = {fm} Hz')
        ax.set_xlabel('Frequencia (Hz)')
        ax.set_ylabel('dB')
        ax.set_xlim([0, min(FC + max(FM_SWEEP) + 2000, SAMP_RATE / 2)])
        ax.set_ylim([-120, 10])
        ax.legend(fontsize=7)

        log(f"  {fm:>8} | {FC - fm:>10} | {lsb_freq:>10.0f} | "
            f"{FC + fm:>10} | {usb_freq:>10.0f} | {lsb_mag:>9.1f} | "
            f"{usb_mag:>9.1f}")
        csv_rows.append([fm, FC - fm, f"{lsb_freq:.0f}", FC + fm,
                         f"{usb_freq:.0f}", f"{lsb_mag:.1f}",
                         f"{usb_mag:.1f}"])

    plt.suptitle("Etapa 2: Variacao da Frequencia da Mensagem",
                 fontsize=13, fontweight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, "etapa2_variacao_fm.png"),
                dpi=150, bbox_inches='tight')
    plt.close()

    save_csv("etapa2_bandas_laterais.csv",
             ["fm_Hz", "LSB_teorica_Hz", "LSB_medida_Hz",
              "USB_teorica_Hz", "USB_medida_Hz", "LSB_dB", "USB_dB"],
             csv_rows)

    log(f"\n  Resolucao da FFT: {SAMP_RATE / FFT_SIZE:.2f} Hz "
        f"(FFT de {FFT_SIZE} pontos)")
    log(f"  -> etapa2_variacao_fm.png")
    log(f"  -> dados/etapa2_bandas_laterais.csv")
    log(f"\n  Resposta Q2: As bandas laterais aparecem em fc +/- fm.")
    log(f"  Ao aumentar fm, as bandas se afastam simetricamente de fc.")
    log(f"  A largura de banda do sinal DSB-SC e 2*fm.")
    log(f"  Quando fm -> fc a banda inferior chega a 0 Hz; para fm > fc")
    log(f"  ela se dobra sobre o eixo e as duas bandas se cruzam.")


# =====================================================================
# ETAPA 3: Demodulacao coerente
# =====================================================================
def etapa3():
    log("\n" + "=" * 65)
    log("ETAPA 3: Demodulacao coerente")
    log("=" * 65)

    tb = DSBSCDemodulator(fm=FM, fc=FC, phase_error_deg=0.0)
    msg_data, mod_data, demod_data = tb.run_and_collect()
    fir_delay = tb.fir_delay
    s0 = steady_start(fir_delay)

    demod_amp = amp_at(demod_data, FM, start=s0)

    # --- Plots ---
    fig, axes = plt.subplots(3, 1, figsize=(15, 10))

    n_pts = int(5 * SAMP_RATE / 1000)  # 5 ms
    t = np.arange(n_pts) / SAMP_RATE * 1000

    # Mensagem original
    axes[0].plot(t, msg_data[:n_pts], linewidth=0.9, color='#1f77b4',
                 label='Mensagem original')
    axes[0].set_ylabel('Amplitude')
    axes[0].set_title('Mensagem original: cos(2pi fm t)')
    axes[0].legend(fontsize=8)

    # Sinal DSB-SC
    axes[1].plot(t, mod_data[:n_pts], linewidth=0.9, color='#d62728',
                 label='DSB-SC')
    axes[1].set_ylabel('Amplitude')
    axes[1].set_title('Sinal DSB-SC modulado')
    axes[1].legend(fontsize=8)

    # Sinal demodulado vs original, ja alinhados pelo atraso do FIR
    td, dem_w, msg_w = aligned_window(demod_data, msg_data, fir_delay, n_pts)
    axes[2].plot(td, msg_w * 0.5, linewidth=1.4, color='#1f77b4',
                 alpha=0.45, label='Mensagem x 0.5 (referencia)')
    axes[2].plot(td, dem_w, linewidth=0.9, color='#2ca02c',
                 label='Demodulado (LPF)')
    axes[2].set_xlabel('Tempo (ms) apos o transitorio do filtro')
    axes[2].set_ylabel('Amplitude')
    axes[2].set_title(f'Sinal demodulado, corte do LPF = {LPF_CUTOFF:.0f} Hz, '
                      f'atraso de grupo compensado ({fir_delay} amostras)')
    axes[2].legend(fontsize=8)

    fig.suptitle("Etapa 3: Demodulacao Coerente DSB-SC",
                 fontsize=13, fontweight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, "etapa3_demodulacao.png"),
                dpi=150, bbox_inches='tight')
    plt.close()

    erro_max = float(np.max(np.abs(dem_w - 0.5 * msg_w))) if len(dem_w) else 0.0

    log(f"  Atraso do filtro FIR: {fir_delay} amostras "
        f"({fir_delay / SAMP_RATE * 1000:.2f} ms)")
    log(f"  Amplitude demodulada (regime permanente): {demod_amp:.4f}")
    log(f"  Amplitude teorica: 0.5000 (identidade trigonometrica)")
    log(f"  Erro maximo ponto a ponto apos alinhamento: {erro_max:.5f}")
    log(f"  -> etapa3_demodulacao.png")
    log(f"\n  Resposta Q5: A amplitude de saida e metade da original.")
    log(f"  cos(2pi fm t) * cos(2pi fc t) * cos(2pi fc t)")
    log(f"  = cos(2pi fm t) * (1/2)[1 + cos(2pi 2fc t)]")
    log(f"  = (1/2)cos(2pi fm t) + (1/2)cos(2pi fm t)cos(2pi 2fc t)")
    log(f"  Apos LPF: (1/2)cos(2pi fm t)")
    log(f"  O unico efeito adicional e o atraso de grupo do filtro FIR,")
    log(f"  constante e igual a (N-1)/2 amostras; nao e distorcao.")


# =====================================================================
# ETAPA 4: Erro de fase na demodulacao
# =====================================================================
def etapa4():
    log("\n" + "=" * 65)
    log("ETAPA 4: Erro de fase na demodulacao")
    log("=" * 65)

    fig, axes = plt.subplots(2, 3, figsize=(17, 9))
    csv_rows = []

    log(f"\n  {'Fase (graus)':>14} | {'Amp. medida':>12} | "
        f"{'Amp. teorica':>13} | {'cos(phi)':>10} | {'Erro (%)':>10}")
    log(f"  {'-'*14}-+-{'-'*12}-+-{'-'*13}-+-{'-'*10}-+-{'-'*10}")

    for ax, phase_deg in zip(axes.flat, PHASE_SWEEP):
        tb = DSBSCDemodulator(fm=FM, fc=FC, phase_error_deg=phase_deg)
        msg_data, _, demod_data = tb.run_and_collect()
        fir_delay = tb.fir_delay

        measured_amp = amp_at(demod_data, FM, start=steady_start(fir_delay))

        # Valor teorico: (1/2) * cos(phase_error)
        theoretical_amp = 0.5 * np.cos(np.deg2rad(phase_deg))
        cos_phi = np.cos(np.deg2rad(phase_deg))

        if theoretical_amp > 0.01:
            error_pct = abs(measured_amp - theoretical_amp) / \
                theoretical_amp * 100
            error_txt = f"{error_pct:.2f}"
        else:
            # Em 90 graus o valor teorico e zero: reporta a atenuacao em dB
            atten_db = 20 * np.log10(measured_amp / 0.5 + 1e-15)
            error_txt = f"{atten_db:.1f} dB"

        log(f"  {phase_deg:>14} | {measured_amp:>12.4f} | "
            f"{theoretical_amp:>13.4f} | {cos_phi:>10.4f} | "
            f"{error_txt:>10}")
        csv_rows.append([phase_deg, f"{measured_amp:.4f}",
                         f"{theoretical_amp:.4f}", f"{cos_phi:.4f}",
                         error_txt])

        # Plot alinhado e sem transitorio
        n_pts = int(5 * SAMP_RATE / 1000)
        td, dem_w, msg_w = aligned_window(demod_data, msg_data,
                                          fir_delay, n_pts)
        ax.plot(td, msg_w * 0.5, linewidth=1.4, color='#1f77b4',
                alpha=0.35, label='Ref x0.5')
        ax.plot(td, dem_w, linewidth=0.9, color='#2ca02c',
                label='Demodulado')
        ax.axhline(theoretical_amp, color='#d62728', ls='--', lw=0.8,
                   alpha=0.7, label='0.5 cos(phi)')
        ax.axhline(-theoretical_amp, color='#d62728', ls='--', lw=0.8,
                   alpha=0.7)
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
              "erro"],
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

    f_img_low = 2 * FC - FM   # termo de frequencia dupla, lado inferior
    f_img_high = 2 * FC + FM  # termo de frequencia dupla, lado superior

    n_plots = len(CUTOFF_SWEEP)
    fig, axes = plt.subplots(n_plots, 2, figsize=(15, 3.1 * n_plots))
    csv_rows = []

    log(f"\n  Termo de frequencia dupla em 2fc -/+ fm = "
        f"{f_img_low} e {f_img_high} Hz")
    log(f"  Faixa util do corte: fm = {FM} Hz  <  fcorte  <  "
        f"2fc - fm = {f_img_low} Hz\n")
    log(f"  {'fcorte (Hz)':>12} | {'Amp. em fm':>11} | "
        f"{'Residuo 2fc':>12} | {'Qualidade':>26}")
    log(f"  {'-'*12}-+-{'-'*11}-+-{'-'*12}-+-{'-'*26}")

    for row, cutoff in zip(axes, CUTOFF_SWEEP):
        ax_t, ax_f = row

        tb = DSBSCDemodulator(fm=FM, fc=FC, phase_error_deg=0.0,
                              lpf_cutoff=cutoff)
        msg_data, _, demod_data = tb.run_and_collect()
        fir_delay = tb.fir_delay
        s0 = steady_start(fir_delay)

        amp_msg = amp_at(demod_data, FM, start=s0)
        amp_img = max(amp_at(demod_data, f_img_low, start=s0),
                      amp_at(demod_data, f_img_high, start=s0))

        # Classificacao a partir da medida, nao de uma regra fixa
        if amp_msg < 0.4 * 0.5:
            quality = "Mensagem atenuada"
        elif amp_img > 0.05 * 0.5:
            quality = "Vazamento do termo em 2fc"
        elif amp_msg < 0.9 * 0.5:
            quality = "Limiar"
        else:
            quality = "Recuperacao fiel"

        log(f"  {cutoff:>12} | {amp_msg:>11.4f} | {amp_img:>12.4f} | "
            f"{quality:>26}")
        csv_rows.append([cutoff, f"{amp_msg:.4f}", f"{amp_img:.4f}",
                         quality])

        # Painel de tempo, alinhado e sem transitorio
        n_pts = int(5 * SAMP_RATE / 1000)
        td, dem_w, msg_w = aligned_window(demod_data, msg_data,
                                          fir_delay, n_pts)
        ax_t.plot(td, msg_w * 0.5, linewidth=1.4, color='#1f77b4',
                  alpha=0.35, label='Ref x0.5')
        ax_t.plot(td, dem_w, linewidth=0.9, color='#2ca02c',
                  label='Demodulado')
        ax_t.set_title(f'fcorte = {cutoff} Hz -- {quality}')
        ax_t.set_xlabel('Tempo (ms)')
        ax_t.set_ylabel('Amplitude')
        ax_t.set_ylim([-0.8, 0.8])
        ax_t.legend(fontsize=7)

        # Painel de espectro da saida
        freqs, mag = spectrum(demod_data, start=s0)
        ax_f.plot(freqs, mag, linewidth=0.8, color='#7f7f7f')
        ax_f.axvline(FM, color='#2ca02c', ls='--', alpha=0.7,
                     label=f'fm = {FM} Hz')
        ax_f.axvline(f_img_low, color='#d62728', ls='--', alpha=0.7,
                     label=f'2fc-fm = {f_img_low} Hz')
        ax_f.axvline(f_img_high, color='#ff7f0e', ls='--', alpha=0.7,
                     label=f'2fc+fm = {f_img_high} Hz')
        ax_f.axvline(cutoff, color='k', ls=':', alpha=0.8,
                     label='fcorte')
        ax_f.set_xlim([0, 2 * FC + 3000])
        ax_f.set_ylim([-120, 10])
        ax_f.set_xlabel('Frequencia (Hz)')
        ax_f.set_ylabel('dB')
        ax_f.set_title('Espectro da saida do LPF')
        ax_f.legend(fontsize=6)

    plt.suptitle("Etapa 5: Efeito do Corte do Filtro Passa-Baixa",
                 fontsize=13, fontweight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, "etapa5_lpf_cutoff.png"),
                dpi=150, bbox_inches='tight')
    plt.close()

    save_csv("etapa5_lpf_cutoff.csv",
             ["cutoff_Hz", "amp_em_fm", "residuo_2fc", "qualidade"],
             csv_rows)

    log(f"\n  -> etapa5_lpf_cutoff.png")
    log(f"  -> dados/etapa5_lpf_cutoff.csv")
    log(f"\n  Resposta Q4: a frequencia de corte deve satisfazer")
    log(f"  fm < fcorte < 2fc - fm, ou seja {FM} < fcorte < {f_img_low} Hz.")
    log(f"  Com fcorte < fm a propria mensagem e atenuada.")
    log(f"  Com fcorte > 2fc - fm o termo de frequencia dupla gerado pela")
    log(f"  multiplicacao passa pelo filtro e distorce a saida.")
    log(f"  A largura de transicao define quanta atenuacao sobra para esse")
    log(f"  termo quando o corte se aproxima de 2fc - fm.")


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
    log(f"LPF nominal: corte = {LPF_CUTOFF:.0f} Hz | "
        f"transicao = {LPF_WIDTH} Hz")
    log(f"Saida: {BASE_DIR}")
    log("=" * 65)

    verificar_oscilador()
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
