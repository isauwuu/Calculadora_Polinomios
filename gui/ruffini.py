"""Dibujo de esquemas de Horner/Ruffini y división larga sobre un Canvas."""

import tkinter as tk
import tkinter.font as tkfont
from tkinter import ttk
import traceback

from gui import imagenes
from gui.estilo import CARD, INK, MUTED, NAVY, GREEN, LINE, AMBER
from gui.esquema import poly_texto, termino

VERDE_FONDO = "#F4FBF7"
VERDE_BORDE = "#CFDAD4"
VERDE_TEXTO = INK
MORADO = MUTED

COLOR = {"p": INK, "d": MUTED, "q": NAVY, "r": AMBER, "t": INK}
TINTE = {"p": VERDE_FONDO, "q": "#E8F0F8", "r": "#FFF8ED"}


class TablaEsquema(tk.Frame):
    ANCHO_CELDA = 60
    ALTO_FILA = 36
    ANCHO_ETIQUETA = 60
    MARGEN = 24
    ESCALA_MAX = 1.8
    ESCALA_MIN = 1.0

    def __init__(self, master, fuentes, bg=CARD):
        super().__init__(master, bg=bg)
        self.fuentes = fuentes
        self.bg = bg
        self._esquemas = None
        self._mensaje = "Ingresá los datos y presioná Calcular."
        self._cache = {}
        self._cache_cabecera = []

        self.canvas = tk.Canvas(self, bg=bg, highlightthickness=0, bd=0)
        self.yscroll = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.xscroll = ttk.Scrollbar(self, orient="horizontal", command=self.canvas.xview)
        self.canvas.configure(yscrollcommand=self.yscroll.set, xscrollcommand=self.xscroll.set)
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.yscroll.grid(row=0, column=1, sticky="ns")
        self.xscroll.grid(row=1, column=0, sticky="ew")
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        self.canvas.bind("<Configure>", lambda _: self._redibujar())
        self.canvas.bind("<MouseWheel>", lambda e: self.canvas.yview_scroll(-1 if e.delta > 0 else 1, "units"))
        self.canvas.bind("<Shift-MouseWheel>", lambda e: self.canvas.xview_scroll(-1 if e.delta > 0 else 1, "units"))

    # ------------------------------------------------------------------ API
    def mostrar(self, esquemas):
        self._esquemas = esquemas
        self._redibujar()

    def limpiar(self, mensaje="Ingresá los datos y presioná Calcular."):
        self._esquemas = None
        self._mensaje = mensaje
        self._redibujar()

    def cerrar(self):
        try:
            self.canvas.destroy()
        except tk.TclError:
            pass

    # ------------------------------------------------------------ utilidades
    def _f(self, nombre, s=1.0):
        clave = (nombre, round(s, 1))
        f = self._cache.get(clave)
        if f is None:
            f = tkfont.Font(root=self, font=getattr(self.fuentes, nombre))
            tam = f.actual("size")
            nuevo = int(round(tam * clave[1]))
            f.configure(size=nuevo if nuevo else (1 if tam > 0 else -1))
            self._cache[clave] = f
        return f

    @staticmethod
    def _medir(f, texto):
        return f.measure(texto)

    @staticmethod
    def _h(f):
        return f.metrics("linespace")

    def _escala(self, total_base, ancho_disp, tope):
        s = (ancho_disp - 2 * self.MARGEN) / max(total_base, 1)
        s = max(self.ESCALA_MIN, min(tope, s))
        return int(s * 10) / 10

    # --------------------------------------------------------------- dibujo
    def _redibujar(self):
        c = self.canvas
        c.delete("all")
        self._cache_cabecera.clear()

        self.canvas.xview_moveto(0)
        self.canvas.yview_moveto(0)

        ancho = max(c.winfo_width(), 320)

        if not self._esquemas:
            alto = max(c.winfo_height(), 240)
            self.yscroll.grid_remove()
            self.xscroll.grid_remove()
            c.configure(scrollregion=(0, 0, ancho, alto))
            c.create_text(ancho / 2, alto / 2, text=self._mensaje, font=self.fuentes.small,
                          fill=MUTED, justify="center", width=max(ancho - 90, 220))
            return

        try:
            y = self.MARGEN
            for esq in self._esquemas:
                tipo = esq.get("tipo")
                if tipo == "larga":
                    y = self._dibujar_larga(esq, y, ancho)
                elif tipo == "resumen":
                    y = self._dibujar_resumen(esq, y, ancho)
                else:
                    y = self._dibujar_matricial(esq, y, ancho)

            bbox = c.bbox("all")
            if bbox:
                x0, y0, x1, y1 = bbox
                region = (min(x0, 0), 0, max(x1 + self.MARGEN, ancho), y1 + self.MARGEN)
                c.configure(scrollregion=region)
                if region[3] > c.winfo_height(): self.yscroll.grid()
                else: self.yscroll.grid_remove()
                if region[2] > ancho: self.xscroll.grid()
                else: self.xscroll.grid_remove()
            else:
                c.configure(scrollregion=(0, 0, ancho, max(c.winfo_height(), 240)))
                self.yscroll.grid_remove()
                self.xscroll.grid_remove()
        except Exception as e:
            traceback.print_exc()
            c.delete("all")
            c.configure(scrollregion=(0, 0, ancho, 240))
            c.create_text(ancho/2, 100, text=f"Error al dibujar el esquema:\n{e}",
                          fill="red", font=self.fuentes.normal, justify="center", width=ancho-40)

    # ---- bloques comunes ---------------------------------------------------
    def _titulo(self, texto, x, y, ancho_disp, s):
        f = self._f("bold", min(s, 1.2))
        item = self.canvas.create_text(x, y, text=texto, anchor="nw", font=f, fill=NAVY,
                                       width=max(ancho_disp - 2 * self.MARGEN, 260))
        return self.canvas.bbox(item)[3] + 12

    def _dibujar_cabecera(self, cab, y, ancho_disp, s):
        s2 = min(s, 1.2)
        fx = self._f("bold", s2)
        pad = 12 * s2
        icon_size = max(1, int(18 * s2))

        icon = imagenes.photo(imagenes.icon_image("check", icon_size, GREEN))
        self._cache_cabecera.append(icon)
        icon_w = icon.width()

        cajas = []
        for _, expr in cab:
            w = self._medir(fx, expr) + icon_w + pad * 3
            cajas.append((expr, w))

        alto = self._h(fx) + 16 * s2
        gap = 12
        disp = ancho_disp - 2 * self.MARGEN
        total = sum(w for _, w in cajas) + gap * (len(cajas) - 1)

        if total <= disp:
            x = (ancho_disp - total) / 2
            for expr, w in cajas:
                self._pintar_caja(x, y, w, alto, expr, fx, pad, icon, icon_w)
                x += w + gap
            return y + alto + 16
        else:
            for expr, w in cajas:
                x = max((ancho_disp - w) / 2, self.MARGEN)
                self._pintar_caja(x, y, w, alto, expr, fx, pad, icon, icon_w)
                y += alto + 8
            return y + 8

    def _pintar_caja(self, x, y, w, alto, expr, fx, pad, icon, icon_w):
        pil = imagenes.rounded_image(int(w), int(alto), 12, VERDE_FONDO, VERDE_BORDE, 1, 0, False, self.bg)
        img = imagenes.photo(pil)
        self._cache_cabecera.append(img)
        self.canvas.create_image(x, y, image=img, anchor="nw")

        self.canvas.create_image(x + pad, y + alto / 2, image=icon, anchor="w")
        self.canvas.create_text(x + pad + icon_w + pad, y + alto / 2, text=expr, anchor="w", font=fx, fill=NAVY)

    def _dibujar_identidad(self, partes, y, ancho_disp, s):
        s = min(s, 1.2)
        disp = ancho_disp - 2 * self.MARGEN
        while True:
            f = self._f("bold", s)
            total = sum(self._medir(f, t) for t, _ in partes)
            if total <= disp or s <= 0.7:
                break
            s = round(s - 0.1, 1)
        x = max((ancho_disp - total) / 2, self.MARGEN)
        for texto, rol in partes:
            self.canvas.create_text(x, y, text=texto, anchor="nw", font=f, fill=COLOR.get(rol, INK))
            x += self._medir(f, texto)
        return y + self._h(f) + 12

    def _nota(self, texto, x, y, ancho_disp, s):
        item = self.canvas.create_text(x, y, text=texto, anchor="nw", font=self._f("small", min(s, 1.1)),
                                       fill=MUTED, width=max(ancho_disp - 2 * self.MARGEN, 260))
        return self.canvas.bbox(item)[3] + 10

    # ---- resumen (NUEVO FORMATO MATRIZ) ------------------------------------
    def _dibujar_resumen(self, esq, y, ancho_disp):
        c = self.canvas
        fr = self._f("bold", 1.0)
        fv = self._f("bold", 1.1)
        pad = 12
        gap_x = 16
        gap_y = 8
        items = esq["items"]
        n = len(items)

        if n == 0:
            return y + 10

        # Calcular el ancho máximo de una caja individual
        w_box = max(self._medir(fr, r) + 16 + self._medir(fv, v) for r, v, _ in items) + 2 * pad + 10
        alto = max(self._h(fr), self._h(fv)) + 18

        # Lógica de columnas: 2 si hay más de 1, a menos que no entren en el ancho
        cols = 2 if n >= 2 else 1
        if cols == 2 and (2 * w_box + gap_x) > (ancho_disp - 2 * self.MARGEN):
            cols = 1

        rows = (n + cols - 1) // cols

        # Calcular posición inicial para centrar la matriz completa
        total_w = cols * w_box + (cols - 1) * gap_x
        x_start = max((ancho_disp - total_w) / 2, self.MARGEN)
        y_start = y

        for i, (rotulo, valor, rol) in enumerate(items):
            r = i // cols
            c_idx = i % cols
            x_curr = x_start + c_idx * (w_box + gap_x)
            y_curr = y_start + r * (alto + gap_y)

            col = COLOR[rol]
            c.create_rectangle(x_curr, y_curr, x_curr + w_box, y_curr + alto, fill=TINTE.get(rol, CARD), outline=LINE, width=1)
            c.create_rectangle(x_curr, y_curr, x_curr + 6, y_curr + alto, fill=col, outline=col)

            y_mid = y_curr + alto / 2

            c.create_text(x_curr + 6 + pad, y_mid, text=rotulo, anchor="w", font=fr, fill=MUTED)
            c.create_text(x_curr + 6 + pad + self._medir(fr, rotulo) + 16, y_mid, text=valor,
                          anchor="w", font=fv, fill=col)

        y_fin = y_start + rows * alto + (rows - 1) * gap_y
        return y_fin + 10

    # ---- esquema matricial (Ruffini / Horner) ------------------------------
    def _dibujar_matricial(self, esq, y, ancho_disp):
        c = self.canvas
        filas = esq["filas"]
        ncol = max(len(f["celdas"]) for f in filas)
        textos = [t for f in filas for t in f["celdas"] if t]
        etqs = [f["etiqueta"] for f in filas if f["etiqueta"]]

        f1 = self._f("bold", 1.0)
        wc1 = max(self.ANCHO_CELDA, max((self._medir(f1, t) for t in textos), default=0) + 24)
        we1 = max(self.ANCHO_ETIQUETA, max((self._medir(f1, t) for t in etqs), default=0) + 30)
        s = self._escala(we1 + ncol * wc1, ancho_disp, self.ESCALA_MAX)

        fn, fb, fs = self._f("normal", s), self._f("bold", s), self._f("small", s)
        w = max(self.ANCHO_CELDA * s, max((self._medir(fb, t) for t in textos), default=0) + 24 * s)
        we = max(self.ANCHO_ETIQUETA * s, max((self._medir(fn, t) for t in etqs), default=0) + 30 * s)
        h = self.ALTO_FILA * s

        ancho_total = we + ncol * w
        x = max((ancho_disp - ancho_total) / 2, self.MARGEN)
        xc = x + we

        if esq.get("titulo"):
            y = self._titulo(esq["titulo"], self.MARGEN, y, ancho_disp, s)
        if esq.get("cabecera"):
            y = self._dibujar_cabecera(esq["cabecera"], y, ancho_disp, s)

        nf = len(filas)
        c.create_line(xc, y, xc, y + nf * h, width=1, fill=MUTED)
        if nf > 1:
            yh = y + (nf - 1) * h
            c.create_line(x, yh, xc + ncol * w, yh, width=1, fill=MUTED)

        cociente = esq.get("cociente")
        resto = esq.get("resto")

        for r, fila in enumerate(filas):
            yc = y + r * h + h / 2
            if fila["etiqueta"]:
                c.create_text(xc - 14 * s, yc, text=fila["etiqueta"], anchor="e", font=fn, fill=MUTED)
            for k, texto in enumerate(fila["celdas"]):
                if texto == "":
                    continue
                xk = xc + k * w + w / 2
                color, fuente = INK, fn
                if fila["tipo"] == "producto":
                    color = MUTED
                elif fila["tipo"] == "resultado":
                    fuente = fb
                    color = AMBER if (resto and resto[0] <= k <= resto[1]) else NAVY
                if texto.strip() == "0" and fila["tipo"] == "producto":
                    color = MUTED
                c.create_text(xk, yc, text=texto, font=fuente, fill=color)

        y_fin = y + nf * h

        if resto:
            x1 = xc + resto[0] * w + 4
            x2 = xc + (resto[1] + 1) * w - 4
            c.create_rectangle(x1, y_fin - h + 4, x2, y_fin - 4, outline=AMBER, width=1)

        yl = y_fin + 6 * s
        if cociente:
            xa, xb = xc + cociente[0] * w + 6, xc + (cociente[1] + 1) * w - 6
            c.create_line(xa, yl, xb, yl, fill=NAVY, width=1)
            c.create_text((xa + xb) / 2, yl + 14 * s, text=esq.get("etq_c", "C(x)"), font=fs, fill=NAVY)
        if resto:
            xa, xb = xc + resto[0] * w + 6, xc + (resto[1] + 1) * w - 6
            c.create_line(xa, yl, xb, yl, fill=AMBER, width=1)
            c.create_text((xa + xb) / 2, yl + 14 * s, text=esq.get("etq_r", "R"), font=fs, fill=AMBER)

        y = y_fin + 40 * s
        if esq.get("identidad"):
            y = self._dibujar_identidad(esq["identidad"], y, ancho_disp, s)
        if esq.get("nota"):
            y = self._nota(esq["nota"], self.MARGEN, y, ancho_disp, s)
        return y + 14

    # ---- división larga estándar ------------------------------------------------
    def _dibujar_larga(self, esq, y, ancho_disp):
        c = self.canvas
        n = esq["n"]
        d_txt = poly_texto(esq["divisor"])
        q_txt = poly_texto(esq["cociente_coef"])
        pasos = esq["pasos"]

        def ordenar(dct):
            return sorted(dct.items(), reverse=True)

        filas = [("dividendo", ordenar(esq["dividendo"]), None)]
        for i, p in enumerate(pasos):
            final = i == len(pasos) - 1
            filas.append(("prod", ordenar(p["prod"]), None))
            filas.append(("final" if final else "resto", ordenar(p["resto"]), None))

        textos = [termino(cf, e, primero=(k == 0)) for _, ts, _ in filas for k, (e, cf) in enumerate(ts)]
        etiquetas = [e for _, _, e in filas if e]

        def medir(s):
            fb, fl = self._f("bold", s), self._f("normal", s)
            cw = max(self._medir(fb, t) for t in textos + ["0"]) + 26 * s
            gutter = max(self._medir(fl, t) for t in etiquetas) + 30 * s if etiquetas else 0
            wdiv = max(self._medir(fb, d_txt), self._medir(fb, q_txt)) + 40 * s
            return gutter + (n + 1) * cw + 16 * s + wdiv, cw, gutter, wdiv

        s = 1.3
        while s > 0.5 and medir(s)[0] + 2 * self.MARGEN > ancho_disp:
            s = round(s - 0.1, 1)
        total, cw, gutter, wdiv = medir(s)

        fm, fb, fl = self._f("normal", s), self._f("bold", s), self._f("normal", s)

        if esq.get("titulo"):
            y = self._titulo(esq["titulo"], self.MARGEN, y, ancho_disp, s)
        if esq.get("cabecera"):
            y = self._dibujar_cabecera(esq["cabecera"], y, ancho_disp, s)

        x_left = max((ancho_disp - total) / 2, self.MARGEN)
        x0 = x_left + gutter
        rh = self._h(fm) * 1.6

        def xc(e):
            return x0 + (n - e) * cw + cw / 2

        x_div = x0 + (n + 1) * cw + 6 * s
        c.create_line(x_div, y + 2, x_div, y + 2 * rh - 2, width=1, fill=MUTED)
        c.create_line(x_div, y + rh, x_div + wdiv, y + rh, width=1, fill=MUTED)
        c.create_text(x_div + 14 * s, y + rh / 2, text=d_txt, anchor="w", font=fb, fill=INK)
        c.create_text(x_div + 14 * s, y + 1.5 * rh, text=q_txt, anchor="w", font=fb, fill=NAVY)

        yy = y
        for tipo, terminos, etq in filas:
            cy = yy + rh / 2
            for k, (e, cf) in enumerate(terminos):
                color, fuente = INK, fm
                if tipo in ("dividendo", "resto") and k == 0:
                    color = MUTED
                if tipo == "final":
                    color, fuente = AMBER, fb
                c.create_text(xc(e), cy, text=termino(cf, e, primero=(k == 0)), font=fuente, fill=color)
            if tipo == "final" and not terminos:
                c.create_text(xc(0), cy, text="0", font=fb, fill=AMBER)
            if etq:
                c.create_text(x0 - 10 * s, cy, text=etq, anchor="e", font=fl, fill=MORADO)
            if tipo == "prod" and terminos:
                xa = xc(terminos[0][0]) - cw / 2 + 6
                xb = xc(terminos[-1][0]) + cw / 2 - 6
                c.create_line(xa, yy + rh - 2, xb, yy + rh - 2, width=1, fill=MUTED)
            yy += rh

        y = yy + 14
        if esq.get("identidad"):
            y = self._dibujar_identidad(esq["identidad"], y, ancho_disp, s)
        if esq.get("nota"):
            y = self._nota(esq["nota"], self.MARGEN, y, ancho_disp, s)
        return y + 14