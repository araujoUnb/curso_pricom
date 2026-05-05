"""
Verificação via GNU Radio -- Prática 05 (Parte I)
Roda o flowgraph equivalente ao pratica_05_fm.grc de forma headless,
captura sinais reais via vector_sink e gera figura de verificação.
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


class FmFlowgraph(gr.top_block):
    """Replica pratica_05_fm.grc: WBFM Transmit + ruído + WBFM Receive."""

    def __init__(self, fm_freq, max_dev, noise_amp, n_audio):
        gr.top_block.__init__(self)
        n_quad = n_audio * DECIM

        self.src_msg = analog.sig_source_f(
            AUDIO_RATE, analog.GR_COS_WAVE, fm_freq, 1.0
        )
        self.wbfm_tx = analog.wfm_tx(AUDIO_RATE, SAMP_RATE, tau=75e-6,
                                     max_dev=max_dev)
        self.noise = analog.noise_source_c(analog.GR_GAUSSIAN, noise_amp, 0)
        self.add = blocks.add_cc()
        self.wbfm_rx = analog.wfm_rcv(SAMP_RATE, DECIM)

        self.head_msg = blocks.head(gr.sizeof_float, n_audio)
        self.head_demod = blocks.head(gr.sizeof_float, n_audio)
        self.head_fm = blocks.head(gr.sizeof_gr_complex, n_quad)

        self.sink_msg = blocks.vector_sink_f()
        self.sink_demod = blocks.vector_sink_f()
        self.sink_fm = blocks.vector_sink_c()

        self.connect(self.src_msg, self.head_msg, self.sink_msg)
        self.connect(self.src_msg, self.wbfm_tx)
        self.connect(self.wbfm_tx, (self.add, 0))
        self.connect(self.noise, (self.add, 1))
        self.connect(self.add, self.head_fm, self.sink_fm)
        self.connect(self.add, self.wbfm_rx, self.head_demod, self.sink_demod)


def run_case(fm_freq, max_dev, noise_amp=0.0, dur_s=0.05):
    n_audio = int(dur_s * AUDIO_RATE)
    tb = FmFlowgraph(fm_freq, max_dev, noise_amp, n_audio)
    tb.run()
    return (
        np.array(tb.sink_msg.data()),
        np.array(tb.sink_demod.data()),
        np.array(tb.sink_fm.data()),
    )


def aligned_correlation(reference, recovered, max_lag=400):
    """Correlação após alinhar pelo melhor atraso e normalizar amplitude.

    Considera tanto correlação positiva quanto negativa (sinal pode vir
    invertido devido ao discriminador), retornando |ρ| no melhor lag.
    """
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
    delay = (lo + idx) - center  # delay > 0: recovered is delayed wrt reference
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
    rho = float(np.corrcoef(a, b)[0, 1])
    return rho, int(delay)


def fft_db(sig, fs, n_fft=None):
    if n_fft is None:
        n_fft = len(sig)
    seg = sig[:n_fft]
    spec = np.fft.fftshift(np.fft.fft(seg, n=n_fft))
    freqs = np.fft.fftshift(np.fft.fftfreq(n_fft, d=1.0 / fs))
    mag = np.abs(spec) / n_fft
    return freqs, 20 * np.log10(np.maximum(mag, 1e-10))


def measure_bw_db(sig, fs, threshold_db=-20, n_fft=8192):
    freqs, mag_db = fft_db(sig, fs, n_fft=n_fft)
    cutoff = mag_db.max() + threshold_db
    mask = mag_db > cutoff
    if not mask.any():
        return 0.0
    return float(freqs[mask].max() - freqs[mask].min())


def main():
    print("=" * 60)
    print("Verificação GNU Radio -- Prática 05 (Parte I)")
    print("=" * 60)

    # Verificação numérica de Carson
    print("\n[1] Regra de Carson (BW medida em -20 dB):")
    cases = [
        (2_000, 1_000),
        (2_000, 2_000),
        (2_000, 5_000),
        (2_000, 10_000),
        (1_000, 5_000),
        (4_000, 20_000),
    ]
    print(f"{'fm':>6}  {'Δf':>8}  {'β':>5}  {'BT-Carson':>10}  {'BT-medida':>10}  {'erro%':>7}")
    print("-" * 60)
    carson_results = []
    for fm, df in cases:
        beta = df / fm
        bt_carson = 2 * (df + fm)
        _, _, fm_sig = run_case(fm_freq=fm, max_dev=df, dur_s=0.1)
        bt_meas = measure_bw_db(fm_sig, SAMP_RATE, threshold_db=-20)
        err = (bt_meas - bt_carson) / bt_carson * 100
        carson_results.append((fm, df, beta, bt_carson, bt_meas, err))
        print(f"{fm:>6}  {df:>8}  {beta:>5.2f}  {bt_carson:>10.0f}  {bt_meas:>10.0f}  {err:>+7.1f}")

    # Verificação de fidelidade
    print("\n[2] Fidelidade da demodulação (sem ruído):")
    for label, df in [('NBFM β=0.5', 1_000),
                      ('FM   β=1.0', 2_000),
                      ('WBFM β=2.5', 5_000),
                      ('WBFM β=5.0', 10_000)]:
        msg, demod, _ = run_case(fm_freq=2_000, max_dev=df)
        rho, delay = aligned_correlation(msg, demod)
        print(f"  {label}: ρ = {rho:+.4f}  (atraso = {delay} amostras)")

    # Robustez ao ruído
    print("\n[3] Robustez ao ruído (NBFM β=0.5 vs WBFM β=10):")
    print(f"  {'noise_amp':>10}  {'ρ NBFM':>10}  {'ρ WBFM':>10}")
    print("  " + "-" * 36)
    amps = [0.0, 0.05, 0.1, 0.2, 0.3, 0.5]
    rho_nbfm_pts = []
    rho_wbfm_pts = []
    for amp in amps:
        msg, demod, _ = run_case(fm_freq=2_000, max_dev=1_000, noise_amp=amp)
        rho_n, _ = aligned_correlation(msg, demod)
        msg, demod, _ = run_case(fm_freq=2_000, max_dev=20_000, noise_amp=amp)
        rho_w, _ = aligned_correlation(msg, demod)
        rho_nbfm_pts.append(rho_n)
        rho_wbfm_pts.append(rho_w)
        print(f"  {amp:>10.2f}  {rho_n:>+10.3f}  {rho_w:>+10.3f}")

    # ============================================================
    # FIGURA
    # ============================================================
    fig, axes = plt.subplots(2, 2, figsize=(14, 9), constrained_layout=True)

    ax = axes[0, 0]
    for fm, df, label, color, ls in [
        (2_000, 1_000, 'NBFM β=0.5', 'C0', '-'),
        (2_000, 5_000, 'FM β=2.5', 'C1', '--'),
        (2_000, 10_000, 'WBFM β=5', 'C2', '-.'),
        (2_000, 20_000, 'WBFM β=10', 'C3', ':'),
    ]:
        _, _, sig = run_case(fm_freq=fm, max_dev=df, dur_s=0.1)
        f, m = fft_db(sig, SAMP_RATE, n_fft=8192)
        mask = (f >= -60_000) & (f <= 60_000)
        ax.plot(f[mask] / 1e3, m[mask], color=color, ls=ls, lw=1.2, label=label)
    ax.set_xlim(-50, 50)
    ax.set_ylim(-90, -20)
    ax.set_title('1 -- Espectro FM via GNU Radio (efeito de β)', fontweight='bold')
    ax.set_xlabel('Frequência (kHz)')
    ax.set_ylabel('Magnitude (dB)')
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

    ax = axes[0, 1]
    betas = [r[2] for r in carson_results]
    bt_c = [r[3] / 1e3 for r in carson_results]
    bt_m = [r[4] / 1e3 for r in carson_results]
    idx = np.argsort(betas)
    betas = np.array(betas)[idx]
    bt_c = np.array(bt_c)[idx]
    bt_m = np.array(bt_m)[idx]
    ax.plot(betas, bt_c, 'o-', label='Regra de Carson', lw=2, ms=8)
    ax.plot(betas, bt_m, 's--', label='Medida em -20 dB', lw=1.5, ms=8)
    ax.set_title('2 -- Carson: previsto vs medido', fontweight='bold')
    ax.set_xlabel('Índice β = Δf/fm')
    ax.set_ylabel('Largura de banda (kHz)')
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3)

    ax = axes[1, 0]
    msg, demod, _ = run_case(fm_freq=2_000, max_dev=10_000)
    _, delay = aligned_correlation(msg, demod)
    n_show = int(0.005 * AUDIO_RATE)
    skip = max(50, delay)
    t_ms = np.arange(n_show) / AUDIO_RATE * 1e3
    ax.plot(t_ms, msg[skip:skip + n_show], 'k-', lw=1.6,
            label='Mensagem original', alpha=0.85)
    d_seg = demod[skip + delay: skip + delay + n_show]
    if np.std(d_seg) > 1e-9:
        d_norm = (d_seg - d_seg.mean()) / np.std(d_seg) * np.std(msg[skip:skip + n_show])
    else:
        d_norm = d_seg
    ax.plot(t_ms, d_norm, 'C1--', lw=1.2,
            label='WBFM Receive (alinhado, normalizado)', alpha=0.95)
    ax.set_title('3 -- WBFM Receive: recuperação da mensagem (β=5)',
                 fontweight='bold')
    ax.set_xlabel('Tempo (ms)')
    ax.set_ylabel('Amplitude')
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

    ax = axes[1, 1]
    ax.plot(amps, np.abs(rho_nbfm_pts), 'o-', label='NBFM β=0.5', lw=1.8, ms=8)
    ax.plot(amps, np.abs(rho_wbfm_pts), 's-', label='WBFM β=10', lw=1.8, ms=8)
    ax.set_xlabel('noise\\_amp')
    ax.set_ylabel('|ρ| alinhada (mensagem, demod)')
    ax.set_title('4 -- Robustez ao ruído: NBFM vs WBFM', fontweight='bold')
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3)
    ax.set_ylim(0.0, 1.05)

    fig.suptitle('Prática 05 -- Parte I: verificação via GNU Radio',
                 fontsize=13, fontweight='bold')
    out = 'verificacao_gnuradio.png'
    fig.savefig(out, dpi=160, bbox_inches='tight')
    print(f"\nFigura salva: {out}")


if __name__ == '__main__':
    main()
