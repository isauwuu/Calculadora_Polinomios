"""Dibujo de tablas de Ruffini y esquemas de pasos en la tarjeta derecha."""

import tkinter as tk
from tkinter import ttk

from gui.estilo import (
    AMBER_L, CARD, INK, LINE, MUTED, NAVY, ORANGE, PLOT, RED,
    RUFFINI_BAND, RUFFINI_BOX, RUFFINI_LINE, RUFFINI_PRODUCT,
)

class _DatosCelda:
    __slots__ = ("rect", "texto", "fila", "columna", "base_fill", "base_outline", "calculo")
    def __init__(self, rect, texto, fila, columna, base_fill, base_outline, calculo):
        self.rect = rect
        self.texto = texto
        self.fila = fila
        self.columna = columna
        self.base_fill = base_fill
        self.base_outline = base_outline
        self.calculo = calculo


def _crear_rect_redondeado(canvas, x1, y1, x2, y2, r, **kwargs):
    """Dibuja un rectángulo redondeado usando un polígono suavizado."""
    points = [
        x1 + r, y1, x2 - r, y1, x2, y1, x2, y1 + r,
        x2, y2 - r, x2, y2, x2 - r, y2, x1 + r, y2,
        x1, y2, x1, y2 - r, x1, y1 + r, x1, y1
    ]
    return canvas.create_polygon(points, smooth=True, **kwargs)


