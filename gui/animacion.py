"""Reproducción paso a paso para tablas y gráficos.

``ControladorAnimacion`` no depende de Tkinter para su lógica: guarda el
índice, avanza, retrocede y programa el siguiente cuadro con ``after``. La
barra de botones es un widget separado para poder reutilizarla en todas las
pestañas.
"""

import tkinter as tk
from tkinter import ttk

from gui.estilo import CARD, FIELD, FIELD_B, INK, MUTED, NAVY
from gui.widgets import RButton


# Milisegundos entre pasos. La velocidad se elige desde la barra.
VELOCIDADES = {
    "Lento": 1200,
    "Normal": 650,
    "Rápido": 260,
}


class ControladorAnimacion:
    """Índice y temporizador de una lista de pasos.

    El índice arranca en el último paso al configurar la lista, para que el
    resultado completo quede visible después de calcular. ``reiniciar`` vuelve
    al primer paso y ``reproducir`` recorre el resto con ``after()``.
    """

    def __init__(
        self,
        maestro=None,
        pasos=None,
        intervalo=VELOCIDADES["Normal"],
        al_cambiar=None,
        al_terminar=None,
    ):
        self.maestro = maestro
        self.pasos = list(pasos or [])
        self.intervalo = int(intervalo)
        self.al_cambiar = al_cambiar
        self.al_terminar = al_terminar
        self.indice = -1
        self.reproduciendo = False
        self._after_id = None
        if self.pasos:
            self.configurar(self.pasos)

    @property
    def total(self):
        return len(self.pasos)

    @property
    def paso_actual(self):
        if 0 <= self.indice < len(self.pasos):
            return self.pasos[self.indice]
        return None

    # ------------------------------------------------------------------ configuración
    def configurar(self, pasos, inicial=None):
        """Cambia la lista de pasos y se ubica en el último por defecto."""
        self.pausar()
        self.pasos = list(pasos or [])
        if not self.pasos:
            self.indice = -1
        else:
            if inicial is None:
                inicial = len(self.pasos) - 1
            elif inicial == "primero":
                inicial = 0
            self.indice = self._limitar(inicial)
        self._notificar()
        return self.indice

    def _limitar(self, indice):
        if not self.pasos:
            return -1
        try:
            indice = int(indice)
        except (TypeError, ValueError):
            indice = 0
        return max(0, min(indice, len(self.pasos) - 1))

    # ------------------------------------------------------------------ navegación
    def ir_a(self, indice, notificar=True):
        """Salta a un índice válido; fuera de rango se recorta."""
        if not self.pasos:
            self.indice = -1
            if notificar:
                self._notificar()
            return self.indice
        self.indice = self._limitar(indice)
        if notificar:
            self._notificar()
        return self.indice

    def siguiente(self):
        """Avanza un paso. Devuelve False si ya estaba en el último."""
        if not self.pasos or self.indice >= len(self.pasos) - 1:
            return False
        self.indice += 1
        self._notificar()
        return True

    def anterior(self):
        """Retrocede un paso. Devuelve False si ya estaba en el primero."""
        if not self.pasos or self.indice <= 0:
            return False
        self.indice -= 1
        self._notificar()
        return True

    # Nombres equivalentes, útiles para tests y para otras vistas.
    avanzar = siguiente
    retroceder = anterior

    def reiniciar(self):
        """Vuelve al primer paso y detiene la reproducción."""
        self.pausar()
        if self.pasos:
            self.indice = 0
        else:
            self.indice = -1
        self._notificar()
        return self.indice

    # ------------------------------------------------------------------ reproducción
    def reproducir(self):
        """Arranca o continúa la reproducción con ``after``."""
        if not self.pasos or len(self.pasos) <= 1 or self.reproduciendo:
            return False
        if self.indice >= len(self.pasos) - 1:
            self.indice = 0
            self._notificar()
        self.reproduciendo = True
        self._programar()
        self._notificar()
        return True

    def pausar(self):
        """Detiene el temporizador; no cambia el índice."""
        self.reproduciendo = False
        if self._after_id is not None and self.maestro is not None:
            try:
                self.maestro.after_cancel(self._after_id)
            except (tk.TclError, ValueError):
                pass
        self._after_id = None

    def alternar(self):
        """Reproduce o pausa según el estado actual."""
        if self.reproduciendo:
            self.pausar()
            self._notificar()
            return False
        return self.reproducir()

    def set_velocidad(self, nombre):
        """Cambia el intervalo entre pasos ('Lento', 'Normal' o 'Rápido')."""
        self.intervalo = int(VELOCIDADES.get(nombre, VELOCIDADES["Normal"]))
        if self.reproduciendo:
            self.pausar()
            self.reproduciendo = True
            self._programar()
        return self.intervalo

    def cerrar(self):
        self.pausar()

    # ------------------------------------------------------------------ interno
    def _programar(self):
        if self.maestro is None:
            return
        if self._after_id is not None:
            try:
                self.maestro.after_cancel(self._after_id)
            except (tk.TclError, ValueError):
                pass
        self._after_id = self.maestro.after(self.intervalo, self._tick)

    def _tick(self):
        self._after_id = None
        if not self.reproduciendo:
            return
        if self.indice >= len(self.pasos) - 1:
            self.reproduciendo = False
            self._notificar()
            if self.al_terminar is not None:
                self.al_terminar()
            return
        self.indice += 1
        self._notificar()
        if self.indice >= len(self.pasos) - 1:
            self.reproduciendo = False
            if self.al_terminar is not None:
                self.al_terminar()
        else:
            self._programar()

    def _notificar(self):
        if self.al_cambiar is not None:
            self.al_cambiar(self.indice)


