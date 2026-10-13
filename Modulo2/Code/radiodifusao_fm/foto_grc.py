# Salva a imagem do flowgraph de cada .grc pelo próprio GNU Radio Companion.
# Uso, com um X (por exemplo Xvfb): python foto_grc.py tx_estereo.grc banda_fm.grc rx_super.grc
import os, sys
import gi
gi.require_version("Gtk", "3.0"); gi.require_version("PangoCairo", "1.0")
from gi.repository import GLib
from gnuradio import gr
from gnuradio.grc.gui.Platform import Platform
from gnuradio.grc.gui.Application import Application
from gnuradio.grc.gui import Utils

arqs = [os.path.abspath(a) for a in sys.argv[1:]]
os.makedirs("fotos_grc", exist_ok=True)
platform = Platform(version=gr.version(), version_parts=(gr.major_version(), gr.api_version(), gr.minor_version()),
                    prefs=gr.prefs(), install_prefix=gr.prefix())
platform.build_library()
app = Application(arqs, platform)


estado = {"i": 0}


def mostra():
    nb = app.main_window.notebook
    if estado["i"] >= nb.get_n_pages():
        app.quit(); return False
    nb.set_current_page(estado["i"])
    GLib.timeout_add(2500, captura)
    return False


def captura():
    nb = app.main_window.notebook
    pg = nb.get_nth_page(estado["i"])
    nome = os.path.splitext(os.path.basename(pg.file_path))[0]
    try:
        Utils.make_screenshot(pg.flow_graph, os.path.join("fotos_grc", nome + ".png"))
        print("ok", nome, flush=True)
    except Exception as e:
        print("falhou", nome, e, flush=True)
    estado["i"] += 1
    GLib.timeout_add(500, mostra)
    return False


GLib.timeout_add(6000, mostra)
app.run()
