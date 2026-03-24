#!/usr/bin/env python3
"""
Gera figuras de filtros ideais vs práticos.
Curso de Princípios de Comunicação - UnB.
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy import signal as sig
import os

plt.rcParams.update({
    'text.usetex': False,
    'font.size': 12,
    'axes.labelsize': 14,
    'axes.titlesize': 14,
    'xtick.labelsize': 11,
    'ytick.labelsize': 11,
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


# ====================================================================
# 1. Filtro ideal vs Butterworth de várias ordens
# ====================================================================
def fig_ideal_vs_butterworth():
    print('Gerando: filtro_ideal_vs_butterworth')

    fc = 1000  # Hz
    wc = 2 * np.pi * fc
    f = np.linspace(0, 3000, 2000)
    w = 2 * np.pi * f

    # Filtro ideal
    H_ideal = np.where(f <= fc, 1.0, 0.0)

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    # Magnitude
    axes[0].plot(f/1000, H_ideal, 'k--', linewidth=2,
                 label='Ideal', alpha=0.8)
    colors = ['#2196F3', '#4CAF50', '#FF9800', '#F44336']
    for n, c in zip([1, 2, 4, 8], colors):
        H_mag = 1.0 / np.sqrt(1 + (f/fc)**(2*n))
        axes[0].plot(f/1000, H_mag, color=c, linewidth=1.8,
                     label=f'Butterworth n={n}')

    axes[0].axhline(y=1/np.sqrt(2), color='gray', linestyle=':',
                    alpha=0.5)
    axes[0].annotate('-3 dB', xy=(1.05, 1/np.sqrt(2)),
                     fontsize=10, color='gray')
    axes[0].axvline(x=1, color='gray', linestyle=':', alpha=0.5)
    axes[0].set_xlabel('Frequência (kHz)')
    axes[0].set_ylabel('|H(f)|')
    axes[0].set_title('Magnitude — Ideal vs Butterworth')
    axes[0].legend(fontsize=10)
    axes[0].set_ylim([-0.05, 1.15])

    # Magnitude em dB
    axes[1].plot(f[1:]/1000,
                 20*np.log10(H_ideal[1:] + 1e-10),
                 'k--', linewidth=2, label='Ideal', alpha=0.8)
    for n, c in zip([1, 2, 4, 8], colors):
        H_mag = 1.0 / np.sqrt(1 + (f/fc)**(2*n))
        axes[1].plot(f[1:]/1000, 20*np.log10(H_mag[1:]),
                     color=c, linewidth=1.8,
                     label=f'n={n} ({20*n} dB/déc)')

    axes[1].axhline(y=-3, color='gray', linestyle=':', alpha=0.5)
    axes[1].axvline(x=1, color='gray', linestyle=':', alpha=0.5)
    axes[1].set_xlabel('Frequência (kHz)')
    axes[1].set_ylabel('|H(f)| (dB)')
    axes[1].set_title('Magnitude em dB')
    axes[1].legend(fontsize=10)
    axes[1].set_ylim([-80, 5])

    fig.suptitle(r'Filtro Passa-Baixas Ideal vs Butterworth ($f_c$ = 1 kHz)',
                 fontsize=15, fontweight='bold', y=1.02)
    fig.tight_layout()
    save(fig, 'filtro_ideal_vs_butterworth')


# ====================================================================
# 2. Resposta ao impulso: ideal (sinc) vs prático
# ====================================================================
def fig_resposta_impulso_ideal_vs_pratico():
    print('Gerando: resposta_impulso_ideal_vs_pratico')

    fs = 48000
    fc = 2000
    wc = 2 * np.pi * fc
    T = 0.005  # 5 ms
    t = np.arange(-T, T, 1/fs)

    # Resposta ao impulso ideal: sinc
    h_ideal = wc/np.pi * np.sinc(wc*t/np.pi)

    # Respostas ao impulso práticas
    # Butterworth ordem 4
    sos_but = sig.butter(4, fc, fs=fs, output='sos')
    imp = np.zeros(len(t))
    imp[len(t)//2] = fs  # impulso unitário escalado
    t_causal = np.arange(0, T, 1/fs)

    imp_c = np.zeros(len(t_causal))
    imp_c[0] = fs
    h_but = sig.sosfilt(sos_but, imp_c)

    # Bessel ordem 4
    sos_bes = sig.bessel(4, fc, btype='low', fs=fs,
                         output='sos', norm='mag')
    h_bes = sig.sosfilt(sos_bes, imp_c)

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    # Ideal
    axes[0].plot(t*1000, h_ideal, 'b-', linewidth=2)
    axes[0].axvline(x=0, color='red', linestyle='--', alpha=0.7,
                    label='t = 0 (impulso)')
    axes[0].fill_between(t[t < 0]*1000, h_ideal[t < 0], 0,
                         alpha=0.3, color='red',
                         label='NÃO-CAUSAL (t < 0)')
    axes[0].set_xlabel('Tempo (ms)')
    axes[0].set_ylabel('h(t)')
    axes[0].set_title(
        r'Filtro Ideal: $h(t) = \frac{\omega_c}{\pi}'
        r'\mathrm{sinc}(\omega_c t/\pi)$')
    axes[0].legend(fontsize=10)

    # Práticos
    axes[1].plot(t_causal*1000, h_but, 'g-', linewidth=2,
                 label='Butterworth n=4')
    axes[1].plot(t_causal*1000, h_bes, 'm-', linewidth=2,
                 label='Bessel n=4')
    axes[1].axvline(x=0, color='red', linestyle='--', alpha=0.7)
    axes[1].set_xlabel('Tempo (ms)')
    axes[1].set_ylabel('h(t)')
    axes[1].set_title('Filtros Práticos: CAUSAIS (h(t)=0 para t<0)')
    axes[1].legend(fontsize=10)

    fig.suptitle(
        'Resposta ao Impulso — Filtro Ideal vs Filtros Práticos'
        r' ($f_c$ = 2 kHz)',
        fontsize=15, fontweight='bold', y=1.02)
    fig.tight_layout()
    save(fig, 'resposta_impulso_ideal_vs_pratico')


# ====================================================================
# 3. Comparação completa: Butterworth, Chebyshev I, Bessel, Elíptico
# ====================================================================
def fig_comparacao_filtros_completa():
    print('Gerando: comparacao_filtros_completa')

    fs = 48000
    fc = 4000
    ordem = 5

    # Projetar filtros
    filtros = {}
    filtros['Butterworth'] = sig.butter(
        ordem, fc, fs=fs, output='sos')
    filtros['Chebyshev I (1dB)'] = sig.cheby1(
        ordem, 1, fc, fs=fs, output='sos')
    filtros['Bessel'] = sig.bessel(
        ordem, fc, fs=fs, output='sos', norm='mag')
    filtros['Elíptico (1dB, 40dB)'] = sig.ellip(
        ordem, 1, 40, fc, fs=fs, output='sos')

    cores = {'Butterworth': '#2196F3',
             'Chebyshev I (1dB)': '#F44336',
             'Bessel': '#4CAF50',
             'Elíptico (1dB, 40dB)': '#FF9800'}

    fig, axes = plt.subplots(2, 2, figsize=(13, 9))

    for nome, sos in filtros.items():
        w, h = sig.sosfreqz(sos, worN=4096, fs=fs)
        cor = cores[nome]

        # Magnitude
        axes[0, 0].plot(w/1000, 20*np.log10(np.abs(h) + 1e-15),
                        color=cor, linewidth=1.8, label=nome)

        # Magnitude linear (zoom passante)
        axes[0, 1].plot(w/1000, np.abs(h),
                        color=cor, linewidth=1.8, label=nome)

        # Fase
        axes[1, 0].plot(w/1000, np.unwrap(np.angle(h))*180/np.pi,
                        color=cor, linewidth=1.8, label=nome)

        # Atraso de grupo
        b, a = sig.sos2tf(sos)
        w_gd, gd = sig.group_delay((b, a), fs=fs)
        gd_ms = gd / fs * 1000
        mask = w_gd <= 8000
        axes[1, 1].plot(w_gd[mask]/1000, gd_ms[mask],
                        color=cor, linewidth=1.8, label=nome)

    # Configurar eixos
    axes[0, 0].set_xlabel('Frequência (kHz)')
    axes[0, 0].set_ylabel('|H(f)| (dB)')
    axes[0, 0].set_title('Resposta em Magnitude')
    axes[0, 0].set_xlim([0, 12])
    axes[0, 0].set_ylim([-80, 5])
    axes[0, 0].axhline(y=-3, color='gray', linestyle=':', alpha=0.5)
    axes[0, 0].axvline(x=fc/1000, color='gray', linestyle=':',
                       alpha=0.5)
    axes[0, 0].legend(fontsize=9)

    axes[0, 1].set_xlabel('Frequência (kHz)')
    axes[0, 1].set_ylabel('|H(f)|')
    axes[0, 1].set_title('Magnitude (zoom na banda passante)')
    axes[0, 1].set_xlim([0, 6])
    axes[0, 1].set_ylim([0.6, 1.15])
    axes[0, 1].axhline(y=1/np.sqrt(2), color='gray',
                       linestyle=':', alpha=0.5)
    axes[0, 1].axvline(x=fc/1000, color='gray', linestyle=':',
                       alpha=0.5)
    axes[0, 1].legend(fontsize=9)

    axes[1, 0].set_xlabel('Frequência (kHz)')
    axes[1, 0].set_ylabel('Fase (graus)')
    axes[1, 0].set_title('Resposta de Fase')
    axes[1, 0].set_xlim([0, 8])
    axes[1, 0].legend(fontsize=9)

    axes[1, 1].set_xlabel('Frequência (kHz)')
    axes[1, 1].set_ylabel(r'$\tau_g$ (ms)')
    axes[1, 1].set_title(
        r'Atraso de Grupo $\tau_g = -d\phi/d\omega$')
    axes[1, 1].set_xlim([0, 8])
    axes[1, 1].legend(fontsize=9)

    fig.suptitle(
        f'Comparação de Filtros Práticos — Ordem {ordem},'
        f' fc = {fc/1000:.0f} kHz',
        fontsize=15, fontweight='bold', y=1.02)
    fig.tight_layout()
    save(fig, 'comparacao_filtros_completa')


# ====================================================================
# 4. Sinal passando por cada filtro (tempo + freq)
# ====================================================================
def fig_sinal_filtrado_comparacao():
    print('Gerando: sinal_filtrado_comparacao')

    fs = 48000
    fc = 3000
    ordem = 6
    T = 0.008
    t = np.arange(0, T, 1/fs)

    # Sinal: soma de cossenos
    x = (np.cos(2*np.pi*500*t)
         + 0.8*np.cos(2*np.pi*2000*t)
         + 0.6*np.cos(2*np.pi*4500*t)
         + 0.4*np.cos(2*np.pi*7000*t))

    filtros = {
        'Butterworth': sig.butter(ordem, fc, fs=fs, output='sos'),
        'Chebyshev I': sig.cheby1(ordem, 1, fc, fs=fs, output='sos'),
        'Bessel': sig.bessel(ordem, fc, fs=fs, output='sos',
                             norm='mag'),
        'Elíptico': sig.ellip(ordem, 1, 40, fc, fs=fs, output='sos'),
    }
    cores = {'Butterworth': '#2196F3', 'Chebyshev I': '#F44336',
             'Bessel': '#4CAF50', 'Elíptico': '#FF9800'}

    fig, axes = plt.subplots(2, 2, figsize=(13, 8))

    t_ms = t * 1000
    N = len(t)
    freqs = np.fft.rfftfreq(N, 1/fs)
    fmask = freqs <= 10000

    for ax_row, (nome, sos) in zip(
            [(0, 0), (0, 1), (1, 0), (1, 1)], filtros.items()):
        r, c = ax_row
        y = sig.sosfilt(sos, x)
        cor = cores[nome]

        ax = axes[r, c]
        ax.plot(t_ms, x, 'b-', linewidth=1, alpha=0.3,
                label='Original')
        ax.plot(t_ms, y, color=cor, linewidth=1.5,
                label=f'{nome}')
        ax.set_title(f'{nome} (ordem {ordem}, fc={fc/1000:.0f} kHz)')
        ax.set_xlabel('Tempo (ms)')
        ax.set_ylabel('Amplitude')
        ax.legend(fontsize=9, loc='upper right')
        ax.set_xlim([1, 6])

    fig.suptitle(
        'Sinal Filtrado por Diferentes Tipos de Filtros',
        fontsize=15, fontweight='bold', y=1.02)
    fig.tight_layout()
    save(fig, 'sinal_filtrado_comparacao')


# ====================================================================
# 5. Efeito da ordem no Butterworth (sinal real)
# ====================================================================
def fig_butterworth_efeito_ordem():
    print('Gerando: butterworth_efeito_ordem')

    fs = 48000
    fc = 2000
    T = 0.008
    t = np.arange(0, T, 1/fs)

    # Sinal com componentes dentro e fora da banda
    x = (np.cos(2*np.pi*500*t)
         + np.cos(2*np.pi*1500*t)
         + np.cos(2*np.pi*3000*t)
         + np.cos(2*np.pi*5000*t))

    ordens = [1, 2, 4, 8]
    cores = ['#2196F3', '#4CAF50', '#FF9800', '#F44336']

    fig, axes = plt.subplots(2, 2, figsize=(13, 8))

    N = len(t)
    freqs = np.fft.rfftfreq(N, 1/fs)
    X_mag = 2*np.abs(np.fft.rfft(x))/N
    fmask = freqs <= 8000
    t_ms = t * 1000

    for idx, (n, cor) in enumerate(zip(ordens, cores)):
        r, c = divmod(idx, 2)
        sos = sig.butter(n, fc, fs=fs, output='sos')
        y = sig.sosfilt(sos, x)
        Y_mag = 2*np.abs(np.fft.rfft(y))/N

        ax = axes[r, c]

        # Espectro original em cinza
        ax.stem(freqs[fmask]/1000, X_mag[fmask],
                linefmt='b-', markerfmt='bo', basefmt='b-',
                label='Original')
        ax.stem(freqs[fmask]/1000, Y_mag[fmask],
                linefmt='-', markerfmt='^', basefmt='-',
                label=f'Butterworth n={n}')
        # Colorir os stems
        ax.get_children()[3].set_color(cor)  # lines
        ax.get_children()[4].set_color(cor)  # markers

        ax.axvline(x=fc/1000, color='gray', linestyle=':',
                   alpha=0.5, label=f'fc={fc/1000:.0f} kHz')
        ax.set_xlabel('Frequência (kHz)')
        ax.set_ylabel('|X(f)|')
        ax.set_title(f'Butterworth n={n} — '
                     f'Atenuação: {20*n} dB/déc')
        ax.legend(fontsize=9)
        ax.set_xlim([-0.2, 8])

    fig.suptitle(
        'Efeito da Ordem do Filtro Butterworth'
        f' (fc = {fc/1000:.0f} kHz)',
        fontsize=15, fontweight='bold', y=1.02)
    fig.tight_layout()
    save(fig, 'butterworth_efeito_ordem')


# ====================================================================
# 6. Resposta ao degrau: comparação de filtros
# ====================================================================
def fig_resposta_degrau():
    print('Gerando: resposta_degrau_filtros')

    fs = 48000
    fc = 2000
    ordem = 4
    T = 0.004
    t = np.arange(0, T, 1/fs)

    # Degrau unitário
    step = np.ones(len(t))

    filtros = {
        'Butterworth': sig.butter(ordem, fc, fs=fs, output='sos'),
        'Chebyshev I': sig.cheby1(ordem, 1, fc, fs=fs, output='sos'),
        'Bessel': sig.bessel(ordem, fc, fs=fs, output='sos',
                             norm='mag'),
        'Elíptico': sig.ellip(ordem, 1, 40, fc, fs=fs, output='sos'),
    }
    cores = {'Butterworth': '#2196F3', 'Chebyshev I': '#F44336',
             'Bessel': '#4CAF50', 'Elíptico': '#FF9800'}

    fig, ax = plt.subplots(1, 1, figsize=(10, 5))

    t_ms = t * 1000
    ax.plot(t_ms, step, 'k--', linewidth=1.5, alpha=0.4,
            label='Degrau ideal')

    for nome, sos in filtros.items():
        y = sig.sosfilt(sos, step)
        ax.plot(t_ms, y, color=cores[nome], linewidth=2,
                label=nome)

    ax.set_xlabel('Tempo (ms)')
    ax.set_ylabel('Amplitude')
    ax.set_title(
        f'Resposta ao Degrau — Filtros de Ordem {ordem}'
        f' (fc = {fc/1000:.0f} kHz)')
    ax.legend(fontsize=11)
    ax.set_xlim([0, T*1000])
    ax.set_ylim([-0.1, 1.4])

    # Anotações
    ax.annotate('Bessel: mínimo overshoot\n(preserva pulsos)',
                xy=(0.7, 0.95), fontsize=9, color='#4CAF50',
                fontstyle='italic')
    ax.annotate('Chebyshev/Elíptico:\novershoot e ringing',
                xy=(0.4, 1.18), fontsize=9, color='#F44336',
                fontstyle='italic')

    fig.tight_layout()
    save(fig, 'resposta_degrau_filtros')


# ====================================================================
if __name__ == '__main__':
    print('=== Gerando figuras de filtros ===')
    fig_ideal_vs_butterworth()
    fig_resposta_impulso_ideal_vs_pratico()
    fig_comparacao_filtros_completa()
    fig_sinal_filtrado_comparacao()
    fig_butterworth_efeito_ordem()
    fig_resposta_degrau()
    print('=== Concluído! ===')
