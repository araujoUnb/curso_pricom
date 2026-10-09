# Abre um .grc no GNU Radio Companion (GTK) e salva PNG do flowgraph e da janela de
# propriedades de cada bloco. Uso (com um X, por exemplo Xvfb): capture_grc.py arquivo.grc saida/
import os, sys, time
import gi
gi.require_version("Gtk", "3.0"); gi.require_version("PangoCairo", "1.0")
from gi.repository import Gtk, Gdk, GLib
from gnuradio import gr
from gnuradio.grc.gui.Platform import Platform
from gnuradio.grc.gui.Application import Application
from gnuradio.grc.gui.PropsDialog import PropsDialog
from gnuradio.grc.gui import Utils

grc, out = os.path.abspath(sys.argv[1]), sys.argv[2]
os.makedirs(out, exist_ok=True)
platform = Platform(version=gr.version(), version_parts=(gr.major_version(), gr.api_version(), gr.minor_version()),
                    prefs=gr.prefs(), install_prefix=gr.prefix())
platform.build_library()
app = Application([grc], platform)

def pump(t=0.6):
    end = time.time() + t
    while time.time() < end:
        while Gtk.events_pending(): Gtk.main_iteration_do(False)
        time.sleep(0.02)

def grab(win, path):
    gw = win.get_window(); w, h = gw.get_width(), gw.get_height()
    Gdk.pixbuf_get_from_window(gw, 0, 0, w, h).savev(path, "png", [], [])

def capture():
    try:
        mw = app.main_window
        fg = mw.current_page.flow_graph
        Utils.make_screenshot(fg, os.path.join(out, "flowgraph.png"))
        for blk in fg.blocks:
            if blk.key in ("options",):
                continue
            dlg = PropsDialog(mw, blk); dlg.resize(760, 620); dlg.show_all(); pump()
            grab(dlg, os.path.join(out, f"bloco_{blk.name}.png")); print("ok", blk.name, blk.key, flush=True)
            dlg.destroy(); pump(0.1)
    except Exception as e:
        import traceback; traceback.print_exc()
    app.quit()
    return False

GLib.timeout_add(5000, capture)
app.run()
