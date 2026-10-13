# Gera os flowgraphs da radiodifusão FM (Proakis, seção 4.4) pela API do GRC,
# que preenche os parâmetros padrão e valida cada bloco.
# Uso: python gerar_grc.py  (no Python do GNU Radio 3.10)
import sys
from gnuradio import gr
from gnuradio.grc.core.platform import Platform

P = Platform(version=gr.version(), version_parts=(gr.major_version(), gr.api_version(), gr.minor_version()),
             prefs=gr.prefs(), install_prefix=gr.prefix())
P.build_library()


class Grafo:
    def __init__(self, ident, titulo, descricao, janela="(1600,1000)"):
        self.fg = P.make_flow_graph()
        opt = [b for b in self.fg.blocks if b.key == "options"][0]
        for k, v in dict(id=ident, title=titulo, description=descricao, author="Prof. Daniel Costa Araújo",
                         window_size=janela, generate_options="qt_gui", run_options="prompt").items():
            opt.params[k].set_value(v)
        opt.states["coordinate"] = (8, 8)
        self.ident = ident
        self.vy = 8

    def var(self, nome, valor, comentario=""):
        b = self.fg.new_block("variable")
        b.params["id"].set_value(nome); b.params["value"].set_value(str(valor)); b.params["comment"].set_value(comentario)
        b.states["coordinate"] = (8, self.vy + 150); self.vy += 92
        return b

    def bloco(self, chave, nome, xy, **par):
        b = self.fg.new_block(chave)
        b.params["id"].set_value(nome)
        for k, v in par.items():
            b.params[k].set_value(str(v))
        b.states["coordinate"] = xy
        b.rewrite()
        return b

    def liga(self, a, b, sa=0, sb=0):
        self.fg.rewrite()
        self.fg.connect(a.sources[sa], b.sinks[sb])

    def salva(self):
        self.fg.rewrite(); self.fg.validate()
        erros = list(self.fg.iter_error_messages())
        for e in erros:
            print("ERRO", self.ident, e)
        P.save_flow_graph(f"{self.ident}.grc", self.fg)
        print("salvo", self.ident, "válido" if not erros else f"{len(erros)} erros")
        return not erros


def col(i): return int(240 + 250 * i)
def lin(j): return int(40 + 170 * j)

FLT = dict(type="float")
COS = "analog.GR_COS_WAVE"

# ---------------------------------------------------------------- transmissor estéreo
g = Grafo("tx_estereo", "Transmissor FM estéreo (Fig. 4.17)",
          "Proakis 4.4: L+R, L-R em DSB-SC a 38 kHz, piloto de 19 kHz e modulador FM")
for n, v, c in [("samp_rate", 192000, "taxa do sinal composto"), ("rf_rate", 960000, "taxa do FM em banda base complexa"),
                ("f_l", 1000, "tom do canal esquerdo"), ("f_r", 3000, "tom do canal direito"), ("amp", 0.5, "amplitude de cada tom"),
                ("a", 0.45, "peso de L+R e de L-R no composto"), ("a_p", 0.1, "amplitude do piloto"),
                ("tau", 75e-6, "pré-ênfase, 75 us"), ("df", 75000, "desvio de pico"), ("n_arq", "int(0.1*samp_rate)", "amostras gravadas")]:
    g.var(n, v, c)
