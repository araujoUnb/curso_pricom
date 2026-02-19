#!/usr/bin/env python3
"""
Script 06: Funções de Bessel e Espectro FM
Gera: Gráficos de Jn(β) vs β e espectro FM para diferentes índices
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.special import jv

plt.rcParams['font.size'] = 10
plt.rcParams['axes.grid'] = True

# Gráfico 1: Funções de Bessel vs β
fig1, ax1 = plt.subplots(figsize=(12, 8))

beta_range = np.linspace(0, 10, 500)
orders = [0, 1, 2, 3, 4, 5]
colors = ['blue', 'red', 'green', 'orange', 'purple', 'brown']

for n, color in zip(orders, colors):
    J_n = jv(n, beta_range)
    ax1.plot(beta_range, J_n, color=color, linewidth=2, label=f'J₍{n}₎(β)')

ax1.axhline(y=0, color='k', linestyle='-', linewidth=0.5)
ax1.set_xlabel('Índice de Modulação β')
ax1.set_ylabel('Jₙ(β)')
ax1.set_title('Funções de Bessel de Primeira Espécie', fontsize=14, fontweight='bold')
ax1.legend(loc='upper right', ncol=2)
ax1.grid(True, alpha=0.3)
ax1.set_xlim([0, 10])
ax1.set_ylim([-0.5, 1])

# Marcar alguns pontos importantes
important_betas = [0.5, 1.0, 2.0, 5.0]
for beta_val in important_betas:
    ax1.axvline(x=beta_val, color='gray', linestyle='--', linewidth=0.8, alpha=0.3)
    ax1.text(beta_val, -0.45, f'β={beta_val}', ha='center', fontsize=8)

plt.tight_layout()
plt.savefig('../fm_bessel_functions.pdf', bbox_inches='tight')
plt.savefig('../fm_bessel_functions.png', dpi=300, bbox_inches='tight')
print("Figura salva: fm_bessel_functions.pdf/png")
plt.close()

# Gráfico 2: Espectro FM para diferentes β
fig2 = plt.figure(figsize=(14, 10))
gs = fig2.add_gridspec(2, 2, hspace=0.3, wspace=0.3)

beta_values = [0.5, 1.0, 2.0, 5.0]
titles = ['NBFM: β = 0.5', 'β = 1.0', 'β = 2.0', 'WBFM: β = 5.0']

for idx, (beta, title) in enumerate(zip(beta_values, titles)):
    ax = fig2.add_subplot(gs[idx//2, idx%2])
    
    # Calcular componentes espectrais
    max_n = int(beta + 10)  # Incluir mais componentes
    n_values = np.arange(-max_n, max_n+1)
    amplitudes = np.abs(jv(n_values, beta))
    
    # Plotar apenas componentes significativas (> 1%)
    significant = amplitudes > 0.01
    n_sig = n_values[significant]
    amp_sig = amplitudes[significant]
    
    # Stem plot
    markerline, stemlines, baseline = ax.stem(n_sig, amp_sig, basefmt=' ')
    plt.setp(stemlines, linewidth=1.5)
    plt.setp(markerline, markersize=8)
    
    ax.set_xlabel('Ordem da Banda Lateral n')
    ax.set_ylabel('Amplitude |Jₙ(β)|')
    ax.set_title(title)
    ax.grid(True, alpha=0.3)
    ax.axvline(x=0, color='r', linestyle='--', linewidth=1.5, alpha=0.5, label='Portadora')
    
    # Calcular largura de banda aproximada
    bandwidth_approx = 2 * (beta + 1)
    ax.text(0.98, 0.95, f'B ≈ 2(β+1)fₘ = {bandwidth_approx:.1f}fₘ', 
           transform=ax.transAxes, ha='right', va='top',
           bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    # Marcar significância de 98%
    power_sum = 0
    n_98 = 0
    for n in range(max_n+1):
        power_sum += jv(n, beta)**2 + (jv(-n, beta)**2 if n > 0 else 0)
        if power_sum >= 0.98:
            n_98 = n
            break
    
    if n_98 > 0:
        ax.axvspan(-n_98, n_98, alpha=0.1, color='green')
        ax.text(0.98, 0.85, f'98% potência: |n| ≤ {n_98}', 
               transform=ax.transAxes, ha='right', va='top', fontsize=9)

plt.suptitle('Espectro FM para Diferentes Índices de Modulação β', 
            fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig('../fm_spectrum_beta.pdf', bbox_inches='tight')
plt.savefig('../fm_spectrum_beta.png', dpi=300, bbox_inches='tight')
print("Figura salva: fm_spectrum_beta.pdf/png")
plt.close()

# Gráfico 3: Tabela de valores de Bessel
fig3, ax3 = plt.subplots(figsize=(12, 6))
ax3.axis('tight')
ax3.axis('off')

beta_table = [0.5, 1.0, 2.0, 5.0, 10.0]
n_table = range(11)
table_data = []

for beta in beta_table:
    row = [f'{beta:.1f}']
    for n in n_table:
        val = jv(n, beta)
        if abs(val) < 0.005:
            row.append('—')
        else:
            row.append(f'{val:.3f}')
    table_data.append(row)

columns = ['β'] + [f'J₍{n}₎' for n in n_table]
table = ax3.table(cellText=table_data, colLabels=columns,
                 cellLoc='center', loc='center',
                 colWidths=[0.08]*len(columns))
table.auto_set_font_size(False)
table.set_fontsize(9)
table.scale(1, 2)

# Colorir cabeçalho
for i in range(len(columns)):
    table[(0, i)].set_facecolor('#4CAF50')
    table[(0, i)].set_text_props(weight='bold', color='white')

# Colorir primeira coluna
for i in range(1, len(beta_table)+1):
    table[(i, 0)].set_facecolor('#E0E0E0')
    table[(i, 0)].set_text_props(weight='bold')

plt.title('Valores das Funções de Bessel Jₙ(β)', fontsize=14, fontweight='bold', pad=20)
plt.tight_layout()
plt.savefig('../fm_bessel_table.pdf', bbox_inches='tight')
plt.savefig('../fm_bessel_table.png', dpi=300, bbox_inches='tight')
print("Figura salva: fm_bessel_table.pdf/png")
plt.close()
