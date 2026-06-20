#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: Prática 06 - Phase-Locked Loop (PLL)
# Author: Prof. Daniel Costa Araújo
# Description: Prática 06 - Phase-Locked Loop (PLL)
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
import sip
import threading



class pratica_06_pll(gr.top_block, Qt.QWidget):

    def __init__(self):
        gr.top_block.__init__(self, "Prática 06 - Phase-Locked Loop (PLL)", catch_exceptions=True)
        Qt.QWidget.__init__(self)
        self.setWindowTitle("Prática 06 - Phase-Locked Loop (PLL)")
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

        self.settings = Qt.QSettings("gnuradio/flowgraphs", "pratica_06_pll")

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
        self.samp_rate = samp_rate = 32000
        self.max_freq = max_freq = 2*3.14159265*2000/samp_rate
        self.noise_amp = noise_amp = 0
        self.min_freq = min_freq = -max_freq
        self.loop_bw = loop_bw = 0.062
        self.freq_in = freq_in = 1000

        ##################################################
        # Blocks
        ##################################################

        self._noise_amp_range = qtgui.Range(0, 1.0, 0.05, 0, 200)
        self._noise_amp_win = qtgui.RangeWidget(self._noise_amp_range, self.set_noise_amp, "Amplitude do Ruído", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_grid_layout.addWidget(self._noise_amp_win, 1, 0, 1, 1)
        for r in range(1, 2):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 1):
            self.top_grid_layout.setColumnStretch(c, 1)
        self._loop_bw_range = qtgui.Range(0.01, 0.628, 0.01, 0.062, 200)
        self._loop_bw_win = qtgui.RangeWidget(self._loop_bw_range, self.set_loop_bw, "Loop Bandwidth (rad/amostra)", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_grid_layout.addWidget(self._loop_bw_win, 0, 0, 1, 1)
        for r in range(0, 1):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 1):
            self.top_grid_layout.setColumnStretch(c, 1)
        self._freq_in_range = qtgui.Range(200, 1800, 50, 1000, 200)
        self._freq_in_win = qtgui.RangeWidget(self._freq_in_range, self.set_freq_in, "Frequência de entrada (Hz)", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_grid_layout.addWidget(self._freq_in_win, 0, 1, 1, 1)
        for r in range(0, 1):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(1, 2):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.time_sink = qtgui.time_sink_f(
            4096, #size
            samp_rate, #samp_rate
            "Convergência do PLL", #name
            1, #number of inputs
            None # parent
        )
        self.time_sink.set_update_time(0.10)
        self.time_sink.set_y_axis(-1.5, 1.5)

        self.time_sink.set_y_label('Amplitude', "")

        self.time_sink.enable_tags(True)
        self.time_sink.set_trigger_mode(qtgui.TRIG_MODE_FREE, qtgui.TRIG_SLOPE_POS, 0.0, 0, 0, "")
        self.time_sink.enable_autoscale(True)
        self.time_sink.enable_grid(True)
        self.time_sink.enable_axis_labels(True)
        self.time_sink.enable_control_panel(False)
        self.time_sink.enable_stem_plot(False)


        labels = ['Saída PLL (frequência)', 'Signal 2', 'Signal 3', 'Signal 4', 'Signal 5',
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


        for i in range(1):
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
        self.top_grid_layout.addWidget(self._time_sink_win, 2, 0, 1, 1)
        for r in range(2, 3):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 1):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.throttle = blocks.throttle( gr.sizeof_float*1, samp_rate, True, 0 if "auto" == "auto" else max( int(float(0.1) * samp_rate) if "auto" == "time" else int(0.1), 1) )
        self.src_signal = analog.sig_source_c(samp_rate, analog.GR_COS_WAVE, freq_in, 1.0, 0, 0)
        self.src_noise = analog.noise_source_c(analog.GR_GAUSSIAN, noise_amp, 0)
        self.pll_freqdet = analog.pll_freqdet_cf(loop_bw, max_freq, min_freq)
        self.freq_sink_entrada = qtgui.freq_sink_c(
            4096, #size
            window.WIN_HANN, #wintype
            0, #fc
            samp_rate, #bw
            "Espectro do Sinal de Entrada", #name
            1,
            None # parent
        )
        self.freq_sink_entrada.set_update_time(0.10)
        self.freq_sink_entrada.set_y_axis((-100), 10)
        self.freq_sink_entrada.set_y_label('Relative Gain', 'dB')
        self.freq_sink_entrada.set_trigger_mode(qtgui.TRIG_MODE_FREE, 0.0, 0, "")
        self.freq_sink_entrada.enable_autoscale(False)
        self.freq_sink_entrada.enable_grid(True)
        self.freq_sink_entrada.set_fft_average(1.0)
        self.freq_sink_entrada.enable_axis_labels(True)
        self.freq_sink_entrada.enable_control_panel(False)
        self.freq_sink_entrada.set_fft_window_normalized(False)



        labels = ['Sinal de entrada', '', '', '', '',
            '', '', '', '', '']
        widths = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        colors = ["blue", "red", "green", "black", "cyan",
            "magenta", "yellow", "dark red", "dark green", "dark blue"]
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0, 1.0, 1.0]

        for i in range(1):
            if len(labels[i]) == 0:
                self.freq_sink_entrada.set_line_label(i, "Data {0}".format(i))
            else:
                self.freq_sink_entrada.set_line_label(i, labels[i])
            self.freq_sink_entrada.set_line_width(i, widths[i])
            self.freq_sink_entrada.set_line_color(i, colors[i])
            self.freq_sink_entrada.set_line_alpha(i, alphas[i])

        self._freq_sink_entrada_win = sip.wrapinstance(self.freq_sink_entrada.qwidget(), Qt.QWidget)
        self.top_grid_layout.addWidget(self._freq_sink_entrada_win, 2, 1, 1, 1)
        for r in range(2, 3):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(1, 2):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.add_block = blocks.add_vcc(1)


        ##################################################
        # Connections
        ##################################################
        self.connect((self.add_block, 0), (self.freq_sink_entrada, 0))
        self.connect((self.add_block, 0), (self.pll_freqdet, 0))
        self.connect((self.pll_freqdet, 0), (self.throttle, 0))
        self.connect((self.src_noise, 0), (self.add_block, 1))
        self.connect((self.src_signal, 0), (self.add_block, 0))
        self.connect((self.throttle, 0), (self.time_sink, 0))


    def closeEvent(self, event):
        self.settings = Qt.QSettings("gnuradio/flowgraphs", "pratica_06_pll")
        self.settings.setValue("geometry", self.saveGeometry())
        self.stop()
        self.wait()

        event.accept()

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.set_max_freq(2*3.14159265*2000/self.samp_rate)
        self.src_signal.set_sampling_freq(self.samp_rate)
        self.throttle.set_sample_rate(self.samp_rate)
        self.time_sink.set_samp_rate(self.samp_rate)
        self.freq_sink_entrada.set_frequency_range(0, self.samp_rate)

    def get_max_freq(self):
        return self.max_freq

    def set_max_freq(self, max_freq):
        self.max_freq = max_freq
        self.set_min_freq(-self.max_freq)
        self.pll_freqdet.set_max_freq(self.max_freq)

    def get_noise_amp(self):
        return self.noise_amp

    def set_noise_amp(self, noise_amp):
        self.noise_amp = noise_amp
        self.src_noise.set_amplitude(self.noise_amp)

    def get_min_freq(self):
        return self.min_freq

    def set_min_freq(self, min_freq):
        self.min_freq = min_freq
        self.pll_freqdet.set_min_freq(self.min_freq)

    def get_loop_bw(self):
        return self.loop_bw

    def set_loop_bw(self, loop_bw):
        self.loop_bw = loop_bw
        self.pll_freqdet.set_loop_bandwidth(self.loop_bw)

    def get_freq_in(self):
        return self.freq_in

    def set_freq_in(self, freq_in):
        self.freq_in = freq_in
        self.src_signal.set_frequency(self.freq_in)




def main(top_block_cls=pratica_06_pll, options=None):

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
