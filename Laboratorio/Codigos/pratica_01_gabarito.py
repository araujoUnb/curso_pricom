#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Prática 01 – FFT e Análise Espectral: Gabarito do Professor
=============================================================
Executa o flowgraph da Prática 01 em modo headless (sem GUI),
reproduzindo todas as etapas do enunciado e gerando:

  1. Figuras PNG de referência (tempo + espectro) para cada cenário
  2. Dados numéricos de cada medição (picos, SNR, resolução)
  3. Tabelas preenchidas (resolução espectral, parâmetros)
  4. Relatório resumo em texto

Execução:
    /usr/bin/python3 pratica_01_gabarito.py

Saída:
    ./pratica_01_gabarito/
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
    print("Execute com: /usr/bin/python3 pratica_01_gabarito.py")
    sys.exit(1)

try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.gridspec import GridSpec
except ImportError:
    print("ERRO: matplotlib não encontrado.")
    sys.exit(1)

from scipy.signal import find_peaks

# =====================================================================
# CONFIGURAÇÃO
# =====================================================================
SAMP_RATE = 32000
N_SAMPLES = 32768

BASE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "pratica_01_gabarito")
FIG_DIR = os.path.join(BASE_DIR, "figuras")
DATA_DIR = os.path.join(BASE_DIR, "dados")

for d in [BASE_DIR, FIG_DIR, DATA_DIR]:
    os.makedirs(d, exist_ok=True)

# Acumula linhas do relatório
relatorio = []


def log(msg=""):
    """Imprime e acumula no relatório."""
    print(msg)
    relatorio.append(msg)


# =====================================================================
# FLOWGRAPHS HEADLESS
# =====================================================================
class FlowgraphBase(gr.top_block):
    """Flowgraph genérico: fontes -> add -> add_noise -> head -> sink"""

    def __init__(self, sources, noise_amp=0.0, n_samples=N_SAMPLES):
        gr.top_block.__init__(self, "Pratica01")

        # Criar fontes de sinal
        self._sources = []
        for freq, amp in sources:
            src = analog.sig_source_f(
                SAMP_RATE, analog.GR_COS_WAVE, freq, amp, 0)
            self._sources.append(src)

        # Somar fontes
        if len(self._sources) == 1:
            signal_out = self._sources[0]
        else:
            self.add_sig = blocks.add_ff()
            for i, src in enumerate(self._sources):
                self.connect(src, (self.add_sig, i))
            signal_out = self.add_sig

        # Somar ruído
        if noise_amp > 0:
            self.noise = analog.noise_source_f(
                analog.GR_GAUSSIAN, noise_amp)
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
    """Captura amostras de um flowgraph e retorna numpy array."""
    tb = FlowgraphBase(sources, noise_amp, n_samples)
    tb.run()
    return np.array(tb.sink.data())


# =====================================================================
# FUNÇÕES DE ANÁLISE
# =====================================================================
WINDOWS = {
    'Rectangular': np.ones,
    'Hann': np.hanning,
    'Hamming': np.hamming,
    'Blackman-Harris': np.blackman,
}


def spectrum(data, fft_size, window='Hann'):
    """Retorna (freqs_hz, magnitude_dB)."""
    w = WINDOWS[window](fft_size)
    seg = data[-fft_size:]
    X = np.fft.rfft(seg * w)
    mag = 20 * np.log10(np.abs(X) / fft_size + 1e-12)
    freqs = np.fft.rfftfreq(fft_size, 1.0 / SAMP_RATE)
    return freqs, mag


def find_spectral_peaks(freqs, mag, height=-30, distance=10):
    """Encontra picos espectrais, retorna [(freq, mag_dB), ...]."""
    idx, _ = find_peaks(mag, height=height, distance=distance)
    # Ordenar por magnitude decrescente
    order = np.argsort(mag[idx])[::-1]
    return [(freqs[idx[i]], mag[idx[i]]) for i in order]


def noise_floor(freqs, mag, exclude_freqs, margin=200):
    """Estima piso de ruído excluindo regiões ao redor dos tons."""
    mask = np.ones(len(freqs), dtype=bool)
    mask[freqs < 100] = False
    for f in exclude_freqs:
        mask &= np.abs(freqs - f) > margin
    if np.any(mask):
        return np.median(mag[mask])
    return -80.0


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


