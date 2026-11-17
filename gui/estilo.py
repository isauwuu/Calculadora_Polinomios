"""Paleta, fuentes y estilos ttk compartidos por toda la interfaz."""

import tkinter as tk
from tkinter import font as tkfont
from tkinter import ttk

# --------------------------------------------------------------------------- paleta
BG = "#F1F5F3"
CARD = "#FFFFFF"
LINE = "#DAE3DE"
INK = "#17303F"
MUTED = "#6A7B86"
NAVY = "#13335A"
GREEN = "#2F9A5B"
GREEN_D = "#25804B"
GREEN_L = "#E7F4EB"
GREEN_B = "#BEE0C9"
FIELD = "#F8FAF9"
FIELD_B = "#CFDAD4"
AMBER = "#A65F00"
AMBER_L = "#FFF4DC"
AMBER_B = "#F2C46A"
ORANGE = "#F4A83A"
PLOT = "#1D3F9E"
RED = "#A83232"
RED_L = "#FDECEC"
RED_B = "#E8B4B4"
BLUE_L = "#EAF0F7"
RUFFINI_LINE = "#A9B7C0"
RUFFINI_BAND = "#E8F1FA"
RUFFINI_BOX = "#F3F5F6"
RUFFINI_PRODUCT = "#58708A"


def _primera_familia(root, candidatas):
    """Devuelve la primera fuente instalada de la lista, o la del sistema."""
    disponibles = set(tkfont.families(root))
    for familia in candidatas:
        if familia in disponibles:
            return familia
    return tkfont.nametofont("TkDefaultFont").actual("family")


class Fuentes:
    """Fuentes de la aplicación con fallback si Inter no está instalada."""

    def __init__(self, root):
        self.familia = _primera_familia(
            root, ("Inter", "Segoe UI", "Trebuchet MS", "DejaVu Sans")
        )
        self.mono = _primera_familia(
            root, ("Cascadia Mono", "Consolas", "DejaVu Sans Mono", "Courier New")
        )
        # Serif tipo apunte para los esquemas de Ruffini.
        self.math_familia = _primera_familia(
            root,
            ("DejaVu Serif", "Liberation Serif", "Noto Serif", "Georgia", "Times New Roman"),
        )

        def F(**opciones):
            return tkfont.Font(root=root, family=self.familia, **opciones)

        def M(**opciones):
            return tkfont.Font(root=root, family=self.mono, **opciones)

        def S(**opciones):
            return tkfont.Font(root=root, family=self.math_familia, **opciones)

        # Tamaños en píxeles (los negativos evitan el escalado automático de Tk).
        self.title = F(size=-26, weight="bold")
        self.subtitle = F(size=-14)
        self.tab = F(size=-15)
        self.h2 = F(size=-20, weight="bold")
        self.h3 = F(size=-18, weight="bold")
        self.label = F(size=-15)
        self.small = F(size=-13)
        self.small_italic = F(size=-13, slant="italic")
        self.hint = F(size=-13, slant="italic")
        self.button = F(size=-15, weight="bold")
        self.entry = M(size=-15)
        self.big = F(size=-27, weight="bold")
        self.normal = F(size=-15)
        self.bold = F(size=-15, weight="bold")
        self.value = F(size=-18, weight="bold")
        self.mono = M(size=-15)
        self.mono_bold = M(size=-15, weight="bold")
        self.head = F(size=-14, weight="bold")

        # Esquemas matemáticos: números grandes y etiquetas más chicas.
        self.math = S(size=-18)
        self.math_bold = S(size=-18, weight="bold")
        self.math_label = S(size=-15)
        self.math_small = S(size=-13)
        self.math_small_bold = S(size=-13, weight="bold")
        self.math_sub = S(size=-10)
        self.math_italic = S(size=-13, slant="italic")


def crear_estilos(root, fuentes):
    """Configura ttk para que Treeview y Combobox sigan la estética de las tarjetas."""
    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except tk.TclError:
        pass

    style.configure(
        "Calc.Treeview",
        background=CARD,
        fieldbackground=CARD,
        foreground=INK,
        rowheight=34,
        borderwidth=0,
        font=fuentes.mono,
    )
    style.configure(
        "Calc.Treeview.Heading",
        background=NAVY,
        foreground="white",
        font=fuentes.head,
        relief="flat",
        padding=(8, 8),
        borderwidth=0,
        bordercolor=NAVY,
        lightcolor=NAVY,
        darkcolor=NAVY,
    )
    style.map("Calc.Treeview.Heading", background=[("active", NAVY)])
    style.map(
        "Calc.Treeview",
        background=[("selected", GREEN_L)],
        foreground=[("selected", INK)],
    )
    style.layout("Calc.Treeview", [("Treeview.treearea", {"sticky": "nswe"})])

    style.configure(
        "Calc.TCombobox",
        font=fuentes.normal,
        fieldbackground=FIELD,
        background=FIELD,
        foreground=INK,
        arrowcolor=NAVY,
        bordercolor=FIELD_B,
        lightcolor=FIELD_B,
        darkcolor=FIELD_B,
        padding=(8, 7),
    )
    style.configure(
        "Calc.TNotebook",
        background=CARD,
        borderwidth=0,
        tabmargins=(0, 0, 0, 0),
    )
    style.configure(
        "Calc.TNotebook.Tab",
        background="#EAF0ED",
        foreground=INK,
        font=fuentes.normal,
        padding=(16, 8),
        borderwidth=0,
    )
    style.map(
        "Calc.TNotebook.Tab",
        background=[("selected", CARD), ("active", GREEN_L)],
        foreground=[("selected", NAVY)],
    )
    style.map(
        "Calc.TCombobox",
        fieldbackground=[("readonly", FIELD)],
        foreground=[("readonly", INK)],
        selectbackground=[("readonly", FIELD)],
        selectforeground=[("readonly", INK)],
    )
    root.option_add("*TCombobox*Listbox.font", fuentes.normal)
    root.option_add("*TCombobox*Listbox.background", CARD)
    root.option_add("*TCombobox*Listbox.foreground", INK)
    root.option_add("*TCombobox*Listbox.selectBackground", GREEN_L)
    root.option_add("*TCombobox*Listbox.selectForeground", INK)
    # Barras finas, sin flechas y con el riel del color de la tarjeta.
    for orient, sticky in (("Vertical", "ns"), ("Horizontal", "ew")):
        estilo = f"{orient}.TScrollbar"
        style.configure(
            estilo,
            background="#B7C8D2",
            troughcolor=CARD,
            bordercolor=CARD,
            lightcolor=CARD,
            darkcolor=CARD,
            arrowcolor=CARD,
            arrowsize=0,
            borderwidth=0,
            relief="flat",
            width=8,
        )
        style.map(estilo, background=[("active", "#9FB3BF")])
        style.layout(
            estilo,
            [
                (
                    f"{orient}.Scrollbar.trough",
                    {
                        "sticky": sticky,
                        "children": [
                            (
                                f"{orient}.Scrollbar.thumb",
                                {"expand": "1", "sticky": "nswe"},
                            )
                        ],
                    },
                )
            ],
        )