#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Pratica 03 -- AM Convencional (DSB+C): Gabarito do Professor
=============================================================
Executa o flowgraph da Pratica 03 em modo headless (sem GUI),
reproduzindo todas as etapas do enunciado e gerando:

  1. Figuras PNG de referencia (tempo + espectro) para cada cenario
  2. Dados numericos de cada medicao (amplitudes, eficiencia)
  3. Tabela comparativa para diferentes indices de modulacao
  4. Relatorio resumo em texto

Execucao:
    /usr/bin/python3 pratica_03_gabarito.py

Saida:
    ./pratica_03_gabarito/
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
    print("Execute com: /usr/bin/python3 pratica_03_gabarito.py")
    sys.exit(1)

try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
except ImportError:
    print("ERRO: matplotlib nao encontrado.")
    sys.exit(1)

from scipy.signal import hilbert, find_peaks

# =====================================================================
# CONFIGURACAO
# =====================================================================
SAMP_RATE = 48000
FC = 5000       # frequencia da portadora (Hz)
FM = 500        # frequencia da mensagem (Hz)
AC = 1.0        # amplitude da portadora
N_SAMPLES = 48000 * 2  # 2 segundos de sinal

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
# FLOWGRAPH HEADLESS: AM DSB+C
# =====================================================================
class AMFlowgraph(gr.top_block):
    """
    Gera sinal AM DSB+C: s(t) = Ac * [1 + mu*m(t)] * cos(2*pi*fc*t)

    Implementacao com blocos GNU Radio:
      msg_source ---> multiply_const(mu) ---> add_const(1.0)
                                                    |
      carrier_source -----> multiply_ff <-----------+
                                |
                            head -> sink
    """

    def __init__(self, mu, fc=FC, fm=FM, ac=AC,
                 samp_rate=SAMP_RATE, n_samples=N_SAMPLES):
        gr.top_block.__init__(self, "AM_DSB_C")

        # Fonte da mensagem: m(t) = cos(2*pi*fm*t)
        self.msg_source = analog.sig_source_f(
            samp_rate, analog.GR_COS_WAVE, fm, 1.0, 0)

        # Multiplicar por mu: mu * m(t)
        self.mu_scale = blocks.multiply_const_ff(mu)

        # Somar DC: 1 + mu*m(t)
        self.add_dc = blocks.add_const_ff(1.0)

        # Portadora: cos(2*pi*fc*t)
        self.carrier = analog.sig_source_f(
            samp_rate, analog.GR_COS_WAVE, fc, ac, 0)

        # Multiplicar envoltoria pela portadora
        self.multiply = blocks.multiply_ff()

        # Limitador de amostras e sink
        self.head = blocks.head(gr.sizeof_float, n_samples)
        self.sink = blocks.vector_sink_f()

        # Conexoes
        self.connect(self.msg_source, self.mu_scale, self.add_dc,
                     (self.multiply, 0))
        self.connect(self.carrier, (self.multiply, 1))
        self.connect(self.multiply, self.head, self.sink)


def capture_am(mu, n_samples=N_SAMPLES):
    """Captura amostras de um sinal AM DSB+C e retorna numpy array."""
    tb = AMFlowgraph(mu, n_samples=n_samples)
    tb.run()
    return np.array(tb.sink.data())


# =====================================================================
# FUNCOES DE ANALISE
# =====================================================================
def spectrum(data, fft_size=4096, window='hann'):
    """Retorna (freqs_hz, magnitude_dB)."""
    if window == 'hann':
        w = np.hanning(fft_size)
    else:
        w = np.ones(fft_size)
    seg = data[-fft_size:]
    X = np.fft.rfft(seg * w)
    mag = 20 * np.log10(np.abs(X) / fft_size + 1e-12)
    freqs = np.fft.rfftfreq(fft_size, 1.0 / SAMP_RATE)
    return freqs, mag


def measure_spectral_component(freqs, mag, target_freq, search_bw=50):
    """Mede amplitude de um componente espectral proximo a target_freq."""
    mask = np.abs(freqs - target_freq) < search_bw
    if not np.any(mask):
        return target_freq, -100.0
    idx = np.where(mask)[0]
    best = idx[np.argmax(mag[idx])]
    return freqs[best], mag[best]