src_l = g.bloco("analog_sig_source_x", "esquerdo", (col(0), lin(0)), waveform=COS, samp_rate="samp_rate", freq="f_l", amp="amp", **FLT)
src_r = g.bloco("analog_sig_source_x", "direito", (col(0), lin(2)), waveform=COS, samp_rate="samp_rate", freq="f_r", amp="amp", **FLT)
soma = g.bloco("blocks_add_xx", "soma_lr", (col(1), lin(0)), num_inputs=2, **FLT)
dif = g.bloco("blocks_sub_xx", "dif_lr", (col(1), lin(2)), num_inputs=2, **FLT)
pre_s = g.bloco("analog_fm_preemph", "preenf_soma", (col(2), lin(0)), samp_rate="samp_rate", tau="tau", fh="-1.0")
pre_d = g.bloco("analog_fm_preemph", "preenf_dif", (col(2), lin(2)), samp_rate="samp_rate", tau="tau", fh="-1.0")
piloto = g.bloco("analog_sig_source_x", "piloto", (col(2), lin(4)), waveform=COS, samp_rate="samp_rate", freq="19000", amp="1", **FLT)
dobr = g.bloco("blocks_multiply_xx", "dobrador", (col(3), lin(4)), num_inputs=2, **FLT)
dobr_k = g.bloco("blocks_multiply_const_vxx", "dobrador_ganho", (col(4), lin(4)), const="2", **FLT)
dobr_c = g.bloco("blocks_add_const_vxx", "dobrador_dc", (col(5), lin(4)), const="-1", **FLT)
dsb = g.bloco("blocks_multiply_xx", "dsb_sc", (col(4), lin(2)), num_inputs=2, **FLT)
k_s = g.bloco("blocks_multiply_const_vxx", "peso_soma", (col(4), lin(0)), const="a", **FLT)
k_d = g.bloco("blocks_multiply_const_vxx", "peso_dif", (col(5), lin(2)), const="a", **FLT)
k_p = g.bloco("blocks_multiply_const_vxx", "peso_piloto", (col(3), lin(5)), const="a_p", **FLT)
comp = g.bloco("blocks_add_xx", "composto", (col(6), lin(1)), num_inputs=3, **FLT)
thr = g.bloco("blocks_throttle2", "throttle", (col(7), lin(1)), samples_per_second="samp_rate", **FLT)
head = g.bloco("blocks_head", "limite_arquivo", (col(8), lin(3)), num_items="n_arq", **FLT)
arq = g.bloco("blocks_file_sink", "arquivo_composto", (col(9), lin(3)), file="composto.f32", unbuffered="False", **FLT)
rs = g.bloco("rational_resampler_xxx", "reamostra", (col(8), lin(0)), type="fff", interp="5", decim="1", taps="firdes.low_pass(5, 5*samp_rate, 60e3, 30e3)")
fm = g.bloco("analog_frequency_modulator_fc", "modulador_fm", (col(9), lin(0)), sensitivity="2*3.141592653589793*df/rf_rate")
q_comp = g.bloco("qtgui_freq_sink_x", "espectro_composto", (col(8), lin(1)), type="float", freqhalf="False", name='"Sinal composto"', fftsize="4096",
                 bw="samp_rate", fc="0", ymin="-100", ymax="0", average="0.2", gui_hint="0,0,1,1")
q_t = g.bloco("qtgui_time_sink_x", "tempo_composto", (col(8), lin(2)), type="float", name='"Sinal composto no tempo"', size="1920",
              srate="samp_rate", ymin="-1", ymax="1", autoscale="False", gui_hint="1,0,1,1")
q_rf = g.bloco("qtgui_freq_sink_x", "espectro_fm", (col(10), lin(0)), type="complex", name='"Sinal FM em banda base"', fftsize="8192",
               bw="rf_rate", fc="0", ymin="-100", ymax="0", average="0.2", gui_hint="0,1,2,1")
g.liga(src_l, soma, 0, 0); g.liga(src_r, soma, 0, 1); g.liga(src_l, dif, 0, 0); g.liga(src_r, dif, 0, 1)
g.liga(soma, pre_s); g.liga(dif, pre_d)
g.liga(piloto, dobr, 0, 0); g.liga(piloto, dobr, 0, 1); g.liga(dobr, dobr_k); g.liga(dobr_k, dobr_c)
g.liga(pre_d, dsb, 0, 0); g.liga(dobr_c, dsb, 0, 1)
g.liga(pre_s, k_s); g.liga(dsb, k_d); g.liga(piloto, k_p)
g.liga(k_s, comp, 0, 0); g.liga(k_d, comp, 0, 1); g.liga(k_p, comp, 0, 2)
g.liga(comp, thr); g.liga(thr, head); g.liga(head, arq); g.liga(thr, rs); g.liga(rs, fm)
g.liga(thr, q_comp); g.liga(thr, q_t); g.liga(fm, q_rf)
ok1 = g.salva()

