# Recorta as fotos do GRC por etapa, em frações da largura e da altura da imagem.
from PIL import Image
cortes = {
    "rx_super": {"rx_frente": (0.07, 0.0, 0.47, 0.235), "rx_fi_disc": (0.46, 0.0, 1.0, 0.235), "rx_decod": (0.07, 0.25, 0.92, 0.52)},
}
for base, d in cortes.items():
    im = Image.open(f"fotos_grc/{base}.png"); w, h = im.size
    for nome, (x0, y0, x1, y1) in d.items():
        im.crop((int(x0 * w), int(y0 * h), int(x1 * w), int(y1 * h))).save(f"fotos_grc/{nome}.png"); print(nome)