def plot_time_freq(data, fft_size, title, filename,
                   window='Hann', t_ms=5, markers=None):
    """Plota tempo e espectro lado a lado com marcadores opcionais."""
    fig, (ax_t, ax_f) = plt.subplots(1, 2, figsize=(15, 4.5))

    # --- Tempo ---
    n_pts = int(t_ms * SAMP_RATE / 1000)
    t = np.arange(n_pts) / SAMP_RATE * 1000
    ax_t.plot(t, data[:n_pts], linewidth=0.8, color='#1f77b4')
    ax_t.set_xlabel('Tempo (ms)')
    ax_t.set_ylabel('Amplitude')
    ax_t.set_title('Domínio do Tempo')

    # --- Espectro ---
    freqs, mag = spectrum(data, fft_size, window)
    ax_f.plot(freqs, mag, linewidth=0.8, color='#1f77b4')
    ax_f.set_xlabel('Frequência (Hz)')
    ax_f.set_ylabel('Magnitude (dB)')
    ax_f.set_title(f'Espectro (N={fft_size}, {window})')
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


# =====================================================================
# ETAPA 1: Tom único 1 kHz
# =====================================================================
def etapa1():
    log("\n" + "=" * 65)
    log("ETAPA 1: Configuração inicial — Tom único 1 kHz")
    log("=" * 65)

    data = capture([(1000, 1.0)])
    plot_time_freq(data, 1024,
                   "Etapa 1: Tom único — 1 kHz (referência)",
                   "etapa1_tom_1kHz.png",
                   markers=[(1000, '1 kHz')])

    freqs, mag = spectrum(data, 1024)
    peak_f = freqs[np.argmax(mag)]
    peak_db = np.max(mag)

    log(f"  Pico: {peak_f:.0f} Hz @ {peak_db:.1f} dB")
    log(f"  Resultado: {'OK' if abs(peak_f - 1000) < 50 else 'FALHA'}")
    log(f"  -> etapa1_tom_1kHz.png")

    return data


# =====================================================================
# ETAPA 2: Variação de frequência
# =====================================================================
def etapa2():
    log("\n" + "=" * 65)
    log("ETAPA 2: Variação de frequência do tom único")
    log("=" * 65)

    test_freqs = [500, 1000, 2000, 4000]
    fig, axes = plt.subplots(2, 2, figsize=(15, 9))
    csv_rows = []

    for ax, freq in zip(axes.flat, test_freqs):
        data = capture([(freq, 1.0)])
        freqs, mag = spectrum(data, 1024)

        peak_f = freqs[np.argmax(mag)]
        peak_db = np.max(mag)
        bin_k = int(round(freq * 1024 / SAMP_RATE))

        ax.plot(freqs, mag, linewidth=0.8)
        ax.axvline(freq, color='r', ls='--', alpha=0.5)
        ax.set_title(f'f = {freq} Hz → pico em {peak_f:.0f} Hz '
                     f'(bin k={bin_k})')
        ax.set_xlabel('Frequência (Hz)')
        ax.set_ylabel('dB')
        ax.set_xlim([0, SAMP_RATE / 2])

        log(f"  f={freq:>5} Hz → pico={peak_f:>6.0f} Hz "
            f"(bin k={bin_k:>3}) @ {peak_db:.1f} dB")
        csv_rows.append([freq, peak_f, bin_k, f"{peak_db:.1f}"])

    plt.suptitle("Etapa 2: Variação de Frequência — Referência",
                 fontsize=13, fontweight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, "etapa2_variacao_freq.png"),
                dpi=150, bbox_inches='tight')
    plt.close()

    save_csv("etapa2_freq_vs_bin.csv",
             ["freq_config_Hz", "freq_pico_Hz", "bin_k", "mag_dB"],
             csv_rows)

    log(f"  -> etapa2_variacao_freq.png")
    log(f"  -> dados/etapa2_freq_vs_bin.csv")
    log(f"\n  Resposta Q1: f_k = k·f_s/N. Cada frequência aparece"
        f" exatamente no bin correspondente.")