# ---------------------------------------------------------------- banda de FM na antena
g = Grafo("banda_fm", "Banda de FM na antena", "Cinco emissoras entre 88 e 108 MHz e um sinal AM aeronáutico na frequência imagem, a 480 MHz")
for n, v, c in [("rf_rate", 480000000, "taxa do sinal de RF real"), ("comp_rate", 192000, "taxa do composto gravado"), ("mod_rate", 960000, "taxa antes da repetição"),
                ("rep", "int(rf_rate/mod_rate)", "fator de repetição"), ("df", 75000, "desvio de pico"),
                ("f_sel", 97.9e6, "emissora estéreo"), ("f_img", "f_sel+2*10.7e6", "frequência imagem"),
                ("n_rf", "int(0.06*rf_rate)", "60 ms de RF")]:
    g.var(n, v, c)
fonte = g.bloco("blocks_file_source", "composto", (col(0), lin(0)), file="composto.f32", repeat="True", **FLT)
interp = g.bloco("rational_resampler_xxx", "reamostra", (col(1), lin(0)), type="fff", interp="5", decim="1", taps="firdes.low_pass(5, mod_rate, 60e3, 30e3)")
k_df = g.bloco("blocks_multiply_const_vxx", "desvio", (col(2), lin(0)), const="df", **FLT)
k_fc = g.bloco("blocks_add_const_vxx", "portadora", (col(3), lin(0)), const="f_sel", **FLT)
rep0 = g.bloco("blocks_repeat", "repete_sel", (col(4), lin(0)), interp="rep", **FLT)
vco0 = g.bloco("blocks_vco_f", "vco_978", (col(5), lin(0)), samp_rate="rf_rate", sensitivity="2*3.141592653589793", amplitude="1")
desv = g.bloco("analog_sig_source_x", "desvanecimento", (col(5), lin(1)), waveform=COS, samp_rate="rf_rate", freq="300", amp="0.3", offset="1", **FLT)
fad = g.bloco("blocks_multiply_xx", "com_desvanecimento", (col(6), lin(0)), num_inputs=2, **FLT)
soma = g.bloco("blocks_add_xx", "antena", (col(7), lin(2)), num_inputs=7, **FLT)
g.liga(fonte, interp); g.liga(interp, k_df); g.liga(k_df, k_fc); g.liga(k_fc, rep0); g.liga(rep0, vco0); g.liga(vco0, fad, 0, 0); g.liga(desv, fad, 0, 1)
g.liga(fad, soma, 0, 0)
mono = [(88.1e6, 400), (93.3e6, 700), (101.5e6, 1200), (105.7e6, 2000)]
for i, (fc, ft) in enumerate(mono):
    s = g.bloco("analog_sig_source_x", f"audio_{int(fc/1e5)}", (col(0), lin(2 + i)), waveform=COS, samp_rate="mod_rate",
                freq=str(ft), amp="0.8*df", offset=repr(fc), **FLT)
    r = g.bloco("blocks_repeat", f"repete_{int(fc/1e5)}", (col(2), lin(2 + i)), interp="rep", **FLT)
    v = g.bloco("blocks_vco_f", f"vco_{int(fc/1e5)}", (col(4), lin(2 + i)), samp_rate="rf_rate", sensitivity="2*3.141592653589793", amplitude="1")
    g.liga(s, r); g.liga(r, v); g.liga(v, soma, 0, 1 + i)
