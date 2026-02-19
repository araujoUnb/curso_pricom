#!/usr/bin/env python3
"""
Script 12: Cascata de estágios e figura de ruído (Friis)
F_tot vs. G_1 para dois estágios
"""

import numpy as np
import matplotlib.pyplot as plt

plt.rcParams['font.size'] = 10
plt.rcParams['axes.grid'] = True

# Friis: F_tot = F_1 + (F_2 - 1)/G_1
# Dois estágios: F_1=2, F_2=4
F1, F2 = 2.0, 4.0
G1_dB = np.linspace(0, 30, 100)
G1_lin = 10**(G1_dB / 10)

F_tot = F1 + (F2 - 1) / G1_lin
F_tot_dB = 10 * np.log10(F_tot)

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))

# F_tot vs G_1 (linear)
ax1.plot(G1_dB, F_tot_dB, 'b-', linewidth=2)
ax1.axhline(y=10*np.log10(F1), color='gray', linestyle='--', linewidth=1, label=f'$F_1$ = {10*np.log10(F1):.1f} dB')
ax1.axhline(y=10*np.log10(F2), color='gray', linestyle=':', linewidth=1, label=f'$F_2$ = {10*np.log10(F2):.1f} dB')
ax1.set_xlabel('Ganho do 1º estágio $G_1$ (dB)')
ax1.set_ylabel('Figura de ruído total $F_{tot}$ (dB)')
ax1.set_title('Cascata de 2 estágios: $F_{tot} = F_1 + (F_2-1)/G_1$ (Friis)')
ax1.legend()
ax1.grid(True, alpha=0.3)
ax1.set_xlim([0, 30])

# Ordem dos estágios: F1 primeiro vs F2 primeiro
# Ordem A: F1=2, G1=10; F2=4, G2=5  -> F_tot_A = 2 + 3/10 = 2.3
# Ordem B: F2=4, G2=5; F1=2, G1=10   -> F_tot_B = 4 + 1/5 = 4.2
G1_fix, G2_fix = 10, 5
F_tot_A = F1 + (F2 - 1) / G1_fix
F_tot_B = F2 + (F1 - 1) / G2_fix

labels = ['Ordem: $F_1$=2, $G_1$=10 → $F_2$=4, $G_2$=5', 'Ordem: $F_2$=4, $G_2$=5 → $F_1$=2, $G_1$=10']
values = [F_tot_A, F_tot_B]
colors = ['green', 'red']
bars = ax2.bar(labels, [10*np.log10(v) for v in values], color=colors, edgecolor='black')
ax2.set_ylabel('$F_{tot}$ (dB)')
ax2.set_title('Efeito da ordem dos estágios na figura de ruído total')
ax2.grid(True, axis='y', alpha=0.3)
for bar, v in zip(bars, values):
    ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1, f'{v:.2f} ({10*np.log10(v):.1f} dB)', ha='center', fontsize=9)

plt.tight_layout()
plt.savefig('../noise_figure_cascade.pdf', bbox_inches='tight')
plt.savefig('../noise_figure_cascade.png', dpi=300, bbox_inches='tight')
print("Figura salva: noise_figure_cascade.pdf/png")
plt.close()
