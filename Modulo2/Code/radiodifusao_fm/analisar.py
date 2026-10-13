# Lê dados/ (gravados por rodar.py) e gera radiodifusao.json com os espectros e
# medidas de cada etapa, já reduzidos para os gráficos dos slides.
import json
import numpy as np
from scipy import signal

D = "dados/"
f32 = lambda n: np.fromfile(D + n, dtype=np.float32)
R = lambda v, n=4: float(np.round(v, n))


def psd(x, fs, nper, f0, f1, npts, complexo=False):
    f, p = signal.welch(x, fs, window="hann", nperseg=nper, return_onesided=not complexo, scaling="spectrum")
    if complexo:
        f, p = np.fft.fftshift(f), np.fft.fftshift(p)
    sel = (f >= f0) & (f <= f1); f, p = f[sel], p[sel]
    grade = np.linspace(f0, f1, npts + 1)
    idx = np.clip(np.digitize(f, grade) - 1, 0, npts - 1)
    m = np.full(npts, 1e-30)
    np.maximum.at(m, idx, p)
    db = 10 * np.log10(m)
    return [R(v, 1) for v in np.maximum(db - db.max(), -120)]


def tom(x, fs, f):
    t = np.arange(len(x)) / fs; w = np.hanning(len(x))
    return 2 * abs(np.sum(x * w * np.exp(-2j * np.pi * f * t))) / np.sum(w)


out = {}
fsc = 192000
# ---- transmissor: 0 a 60 kHz, 600 pontos
tx = {n: f32(f"tx_{n}.f32")[4000:4000 + 65536] for n in ["soma_lr", "dif_lr", "preenf_soma", "preenf_dif", "dobrador", "dobrador_dc", "dsb_sc", "composto"]}
out["tx"] = {n: psd(x, fsc, 32768, 0, 60e3, 600) for n, x in tx.items()}
out["tx"]["ganho_preenf"] = {str(f): R(tom(tx["preenf_soma"], fsc, f) / tom(tx["soma_lr"], fsc, f), 3) for f in [1000, 3000]}
out["tx"]["comp_tempo"] = [R(v, 3) for v in tx["composto"][:960]]
fm = np.fromfile(D + "tx_fm.c64", dtype=np.complex64)[20000:20000 + 262144]
out["tx"]["fm"] = psd(fm, 960e3, 16384, -250e3, 250e3, 500, complexo=True)
f, p = signal.welch(fm, 960e3, nperseg=16384, return_onesided=False); f, p = np.fft.fftshift(f), np.fft.fftshift(p)
c = np.cumsum(p) / p.sum()
out["tx"]["b98"] = R((f[np.searchsorted(c, 0.99)] - f[np.searchsorted(c, 0.01)]) / 1e3, 1)

# ---- antena e RF: 80 a 130 MHz
frf = 480e6
ant = np.fromfile("antena.f32", dtype=np.float32)
rf = f32("rx_amp_rf.f32")
mix = f32("rx_misturador.f32")
out["rf"] = {"antena": psd(ant, frf, 65536, 80e6, 130e6, 1000), "amp_rf": psd(rf, frf, 65536, 80e6, 130e6, 1000)}
out["rf"]["mix"] = psd(mix, frf, 65536, 0, 240e6, 960)
# sem o amplificador de RF: a mesma mistura feita direto sobre a antena
n = len(ant); t = np.arange(n) / frf
lo = np.cos(2 * np.pi * (97.9e6 + 10.7e6) * t).astype(np.float32)
mix_sem = ant * lo
del t, lo
out["rf"]["fi_com"] = psd(mix, frf, 262144, 9.7e6, 11.7e6, 800)
out["rf"]["fi_sem"] = psd(mix_sem, frf, 262144, 9.7e6, 11.7e6, 800)
del mix_sem

# ---- FI, limitador
fif = 60e6
fi = f32("rx_amp_fi.f32"); lim_q = f32("rx_limitador_dc.f32"); lim = f32("rx_limitador_filtro.f32")
out["fi"] = {"fi": psd(fi, fif, 65536, 10.2e6, 11.2e6, 500), "lim_q": psd(lim_q, fif, 65536, 0, 30e6, 600), "lim": psd(lim, fif, 65536, 10.2e6, 11.2e6, 500)}
from numpy.lib.stride_tricks import sliding_window_view as sw
blk = 6000
env = lambda x: sw(np.abs(x[:len(x) // blk * blk]), blk)[::blk].max(axis=1)
e1, e2 = env(fi), env(lim)
out["fi"]["env_fi"] = [R(v, 3) for v in e1]; out["fi"]["env_lim"] = [R(v, 3) for v in e2]
out["fi"]["env_dt_ms"] = blk / fif * 1e3
k = 300000
out["fi"]["tr_fi"] = [R(v, 3) for v in fi[k:k + 120]]; out["fi"]["tr_q"] = [R(v, 3) for v in lim_q[k:k + 120]]; out["fi"]["tr_lim"] = [R(v, 3) for v in lim[k:k + 120]]

# ---- composto recuperado e decodificador
crx = f32("rx_reamostra_composto.f32")[1500:]
out["dec"] = {"comp_rx": psd(crx, fsc, 4096, 0, 60e3, 600), "comp_tx": psd(tx["composto"], fsc, 4096, 0, 60e3, 600)}
for nm in ["filtro_soma", "filtro_dif", "filtro_38k"]:
    out["dec"][nm] = psd(f32(f"rx_{nm}.f32")[1500:], fsc, 4096, 0, 60e3, 600)
med = {}
for f in [1000, 3000, 19000, 35000, 37000, 39000, 41000]:
    med[str(f)] = {"tx": R(tom(tx["composto"][:len(crx)], fsc, f)), "rx": R(tom(crx, fsc, f))}
out["dec"]["tons"] = med
sep = {}
for suf in ["", "_fi260"]:
    L = f32(f"rx_audio_l{suf}.f32")[400:]; Rr = f32(f"rx_audio_r{suf}.f32")[400:]
    sep[suf or "_fi200"] = {"L1k": R(tom(L, 48e3, 1000)), "L3k": R(tom(L, 48e3, 3000)), "R1k": R(tom(Rr, 48e3, 1000)), "R3k": R(tom(Rr, 48e3, 3000))}
out["dec"]["sep"] = sep
La = f32("rx_audio_l.f32"); Ra = f32("rx_audio_r.f32")
out["dec"]["audio_l"] = [R(v, 3) for v in La[1000:1480]]; out["dec"]["audio_r"] = [R(v, 3) for v in Ra[1000:1480]]

# ---- AFC
afc = {}
for suf, err in [("", 0), ("_lo+30000", 30000), ("_lo-30000", -30000)]:
    d = f32(f"rx_discriminador{suf}.f32")
    afc[str(err)] = {"media_hz": R(float(d[2000:].mean() * 75000), 0), "tempo": [R(v * 75, 2) for v in d[2000:2000 + 4800:8]]}
out["afc"] = afc
json.dump(out, open("radiodifusao.json", "w"), separators=(",", ":"))
print("ok", len(json.dumps(out)) // 1024, "kB", "b98", out["tx"]["b98"], "preenf", out["tx"]["ganho_preenf"], "sep", sep, "afc", {k: v["media_hz"] for k, v in afc.items()})
