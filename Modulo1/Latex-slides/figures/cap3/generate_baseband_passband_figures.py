#!/usr/bin/env python3
"""
Gera figuras ilustrando a derivação passo a passo do envelope complexo
de um sinal passante.
Curso de Princípios de Comunicação - UnB.
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os

# ---------- estilo global ----------
plt.rcParams.update({
    'text.usetex': False,
    'font.size': 12,
    'axes.labelsize': 14,
    'axes.titlesize': 14,
    'xtick.labelsize': 12,
    'ytick.labelsize': 12,
    'axes.grid': True,
    'grid.linestyle': '--',
    'grid.alpha': 0.4,
    'figure.facecolor': 'white',
    'axes.facecolor': 'white',
    'savefig.facecolor': 'white',
    'savefig.bbox': 'tight',
    'savefig.dpi': 150,
})

OUTDIR = os.path.dirname(os.path.abspath(__file__))


def save(fig, name):
    base = os.path.join(OUTDIR, name)
    fig.savefig(base + '.pdf')
    fig.savefig(base + '.png', dpi=150)
    plt.close(fig)
    print(f'  -> {name}.pdf / .png')


# ---------- parâmetros do exemplo ----------
fs = 48000          # taxa de amostragem
T = 0.02            # duração (20 ms)
fc = 5000           # frequência da portadora
freqs_msg = [100, 300, 500]   # tons da mensagem m(t)

# cores consistentes
COR_ORIG = '#1f77b4'       # azul — sinal original / passante
COR_ANALITICO = '#d62728'  # vermelho — sinal analítico
COR_BB = '#2ca02c'         # verde — banda básica
COR_CINZA = '#aaaaaa'


def _gerar_sinais():
    """Gera todos os sinais usados nas figuras."""
    t = np.arange(0, T, 1 / fs)
    N = len(t)

    # Mensagem (banda básica real)
    m = sum(np.cos(2 * np.pi * f * t) for f in freqs_msg)

    # Sinal passante
    s = m * np.cos(2 * np.pi * fc * t)

    # FFT bilateral
    freqs = np.fft.fftshift(np.fft.fftfreq(N, 1 / fs))
    S = np.fft.fftshift(np.fft.fft(s)) / N

    # Sinal analítico: zerar freqs negativas, dobrar positivas
    S_one = np.fft.fft(s) / N
    Z_one = np.zeros_like(S_one)
    # f=0 mantém, f>0 dobra, f<0 zera
    Z_one[0] = S_one[0]
    Z_one[1:N // 2] = 2 * S_one[1:N // 2]
    if N % 2 == 0:
        Z_one[N // 2] = S_one[N // 2]  # Nyquist
    Z = np.fft.fftshift(Z_one)

    # Envelope complexo: deslocar analítico para banda básica
    z_t = np.fft.ifft(Z_one * N)  # voltar ao tempo (desfaz /N)
    s_tilde_t = z_t * np.exp(-1j * 2 * np.pi * fc * t)
    S_tilde_one = np.fft.fft(s_tilde_t) / N
    S_tilde = np.fft.fftshift(S_tilde_one)

    return dict(t=t, N=N, freqs=freqs, S=S, Z=Z,
                S_tilde=S_tilde, s=s, m=m, z_t=z_t, s_tilde_t=s_tilde_t)


# ====================================================================
# Figura 1 — Espectro do sinal passante
# ====================================================================
def fig_passo1_espectro():
    print('Gerando: passband_passo1_espectro')
    d = _gerar_sinais()
    freqs_hz = d['freqs'] / 1000  # em kHz
    S_mag = np.abs(d['S'])

    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(freqs_hz, S_mag, color=COR_ORIG, linewidth=1.5)
    ax.fill_between(freqs_hz, S_mag, alpha=0.25, color=COR_ORIG)

    ax.set_xlim(-8, 8)
    ax.set_xlabel('Frequência (kHz)')
    ax.set_ylabel('|S(f)|')
    ax.set_title('Passo 1: Espectro do Sinal Passante S(f)')

    # Anotações de fc e -fc
    ymax = S_mag.max() * 1.15
    ax.annotate(r'$f_c$', xy=(fc / 1000, S_mag.max()), fontsize=13,
                xytext=(fc / 1000 + 0.4, S_mag.max() * 0.9),
                arrowprops=dict(arrowstyle='->', color='k'),
                fontweight='bold')
    ax.annotate(r'$-f_c$', xy=(-fc / 1000, S_mag.max()), fontsize=13,
                xytext=(-fc / 1000 - 1.2, S_mag.max() * 0.9),
                arrowprops=dict(arrowstyle='->', color='k'),
                fontweight='bold')

    # Largura de faixa W
    W = max(freqs_msg) / 1000  # em kHz
    ax.annotate('', xy=(fc / 1000 - W, ymax * 0.75),
                xytext=(fc / 1000 + W, ymax * 0.75),
                arrowprops=dict(arrowstyle='<->', color='purple', lw=1.5))
    ax.text(fc / 1000, ymax * 0.82, f'W = {max(freqs_msg)} Hz',
            ha='center', fontsize=12, color='purple', fontweight='bold')

    ax.set_ylim(0, ymax)
    fig.tight_layout()
    save(fig, 'passband_passo1_espectro')


# ====================================================================
# Figura 2 — Sinal analítico (manter apenas freqs positivas)
# ====================================================================
def fig_passo2_analitico():
    print('Gerando: passband_passo2_analitico')
    d = _gerar_sinais()
    freqs_hz = d['freqs'] / 1000
    S_mag = np.abs(d['S'])
    Z_mag = np.abs(d['Z'])

    fig, axes = plt.subplots(2, 1, figsize=(10, 6), sharex=True)

    # --- Topo: S(f) ---
    axes[0].plot(freqs_hz, S_mag, color=COR_ORIG, linewidth=1.5)
    axes[0].fill_between(freqs_hz, S_mag, alpha=0.25, color=COR_ORIG)
    axes[0].set_ylabel('|S(f)|')
    axes[0].set_title('Passo 2: Manter Apenas Frequências Positivas')
    axes[0].set_xlim(-8, 8)

    # --- Baixo: Z(f) ---
    axes[1].plot(freqs_hz, Z_mag, color=COR_ANALITICO, linewidth=1.5)
    axes[1].fill_between(freqs_hz, Z_mag, alpha=0.25, color=COR_ANALITICO)
    axes[1].set_ylabel('|Z(f)|')
    axes[1].set_xlabel('Frequência (kHz)')

    # Sombrear parte negativa removida
    mask_neg = freqs_hz < 0
    axes[1].fill_between(freqs_hz[mask_neg], 0, S_mag.max() * 2.2,
                         alpha=0.12, color=COR_CINZA, hatch='xx',
                         edgecolor=COR_CINZA, linewidth=0)
    axes[1].text(-4, S_mag.max() * 1.4, 'removido', fontsize=13,
                 ha='center', color='gray', fontstyle='italic')

    # Anotações
    axes[1].text(5.5, Z_mag.max() * 0.65,
                 r'$Z(f) = 2 \cdot S(f) \cdot u(f)$',
                 fontsize=13, color=COR_ANALITICO,
                 bbox=dict(boxstyle='round,pad=0.3', fc='white', ec=COR_ANALITICO, alpha=0.8))
    axes[0].text(-7.5, S_mag.max() * 0.75,
                 r'$z(t) = s(t) + j\hat{s}(t)$',
                 fontsize=13, color=COR_ANALITICO)

    axes[1].set_xlim(-8, 8)
    fig.tight_layout()
    save(fig, 'passband_passo2_analitico')


# ====================================================================
# Figura 3 — Deslocamento para banda básica
# ====================================================================
def fig_passo3_desloc():
    print('Gerando: passband_passo3_desloc')
    d = _gerar_sinais()
    freqs_hz = d['freqs'] / 1000
    Z_mag = np.abs(d['Z'])
    S_tilde_mag = np.abs(d['S_tilde'])

    fig, axes = plt.subplots(2, 1, figsize=(10, 6), sharex=True)

    # --- Topo: Z(f) ---
    axes[0].plot(freqs_hz, Z_mag, color=COR_ANALITICO, linewidth=1.5)
    axes[0].fill_between(freqs_hz, Z_mag, alpha=0.25, color=COR_ANALITICO)
    axes[0].set_ylabel('|Z(f)|')
    axes[0].set_title('Passo 3: Deslocar para Banda Básica')
    axes[0].set_xlim(-8, 8)

    # --- Baixo: S̃(f) ---
    axes[1].plot(freqs_hz, S_tilde_mag, color=COR_BB, linewidth=1.5)
    axes[1].fill_between(freqs_hz, S_tilde_mag, alpha=0.25, color=COR_BB)
    axes[1].set_ylabel(r'$|\tilde{S}(f)|$')
    axes[1].set_xlabel('Frequência (kHz)')
    axes[1].set_xlim(-8, 8)

    # Seta mostrando deslocamento de -fc
    yref = Z_mag.max() * 0.6
    axes[0].annotate('', xy=(0, yref), xytext=(fc / 1000, yref),
                     arrowprops=dict(arrowstyle='->', color='purple',
                                     lw=2, connectionstyle='arc3,rad=-0.2'))
    axes[0].text(fc / 2000, yref * 1.25, r'deslocar $-f_c$',
                 fontsize=13, ha='center', color='purple', fontweight='bold')

    # Anotação
    axes[1].text(3.0, S_tilde_mag.max() * 0.7,
                 r'$\tilde{s}(t) = z(t) \cdot e^{-j2\pi f_c t}$',
                 fontsize=13, color=COR_BB,
                 bbox=dict(boxstyle='round,pad=0.3', fc='white', ec=COR_BB, alpha=0.8))

    fig.tight_layout()
    save(fig, 'passband_passo3_desloc')


# ====================================================================
# Figura 4 — Transformada de Hilbert: de onde vem?
# ====================================================================
def fig_passo4_hilbert():
    print('Gerando: passband_passo4_hilbert')

    fig, ax = plt.subplots(figsize=(10, 4))

    f_plot = np.linspace(-8, 8, 2000)
    # 2u(f) = 1 + sgn(f)
    two_u = np.where(f_plot > 0, 2.0, np.where(f_plot == 0, 1.0, 0.0))

    ax.step(f_plot, two_u, where='mid', color=COR_ANALITICO, linewidth=2.0)
    ax.fill_between(f_plot, two_u, step='mid', alpha=0.15, color=COR_ANALITICO)

    ax.set_xlim(-8, 8)
    ax.set_ylim(-0.3, 2.8)
    ax.set_xlabel('Frequência (kHz)')
    ax.set_ylabel('Amplitude')
    ax.set_title('De Onde Vem a Transformada de Hilbert?')

    # Anotações de valor
    ax.text(4, 2.15, '2', fontsize=16, fontweight='bold', color=COR_ANALITICO,
            ha='center')
    ax.text(-4, 0.2, '0', fontsize=16, fontweight='bold', color=COR_ANALITICO,
            ha='center')

    # Fórmula
    ax.text(4.5, 1.3, r'$2u(f) = 1 + \mathrm{sgn}(f)$',
            fontsize=14, color='black',
            bbox=dict(boxstyle='round,pad=0.4', fc='lightyellow', ec='orange', alpha=0.9))

    ax.text(0, -0.6,
            'Multiplicar por $2u(f)$ no domínio da frequência',
            fontsize=13, ha='center', color='purple', fontweight='bold',
            transform=ax.get_xaxis_transform())

    # Texto inferior: relação no tempo
    ax.text(0, -0.85,
            r'No tempo: $z(t) = s(t) + j\hat{s}(t)$  onde  '
            r'$\hat{s}(t) = \mathcal{H}\{s(t)\}$',
            fontsize=13, ha='center', color=COR_ANALITICO,
            transform=ax.get_xaxis_transform(),
            bbox=dict(boxstyle='round,pad=0.3', fc='white', ec=COR_ANALITICO, alpha=0.8))

    fig.tight_layout()
    fig.subplots_adjust(bottom=0.30)
    save(fig, 'passband_passo4_hilbert')


# ====================================================================
# Figura 5 — Componentes I e Q no domínio da frequência
# ====================================================================
def fig_passo5_IQ():
    print('Gerando: passband_passo5_IQ')
    d = _gerar_sinais()
    freqs_hz = d['freqs'] / 1000
    S_tilde = d['S_tilde']
    S_tilde_mag = np.abs(S_tilde)
    S_tilde_re = np.abs(np.real(S_tilde))
    S_tilde_im = np.abs(np.imag(S_tilde))

    fig, axes = plt.subplots(3, 1, figsize=(10, 7), sharex=True)

    # --- Topo: |S̃(f)| ---
    axes[0].plot(freqs_hz, S_tilde_mag, color=COR_BB, linewidth=1.5)
    axes[0].fill_between(freqs_hz, S_tilde_mag, alpha=0.25, color=COR_BB)
    axes[0].set_ylabel(r'$|\tilde{S}(f)|$')
    axes[0].set_title('Componentes I e Q — Domínio da Frequência')

    # --- Meio: Re{S̃(f)} ---
    axes[1].plot(freqs_hz, S_tilde_re, color=COR_ORIG, linewidth=1.5)
    axes[1].fill_between(freqs_hz, S_tilde_re, alpha=0.25, color=COR_ORIG)
    axes[1].set_ylabel(r'$|\mathrm{Re}\{\tilde{S}(f)\}|$')
    axes[1].text(0.97, 0.85, r'$s_I(t)$ — componente em fase',
                 fontsize=13, color=COR_ORIG, ha='right',
                 transform=axes[1].transAxes,
                 bbox=dict(boxstyle='round,pad=0.3',
                           fc='white', ec=COR_ORIG, alpha=0.8))

    # --- Baixo: Im{S̃(f)} ---
    axes[2].plot(freqs_hz, S_tilde_im, color='darkorange', linewidth=1.5)
    axes[2].fill_between(freqs_hz, S_tilde_im,
                         alpha=0.25, color='darkorange')
    axes[2].set_ylabel(r'$|\mathrm{Im}\{\tilde{S}(f)\}|$')
    axes[2].set_xlabel('Frequência (kHz)')
    axes[2].text(0.97, 0.85,
                 r'$s_Q(t)$ — componente em quadratura',
                 fontsize=13, color='darkorange', ha='right',
                 transform=axes[2].transAxes,
                 bbox=dict(boxstyle='round,pad=0.3',
                           fc='white', ec='darkorange', alpha=0.8))

    for ax in axes:
        ax.set_xlim(-3, 3)

    fig.subplots_adjust(hspace=0.3, left=0.1, right=0.95, top=0.93, bottom=0.08)
    save(fig, 'passband_passo5_IQ')


# ====================================================================
# Figura 6 — Reconstrução: banda básica → banda passante
# ====================================================================
def fig_passo6_reconstrucao():
    print('Gerando: passband_passo6_reconstrucao')
    d = _gerar_sinais()
    freqs_hz = d['freqs'] / 1000
    S_mag = np.abs(d['S'])
    Z_mag = np.abs(d['Z'])
    S_tilde_mag = np.abs(d['S_tilde'])

    fig, axes = plt.subplots(3, 1, figsize=(10, 7), sharex=True)

    # --- Topo: S̃(f) banda básica ---
    axes[0].plot(freqs_hz, S_tilde_mag, color=COR_BB, linewidth=1.5)
    axes[0].fill_between(freqs_hz, S_tilde_mag, alpha=0.25, color=COR_BB)
    axes[0].set_ylabel(r'$|\tilde{S}(f)|$')
    axes[0].set_title('Reconstrução: Banda Básica → Banda Passante')

    # Seta de subida
    axes[0].annotate('', xy=(fc / 1000, S_tilde_mag.max() * 0.5),
                     xytext=(0, S_tilde_mag.max() * 0.5),
                     arrowprops=dict(arrowstyle='->', color='purple',
                                     lw=2, connectionstyle='arc3,rad=-0.2'))
    axes[0].text(fc / 2000, S_tilde_mag.max() * 0.75,
                 r'multiplicar por $e^{j2\pi f_c t}$',
                 fontsize=12, ha='center', color='purple', fontweight='bold')

    # --- Meio: Z(f) deslocado de volta ---
    axes[1].plot(freqs_hz, Z_mag, color=COR_ANALITICO, linewidth=1.5)
    axes[1].fill_between(freqs_hz, Z_mag, alpha=0.25, color=COR_ANALITICO)
    axes[1].set_ylabel('|Z(f)|')
    axes[1].text(5.8, Z_mag.max() * 0.7,
                 r'$\tilde{S}(f - f_c) = Z(f)$',
                 fontsize=13, color=COR_ANALITICO,
                 bbox=dict(boxstyle='round,pad=0.3', fc='white', ec=COR_ANALITICO, alpha=0.8))

    # --- Baixo: S(f) recuperado ---
    axes[2].plot(freqs_hz, S_mag, color=COR_ORIG, linewidth=1.5)
    axes[2].fill_between(freqs_hz, S_mag, alpha=0.25, color=COR_ORIG)
    axes[2].set_ylabel('|S(f)|')
    axes[2].set_xlabel('Frequência (kHz)')

    # Anotação de reconstrução
    axes[2].text(0, -0.45,
                 r'$s(t) = \mathrm{Re}\{\tilde{s}(t) e^{j2\pi f_c t}\}'
                 r' = s_I(t)\cos(2\pi f_c t) - s_Q(t)\sin(2\pi f_c t)$',
                 fontsize=13, ha='center', color='black',
                 transform=axes[2].get_xaxis_transform(),
                 bbox=dict(boxstyle='round,pad=0.4', fc='lightyellow', ec='orange', alpha=0.9))

    for ax in axes:
        ax.set_xlim(-8, 8)

    fig.tight_layout()
    fig.subplots_adjust(bottom=0.15)
    save(fig, 'passband_passo6_reconstrucao')


# ====================================================================
if __name__ == '__main__':
    print('=== Gerando figuras: envelope complexo do sinal passante ===')
    fig_passo1_espectro()
    fig_passo2_analitico()
    fig_passo3_desloc()
    fig_passo4_hilbert()
    fig_passo5_IQ()
    fig_passo6_reconstrucao()
    print('=== Concluído! ===')