# =====================================================================
# ETAPA 3: Dois tons
# =====================================================================
def etapa3():
    log("\n" + "=" * 65)
    log("ETAPA 3: Sinal com dois tons (1000 Hz + 2500 Hz)")
    log("=" * 65)

    data = capture([(1000, 1.0), (2500, 0.5)])
    plot_time_freq(data, 1024,
                   "Etapa 3: Dois tons — 1000 Hz (A=1) + 2500 Hz (A=0.5)",
                   "etapa3_dois_tons.png",
                   markers=[(1000, 'f₁=1 kHz'), (2500, 'f₂=2.5 kHz')])

    freqs, mag = spectrum(data, 1024)
    mag1 = mag[np.argmin(np.abs(freqs - 1000))]
    mag2 = mag[np.argmin(np.abs(freqs - 2500))]
    diff = mag1 - mag2

    log(f"  Tom 1 (1000 Hz, A=1.0): {mag1:.1f} dB")
    log(f"  Tom 2 (2500 Hz, A=0.5): {mag2:.1f} dB")
    log(f"  Diferença: {diff:.1f} dB (esperado: ~6.0 dB)")
    log(f"  -> etapa3_dois_tons.png")
    log(f"\n  Resposta Q3: Sim, superposição linear. DFT é linear,")
    log(f"  logo X[k] = X1[k] + X2[k]. Não há intermodulação.")

    return data


# =====================================================================
# ETAPA 4: Resolução espectral
# =====================================================================
def etapa4():
    log("\n" + "=" * 65)
    log("ETAPA 4: Resolução espectral — efeito do FFT size")
    log("=" * 65)

    # Dois tons próximos para testar resolução
    data_200 = capture([(1000, 1.0), (1200, 1.0)])
    data_100 = capture([(1000, 1.0), (1100, 1.0)])

    fft_sizes = [256, 512, 1024, 2048, 4096]
    n = len(fft_sizes)
    fig, axes = plt.subplots(n, 1, figsize=(13, 3.2 * n))

    log(f"\n  Tons em 1000 Hz e 1200 Hz (Δ=200 Hz):")
    header = f"  {'N':>6} | {'Δf (Hz)':>8} | {'Separados?':>12}"
    log(header)
    log(f"  {'-'*6}-+-{'-'*8}-+-{'-'*12}")

    csv_rows = []

    for ax, N in zip(axes, fft_sizes):
        delta_f = SAMP_RATE / N
        freqs, mag = spectrum(data_200, N)

        # Verificar separação
        i1 = np.argmin(np.abs(freqs - 900))
        i2 = np.argmin(np.abs(freqs - 1300))
        region = mag[i1:i2]
        fr = freqs[i1:i2]

        separated = False
        if len(region) > 3:
            p1 = np.argmin(np.abs(fr - 1000))
            p2 = np.argmin(np.abs(fr - 1200))
            if p1 < p2 and p2 - p1 > 1:
                valley = np.min(region[p1:p2 + 1])
                peak = max(region[p1], region[p2])
                separated = (peak - valley) > 3

        status = "Sim" if separated else "Não"
        log(f"  {N:>6} | {delta_f:>8.1f} | {status:>12}")
        csv_rows.append([N, f"{delta_f:.1f}", status])

        ax.plot(freqs, mag, linewidth=0.8)
        ax.axvline(1000, color='r', ls='--', alpha=0.4)
        ax.axvline(1200, color='g', ls='--', alpha=0.4)
        ax.set_xlim([500, 2000])
        ax.set_title(f'N = {N}  |  Δf = {delta_f:.1f} Hz  |  '
                     f'Separados: {status}')
        ax.set_ylabel('dB')

    axes[-1].set_xlabel('Frequência (Hz)')
    plt.suptitle("Etapa 4: Resolução Espectral — Tons 1000 + 1200 Hz",
                 fontsize=13, fontweight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, "etapa4_resolucao_fft.png"),
                dpi=150, bbox_inches='tight')
    plt.close()

    save_csv("etapa4_resolucao.csv",
             ["FFT_Size_N", "Delta_f_Hz", "Picos_Separados"],
             csv_rows)

    log(f"\n  -> etapa4_resolucao_fft.png")
    log(f"  -> dados/etapa4_resolucao.csv")

    # Q2: mínimo N para 100 Hz
    log(f"\n  Resposta Q2: Para separar tons com Δ=100 Hz:")
    log(f"    Δf = f_s/N ≤ 100  →  N ≥ {SAMP_RATE}/100 = 320")
    log(f"    Menor potência de 2: N = 512 (Δf = 62.5 Hz)")


