#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: Exemplo 03 - Atraso de Grupo
# Author: Curso PriCom - UnB
# Description: Exemplo 03 - Atraso de Grupo em Canal LTI
# GNU Radio version: 3.10.12.0

from PyQt5 import Qt
from gnuradio import qtgui
from gnuradio import analog
from gnuradio import blocks
from gnuradio import filter
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



class exemplo_03_atraso_grupo(gr.top_block, Qt.QWidget):

    def __init__(self):
        gr.top_block.__init__(self, "Exemplo 03 - Atraso de Grupo", catch_exceptions=True)
        Qt.QWidget.__init__(self)
        self.setWindowTitle("Exemplo 03 - Atraso de Grupo")
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

        self.settings = Qt.QSettings("gnuradio/flowgraphs", "exemplo_03_atraso_grupo")

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
        self.freq3 = freq3 = 3500
        self.freq2 = freq2 = 1200
        self.freq1 = freq1 = 300
        self.coef_a = coef_a = 0.95

        ##################################################
        # Blocks
        ##################################################

        self.qtgui_time_sink = qtgui.time_sink_f(
            2048, #size
            samp_rate, #samp_rate
            "Dominio do Tempo - Efeito do Atraso de Grupo", #name
            2, #number of inputs
            None # parent
        )
        self.qtgui_time_sink.set_update_time(0.10)
        self.qtgui_time_sink.set_y_axis(-3.5, 3.5)

        self.qtgui_time_sink.set_y_label('Amplitude', "")

        self.qtgui_time_sink.enable_tags(True)
        self.qtgui_time_sink.set_trigger_mode(qtgui.TRIG_MODE_FREE, qtgui.TRIG_SLOPE_POS, 0.0, 0, 0, "")
        self.qtgui_time_sink.enable_autoscale(False)
        self.qtgui_time_sink.enable_grid(True)
        self.qtgui_time_sink.enable_axis_labels(True)
        self.qtgui_time_sink.enable_control_panel(False)
        self.qtgui_time_sink.enable_stem_plot(False)


        labels = ['Original', 'Apos canal (atraso de grupo variavel)', 'Signal 3', 'Signal 4', 'Signal 5',
            'Signal 6', 'Signal 7', 'Signal 8', 'Signal 9', 'Signal 10']
        widths = [2, 2, 1, 1, 1,
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
                self.qtgui_time_sink.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_time_sink.set_line_label(i, labels[i])
            self.qtgui_time_sink.set_line_width(i, widths[i])
            self.qtgui_time_sink.set_line_color(i, colors[i])
            self.qtgui_time_sink.set_line_style(i, styles[i])
            self.qtgui_time_sink.set_line_marker(i, markers[i])
            self.qtgui_time_sink.set_line_alpha(i, alphas[i])

        self._qtgui_time_sink_win = sip.wrapinstance(self.qtgui_time_sink.qwidget(), Qt.QWidget)
        self.top_grid_layout.addWidget(self._qtgui_time_sink_win, 0, 0, 1, 1)
        for r in range(0, 1):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 1):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.qtgui_freq_sink = qtgui.freq_sink_f(
            4096, #size
            window.WIN_BLACKMAN_hARRIS, #wintype
            0, #fc
            samp_rate, #bw
            "Dominio da Frequencia - Magnitude Preservada", #name
            2,
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

        labels = ['Original', 'Apos canal', '', '', '',
            '', '', '', '', '']
        widths = [2, 2, 1, 1, 1,
            1, 1, 1, 1, 1]
        colors = ["blue", "red", "green", "black", "cyan",
            "magenta", "yellow", "dark red", "dark green", "dark blue"]
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0, 1.0, 1.0]

        for i in range(2):
            if len(labels[i]) == 0:
                self.qtgui_freq_sink.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_freq_sink.set_line_label(i, labels[i])
            self.qtgui_freq_sink.set_line_width(i, widths[i])
            self.qtgui_freq_sink.set_line_color(i, colors[i])
            self.qtgui_freq_sink.set_line_alpha(i, alphas[i])

        self._qtgui_freq_sink_win = sip.wrapinstance(self.qtgui_freq_sink.qwidget(), Qt.QWidget)
        self.top_grid_layout.addWidget(self._qtgui_freq_sink_win, 1, 0, 1, 1)
        for r in range(1, 2):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 1):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.iir_allpass_4 = filter.iir_filter_ffd([coef_a, 1], [1, coef_a], True)
        self.iir_allpass_3 = filter.iir_filter_ffd([coef_a, 1], [1, coef_a], True)
        self.iir_allpass_2 = filter.iir_filter_ffd([coef_a, 1], [1, coef_a], True)
        self.iir_allpass_1 = filter.iir_filter_ffd([coef_a, 1], [1, coef_a], True)
        self.cos3 = analog.sig_source_f(samp_rate, analog.GR_COS_WAVE, freq3, 1, 0, 0)
        self.cos2 = analog.sig_source_f(samp_rate, analog.GR_COS_WAVE, freq2, 1, 0, 0)
        self.cos1 = analog.sig_source_f(samp_rate, analog.GR_COS_WAVE, freq1, 1, 0, 0)
        self.blocks_throttle = blocks.throttle( gr.sizeof_float*1, samp_rate, True, 0 if "auto" == "auto" else max( int(float(0.1) * samp_rate) if "auto" == "time" else int(0.1), 1) )
        self.blocks_add = blocks.add_vff(1)


        ##################################################
        # Connections
        ##################################################
        self.connect((self.blocks_add, 0), (self.blocks_throttle, 0))
        self.connect((self.blocks_throttle, 0), (self.iir_allpass_1, 0))
        self.connect((self.blocks_throttle, 0), (self.qtgui_freq_sink, 0))
        self.connect((self.blocks_throttle, 0), (self.qtgui_time_sink, 0))
        self.connect((self.cos1, 0), (self.blocks_add, 0))
        self.connect((self.cos2, 0), (self.blocks_add, 1))
        self.connect((self.cos3, 0), (self.blocks_add, 2))
        self.connect((self.iir_allpass_1, 0), (self.iir_allpass_2, 0))
        self.connect((self.iir_allpass_2, 0), (self.iir_allpass_3, 0))
        self.connect((self.iir_allpass_3, 0), (self.iir_allpass_4, 0))
        self.connect((self.iir_allpass_4, 0), (self.qtgui_freq_sink, 1))
        self.connect((self.iir_allpass_4, 0), (self.qtgui_time_sink, 1))


    def closeEvent(self, event):
        self.settings = Qt.QSettings("gnuradio/flowgraphs", "exemplo_03_atraso_grupo")
        self.settings.setValue("geometry", self.saveGeometry())
        self.stop()
        self.wait()

        event.accept()

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.blocks_throttle.set_sample_rate(self.samp_rate)
        self.cos1.set_sampling_freq(self.samp_rate)
        self.cos2.set_sampling_freq(self.samp_rate)
        self.cos3.set_sampling_freq(self.samp_rate)
        self.qtgui_freq_sink.set_frequency_range(0, self.samp_rate)
        self.qtgui_time_sink.set_samp_rate(self.samp_rate)

    def get_freq3(self):
        return self.freq3

    def set_freq3(self, freq3):
        self.freq3 = freq3
        self.cos3.set_frequency(self.freq3)

    def get_freq2(self):
        return self.freq2

    def set_freq2(self, freq2):
        self.freq2 = freq2
        self.cos2.set_frequency(self.freq2)

    def get_freq1(self):
        return self.freq1

    def set_freq1(self, freq1):
        self.freq1 = freq1
        self.cos1.set_frequency(self.freq1)

    def get_coef_a(self):
        return self.coef_a

    def set_coef_a(self, coef_a):
        self.coef_a = coef_a
        self.iir_allpass_1.set_taps([self.coef_a, 1], [1, self.coef_a])
        self.iir_allpass_2.set_taps([self.coef_a, 1], [1, self.coef_a])
        self.iir_allpass_3.set_taps([self.coef_a, 1], [1, self.coef_a])
        self.iir_allpass_4.set_taps([self.coef_a, 1], [1, self.coef_a])




def main(top_block_cls=exemplo_03_atraso_grupo, options=None):

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