def envelope_detector(signal, samp_rate=SAMP_RATE, fc=FC):
    """
    Detector de envoltoria usando transformada de Hilbert.
    Retorna a envoltoria do sinal AM.
    """
    analytic = hilbert(signal)
    envelope = np.abs(analytic)

    # Filtro passa-baixas para suavizar (corte bem abaixo de fc)
    cutoff = fc / 2
    from scipy.signal import butter, filtfilt
    order = 4
    nyq = samp_rate / 2
    b, a = butter(order, cutoff / nyq, btype='low')
    envelope_filtered = filtfilt(b, a, envelope)

    return envelope_filtered


def am_efficiency(mu):
    """Eficiencia AM para modulacao tonal: eta = mu^2 / (2 + mu^2)."""
    return mu**2 / (2 + mu**2)


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
# ETAPA 1: Modulador AM DSB+C
# =====================================================================
def etapa1():
    log("\n" + "=" * 65)
    log("ETAPA 1: Modulador AM DSB+C")
    log("=" * 65)
    log(f"  Parametros: fc={FC} Hz, fm={FM} Hz, Ac={AC}, mu=0.5")
    log(f"  s(t) = Ac * [1 + mu*m(t)] * cos(2*pi*fc*t)")

    mu = 0.5
    data = capture_am(mu)

    # --- Plotar tempo e espectro ---
    fig, (ax_t, ax_f) = plt.subplots(1, 2, figsize=(15, 4.5))

    # Tempo: mostrar alguns ciclos da mensagem (4 periodos de fm)
    n_pts = int(4 * SAMP_RATE / FM)
    t = np.arange(n_pts) / SAMP_RATE * 1000  # ms
    ax_t.plot(t, data[:n_pts], linewidth=0.5, color='#1f77b4',
              label='s(t)')

    # Envoltoria teorica
    t_s = np.arange(n_pts) / SAMP_RATE
    env_pos = AC * (1 + mu * np.cos(2 * np.pi * FM * t_s))
    env_neg = -AC * (1 + mu * np.cos(2 * np.pi * FM * t_s))
    ax_t.plot(t, env_pos, 'r--', linewidth=1.2, alpha=0.7,
              label='Envoltoria')
    ax_t.plot(t, env_neg, 'r--', linewidth=1.2, alpha=0.7)
    ax_t.set_xlabel('Tempo (ms)')
    ax_t.set_ylabel('Amplitude')
    ax_t.set_title(f'AM DSB+C no Tempo (mu={mu})')
    ax_t.legend(fontsize=8)

    # Espectro
    freqs, mag = spectrum(data)
    ax_f.plot(freqs, mag, linewidth=0.8, color='#1f77b4')
    ax_f.axvline(FC, color='r', ls='--', alpha=0.6,
                 label=f'Portadora ({FC} Hz)')
    ax_f.axvline(FC - FM, color='g', ls='--', alpha=0.6,
                 label=f'LSB ({FC - FM} Hz)')
    ax_f.axvline(FC + FM, color='orange', ls='--', alpha=0.6,
                 label=f'USB ({FC + FM} Hz)')
    ax_f.set_xlabel('Frequencia (Hz)')
    ax_f.set_ylabel('Magnitude (dB)')
    ax_f.set_title('Espectro AM DSB+C')
    ax_f.set_xlim([0, 3 * FC])
    ax_f.legend(fontsize=8)

    fig.suptitle("Etapa 1: Modulador AM DSB+C (mu=0.5)",
                 fontsize=13, fontweight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, "etapa1_am_dsbc.png"),
                dpi=150, bbox_inches='tight')
    plt.close()

    # Medicoes espectrais
    _, carrier_db = measure_spectral_component(freqs, mag, FC)
    _, lsb_db = measure_spectral_component(freqs, mag, FC - FM)
    _, usb_db = measure_spectral_component(freqs, mag, FC + FM)

    log(f"\n  Medicoes espectrais (mu={mu}):")
    log(f"    Portadora ({FC} Hz):       {carrier_db:.1f} dB")
    log(f"    LSB ({FC - FM} Hz):        {lsb_db:.1f} dB")
    log(f"    USB ({FC + FM} Hz):        {usb_db:.1f} dB")
    log(f"    Diferenca port-banda:      {carrier_db - lsb_db:.1f} dB")

    log(f"\n  Resposta Q5: A portadora tem amplitude Ac = {AC}.")
    log(f"  Cada banda lateral tem amplitude mu*Ac/2 = {mu*AC/2}.")
    log(f"  Diferenca esperada: 20*log10(2/mu) = "
        f"{20*np.log10(2/mu):.1f} dB")

    log(f"\n  -> etapa1_am_dsbc.png")

    # Salvar CSV
    save_csv("etapa1_espectro.csv",
             ["componente", "freq_Hz", "mag_dB"],
             [["portadora", FC, f"{carrier_db:.1f}"],
              ["LSB", FC - FM, f"{lsb_db:.1f}"],
              ["USB", FC + FM, f"{usb_db:.1f}"]])
    log(f"  -> dados/etapa1_espectro.csv")

    return data


