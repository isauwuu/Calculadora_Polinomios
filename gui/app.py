"""Ventana principal: encabezado, pestañas, cuerpo y barra de estado."""

import tkinter as tk

from gui import imagenes
from gui.estilo import BG, CARD, INK, MUTED, Fuentes, crear_estilos
from gui.graficos import configurar_fuente
from gui.pestanas.p1_evaluar_dividir import PestanaEvaluarDividir
from gui.pestanas.p2_enteras_racionales import PestanaEnterasRacionales
from gui.pestanas.p4_newton_halley import PestanaNewtonHalley
from gui.pestanas.placeholder import PestanaPlaceholder
from gui.widgets import Card, TabBar


ETIQUETAS = [
    "Evaluar y dividir",
    "Enteras y racionales",
    "Cotas",
    "Newton y Halley",
    "Sturm",
    "Bairstow",
]


class App(tk.Tk):
    """Ventana principal de la calculadora."""

    def __init__(self):
        super().__init__()
        self.title("Raíces de Polinomios")
        self.configure(bg=BG)
        self.minsize(1100, 700)
        self.fuentes = Fuentes(self)
        crear_estilos(self, self.fuentes)
        configurar_fuente(self.fuentes.familia)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self._crear_iconos()
        self._crear_encabezado()
        self._crear_pestanas()
        self._crear_cuerpo()
        self._crear_estado()

        self._pagina_actual = None
        self._mostrar_pagina(0)
        self.protocol("WM_DELETE_WINDOW", self._cerrar)
        self.after(0, self._centrar)

    # ------------------------------------------------------------------ piezas
    def _crear_iconos(self):
        self.iconos = {
            "sparkle": imagenes.photo(imagenes.icon_image("sparkle", 26, "#2F9A5B")),
            "table": imagenes.photo(imagenes.icon_image("table", 22, "#2F9A5B")),
            "chart": imagenes.photo(imagenes.icon_image("chart", 22, "#2F9A5B")),
            "play": imagenes.photo(imagenes.icon_image("play", 15, "#FFFFFF")),
            "trash": imagenes.photo(imagenes.icon_image("trash", 15, "#6A7B86")),
            "dot_ok": imagenes.photo(imagenes.icon_image("dot", 14, "#2F9A5B")),
            "dot_advertencia": imagenes.photo(imagenes.icon_image("dot", 14, "#E39A12")),
            "dot_error": imagenes.photo(imagenes.icon_image("dot", 14, "#D64545")),
        }

    def _crear_encabezado(self):
        self.encabezado = tk.Canvas(self, height=64, bg=BG, highlightthickness=0, bd=0)
        self.encabezado.grid(row=0, column=0, sticky="ew")
        self.encabezado.bind("<Configure>", self._dibujar_encabezado)

    def _crear_pestanas(self):
        self.tabbar = TabBar(self, ETIQUETAS, self.fuentes.tab, self._mostrar_pagina)
        self.tabbar.grid(row=1, column=0, sticky="w", padx=14, pady=(8, 2))

    def _crear_cuerpo(self):
        self.cuerpo = tk.Frame(self, bg=BG)
        self.cuerpo.grid(row=2, column=0, sticky="nsew", padx=10, pady=(2, 6))
        self.cuerpo.grid_rowconfigure(0, weight=1)
        self.cuerpo.grid_columnconfigure(0, weight=1)
        self.paginas = [
            PestanaPlaceholder(self.cuerpo, self, i + 1, etiqueta)
            for i, etiqueta in enumerate(ETIQUETAS)
        ]
        self.paginas[0] = PestanaEvaluarDividir(self.cuerpo, self)
        self.paginas[1] = PestanaEnterasRacionales(self.cuerpo, self)
        self.paginas[3] = PestanaNewtonHalley(self.cuerpo, self)

    def _crear_estado(self):
        self.status = Card(self, r=12, fill=CARD, outer=BG, shadow=False, pad=11)
        self.status.configure(height=70)
        self.status.grid(row=3, column=0, sticky="ew", padx=10, pady=(0, 8))
        fila = tk.Frame(self.status.inner, bg=CARD)
        fila.pack(fill="both", expand=True)
        self.st_dot = tk.Label(fila, image=self.iconos["dot_ok"], bg=CARD)
        self.st_dot.pack(side="left", padx=(0, 10))
        columna = tk.Frame(fila, bg=CARD)
        columna.pack(side="left", fill="x", expand=True)
        tk.Label(
            columna,
            text="Estado",
            font=self.fuentes.small,
            bg=CARD,
            fg=MUTED,
            anchor="w",
        ).pack(anchor="w")
        self.st_msg = tk.Label(
            columna,
            text="Listo. Ingresá los datos y presioná Calcular.",
            font=self.fuentes.normal,
            bg=CARD,
            fg=INK,
            anchor="w",
            justify="left",
            wraplength=1000,
        )
        self.st_msg.pack(anchor="w")

    # ------------------------------------------------------------------ encabezado
    def _dibujar_encabezado(self, evento):
        w = max(evento.width, 8)
        h = 64
        t1 = 128 + self.fuentes.title.measure("Raíces de Polinomios") + 18
        self._imagen_encabezado = imagenes.photo(imagenes.header_image(w, h, 106, t1))
        self.encabezado.delete("all")
        self.encabezado.create_image(0, 0, image=self._imagen_encabezado, anchor="nw")
        self.encabezado.create_text(
            128,
            h / 2,
            text="Raíces de Polinomios",
            anchor="w",
            font=self.fuentes.title,
            fill="white",
        )
        self.encabezado.create_text(
            t1 + 14,
            h / 2,
            text="Programación Numérica (UNSa)",
            anchor="w",
            font=self.fuentes.subtitle,
            fill="#DCE8EE",
        )

    # ------------------------------------------------------------------ páginas
    def _mostrar_pagina(self, indice):
        pagina = self.paginas[indice]
        if self._pagina_actual is pagina:
            self.tabbar.select(indice, fire=False)
            return
        if self._pagina_actual is not None:
            self._pagina_actual.grid_remove()
        pagina.grid(row=0, column=0, sticky="nsew")
        pagina.tkraise()
        self._pagina_actual = pagina
        self.tabbar.select(indice, fire=False)
        pagina.al_mostrar()
        self.estado("ok", "Listo. Ingresá los datos y presioná Calcular.")

    def estado(self, tipo, mensaje):
        """Actualiza el punto y el texto de la barra de estado."""
        icono = {
            "ok": "dot_ok",
            "advertencia": "dot_advertencia",
            "error": "dot_error",
        }.get(tipo, "dot_ok")
        self.st_dot.configure(image=self.iconos[icono])
        self.st_msg.configure(text=mensaje)

    def _centrar(self):
        try:
            ancho, alto = 1280, 800
            x = max(0, (self.winfo_screenwidth() - ancho) // 2)
            y = max(0, (self.winfo_screenheight() - alto) // 2)
            self.geometry(f"{ancho}x{alto}+{x}+{y}")
        except tk.TclError:
            self.geometry("1280x800")

    def _cerrar(self):
        for pagina in getattr(self, "paginas", []):
            try:
                pagina.cerrar()
            except Exception:
                pass
        self.destroy()
