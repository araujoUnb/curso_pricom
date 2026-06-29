#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: Demo: Formatação de Pulso, ISI e Diagrama de Olho
# Author: Prof. Daniel Costa Araújo
# Description: Formatação de pulso (RRC), ISI e diagrama de olho
# GNU Radio version: 3.10.12.0

from PyQt5 import Qt
from gnuradio import qtgui
from PyQt5 import QtCore
from gnuradio import analog
from gnuradio import blocks
from gnuradio import digital
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



class demo_pulse_shaping_olho(gr.top_block, Qt.QWidget):

    def __init__(self):
        gr.top_block.__init__(self, "Demo: Formatação de Pulso, ISI e Diagrama de Olho", catch_exceptions=True)
        Qt.QWidget.__init__(self)
        self.setWindowTitle("Demo: Formatação de Pulso, ISI e Diagrama de Olho")
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

        self.settings = Qt.QSettings("gnuradio/flowgraphs", "demo_pulse_shaping_olho")

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
        self.sps = sps = 8
        self.samp_rate = samp_rate = 32000
        self.sym_rate = sym_rate = samp_rate/sps
        self.ntaps = ntaps = 11*sps+1
        self.noise_amp = noise_amp = 0.0
        self.alpha = alpha = 0.35

        ##################################################
        # Blocks
        ##################################################

        self._alpha_range = qtgui.Range(0.0, 1.0, 0.05, 0.35, 200)
        self._alpha_win = qtgui.RangeWidget(self._alpha_range, self.set_alpha, "Roll-off alpha", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_grid_layout.addWidget(self._alpha_win, 0, 0, 1, 1)
        for r in range(0, 1):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 1):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.tx_rrc = filter.interp_fir_filter_fff(
            sps,
            firdes.root_raised_cosine(
                sps,
                samp_rate,
                sym_rate,
                alpha,
                ntaps))
        self.time_sink_tx = qtgui.time_sink_f(
            512, #size
            samp_rate, #samp_rate
            "Formata\xE7\xE3o de Pulso RRC (tempo)", #name
            1, #number of inputs
            None # parent
        )
        self.time_sink_tx.set_update_time(0.10)
        self.time_sink_tx.set_y_axis(-2, 2)

        self.time_sink_tx.set_y_label('Amplitude', "")

        self.time_sink_tx.enable_tags(True)
        self.time_sink_tx.set_trigger_mode(qtgui.TRIG_MODE_FREE, qtgui.TRIG_SLOPE_POS, 0.0, 0, 0, "")
        self.time_sink_tx.enable_autoscale(True)
        self.time_sink_tx.enable_grid(True)
        self.time_sink_tx.enable_axis_labels(True)
        self.time_sink_tx.enable_control_panel(False)
        self.time_sink_tx.enable_stem_plot(False)


        labels = ['Signal 1', 'Signal 2', 'Signal 3', 'Signal 4', 'Signal 5',
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
                self.time_sink_tx.set_line_label(i, "Data {0}".format(i))
            else:
                self.time_sink_tx.set_line_label(i, labels[i])
            self.time_sink_tx.set_line_width(i, widths[i])
            self.time_sink_tx.set_line_color(i, colors[i])
            self.time_sink_tx.set_line_style(i, styles[i])
            self.time_sink_tx.set_line_marker(i, markers[i])
            self.time_sink_tx.set_line_alpha(i, alphas[i])

        self._time_sink_tx_win = sip.wrapinstance(self.time_sink_tx.qwidget(), Qt.QWidget)
        self.top_grid_layout.addWidget(self._time_sink_tx_win, 1, 0, 1, 1)
        for r in range(1, 2):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 1):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.throttle = blocks.throttle( gr.sizeof_float*1, sym_rate, True, 0 if "auto" == "auto" else max( int(float(0.1) * sym_rate) if "auto" == "time" else int(0.1), 1) )
        self.rx_rrc = filter.fir_filter_fff(
            1,
            firdes.root_raised_cosine(
                1,
                samp_rate,
                sym_rate,
                alpha,
                ntaps))
        self._noise_amp_range = qtgui.Range(0.0, 0.6, 0.02, 0.0, 200)
        self._noise_amp_win = qtgui.RangeWidget(self._noise_amp_range, self.set_noise_amp, "Ruído do canal (AWGN)", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_grid_layout.addWidget(self._noise_amp_win, 0, 1, 1, 1)
        for r in range(0, 1):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(1, 2):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.noise = analog.noise_source_f(analog.GR_GAUSSIAN, noise_amp, 0)
        self.glfsr = digital.glfsr_source_b(8, True, 0, 1)
        self.freq_sink_tx = qtgui.freq_sink_f(
            2048, #size
            window.WIN_BLACKMAN_hARRIS, #wintype
            0, #fc
            samp_rate, #bw
            "Espectro do sinal formatado", #name
            1,
            None # parent
        )
        self.freq_sink_tx.set_update_time(0.10)
        self.freq_sink_tx.set_y_axis((-100), 10)
        self.freq_sink_tx.set_y_label('Relative Gain', 'dB')
        self.freq_sink_tx.set_trigger_mode(qtgui.TRIG_MODE_FREE, 0.0, 0, "")
        self.freq_sink_tx.enable_autoscale(False)
        self.freq_sink_tx.enable_grid(True)
        self.freq_sink_tx.set_fft_average(1.0)
        self.freq_sink_tx.enable_axis_labels(True)
        self.freq_sink_tx.enable_control_panel(False)
        self.freq_sink_tx.set_fft_window_normalized(False)


        self.freq_sink_tx.set_plot_pos_half(not True)

        labels = ['', '', '', '', '',
            '', '', '', '', '']
        widths = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        colors = ["blue", "red", "green", "black", "cyan",
            "magenta", "yellow", "dark red", "dark green", "dark blue"]
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0, 1.0, 1.0]

        for i in range(1):
            if len(labels[i]) == 0:
                self.freq_sink_tx.set_line_label(i, "Data {0}".format(i))
            else:
                self.freq_sink_tx.set_line_label(i, labels[i])
            self.freq_sink_tx.set_line_width(i, widths[i])
            self.freq_sink_tx.set_line_color(i, colors[i])
            self.freq_sink_tx.set_line_alpha(i, alphas[i])

        self._freq_sink_tx_win = sip.wrapinstance(self.freq_sink_tx.qwidget(), Qt.QWidget)
        self.top_grid_layout.addWidget(self._freq_sink_tx_win, 1, 1, 1, 1)
        for r in range(1, 2):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(1, 2):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.eye_sink_rx = qtgui.eye_sink_f(
            1024, #size
            samp_rate, #samp_rate
            1, #number of inputs
            None
        )
        self.eye_sink_rx.set_update_time(0.10)
        self.eye_sink_rx.set_samp_per_symbol(sps)
        self.eye_sink_rx.set_y_axis(-2.5, 2.5)

        self.eye_sink_rx.set_y_label('Amplitude', "")

        self.eye_sink_rx.enable_tags(True)
        self.eye_sink_rx.set_trigger_mode(qtgui.TRIG_MODE_FREE, qtgui.TRIG_SLOPE_POS, 0.0, 0, 0, "")
        self.eye_sink_rx.enable_autoscale(False)
        self.eye_sink_rx.enable_grid(True)
        self.eye_sink_rx.enable_axis_labels(True)
        self.eye_sink_rx.enable_control_panel(False)


        labels = ['Signal 1', 'Signal 2', 'Signal 3', 'Signal 4', 'Signal 5',
            'Signal 6', 'Signal 7', 'Signal 8', 'Signal 9', 'Signal 10']
        widths = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        colors = ['blue', 'blue', 'blue', 'blue', 'blue',
            'blue', 'blue', 'blue', 'blue', 'blue']
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0, 1.0, 1.0]
        styles = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        markers = [-1, -1, -1, -1, -1,
            -1, -1, -1, -1, -1]


        for i in range(1):
            if len(labels[i]) == 0:
                self.eye_sink_rx.set_line_label(i, "Eye[Data {0}]".format(i))
            else:
                self.eye_sink_rx.set_line_label(i, labels[i])
            self.eye_sink_rx.set_line_width(i, widths[i])
            self.eye_sink_rx.set_line_color(i, colors[i])
            self.eye_sink_rx.set_line_style(i, styles[i])
            self.eye_sink_rx.set_line_marker(i, markers[i])
            self.eye_sink_rx.set_line_alpha(i, alphas[i])

        self._eye_sink_rx_win = sip.wrapinstance(self.eye_sink_rx.qwidget(), Qt.QWidget)
        self.top_grid_layout.addWidget(self._eye_sink_rx_win, 2, 0, 1, 2)
        for r in range(2, 3):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 2):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.chunks_to_symbols = digital.chunks_to_symbols_bf([-1, 1], 1)
        self.add_canal = blocks.add_vff(1)


        ##################################################
        # Connections
        ##################################################
        self.connect((self.add_canal, 0), (self.rx_rrc, 0))
        self.connect((self.chunks_to_symbols, 0), (self.throttle, 0))
        self.connect((self.glfsr, 0), (self.chunks_to_symbols, 0))
        self.connect((self.noise, 0), (self.add_canal, 1))
        self.connect((self.rx_rrc, 0), (self.eye_sink_rx, 0))
        self.connect((self.throttle, 0), (self.tx_rrc, 0))
        self.connect((self.tx_rrc, 0), (self.add_canal, 0))
        self.connect((self.tx_rrc, 0), (self.freq_sink_tx, 0))
        self.connect((self.tx_rrc, 0), (self.time_sink_tx, 0))


    def closeEvent(self, event):
        self.settings = Qt.QSettings("gnuradio/flowgraphs", "demo_pulse_shaping_olho")
        self.settings.setValue("geometry", self.saveGeometry())
        self.stop()
        self.wait()

        event.accept()

    def get_sps(self):
        return self.sps

    def set_sps(self, sps):
        self.sps = sps
        self.set_sym_rate(self.samp_rate/self.sps)
        self.set_ntaps(11*self.sps+1)
        self.tx_rrc.set_taps(firdes.root_raised_cosine(self.sps, self.samp_rate, self.sym_rate, self.alpha, self.ntaps))
        self.eye_sink_rx.set_samp_per_symbol(self.sps)

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.set_sym_rate(self.samp_rate/self.sps)
        self.tx_rrc.set_taps(firdes.root_raised_cosine(self.sps, self.samp_rate, self.sym_rate, self.alpha, self.ntaps))
        self.rx_rrc.set_taps(firdes.root_raised_cosine(1, self.samp_rate, self.sym_rate, self.alpha, self.ntaps))
        self.time_sink_tx.set_samp_rate(self.samp_rate)
        self.freq_sink_tx.set_frequency_range(0, self.samp_rate)
        self.eye_sink_rx.set_samp_rate(self.samp_rate)

    def get_sym_rate(self):
        return self.sym_rate

    def set_sym_rate(self, sym_rate):
        self.sym_rate = sym_rate
        self.throttle.set_sample_rate(self.sym_rate)
        self.tx_rrc.set_taps(firdes.root_raised_cosine(self.sps, self.samp_rate, self.sym_rate, self.alpha, self.ntaps))
        self.rx_rrc.set_taps(firdes.root_raised_cosine(1, self.samp_rate, self.sym_rate, self.alpha, self.ntaps))

    def get_ntaps(self):
        return self.ntaps

    def set_ntaps(self, ntaps):
        self.ntaps = ntaps
        self.tx_rrc.set_taps(firdes.root_raised_cosine(self.sps, self.samp_rate, self.sym_rate, self.alpha, self.ntaps))
        self.rx_rrc.set_taps(firdes.root_raised_cosine(1, self.samp_rate, self.sym_rate, self.alpha, self.ntaps))

    def get_noise_amp(self):
        return self.noise_amp

    def set_noise_amp(self, noise_amp):
        self.noise_amp = noise_amp
        self.noise.set_amplitude(self.noise_amp)

    def get_alpha(self):
        return self.alpha

    def set_alpha(self, alpha):
        self.alpha = alpha
        self.tx_rrc.set_taps(firdes.root_raised_cosine(self.sps, self.samp_rate, self.sym_rate, self.alpha, self.ntaps))
        self.rx_rrc.set_taps(firdes.root_raised_cosine(1, self.samp_rate, self.sym_rate, self.alpha, self.ntaps))




def main(top_block_cls=demo_pulse_shaping_olho, options=None):

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
