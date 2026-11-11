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

        def F(**opciones):
            return tkfont.Font(root=root, family=self.familia, **opciones)

        def M(**opciones):
            return tkfont.Font(root=root, family=self.mono, **opciones)

        self.title = F(size=-25, weight="bold")
        self.subtitle = F(size=-13)
        self.tab = F(size=-12)
        self.h2 = F(size=-17, weight="bold")
        self.label = F(size=-12)
        self.small = F(size=-10)
        self.small_italic = F(size=-10, slant="italic")
        self.hint = F(size=-10, slant="italic")
        self.button = F(size=-13, weight="bold")
        self.entry = M(size=-13)
        self.big = F(size=-24, weight="bold")
        self.normal = F(size=-12)
        self.bold = F(size=-12, weight="bold")
        self.mono = M(size=-11)
        self.mono_bold = M(size=-11, weight="bold")
        self.head = F(size=-11, weight="bold")


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
        rowheight=29,
        borderwidth=0,
        font=fuentes.mono,
    )
    style.configure(
        "Calc.Treeview.Heading",
        background=NAVY,
        foreground="white",
        font=fuentes.head,
        relief="flat",
        padding=(7, 7),
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
        padding=(7, 6),
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
