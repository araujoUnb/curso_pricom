#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: Prática 08 - Amostragem e Aliasing
# Author: Prof. Daniel Costa Araújo
# Description: Prática 08 - Amostragem e Aliasing
# GNU Radio version: 3.10.12.0

from PyQt5 import Qt
from gnuradio import qtgui
from PyQt5 import QtCore
from gnuradio import analog
from gnuradio import blocks
from gnuradio import filter
from gnuradio.filter import firdes
from gnuradio import gr
from gnuradio.fft import window
import sys
import signal
from PyQt5 import Qt
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
import sip
import threading



class pratica_08_amostragem_aliasing(gr.top_block, Qt.QWidget):

    def __init__(self):
        gr.top_block.__init__(self, "Prática 08 - Amostragem e Aliasing", catch_exceptions=True)
        Qt.QWidget.__init__(self)
        self.setWindowTitle("Prática 08 - Amostragem e Aliasing")
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

        self.settings = Qt.QSettings("gnuradio/flowgraphs", "pratica_08_amostragem_aliasing")

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
        self.decim = decim = 4
        self.fs_eff = fs_eff = samp_rate/decim
        self.f_sinal = f_sinal = 1000

        ##################################################
        # Blocks
        ##################################################

        self._f_sinal_range = qtgui.Range(500, 20000, 500, 1000, 200)
        self._f_sinal_win = qtgui.RangeWidget(self._f_sinal_range, self.set_f_sinal, "Frequência do sinal (Hz)", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_grid_layout.addWidget(self._f_sinal_win, 0, 1, 1, 1)
        for r in range(0, 1):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(1, 2):
            self.top_grid_layout.setColumnStretch(c, 1)
        self._decim_range = qtgui.Range(2, 20, 1, 4, 200)
        self._decim_win = qtgui.RangeWidget(self._decim_range, self.set_decim, "Fator de decimação (decim)", "counter_slider", int, QtCore.Qt.Horizontal)
        self.top_grid_layout.addWidget(self._decim_win, 0, 0, 1, 1)
        for r in range(0, 1):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 1):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.time_sink_original = qtgui.time_sink_f(
            1024, #size
            samp_rate, #samp_rate
            "Sinal Original (Tempo)", #name
            1, #number of inputs
            None # parent
        )
        self.time_sink_original.set_update_time(0.10)
        self.time_sink_original.set_y_axis(-1.5, 1.5)

        self.time_sink_original.set_y_label('Amplitude', "")

        self.time_sink_original.enable_tags(True)
        self.time_sink_original.set_trigger_mode(qtgui.TRIG_MODE_FREE, qtgui.TRIG_SLOPE_POS, 0.0, 0, 0, "")
        self.time_sink_original.enable_autoscale(True)
        self.time_sink_original.enable_grid(True)
        self.time_sink_original.enable_axis_labels(True)
        self.time_sink_original.enable_control_panel(False)
        self.time_sink_original.enable_stem_plot(False)


        labels = ['Sinal original', 'Signal 2', 'Signal 3', 'Signal 4', 'Signal 5',
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
                self.time_sink_original.set_line_label(i, "Data {0}".format(i))
            else:
                self.time_sink_original.set_line_label(i, labels[i])
            self.time_sink_original.set_line_width(i, widths[i])
            self.time_sink_original.set_line_color(i, colors[i])
            self.time_sink_original.set_line_style(i, styles[i])
            self.time_sink_original.set_line_marker(i, markers[i])
            self.time_sink_original.set_line_alpha(i, alphas[i])

        self._time_sink_original_win = sip.wrapinstance(self.time_sink_original.qwidget(), Qt.QWidget)
        self.top_grid_layout.addWidget(self._time_sink_original_win, 2, 0, 1, 1)
        for r in range(2, 3):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 1):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.time_sink_decim = qtgui.time_sink_f(
            1024, #size
            fs_eff, #samp_rate
            "Sinais Decimados (Tempo)", #name
            2, #number of inputs
            None # parent
        )
        self.time_sink_decim.set_update_time(0.10)
        self.time_sink_decim.set_y_axis(-1.5, 1.5)

        self.time_sink_decim.set_y_label('Amplitude', "")

        self.time_sink_decim.enable_tags(True)
        self.time_sink_decim.set_trigger_mode(qtgui.TRIG_MODE_FREE, qtgui.TRIG_SLOPE_POS, 0.0, 0, 0, "")
        self.time_sink_decim.enable_autoscale(True)
        self.time_sink_decim.enable_grid(True)
        self.time_sink_decim.enable_axis_labels(True)
        self.time_sink_decim.enable_control_panel(False)
        self.time_sink_decim.enable_stem_plot(False)


        labels = ['Sem filtro AA', 'Com filtro AA', 'Signal 3', 'Signal 4', 'Signal 5',
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
                self.time_sink_decim.set_line_label(i, "Data {0}".format(i))
            else:
                self.time_sink_decim.set_line_label(i, labels[i])
            self.time_sink_decim.set_line_width(i, widths[i])
            self.time_sink_decim.set_line_color(i, colors[i])
            self.time_sink_decim.set_line_style(i, styles[i])
            self.time_sink_decim.set_line_marker(i, markers[i])
            self.time_sink_decim.set_line_alpha(i, alphas[i])

        self._time_sink_decim_win = sip.wrapinstance(self.time_sink_decim.qwidget(), Qt.QWidget)
        self.top_grid_layout.addWidget(self._time_sink_decim_win, 3, 0, 1, 1)
        for r in range(3, 4):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 1):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.throttle = blocks.throttle( gr.sizeof_float*1, samp_rate, True, 0 if "auto" == "auto" else max( int(float(0.1) * samp_rate) if "auto" == "time" else int(0.1), 1) )
        self.src_sinal = analog.sig_source_f(samp_rate, analog.GR_SQR_WAVE, f_sinal, 1.0, 0, 0)
        self.lpf_aa = filter.fir_filter_fff(
            1,
            firdes.low_pass(
                1,
                samp_rate,
                (fs_eff/2*0.9),
                200,
                window.WIN_HAMMING,
                6.76))
        self.keep_1_in_n_sem_filtro = blocks.keep_one_in_n(gr.sizeof_float*1, decim)
        self.keep_1_in_n_com_filtro = blocks.keep_one_in_n(gr.sizeof_float*1, decim)
        self.freq_sink_original = qtgui.freq_sink_f(
            4096, #size
            window.WIN_HANN, #wintype
            0, #fc
            samp_rate, #bw
            "Espectro Original", #name
            1,
            None # parent
        )
        self.freq_sink_original.set_update_time(0.10)
        self.freq_sink_original.set_y_axis((-100), 10)
        self.freq_sink_original.set_y_label('Relative Gain', 'dB')
        self.freq_sink_original.set_trigger_mode(qtgui.TRIG_MODE_FREE, 0.0, 0, "")
        self.freq_sink_original.enable_autoscale(False)
        self.freq_sink_original.enable_grid(True)
        self.freq_sink_original.set_fft_average(1.0)
        self.freq_sink_original.enable_axis_labels(True)
        self.freq_sink_original.enable_control_panel(False)
        self.freq_sink_original.set_fft_window_normalized(False)


        self.freq_sink_original.set_plot_pos_half(not True)

        labels = ['Sinal original', '', '', '', '',
            '', '', '', '', '']
        widths = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        colors = ["blue", "red", "green", "black", "cyan",
            "magenta", "yellow", "dark red", "dark green", "dark blue"]
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0, 1.0, 1.0]

        for i in range(1):
            if len(labels[i]) == 0:
                self.freq_sink_original.set_line_label(i, "Data {0}".format(i))
            else:
                self.freq_sink_original.set_line_label(i, labels[i])
            self.freq_sink_original.set_line_width(i, widths[i])
            self.freq_sink_original.set_line_color(i, colors[i])
            self.freq_sink_original.set_line_alpha(i, alphas[i])

        self._freq_sink_original_win = sip.wrapinstance(self.freq_sink_original.qwidget(), Qt.QWidget)
        self.top_grid_layout.addWidget(self._freq_sink_original_win, 2, 1, 1, 1)
        for r in range(2, 3):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(1, 2):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.freq_sink_decim = qtgui.freq_sink_f(
            4096, #size
            window.WIN_HANN, #wintype
            0, #fc
            fs_eff, #bw
            "Espectro Decimado", #name
            2,
            None # parent
        )
        self.freq_sink_decim.set_update_time(0.10)
        self.freq_sink_decim.set_y_axis((-100), 10)
        self.freq_sink_decim.set_y_label('Relative Gain', 'dB')
        self.freq_sink_decim.set_trigger_mode(qtgui.TRIG_MODE_FREE, 0.0, 0, "")
        self.freq_sink_decim.enable_autoscale(False)
        self.freq_sink_decim.enable_grid(True)
        self.freq_sink_decim.set_fft_average(1.0)
        self.freq_sink_decim.enable_axis_labels(True)
        self.freq_sink_decim.enable_control_panel(False)
        self.freq_sink_decim.set_fft_window_normalized(False)


        self.freq_sink_decim.set_plot_pos_half(not True)

        labels = ['Sem filtro AA', 'Com filtro AA', '', '', '',
            '', '', '', '', '']
        widths = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        colors = ["blue", "red", "green", "black", "cyan",
            "magenta", "yellow", "dark red", "dark green", "dark blue"]
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0, 1.0, 1.0]

        for i in range(2):
            if len(labels[i]) == 0:
                self.freq_sink_decim.set_line_label(i, "Data {0}".format(i))
            else:
                self.freq_sink_decim.set_line_label(i, labels[i])
            self.freq_sink_decim.set_line_width(i, widths[i])
            self.freq_sink_decim.set_line_color(i, colors[i])
            self.freq_sink_decim.set_line_alpha(i, alphas[i])

        self._freq_sink_decim_win = sip.wrapinstance(self.freq_sink_decim.qwidget(), Qt.QWidget)
        self.top_grid_layout.addWidget(self._freq_sink_decim_win, 3, 1, 1, 1)
        for r in range(3, 4):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(1, 2):
            self.top_grid_layout.setColumnStretch(c, 1)


        ##################################################
        # Connections
        ##################################################
        self.connect((self.keep_1_in_n_com_filtro, 0), (self.freq_sink_decim, 1))
        self.connect((self.keep_1_in_n_com_filtro, 0), (self.time_sink_decim, 1))
        self.connect((self.keep_1_in_n_sem_filtro, 0), (self.freq_sink_decim, 0))
        self.connect((self.keep_1_in_n_sem_filtro, 0), (self.time_sink_decim, 0))
        self.connect((self.lpf_aa, 0), (self.keep_1_in_n_com_filtro, 0))
        self.connect((self.src_sinal, 0), (self.throttle, 0))
        self.connect((self.throttle, 0), (self.freq_sink_original, 0))
        self.connect((self.throttle, 0), (self.keep_1_in_n_sem_filtro, 0))
        self.connect((self.throttle, 0), (self.lpf_aa, 0))
        self.connect((self.throttle, 0), (self.time_sink_original, 0))


    def closeEvent(self, event):
        self.settings = Qt.QSettings("gnuradio/flowgraphs", "pratica_08_amostragem_aliasing")
        self.settings.setValue("geometry", self.saveGeometry())
        self.stop()
        self.wait()

        event.accept()

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.set_fs_eff(self.samp_rate/self.decim)
        self.freq_sink_original.set_frequency_range(0, self.samp_rate)
        self.lpf_aa.set_taps(firdes.low_pass(1, self.samp_rate, (self.fs_eff/2*0.9), 200, window.WIN_HAMMING, 6.76))
        self.src_sinal.set_sampling_freq(self.samp_rate)
        self.throttle.set_sample_rate(self.samp_rate)
        self.time_sink_original.set_samp_rate(self.samp_rate)

    def get_decim(self):
        return self.decim

    def set_decim(self, decim):
        self.decim = decim
        self.set_fs_eff(self.samp_rate/self.decim)
        self.keep_1_in_n_com_filtro.set_n(self.decim)
        self.keep_1_in_n_sem_filtro.set_n(self.decim)

    def get_fs_eff(self):
        return self.fs_eff

    def set_fs_eff(self, fs_eff):
        self.fs_eff = fs_eff
        self.freq_sink_decim.set_frequency_range(0, self.fs_eff)
        self.lpf_aa.set_taps(firdes.low_pass(1, self.samp_rate, (self.fs_eff/2*0.9), 200, window.WIN_HAMMING, 6.76))
        self.time_sink_decim.set_samp_rate(self.fs_eff)

    def get_f_sinal(self):
        return self.f_sinal

    def set_f_sinal(self, f_sinal):
        self.f_sinal = f_sinal
        self.src_sinal.set_frequency(self.f_sinal)




def main(top_block_cls=pratica_08_amostragem_aliasing, options=None):

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
