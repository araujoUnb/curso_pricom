"""
Embedded Python Block -- Quantizador Uniforme PCM (mid-rise)
============================================================
Quantizador uniforme de n_bits na faixa [-vmax, +vmax].

  L     = 2**n_bits          numero de niveis
  Delta = 2*vmax / L         passo de quantizacao
  y     = Delta*(floor(x/Delta) + 0.5)   nivel mais proximo (mid-rise)

Erro de quantizacao limitado a [-Delta/2, +Delta/2], com potencia
Pq = Delta**2 / 12. Para uma senoide de fundo de escala o SQNR teorico
vale 1,76 + 6,02*n_bits dB (regra dos 6 dB/bit vista em sala).

Cole este codigo em um bloco "Embedded Python Block" do GNU Radio
Companion, ou mantenha o arquivo ao lado do .grc.
"""

import numpy as np
from gnuradio import gr


class blk(gr.sync_block):
    def __init__(self, n_bits=3, vmax=1.0):
        gr.sync_block.__init__(
            self,
            name="Quantizador PCM (n_bits)",
            in_sig=[np.float32],
            out_sig=[np.float32],
        )
        self.n_bits = int(n_bits)
        self.vmax = float(vmax)

    @property
    def delta(self):
        return 2.0 * self.vmax / (2 ** self.n_bits)

    def work(self, input_items, output_items):
        delta = self.delta
        x = np.clip(input_items[0], -self.vmax, self.vmax - 1e-9)
        output_items[0][:] = delta * (np.floor(x / delta) + 0.5)
        return len(output_items[0])
