# Roda os flowgraphs gerados pelo grcc sem tela, grava cada etapa em dados/ e
# fotografa a interface Qt. Uso: QT_QPA_PLATFORM=offscreen python rodar.py
import os, sys, time, threading
import numpy as np
from PyQt5 import Qt
from gnuradio import blocks, gr

app = Qt.QApplication(sys.argv)
os.makedirs("dados", exist_ok=True); os.makedirs("fotos_gui", exist_ok=True)


def sonda(tb, nome, arq, tipo=gr.sizeof_float):
    s = blocks.file_sink(tipo, os.path.join("dados", arq), False)
    tb.connect(getattr(tb, nome), s)


def roda(tb, foto, dur=None):
    tb.resize(1600, 1000); tb.show()
    tb.start()
    if dur is None:
        t = threading.Thread(target=tb.wait); t.start()
        while t.is_alive():
            app.processEvents(); time.sleep(0.05)
    else:
        fim = time.time() + dur
        while time.time() < fim:
            app.processEvents(); time.sleep(0.05)
    tb.show(); fim = time.time() + 2
    while time.time() < fim:
        app.processEvents(); time.sleep(0.05)
    tb.grab().save(os.path.join("fotos_gui", foto))
    tb.stop(); tb.wait(); tb.close()


qual = sys.argv[1:] or ["tx", "banda", "rx"]

if "tx" in qual:
    import tx_estereo
    tb = tx_estereo.tx_estereo()
    for n in ["soma_lr", "dif_lr", "preenf_soma", "preenf_dif", "dobrador", "dobrador_dc", "dsb_sc", "composto"]:
        sonda(tb, n, f"tx_{n}.f32")
    sonda(tb, "modulador_fm", "tx_fm.c64", gr.sizeof_gr_complex)
    roda(tb, "tx_estereo.png", dur=1.5)
    print("tx ok", os.path.getsize("composto.f32") // 4, "amostras no arquivo", flush=True)

if "banda" in qual:
    import banda_fm
    tb = banda_fm.banda_fm()
    t0 = time.time(); roda(tb, "banda_fm.png"); print("banda ok", round(time.time() - t0, 1), "s", flush=True)

if "rx" in qual:
    import rx_super
    casos = [(0, 200e3), (30000, 200e3), (-30000, 200e3), (0, 260e3)]
    for err, bw in casos:
        tb = rx_super.rx_super(); tb.set_lo_err(err); tb.set_bw_fi(bw)
        suf = ("" if err == 0 else f"_lo{err:+d}") + ("" if bw == 200e3 else f"_fi{int(bw/1e3)}")
        if suf == "":
            for n in ["amp_rf", "misturador", "fi_decima", "amp_fi", "limitador_dc", "limitador_filtro", "reamostra_composto",
                      "filtro_soma", "filtro_dif", "filtro_38k", "audio_l", "audio_r"]:
                sonda(tb, n, f"rx_{n}.f32")
        sonda(tb, "discriminador", f"rx_discriminador{suf}.f32")
        if suf:
            sonda(tb, "audio_l", f"rx_audio_l{suf}.f32"); sonda(tb, "audio_r", f"rx_audio_r{suf}.f32")
        t0 = time.time(); roda(tb, f"rx_super{suf}.png"); print("rx ok", err, round(time.time() - t0, 1), "s", flush=True)