# =====================================================================
# ETAPA 5: Efeito do ruído
# =====================================================================
def etapa5():
    log("\n" + "=" * 65)
    log("ETAPA 5: Efeito do ruído gaussiano")
    log("=" * 65)

    noise_levels = [0, 0.5, 1.0, 2.0, 5.0, 10.0]
    fig, axes = plt.subplots(2, 3, figsize=(17, 9))
    csv_rows = []

    log(f"\n  {'noise':>7} | {'Piso(dB)':>9} | "
        f"{'SNR₁(dB)':>9} {'Tom1':>10} | "
        f"{'SNR₂(dB)':>9} {'Tom2':>10}")
    log(f"  {'-'*7}-+-{'-'*9}-+-{'-'*9}-{'-'*10}-+-"
        f"{'-'*9}-{'-'*10}")

    for ax, na in zip(axes.flat, noise_levels):
        data = capture([(1000, 1.0), (2500, 0.5)], noise_amp=na)
        freqs, mag = spectrum(data, 1024)

        ax.plot(freqs, mag, linewidth=0.6)
        ax.axvline(1000, color='r', ls='--', alpha=0.3)
        ax.axvline(2500, color='g', ls='--', alpha=0.3)
        ax.set_title(f'noise_amp = {na}')
        ax.set_xlabel('Frequência (Hz)')
        ax.set_ylabel('dB')
        ax.set_xlim([0, SAMP_RATE / 2])
        ax.set_ylim([-80, 10])

        peak1 = mag[np.argmin(np.abs(freqs - 1000))]
        peak2 = mag[np.argmin(np.abs(freqs - 2500))]
        nf = noise_floor(freqs, mag, [1000, 2500]) if na > 0 else -80
        snr1 = peak1 - nf
        snr2 = peak2 - nf

        v1 = "visível" if snr1 > 3 else "MASCARADO"
        v2 = "visível" if snr2 > 3 else "MASCARADO"
        log(f"  {na:>7.1f} | {nf:>9.1f} | "
            f"{snr1:>9.1f} {v1:>10} | "
            f"{snr2:>9.1f} {v2:>10}")
        csv_rows.append([na, f"{nf:.1f}", f"{snr1:.1f}", v1,
                         f"{snr2:.1f}", v2])

    plt.suptitle("Etapa 5: Efeito do Ruído Gaussiano",
                 fontsize=13, fontweight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, "etapa5_ruido.png"),
                dpi=150, bbox_inches='tight')
    plt.close()

    save_csv("etapa5_ruido.csv",
             ["noise_amp", "piso_dB", "SNR1_dB", "tom1_status",
              "SNR2_dB", "tom2_status"],
             csv_rows)

    log(f"\n  -> etapa5_ruido.png")
    log(f"  -> dados/etapa5_ruido.csv")
    log(f"\n  Resposta Q4: O piso de ruído sobe uniformemente.")
    log(f"  O tom de menor amplitude (A=0.5) é mascarado primeiro.")
    log(f"  Critério mínimo: SNR ≈ 0-3 dB para detecção visual.")


# =====================================================================
# ETAPA 6: Funções de janela
# =====================================================================
def etapa6():
    log("\n" + "=" * 65)
    log("ETAPA 6: Funções de janela e vazamento espectral")
    log("=" * 65)

    # Tom em 1000 Hz (frequência que cai exatamente no bin)
    data_on = capture([(1000, 1.0)])
    # Tom em 1050 Hz (NÃO cai no bin — maximiza vazamento)
    data_off = capture([(1050, 1.0)])

    win_names = list(WINDOWS.keys())
    fig, axes = plt.subplots(2, 2, figsize=(15, 9))
    csv_rows = []

    log(f"\n  Tom em 1050 Hz (off-bin, maximiza vazamento):")
    log(f"  {'Janela':>18} | {'Pico(dB)':>9} | "
        f"{'Larg -3dB(Hz)':>14} | {'Supressão(dB)':>14}")
    log(f"  {'-'*18}-+-{'-'*9}-+-{'-'*14}-+-{'-'*14}")

    for ax, wname in zip(axes.flat, win_names):
        freqs, mag = spectrum(data_off, 1024, window=wname)

        peak_idx = np.argmax(mag)
        peak_val = mag[peak_idx]
        peak_freq = freqs[peak_idx]

        # Largura a -3 dB
        above = mag > (peak_val - 3)
        width_hz = np.sum(above) * (SAMP_RATE / 1024)

        # Supressão do maior lóbulo lateral
        side_mask = np.abs(freqs - peak_freq) > 300
        max_side = np.max(mag[side_mask]) if np.any(side_mask) else -100
        suppression = peak_val - max_side

        log(f"  {wname:>18} | {peak_val:>9.1f} | "
            f"{width_hz:>14.0f} | {suppression:>14.1f}")
        csv_rows.append([wname, f"{peak_val:.1f}",
                         f"{width_hz:.0f}", f"{suppression:.1f}"])

        ax.plot(freqs, mag, linewidth=0.8)
        ax.set_title(f'{wname}  (pico={peak_val:.1f} dB, '
                     f'supressão={suppression:.1f} dB)')
        ax.set_xlabel('Frequência (Hz)')
        ax.set_ylabel('dB')
        ax.set_xlim([0, 4000])
        ax.set_ylim([-100, 10])

    plt.suptitle("Etapa 6: Funções de Janela — Tom 1050 Hz (off-bin)",
                 fontsize=13, fontweight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, "etapa6_janelas.png"),
                dpi=150, bbox_inches='tight')
    plt.close()

    save_csv("etapa6_janelas.csv",
             ["janela", "pico_dB", "largura_3dB_Hz", "supressao_dB"],
             csv_rows)

    log(f"\n  -> etapa6_janelas.png")
    log(f"  -> dados/etapa6_janelas.csv")
    log(f"\n  Resposta Q5:")
    log(f"  - Rectangular: pico mais alto, mas lóbulos laterais"
        f" elevados (vazamento).")
    log(f"  - Hann: pico ~6 dB menor, mas lóbulos laterais muito"
        f" mais baixos.")
    log(f"  - Blackman-Harris: maior supressão de lóbulos,"
        f" pico ligeiramente menor.")
    log(f"  Tradeoff: resolução em amplitude vs. vazamento espectral.")