am_m = g.bloco("analog_sig_source_x", "audio_aero", (col(0), lin(6)), waveform=COS, samp_rate="mod_rate", freq="500", amp="0.5", offset="1", **FLT)
am_r = g.bloco("blocks_repeat", "repete_aero", (col(2), lin(6)), interp="rep", **FLT)
am_c = g.bloco("analog_sig_source_x", "portadora_aero", (col(2), lin(7)), waveform=COS, samp_rate="rf_rate", freq="f_img", amp="2", **FLT)
am = g.bloco("blocks_multiply_xx", "am_aero", (col(4), lin(6)), num_inputs=2, **FLT)
g.liga(am_m, am_r); g.liga(am_r, am, 0, 0); g.liga(am_c, am, 0, 1); g.liga(am, soma, 0, 5)
ruido = g.bloco("analog_noise_source_x", "ruido", (col(5), lin(7)), noise_type="analog.GR_GAUSSIAN", amp="0.02", seed="0", **FLT)
g.liga(ruido, soma, 0, 6)
head = g.bloco("blocks_head", "limite", (col(8), lin(2)), num_items="n_rf", **FLT)
arq = g.bloco("blocks_file_sink", "arquivo_antena", (col(9), lin(2)), file="antena.f32", unbuffered="False", **FLT)
q = g.bloco("qtgui_freq_sink_x", "espectro_antena", (col(8), lin(4)), type="float", freqhalf="False", name='"Sinal na antena"', fftsize="32768",
            bw="rf_rate", fc="0", ymin="-120", ymax="0", average="0.2")
g.liga(soma, head); g.liga(head, arq); g.liga(head, q)
ok2 = g.salva()

# ---------------------------------------------------------------- receptor super-heteródino
g = Grafo("rx_super", "Receptor FM super-heteródino (Fig. 4.16)",
          "Amplificador de RF, misturador, FI de 10,7 MHz, limitador, discriminador, decodificador estéreo e de-ênfase")
for n, v, c in [("rf_rate", 480000000, "taxa do RF"), ("f_sel", 97.9e6, "emissora sintonizada"), ("f_if", 10.7e6, "frequência intermediária"),
                ("lo_err", 0, "erro do oscilador local, Hz"), ("dec_if", 8, "decimação até a FI"), ("if_rate", "rf_rate/dec_if", "taxa na FI"),
                ("dem_dec", 125, "decimação no discriminador"), ("dem_rate", "if_rate/dem_dec", "taxa do composto recuperado"),
                ("comp_rate", 192000, "taxa do decodificador"), ("df", 75000, "desvio de pico"), ("a", 0.45, "peso de L+R e L-R"),
                ("a_p", 0.1, "amplitude do piloto"), ("tau", 75e-6, "de-ênfase, 75 us"),
                ("pil_taps", "firdes.band_pass(1, comp_rate, 18500, 19500, 1000)", "passa-faixa do piloto"),
                ("p38_taps", "firdes.band_pass(1, comp_rate, 36000, 40000, 2000)", "passa-faixa da portadora de 38 kHz"),
                ("atraso", "(len(pil_taps)-1)//2+(len(p38_taps)-1)//2", "atraso dos dois filtros do ramo do piloto"),
                ("bw_fi", 200e3, "banda da FI")]:
    g.var(n, v, c)
fonte = g.bloco("blocks_file_source", "antena", (col(0), lin(0)), file="antena.f32", repeat="False", **FLT)
rf = g.bloco("band_pass_filter", "amp_rf", (col(1), lin(0)), type="fir_filter_fff", decim="1", gain="1", samp_rate="rf_rate",
             low_cutoff_freq="f_sel-4e6", high_cutoff_freq="f_sel+4e6", width="4e6")
lo = g.bloco("analog_sig_source_x", "oscilador_local", (col(1), lin(1.25)), waveform=COS, samp_rate="rf_rate", freq="f_sel+f_if+lo_err", amp="1", **FLT)
mix = g.bloco("blocks_multiply_xx", "misturador", (col(2), lin(0)), num_inputs=2, **FLT)
fi_lp = g.bloco("low_pass_filter", "fi_decima", (col(3), lin(0)), type="fir_filter_fff", decim="dec_if", gain="2", samp_rate="rf_rate",
                cutoff_freq="20e6", width="10e6")