class BarraAnimacion(tk.Frame):
    """Controles compactos para reproducir los pasos de la pestaña."""

    def __init__(self, master, fuentes, al_cambiar=None, bg=CARD):
        super().__init__(master, bg=bg)
        self.fuentes = fuentes
        self.bg = bg
        self._al_cambiar = al_cambiar
        self._listo = False

        self.controlador = ControladorAnimacion(
            maestro=self,
            al_cambiar=self._cambio,
            al_terminar=self._termino,
        )

        fila = tk.Frame(self, bg=bg)
        fila.pack(fill="x")
        for i in range(4):
            fila.columnconfigure(i, weight=1, uniform="anim")

        self.b_reiniciar = self._boton(fila, "Reiniciar", self._reiniciar, 0, 74)
        self.b_anterior = self._boton(fila, "Anterior", self._anterior, 1, 64)
        self.b_reproducir = self._boton(fila, "Reproducir", self._reproducir, 2, 86)
        self.b_siguiente = self._boton(fila, "Siguiente", self._siguiente, 3, 70)

        fila2 = tk.Frame(self, bg=bg)
        fila2.pack(fill="x", pady=(5, 0))
        self.lbl_paso = tk.Label(
            fila2,
            text="Sin pasos",
            font=fuentes.small,
            bg=bg,
            fg=MUTED,
            anchor="w",
        )
        self.lbl_paso.pack(side="left")
        tk.Label(
            fila2,
            text="Velocidad",
            font=fuentes.small,
            bg=bg,
            fg=MUTED,
        ).pack(side="right", padx=(0, 5))
        self.v_velocidad = tk.StringVar(value="Normal")
        self.combo = ttk.Combobox(
            fila2,
            textvariable=self.v_velocidad,
            values=list(VELOCIDADES),
            state="readonly",
            width=7,
            style="Calc.TCombobox",
            font=fuentes.small,
        )
        self.combo.pack(side="right", padx=(0, 8))
        self.combo.bind("<<ComboboxSelected>>", lambda _: self._cambiar_velocidad())

        self._listo = True
        self._actualizar()

    def _boton(self, parent, texto, comando, columna, ancho):
        boton = RButton(
            parent,
            texto,
            comando,
            FIELD,
            INK,
            "#EDF2EF",
            outline=FIELD_B,
            font=self.fuentes.small,
            height=30,
            bg=self.bg,
        )
        boton.configure(width=ancho)
        boton.grid(row=0, column=columna, sticky="ew", padx=(0 if columna == 0 else 4, 0))
        return boton

    # ------------------------------------------------------------------ API
    def configurar(self, pasos, inicial=None):
        """Carga los pasos; por defecto deja visible el resultado completo."""
        self.controlador.configurar(pasos, inicial=inicial)
        self._actualizar()

    def detener(self):
        self.controlador.pausar()
        self._actualizar()

    def cerrar(self):
        self.controlador.cerrar()

    def redibujar(self):
        for boton in (
            self.b_reiniciar,
            self.b_anterior,
            self.b_reproducir,
            self.b_siguiente,
        ):
            boton._dibujar()

    # ------------------------------------------------------------------ callbacks
    def _reiniciar(self):
        self.controlador.reiniciar()
        self._actualizar()

    def _anterior(self):
        self.controlador.anterior()
        self._actualizar()

    def _siguiente(self):
        self.controlador.siguiente()
        self._actualizar()

    def _reproducir(self):
        self.controlador.alternar()
        self._actualizar()

    def _cambiar_velocidad(self):
        self.controlador.set_velocidad(self.v_velocidad.get())

    def _termino(self):
        self._actualizar()

    def _cambio(self, indice):
        self._actualizar()
        if self._listo and self._al_cambiar is not None:
            self._al_cambiar(indice)

    def _actualizar(self):
        if not hasattr(self, "b_reiniciar"):
            return
        total = self.controlador.total
        indice = self.controlador.indice
        if total == 0:
            self.lbl_paso.configure(text="Sin pasos")
        elif indice < 0:
            self.lbl_paso.configure(text=f"0/{total}")
        else:
            self.lbl_paso.configure(text=f"Paso {indice + 1}/{total}")

        activo = total > 1
        self.b_reiniciar.set_habilitado(total > 0)
        self.b_anterior.set_habilitado(activo and indice > 0)
        self.b_siguiente.set_habilitado(activo and indice < total - 1)
        self.b_reproducir.set_habilitado(activo)
        self.b_reproducir.set_texto(
            "Pausar" if self.controlador.reproduciendo else "Reproducir"
        )
