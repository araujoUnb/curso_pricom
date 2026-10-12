import numpy as np
from gnuradio import gr

class blk(gr.sync_block):
    """Desenrola a fase e divide por 2 (recuperacao de portadora via quadrado)"""
    def __init__(self):
        gr.sync_block.__init__(
            self,
            name='Unwrap e Divide por 2',
            in_sig=[np.complex64],   # saida do PLL Carrier Regeneration (em 2*theta)
            out_sig=[np.complex64]   # portadora reconstruida (em theta)
        )
        self.fase_anterior = 0.0
        self.acumulado = 0.0

    def work(self, input_items, output_items):
        x = input_items[0]
        y = output_items[0]
        fase_ant = self.fase_anterior
        acumulado = self.acumulado

        for n in range(len(x)):
            fase_bruta = np.angle(x[n])
            diferenca = fase_bruta - fase_ant

            if diferenca > np.pi:
                acumulado -= 2*np.pi
            elif diferenca < -np.pi:
                acumulado += 2*np.pi

            fase_continua = fase_bruta + acumulado
            fase_ant = fase_bruta

            theta = fase_continua / 2.0
            y[n] = np.exp(1j*theta)

        self.fase_anterior = fase_ant
        self.acumulado = acumulado
        return len(output_items[0])