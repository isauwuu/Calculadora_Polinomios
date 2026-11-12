"""Dibujo de tablas de Ruffini y esquemas de pasos en la tarjeta derecha.

La vista no calcula nada: recibe las secciones ya armadas por
``gui/controlador.py`` y solo las pinta. La tabla se dibuja una vez y luego se
resaltan celdas o filas para animar el llenado.
"""

import tkinter as tk
from tkinter import ttk

from gui.estilo import (
    AMBER_L,
    BLUE_L,
    CARD,
    FIELD,
    GREEN_B,
    GREEN_D,
    GREEN_L,
    INK,
    LINE,
    MUTED,
    NAVY,
    ORANGE,
)


class _DatosCelda:
    """Información mínima de una celda para resaltarla y mostrar su cálculo."""

    __slots__ = ("rect", "texto", "fila", "columna", "base_fill", "base_outline", "calculo")

    def __init__(self, rect, texto, fila, columna, base_fill, base_outline, calculo):
        self.rect = rect
        self.texto = texto
        self.fila = fila
        self.columna = columna
        self.base_fill = base_fill
        self.base_outline = base_outline
        self.calculo = calculo


class TablaEsquema(tk.Frame):
    """Tabla con scroll para los esquemas de Ruffini y las tablas de pasos."""

    ALTO_FILA = 29
    ALTO_TITULO = 25
    ALTO_NOTA = 30
    ALTO_ENCABEZADO = 29
    MARGEN = 8

    def __init__(self, master, fuentes, bg=CARD):
        super().__init__(master, bg=bg)
        self.fuentes = fuentes
        self.bg = bg
        self._esquema = None
        self._paso_activo = None
        self._celdas = {}
        self._item_celda = {}
        self._mensaje = ""

        self.canvas = tk.Canvas(self, bg=bg, highlightthickness=0, bd=0)
        self.yscroll = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.xscroll = ttk.Scrollbar(self, orient="horizontal", command=self.canvas.xview)
        self.canvas.configure(
            yscrollcommand=self.yscroll.set,
            xscrollcommand=self.xscroll.set,
        )
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.yscroll.grid(row=0, column=1, sticky="ns")
        self.xscroll.grid(row=1, column=0, sticky="ew")
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        self.hover = tk.Label(
            self,
            text="",
            font=fuentes.small,
            bg=bg,
            fg=MUTED,
            anchor="w",
            justify="left",
            wraplength=330,
        )
        self.hover.grid(row=2, column=0, sticky="ew", pady=(3, 0))

        self.canvas.bind("<Configure>", lambda _: self._redibujar())
        self.canvas.bind("<Motion>", self._al_mover)
        self.canvas.bind("<Leave>", lambda _: self.hover.configure(text=""))
        self.canvas.bind("<MouseWheel>", self._rueda)
        self.canvas.bind("<Shift-MouseWheel>", self._rueda_horizontal)

    # ------------------------------------------------------------------ API
    def mostrar(self, esquema):
        """Carga un esquema y lo dibuja desde cero."""
        self._esquema = esquema or {}
        self._paso_activo = None
        self.hover.configure(text="")
        self._redibujar()

    def limpiar(self, mensaje="Ingresá los datos y presioná Calcular."):
        self._esquema = None
        self._paso_activo = None
        self._mensaje = mensaje
        self.canvas.delete("all")
        self._celdas.clear()
        self._item_celda.clear()
        self.hover.configure(text="")
        self.canvas.configure(scrollregion=(0, 0, 0, 0))
        self.canvas.create_text(
            12,
            18,
            text=mensaje,
            anchor="nw",
            font=self.fuentes.small,
            fill=MUTED,
            width=340,
            tags="mensaje",
        )

    def resaltar_paso(self, paso):
        """Resalta las celdas indicadas por un paso de animación."""
        self._paso_activo = paso
        self._aplicar_resaltado()

    def redibujar(self):
        self._redibujar()

    def cerrar(self):
        try:
            self.canvas.destroy()
        except tk.TclError:
            pass

    # ------------------------------------------------------------------ dibujo
    def _redibujar(self):
        if not self._esquema:
            if self._mensaje:
                self.limpiar(self._mensaje)
            return

        self.canvas.delete("all")
        self._celdas.clear()
        self._item_celda.clear()
        ancho = max(self.canvas.winfo_width(), 250)
        y = self.MARGEN
        x0 = self.MARGEN

        for s, seccion in enumerate(self._esquema.get("secciones", [])):
            y = self._dibujar_seccion(s, seccion, x0, y, ancho)

        self.canvas.configure(scrollregion=self.canvas.bbox("all") or (0, 0, ancho, y))
        self._aplicar_resaltado()

    def _anchos(self, seccion):
        filas = seccion.get("filas", [])
        columnas = seccion.get("columnas") or []
        cantidad = max(
            [len(columnas)] + [len(fila.get("valores", [])) for fila in filas] + [1]
        )
        anchos = []
        for c in range(cantidad):
            textos = []
            if c < len(columnas):
                textos.append(str(columnas[c]))
            for fila in filas:
                valores = fila.get("valores", [])
                if c < len(valores):
                    textos.append(str(valores[c]))
            ancho = max([self.fuentes.mono.measure(t) for t in textos] + [32]) + 20
            if c == 0 and not columnas:
                ancho = max(ancho, 62)
            anchos.append(max(44, int(ancho)))
        return anchos

    def _dibujar_seccion(self, s, seccion, x0, y, ancho_disponible):
        titulo = seccion.get("titulo")
        if titulo:
            self.canvas.create_text(
                x0,
                y,
                text=titulo,
                anchor="nw",
                font=self.fuentes.bold,
                fill=NAVY,
            )
            y += self.ALTO_TITULO

        filas = seccion.get("filas", [])
        columnas = seccion.get("columnas") or []
        anchos = self._anchos(seccion)
        ancho_total = sum(anchos)

        if columnas:
            x = x0
            for c, titulo_col in enumerate(columnas):
                self.canvas.create_rectangle(
                    x,
                    y,
                    x + anchos[c],
                    y + self.ALTO_ENCABEZADO,
                    fill=NAVY,
                    outline=NAVY,
                )
                self.canvas.create_text(
                    x + anchos[c] / 2,
                    y + self.ALTO_ENCABEZADO / 2,
                    text=str(titulo_col),
                    font=self.fuentes.head,
                    fill="white",
                )
                x += anchos[c]
            y += self.ALTO_ENCABEZADO

        resto = set(tuple(pos) for pos in seccion.get("resto", []))
        for r, fila in enumerate(filas):
            if fila.get("separador_arriba"):
                self.canvas.create_line(
                    x0,
                    y,
                    x0 + ancho_total,
                    y,
                    fill=NAVY,
                    width=1.5,
                )
            valores = fila.get("valores", [])
            calculos = fila.get("calculos", [])
            x = x0
            for c in range(len(anchos)):
                valor = valores[c] if c < len(valores) else ""
                tipo = fila.get("tipo", "normal")
                if (r, c) in resto:
                    fill = GREEN_L
                    outline = GREEN_D
                    grosor = 2
                else:
                    fill = {
                        "coef": "#F7FAF8",
                        "producto": BLUE_L,
                        "suma": CARD,
                        "alerta": AMBER_L,
                    }.get(tipo, CARD)
                    outline = LINE
                    grosor = 1

                rect = self.canvas.create_rectangle(
                    x,
                    y,
                    x + anchos[c],
                    y + self.ALTO_FILA,
                    fill=fill,
                    outline=outline,
                    width=grosor,
                )
                texto = self.canvas.create_text(
                    x + anchos[c] / 2,
                    y + self.ALTO_FILA / 2,
                    text=str(valor),
                    font=self.fuentes.mono,
                    fill=INK,
                )
                calculo = calculos[c] if c < len(calculos) else ""
                if not calculo and str(valor):
                    calculo = f"{valor}"
                dato = _DatosCelda(rect, texto, r, c, fill, outline, calculo)
                self._celdas[(s, r, c)] = dato
                self._item_celda[rect] = dato
                self._item_celda[texto] = dato
                x += anchos[c]
            y += self.ALTO_FILA

        nota = seccion.get("nota")
        if nota:
            self.canvas.create_text(
                x0,
                y + 5,
                text=nota,
                anchor="nw",
                font=self.fuentes.small,
                fill=MUTED,
                width=max(ancho_disponible, 300),
            )
            y += self.ALTO_NOTA + 6

        return y + 12

    def _aplicar_resaltado(self):
        for dato in self._celdas.values():
            self.canvas.itemconfigure(
                dato.rect,
                fill=dato.base_fill,
                outline=dato.base_outline,
                width=2 if dato.base_outline == GREEN_D else 1,
            )

        paso = self._paso_activo
        if not paso:
            return

        indice_seccion = paso.get("seccion", 0)
        celdas = [
            dato
            for (s, _r, _c), dato in self._celdas.items()
            if s == indice_seccion
        ]
        objetivo = []

        if "fila" in paso:
            objetivo = [d for d in celdas if d.fila == paso["fila"]]
        else:
            columnas = paso.get("columnas")
            if columnas is None:
                columnas = [paso.get("columna")]
            filas = paso.get("filas")
            for dato in celdas:
                if dato.columna in columnas and (filas is None or dato.fila in filas):
                    objetivo.append(dato)

        for dato in objetivo:
            self.canvas.itemconfigure(
                dato.rect,
                fill=AMBER_L,
                outline=ORANGE,
                width=2,
            )
            self.canvas.tag_raise(dato.texto)

    # ------------------------------------------------------------------ interacción
    def _al_mover(self, evento):
        x = self.canvas.canvasx(evento.x)
        y = self.canvas.canvasy(evento.y)
        dato = None
        for item in self.canvas.find_overlapping(x - 1, y - 1, x + 1, y + 1):
            dato = self._item_celda.get(item)
            if dato is not None:
                break
        if dato is None or not dato.calculo:
            self.hover.configure(text="")
        else:
            self.hover.configure(text=dato.calculo)

    def _rueda(self, evento):
        self.canvas.yview_scroll(-1 if evento.delta > 0 else 1, "units")
        return "break"

    def _rueda_horizontal(self, evento):
        self.canvas.xview_scroll(-1 if evento.delta > 0 else 1, "units")
        return "break"
