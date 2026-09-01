"""
Verificação via GNU Radio -- Prática 06
Roda o flowgraph equivalente ao pratica_06_fm_parte2.grc:
slope detector, discriminador balanceado e WBFM Receive em paralelo.
Confirma que os três demoduladores recuperam a mensagem e compara
fidelidade e robustez ao ruído.
"""
import sys
sys.path.insert(0, '/usr/lib/python3/dist-packages')

import numpy as np
import matplotlib.pyplot as plt

from gnuradio import gr, blocks, analog, filter as gr_filter
from gnuradio.filter import firdes


SAMP_RATE = 480_000
AUDIO_RATE = 48_000
DECIM = SAMP_RATE // AUDIO_RATE


class FmDemodFlowgraph(gr.top_block):
    """Replica pratica_06_fm_parte2.grc completo: três demoduladores em paralelo."""

    def __init__(self, fm_freq, max_dev, noise_amp, n_audio):
        gr.top_block.__init__(self)
        n_quad = n_audio * DECIM

        # Cadeia comum: mensagem + WBFM TX + ruído
        self.src_msg = analog.sig_source_f(
            AUDIO_RATE, analog.GR_COS_WAVE, fm_freq, 1.0
        )
        self.wbfm_tx = analog.wfm_tx(AUDIO_RATE, SAMP_RATE,
                                     tau=75e-6, max_dev=max_dev)
        self.noise = analog.noise_source_c(analog.GR_GAUSSIAN, noise_amp, 0)
        self.add = blocks.add_cc()

        # Ramo 1: WBFM Receive (referência)
        self.wbfm_rx = analog.wfm_rcv(SAMP_RATE, DECIM)

        # Filtros passa-faixa com taps complexos (single-sideband)
        bpf_pos_taps = firdes.complex_band_pass(
            1.0, SAMP_RATE,
            max_dev / 2, 3 * max_dev / 2,
            max_dev / 4
        )
        bpf_neg_taps = firdes.complex_band_pass(
            1.0, SAMP_RATE,
            -3 * max_dev / 2, -max_dev / 2,
            max_dev / 4
        )
        self.bpf_pos = gr_filter.fir_filter_ccc(1, bpf_pos_taps)
        self.bpf_neg = gr_filter.fir_filter_ccc(1, bpf_neg_taps)

        # Detectores de envelope
        self.mag_pos = blocks.complex_to_mag(1)
        self.mag_neg = blocks.complex_to_mag(1)

        # Ramo 2: slope detector (apenas mag_pos)
        self.dc_slope = gr_filter.dc_blocker_ff(128, True)
        lpf_taps = firdes.low_pass(1.0, SAMP_RATE, 5000, 2000)
        self.lpf_slope = gr_filter.fir_filter_fff(DECIM, lpf_taps)

        # Ramo 3: discriminador balanceado
        self.sub = blocks.sub_ff(1)
        self.dc_bal = gr_filter.dc_blocker_ff(128, True)
        self.lpf_bal = gr_filter.fir_filter_fff(DECIM, lpf_taps)

        # Heads e sinks
        self.head_msg = blocks.head(gr.sizeof_float, n_audio)
        self.head_slope = blocks.head(gr.sizeof_float, n_audio)
        self.head_bal = blocks.head(gr.sizeof_float, n_audio)
        self.head_wbfm = blocks.head(gr.sizeof_float, n_audio)

        self.sink_msg = blocks.vector_sink_f()
        self.sink_slope = blocks.vector_sink_f()
        self.sink_bal = blocks.vector_sink_f()
        self.sink_wbfm = blocks.vector_sink_f()

        # Conexões
        self.connect(self.src_msg, self.head_msg, self.sink_msg)
        self.connect(self.src_msg, self.wbfm_tx)
        self.connect(self.wbfm_tx, (self.add, 0))
        self.connect(self.noise, (self.add, 1))
        # Referência
        self.connect(self.add, self.wbfm_rx, self.head_wbfm, self.sink_wbfm)
        # BPFs
        self.connect(self.add, self.bpf_pos, self.mag_pos)
        self.connect(self.add, self.bpf_neg, self.mag_neg)
        # Slope detector
        self.connect(self.mag_pos, self.dc_slope, self.lpf_slope,
                     self.head_slope, self.sink_slope)
        # Balanceado
        self.connect(self.mag_pos, (self.sub, 0))
        self.connect(self.mag_neg, (self.sub, 1))
        self.connect(self.sub, self.dc_bal, self.lpf_bal,
                     self.head_bal, self.sink_bal)


def run_case(fm_freq, max_dev, noise_amp=0.0, dur_s=0.05):
    n_audio = int(dur_s * AUDIO_RATE)
    tb = FmDemodFlowgraph(fm_freq, max_dev, noise_amp, n_audio)
    tb.run()
    return {
        'msg': np.array(tb.sink_msg.data()),
        'slope': np.array(tb.sink_slope.data()),
        'bal': np.array(tb.sink_bal.data()),
        'wbfm': np.array(tb.sink_wbfm.data()),
    }


