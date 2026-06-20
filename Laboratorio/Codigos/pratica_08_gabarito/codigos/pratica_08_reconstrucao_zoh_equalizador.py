"""
Embedded Python Block -- Equalizador de reconstrucao ZOH (inverse-sinc)
=======================================================================
Um DAC real segura cada amostra por Ts = 1/fs_low (zero-order hold), o que
multiplica o espectro pelo envelope |H_ZOH(f)| = |sinc(f/fs_low)|. Esse
envelope atenua as altas frequencias -- efeito de abertura -- com perda de
sinc(0,5) = 2/pi ~ -3,9 dB na borda da banda f = fs_low/2.

Este bloco aplica um FIR de compensacao com resposta proporcional a
1/sinc(f/fs_low) na banda de passagem, achatando o droop, e com rolloff acima
de fs_low/2 para suprimir as imagens espectrais.

Cole este codigo em um "Embedded Python Block" do GNU Radio Companion, com os
parametros fs_low, fs_high e ntaps. A funcao design_eq tambem e reutilizada
pelo gabarito (pratica_08_gabarito.py).
"""

import numpy as np
from gnuradio import gr
from scipy.signal import firwin2


def design_eq(fs_low, fs_high, ntaps=201, pb_frac=0.45):
    """FIR equalizador inverse-sinc no rate fs_high.

    fs_low  -- taxa antes do ZOH (Hz)
    fs_high -- taxa apos o ZOH/upsampling (Hz)
    ntaps   -- numero de coeficientes (impar)
    pb_frac -- fracao de fs_low/2 ate onde a banda e equalizada
    """
    f = np.linspace(0.0, 1.0, 512)            # normalizado a fs_high/2
    fc = (pb_frac * fs_low) / (fs_high / 2.0)
    g = np.zeros_like(f)
    pb = f <= fc
    g[pb] = 1.0 / np.sinc(f[pb] * (fs_high / 2.0) / fs_low)
    return np.asarray(firwin2(ntaps, f, g), dtype=np.float32)


class blk(gr.sync_block):
    def __init__(self, fs_low=6000, fs_high=48000, ntaps=201):
        gr.sync_block.__init__(self, name="Equalizador ZOH (inverse-sinc)",
                               in_sig=[np.float32], out_sig=[np.float32])
        self.taps = design_eq(fs_low, fs_high, ntaps)
        self.set_history(len(self.taps))

    def work(self, input_items, output_items):
        y = np.convolve(input_items[0], self.taps, 'valid')
        output_items[0][:] = y
        return len(output_items[0])
