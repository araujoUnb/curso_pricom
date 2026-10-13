#!/usr/bin/env python3
"""
Script 11: espectro de FM com três tons
Gera, em Latex-slides/FM/dados/:
  trestons_prod.dat   f absJ   produto de três espectros de Bessel, f = m f1 + n f2 + p f3
"""

import os
import sys
import numpy as np
from scipy.special import jv

saida = sys.argv[1] if len(sys.argv) > 1 else '../../Latex-slides/FM/dados'
os.makedirs(saida, exist_ok=True)

# Três tons: os dois do exemplo anterior e um terceiro em 3,5 kHz com beta3 = 0,6
tons = [(1.0, 1.0), (0.5, 10.0), (0.6, 3.5)]   # (beta, f em kHz)
espec = {0.0: 1.0 + 0j}
for beta, fk in tons:
    novo = {}
    for f0, a0 in espec.items():
        for n in range(-8, 9):
            f = round(f0 + n * fk, 3)
            novo[f] = novo.get(f, 0) + a0 * jv(n, beta)
    espec = {f: a for f, a in novo.items() if abs(a) >= 1e-4}
F = np.array(sorted(espec)); A = np.abs([espec[f] for f in F])
sel = (A >= 0.005) & (np.abs(F) <= 24)
np.savetxt(f'{saida}/trestons_prod.dat', np.column_stack([F[sel], A[sel]]),
           header='f absJ', comments='', fmt='%.5f')
print(f'três tons: {sel.sum()} componentes com |A| >= 0,005; portadora {espec[0.0].real:.3f}')