def aligned_correlation(reference, recovered, max_lag=400):
    r = reference - reference.mean()
    g = recovered - recovered.mean()
    if np.std(g) < 1e-12 or np.std(r) < 1e-12:
        return 0.0, 0
    r_n = r / np.std(r)
    g_n = g / np.std(g)
    n = min(len(r_n), len(g_n))
    r_n = r_n[:n]
    g_n = g_n[:n]
    xc = np.correlate(g_n, r_n, mode='full') / n
    center = n - 1
    lo = max(0, center - max_lag)
    hi = min(len(xc), center + max_lag + 1)
    seg = xc[lo:hi]
    idx = int(np.argmax(np.abs(seg)))
    delay = (lo + idx) - center
    if delay >= 0:
        a = r_n[: n - delay]
        b = g_n[delay:n]
    else:
        a = r_n[-delay:n]
        b = g_n[: n + delay]
    margin = 100
    if len(a) > 2 * margin:
        a = a[margin:-margin]
        b = b[margin:-margin]
    if len(a) < 10:
        return 0.0, delay
    return float(np.corrcoef(a, b)[0, 1]), int(delay)


def thd(sig, fs, fund_freq, n_harmonics=5):
    """Total Harmonic Distortion via FFT."""
    n_fft = len(sig)
    spec = np.abs(np.fft.rfft(sig - sig.mean()))
    freqs = np.fft.rfftfreq(n_fft, 1.0 / fs)
    df = freqs[1]

    def amp_at(f):
        idx = int(round(f / df))
        if idx >= len(spec):
            return 0.0
        lo = max(0, idx - 3)
        hi = min(len(spec), idx + 4)
        return spec[lo:hi].max()

    fund = amp_at(fund_freq)
    if fund < 1e-12:
        return float('nan')
    harmonics = sum(amp_at((k + 2) * fund_freq) ** 2 for k in range(n_harmonics))
    return float(np.sqrt(harmonics) / fund)


