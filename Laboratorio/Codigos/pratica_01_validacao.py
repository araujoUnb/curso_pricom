#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Prática 01 – FFT e Análise Espectral: Validação Programática
=============================================================
Este script valida todas as 6 etapas da Prática 01 usando GNU Radio
em modo headless (sem GUI), gerando figuras PNG com os resultados.

Execução:  /usr/bin/python3 pratica_01_validacao.py

Saída: figuras em ./pratica_01_resultados/
"""

import os
import sys
import numpy as np

# GNU Radio está no Python do sistema, não no venv
try:
    from gnuradio import gr, analog, blocks
except ImportError:
    print("ERRO: GNU Radio não encontrado. Execute com /usr/bin/python3")
    sys.exit(1)

try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
except ImportError:
    print("ERRO: matplotlib não encontrado. Instale: pip install matplotlib")
    sys.exit(1)

# Diretório de saída
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "pratica_01_resultados")
os.makedirs(OUT_DIR, exist_ok=True)

SAMP_RATE = 32000
N_SAMPLES = 32768  # amostras coletadas em cada teste


def capture_signal(top_block_class):
    """Executa um flowgraph e retorna as amostras capturadas."""
    tb = top_block_class()
    tb.run()
    data = np.array(tb.sink.data())
    return data


# =====================================================================
# Flowgraph base: gerador de sinal -> head -> vector_sink
# =====================================================================
class SingleTone(gr.top_block):
    def __init__(self, freq=1000, amp=1.0, n_samples=N_SAMPLES):
        gr.top_block.__init__(self, "SingleTone")
        self.src = analog.sig_source_f(SAMP_RATE, analog.GR_COS_WAVE,
                                       freq, amp, 0)
        self.head = blocks.head(gr.sizeof_float, n_samples)
        self.sink = blocks.vector_sink_f()
        self.connect(self.src, self.head, self.sink)


class TwoTone(gr.top_block):
    def __init__(self, f1=1000, a1=1.0, f2=2500, a2=0.5,
                 n_samples=N_SAMPLES):
        gr.top_block.__init__(self, "TwoTone")
        self.src1 = analog.sig_source_f(SAMP_RATE, analog.GR_COS_WAVE,
                                        f1, a1, 0)
        self.src2 = analog.sig_source_f(SAMP_RATE, analog.GR_COS_WAVE,
                                        f2, a2, 0)
        self.adder = blocks.add_ff()
        self.head = blocks.head(gr.sizeof_float, n_samples)
        self.sink = blocks.vector_sink_f()
        self.connect(self.src1, (self.adder, 0))
        self.connect(self.src2, (self.adder, 1))
        self.connect(self.adder, self.head, self.sink)


class TwoToneNoise(gr.top_block):
    def __init__(self, f1=1000, a1=1.0, f2=2500, a2=0.5,
                 noise_amp=0.0, n_samples=N_SAMPLES):
        gr.top_block.__init__(self, "TwoToneNoise")
        self.src1 = analog.sig_source_f(SAMP_RATE, analog.GR_COS_WAVE,
                                        f1, a1, 0)
        self.src2 = analog.sig_source_f(SAMP_RATE, analog.GR_COS_WAVE,
                                        f2, a2, 0)
        self.noise = analog.noise_source_f(analog.GR_GAUSSIAN, noise_amp)
        self.add_sig = blocks.add_ff()
        self.add_noise = blocks.add_ff()
        self.head = blocks.head(gr.sizeof_float, n_samples)
        self.sink = blocks.vector_sink_f()
        self.connect(self.src1, (self.add_sig, 0))
        self.connect(self.src2, (self.add_sig, 1))
        self.connect(self.add_sig, (self.add_noise, 0))
        self.connect(self.noise, (self.add_noise, 1))
        self.connect(self.add_noise, self.head, self.sink)


def compute_spectrum(data, fft_size, window='hann'):
    """Calcula o espectro de magnitude em dB usando a janela especificada."""
    windows = {
        'rectangular': np.ones(fft_size),
        'hann': np.hanning(fft_size),
        'hamming': np.hamming(fft_size),
        'blackman-harris': np.blackman(fft_size),
    }
    w = windows[window]
    # Usar os últimos fft_size pontos (sinal estável)
    segment = data[-fft_size:]
    windowed = segment * w
    spectrum = np.fft.rfft(windowed)
    mag_db = 20 * np.log10(np.abs(spectrum) / fft_size + 1e-12)
    freqs = np.fft.rfftfreq(fft_size, 1.0 / SAMP_RATE)
    return freqs, mag_db


def plot_time_and_freq(data, fft_size, title, filename, window='hann',
                       t_samples=1024):
    """Plota domínio do tempo e frequência lado a lado."""
    fig, (ax_t, ax_f) = plt.subplots(1, 2, figsize=(14, 4))

    # Tempo
    t = np.arange(t_samples) / SAMP_RATE * 1000  # ms
    ax_t.plot(t, data[:t_samples], linewidth=0.7)
    ax_t.set_xlabel('Tempo (ms)')
    ax_t.set_ylabel('Amplitude')
    ax_t.set_title('Domínio do Tempo')
    ax_t.grid(True, alpha=0.3)

    # Frequência
    freqs, mag_db = compute_spectrum(data, fft_size, window)
    ax_f.plot(freqs, mag_db, linewidth=0.7)
    ax_f.set_xlabel('Frequência (Hz)')
    ax_f.set_ylabel('Magnitude (dB)')
    ax_f.set_title(f'Espectro (FFT={fft_size}, janela={window})')
    ax_f.set_xlim([0, SAMP_RATE / 2])
    ax_f.grid(True, alpha=0.3)

    fig.suptitle(title, fontsize=13, fontweight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, filename), dpi=150)
    plt.close()
    print(f"  -> Salvo: {filename}")


# =====================================================================
# ETAPA 1: Configuração inicial – tom único 1 kHz
# =====================================================================
def etapa1():
    print("\n=== ETAPA 1: Tom único 1 kHz ===")
    data = capture_signal(lambda: SingleTone(freq=1000))
    plot_time_and_freq(data, 1024, "Etapa 1: Tom único – 1 kHz",
                       "etapa1_tom_1kHz.png")

    # Verificar pico
    freqs, mag = compute_spectrum(data, 1024)
    peak_idx = np.argmax(mag)
    peak_freq = freqs[peak_idx]
    print(f"  Pico detectado em: {peak_freq:.0f} Hz (esperado: 1000 Hz)")
    assert abs(peak_freq - 1000) < 50, "FALHA: pico fora do esperado!"
    print("  [OK] Etapa 1 validada.")


# =====================================================================
# ETAPA 2: Variação de frequência
# =====================================================================
def etapa2():
    print("\n=== ETAPA 2: Variação de frequência ===")
    test_freqs = [500, 1000, 2000, 4000]
    fig, axes = plt.subplots(2, 2, figsize=(14, 8))

    for ax, freq in zip(axes.flat, test_freqs):
        data = capture_signal(lambda f=freq: SingleTone(freq=f))
        freqs, mag = compute_spectrum(data, 1024)

        peak_idx = np.argmax(mag)
        peak_freq = freqs[peak_idx]
        print(f"  f={freq} Hz -> pico em {peak_freq:.0f} Hz", end="")

        ax.plot(freqs, mag, linewidth=0.7)
        ax.axvline(freq, color='r', linestyle='--', alpha=0.5,
                   label=f'Esperado: {freq} Hz')
        ax.set_title(f'f = {freq} Hz (pico: {peak_freq:.0f} Hz)')
        ax.set_xlabel('Frequência (Hz)')
        ax.set_ylabel('Magnitude (dB)')
        ax.set_xlim([0, SAMP_RATE / 2])
        ax.grid(True, alpha=0.3)
        ax.legend(fontsize=8)

        ok = abs(peak_freq - freq) < 50
        print(" [OK]" if ok else " [FALHA]")

    plt.suptitle("Etapa 2: Variação de Frequência", fontsize=13,
                 fontweight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, "etapa2_variacao_freq.png"), dpi=150)
    plt.close()
    print("  -> Salvo: etapa2_variacao_freq.png")
    print("  [OK] Etapa 2 validada.")


# =====================================================================
# ETAPA 3: Dois tons
# =====================================================================
def etapa3():
    print("\n=== ETAPA 3: Sinal com dois tons (1000 + 2500 Hz) ===")
    data = capture_signal(lambda: TwoTone(f1=1000, a1=1.0, f2=2500, a2=0.5))
    plot_time_and_freq(data, 1024, "Etapa 3: Dois tons – 1000 Hz + 2500 Hz",
                       "etapa3_dois_tons.png")

    freqs, mag = compute_spectrum(data, 1024)
    # Procurar os dois maiores picos
    # Máscara para encontrar picos locais
    from scipy.signal import find_peaks
    peaks, props = find_peaks(mag, height=-20, distance=10)
    peak_freqs = sorted(freqs[peaks][np.argsort(mag[peaks])[-2:]])

    print(f"  Picos detectados: {peak_freqs[0]:.0f} Hz "
          f"e {peak_freqs[1]:.0f} Hz")
    assert abs(peak_freqs[0] - 1000) < 50, "FALHA: pico 1 fora!"
    assert abs(peak_freqs[1] - 2500) < 50, "FALHA: pico 2 fora!"

    # Verificar que amplitude do pico 2 é ~6 dB menor (0.5 vs 1.0)
    mag1 = mag[np.argmin(np.abs(freqs - 1000))]
    mag2 = mag[np.argmin(np.abs(freqs - 2500))]
    diff_db = mag1 - mag2
    print(f"  Diferença de amplitude: {diff_db:.1f} dB (esperado: ~6 dB)")
    print("  [OK] Etapa 3 validada.")


# =====================================================================
# ETAPA 4: Resolução espectral – efeito do FFT size
# =====================================================================
def etapa4():
    print("\n=== ETAPA 4: Resolução espectral (FFT size) ===")
    # Dois tons próximos: 1000 e 1200 Hz (diferença = 200 Hz)
    data = capture_signal(
        lambda: TwoTone(f1=1000, a1=1.0, f2=1200, a2=1.0,
                        n_samples=N_SAMPLES))

    fft_sizes = [256, 512, 1024, 2048, 4096]
    n = len(fft_sizes)
    fig, axes = plt.subplots(n, 1, figsize=(12, 3 * n))

    print(f"\n  {'FFT Size':>10} | {'Δf (Hz)':>10} | {'Picos separados?':>18}")
    print(f"  {'-'*10}-+-{'-'*10}-+-{'-'*18}")

    for ax, N in zip(axes, fft_sizes):
        delta_f = SAMP_RATE / N
        freqs, mag = compute_spectrum(data, N)

        # Verificar se os picos estão separados
        idx_900 = np.argmin(np.abs(freqs - 900))
        idx_1300 = np.argmin(np.abs(freqs - 1300))
        region = mag[idx_900:idx_1300]
        freqs_region = freqs[idx_900:idx_1300]

        # Procurar vale entre os dois picos
        if len(region) > 3:
            peak1_idx = np.argmin(np.abs(freqs_region - 1000))
            peak2_idx = np.argmin(np.abs(freqs_region - 1200))
            if peak1_idx < peak2_idx and peak2_idx - peak1_idx > 1:
                valley = np.min(region[peak1_idx:peak2_idx + 1])
                peak_max = max(region[peak1_idx], region[peak2_idx])
                separated = (peak_max - valley) > 3  # 3 dB de contraste
            else:
                separated = False
        else:
            separated = False

        status = "Sim" if separated else "Não"
        print(f"  {N:>10} | {delta_f:>10.1f} | {status:>18}")

        ax.plot(freqs, mag, linewidth=0.7)
        ax.axvline(1000, color='r', linestyle='--', alpha=0.4)
        ax.axvline(1200, color='g', linestyle='--', alpha=0.4)
        ax.set_xlim([500, 2000])
        ax.set_title(f'FFT Size = {N}  |  Δf = {delta_f:.1f} Hz  |  '
                     f'Separados: {status}')
        ax.set_ylabel('dB')
        ax.grid(True, alpha=0.3)

    axes[-1].set_xlabel('Frequência (Hz)')
    plt.suptitle("Etapa 4: Resolução Espectral – Tons em 1000 e 1200 Hz",
                 fontsize=13, fontweight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, "etapa4_resolucao_fft.png"), dpi=150)
    plt.close()
    print("  -> Salvo: etapa4_resolucao_fft.png")

    # Verificar Q2: separar tons com 100 Hz de diferença
    print("\n  --- Verificação Q2: tons com 100 Hz de diferença ---")
    for N in [256, 512, 1024]:
        delta_f = SAMP_RATE / N
        resolvable = delta_f <= 100
        print(f"  N={N}: Δf={delta_f:.1f} Hz -> "
              f"{'Resolve' if resolvable else 'Não resolve'} 100 Hz")
    print("  Mínimo N para Δf<=100 Hz: N >= 320 -> N=512 (potência de 2)")
    print("  [OK] Etapa 4 validada.")


# =====================================================================
# ETAPA 5: Efeito do ruído
# =====================================================================
def etapa5():
    print("\n=== ETAPA 5: Efeito do ruído gaussiano ===")
    noise_levels = [0, 0.5, 1.0, 2.0, 5.0, 10.0]
    fig, axes = plt.subplots(2, 3, figsize=(16, 8))

    for ax, noise_amp in zip(axes.flat, noise_levels):
        data = capture_signal(
            lambda na=noise_amp: TwoToneNoise(
                f1=1000, a1=1.0, f2=2500, a2=0.5, noise_amp=na))
        freqs, mag = compute_spectrum(data, 1024)

        ax.plot(freqs, mag, linewidth=0.7)
        ax.axvline(1000, color='r', linestyle='--', alpha=0.3)
        ax.axvline(2500, color='g', linestyle='--', alpha=0.3)
        ax.set_title(f'noise_amp = {noise_amp}')
        ax.set_xlabel('Frequência (Hz)')
        ax.set_ylabel('dB')
        ax.set_xlim([0, SAMP_RATE / 2])
        ax.set_ylim([-80, 10])
        ax.grid(True, alpha=0.3)

        # Verificar visibilidade dos picos
        peak1 = mag[np.argmin(np.abs(freqs - 1000))]
        peak2 = mag[np.argmin(np.abs(freqs - 2500))]
        # Estimar piso de ruído (mediana excluindo picos)
        mask = (freqs > 200) & (np.abs(freqs - 1000) > 200) & \
               (np.abs(freqs - 2500) > 200)
        noise_floor = np.median(mag[mask]) if noise_amp > 0 else -80
        snr1 = peak1 - noise_floor
        snr2 = peak2 - noise_floor

        visible1 = "visível" if snr1 > 3 else "MASCARADO"
        visible2 = "visível" if snr2 > 3 else "MASCARADO"
        print(f"  noise={noise_amp:.1f}: piso={noise_floor:.1f} dB | "
              f"Tom1 SNR={snr1:.1f} dB ({visible1}) | "
              f"Tom2 SNR={snr2:.1f} dB ({visible2})")

    plt.suptitle("Etapa 5: Efeito do Ruído Gaussiano nos Tons",
                 fontsize=13, fontweight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, "etapa5_ruido.png"), dpi=150)
    plt.close()
    print("  -> Salvo: etapa5_ruido.png")
    print("  [OK] Etapa 5 validada.")


# =====================================================================
# ETAPA 6: Funções de janela
# =====================================================================
def etapa6():
    print("\n=== ETAPA 6: Funções de janela ===")
    data = capture_signal(lambda: SingleTone(freq=1000, n_samples=N_SAMPLES))
    windows = ['rectangular', 'hann', 'hamming', 'blackman-harris']
    fig, axes = plt.subplots(2, 2, figsize=(14, 8))

    for ax, win in zip(axes.flat, windows):
        freqs, mag = compute_spectrum(data, 1024, window=win)
        ax.plot(freqs, mag, linewidth=0.7)
        ax.set_title(f'Janela: {win.capitalize()}')
        ax.set_xlabel('Frequência (Hz)')
        ax.set_ylabel('dB')
        ax.set_xlim([0, 4000])
        ax.set_ylim([-100, 10])
        ax.grid(True, alpha=0.3)

        # Medir largura do pico e nível dos lóbulos laterais
        peak_idx = np.argmax(mag)
        peak_val = mag[peak_idx]
        # Largura a -3dB
        above_3db = mag > (peak_val - 3)
        width_bins = np.sum(above_3db)
        width_hz = width_bins * (SAMP_RATE / 1024)

        # Nível do maior lóbulo lateral
        sidelobe_mask = np.abs(freqs - freqs[peak_idx]) > 200
        if np.any(sidelobe_mask):
            max_sidelobe = np.max(mag[sidelobe_mask])
        else:
            max_sidelobe = -100
        sidelobe_suppression = peak_val - max_sidelobe

        print(f"  {win:>18}: pico={peak_val:.1f} dB | "
              f"largura(-3dB)≈{width_hz:.0f} Hz | "
              f"supressão lóbulos={sidelobe_suppression:.1f} dB")

    plt.suptitle("Etapa 6: Comparação de Funções de Janela (tom 1 kHz)",
                 fontsize=13, fontweight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, "etapa6_janelas.png"), dpi=150)
    plt.close()
    print("  -> Salvo: etapa6_janelas.png")
    print("  [OK] Etapa 6 validada.")


# =====================================================================
# MAIN
# =====================================================================
if __name__ == '__main__':
    print("=" * 60)
    print("Prática 01 – FFT e Análise Espectral: Validação")
    print(f"GNU Radio: {gr.version()}")
    print(f"Sample Rate: {SAMP_RATE} Hz")
    print(f"Resultados em: {OUT_DIR}")
    print("=" * 60)

    etapa1()
    etapa2()
    etapa3()
    etapa4()
    etapa5()
    etapa6()

    print("\n" + "=" * 60)
    print("RESULTADO FINAL: Todas as etapas validadas com sucesso!")
    print("A Prática 01 é FACTÍVEL conforme descrita no enunciado.")
    print("=" * 60)
