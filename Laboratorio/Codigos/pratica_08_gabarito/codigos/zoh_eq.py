"""
Equalizador de reconstrucao ZOH (inverse-sinc).

O segurador de ordem zero multiplica o espectro por |sinc(f/fs_low)|, atenuando
as altas frequencias. Este bloco aplica um FIR de resposta proporcional a
1/sinc(f/fs_low) na banda de passagem, achatando o droop, e com rolloff acima
de fs_low/2 para suprimir as imagens espectrais.

Parametros: fs_low (taxa antes do ZOH), fs_high (taxa apos o ZOH), ntaps
(numero de coeficientes do FIR) e ngrid (pontos da grade de frequencia usada no
projeto do filtro).
"""

import numpy as np
from gnuradio import gr
from scipy.signal import firwin2


def design_eq(fs_low, fs_high, ntaps=201, pb_frac=0.45, ngrid=512):
    f = np.linspace(0.0, 1.0, ngrid)          # normalizado a fs_high/2
    fc = (pb_frac * fs_low) / (fs_high / 2.0)
    g = np.zeros_like(f)
    pb = f <= fc
    g[pb] = 1.0 / np.sinc(f[pb] * (fs_high / 2.0) / fs_low)
    return np.asarray(firwin2(ntaps, f, g), dtype=np.float32)


class blk(gr.sync_block):
    def __init__(self, fs_low=6000, fs_high=48000, ntaps=201, ngrid=512):
        gr.sync_block.__init__(self, name="Equalizador ZOH (inverse-sinc)",
                               in_sig=[np.float32], out_sig=[np.float32])
        self.taps = design_eq(fs_low, fs_high, ntaps, ngrid=ngrid)
        self.set_history(len(self.taps))

    def work(self, input_items, output_items):
        y = np.convolve(input_items[0], self.taps, 'valid')
        output_items[0][:] = y
        return len(output_items[0])
