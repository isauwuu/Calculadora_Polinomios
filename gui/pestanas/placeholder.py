"""Pestaña temporal para las etapas intermedias de la interfaz."""

import tkinter as tk

from core.errores import EntradaInvalida
from gui.estilo import CARD, MUTED
from gui.pestanas.base import PestanaBase


class PestanaPlaceholder(PestanaBase):
    """Muestra el esquema común mientras se implementa una pestaña."""

    def __init__(self, master, app, numero=1, nombre="Pestaña"):
        self.numero = numero
        self.nombre = nombre
        super().__init__(master, app)

    def construir_entrada(self, parent):
        tk.Label(
            parent,
            text=f"Pestaña {self.numero}: {self.nombre}",
            font=self.fuentes.bold,
            bg=CARD,
            fg=MUTED,
            wraplength=220,
            justify="left",
        ).pack(anchor="w", pady=(10, 0))
        tk.Label(
            parent,
            text="La estructura visual ya está lista. El contenido se implementa en la próxima etapa.",
            font=self.fuentes.small,
            bg=CARD,
            fg=MUTED,
            wraplength=220,
            justify="left",
        ).pack(anchor="w", pady=(6, 0))

    def _calcular(self):
        raise EntradaInvalida("Esta pestaña todavía no está implementada.")

    def _mostrar_resultado(self, resultado):
        return None
