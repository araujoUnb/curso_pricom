#!/usr/bin/env python3
"""
Script 09: tabelas de J_n(beta) para os gráficos pgfplots dos slides de FM
Gera, em Latex-slides/FM/dados/:
  bessel_curvas.dat      beta J0 J1 J2 J3
  comp_b<beta>.dat       n J absJ, componentes |J_n| >= 0.005
  carson.dat             beta carson criterio1pct, ambos em unidades de f_m
  doistons_g1.dat        espectro de e^{j beta1 sin}, f1 = 1 kHz
  doistons_g2.dat        espectro de e^{j beta2 sin}, f2 = 10 kHz
  doistons_prod.dat      produto, f = m f1 + n f2
"""

import os
import sys
import numpy as np
from scipy.special import jv

saida = sys.argv[1] if len(sys.argv) > 1 else '../../Latex-slides/FM/dados'
os.makedirs(saida, exist_ok=True)

# Curvas J_0 a J_3
b = np.linspace(0, 10, 201)
np.savetxt(f'{saida}/bessel_curvas.dat',
           np.column_stack([b] + [jv(k, b) for k in range(4)]),
           header='beta J0 J1 J2 J3', comments='', fmt='%.5f')

# Componentes para alguns valores de beta
for beta in [0.3, 0.5, 1, 2, 5, 10, 15]:
    n = np.arange(-25, 26)
    J = jv(n, beta)
    sel = np.abs(J) >= 0.005
    nome = str(beta).replace('.', 'p')
    np.savetxt(f'{saida}/comp_b{nome}.dat', np.column_stack([n[sel], J[sel], np.abs(J[sel])]),
               header='n J absJ', comments='', fmt=['%d', '%.5f', '%.5f'])
    nc = int(np.floor(beta + 1))
    frac = jv(0, beta)**2 + 2 * np.sum(jv(np.arange(1, nc + 1), beta)**2)
    print(f'beta={beta}: soma J^2 = {np.sum(J**2):.4f}, potência em Carson (|n|<={nc}) = {100*frac:.1f} %')

# Banda: Carson contra o critério de 1 %
bc = np.linspace(0.1, 10, 100)
crit = []
for beta in bc:
    n = np.arange(0, 60)
    crit.append(2 * n[np.abs(jv(n, beta)) >= 0.01].max())
np.savetxt(f'{saida}/carson.dat', np.column_stack([bc, 2 * (bc + 1), crit]),
           header='beta carson crit', comments='', fmt='%.4f')

# Dois tons: beta1 = 1 em f1 = 1 kHz, beta2 = 0.5 em f2 = 10 kHz
b1, b2, f1, f2 = 1.0, 0.5, 1, 10
m = np.arange(-4, 5)
n = np.arange(-3, 4)
g1 = jv(m, b1); g2 = jv(n, b2)
np.savetxt(f'{saida}/doistons_g1.dat', np.column_stack([m * f1, g1, np.abs(g1)])[np.abs(g1) >= 0.005],
           header='f J absJ', comments='', fmt='%.5f')
np.savetxt(f'{saida}/doistons_g2.dat', np.column_stack([n * f2, g2, np.abs(g2)])[np.abs(g2) >= 0.005],
           header='f J absJ', comments='', fmt='%.5f')
M, N = np.meshgrid(m, n)
A = jv(M, b1) * jv(N, b2)
F = M * f1 + N * f2
sel = np.abs(A) >= 0.005
np.savetxt(f'{saida}/doistons_prod.dat', np.column_stack([F[sel], A[sel], np.abs(A[sel])]),
           header='f J absJ', comments='', fmt='%.5f')

for k in range(6):
    print(f'J_{k}: ' + '  '.join(f'b={beta}: {jv(k, beta):+.4f}' for beta in [0.5, 1, 2, 5]))
