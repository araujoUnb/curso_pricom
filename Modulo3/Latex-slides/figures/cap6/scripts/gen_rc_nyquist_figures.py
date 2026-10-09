#!/usr/bin/env python3
"""
Conecta o cosseno levantado ao Criterio de Nyquist.
Mostra que a borda de roll-off e anti-simetrica em torno da frequencia
de Nyquist f = 1/2T: a descida de uma replica completa a subida da
vizinha, somando exatamente T.

Saida: ../rc_nyq_1.pdf  -> espectro P(f) e a frequencia de Nyquist 1/2T
       ../rc_nyq_2.pdf  -> anti-simetria: P(1/2T-d) + P(1/2T+d) = T
       ../rc_nyq_3.pdf  -> replica vizinha sobe onde P(f) desce
       ../rc_nyq_4.pdf  -> soma das bordas = T (criterio satisfeito)

Uso: python gen_rc_nyquist_figures.py
"""

import numpy as np
import matplotlib.pyplot as plt

plt.rcParams.update({
    'font.size': 11,
    'font.family': 'serif',
    'axes.labelsize': 12,
    'axes.titlesize': 12,
    'xtick.labelsize': 10,
    'ytick.labelsize': 10,
    'figure.dpi': 150,
    'text.usetex': False,
    'axes.spines.top': False,
    'axes.spines.right': False,
    'axes.grid': True,
    'grid.alpha': 0.3,
})

UNB_BLUE  = '#003B5C'
UNB_GREEN = '#006633'
UNB_GOLD  = '#F2A900'
RED       = '#C0392B'
PURPLE    = '#8E44AD'


def rc_freq(f, T, alpha):
    P = np.zeros_like(f)
    fa = np.abs(f)
    f1 = (1 - alpha) / (2 * T)
    f2 = (1 + alpha) / (2 * T)
    flat = fa <= f1
    roll = (fa > f1) & (fa <= f2)
    P[flat] = T
    P[roll] = (T / 2.0) * (1 + np.cos((np.pi * T / alpha) * (fa[roll] - f1)))
    return P


T = 1.0
alpha = 0.5
fN = 1.0 / (2 * T)          # frequencia de Nyquist
f1 = (1 - alpha) / (2 * T)
f2 = (1 + alpha) / (2 * T)
delta = 0.6 * (alpha / (2 * T))   # ponto de exemplo na borda

f = np.linspace(-0.15 / T, 1.65 / T, 4000)
P0 = rc_freq(f, T, alpha)
P1 = rc_freq(f - 1.0 / T, T, alpha)   # replica vizinha k=1
Psum = P0 + P1


def base_axes():
    fig, ax = plt.subplots(figsize=(7.4, 3.5))
    ax.set_xlabel(r'$f$  (em unidades de $1/T$)')
    ax.set_ylabel(r'$P(f)$')
    ax.set_xlim(-0.15 / T, 1.65 / T)
    ax.set_ylim(0, 1.32 * T)
    ax.set_xticks([0, f1, fN, f2, 1/T])
    ax.set_xticklabels(['0', r'$\frac{1-\alpha}{2T}$', r'$\frac{1}{2T}$',
                        r'$\frac{1+\alpha}{2T}$', r'$\frac{1}{T}$'])
    ax.set_yticks([0, T/2, T])
    ax.set_yticklabels(['0', r'$T/2$', r'$T$'])
    ax.axvline(fN, color='0.55', ls='--', lw=1)
    return fig, ax


# ---------------------------------------------------------------------------
# 1: espectro P(f) e a frequencia de Nyquist
# ---------------------------------------------------------------------------
fig, ax = base_axes()
ax.plot(f, P0, color=UNB_BLUE, lw=2.6, label=r'$P(f)$')
ax.axvspan(f1, f2, color=UNB_GOLD, alpha=0.13)
ax.plot([fN], [T/2], 'o', color=UNB_BLUE, ms=7)
ax.annotate(r'$P\left(\frac{1}{2T}\right)=\frac{T}{2}$',
            xy=(fN, T/2), xytext=(fN + 0.18/T, 0.72*T),
            fontsize=11, arrowprops=dict(arrowstyle='->', color='0.4'))
ax.annotate('freq. de Nyquist', xy=(fN, 1.18*T), ha='center',
            color='0.4', fontsize=10)
ax.annotate('roll-off', xy=((f1+f2)/2, 0.06*T), ha='center',
            color='#9a7d00', fontsize=10)
ax.legend(loc='upper right', frameon=False)
fig.tight_layout()
fig.savefig('../rc_nyq_1.pdf', bbox_inches='tight')
plt.close(fig)

# ---------------------------------------------------------------------------
# 2: anti-simetria em torno de 1/2T
# ---------------------------------------------------------------------------
fig, ax = base_axes()
ax.plot(f, P0, color=UNB_BLUE, lw=2.6, label=r'$P(f)$')
ax.axvspan(f1, f2, color=UNB_GOLD, alpha=0.13)