# =====================================================================
# TABELA DE PARÂMETROS (3 cenários do enunciado)
# =====================================================================
def tabela_parametros():
    log("\n" + "=" * 65)
    log("TABELA DE PARÂMETROS — 3 CENÁRIOS DE REFERÊNCIA")
    log("=" * 65)

    header = (f"  {'Parâmetro':<22} | {'Cenário A':>12} | "
              f"{'Cenário B':>12} | {'Cenário C':>12}")
    log(header)
    log(f"  {'-'*22}-+-{'-'*12}-+-{'-'*12}-+-{'-'*12}")

    rows = [
        ("f₁ (Hz)",       "1000",  "1000",  "1000"),
        ("f₂ (Hz)",       "—",     "2500",  "2500"),
        ("A₁",            "1.0",   "1.0",   "1.0"),
        ("A₂",            "—",     "0.5",   "0.5"),
        ("samp_rate (Hz)", "32000", "32000", "32000"),
        ("FFT Size",       "1024",  "1024",  "1024"),
        ("noise_amp",      "0",     "0",     "5.0"),
        ("Janela",         "Hann",  "Hann",  "Hann"),
    ]

    for name, a, b, c in rows:
        log(f"  {name:<22} | {a:>12} | {b:>12} | {c:>12}")

    # Gerar figuras dos 3 cenários
    scenarios = [
        ("Cenário A: tom único",
         [(1000, 1.0)], 0, "cenario_A_tom_unico.png",
         [(1000, '1 kHz')]),
        ("Cenário B: dois tons sem ruído",
         [(1000, 1.0), (2500, 0.5)], 0, "cenario_B_dois_tons.png",
         [(1000, 'f₁'), (2500, 'f₂')]),
        ("Cenário C: dois tons com ruído",
         [(1000, 1.0), (2500, 0.5)], 5.0,
         "cenario_C_dois_tons_ruido.png",
         [(1000, 'f₁'), (2500, 'f₂')]),
    ]

    for title, srcs, na, fname, markers in scenarios:
        data = capture(srcs, noise_amp=na)
        plot_time_freq(data, 1024, title, fname, markers=markers)
        log(f"\n  -> {fname}")


# =====================================================================
# MAIN
# =====================================================================
if __name__ == '__main__':
    log("=" * 65)
    log("PRÁTICA 01 — FFT E ANÁLISE ESPECTRAL")
    log("GABARITO DO PROFESSOR")
    log(f"Data: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    log(f"GNU Radio: {gr.version()}")
    log(f"Sample Rate: {SAMP_RATE} Hz | Amostras: {N_SAMPLES}")
    log(f"Saída: {BASE_DIR}")
    log("=" * 65)

    etapa1()
    etapa2()
    etapa3()
    etapa4()
    etapa5()
    etapa6()
    tabela_parametros()

    log("\n" + "=" * 65)
    log("GABARITO COMPLETO GERADO COM SUCESSO")
    log("=" * 65)

    # Salvar relatório em texto
    report_path = os.path.join(BASE_DIR, "relatorio.txt")
    with open(report_path, 'w') as f:
        f.write('\n'.join(relatorio))
    print(f"\nRelatório salvo em: {report_path}")
