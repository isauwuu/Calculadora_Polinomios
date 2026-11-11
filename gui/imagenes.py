"""Dibujos generados en memoria con Pillow: tarjetas, íconos, pestañas y encabezado.

Tkinter no tiene bordes redondeados ni sombras. La estrategia es dibujar esas
piezas con Pillow, convertirlas a PhotoImage y ponerlas detrás de widgets
normales. Todo se guarda en caché para no redibujar en cada resize.
"""

from functools import lru_cache

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageTk

from gui.estilo import BG, CARD, GREEN, GREEN_B, LINE, NAVY

SS = 3  # supersampling para bordes suaves


def rgb(color):
    """Convierte '#RRGGBB' a una tupla (r, g, b)."""
    color = color.lstrip("#")
    return tuple(int(color[i : i + 2], 16) for i in (0, 2, 4))


def _sparkle(d, cx, cy, r, color, k=0.2):
    puntos = [
        (cx, cy - r),
        (cx + k * r, cy - k * r),
        (cx + r, cy),
        (cx + k * r, cy + k * r),
        (cx, cy + r),
        (cx - k * r, cy + k * r),
        (cx - r, cy),
        (cx - k * r, cy - k * r),
    ]
    d.polygon(puntos, fill=color)


def _blobs(d, box, escala=1.0):
    """Adornos verde/azul recortados por la tarjeta."""
    x0, y0, x1, y1 = box
    u = SS * escala
    d.ellipse((x1 - 150 * u, y1 - 62 * u, x1 + 40 * u, y1 + 90 * u), fill=(176, 226, 190, 255))
    d.ellipse((x1 - 105 * u, y1 - 44 * u, x1 + 30 * u, y1 + 70 * u), fill=(120, 196, 148, 255))
    d.ellipse((x1 - 46 * u, y1 - 40 * u, x1 + 40 * u, y1 + 40 * u), fill=(40, 74, 148, 255))


@lru_cache(maxsize=256)
def rounded_image(
    w,
    h,
    r,
    fill,
    outline=None,
    ow=1,
    m=0,
    shadow=False,
    bg=BG,
    deco=None,
):
    """Rectángulo redondeado con sombra suave opcional.

    `deco` puede ser None, "blobs" (adornos de la tarjeta de gráfico) o
    "result" (destello de la tarjeta de resultado). Todos los argumentos son
    hashables para poder cachear la imagen.
    """
    w, h = max(int(w), 8), max(int(h), 8)
    base = Image.new("RGB", (w, h), rgb(bg))
    if shadow:
        sombra = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        ImageDraw.Draw(sombra).rounded_rectangle(
            (m, m + 3, w - m - 1, h - m + 2), r, fill=(25, 70, 55, 34)
        )
        sombra = sombra.filter(ImageFilter.GaussianBlur(6))
        base.paste(sombra, (0, 0), sombra)

    grande = base.resize((w * SS, h * SS), Image.BILINEAR)
    d = ImageDraw.Draw(grande)
    caja = (m * SS, m * SS, (w - m) * SS - 1, (h - m) * SS - 1)
    d.rounded_rectangle(
        caja,
        r * SS,
        fill=rgb(fill),
        outline=rgb(outline) if outline else None,
        width=ow * SS,
    )

    if deco:
        capa = Image.new("RGBA", grande.size, (0, 0, 0, 0))
        dc = ImageDraw.Draw(capa)
        if deco == "blobs":
            _blobs(dc, caja)
        elif deco == "result":
            _sparkle(dc, caja[2] - 48 * SS, caja[1] + 48 * SS, 20 * SS, (77, 178, 122, 255))
        mascara = Image.new("L", grande.size, 0)
        ImageDraw.Draw(mascara).rounded_rectangle(caja, r * SS, fill=255)
        capa.putalpha(ImageChops.multiply(capa.getchannel("A"), mascara))
        grande.paste(capa, (0, 0), capa)

    return grande.resize((w, h), Image.Resampling.LANCZOS)