# =====================================================================
# ETAPA 2: Variacao do indice de modulacao
# =====================================================================
def etapa2():
    log("\n" + "=" * 65)
    log("ETAPA 2: Variacao do indice de modulacao")
    log("=" * 65)

    mu_values = [0.3, 0.5, 0.8, 1.0, 1.3, 1.8]

    fig, axes = plt.subplots(3, 2, figsize=(16, 14))
    csv_rows = []

    log(f"\n  {'mu':>5} | {'Port(dB)':>9} | {'Banda(dB)':>10} | "
        f"{'Diff(dB)':>9} | {'Efic(%)':>8} | {'Status':>14}")
    log(f"  {'-'*5}-+-{'-'*9}-+-{'-'*10}-+-"
        f"{'-'*9}-+-{'-'*8}-+-{'-'*14}")

    for ax, mu in zip(axes.flat, mu_values):
        data = capture_am(mu)

        # Espectro
        freqs, mag = spectrum(data)
        _, carrier_db = measure_spectral_component(freqs, mag, FC)
        _, lsb_db = measure_spectral_component(freqs, mag, FC - FM)
        _, usb_db = measure_spectral_component(freqs, mag, FC + FM)
        sideband_db = (lsb_db + usb_db) / 2

        # Eficiencia
        eta = am_efficiency(mu) * 100

        # Detectar sobre-modulacao: verificar cruzamentos por zero
        # na envoltoria (1 + mu*m(t))
        t_s = np.arange(len(data)) / SAMP_RATE
        envelope_func = 1 + mu * np.cos(2 * np.pi * FM * t_s)
        min_envelope = np.min(envelope_func)
        over_mod = mu > 1.0

        if over_mod:
            status = "SOBRE-MODULADO"
        elif mu == 1.0:
            status = "MODULACAO PLENA"
        else:
            status = "sub-modulado"

        log(f"  {mu:>5.1f} | {carrier_db:>9.1f} | {sideband_db:>10.1f} | "
            f"{carrier_db - sideband_db:>9.1f} | {eta:>8.1f} | "
            f"{status:>14}")

        csv_rows.append([mu, f"{carrier_db:.1f}", f"{sideband_db:.1f}",
                         f"{carrier_db - sideband_db:.1f}",
                         f"{eta:.1f}", status])

        # --- Subplot: tempo ---
        # Mostrar 3 periodos da mensagem
        n_pts = int(3 * SAMP_RATE / FM)
        t_ms = np.arange(n_pts) / SAMP_RATE * 1000

        ax.plot(t_ms, data[:n_pts], linewidth=0.4, color='#1f77b4')

        # Envoltoria teorica
        t_env = np.arange(n_pts) / SAMP_RATE
        env_pos = AC * (1 + mu * np.cos(2 * np.pi * FM * t_env))
        env_neg = -AC * (1 + mu * np.cos(2 * np.pi * FM * t_env))
        ax.plot(t_ms, env_pos, 'r-', linewidth=1.0, alpha=0.7)
        ax.plot(t_ms, env_neg, 'r-', linewidth=1.0, alpha=0.7)

        if over_mod:
            ax.axhline(0, color='k', ls=':', alpha=0.5)

        ax.set_title(f'mu={mu} ({status}) | eta={eta:.1f}%',
                     fontsize=10)
        ax.set_xlabel('Tempo (ms)')
        ax.set_ylabel('Amplitude')
        ymax = AC * (1 + mu) * 1.1
        ax.set_ylim([-ymax, ymax])

    plt.suptitle("Etapa 2: Variacao do Indice de Modulacao (mu)",
                 fontsize=13, fontweight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, "etapa2_variacao_mu.png"),
                dpi=150, bbox_inches='tight')
    plt.close()

    save_csv("etapa2_variacao_mu.csv",
             ["mu", "portadora_dB", "banda_lateral_dB",
              "diferenca_dB", "eficiencia_pct", "status"],
             csv_rows)

    # --- Espectros comparativos ---
    fig, axes = plt.subplots(3, 2, figsize=(16, 14))
    for ax, mu in zip(axes.flat, mu_values):
        data = capture_am(mu)
        freqs, mag = spectrum(data)
        ax.plot(freqs, mag, linewidth=0.8, color='#1f77b4')
        ax.axvline(FC, color='r', ls='--', alpha=0.5, label='Portadora')
        ax.axvline(FC - FM, color='g', ls='--', alpha=0.5, label='LSB')
        ax.axvline(FC + FM, color='orange', ls='--', alpha=0.5,
                   label='USB')
        ax.set_xlim([FC - 3 * FM, FC + 3 * FM])
        ax.set_title(f'Espectro: mu={mu}')
        ax.set_xlabel('Frequencia (Hz)')
        ax.set_ylabel('Magnitude (dB)')
        if mu == mu_values[0]:
            ax.legend(fontsize=7)

    plt.suptitle("Etapa 2: Espectros AM para diferentes mu",
                 fontsize=13, fontweight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, "etapa2_espectros_mu.png"),
                dpi=150, bbox_inches='tight')
    plt.close()

    log(f"\n  Resposta Q1: mu = (Amax - Amin) / (Amax + Amin)")
    log(f"    onde Amax e Amin sao os valores maximo e minimo "
        f"da envoltoria.")
    log(f"  Resposta Q2: Para mu <= 1, a envoltoria segue a mensagem.")
    log(f"    Para mu > 1, a envoltoria cruza zero e distorce.")

    log(f"\n  -> etapa2_variacao_mu.png")
    log(f"  -> etapa2_espectros_mu.png")
    log(f"  -> dados/etapa2_variacao_mu.csv")