def main():
    print("=" * 60)
    print("Verificação GNU Radio -- Prática 06")
    print("=" * 60)

    # Caso de referência: sem ruído
    fm = 1_000
    df = 25_000
    out = run_case(fm_freq=fm, max_dev=df, noise_amp=0.0, dur_s=0.1)

    print(f"\nParâmetros: fm = {fm} Hz, Δf = {df} Hz, β = {df/fm:.1f}")
    print(f"Duração: 100 ms ({len(out['msg'])} amostras de áudio)")

    print("\n[1] Fidelidade (correlação alinhada com a mensagem original):")
    for name, key in [('Slope detector  ', 'slope'),
                      ('Discrim. balanc.', 'bal'),
                      ('WBFM Receive    ', 'wbfm')]:
        rho, delay = aligned_correlation(out['msg'], out[key])
        print(f"  {name}: |ρ| = {abs(rho):.4f}  (atraso = {delay:>4} amostras)")

    print("\n[2] Distorção harmônica total (THD) na saída:")
    for name, key in [('Slope detector  ', 'slope'),
                      ('Discrim. balanc.', 'bal'),
                      ('WBFM Receive    ', 'wbfm')]:
        d = thd(out[key], AUDIO_RATE, fm)
        print(f"  {name}: THD = {d * 100:.2f} %")

    print("\n[3] Robustez ao ruído (|ρ| em função de noise_amp):")
    print(f"  {'noise_amp':>10}  {'slope':>8}  {'bal':>8}  {'wbfm':>8}")
    print("  " + "-" * 40)
    amps = [0.0, 0.02, 0.05, 0.1, 0.2, 0.5, 1.0]
    rho_history = {'slope': [], 'bal': [], 'wbfm': []}
    for amp in amps:
        out_n = run_case(fm_freq=fm, max_dev=df, noise_amp=amp, dur_s=0.1)
        row = []
        for key in ['slope', 'bal', 'wbfm']:
            rho, _ = aligned_correlation(out_n['msg'], out_n[key])
            rho_history[key].append(abs(rho))
            row.append(abs(rho))
        print(f"  {amp:>10.2f}  {row[0]:>8.3f}  {row[1]:>8.3f}  {row[2]:>8.3f}")

    # ============================================================
    # FIGURA
    # ============================================================
    fig, axes = plt.subplots(2, 2, figsize=(14, 9), constrained_layout=True)

    # 1. Formas de onda no tempo, sem ruído
    ax = axes[0, 0]
    n_show = int(0.005 * AUDIO_RATE)  # 5 ms
    skip = 200
    t_ms = np.arange(n_show) / AUDIO_RATE * 1e3
    msg = out['msg'][skip:skip + n_show]
    ax.plot(t_ms, msg, 'k-', lw=1.6, label='Mensagem original', alpha=0.85)
    for label, key, color, ls in [
        ('Slope detector', 'slope', 'C0', '--'),
        ('Discrim. balanc.', 'bal', 'C1', '-.'),
        ('WBFM Receive', 'wbfm', 'C2', ':'),
    ]:
        rho, delay = aligned_correlation(out['msg'], out[key])
        d = out[key][skip + delay: skip + delay + n_show]
        d_n = (d - d.mean()) / (np.std(d) + 1e-12) * np.std(msg)
        if rho < 0:
            d_n = -d_n
        ax.plot(t_ms, d_n, color=color, ls=ls, lw=1.3, label=label, alpha=0.95)
    ax.set_title('1 -- Comparação no tempo (sem ruído, β=25, normalizado)',
                 fontweight='bold')
    ax.set_xlabel('Tempo (ms)')
    ax.set_ylabel('Amplitude')
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

    # 2. Espectro do sinal recuperado (slope, balanced, WBFM)
    ax = axes[0, 1]
    n_fft = 2 ** 14
    fr = np.fft.rfftfreq(n_fft, 1.0 / AUDIO_RATE)
    for sig, label, color, ls in [
        (out['msg'], 'Mensagem', 'k', '-'),
        (out['slope'], 'Slope', 'C0', '--'),
        (out['bal'], 'Balanc.', 'C1', '-.'),
        (out['wbfm'], 'WBFM Rx', 'C2', ':'),
    ]:
        s = sig - sig.mean()
        spec = np.abs(np.fft.rfft(s, n=n_fft))
        spec_db = 20 * np.log10(np.maximum(spec / spec.max(), 1e-6))
        ax.plot(fr / 1e3, spec_db, color=color, ls=ls, lw=1.2,
                label=label, alpha=0.9)
    ax.set_xlim(0, 12)
    ax.set_ylim(-100, 5)
    ax.set_title('2 -- Espectro normalizado das saídas (sem ruído)',
                 fontweight='bold')
    ax.set_xlabel('Frequência (kHz)')
    ax.set_ylabel('Magnitude (dB rel. ao pico)')
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

    # 3. Robustez ao ruído: |ρ| vs noise_amp
    ax = axes[1, 0]
    for label, key, color, marker in [
        ('Slope detector', 'slope', 'C0', 'o'),
        ('Discrim. balanc.', 'bal', 'C1', 's'),
        ('WBFM Receive', 'wbfm', 'C2', '^'),
    ]:
        ax.plot(amps, rho_history[key], color=color, marker=marker,
                lw=1.8, ms=8, label=label)
    ax.set_xlabel('noise\\_amp')
    ax.set_ylabel('|ρ| alinhada')
    ax.set_title('3 -- Robustez ao ruído (β=25)', fontweight='bold')
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3)
    ax.set_ylim(0.0, 1.05)
    ax.set_xscale('log')
    ax.set_xticks([0.02, 0.05, 0.1, 0.2, 0.5, 1.0])
    ax.get_xaxis().set_major_formatter(plt.matplotlib.ticker.ScalarFormatter())

    # 4. Resposta dos filtros bpf_pos e bpf_neg
    ax = axes[1, 1]
    bpf_pos_taps = firdes.complex_band_pass(
        1.0, SAMP_RATE, df / 2, 3 * df / 2, df / 4
    )
    bpf_neg_taps = firdes.complex_band_pass(
        1.0, SAMP_RATE, -3 * df / 2, -df / 2, df / 4
    )
    n_freq = 4096
    f_axis = np.linspace(-SAMP_RATE / 2, SAMP_RATE / 2, n_freq)
    H_pos = np.zeros(n_freq, dtype=complex)
    H_neg = np.zeros(n_freq, dtype=complex)
    for i, f in enumerate(f_axis):
        z = np.exp(-1j * 2 * np.pi * f / SAMP_RATE * np.arange(len(bpf_pos_taps)))
        H_pos[i] = np.sum(np.array(bpf_pos_taps) * z)
        z = np.exp(-1j * 2 * np.pi * f / SAMP_RATE * np.arange(len(bpf_neg_taps)))
        H_neg[i] = np.sum(np.array(bpf_neg_taps) * z)
    H_pos_db = 20 * np.log10(np.abs(H_pos) + 1e-9)
    H_neg_db = 20 * np.log10(np.abs(H_neg) + 1e-9)
    ax.plot(f_axis / 1e3, H_pos_db, 'C0', lw=1.6, label='bpf_pos (+Δf)')
    ax.plot(f_axis / 1e3, H_neg_db, 'C1', lw=1.6, label='bpf_neg (-Δf)')
    ax.axvline(df / 1e3, color='C0', ls=':', alpha=0.5)
    ax.axvline(-df / 1e3, color='C1', ls=':', alpha=0.5)
    ax.set_xlim(-60, 60)
    ax.set_ylim(-80, 10)
    ax.set_title('4 -- Resposta dos filtros de inclinação', fontweight='bold')
    ax.set_xlabel('Frequência (kHz)')
    ax.set_ylabel('|H(f)| (dB)')
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3)

    fig.suptitle('Prática 06: verificação via GNU Radio',
                 fontsize=13, fontweight='bold')
    out_png = 'verificacao_gnuradio.png'
    fig.savefig(out_png, dpi=160, bbox_inches='tight')
    print(f"\nFigura salva: {out_png}")


if __name__ == '__main__':
    main()
