#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: Exemplo 05 - Comparacao LPF vs BPF
# Author: Curso PriCom - UnB
# Description: Comparacao de Filtros Praticos
# GNU Radio version: 3.10.12.0

from PyQt5 import Qt
from gnuradio import qtgui
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



class exemplo_05_comparacao_filtros(gr.top_block, Qt.QWidget):

    def __init__(self):
        gr.top_block.__init__(self, "Exemplo 05 - Comparacao LPF vs BPF", catch_exceptions=True)
        Qt.QWidget.__init__(self)
        self.setWindowTitle("Exemplo 05 - Comparacao LPF vs BPF")
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

        self.settings = Qt.QSettings("gnuradio/flowgraphs", "exemplo_05_comparacao_filtros")

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
        self.fc_lp = fc_lp = 2000
        self.fc_bp_low = fc_bp_low = 1000
        self.fc_bp_high = fc_bp_high = 3000

        ##################################################
        # Blocks
        ##################################################

        self.qtgui_time_sink = qtgui.time_sink_f(
            2048, #size
            samp_rate, #samp_rate
            "Tempo - LPF vs BPF", #name
            3, #number of inputs
            None # parent
        )
        self.qtgui_time_sink.set_update_time(0.10)
        self.qtgui_time_sink.set_y_axis(-3, 3)

        self.qtgui_time_sink.set_y_label('Amplitude', "")

        self.qtgui_time_sink.enable_tags(True)
        self.qtgui_time_sink.set_trigger_mode(qtgui.TRIG_MODE_FREE, qtgui.TRIG_SLOPE_POS, 0.0, 0, 0, "")
        self.qtgui_time_sink.enable_autoscale(True)
        self.qtgui_time_sink.enable_grid(True)
        self.qtgui_time_sink.enable_axis_labels(True)
        self.qtgui_time_sink.enable_control_panel(False)
        self.qtgui_time_sink.enable_stem_plot(False)


        labels = ['Original', 'Passa-Baixas', 'Passa-Faixa', 'Signal 4', 'Signal 5',
            'Signal 6', 'Signal 7', 'Signal 8', 'Signal 9', 'Signal 10']
        widths = [2, 2, 2, 1, 1,
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
                self.qtgui_time_sink.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_time_sink.set_line_label(i, labels[i])
            self.qtgui_time_sink.set_line_width(i, widths[i])
            self.qtgui_time_sink.set_line_color(i, colors[i])
            self.qtgui_time_sink.set_line_style(i, styles[i])
            self.qtgui_time_sink.set_line_marker(i, markers[i])
            self.qtgui_time_sink.set_line_alpha(i, alphas[i])

        self._qtgui_time_sink_win = sip.wrapinstance(self.qtgui_time_sink.qwidget(), Qt.QWidget)
        self.top_grid_layout.addWidget(self._qtgui_time_sink_win, 1, 0, 1, 1)
        for r in range(1, 2):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 1):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.qtgui_freq_sink = qtgui.freq_sink_f(
            4096, #size
            window.WIN_BLACKMAN_hARRIS, #wintype
            0, #fc
            samp_rate, #bw
            "Espectro - LPF vs BPF", #name
            3,
            None # parent
        )
        self.qtgui_freq_sink.set_update_time(0.10)
        self.qtgui_freq_sink.set_y_axis((-80), 10)
        self.qtgui_freq_sink.set_y_label('Relative Gain', 'dB')
        self.qtgui_freq_sink.set_trigger_mode(qtgui.TRIG_MODE_FREE, 0.0, 0, "")
        self.qtgui_freq_sink.enable_autoscale(False)
        self.qtgui_freq_sink.enable_grid(True)
        self.qtgui_freq_sink.set_fft_average(1.0)
        self.qtgui_freq_sink.enable_axis_labels(True)
        self.qtgui_freq_sink.enable_control_panel(False)
        self.qtgui_freq_sink.set_fft_window_normalized(False)


        self.qtgui_freq_sink.set_plot_pos_half(not True)

        labels = ['Original', 'Passa-Baixas (fc=2kHz)', 'Passa-Faixa (1-3kHz)', '', '',
            '', '', '', '', '']
        widths = [2, 2, 2, 1, 1,
            1, 1, 1, 1, 1]
        colors = ["blue", "red", "green", "black", "cyan",
            "magenta", "yellow", "dark red", "dark green", "dark blue"]
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0, 1.0, 1.0]

        for i in range(3):
            if len(labels[i]) == 0:
                self.qtgui_freq_sink.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_freq_sink.set_line_label(i, labels[i])
            self.qtgui_freq_sink.set_line_width(i, widths[i])
            self.qtgui_freq_sink.set_line_color(i, colors[i])
            self.qtgui_freq_sink.set_line_alpha(i, alphas[i])

        self._qtgui_freq_sink_win = sip.wrapinstance(self.qtgui_freq_sink.qwidget(), Qt.QWidget)
        self.top_grid_layout.addWidget(self._qtgui_freq_sink_win, 0, 0, 1, 1)
        for r in range(0, 1):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 1):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.low_pass_filter = filter.fir_filter_fff(
            1,
            firdes.low_pass(
                1,
                samp_rate,
                fc_lp,
                200,
                window.WIN_HAMMING,
                6.76))
        self.cos_5000 = analog.sig_source_f(samp_rate, analog.GR_COS_WAVE, 5000, 1, 0, 0)
        self.cos_500 = analog.sig_source_f(samp_rate, analog.GR_COS_WAVE, 500, 1, 0, 0)
        self.cos_2000 = analog.sig_source_f(samp_rate, analog.GR_COS_WAVE, 2000, 1, 0, 0)
        self.blocks_throttle = blocks.throttle( gr.sizeof_float*1, samp_rate, True, 0 if "auto" == "auto" else max( int(float(0.1) * samp_rate) if "auto" == "time" else int(0.1), 1) )
        self.blocks_add = blocks.add_vff(1)
        self.band_pass_filter = filter.fir_filter_fff(
            1,
            firdes.band_pass(
                1,
                samp_rate,
                fc_bp_low,
                fc_bp_high,
                200,
                window.WIN_HAMMING,
                6.76))


        ##################################################
        # Connections
        ##################################################
        self.connect((self.band_pass_filter, 0), (self.qtgui_freq_sink, 2))
        self.connect((self.band_pass_filter, 0), (self.qtgui_time_sink, 2))
        self.connect((self.blocks_add, 0), (self.blocks_throttle, 0))
        self.connect((self.blocks_throttle, 0), (self.band_pass_filter, 0))
        self.connect((self.blocks_throttle, 0), (self.low_pass_filter, 0))
        self.connect((self.blocks_throttle, 0), (self.qtgui_freq_sink, 0))
        self.connect((self.blocks_throttle, 0), (self.qtgui_time_sink, 0))
        self.connect((self.cos_2000, 0), (self.blocks_add, 1))
        self.connect((self.cos_500, 0), (self.blocks_add, 0))
        self.connect((self.cos_5000, 0), (self.blocks_add, 2))
        self.connect((self.low_pass_filter, 0), (self.qtgui_freq_sink, 1))
        self.connect((self.low_pass_filter, 0), (self.qtgui_time_sink, 1))


    def closeEvent(self, event):
        self.settings = Qt.QSettings("gnuradio/flowgraphs", "exemplo_05_comparacao_filtros")
        self.settings.setValue("geometry", self.saveGeometry())
        self.stop()
        self.wait()

        event.accept()

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.cos_500.set_sampling_freq(self.samp_rate)
        self.cos_2000.set_sampling_freq(self.samp_rate)
        self.cos_5000.set_sampling_freq(self.samp_rate)
        self.blocks_throttle.set_sample_rate(self.samp_rate)
        self.low_pass_filter.set_taps(firdes.low_pass(1, self.samp_rate, self.fc_lp, 200, window.WIN_HAMMING, 6.76))
        self.band_pass_filter.set_taps(firdes.band_pass(1, self.samp_rate, self.fc_bp_low, self.fc_bp_high, 200, window.WIN_HAMMING, 6.76))
        self.qtgui_freq_sink.set_frequency_range(0, self.samp_rate)
        self.qtgui_time_sink.set_samp_rate(self.samp_rate)

    def get_fc_lp(self):
        return self.fc_lp

    def set_fc_lp(self, fc_lp):
        self.fc_lp = fc_lp
        self.low_pass_filter.set_taps(firdes.low_pass(1, self.samp_rate, self.fc_lp, 200, window.WIN_HAMMING, 6.76))

    def get_fc_bp_low(self):
        return self.fc_bp_low

    def set_fc_bp_low(self, fc_bp_low):
        self.fc_bp_low = fc_bp_low
        self.band_pass_filter.set_taps(firdes.band_pass(1, self.samp_rate, self.fc_bp_low, self.fc_bp_high, 200, window.WIN_HAMMING, 6.76))

    def get_fc_bp_high(self):
        return self.fc_bp_high

    def set_fc_bp_high(self, fc_bp_high):
        self.fc_bp_high = fc_bp_high
        self.band_pass_filter.set_taps(firdes.band_pass(1, self.samp_rate, self.fc_bp_low, self.fc_bp_high, 200, window.WIN_HAMMING, 6.76))




def main(top_block_cls=exemplo_05_comparacao_filtros, options=None):

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
