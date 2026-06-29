#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: Prática 08 - Quantização PCM
# Author: Prof. Daniel Costa Araújo
# Description: Prática 08 - Quantização PCM
# GNU Radio version: 3.10.12.0

from PyQt5 import Qt
from gnuradio import qtgui
from PyQt5 import QtCore
from gnuradio import analog
from gnuradio import blocks
from gnuradio import gr
from gnuradio.filter import firdes
from gnuradio.fft import window
import sys
import signal
from PyQt5 import Qt
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
import pratica_08_quantizacao_pcm_quantizador as quantizador  # embedded python block
import sip
import threading



class pratica_08_quantizacao_pcm(gr.top_block, Qt.QWidget):

    def __init__(self):
        gr.top_block.__init__(self, "Prática 08 - Quantização PCM", catch_exceptions=True)
        Qt.QWidget.__init__(self)
        self.setWindowTitle("Prática 08 - Quantização PCM")
        qtgui.util.check_set_qss()
        try:
            self.setWindowIcon(Qt.QIcon.fromTheme('gnuradio-grc'))
        except BaseException as exc:
            print(f"Qt GUI: Could not set Icon: {str(exc)}", file=sys.stderr)
        self.top_scroll_layout = Qt.QVBoxLayout()
        self.setLayout(self.top_scroll_layout)
        self.top_scroll = Qt.QScrollArea()
        self.top_scroll.setFrameStyle(Qt.QFrame.NoFrame)
        self.top_scroll_layout.addWidget(self.top_scroll)
        self.top_scroll.setWidgetResizable(True)
        self.top_widget = Qt.QWidget()
        self.top_scroll.setWidget(self.top_widget)
        self.top_layout = Qt.QVBoxLayout(self.top_widget)
        self.top_grid_layout = Qt.QGridLayout()
        self.top_layout.addLayout(self.top_grid_layout)

        self.settings = Qt.QSettings("gnuradio/flowgraphs", "pratica_08_quantizacao_pcm")

        try:
            geometry = self.settings.value("geometry")
            if geometry:
                self.restoreGeometry(geometry)
        except BaseException as exc:
            print(f"Qt GUI: Could not restore geometry: {str(exc)}", file=sys.stderr)
        self.flowgraph_started = threading.Event()

        ##################################################
        # Variables
        ##################################################
        self.vmax = vmax = 1.0
        self.samp_rate = samp_rate = 48000
        self.n_bits = n_bits = 4
        self.ma_len = ma_len = 16384
        self.f_sinal = f_sinal = 997

        ##################################################
        # Blocks
        ##################################################

        self._n_bits_range = qtgui.Range(2, 16, 1, 4, 200)
        self._n_bits_win = qtgui.RangeWidget(self._n_bits_range, self.set_n_bits, "Número de bits (n)", "counter_slider", int, QtCore.Qt.Horizontal)
        self.top_grid_layout.addWidget(self._n_bits_win, 0, 0, 1, 1)
        for r in range(0, 1):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 1):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.time_sink = qtgui.time_sink_f(
            1024, #size
            samp_rate, #samp_rate
            "Sinal: original, quantizado e erro (tempo)", #name
            3, #number of inputs
            None # parent
        )
        self.time_sink.set_update_time(0.10)
        self.time_sink.set_y_axis(-1.2, 1.2)

        self.time_sink.set_y_label('Amplitude', "")

        self.time_sink.enable_tags(True)
        self.time_sink.set_trigger_mode(qtgui.TRIG_MODE_FREE, qtgui.TRIG_SLOPE_POS, 0.0, 0, 0, "")
        self.time_sink.enable_autoscale(False)
        self.time_sink.enable_grid(True)
        self.time_sink.enable_axis_labels(True)
        self.time_sink.enable_control_panel(False)
        self.time_sink.enable_stem_plot(False)


        labels = ['Original', 'Quantizado', 'Erro de quantização', 'Signal 4', 'Signal 5',
            'Signal 6', 'Signal 7', 'Signal 8', 'Signal 9', 'Signal 10']
        widths = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        colors = ['blue', 'red', 'green', 'black', 'cyan',
            'magenta', 'yellow', 'dark red', 'dark green', 'dark blue']
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0, 1.0, 1.0]
        styles = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        markers = [-1, -1, -1, -1, -1,
            -1, -1, -1, -1, -1]


        for i in range(3):
            if len(labels[i]) == 0:
                self.time_sink.set_line_label(i, "Data {0}".format(i))
            else:
                self.time_sink.set_line_label(i, labels[i])
            self.time_sink.set_line_width(i, widths[i])
            self.time_sink.set_line_color(i, colors[i])
            self.time_sink.set_line_style(i, styles[i])
            self.time_sink.set_line_marker(i, markers[i])
            self.time_sink.set_line_alpha(i, alphas[i])

        self._time_sink_win = sip.wrapinstance(self.time_sink.qwidget(), Qt.QWidget)
        self.top_grid_layout.addWidget(self._time_sink_win, 2, 0, 1, 2)
        for r in range(2, 3):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 2):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.throttle = blocks.throttle( gr.sizeof_float*1, samp_rate, True, 0 if "auto" == "auto" else max( int(float(0.1) * samp_rate) if "auto" == "time" else int(0.1), 1) )
        self.src_sinal = analog.sig_source_f(samp_rate, analog.GR_COS_WAVE, f_sinal, vmax, 0, 0)
        self.sqnr_db = blocks.nlog10_ff(10, 1, 0)
        self.sq_sinal = blocks.multiply_vff(1)
        self.sq_erro = blocks.multiply_vff(1)
        self.razao = blocks.divide_ff(1)
        self.quantizador = quantizador.blk(n_bits=n_bits, vmax=vmax)
        self.num_sink_sqnr = qtgui.number_sink(
            gr.sizeof_float,
            0,
            qtgui.NUM_GRAPH_HORIZ,
            1,
            None # parent
        )
        self.num_sink_sqnr.set_update_time(0.10)
        self.num_sink_sqnr.set_title("SQNR (dB)")

        labels = ['SQNR medido (dB)', '', '', '', '',
            '', '', '', '', '']
        units = ['dB', '', '', '', '',
            '', '', '', '', '']
        colors = [("black", "black"), ("black", "black"), ("black", "black"), ("black", "black"), ("black", "black"),
            ("black", "black"), ("black", "black"), ("black", "black"), ("black", "black"), ("black", "black")]
        factor = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]

        for i in range(1):
            self.num_sink_sqnr.set_min(i, 0)
            self.num_sink_sqnr.set_max(i, 100)
            self.num_sink_sqnr.set_color(i, colors[i][0], colors[i][1])
            if len(labels[i]) == 0:
                self.num_sink_sqnr.set_label(i, "Data {0}".format(i))
            else:
                self.num_sink_sqnr.set_label(i, labels[i])
            self.num_sink_sqnr.set_unit(i, units[i])
            self.num_sink_sqnr.set_factor(i, factor[i])

        self.num_sink_sqnr.enable_autoscale(False)
        self._num_sink_sqnr_win = sip.wrapinstance(self.num_sink_sqnr.qwidget(), Qt.QWidget)
        self.top_grid_layout.addWidget(self._num_sink_sqnr_win, 1, 0, 1, 2)
        for r in range(1, 2):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 2):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.ma_sinal = blocks.moving_average_ff(ma_len, (1.0/ma_len), ma_len, 1)
        self.ma_erro = blocks.moving_average_ff(ma_len, (1.0/ma_len), ma_len, 1)
        self.freq_sink = qtgui.freq_sink_f(
            4096, #size
            window.WIN_HANN, #wintype
            0, #fc
            samp_rate, #bw
            "Espectro: original e quantizado (ruído de quantização)", #name
            2,
            None # parent
        )
        self.freq_sink.set_update_time(0.10)
        self.freq_sink.set_y_axis((-100), 10)
        self.freq_sink.set_y_label('Relative Gain', 'dB')
        self.freq_sink.set_trigger_mode(qtgui.TRIG_MODE_FREE, 0.0, 0, "")
        self.freq_sink.enable_autoscale(False)
        self.freq_sink.enable_grid(True)
        self.freq_sink.set_fft_average(1.0)
        self.freq_sink.enable_axis_labels(True)
        self.freq_sink.enable_control_panel(False)
        self.freq_sink.set_fft_window_normalized(False)


        self.freq_sink.set_plot_pos_half(not True)

        labels = ['Original', 'Quantizado', '', '', '',
            '', '', '', '', '']
        widths = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        colors = ["blue", "red", "green", "black", "cyan",
            "magenta", "yellow", "dark red", "dark green", "dark blue"]
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0, 1.0, 1.0]

        for i in range(2):
            if len(labels[i]) == 0:
                self.freq_sink.set_line_label(i, "Data {0}".format(i))
            else:
                self.freq_sink.set_line_label(i, labels[i])
            self.freq_sink.set_line_width(i, widths[i])
            self.freq_sink.set_line_color(i, colors[i])
            self.freq_sink.set_line_alpha(i, alphas[i])

        self._freq_sink_win = sip.wrapinstance(self.freq_sink.qwidget(), Qt.QWidget)
        self.top_grid_layout.addWidget(self._freq_sink_win, 3, 0, 1, 2)
        for r in range(3, 4):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 2):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.erro = blocks.sub_ff(1)


        ##################################################
        # Connections
        ##################################################
        self.connect((self.erro, 0), (self.sq_erro, 0))
        self.connect((self.erro, 0), (self.sq_erro, 1))
        self.connect((self.erro, 0), (self.time_sink, 2))
        self.connect((self.ma_erro, 0), (self.razao, 1))
        self.connect((self.ma_sinal, 0), (self.razao, 0))
        self.connect((self.quantizador, 0), (self.erro, 1))
        self.connect((self.quantizador, 0), (self.freq_sink, 1))
        self.connect((self.quantizador, 0), (self.time_sink, 1))
        self.connect((self.razao, 0), (self.sqnr_db, 0))
        self.connect((self.sq_erro, 0), (self.ma_erro, 0))
        self.connect((self.sq_sinal, 0), (self.ma_sinal, 0))
        self.connect((self.sqnr_db, 0), (self.num_sink_sqnr, 0))
        self.connect((self.src_sinal, 0), (self.throttle, 0))
        self.connect((self.throttle, 0), (self.erro, 0))
        self.connect((self.throttle, 0), (self.freq_sink, 0))
        self.connect((self.throttle, 0), (self.quantizador, 0))
        self.connect((self.throttle, 0), (self.sq_sinal, 1))
        self.connect((self.throttle, 0), (self.sq_sinal, 0))
        self.connect((self.throttle, 0), (self.time_sink, 0))


    def closeEvent(self, event):
        self.settings = Qt.QSettings("gnuradio/flowgraphs", "pratica_08_quantizacao_pcm")
        self.settings.setValue("geometry", self.saveGeometry())
        self.stop()
        self.wait()

        event.accept()

    def get_vmax(self):
        return self.vmax

    def set_vmax(self, vmax):
        self.vmax = vmax
        self.src_sinal.set_amplitude(self.vmax)
        self.quantizador.vmax = self.vmax

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.src_sinal.set_sampling_freq(self.samp_rate)
        self.throttle.set_sample_rate(self.samp_rate)
        self.time_sink.set_samp_rate(self.samp_rate)
        self.freq_sink.set_frequency_range(0, self.samp_rate)

    def get_n_bits(self):
        return self.n_bits

    def set_n_bits(self, n_bits):
        self.n_bits = n_bits
        self.quantizador.n_bits = self.n_bits

    def get_ma_len(self):
        return self.ma_len

    def set_ma_len(self, ma_len):
        self.ma_len = ma_len
        self.ma_sinal.set_length_and_scale(self.ma_len, (1.0/self.ma_len))
        self.ma_erro.set_length_and_scale(self.ma_len, (1.0/self.ma_len))

    def get_f_sinal(self):
        return self.f_sinal

    def set_f_sinal(self, f_sinal):
        self.f_sinal = f_sinal
        self.src_sinal.set_frequency(self.f_sinal)




def main(top_block_cls=pratica_08_quantizacao_pcm, options=None):

    qapp = Qt.QApplication(sys.argv)

    tb = top_block_cls()

    tb.start()
    tb.flowgraph_started.set()

    tb.show()

    def sig_handler(sig=None, frame=None):
        tb.stop()
        tb.wait()

        Qt.QApplication.quit()

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    timer = Qt.QTimer()
    timer.start(500)
    timer.timeout.connect(lambda: None)

    qapp.exec_()

if __name__ == '__main__':
    main()