class TablaEsquema(tk.Frame):
    ALTO_FILA = 44
    ALTO_FILA_TABLA = 34
    ALTO_TITULO = 30
    ALTO_CABECERA = 28
    ALTO_ENCABEZADO = 32
    ALTO_NOTA = 34
    MARGEN = 22
    SEPARACION_SECCIONES = 18

    def __init__(self, master, fuentes, bg=CARD):
        super().__init__(master, bg=bg)
        self.fuentes = fuentes
        self.bg = bg
        self._esquema = None
        self._paso_activo = None
        self._celdas = {}
        self._item_celda = {}
        self._mensaje = ""
        self._zoom = 1.0

        self.canvas = tk.Canvas(self, bg=bg, highlightthickness=0, bd=0)
        self.yscroll = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.xscroll = ttk.Scrollbar(self, orient="horizontal", command=self.canvas.xview)
        self.canvas.configure(yscrollcommand=self.yscroll.set, xscrollcommand=self.xscroll.set)
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.yscroll.grid(row=0, column=1, sticky="ns")
        self.xscroll.grid(row=1, column=0, sticky="ew")
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        self.hover = tk.Label(self, text="", font=fuentes.small, bg=bg, fg=MUTED, anchor="w", justify="left", wraplength=330)
        self.hover.grid(row=2, column=0, sticky="ew", pady=(3, 0))

        self.canvas.bind("<Configure>", lambda _: self._redibujar())
        self.canvas.bind("<Motion>", self._al_mover)
        self.canvas.bind("<Leave>", lambda _: self.hover.configure(text=""))
        self.canvas.bind("<MouseWheel>", self._rueda)
        self.canvas.bind("<Shift-MouseWheel>", self._rueda_horizontal)

    def mostrar(self, esquema):
        self._esquema = esquema or {}
        self._paso_activo = None
        self._mensaje = ""
        self.hover.configure(text="")
        self._redibujar()

    def limpiar(self, mensaje="Ingresá los datos y presioná Calcular."):
        self._esquema = None
        self._paso_activo = None
        self._mensaje = mensaje
        self.hover.configure(text="")
        self._dibujar_mensaje()

    def resaltar_paso(self, paso):
        self._paso_activo = paso
        self._aplicar_resaltado()

    def redibujar(self):
        self._redibujar()

    def cerrar(self):
        try: self.canvas.destroy()
        except tk.TclError: pass

    def _fuente_escalada(self, fuente):
        if self._zoom == 1.0: return fuente
        f = fuente.copy()
        f.configure(size=int(f.cget("size") * self._zoom))
        return f

    def _redibujar(self):
        if not self._esquema:
            if self._mensaje: self._dibujar_mensaje()
            return

        self.canvas.delete("all")
        self._celdas.clear()
        self._item_celda.clear()
        ancho = max(self.canvas.winfo_width(), 320)
        self._zoom = max(1.0, min(ancho / 750, 1.6))
        y = self.MARGEN

        for s, seccion in enumerate(self._esquema.get("secciones", [])):
            y = self._dibujar_seccion(s, seccion, y, ancho)

        bbox = self.canvas.bbox("all")
        if bbox is None: bbox = (0, 0, ancho, y)
        bbox = (bbox[0], bbox[1], bbox[2], bbox[3] + self.MARGEN)
        self._ajustar_scrollbars(bbox, ancho)
        self.canvas.configure(scrollregion=bbox)
        self._aplicar_resaltado()

    def _dibujar_mensaje(self):
        self.canvas.delete("all")
        self._celdas.clear()
        self._item_celda.clear()
        self.yscroll.grid_remove()
        self.xscroll.grid_remove()
        ancho = max(self.canvas.winfo_width(), 320)
        alto = max(self.canvas.winfo_height(), 240)
        self.canvas.configure(scrollregion=(0, 0, ancho, alto))
        self.canvas.create_text(ancho / 2, alto / 2, text=self._mensaje, anchor="center", justify="center", font=self._fuente_escalada(self.fuentes.math_small), fill=MUTED, width=max(ancho - 90, 220))

    def _ajustar_scrollbars(self, bbox, ancho):
        alto = max(self.canvas.winfo_height(), 1)
        self.yscroll.grid() if (bbox[3] - bbox[1]) > alto else self.yscroll.grid_remove()
        self.xscroll.grid() if (bbox[2] - bbox[0]) > ancho else self.xscroll.grid_remove()

    def _dibujar_seccion(self, s, seccion, y, ancho):
        if seccion.get("estilo") == "ruffini":
            return self._dibujar_ruffini(s, seccion, y, ancho)
        return self._dibujar_tabla(s, seccion, y, ancho)

    # ------------------------------------------------------------------ Ruffini
    def _anchos_ruffini(self, seccion):
        filas = seccion.get("filas", [])
        cantidad = max([len(fila.get("valores", [])) for fila in filas] + [1])
        etiquetas = [fila.get("valores", [""])[0] for fila in filas]
        ancho_etq = max([self.fuentes.math_label.measure(str(t)) for t in etiquetas] + [40]) + 24
        anchos = [max(int(66 * self._zoom), int(ancho_etq))]
        cabecera = seccion.get("cabecera") or []
        for c in range(1, cantidad):
            textos = []
            for fila in filas:
                valores = fila.get("valores", [])
                if c < len(valores): textos.append(str(valores[c]))
            if c - 1 < len(cabecera): textos.append(str(cabecera[c - 1]).replace("_", ""))
            ancho = max([self.fuentes.math.measure(t) for t in textos] + [28]) + 28
            anchos.append(max(int(56 * self._zoom), int(ancho)))
        return anchos

    def _x_centrada(self, ancho_total, ancho_disponible):
        if ancho_total + 2 * self.MARGEN <= ancho_disponible:
            return (ancho_disponible - ancho_total) / 2
        return self.MARGEN

    def _dibujar_ruffini(self, s, seccion, y, ancho_disponible):
        filas = seccion.get("filas", [])
        if not filas: return y
        anchos = self._anchos_ruffini(seccion)
        ancho_total = sum(anchos)
        x_tabla = self._x_centrada(ancho_total, ancho_disponible)
        x_coefs = x_tabla + anchos[0]
        ancho_coefs = ancho_total - anchos[0]

        titulo = seccion.get("titulo")
        if titulo:
            self.canvas.create_text(x_tabla, y, text=titulo, anchor="nw", font=self._fuente_escalada(self.fuentes.bold), fill=NAVY)
            y += int(self.ALTO_TITULO * self._zoom)

        cabecera = seccion.get("cabecera") or []
        if cabecera:
            xc = x_coefs
            for c, texto in enumerate(cabecera):
                if c + 1 < len(anchos):
                    self._texto_cabecera(xc + anchos[c + 1] / 2, y + int(self.ALTO_CABECERA * self._zoom) / 2, texto)
                    xc += anchos[c + 1]
            y += int(self.ALTO_CABECERA * self._zoom)

        y_tabla = y
        alto_fila = int(self.ALTO_FILA * self._zoom)
        alto_total = alto_fila * len(filas)
        y_resultado = y_tabla + alto_fila * (len(filas) - 1)

        if seccion.get("tipo") == "cuadratica":
            self.canvas.create_rectangle(x_coefs, y_resultado, x_coefs + ancho_coefs, y_tabla + alto_total, fill=RUFFINI_BAND, outline="")

        self._dibujar_caja_resto(seccion, x_tabla, y_tabla, anchos, alto_fila)

        for r, fila in enumerate(filas):
            valores = fila.get("valores", [])
            calculos = fila.get("calculos", [])
            tipo = fila.get("tipo", "normal")
            x = x_tabla
            for c in range(len(anchos)):
                valor = valores[c] if c < len(valores) else ""
                texto_valor = str(valor)
                fuente = self._fuente_escalada(self._fuente_celda(r, c))
                color = self._color_celda(r, c, tipo, texto_valor)

                if texto_valor:
                    # Dibujamos la "Pill" (Caja redondeada)
                    x1 = x + 6
                    y1 = y_tabla + r * alto_fila + 4
                    x2 = x + anchos[c] - 6
                    y2 = y_tabla + (r + 1) * alto_fila - 4

                    fill_color = "#FFFFFF" if tipo == "suma" else ("#F0F4F8" if tipo == "producto" else "#FAFAFA")
                    if tipo == "producto": fill_color = RUFFINI_BOX

                    rect = _crear_rect_redondeado(self.canvas, x1, y1, x2, y2, r=12, fill=fill_color, outline=LINE, width=1)

                    texto = self.canvas.create_text(x + anchos[c] / 2, y_tabla + r * alto_fila + alto_fila / 2, text=texto_valor, font=fuente, fill=color)

                    # Flechitas para los productos
                    if tipo == "producto" and texto_valor not in ("0", "−0", "-0"):
                        self.canvas.create_text(x + anchos[c] - 10, y_tabla + r * alto_fila + 10, text="↘", font=("Arial", int(12 * self._zoom)), fill=MUTED)

                    calculo = calculos[c] if c < len(calculos) else ""
                    if not calculo and texto_valor: calculo = texto_valor
                    dato = _DatosCelda(rect, texto, r, c, "", "", calculo)
                    self._celdas[(s, r, c)] = dato
                    self._item_celda[rect] = dato
                    self._item_celda[texto] = dato
                else:
                    # Dibujar cruces rojas
                    es_cruz = False
                    if seccion.get("tipo") == "cuadratica":
                        if r == 1 and (c == 1 or c == len(anchos) - 1): es_cruz = True
                        elif r == 2 and (c == 1 or c == 2): es_cruz = True

                    if es_cruz:
                        self.canvas.create_text(x + anchos[c] / 2, y_tabla + r * alto_fila + alto_fila / 2, text="✕", font=self._fuente_escalada(self.fuentes.math_bold), fill=RED)
                    rect_vacio = self.canvas.create_rectangle(x, y_tabla + r * alto_fila, x + anchos[c], y_tabla + (r+1)*alto_fila, fill="", outline="")
                    dato = _DatosCelda(rect_vacio, 0, r, c, "", "", "")
                    self._celdas[(s, r, c)] = dato
                    self._item_celda[rect_vacio] = dato
                x += anchos[c]

        y = y_tabla + alto_total
        nota = seccion.get("nota")
        if nota:
            self.canvas.create_text(x_tabla, y + 8, text=nota, anchor="nw", font=self._fuente_escalada(self.fuentes.small), fill=MUTED, width=max(ancho_disponible - x_tabla - self.MARGEN, 260))
            y += int(self.ALTO_NOTA * self._zoom)
        return y + self.SEPARACION_SECCIONES

    def _dibujar_caja_resto(self, seccion, x_tabla, y_tabla, anchos, alto_fila):
        resto = [tuple(pos) for pos in seccion.get("resto", [])]
        if not resto: return
        filas = [r for r, _ in resto]
        columnas = [c for _, c in resto]
        r0, r1 = min(filas), max(filas)
        c0, c1 = min(columnas), max(columnas)
        x1 = x_tabla + sum(anchos[:c0])
        x2 = x1 + sum(anchos[c0 : c1 + 1])
        y1 = y_tabla + r0 * alto_fila
        y2 = y_tabla + (r1 + 1) * alto_fila
        pad = 4
        self.canvas.create_rectangle(x1 + pad, y1 + pad, x2 - pad, y2 - pad, fill=RUFFINI_BOX, outline=RUFFINI_LINE, width=1)

    def _texto_cabecera(self, x, y, texto):
        base, _, sub = str(texto).partition("_")
        f_base = self._fuente_escalada(self.fuentes.math_small)
        f_sub = self._fuente_escalada(self.fuentes.math_sub)
        ancho_base = f_base.measure(base)
        ancho_sub = f_sub.measure(sub) if sub else 0
        inicio = x - (ancho_base + ancho_sub) / 2
        self.canvas.create_text(inicio, y, text=base, anchor="w", font=f_base, fill=MUTED)
        if sub: self.canvas.create_text(inicio + ancho_base, y + 4, text=sub, anchor="w", font=f_sub, fill=MUTED)

    def _fuente_celda(self, fila, columna):
        # Usamos la fuente normal de la app en vez de la matemática serif
        if columna == 0:
            return self.fuentes.bold if fila == 1 else self.fuentes.small
        return self.fuentes.normal

    def _color_celda(self, fila, columna, tipo, valor):
        if columna == 0: return PLOT if fila == 1 else MUTED
        if tipo == "producto": return RUFFINI_PRODUCT
        if valor.strip() in ("0", "−0", "-0"): return RED
        return INK

    # ------------------------------------------------------------------ tablas
    def _anchos_tabla(self, seccion):
        columnas = seccion.get("columnas") or []
        filas = seccion.get("filas", [])
        cantidad = max([len(columnas)] + [len(fila.get("valores", [])) for fila in filas] + [1])
        anchos = []
        for c in range(cantidad):
            textos = []
            if c < len(columnas): textos.append(str(columnas[c]))
            for fila in filas:
                valores = fila.get("valores", [])
                if c < len(valores): textos.append(str(valores[c]))
            ancho = max([self.fuentes.math_small.measure(t) for t in textos] + [40]) + 28
            anchos.append(max(int(64 * self._zoom), int(ancho * self._zoom)))
        return anchos

    def _dibujar_tabla(self, s, seccion, y, ancho_disponible):
        columnas = seccion.get("columnas") or []
        filas = seccion.get("filas", [])
        anchos = self._anchos_tabla(seccion)
        ancho_total = sum(anchos)
        x_tabla = self._x_centrada(ancho_total, ancho_disponible)
        alto_fila = int(self.ALTO_FILA_TABLA * self._zoom)
        alto_encabezado = int(self.ALTO_ENCABEZADO * self._zoom)

        titulo = seccion.get("titulo")
        if titulo:
            self.canvas.create_text(x_tabla, y, text=titulo, anchor="nw", font=self._fuente_escalada(self.fuentes.bold), fill=NAVY)
            y += int(self.ALTO_TITULO * self._zoom)

        if columnas:
            self.canvas.create_rectangle(x_tabla, y, x_tabla + ancho_total, y + alto_encabezado, fill=RUFFINI_BOX, outline="")
            x = x_tabla
            for c, titulo_col in enumerate(columnas):
                self.canvas.create_text(x + anchos[c] / 2, y + alto_encabezado / 2, text=str(titulo_col), font=self._fuente_escalada(self.fuentes.math_small_bold), fill=NAVY)
                x += anchos[c]
            self.canvas.create_line(x_tabla, y + alto_encabezado, x_tabla + ancho_total, y + alto_encabezado, fill=RUFFINI_LINE, width=1)
            y += alto_encabezado

        for r, fila in enumerate(filas):
            valores = fila.get("valores", [])
            calculos = fila.get("calculos", [])
            x = x_tabla
            for c in range(len(anchos)):
                valor = valores[c] if c < len(valores) else ""
                texto_valor = str(valor)
                rect = self.canvas.create_rectangle(x, y, x + anchos[c], y + alto_fila, fill="", outline="")
                texto = self.canvas.create_text(x + anchos[c] / 2, y + alto_fila / 2, text=texto_valor, font=self._fuente_escalada(self.fuentes.math_small), fill=INK)
                calculo = calculos[c] if c < len(calculos) else ""
                if not calculo and texto_valor: calculo = texto_valor
                dato = _DatosCelda(rect, texto, r, c, "", "", calculo)
                self._celdas[(s, r, c)] = dato
                self._item_celda[rect] = dato
                self._item_celda[texto] = dato
                x += anchos[c]
            self.canvas.create_line(x_tabla, y + alto_fila, x_tabla + ancho_total, y + alto_fila, fill=LINE, width=1)
            y += alto_fila

        nota = seccion.get("nota")
        if nota:
            self.canvas.create_text(x_tabla, y + 8, text=nota, anchor="nw", font=self._fuente_escalada(self.fuentes.small), fill=MUTED, width=max(ancho_disponible - x_tabla - self.MARGEN, 260))
            y += int(self.ALTO_NOTA * self._zoom)
        return y + self.SEPARACION_SECCIONES

    # ------------------------------------------------------------------ resaltado
    def _aplicar_resaltado(self):
        for dato in self._celdas.values():
            self.canvas.itemconfigure(dato.rect, fill=dato.base_fill, outline=dato.base_outline, width=1)

        paso = self._paso_activo
        if not paso: return

        indice_seccion = paso.get("seccion", 0)
        celdas = [dato for (s, _r, _c), dato in self._celdas.items() if s == indice_seccion]
        objetivo = []
        if "fila" in paso: objetivo = [d for d in celdas if d.fila == paso["fila"]]
        else:
            columnas = paso.get("columnas")
            if columnas is None: columnas = [paso.get("columna")]
            filas = paso.get("filas")
            for dato in celdas:
                if dato.columna in columnas and (filas is None or dato.fila in filas): objetivo.append(dato)

        for dato in objetivo:
            self.canvas.itemconfigure(dato.rect, fill=AMBER_L, outline=ORANGE, width=2)
            if isinstance(dato.texto, int): self.canvas.tag_raise(dato.texto)

    # ------------------------------------------------------------------ interacción
    def _al_mover(self, evento):
        x = self.canvas.canvasx(evento.x)
        y = self.canvas.canvasy(evento.y)
        dato = None
        for item in self.canvas.find_overlapping(x - 1, y - 1, x + 1, y + 1):
            dato = self._item_celda.get(item)
            if dato is not None: break
        if dato is None or not dato.calculo: self.hover.configure(text="")
        else: self.hover.configure(text=dato.calculo)

    def _rueda(self, evento):
        self.canvas.yview_scroll(-1 if evento.delta > 0 else 1, "units")
        return "break"

    def _rueda_horizontal(self, evento):
        self.canvas.xview_scroll(-1 if evento.delta > 0 else 1, "units")
        return "break"