@lru_cache(maxsize=128)
def icon_image(kind, px, color=GREEN):
    """Ícono vectorial simple dibujado con Pillow."""
    n = px * 4
    im = Image.new("RGBA", (n, n), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    col = rgb(color)

    if kind == "sparkle":
        _sparkle(d, n / 2, n / 2, n / 2, col, 0.22)
    elif kind == "table":
        d.rounded_rectangle((n * .08, n * .12, n * .92, n * .88), n * .12, outline=col, width=int(n * .09))
        d.line((n * .08, n * .4, n * .92, n * .4), fill=col, width=int(n * .08))
        d.line((n * .08, n * .64, n * .92, n * .64), fill=col, width=int(n * .07))
        d.line((n * .5, n * .12, n * .5, n * .88), fill=col, width=int(n * .07))
    elif kind == "chart":
        pts = [(.06, .72), (.28, .36), (.5, .62), (.72, .2), (.94, .46)]
        d.line([(x * n, y * n) for x, y in pts], fill=col, width=int(n * .11), joint="curve")
    elif kind == "check":
        d.ellipse((n * .04, n * .04, n * .96, n * .96), fill=col)
        d.line(
            [(n * .27, n * .53), (n * .44, n * .69), (n * .75, n * .33)],
            fill=(255, 255, 255, 255),
            width=int(n * .12),
            joint="curve",
        )
    elif kind == "play":
        d.polygon([(n * .26, n * .14), (n * .26, n * .86), (n * .84, n * .5)], fill=col)
    elif kind == "trash":
        d.rounded_rectangle((n * .2, n * .3, n * .8, n * .9), n * .06, outline=col, width=int(n * .09))
        d.line((n * .1, n * .26, n * .9, n * .26), fill=col, width=int(n * .09))
        d.rounded_rectangle((n * .36, n * .08, n * .64, n * .26), n * .04, outline=col, width=int(n * .08))
        d.line((n * .42, n * .46, n * .42, n * .76), fill=col, width=int(n * .07))
        d.line((n * .58, n * .46, n * .58, n * .76), fill=col, width=int(n * .07))
    elif kind == "warn":
        d.polygon([(n * .5, n * .06), (n * .96, n * .9), (n * .04, n * .9)], fill=col)
        d.line((n * .5, n * .36, n * .5, n * .62), fill=(255, 255, 255, 255), width=int(n * .1))
        d.ellipse((n * .45, n * .7, n * .55, n * .8), fill=(255, 255, 255, 255))
    elif kind == "dot":
        d.ellipse((n * .2, n * .2, n * .8, n * .8), fill=col)
    elif kind == "ring":
        d.ellipse((n * .15, n * .15, n * .85, n * .85), outline=col, width=int(n * .14))
    elif kind == "radio_on":
        d.ellipse((n * .05, n * .05, n * .95, n * .95), fill=(255, 255, 255, 255))
        d.ellipse((n * .3, n * .3, n * .7, n * .7), fill=rgb(NAVY))
    elif kind == "radio_off":
        d.ellipse((n * .08, n * .08, n * .92, n * .92), outline=rgb("#9DB0A8"), width=int(n * .08))

    return im.resize((px, px), Image.Resampling.LANCZOS)


@lru_cache(maxsize=64)
def header_image(w, h, x_div, x_title_end):
    """Banda azul con degradado, destellos y separadores."""
    w, h = max(int(w), 8), max(int(h), 8)
    grad = Image.new("RGB", (1, h))
    c0, c1 = rgb("#0A2540"), rgb("#12435C")
    for y in range(h):
        t = y / max(h - 1, 1)
        grad.putpixel((0, y), tuple(int(c0[i] + (c1[i] - c0[i]) * t) for i in range(3)))
    grande = grad.resize((w * SS, h * SS), Image.BILINEAR)

    capa = Image.new("RGBA", grande.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(capa)
    s = SS
    d.ellipse(((w - 340) * s, -150 * s, (w - 80) * s, 80 * s), fill=(160, 214, 176, 255))
    d.ellipse(((w - 262) * s, -100 * s, (w - 120) * s, 38 * s), fill=(98, 178, 132, 255))
    d.ellipse(((w - 228) * s, 26 * s, (w - 150) * s, 104 * s), fill=(36, 70, 146, 255))
    grande.paste(capa, (0, 0), capa)

    d = ImageDraw.Draw(grande)
    _sparkle(d, 36 * s, h / 2 * s, 18 * s, (255, 255, 255, 255), 0.2)
    _sparkle(d, (w - 300) * s, h / 2 * s, 14 * s, (252, 236, 190, 255), 0.2)
    for x in (x_div, x_title_end):
        d.line((x * s, 16 * s, x * s, (h - 16) * s), fill=(255, 255, 255, 255), width=int(1.1 * s))
    for i, color in enumerate([(143, 208, 160), (241, 230, 200), (74, 104, 181)]):
        cx = (w - 88 + i * 24) * s
        d.ellipse((cx - 6 * s, (h / 2 - 6) * s, cx + 6 * s, (h / 2 + 6) * s), fill=color)
    return grande.resize((w, h), Image.Resampling.LANCZOS)


@lru_cache(maxsize=128)
def tab_image(w, h, seleccionada):
    """Fondo de una pestaña, con subrayado verde si está activa."""
    w, h = max(int(w), 8), max(int(h), 8)
    fill = NAVY if seleccionada else "#EAF0ED"
    outline = None if seleccionada else LINE
    base = rounded_image(w, h, 13, fill, outline, 1, 0, False, BG)
    grande = base.resize((w * SS, h * SS), Image.BILINEAR)
    d = ImageDraw.Draw(grande)
    if seleccionada:
        d.rounded_rectangle(
            (w * .2 * SS, (h - 5) * SS, w * .8 * SS, (h - 1) * SS),
            2 * SS,
            fill=rgb(GREEN),
        )
    circulo = (255, 255, 255) if seleccionada else rgb(GREEN_B)
    d.ellipse((13 * SS, 10 * SS, 39 * SS, 36 * SS), fill=circulo)
    return grande.resize((w, h), Image.Resampling.LANCZOS)


def photo(imagen):
    """Convierte una imagen Pillow a PhotoImage (el llamador debe conservarla)."""
    return ImageTk.PhotoImage(imagen)