fa_, fb_ = fN - delta, fN + delta
ha_ = float(rc_freq(np.array([fa_]), T, alpha)[0])
hb_ = float(rc_freq(np.array([fb_]), T, alpha)[0])
ax.axhline(T, color='0.7', ls=':', lw=1)
# pontos simetricos
ax.plot([fa_], [ha_], 'o', color=UNB_GREEN, ms=7)
ax.plot([fb_], [hb_], 'o', color=RED, ms=7)
# barras de altura mostrando soma = T
ax.vlines(fa_, 0, ha_, color=UNB_GREEN, lw=5, alpha=0.55)
ax.vlines(fb_, 0, hb_, color=RED, lw=5, alpha=0.55)
ax.annotate(r'$P\left(\frac{1}{2T}-\delta\right)$', xy=(fa_, ha_),
            xytext=(fa_ - 0.02/T, ha_ + 0.10*T), ha='right',
            color=UNB_GREEN, fontsize=10)
ax.annotate(r'$P\left(\frac{1}{2T}+\delta\right)$', xy=(fb_, hb_),
            xytext=(fb_ + 0.02/T, hb_ + 0.10*T), ha='left',
            color=RED, fontsize=10)
# seta dupla horizontal indicando simetria
ax.annotate('', xy=(fa_, 1.06*T), xytext=(fb_, 1.06*T),
            arrowprops=dict(arrowstyle='<->', color='0.4', lw=1.2))
ax.text(fN, 1.10*T, r'$P(\frac{1}{2T}-\delta)+P(\frac{1}{2T}+\delta)=T$',
        ha='center', fontsize=11, color='0.25')
ax.legend(loc='lower left', frameon=False)
fig.tight_layout()
fig.savefig('../rc_nyq_2.pdf', bbox_inches='tight')
plt.close(fig)

# ---------------------------------------------------------------------------
# 3: replica vizinha sobe onde P(f) desce
# ---------------------------------------------------------------------------
fig, ax = base_axes()
ax.plot(f, P0, color=UNB_BLUE, lw=2.6, label=r'$P(f)$')
ax.plot(f, P1, color=RED, lw=2.2, ls='--', label=r'$P(f - 1/T)$')
ax.axvspan(f1, f2, color=UNB_GOLD, alpha=0.18)
ax.annotate('desce', xy=(fN, 0.5*T), xytext=(fN - 0.16/T, 0.30*T),
            color=UNB_BLUE, fontsize=10,
            arrowprops=dict(arrowstyle='->', color=UNB_BLUE))
ax.annotate('sobe', xy=(fN, 0.5*T), xytext=(fN + 0.10/T, 0.30*T),
            color=RED, fontsize=10,
            arrowprops=dict(arrowstyle='->', color=RED))
ax.text((f1+f2)/2, 1.14*T, 'mesma faixa de transição', ha='center',
        color='#9a7d00', fontsize=10)
ax.legend(loc='upper center', frameon=False, ncol=2)
fig.tight_layout()
fig.savefig('../rc_nyq_3.pdf', bbox_inches='tight')
plt.close(fig)

# ---------------------------------------------------------------------------
# 4: soma das bordas = T (criterio satisfeito)
# ---------------------------------------------------------------------------
fig, ax = base_axes()
ax.plot(f, P0, color=UNB_BLUE, lw=1.8, alpha=0.6, label=r'$P(f)$')
ax.plot(f, P1, color=RED, lw=1.6, ls='--', alpha=0.6, label=r'$P(f - 1/T)$')
ax.plot(f, Psum, color=UNB_GREEN, lw=3.2,
        label=r'$P(f)+P(f-1/T)=T$')
ax.axvspan(f1, f2, color=UNB_GOLD, alpha=0.18)
ax.axhline(T, color=UNB_GREEN, ls=':', lw=1)
# barra empilhada num ponto da transicao mostrando azul + vermelho = T
fb_ = fN + delta
h_blue = float(rc_freq(np.array([fb_]), T, alpha)[0])
h_red = float(rc_freq(np.array([fb_ - 1.0/T]), T, alpha)[0])
ax.vlines(fb_, 0, h_blue, color=UNB_BLUE, lw=8, alpha=0.5)
ax.vlines(fb_, h_blue, h_blue + h_red, color=RED, lw=8, alpha=0.5)
ax.annotate('preenche\naté $T$', xy=(fb_, T), xytext=(fb_ + 0.12/T, 0.78*T),
            color='0.3', fontsize=9,
            arrowprops=dict(arrowstyle='->', color='0.4'))
ax.legend(loc='lower left', frameon=False, fontsize=9)
fig.tight_layout()
fig.savefig('../rc_nyq_4.pdf', bbox_inches='tight')
plt.close(fig)

print('Figuras rc_nyq_1..4.pdf geradas.')