# =====================================================================
# ETAPA 3: Deteccao de envoltoria
# =====================================================================
def etapa3():
    log("\n" + "=" * 65)
    log("ETAPA 3: Deteccao de envoltoria")
    log("=" * 65)

    test_mus = [0.5, 1.0, 1.3]
    fig, axes = plt.subplots(3, 2, figsize=(16, 12))

    for i, mu in enumerate(test_mus):
        data = capture_am(mu, n_samples=N_SAMPLES)

        # Detector de envoltoria
        env = envelope_detector(data)

        # Remover DC e normalizar para comparar com mensagem
        env_ac = env - np.mean(env)
        if np.max(np.abs(env_ac)) > 1e-6:
            env_ac = env_ac / np.max(np.abs(env_ac))

        # Mensagem original (referencia)
        t_s = np.arange(len(data)) / SAMP_RATE
        msg_ref = np.cos(2 * np.pi * FM * t_s)

        # Mostrar 4 periodos da mensagem
        n_pts = int(4 * SAMP_RATE / FM)
        t_ms = np.arange(n_pts) / SAMP_RATE * 1000

        # Subplot esquerdo: sinal AM + envoltoria
        ax_l = axes[i, 0]
        ax_l.plot(t_ms, data[:n_pts], linewidth=0.3, color='#1f77b4',
                  alpha=0.6, label='s(t)')
        ax_l.plot(t_ms, env[:n_pts], 'r-', linewidth=1.5,
                  label='Envoltoria detectada')

        # Envoltoria teorica
        env_teorica = AC * (1 + mu * np.cos(2 * np.pi * FM
                                            * np.arange(n_pts)
                                            / SAMP_RATE))
        ax_l.plot(t_ms, env_teorica, 'g--', linewidth=1.2, alpha=0.7,
                  label='Envoltoria teorica')

        ax_l.set_xlabel('Tempo (ms)')
        ax_l.set_ylabel('Amplitude')
        if mu <= 1.0:
            ax_l.set_title(f'mu={mu}: Envoltoria OK')
        else:
            ax_l.set_title(f'mu={mu}: Envoltoria DISTORCIDA')
        ax_l.legend(fontsize=7)

        # Subplot direito: mensagem recuperada vs original
        ax_r = axes[i, 1]
        ax_r.plot(t_ms, msg_ref[:n_pts], 'g-', linewidth=1.5,
                  label='Mensagem original')
        ax_r.plot(t_ms, env_ac[:n_pts], 'r-', linewidth=1.5,
                  alpha=0.8, label='Recuperada (envoltoria)')
        ax_r.set_xlabel('Tempo (ms)')
        ax_r.set_ylabel('Amplitude normalizada')
        ax_r.legend(fontsize=7)

        if mu <= 1.0:
            ax_r.set_title(f'mu={mu}: Mensagem recuperada fielmente')
        else:
            ax_r.set_title(f'mu={mu}: Mensagem distorcida '
                           f'(sobre-modulacao)')

        # Calcular distorcao (correlacao)
        # Alinhar e comparar
        min_len = min(len(env_ac), len(msg_ref))
        corr = np.corrcoef(env_ac[:min_len], msg_ref[:min_len])[0, 1]
        log(f"  mu={mu}: correlacao msg_original vs recuperada = "
            f"{corr:.4f}"
            f" {'(OK)' if corr > 0.95 else '(DISTORCAO)'}")

    plt.suptitle("Etapa 3: Deteccao de Envoltoria",
                 fontsize=13, fontweight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, "etapa3_envoltoria.png"),
                dpi=150, bbox_inches='tight')
    plt.close()

    log(f"\n  Resposta Q2: Para mu <= 1, a envoltoria reproduz "
        f"fielmente a mensagem.")
    log(f"    Para mu > 1, a envoltoria cruza zero, causando "
        f"distorcao na deteccao.")
    log(f"  Resposta Q3: O detector de envoltoria falha para "
        f"mu > 1 porque a envoltoria")
    log(f"    Ac*(1 + mu*m(t)) se torna negativa, e |s(t)| nao "
        f"segue mais a mensagem.")

    log(f"\n  -> etapa3_envoltoria.png")


