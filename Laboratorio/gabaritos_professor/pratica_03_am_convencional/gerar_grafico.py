"""
Gráfico esperado -- Prática 03: AM Convencional (DSB+C)
Gera 'grafico_esperado.png' com quatro subplots:
  1. AM no tempo mu=0.5 (submodulação) com envoltória
  2. AM no tempo mu=1.3 (sobremodulação) com zona invertida
  3. Espectro para mu=0.5, 1.0, 1.3
  4. Detector de envoltória simulado para os três casos
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

# ------------------------------------------------------------------
fs = 48_000;  fc = 10_000;  fm = 1_000;  Ac = 1.0
N = int(0.010 * fs)       # 10 ms
t = np.arange(N) / fs
msg_n = np.cos(2 * np.pi * fm * t)   # mensagem normalizada


def am_signal(mu):
    return Ac * (1 + mu * msg_n) * np.cos(2 * np.pi * fc * t)


def envelope_detect(s, bw=0.02):
    env = np.abs(s)
    out = np.zeros_like(env)
    out[0] = env[0]
    for i in range(1, len(env)):
        out[i] = (1 - bw) * out[i-1] + bw * env[i]
    return out


def fft_onesided(sig, fs_in):
    spec = np.fft.rfft(sig)
    freqs = np.fft.rfftfreq(len(sig), d=1 / fs_in)
    mag = np.abs(spec) / (len(sig) / 2)
    return freqs, mag


mu_vals = [0.5, 1.0, 1.3]

fig = plt.figure(figsize=(14, 9), constrained_layout=True)
gs = gridspec.GridSpec(2, 2, figure=fig)

# 1. AM no tempo mu=0.5
ax1 = fig.add_subplot(gs[0, 0])
s05 = am_signal(0.5)
ax1.plot(t * 1e3, s05, lw=1.1, label='AM $\mu=0.5$')
ax1.plot(t * 1e3, Ac * (1 + 0.5 * msg_n), 'r--', lw=1.5, label='Envoltória superior')
ax1.plot(t * 1e3, -Ac * (1 + 0.5 * msg_n), 'r--', lw=1.5)
ax1.axhline(0, color='gray', lw=0.5)
ax1.set_title('1 – AM no tempo: $\mu = 0.5$ (submodulação)', fontweight='bold')
ax1.set_xlabel('Tempo (ms)'); ax1.set_ylabel('Amplitude')
ax1.legend(fontsize=9); ax1.grid(True, alpha=0.3)

# 2. AM no tempo mu=1.3
ax2 = fig.add_subplot(gs[1, 0])
s13 = am_signal(1.3)
ax2.plot(t * 1e3, s13, lw=1.1, label='AM $\mu=1.3$')
ax2.plot(t * 1e3, Ac * (1 + 1.3 * msg_n), 'r--', lw=1.2, alpha=0.7, label='Envoltória (teórica)')
ax2.axhline(0, color='gray', lw=0.8, ls=':')
mask = (1 + 1.3 * msg_n < 0)
ax2.fill_between(t * 1e3, s13, 0, where=mask, alpha=0.25, color='red', label='Zona invertida')
ax2.set_title('2 – AM no tempo: $\mu = 1.3$ (sobremodulação)', fontweight='bold')
ax2.set_xlabel('Tempo (ms)'); ax2.set_ylabel('Amplitude')
ax2.legend(fontsize=9); ax2.grid(True, alpha=0.3)

# 3. Espectro para diferentes mu
ax3 = fig.add_subplot(gs[0, 1])
for mu_i, color in zip(mu_vals, ['C0', 'C1', 'C2']):
    fi, mi = fft_onesided(am_signal(mu_i), fs)
    ax3.plot(fi / 1e3, mi, color=color, lw=1.4, label=f'$\mu = {mu_i}$')
ax3.axvline(fc / 1e3, color='gray', ls='--', lw=0.8, alpha=0.5, label='$f_c$')
ax3.axvline((fc - fm) / 1e3, color='gray', ls=':', lw=0.8, alpha=0.5)
ax3.axvline((fc + fm) / 1e3, color='gray', ls=':', lw=0.8, alpha=0.5, label='$f_c\\pm f_m$')
ax3.set_xlim(7, 13)
ax3.set_title('3 – Espectro AM: portadora + bandas laterais', fontweight='bold')
ax3.set_xlabel('Frequência (kHz)'); ax3.set_ylabel('Magnitude')
ax3.legend(fontsize=9); ax3.grid(True, alpha=0.3)

# 4. Detector de envoltória
ax4 = fig.add_subplot(gs[1, 1])
for mu_i, color, ls in [(0.5, 'C0', '-'), (1.0, 'C1', '--'), (1.3, 'C2', '-.')]:
    env_i = envelope_detect(am_signal(mu_i))
    ax4.plot(t * 1e3, env_i, color=color, lw=1.5, ls=ls, label=f'Det. envoltória $\mu={mu_i}$')
ax4.plot(t * 1e3, Ac + 0.5 * msg_n, 'k:', lw=1.0, alpha=0.5, label='Envoltória ideal $\mu=0.5$')
ax4.set_title('4 – Detector de envoltória: resultado esperado', fontweight='bold')
ax4.set_xlabel('Tempo (ms)'); ax4.set_ylabel('Amplitude')
ax4.legend(fontsize=8); ax4.grid(True, alpha=0.3)

fig.suptitle('Prática 03 – AM Convencional (DSB+C): gráfico esperado',
             fontsize=13, fontweight='bold')
fig.savefig('grafico_esperado.png', dpi=180, bbox_inches='tight')
print('Salvo: grafico_esperado.png')
