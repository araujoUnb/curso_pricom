#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Prática 07 – Phase-Locked Loop (PLL): Gabarito do Professor
=============================================================
Executa o flowgraph da Prática 07 em modo headless (sem GUI),
reproduzindo todas as etapas do enunciado e gerando:

  1. Figuras PNG de referência para cada cenário
  2. Dados numéricos (CSV) de cada medição
  3. Relatório resumo em texto

Execução:
    /usr/bin/python3 pratica_07_gabarito.py

Saída:
    ./pratica_07_gabarito/
        figuras/          — PNGs de referência
        dados/            — CSVs com dados brutos
        relatorio.txt     — Relatório completo
"""

import os
import sys
import csv
import numpy as np
from datetime import datetime

try:
    from gnuradio import gr, analog, blocks
except ImportError:
    print("ERRO: GNU Radio não encontrado.")
    print("Execute com: /usr/bin/python3 pratica_07_gabarito.py")
    sys.exit(1)

try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
except ImportError:
    print("ERRO: matplotlib não encontrado.")
    sys.exit(1)

# =====================================================================
# CONFIGURAÇÃO
# =====================================================================
SAMP_RATE = 32000
N_SAMPLES = 32000  # 1 segundo de dados

MAX_FREQ = 2 * np.pi * 2000 / SAMP_RATE
MIN_FREQ = -MAX_FREQ

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIG_DIR = os.path.join(BASE_DIR, "figuras")
DATA_DIR = os.path.join(BASE_DIR, "dados")

for d in [BASE_DIR, FIG_DIR, DATA_DIR]:
    os.makedirs(d, exist_ok=True)

# Acumula linhas do relatório
relatorio = []

# Tabelas do enunciado preenchidas com valores medidos
tabelas_enunciado = {
    "lock": [],      # [f_in, valor_regime, locked]
    "pll": [],       # [loop_bw, t_conv_ms, overshoot_pct, std_pos_lock]
    "capture": [],   # [f_in, valor_regime, locked]
    "capture_meta": {},  # {df_cap_med, df_cap_teo}
    "ruido": [],     # [noise_amp, jitter_062, jitter_200]
    "jitter_hz": [],     # [noise_amp, jitter_hz_062, jitter_hz_200]
    "saturacao": [],     # [f_in, f_est, desvio, locked]
    "janela_curta": [],  # [f_in, f_est, locked]
    "janela_curta_meta": {},  # {df_cap_med_curto, df_cap_teo}
    "bias_curto": [],    # [noise_amp, f_est_062, f_est_200]
}


def log(msg=""):
    """Imprime e acumula no relatório."""
    print(msg)
    relatorio.append(msg)


def is_locked(data, threshold_rel=0.02):
    """Critério numérico de lock: std no regime permanente <
    threshold_rel * |mean| (saída estável proporcional a f_in)."""
    tail = data[int(0.8 * len(data)):]
    mean = np.mean(tail)
    std = np.std(tail)
    if abs(mean) < 1e-6:
        return std < 1e-4
    return std / abs(mean) < threshold_rel


# =====================================================================
# FLOWGRAPH HEADLESS — PLL
# =====================================================================
class PLLTest(gr.top_block):
    """Flowgraph: Signal Source (complex) -> [+ noise] -> PLL Freq Det -> sink"""

    def __init__(self, freq, loop_bw, noise_amp=0, n_samples=N_SAMPLES):
        gr.top_block.__init__(self, "Pratica06_PLL")

        self.src = analog.sig_source_c(
            SAMP_RATE, analog.GR_COS_WAVE, freq, 1.0, 0)
        self.pll = analog.pll_freqdet_cf(loop_bw, MAX_FREQ, MIN_FREQ)
        self.head = blocks.head(gr.sizeof_float, n_samples)
        self.sink = blocks.vector_sink_f()

        if noise_amp > 0:
            self.noise = analog.noise_source_c(
                analog.GR_GAUSSIAN, noise_amp)
            self.add = blocks.add_cc()
            self.connect(self.src, (self.add, 0))
            self.connect(self.noise, (self.add, 1))
            self.connect(self.add, self.pll, self.head, self.sink)
        else:
            self.connect(self.src, self.pll, self.head, self.sink)


def capture_pll(freq, loop_bw, noise_amp=0, n_samples=N_SAMPLES):
    """Captura a saída do PLL Freq Det e retorna numpy array."""
    tb = PLLTest(freq, loop_bw, noise_amp, n_samples)
    tb.run()
    return np.array(tb.sink.data())


# =====================================================================
# FUNÇÕES AUXILIARES
# =====================================================================
def save_csv(filename, header, rows):
    """Salva dados em CSV."""
    path = os.path.join(DATA_DIR, filename)
    with open(path, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)
    return path


def measure_convergence(data, threshold_pct=0.02):
    """Mede o tempo de convergência (índice da amostra onde a saída
    se estabiliza dentro de threshold_pct do valor final)."""
    if len(data) < 100:
        return len(data)
    # Valor final: média das últimas 10% amostras
    tail = data[int(0.9 * len(data)):]
    final_val = np.mean(tail)
    if abs(final_val) < 1e-12:
        return 0
    # Encontrar primeira amostra que fica dentro do threshold
    margin = abs(final_val) * threshold_pct
    within = np.abs(data - final_val) < margin
    # Precisa ficar dentro por pelo menos 100 amostras consecutivas
    for i in range(len(within) - 100):
        if np.all(within[i:i + 100]):
            return i
    return len(data)


def measure_overshoot(data):
    """Mede overshoot como percentual do valor final."""
    if len(data) < 100:
        return 0.0
    tail = data[int(0.9 * len(data)):]
    final_val = np.mean(tail)
    if abs(final_val) < 1e-12:
        return 0.0
    peak = np.max(np.abs(data))
    overshoot = (peak - abs(final_val)) / abs(final_val) * 100
    return max(0, overshoot)


def measure_residual_noise(data):
    """Mede ruído residual (desvio padrão) no regime permanente."""
    tail = data[int(0.8 * len(data)):]
    return np.std(tail)


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
# ETAPA 1: PLL básico com PLL Freq Det
# =====================================================================
def etapa1():
    log("\n" + "=" * 65)
    log("ETAPA 1: PLL básico com PLL Freq Det — Tom 1000 Hz")
    log("=" * 65)

    freq_in = 1000
    loop_bw = 0.062
    data = capture_pll(freq_in, loop_bw)

    t = np.arange(len(data)) / SAMP_RATE * 1000  # ms

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 7))

    # Resposta completa
    ax1.plot(t, data, linewidth=0.8, color='#1f77b4')
    ax1.set_xlabel('Tempo (ms)')
    ax1.set_ylabel('Saída PLL (frequência estimada)')
    ax1.set_title('Resposta completa do PLL Freq Det')
    final_val = np.mean(data[int(0.9 * len(data)):])
    ax1.axhline(final_val, color='r', ls='--', alpha=0.5,
                label=f'Valor final: {final_val:.4f}')
    ax1.legend()

    # Zoom no transitório (primeiros 10 ms)
    n_zoom = int(10 * SAMP_RATE / 1000)
    ax2.plot(t[:n_zoom], data[:n_zoom], linewidth=0.8, color='#d62728')
    ax2.set_xlabel('Tempo (ms)')
    ax2.set_ylabel('Saída PLL (frequência estimada)')
    ax2.set_title('Transitório (primeiros 10 ms)')
    ax2.axhline(final_val, color='r', ls='--', alpha=0.5)

    fig.suptitle(f"Etapa 1: PLL Freq Det — f_in={freq_in} Hz, "
                 f"loop_bw={loop_bw}",
                 fontsize=13, fontweight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, "etapa1_pll_basico.png"),
                dpi=150, bbox_inches='tight')
    plt.close()

    conv_idx = measure_convergence(data)
    conv_time = conv_idx / SAMP_RATE * 1000
    overshoot = measure_overshoot(data)

    log(f"  Frequência de entrada: {freq_in} Hz")
    log(f"  Loop bandwidth: {loop_bw} rad/amostra")
    log(f"  Valor de regime permanente: {final_val:.6f}")
    log(f"  Tempo de convergência: {conv_time:.2f} ms "
        f"(amostra {conv_idx})")
    log(f"  Overshoot: {overshoot:.1f}%")
    log(f"  -> etapa1_pll_basico.png")

    log(f"\n  Resposta Q1: O PLL é composto por três blocos fundamentais:")
    log(f"    - Detector de fase (PD): compara a fase do sinal de entrada")
    log(f"      com a fase do oscilador local, gerando um sinal de erro.")
    log(f"    - Filtro de loop (LF): suaviza o sinal de erro, controlando")
    log(f"      a dinâmica de convergência.")
    log(f"    - VCO (Voltage-Controlled Oscillator): ajusta sua frequência")
    log(f"      com base no sinal de erro filtrado.")
    log(f"    O conjunto forma uma malha de realimentação negativa que")
    log(f"    sincroniza a frequência e fase do VCO com o sinal de entrada.")


# =====================================================================
# ETAPA 2: Observação do processo de lock
# =====================================================================
def etapa2():
    log("\n" + "=" * 65)
    log("ETAPA 2: Processo de lock — Diferentes frequências de entrada")
    log("=" * 65)

    test_freqs = [500, 800, 1000, 1200, 1500]
    loop_bw = 0.062
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 7))
    csv_rows = []

    log(f"\n  {'f_in (Hz)':>10} | {'Valor final':>12} | "
        f"{'Conv (ms)':>10} | {'Overshoot%':>11}")
    log(f"  {'-'*10}-+-{'-'*12}-+-{'-'*10}-+-{'-'*11}")

    for freq, color in zip(test_freqs, colors):
        data = capture_pll(freq, loop_bw)
        t = np.arange(len(data)) / SAMP_RATE * 1000

        final_val = np.mean(data[int(0.9 * len(data)):])
        conv_idx = measure_convergence(data)
        conv_time = conv_idx / SAMP_RATE * 1000
        overshoot = measure_overshoot(data)
        locked = 1 if is_locked(data) else 0

        ax1.plot(t, data, linewidth=0.8, color=color,
                 label=f'{freq} Hz')

        # Zoom nos primeiros 20 ms
        n_zoom = int(20 * SAMP_RATE / 1000)
        ax2.plot(t[:n_zoom], data[:n_zoom], linewidth=0.8,
                 color=color, label=f'{freq} Hz')

        log(f"  {freq:>10} | {final_val:>12.6f} | "
            f"{conv_time:>10.2f} | {overshoot:>11.1f}")
        csv_rows.append([freq, f"{final_val:.6f}",
                         f"{conv_time:.2f}", f"{overshoot:.1f}"])
        f_est = final_val * SAMP_RATE / (2 * np.pi)
        tabelas_enunciado["lock"].append(
            (freq, final_val, f_est, locked))

    ax1.set_xlabel('Tempo (ms)')
    ax1.set_ylabel('Saída PLL')
    ax1.set_title('Resposta completa para diferentes frequências')
    ax1.legend()

    ax2.set_xlabel('Tempo (ms)')
    ax2.set_ylabel('Saída PLL')
    ax2.set_title('Transitório (primeiros 20 ms)')
    ax2.legend()

    fig.suptitle("Etapa 2: Processo de Lock — Overlay de transitórios",
                 fontsize=13, fontweight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, "etapa2_lock_process.png"),
                dpi=150, bbox_inches='tight')
    plt.close()

    save_csv("etapa2_lock_process.csv",
             ["freq_Hz", "valor_final", "conv_ms", "overshoot_pct"],
             csv_rows)

    log(f"\n  -> etapa2_lock_process.png")
    log(f"  -> dados/etapa2_lock_process.csv")

    log(f"\n  Resposta Q2: O lock é detectado quando a saída do PLL")
    log(f"    converge para um valor constante (sem oscilação).")
    log(f"    Visualmente: a curva se torna uma linha plana no regime")
    log(f"    permanente. O valor final é proporcional à frequência")
    log(f"    de entrada.")


# =====================================================================
# ETAPA 3: Efeito da largura de banda do loop
# =====================================================================
def etapa3():
    log("\n" + "=" * 65)
    log("ETAPA 3: Efeito da largura de banda do loop (loop_bw)")
    log("=" * 65)

    loop_bws = [0.01, 0.062, 0.2, 0.5]
    freq_in = 1000
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']

    fig, axes = plt.subplots(2, 2, figsize=(15, 9))
    fig_overlay, ax_ov = plt.subplots(1, 1, figsize=(14, 5))
    csv_rows = []

    log(f"\n  {'loop_bw':>8} | {'Conv (ms)':>10} | "
        f"{'Overshoot%':>11} | {'Ruído res.':>11}")
    log(f"  {'-'*8}-+-{'-'*10}-+-{'-'*11}-+-{'-'*11}")

    for ax, lbw, color in zip(axes.flat, loop_bws, colors):
        data = capture_pll(freq_in, lbw)
        t = np.arange(len(data)) / SAMP_RATE * 1000

        final_val = np.mean(data[int(0.9 * len(data)):])
        conv_idx = measure_convergence(data)
        conv_time = conv_idx / SAMP_RATE * 1000
        overshoot = measure_overshoot(data)
        res_noise = measure_residual_noise(data)

        # Plot individual
        n_zoom = int(50 * SAMP_RATE / 1000)
        ax.plot(t[:n_zoom], data[:n_zoom], linewidth=0.8, color=color)
        ax.axhline(final_val, color='r', ls='--', alpha=0.5)
        ax.set_title(f'loop_bw = {lbw} | conv = {conv_time:.1f} ms | '
                     f'overshoot = {overshoot:.1f}%')
        ax.set_xlabel('Tempo (ms)')
        ax.set_ylabel('Saída PLL')

        # Overlay
        ax_ov.plot(t[:n_zoom], data[:n_zoom], linewidth=0.8,
                   color=color, label=f'loop_bw={lbw}')

        log(f"  {lbw:>8.3f} | {conv_time:>10.2f} | "
            f"{overshoot:>11.1f} | {res_noise:>11.6f}")
        csv_rows.append([lbw, f"{conv_time:.2f}",
                         f"{overshoot:.1f}", f"{res_noise:.6f}"])
        tabelas_enunciado["pll"].append(
            (lbw, conv_time, overshoot))

    fig.suptitle(f"Etapa 3: Efeito de loop_bw — f_in={freq_in} Hz",
                 fontsize=13, fontweight='bold')
    plt.figure(fig.number)
    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, "etapa3_loop_bw_individual.png"),
                dpi=150, bbox_inches='tight')
    plt.close(fig)

    ax_ov.set_xlabel('Tempo (ms)')
    ax_ov.set_ylabel('Saída PLL')
    ax_ov.set_title(f'Comparação de loop_bw — f_in={freq_in} Hz')
    ax_ov.legend()
    plt.figure(fig_overlay.number)
    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, "etapa3_loop_bw_overlay.png"),
                dpi=150, bbox_inches='tight')
    plt.close(fig_overlay)

    save_csv("etapa3_loop_bw.csv",
             ["loop_bw", "conv_ms", "overshoot_pct", "residual_noise"],
             csv_rows)

    log(f"\n  -> etapa3_loop_bw_individual.png")
    log(f"  -> etapa3_loop_bw_overlay.png")
    log(f"  -> dados/etapa3_loop_bw.csv")

    log(f"\n  Resposta Q3: Loop_bw mais largo resulta em convergência")
    log(f"    mais rápida, porém com maior overshoot e maior")
    log(f"    sensibilidade ao ruído. Loop_bw estreito converge")
    log(f"    lentamente, mas com maior estabilidade e menor ruído")
    log(f"    residual. Trata-se do clássico tradeoff entre")
    log(f"    velocidade de resposta e estabilidade/filtragem.")


# =====================================================================
# ETAPA 4: Faixa de captura (capture range)
# =====================================================================
def etapa4():
    log("\n" + "=" * 65)
    log("ETAPA 4: Faixa de captura (capture range)")
    log("=" * 65)

    loop_bw = 0.062
    test_freqs = np.arange(200, 1850, 50)
    csv_rows = []
    locked_freqs = []

    log(f"\n  Varredura de frequência com loop_bw = {loop_bw}:")
    log(f"  {'f_in (Hz)':>10} | {'Valor final':>12} | "
        f"{'Ruído res.':>11} | {'Locked':>8}")
    log(f"  {'-'*10}-+-{'-'*12}-+-{'-'*11}-+-{'-'*8}")

    final_vals = []
    lock_status = []

    for freq in test_freqs:
        data = capture_pll(freq, loop_bw, n_samples=SAMP_RATE)
        tail = data[int(0.8 * len(data)):]
        final_val = np.mean(tail)
        res_noise = np.std(tail)

        # Lock criterion: low residual noise relative to final value
        # and consistent output (std < 10% of |mean| or std very small)
        if abs(final_val) > 1e-6:
            rel_noise = res_noise / abs(final_val)
            locked = rel_noise < 0.1
        else:
            locked = res_noise < 1e-4

        status = "SIM" if locked else "NAO"
        if locked:
            locked_freqs.append(freq)

        final_vals.append(final_val)
        lock_status.append(locked)

        if freq % 200 == 0 or not locked:
            log(f"  {freq:>10.0f} | {final_val:>12.6f} | "
                f"{res_noise:>11.6f} | {status:>8}")

        csv_rows.append([freq, f"{final_val:.6f}",
                         f"{res_noise:.6f}", status])

    # Determinar limites
    if locked_freqs:
        cap_min = min(locked_freqs)
        cap_max = max(locked_freqs)
    else:
        cap_min = cap_max = 0

    # Valor teórico: largura total = loop_bw * fs / pi (Hz)
    cap_theoretical_total = loop_bw * SAMP_RATE / np.pi
    cap_theoretical_half = cap_theoretical_total / 2

    log(f"\n  Faixa de captura medida: {cap_min:.0f} — {cap_max:.0f} Hz")
    log(f"  Largura medida: {cap_max - cap_min:.0f} Hz")
    log(f"  Valor teórico (loop_bw * fs / π): "
        f"{cap_theoretical_total:.1f} Hz (largura total)")

    # Subconjunto de frequências do enunciado para a tabela
    freqs_enunciado = [200, 600, 1000, 1400, 1800]
    test_freqs_list = list(test_freqs)
    for fE in freqs_enunciado:
        if fE in test_freqs_list:
            idx = test_freqs_list.index(fE)
            valor_regime = final_vals[idx]
            f_est = valor_regime * SAMP_RATE / (2 * np.pi)
            locked = 1 if lock_status[idx] else 0
            tabelas_enunciado["capture"].append(
                (fE, valor_regime, f_est, locked))
    tabelas_enunciado["capture_meta"] = {
        "df_cap_medida": cap_max - cap_min,
        "df_cap_teorica": cap_theoretical_total,
    }

    # Plot
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 7))

    colors_pts = ['#2ca02c' if l else '#d62728'
                  for l in lock_status]
    ax1.scatter(test_freqs, final_vals, c=colors_pts, s=20, zorder=3)
    ax1.plot(test_freqs, final_vals, linewidth=0.5, alpha=0.5,
             color='gray')
    ax1.set_xlabel('Frequência de entrada (Hz)')
    ax1.set_ylabel('Valor final da saída PLL')
    ax1.set_title('Saída do PLL vs. frequência de entrada '
                  '(verde=locked, vermelho=unlocked)')

    # Ruído residual
    res_noises = []
    for freq in test_freqs:
        data = capture_pll(freq, loop_bw, n_samples=SAMP_RATE)
        tail = data[int(0.8 * len(data)):]
        res_noises.append(np.std(tail))

    ax2.semilogy(test_freqs, res_noises, 'o-', markersize=3,
                 linewidth=0.8)
    ax2.set_xlabel('Frequência de entrada (Hz)')
    ax2.set_ylabel('Ruído residual (std)')
    ax2.set_title('Ruído residual vs. frequência de entrada')

    fig.suptitle(f"Etapa 4: Faixa de Captura — loop_bw={loop_bw}",
                 fontsize=13, fontweight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, "etapa4_capture_range.png"),
                dpi=150, bbox_inches='tight')
    plt.close()

    save_csv("etapa4_capture_range.csv",
             ["freq_Hz", "valor_final", "residual_noise", "locked"],
             csv_rows)

    log(f"\n  -> etapa4_capture_range.png")
    log(f"  -> dados/etapa4_capture_range.csv")

    log(f"\n  Resposta Q4: A faixa de captura é determinada pela")
    log(f"    largura de banda do loop. Teoricamente, capture range")
    log(f"    ≈ loop_bw × samp_rate / π em Hz (largura total).")
    log(f"    Com loop_bw={loop_bw}, o valor teórico é")
    log(f"    ≈ {cap_theoretical_total:.1f} Hz. O valor medido pode ser maior")
    log(f"    em simulação porque a janela de 1 s dá tempo para")
    log(f"    pull-in fora do capture range estrito; o limite duro")
    log(f"    é dado por max_freq/min_freq do bloco (±2000 Hz).")


# =====================================================================
# ETAPA 5: Efeito do ruído
# =====================================================================
def etapa5():
    log("\n" + "=" * 65)
    log("ETAPA 5: Efeito do ruído no PLL")
    log("=" * 65)

    noise_amps = [0, 0.1, 0.3, 0.5, 0.8, 1.0]
    freq_in = 1000
    loop_bw_narrow = 0.062
    loop_bw_wide = 0.2

    # --- Parte A: Efeito do ruído com loop_bw fixo ---
    fig, axes = plt.subplots(2, 3, figsize=(17, 9))
    csv_rows = []

    log(f"\n  Parte A: Efeito do ruído (loop_bw = {loop_bw_narrow}):")
    log(f"  {'noise_amp':>10} | {'Valor final':>12} | "
        f"{'Jitter (std)':>12} | {'Conv (ms)':>10}")
    log(f"  {'-'*10}-+-{'-'*12}-+-{'-'*12}-+-{'-'*10}")

    for ax, na in zip(axes.flat, noise_amps):
        data = capture_pll(freq_in, loop_bw_narrow, noise_amp=na)
        t = np.arange(len(data)) / SAMP_RATE * 1000

        tail = data[int(0.8 * len(data)):]
        final_val = np.mean(tail)
        jitter = np.std(tail)
        conv_idx = measure_convergence(data, threshold_pct=0.05)
        conv_time = conv_idx / SAMP_RATE * 1000

        n_plot = int(50 * SAMP_RATE / 1000)
        ax.plot(t[:n_plot], data[:n_plot], linewidth=0.5)
        ax.axhline(final_val, color='r', ls='--', alpha=0.5)
        ax.set_title(f'noise_amp = {na}  |  jitter = {jitter:.5f}')
        ax.set_xlabel('Tempo (ms)')
        ax.set_ylabel('Saída PLL')

        log(f"  {na:>10.1f} | {final_val:>12.6f} | "
            f"{jitter:>12.6f} | {conv_time:>10.2f}")
        csv_rows.append([na, f"{final_val:.6f}",
                         f"{jitter:.6f}", f"{conv_time:.2f}"])

    fig.suptitle(f"Etapa 5A: Efeito do Ruído — loop_bw={loop_bw_narrow}",
                 fontsize=13, fontweight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, "etapa5a_ruido_efeito.png"),
                dpi=150, bbox_inches='tight')
    plt.close()

    save_csv("etapa5a_ruido.csv",
             ["noise_amp", "valor_final", "jitter_std", "conv_ms"],
             csv_rows)

    # --- Parte B: Comparação narrow vs wide loop_bw com ruído ---
    log(f"\n  Parte B: Narrow vs Wide loop_bw com ruído:")
    log(f"  {'noise_amp':>10} | {'Jitter narrow':>14} | "
        f"{'Jitter wide':>12}")
    log(f"  {'-'*10}-+-{'-'*14}-+-{'-'*12}")

    fig, axes = plt.subplots(len(noise_amps), 2, figsize=(15, 4 * len(noise_amps)))
    csv_rows_b = []

    for i, na in enumerate(noise_amps):
        data_narrow = capture_pll(freq_in, loop_bw_narrow, noise_amp=na)
        data_wide = capture_pll(freq_in, loop_bw_wide, noise_amp=na)

        t = np.arange(len(data_narrow)) / SAMP_RATE * 1000
        n_plot = int(50 * SAMP_RATE / 1000)

        jitter_n = np.std(data_narrow[int(0.8 * len(data_narrow)):])
        jitter_w = np.std(data_wide[int(0.8 * len(data_wide)):])

        axes[i, 0].plot(t[:n_plot], data_narrow[:n_plot], linewidth=0.5)
        axes[i, 0].set_title(f'Narrow (loop_bw={loop_bw_narrow}) | '
                             f'noise={na} | jitter={jitter_n:.5f}')
        axes[i, 0].set_ylabel('Saída PLL')

        axes[i, 1].plot(t[:n_plot], data_wide[:n_plot], linewidth=0.5,
                        color='#ff7f0e')
        axes[i, 1].set_title(f'Wide (loop_bw={loop_bw_wide}) | '
                             f'noise={na} | jitter={jitter_w:.5f}')
        axes[i, 1].set_ylabel('Saída PLL')

        log(f"  {na:>10.1f} | {jitter_n:>14.6f} | {jitter_w:>12.6f}")
        csv_rows_b.append([na, f"{jitter_n:.6f}", f"{jitter_w:.6f}"])
        if na in [0.0, 0.1, 0.3, 0.5, 1.0]:
            tabelas_enunciado["ruido"].append(
                (na, jitter_n, jitter_w))

    axes[-1, 0].set_xlabel('Tempo (ms)')
    axes[-1, 1].set_xlabel('Tempo (ms)')

    fig.suptitle("Etapa 5B: Narrow vs Wide loop_bw com Ruído",
                 fontsize=13, fontweight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, "etapa5b_narrow_vs_wide.png"),
                dpi=150, bbox_inches='tight')
    plt.close()

    save_csv("etapa5b_narrow_vs_wide.csv",
             ["noise_amp", "jitter_narrow", "jitter_wide"],
             csv_rows_b)

    log(f"\n  -> etapa5a_ruido_efeito.png")
    log(f"  -> etapa5b_narrow_vs_wide.png")
    log(f"  -> dados/etapa5a_ruido.csv")
    log(f"  -> dados/etapa5b_narrow_vs_wide.csv")

    log(f"\n  Resposta Q5: O ruído causa jitter (variação) na saída do")
    log(f"    PLL. Com loop_bw mais largo, o PLL acompanha variações")
    log(f"    mais rápidas, incluindo o ruído, resultando em maior")
    log(f"    jitter. Com loop_bw estreito, o PLL filtra mais o ruído,")
    log(f"    mantendo a saída mais estável. O tradeoff é: loop largo")
    log(f"    = resposta rápida mas ruidosa; loop estreito = resposta")
    log(f"    lenta mas limpa.")


# =====================================================================
# ANÁLISES COMPLEMENTARES — DESVIOS DA ESTIMATIVA
# =====================================================================
def etapa6_jitter_hz():
    """Tabela 5: converte o jitter de rad/amostra para Hz."""
    log("\n" + "=" * 65)
    log("ETAPA 6: Jitter da estimativa de frequência em Hz")
    log("=" * 65)
    fator = SAMP_RATE / (2 * np.pi)
    log(f"\n  {'noise_amp':>10} | {'jitter_Hz lbw=0,062':>20} | "
        f"{'jitter_Hz lbw=0,200':>20}")
    log("  " + "-" * 60)
    for na, j062, j200 in tabelas_enunciado["ruido"]:
        j062_hz = j062 * fator
        j200_hz = j200 * fator
        log(f"  {na:>10.1f} | {j062_hz:>20.2f} | {j200_hz:>20.2f}")
        tabelas_enunciado["jitter_hz"].append((na, j062_hz, j200_hz))


def etapa7_saturacao():
    """Tabela 6: f_est em frequências próximas e além de Max Phase/sample."""
    log("\n" + "=" * 65)
    log("ETAPA 7: Saturação fora da faixa de hold (±2000 Hz)")
    log("=" * 65)

    freqs = [1500, 1900, 2000, 2100, 2300]
    loop_bw = 0.062
    fator = SAMP_RATE / (2 * np.pi)

    log(f"\n  {'f_in (Hz)':>10} | {'mu (rad/am)':>12} | "
        f"{'f_est (Hz)':>11} | {'desvio (Hz)':>12} | {'locked':>7}")
    log("  " + "-" * 65)
    for f in freqs:
        data = capture_pll(f, loop_bw, n_samples=2 * SAMP_RATE)
        tail = data[int(0.8 * len(data)):]
        mu = np.mean(tail)
        f_est = mu * fator
        desvio = f_est - f
        locked = 1 if is_locked(data) else 0
        log(f"  {f:>10} | {mu:>12.6f} | {f_est:>11.2f} | "
            f"{desvio:>+12.2f} | {locked:>7d}")
        tabelas_enunciado["saturacao"].append((f, f_est, desvio, locked))


def etapa8_janela_curta():
    """Tabela 7: faixa de captura com janela de observação curta (50 ms)."""
    log("\n" + "=" * 65)
    log("ETAPA 8: Captura com janela curta (50 ms) — convergência teórica")
    log("=" * 65)

    freqs = [200, 600, 1000, 1400, 1800]
    loop_bw = 0.062
    fator = SAMP_RATE / (2 * np.pi)
    n_curto = int(0.05 * SAMP_RATE)  # 50 ms

    locked_freqs = []
    log(f"\n  Janela curta = {n_curto} amostras ({n_curto/SAMP_RATE*1000:.0f} ms)")
    log(f"  {'f_in (Hz)':>10} | {'f_est (Hz)':>11} | {'locked':>7}")
    log("  " + "-" * 40)
    for f in freqs:
        data = capture_pll(f, loop_bw, n_samples=2 * SAMP_RATE)
        data_curto = data[:n_curto]
        # Critério de lock na janela curta: 20% finais da janela curta
        locked = 1 if is_locked(data_curto) else 0
        mu = np.mean(data_curto[int(0.8 * len(data_curto)):])
        f_est = mu * fator
        if locked:
            locked_freqs.append(f)
        log(f"  {f:>10} | {f_est:>11.2f} | {locked:>7d}")
        tabelas_enunciado["janela_curta"].append((f, f_est, locked))

    df_cap_med = max(locked_freqs) - min(locked_freqs) if locked_freqs else 0
    df_cap_teo = loop_bw * SAMP_RATE / np.pi
    tabelas_enunciado["janela_curta_meta"] = {
        "df_cap_med": df_cap_med,
        "df_cap_teo": df_cap_teo,
    }
    log(f"\n  Df_cap medida (janela curta) = {df_cap_med} Hz")
    log(f"  Df_cap teorica               = {df_cap_teo:.1f} Hz")


def etapa9_bias_ruido():
    """Tabela 8: bias de f_est em janela curta sob ruído."""
    log("\n" + "=" * 65)
    log("ETAPA 9: Bias de f_est em janela curta sob ruído (f_in=1000)")
    log("=" * 65)

    freq_in = 1000
    noise_amps = [0.0, 0.3, 0.5, 1.0]
    fator = SAMP_RATE / (2 * np.pi)
    n_curto = int(0.05 * SAMP_RATE)  # 50 ms

    log(f"\n  Janela curta = {n_curto} amostras")
    log(f"  {'noise_amp':>10} | {'f_est lbw=0,062 (Hz)':>22} | "
        f"{'f_est lbw=0,200 (Hz)':>22}")
    log("  " + "-" * 65)
    for na in noise_amps:
        d062 = capture_pll(freq_in, 0.062, noise_amp=na, n_samples=2 * SAMP_RATE)
        d200 = capture_pll(freq_in, 0.200, noise_amp=na, n_samples=2 * SAMP_RATE)
        mu062 = np.mean(d062[:n_curto][int(0.8 * n_curto):])
        mu200 = np.mean(d200[:n_curto][int(0.8 * n_curto):])
        f_est_062 = mu062 * fator
        f_est_200 = mu200 * fator
        log(f"  {na:>10.1f} | {f_est_062:>22.2f} | {f_est_200:>22.2f}")
        tabelas_enunciado["bias_curto"].append((na, f_est_062, f_est_200))


# =====================================================================
# IMPRESSÃO DAS TABELAS NO FORMATO DO ENUNCIADO
# =====================================================================
def imprimir_tabelas_enunciado():
    log("\n" + "=" * 70)
    log("TABELAS DO ENUNCIADO PREENCHIDAS COM OS VALORES MEDIDOS")
    log("=" * 70)

    # Tabela 1 (Etapa 2): tab:lock
    log("\nTabela 1 (tab:lock) — Etapa 2, loop_bw = 0,062")
    log("-" * 80)
    log(f"{'f_in (Hz)':>10} | {'Valor de regime (rad/am)':>24} | "
        f"{'f_est (Hz)':>11} | {'Locked':>7}")
    log("-" * 80)
    for f_in, v, fe, lk in tabelas_enunciado["lock"]:
        log(f"{f_in:>10} | {v:>24.6f} | {fe:>11.2f} | {lk:>7d}")

    # Tabela 2 (Etapa 3): tab:pll
    log("\nTabela 2 (tab:pll) — Etapa 3, f_in = 1000 Hz")
    log("-" * 70)
    log(f"{'loop_bw':>8} | {'t_conv (ms)':>12} | "
        f"{'Overshoot (%)':>14}")
    log("-" * 70)
    for lbw, tc, ov in tabelas_enunciado["pll"]:
        log(f"{lbw:>8.3f} | {tc:>12.2f} | {ov:>14.1f}")

    # Tabela 3 (Etapa 4): tab:capture
    log("\nTabela 3 (tab:capture) — Etapa 4, loop_bw = 0,062")
    log("-" * 80)
    log(f"{'f_in (Hz)':>10} | {'Valor de regime (rad/am)':>24} | "
        f"{'f_est (Hz)':>11} | {'Locked':>7}")
    log("-" * 80)
    for f_in, v, fe, lk in tabelas_enunciado["capture"]:
        log(f"{f_in:>10} | {v:>24.6f} | {fe:>11.2f} | {lk:>7d}")
    meta = tabelas_enunciado["capture_meta"]
    log("-" * 80)
    log(f"Df_cap medida (Hz): {meta.get('df_cap_medida', 0):.0f}")
    log(f"Df_cap teorica (loop_bw * fs / pi) (Hz): "
        f"{meta.get('df_cap_teorica', 0):.1f}")

    # Tabela 4 (Etapa 5): tab:ruido
    log("\nTabela 4 (tab:ruido) — Etapa 5, f_in = 1000 Hz")
    log("-" * 70)
    log(f"{'noise_amp':>10} | {'Jitter loop_bw=0,062':>22} | "
        f"{'Jitter loop_bw=0,200':>22}")
    log("-" * 70)
    for na, jn, jw in tabelas_enunciado["ruido"]:
        log(f"{na:>10.1f} | {jn:>22.6f} | {jw:>22.6f}")

    # Tabela 5: jitter em Hz
    log("\nTabela 5 (jitter em Hz) — Etapa 6")
    log("-" * 70)
    log(f"{'noise_amp':>10} | {'jitter_Hz lbw=0,062':>21} | "
        f"{'jitter_Hz lbw=0,200':>21}")
    log("-" * 70)
    for na, j062, j200 in tabelas_enunciado["jitter_hz"]:
        log(f"{na:>10.1f} | {j062:>21.2f} | {j200:>21.2f}")

    # Tabela 6: saturação
    log("\nTabela 6 (saturacao) — Etapa 7, loop_bw=0,062, sem ruido")
    log("-" * 70)
    log(f"{'f_in (Hz)':>10} | {'f_est (Hz)':>11} | "
        f"{'desvio (Hz)':>12} | {'locked':>7}")
    log("-" * 70)
    for f_in, fe, dv, lk in tabelas_enunciado["saturacao"]:
        log(f"{f_in:>10} | {fe:>11.2f} | {dv:>+12.2f} | {lk:>7d}")

    # Tabela 7: janela curta
    log("\nTabela 7 (janela_curta) — Etapa 8, loop_bw=0,062, janela=50 ms")
    log("-" * 70)
    log(f"{'f_in (Hz)':>10} | {'f_est (Hz)':>11} | {'locked':>7}")
    log("-" * 70)
    for f_in, fe, lk in tabelas_enunciado["janela_curta"]:
        log(f"{f_in:>10} | {fe:>11.2f} | {lk:>7d}")
    meta_jc = tabelas_enunciado["janela_curta_meta"]
    log("-" * 70)
    log(f"Df_cap medida (janela curta) (Hz): {meta_jc.get('df_cap_med', 0)}")
    log(f"Df_cap teorica               (Hz): {meta_jc.get('df_cap_teo', 0):.1f}")

    # Tabela 8: bias em janela curta sob ruído
    log("\nTabela 8 (bias_curto) — Etapa 9, f_in=1000, janela=50 ms")
    log("-" * 70)
    log(f"{'noise_amp':>10} | {'f_est lbw=0,062 (Hz)':>22} | "
        f"{'f_est lbw=0,200 (Hz)':>22}")
    log("-" * 70)
    for na, fe062, fe200 in tabelas_enunciado["bias_curto"]:
        log(f"{na:>10.1f} | {fe062:>22.2f} | {fe200:>22.2f}")

    # Salvar arquivo separado contendo apenas as tabelas formatadas
    tab_path = os.path.join(BASE_DIR, "tabelas_enunciado.txt")
    with open(tab_path, 'w') as f:
        f.write("TABELAS DO ENUNCIADO PREENCHIDAS\n")
        f.write("=" * 70 + "\n\n")
        f.write("Tabela 1 (tab:lock) - Etapa 2, loop_bw = 0,062\n")
        f.write(f"{'f_in (Hz)':>10} | {'Valor de regime':>20} | "
                f"{'f_est (Hz)':>11} | {'Locked':>7}\n")
        for f_in, v, fe, lk in tabelas_enunciado["lock"]:
            f.write(f"{f_in:>10} | {v:>20.6f} | "
                    f"{fe:>11.2f} | {lk:>7d}\n")
        f.write("\nTabela 2 (tab:pll) - Etapa 3, f_in = 1000 Hz\n")
        f.write(f"{'loop_bw':>8} | {'t_conv (ms)':>12} | "
                f"{'Overshoot %':>12}\n")
        for lbw, tc, ov in tabelas_enunciado["pll"]:
            f.write(f"{lbw:>8.3f} | {tc:>12.2f} | {ov:>12.1f}\n")
        f.write("\nTabela 3 (tab:capture) - Etapa 4, loop_bw = 0,062\n")
        f.write(f"{'f_in (Hz)':>10} | {'Valor de regime':>20} | "
                f"{'f_est (Hz)':>11} | {'Locked':>7}\n")
        for f_in, v, fe, lk in tabelas_enunciado["capture"]:
            f.write(f"{f_in:>10} | {v:>20.6f} | "
                    f"{fe:>11.2f} | {lk:>7d}\n")
        meta = tabelas_enunciado["capture_meta"]
        f.write(f"Df_cap medida = {meta.get('df_cap_medida', 0):.0f} Hz\n")
        f.write(f"Df_cap teorica = {meta.get('df_cap_teorica', 0):.1f} Hz\n")
        f.write("\nTabela 4 (tab:ruido) - Etapa 5, f_in = 1000 Hz\n")
        f.write(f"{'noise_amp':>10} | {'Jitter lbw=0,062':>17} | "
                f"{'Jitter lbw=0,200':>17}\n")
        for na, jn, jw in tabelas_enunciado["ruido"]:
            f.write(f"{na:>10.1f} | {jn:>17.6f} | {jw:>17.6f}\n")
    log(f"\n-> {tab_path}")


# =====================================================================
# MAIN
# =====================================================================
if __name__ == '__main__':
    log("=" * 65)
    log("PRÁTICA 07 — PHASE-LOCKED LOOP (PLL)")
    log("GABARITO DO PROFESSOR")
    log(f"Data: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    log(f"GNU Radio: {gr.version()}")
    log(f"Sample Rate: {SAMP_RATE} Hz | Amostras: {N_SAMPLES}")
    log(f"Max Freq: {MAX_FREQ:.6f} rad/amostra | "
        f"Min Freq: {MIN_FREQ:.6f} rad/amostra")
    log(f"Saída: {BASE_DIR}")
    log("=" * 65)

    etapa1()
    etapa2()
    etapa3()
    etapa4()
    etapa5()
    etapa6_jitter_hz()
    etapa7_saturacao()
    etapa8_janela_curta()
    etapa9_bias_ruido()

    imprimir_tabelas_enunciado()

    log("\n" + "=" * 65)
    log("GABARITO COMPLETO GERADO COM SUCESSO")
    log("=" * 65)

    # Salvar relatório em texto
    report_path = os.path.join(BASE_DIR, "relatorio.txt")
    with open(report_path, 'w') as f:
        f.write('\n'.join(relatorio))
    print(f"\nRelatório salvo em: {report_path}")
