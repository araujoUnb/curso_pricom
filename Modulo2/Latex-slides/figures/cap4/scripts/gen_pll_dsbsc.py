#!/usr/bin/env python3
"""
Gera figuras para slides DSB-SC:
1) pll_gnuradio_flowgraph.pdf — diagrama de blocos estilo GNU Radio do demodulador com PLL
2) pll_vs_no_pll.pdf — comparação: PLL em ação vs perda de sincronismo
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle
import matplotlib.patches as mpatches

# ============================================================
# Parâmetros globais
# ============================================================
plt.rcParams.update({
    'font.size': 11,
    'font.family': 'sans-serif',
    'axes.grid': True,
    'grid.alpha': 0.3,
    'figure.facecolor': 'white',
})

FIGDIR = '/home/daniel/Documentos/UnB/Aulas/curso_pricom/Modulo2/Latex-slides/figures/cap4/'

# ============================================================
# Figura 1: Diagrama de blocos estilo GNU Radio
# ============================================================
def draw_gnuradio_flowgraph():
    fig, ax = plt.subplots(1, 1, figsize=(15, 5))
    ax.set_xlim(-0.5, 15.5)
    ax.set_ylim(-2.5, 4)
    ax.set_aspect('equal')
    ax.axis('off')

    # Cores estilo GNU Radio
    c_source = '#4FC3F7'   # azul claro
    c_math = '#FFD54F'     # amarelo
    c_filter = '#81C784'   # verde
    c_sink = '#EF9A9A'     # vermelho claro
    c_pll = '#CE93D8'      # roxo claro
    c_var = '#B0BEC5'      # cinza

    def grc_block(ax, x, y, w, h, label, sublabel, color):
        rect = FancyBboxPatch((x - w/2, y - h/2), w, h,
                              boxstyle="round,pad=0.1", linewidth=1.5,
                              edgecolor='#333333', facecolor=color)
        ax.add_patch(rect)
        ax.text(x, y + 0.12, label, ha='center', va='center',
                fontsize=9, fontweight='bold')
        ax.text(x, y - 0.28, sublabel, ha='center', va='center',
                fontsize=7, fontstyle='italic', color='#444444')

    def arrow(ax, x1, y1, x2, y2, label=''):
        ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle='->', lw=1.5, color='#333'))
        if label:
            mx, my = (x1+x2)/2, (y1+y2)/2
            ax.text(mx, my + 0.2, label, ha='center', va='bottom',
                    fontsize=8, color='#555')

    # === TRANSMISSOR ===
    ax.text(2, 3.5, 'TRANSMISSOR', ha='center', fontsize=10,
            fontweight='bold', color='#1565C0',
            bbox=dict(boxstyle='round', facecolor='#BBDEFB', edgecolor='#1565C0', alpha=0.7))

    # Signal Sources lado a lado verticalmente
    grc_block(ax, 0.5, 2.2, 1.8, 0.8, 'Signal Source', 'fm = 1 kHz', c_source)
    grc_block(ax, 0.5, 1.0, 1.8, 0.8, 'Signal Source', 'fc = 10 kHz', c_source)
    # Multiply TX
    grc_block(ax, 3, 1.6, 1.3, 0.8, 'Multiply', '×', c_math)

    arrow(ax, 1.4, 2.2, 2.35, 1.85)
    arrow(ax, 1.4, 1.0, 2.35, 1.35)
    arrow(ax, 3.65, 1.6, 4.5, 1.6, '$s(t)$')

    # === CANAL ===
    grc_block(ax, 5.3, 1.6, 1.3, 0.8, 'Channel', '+ ruído', c_var)
    arrow(ax, 5.95, 1.6, 6.8, 1.6, '$r(t)$')

    # === RECEPTOR ===
    ax.text(10.5, 3.5, 'RECEPTOR', ha='center', fontsize=10,
            fontweight='bold', color='#2E7D32',
            bbox=dict(boxstyle='round', facecolor='#C8E6C9', edgecolor='#2E7D32', alpha=0.7))

    # Multiply RX
    grc_block(ax, 7.8, 1.6, 1.3, 0.8, 'Multiply', '×', c_math)

    # Low Pass Filter
    grc_block(ax, 10, 1.6, 1.6, 0.8, 'Low Pass', 'Filter', c_filter)
    arrow(ax, 8.45, 1.6, 9.2, 1.6, '$v(t)$')

    # Sinks
    grc_block(ax, 12.2, 2.5, 1.8, 0.7, 'Time Sink', 'QT GUI', c_sink)
    grc_block(ax, 12.2, 1.6, 1.8, 0.7, 'Freq Sink', 'QT GUI', c_sink)
    arrow(ax, 10.8, 1.6, 11.3, 1.6, r'$\hat{m}(t)$')
    # Conexão time sink
    ax.annotate('', xy=(11.3, 2.5), xytext=(10.8, 1.8),
                arrowprops=dict(arrowstyle='->', lw=1, color='#888'))

    # PLL Carrier Tracking — abaixo do Multiply RX
    grc_block(ax, 9, -0.3, 2.2, 0.9, 'PLL Carrier', 'Tracking', c_pll)

    # PLL → Multiply (oscilador local)
    ax.annotate('', xy=(7.8, 1.2), xytext=(7.8, 0.15),
                arrowprops=dict(arrowstyle='->', lw=1.5, color='#7B1FA2'))
    ax.text(6.5, 0.5, r'$2\cos(2\pi f_c t + \hat{\theta})$',
            fontsize=8, color='#7B1FA2', ha='center')

    # Sinal recebido → PLL (referência)
    ax.annotate('', xy=(10.1, 0.15), xytext=(10.5, 1.2),
                arrowprops=dict(arrowstyle='->', lw=1.2, color='#7B1FA2',
                               connectionstyle='arc3,rad=-0.2'))
    ax.text(10.8, 0.5, 'erro', fontsize=8, color='#7B1FA2')

    # Bordas
    from matplotlib.patches import Rectangle
    tx_rect = Rectangle((-0.6, 0.4), 4.8, 3.3, linewidth=1.5,
                        edgecolor='#1565C0', facecolor='none',
                        linestyle='--', alpha=0.4)
    ax.add_patch(tx_rect)
    rx_rect = Rectangle((6.6, -1.0), 7, 4.7, linewidth=1.5,
                         edgecolor='#2E7D32', facecolor='none',
                         linestyle='--', alpha=0.4)
    ax.add_patch(rx_rect)

    fig.tight_layout()
    fig.savefig(FIGDIR + 'pll_gnuradio_flowgraph.pdf', bbox_inches='tight', dpi=150)
    fig.savefig(FIGDIR + 'pll_gnuradio_flowgraph.png', bbox_inches='tight', dpi=150)
    plt.close(fig)
    print('Saved pll_gnuradio_flowgraph.pdf/.png')


# ============================================================
# Figura 2: PLL em ação vs sem PLL (perda de sincronismo)
# ============================================================
def draw_pll_vs_no_pll():
    # Simulação
    fs = 48000
    T = 0.03  # 30 ms de visualização
    t = np.arange(0, T, 1/fs)

    fm = 1000
    fc = 10000
    Ac = 1.0

    # Mensagem
    m = np.cos(2 * np.pi * fm * t)

    # Sinal DSB-SC
    s = Ac * m * np.cos(2 * np.pi * fc * t)

    # --- Caso 1: PLL travado (theta -> 0) ---
    # Simula PLL convergindo: theta começa em 60° e vai a 0° exponencialmente
    tau_pll = 0.005  # constante de tempo do PLL
    theta_pll = np.deg2rad(60) * np.exp(-t / tau_pll)
    osc_pll = 2 * np.cos(2 * np.pi * fc * t + theta_pll)
    v_pll = s * osc_pll

    # Filtro passa-baixas (simples média móvel para visualização)
    from scipy.signal import butter, filtfilt
    b, a = butter(4, 2 * fm / fs * 1.5)
    y_pll = filtfilt(b, a, v_pll)

    # --- Caso 2: Sem PLL, erro de fase fixo = 60° ---
    theta_fix = np.deg2rad(60)
    osc_fix = 2 * np.cos(2 * np.pi * fc * t + theta_fix)
    v_fix = s * osc_fix
    y_fix = filtfilt(b, a, v_fix)

    # --- Caso 3: Sem PLL, erro de fase = 90° (perda total) ---
    theta_90 = np.deg2rad(90)
    osc_90 = 2 * np.cos(2 * np.pi * fc * t + theta_90)
    v_90 = s * osc_90
    y_90 = filtfilt(b, a, v_90)

    t_ms = t * 1000

    # ---- Figura A: PLL em ação (1 painel) ----
    fig1, ax1 = plt.subplots(1, 1, figsize=(12, 4))
    ax1.plot(t_ms, m, 'b-', alpha=0.4, linewidth=1.2, label='Original $m(t)$')
    ax1.plot(t_ms, y_pll, 'g-', linewidth=2.5, label='Recuperado (com PLL)')
    ax1.set_ylabel('Amplitude', fontsize=12)
    ax1.set_xlabel('Tempo (ms)', fontsize=12)
    ax1.set_title('Com PLL: recuperação de portadora em ação',
                  fontsize=13, fontweight='bold', color='#2E7D32')
    ax1.legend(loc='upper right', fontsize=11)
    ax1.set_ylim(-1.4, 1.4)
    ax1.annotate('PLL travando\n(transitório)',
                 xy=(2.5, 0.55), xytext=(8, 1.15),
                 fontsize=10, color='#2E7D32',
                 arrowprops=dict(arrowstyle='->', color='#2E7D32', lw=1.5),
                 ha='center')
    # Região de transitório
    ax1.axvspan(0, 5, alpha=0.08, color='orange', label='_')
    ax1.text(2.5, -1.25, 'Transitório', ha='center', fontsize=9, color='orange')
    fig1.tight_layout()
    fig1.savefig(FIGDIR + 'pll_recovery.pdf', bbox_inches='tight', dpi=150)
    fig1.savefig(FIGDIR + 'pll_recovery.png', bbox_inches='tight', dpi=150)
    plt.close(fig1)
    print('Saved pll_recovery.pdf/.png')

    # ---- Figura B: Sem PLL — erros de fase (2 painéis) ----
    fig2, (ax2, ax3) = plt.subplots(2, 1, figsize=(12, 5.5), sharex=True)

    # Painel 1: Erro fixo de 60°
    ax2.plot(t_ms, m, 'b-', alpha=0.4, linewidth=1.2, label='Original $m(t)$')
    ax2.plot(t_ms, y_fix, 'orange', linewidth=2.5,
             label=r'Sem PLL ($\theta = 60°$): $\cos 60° = 0.5$')
    ax2.set_ylabel('Amplitude', fontsize=12)
    ax2.set_title(r'Sem PLL: erro de fase $\theta = 60°$ — atenuação de 50%',
                  fontsize=13, fontweight='bold', color='#E65100')
    ax2.legend(loc='upper right', fontsize=11)
    ax2.set_ylim(-1.4, 1.4)
    ax2.axhline(y=0.5, color='orange', linestyle=':', alpha=0.5)
    ax2.axhline(y=-0.5, color='orange', linestyle=':', alpha=0.5)

    # Painel 2: Erro de 90° (perda total)
    ax3.plot(t_ms, m, 'b-', alpha=0.4, linewidth=1.2, label='Original $m(t)$')
    ax3.plot(t_ms, y_90, 'r-', linewidth=2.5,
             label=r'Sem PLL ($\theta = 90°$): $\cos 90° = 0$')
    ax3.set_ylabel('Amplitude', fontsize=12)
    ax3.set_xlabel('Tempo (ms)', fontsize=12)
    ax3.set_title(r'Sem PLL: erro de fase $\theta = 90°$ — perda total!',
                  fontsize=13, fontweight='bold', color='#C62828')
    ax3.legend(loc='upper right', fontsize=11)
    ax3.set_ylim(-1.4, 1.4)
    ax3.annotate('Sinal completamente\nperdido!',
                 xy=(15, 0.03), xytext=(22, 0.9),
                 fontsize=11, color='red', fontweight='bold',
                 arrowprops=dict(arrowstyle='->', color='red', lw=1.5),
                 ha='center')

    fig2.tight_layout()
    fig2.savefig(FIGDIR + 'pll_vs_no_pll.pdf', bbox_inches='tight', dpi=150)
    fig2.savefig(FIGDIR + 'pll_vs_no_pll.png', bbox_inches='tight', dpi=150)
    plt.close(fig2)
    print('Saved pll_vs_no_pll.pdf/.png')


if __name__ == '__main__':
    draw_gnuradio_flowgraph()
    draw_pll_vs_no_pll()
    print('Done!')