fi = g.bloco("band_pass_filter", "amp_fi", (col(4), lin(0)), type="fir_filter_fff", decim="1", gain="10", samp_rate="if_rate",
             low_cutoff_freq="f_if-bw_fi/2", high_cutoff_freq="f_if+bw_fi/2", width="50e3")
lim = g.bloco("blocks_threshold_ff", "limitador", (col(5), lin(0)), low="0", high="0", init="0")
lim_k = g.bloco("blocks_multiply_const_vxx", "limitador_ganho", (col(6), lin(0)), const="2", **FLT)
lim_c = g.bloco("blocks_add_const_vxx", "limitador_dc", (col(7), lin(0)), const="-1", **FLT)
lim_bp = g.bloco("band_pass_filter", "limitador_filtro", (col(8), lin(0)), type="fir_filter_fff", decim="1", gain="1", samp_rate="if_rate",
                 low_cutoff_freq="f_if-200e3", high_cutoff_freq="f_if+200e3", width="100e3")
disc_x = g.bloco("freq_xlating_fir_filter_xxx", "discriminador_desloca", (col(9), lin(0)), type="fcc", decim="dem_dec",
                 taps="firdes.low_pass(1, if_rate, 170e3, 40e3)", center_freq="f_if", samp_rate="if_rate")
disc = g.bloco("analog_quadrature_demod_cf", "discriminador", (col(10), lin(0)), gain="-dem_rate/(2*3.141592653589793*df)")
rs = g.bloco("rational_resampler_xxx", "reamostra_composto", (col(0), lin(3)), type="fff", interp="2", decim="5", taps="firdes.low_pass(2, 2*dem_rate, 60e3, 30e3)")
pil = g.bloco("fir_filter_xxx", "filtro_piloto", (col(1), lin(4)), type="fff", decim="1", taps="pil_taps")
pil2 = g.bloco("blocks_multiply_xx", "dobrador", (col(2), lin(4)), num_inputs=2, **FLT)
pil_k = g.bloco("blocks_multiply_const_vxx", "dobrador_ganho", (col(3), lin(4)), const="2/a_p**2", **FLT)
pil_c = g.bloco("fir_filter_xxx", "filtro_38k", (col(4), lin(4)), type="fff", decim="1", taps="p38_taps")
atr = g.bloco("blocks_delay", "atraso_composto", (col(1), lin(3)), delay="atraso", **FLT)
dm = g.bloco("blocks_multiply_xx", "demod_dsb", (col(4), lin(3)), num_inputs=2, **FLT)
lp_d = g.bloco("low_pass_filter", "filtro_dif", (col(5), lin(3)), type="fir_filter_fff", decim="1", gain="2/a", samp_rate="comp_rate",
               cutoff_freq="15e3", width="3e3")
lp_s = g.bloco("low_pass_filter", "filtro_soma", (col(3), lin(2.4)), type="fir_filter_fff", decim="1", gain="1/a", samp_rate="comp_rate",
               cutoff_freq="15e3", width="3e3")
