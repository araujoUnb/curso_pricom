# Conferência rápida dos dados gravados por rodar.py
import numpy as np
D = "dados/"
f32 = lambda n: np.fromfile(D + n, dtype=np.float32)
def tom(x, fs, f):
    t = np.arange(len(x)) / fs; w = np.hanning(len(x))
    return 2 * abs(np.sum(x * w * np.exp(-2j*np.pi*f*t))) / np.sum(w)
fs = 192000
c_tx = f32("tx_composto.f32")[2000:2000+20000]
c_rx = f32("rx_reamostra_composto.f32")[1000:]
for nome, x in [("tx", c_tx), ("rx", c_rx)]:
    print(nome, "composto:", {f: round(tom(x, fs, f), 4) for f in [1000, 3000, 19000, 37000, 39000, 35000, 41000]})
for suf in ["", "_fi260"]:
  L = f32(f"rx_audio_l{suf}.f32")[400:]; R = f32(f"rx_audio_r{suf}.f32")[400:]
  for nome, x in [("L"+suf, L), ("R"+suf, R)]:
    a1, a3 = tom(x, 48000, 1000), tom(x, 48000, 3000)
    print(nome, "1k", round(a1, 4), "3k", round(a3, 4), "separação dB", round(20*np.log10(max(a1, a3)/min(a1, a3)), 1))
for suf in ["", "_lo+30000", "_lo-30000"]:
    d = f32(f"rx_discriminador{suf}.f32")[2000:]
    print("discriminador", suf or "lo ok", "média x75k =", round(float(d.mean()*75000), 0), "Hz")
fi = f32("rx_amp_fi.f32"); lim = f32("rx_limitador_filtro.f32")
from numpy.lib.stride_tricks import sliding_window_view as sw
env = lambda x: sw(np.abs(x[100000:]), 600)[::600].max(axis=1)
e1, e2 = env(fi), env(lim)
print("envoltória FI: min/max", round(e1.min(), 3), round(e1.max(), 3), "razão", round(e1.max()/e1.min(), 2))
print("após limitador: min/max", round(e2.min(), 3), round(e2.max(), 3), "razão", round(e2.max()/e2.min(), 3))