# =====================================================================
# ETAPA 4: Medicoes e tabela comparativa
# =====================================================================
def etapa4():
    log("\n" + "=" * 65)
    log("ETAPA 4: Medicoes e tabela comparativa")
    log("=" * 65)

    mu_values = [0.3, 0.5, 0.8, 1.0, 1.3, 1.8]
    csv_rows = []

    log(f"\n  {'mu':>5} | {'P_port':>8} | {'P_banda':>8} | "
        f"{'P_total':>8} | {'eta(%)':>7} | {'eta_teo(%)':>10}")
    log(f"  {'-'*5}-+-{'-'*8}-+-{'-'*8}-+-"
        f"{'-'*8}-+-{'-'*7}-+-{'-'*10}")

    for mu in mu_values:
        data = capture_am(mu)

        # Potencias teoricas (para sinal tonal):
        # P_portadora = Ac^2 / 2
        # P_cada_banda = (mu*Ac)^2 / 8
        # P_total = P_port + 2*P_banda = Ac^2/2 * (1 + mu^2/2)
        p_carrier_teo = AC**2 / 2
        p_sideband_teo = (mu * AC)**2 / 8  # cada banda
        p_total_teo = p_carrier_teo + 2 * p_sideband_teo
        eta_teo = am_efficiency(mu) * 100

        # Medicao no espectro
        freqs, mag = spectrum(data)
        _, carrier_db = measure_spectral_component(freqs, mag, FC)
        _, lsb_db = measure_spectral_component(freqs, mag, FC - FM)
        _, usb_db = measure_spectral_component(freqs, mag, FC + FM)

        # Converter dB para potencia relativa (para medicao)
        p_carrier_meas = 10**(carrier_db / 10)
        p_lsb_meas = 10**(lsb_db / 10)
        p_usb_meas = 10**(usb_db / 10)
        p_sideband_meas = p_lsb_meas + p_usb_meas
        p_total_meas = p_carrier_meas + p_sideband_meas

        eta_meas = (p_sideband_meas / p_total_meas * 100
                    if p_total_meas > 0 else 0)

        log(f"  {mu:>5.1f} | {p_carrier_teo:>8.4f} | "
            f"{2*p_sideband_teo:>8.4f} | {p_total_teo:>8.4f} | "
            f"{eta_meas:>7.1f} | {eta_teo:>10.1f}")

        csv_rows.append([
            mu,
            f"{p_carrier_teo:.4f}",
            f"{2*p_sideband_teo:.4f}",
            f"{p_total_teo:.4f}",
            f"{eta_meas:.1f}",
            f"{eta_teo:.1f}"
        ])

    save_csv("etapa4_potencias.csv",
             ["mu", "P_portadora", "P_bandas_laterais",
              "P_total", "eficiencia_medida_pct",
              "eficiencia_teorica_pct"],
             csv_rows)

    # --- Grafico de eficiencia ---
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

    mu_range = np.linspace(0.01, 2.0, 200)
    eta_range = am_efficiency(mu_range) * 100

    ax1.plot(mu_range, eta_range, 'b-', linewidth=2,
             label='eta = mu^2 / (2 + mu^2)')
    for mu in mu_values:
        eta = am_efficiency(mu) * 100
        ax1.plot(mu, eta, 'ro', markersize=8)
        ax1.annotate(f'mu={mu}\neta={eta:.1f}%',
                     xy=(mu, eta), xytext=(5, 10),
                     textcoords='offset points', fontsize=7)

    ax1.axvline(1.0, color='gray', ls=':', alpha=0.5,
                label='mu=1 (modulacao plena)')
    ax1.set_xlabel('Indice de modulacao (mu)')
    ax1.set_ylabel('Eficiencia (%)')
    ax1.set_title('Eficiencia AM vs Indice de Modulacao')
    ax1.legend(fontsize=8)
    ax1.set_xlim([0, 2])
    ax1.set_ylim([0, 70])

    # Grafico de barras: potencias
    x = np.arange(len(mu_values))
    width = 0.35
    p_carriers = [AC**2 / 2] * len(mu_values)
    p_sidebands = [(mu * AC)**2 / 4 for mu in mu_values]

    bars1 = ax2.bar(x - width/2, p_carriers, width,
                    label='P portadora', color='#1f77b4')
    bars2 = ax2.bar(x + width/2, p_sidebands, width,
                    label='P bandas laterais', color='#ff7f0e')

    ax2.set_xlabel('Indice de modulacao (mu)')
    ax2.set_ylabel('Potencia (W, normalizada)')
    ax2.set_title('Distribuicao de Potencia AM')
    ax2.set_xticks(x)
    ax2.set_xticklabels([str(m) for m in mu_values])
    ax2.legend(fontsize=8)

    plt.suptitle("Etapa 4: Eficiencia e Potencia AM DSB+C",
                 fontsize=13, fontweight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, "etapa4_eficiencia.png"),
                dpi=150, bbox_inches='tight')
    plt.close()

    log(f"\n  Resposta Q4: Eficiencia AM tonal: "
        f"eta = mu^2 / (2 + mu^2)")
    log(f"    Para mu=1.0 (modulacao plena): "
        f"eta = 1/(2+1) = 33.3%")
    log(f"    Em DSB-SC a portadora nao e transmitida, "
        f"logo eta = 100%.")
    log(f"    A maior parte da potencia AM vai para a portadora "
        f"(sem informacao).")

    log(f"\n  -> etapa4_eficiencia.png")
    log(f"  -> dados/etapa4_potencias.csv")


# =====================================================================
# MAIN
# =====================================================================
if __name__ == '__main__':
    log("=" * 65)
    log("PRATICA 03 -- AM CONVENCIONAL (DSB+C)")
    log("GABARITO DO PROFESSOR")
    log(f"Data: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    log(f"GNU Radio: {gr.version()}")
    log(f"Sample Rate: {SAMP_RATE} Hz | Amostras: {N_SAMPLES}")
    log(f"Portadora: {FC} Hz | Mensagem: {FM} Hz | Ac: {AC}")
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