sl = g.bloco("blocks_add_xx", "soma_l", (col(6), lin(2.4)), num_inputs=2, **FLT)
sr = g.bloco("blocks_sub_xx", "soma_r", (col(6), lin(3.4)), num_inputs=2, **FLT)
hl = g.bloco("blocks_multiply_const_vxx", "meio_l", (col(7), lin(2.4)), const="0.5", **FLT)
hr = g.bloco("blocks_multiply_const_vxx", "meio_r", (col(7), lin(3.4)), const="0.5", **FLT)
de_l = g.bloco("analog_fm_deemph", "deenf_l", (col(8), lin(2.4)), samp_rate="comp_rate", tau="tau")
de_r = g.bloco("analog_fm_deemph", "deenf_r", (col(8), lin(3.4)), samp_rate="comp_rate", tau="tau")
au_l = g.bloco("rational_resampler_xxx", "audio_l", (col(9), lin(2.4)), type="fff", interp="1", decim="4")
au_r = g.bloco("rational_resampler_xxx", "audio_r", (col(9), lin(3.4)), type="fff", interp="1", decim="4")
afc = g.bloco("blocks_moving_average_xx", "afc_media", (col(10), lin(1.25)), length="48000", scale="df/48000", max_iter="4000", **FLT)
q_afc = g.bloco("qtgui_number_sink", "afc_leitura", (col(11), lin(1.25)), name='"AFC: desvio médio (Hz)"', type="float", min="-100e3", max="100e3", gui_hint="2,1,1,1")
q_ant = g.bloco("qtgui_freq_sink_x", "espectro_rf", (col(2), lin(1.25)), type="float", freqhalf="False", name='"Antena e saída do amplificador de RF"', fftsize="32768",
                bw="rf_rate", fc="0", ymin="-140", ymax="0", average="0.2", nconnections="2", gui_hint="0,0,1,1")
q_mix = g.bloco("qtgui_freq_sink_x", "espectro_misturador", (col(3), lin(1.25)), type="float", freqhalf="False", name='"Saída do misturador"', fftsize="32768",
                bw="rf_rate", fc="0", ymin="-140", ymax="0", average="0.2", gui_hint="0,1,1,1")
q_fi = g.bloco("qtgui_freq_sink_x", "espectro_fi", (col(5), lin(1.25)), type="float", freqhalf="False", name='"FI antes e depois do limitador"', fftsize="16384",
               bw="if_rate", fc="0", ymin="-140", ymax="20", average="0.2", nconnections="2", gui_hint="1,0,1,1")
q_env = g.bloco("qtgui_time_sink_x", "tempo_fi", (col(7), lin(1.25)), type="float", name='"FI no tempo: antes e depois do limitador"', size="200000",
                srate="if_rate", autoscale="True", nconnections="2", gui_hint="1,1,1,1")
q_comp = g.bloco("qtgui_freq_sink_x", "espectro_composto", (col(0), lin(4.3)), type="float", freqhalf="False", name='"Composto recuperado"', fftsize="4096",
                 bw="comp_rate", fc="0", ymin="-100", ymax="0", average="0.2", gui_hint="2,0,1,1")
q_au = g.bloco("qtgui_time_sink_x", "audio_lr", (col(10), lin(2.9)), type="float", name='"Áudio: L e R"', size="480",
               srate="48000", autoscale="True", nconnections="2", gui_hint="3,0,1,2")
L = g.liga
L(fonte, rf); L(rf, mix, 0, 0); L(lo, mix, 0, 1); L(mix, fi_lp); L(fi_lp, fi); L(fi, lim); L(lim, lim_k); L(lim_k, lim_c); L(lim_c, lim_bp)
L(lim_bp, disc_x); L(disc_x, disc); L(disc, rs)
L(rs, pil); L(pil, pil2, 0, 0); L(pil, pil2, 0, 1); L(pil2, pil_k); L(pil_k, pil_c)
L(rs, atr); L(atr, dm, 0, 0); L(pil_c, dm, 0, 1); L(dm, lp_d); L(atr, lp_s)
L(lp_s, sl, 0, 0); L(lp_d, sl, 0, 1); L(lp_s, sr, 0, 0); L(lp_d, sr, 0, 1); L(sl, hl); L(sr, hr)
L(hl, de_l); L(hr, de_r); L(de_l, au_l); L(de_r, au_r)
L(disc, afc); L(afc, q_afc)
L(fonte, q_ant, 0, 0); L(rf, q_ant, 0, 1); L(mix, q_mix); L(fi, q_fi, 0, 0); L(lim_bp, q_fi, 0, 1); L(fi, q_env, 0, 0); L(lim_bp, q_env, 0, 1)
L(rs, q_comp); L(au_l, q_au, 0, 0); L(au_r, q_au, 0, 1)
ok3 = g.salva()
sys.exit(0 if (ok1 and ok2 and ok3) else 1)
