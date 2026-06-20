#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: Prática 08 - Reconstrução ZOH e Equalização
# Author: Prof. Daniel Costa Araújo
# Description: Prática 08 - Reconstrução ZOH e equalização
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
import pratica_08_reconstrucao_zoh_equalizador as equalizador  # embedded python block
import sip
import threading



class pratica_08_reconstrucao_zoh(gr.top_block, Qt.QWidget):

    def __init__(self):
        gr.top_block.__init__(self, "Prática 08 - Reconstrução ZOH e Equalização", catch_exceptions=True)
        Qt.QWidget.__init__(self)
        self.setWindowTitle("Prática 08 - Reconstrução ZOH e Equalização")
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

        self.settings = Qt.QSettings("gnuradio/flowgraphs", "pratica_08_reconstrucao_zoh")

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
        self.samp_rate = samp_rate = 48000
        self.N_zoh = N_zoh = 8
        self.fs_low = fs_low = samp_rate//N_zoh
        self.f0 = f0 = 2400

        ##################################################
        # Blocks
        ##################################################

        self._f0_range = qtgui.Range(200, 2800, 100, 2400, 200)
        self._f0_win = qtgui.RangeWidget(self._f0_range, self.set_f0, "Frequência do tom (Hz)", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_grid_layout.addWidget(self._f0_win, 0, 0, 1, 2)
        for r in range(0, 1):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 2):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.zoh = blocks.repeat(gr.sizeof_float*1, N_zoh)
        self.time_sink = qtgui.time_sink_f(
            1024, #size
            samp_rate, #samp_rate
            "Reconstrução no tempo: ZOH (escada) e equalizado", #name
            2, #number of inputs
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


        labels = ['ZOH (escada)', 'Equalizado', 'Signal 3', 'Signal 4', 'Signal 5',
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


        for i in range(2):
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
        self.top_grid_layout.addWidget(self._time_sink_win, 1, 0, 1, 2)
        for r in range(1, 2):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 2):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.throttle = blocks.throttle( gr.sizeof_float*1, samp_rate, True, 0 if "auto" == "auto" else max( int(float(0.1) * samp_rate) if "auto" == "time" else int(0.1), 1) )
        self.src = analog.sig_source_f(fs_low, analog.GR_COS_WAVE, f0, 1.0, 0, 0)
        self.freq_sink = qtgui.freq_sink_f(
            4096, #size
            window.WIN_HANN, #wintype
            0, #fc
            samp_rate, #bw
            "Espectro: ZOH (droop sinc + imagens) e equalizado", #name
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

        labels = ['ZOH', 'Equalizado', '', '', '',
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
        self.top_grid_layout.addWidget(self._freq_sink_win, 2, 0, 1, 2)
        for r in range(2, 3):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 2):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.equalizador = equalizador.blk(fs_low=fs_low, fs_high=samp_rate, ntaps=201)


        ##################################################
        # Connections
        ##################################################
        self.connect((self.equalizador, 0), (self.freq_sink, 1))
        self.connect((self.equalizador, 0), (self.time_sink, 1))
        self.connect((self.src, 0), (self.zoh, 0))
        self.connect((self.throttle, 0), (self.equalizador, 0))
        self.connect((self.throttle, 0), (self.freq_sink, 0))
        self.connect((self.throttle, 0), (self.time_sink, 0))
        self.connect((self.zoh, 0), (self.throttle, 0))


    def closeEvent(self, event):
        self.settings = Qt.QSettings("gnuradio/flowgraphs", "pratica_08_reconstrucao_zoh")
        self.settings.setValue("geometry", self.saveGeometry())
        self.stop()
        self.wait()

        event.accept()

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.set_fs_low(self.samp_rate//self.N_zoh)
        self.throttle.set_sample_rate(self.samp_rate)
        self.time_sink.set_samp_rate(self.samp_rate)
        self.freq_sink.set_frequency_range(0, self.samp_rate)

    def get_N_zoh(self):
        return self.N_zoh

    def set_N_zoh(self, N_zoh):
        self.N_zoh = N_zoh
        self.set_fs_low(self.samp_rate//self.N_zoh)
        self.zoh.set_interpolation(self.N_zoh)

    def get_fs_low(self):
        return self.fs_low

    def set_fs_low(self, fs_low):
        self.fs_low = fs_low
        self.src.set_sampling_freq(self.fs_low)

    def get_f0(self):
        return self.f0

    def set_f0(self, f0):
        self.f0 = f0
        self.src.set_frequency(self.f0)




def main(top_block_cls=pratica_08_reconstrucao_zoh, options=None):

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
