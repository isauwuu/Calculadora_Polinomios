"""ReproducciÃ³n paso a paso para tablas y grÃ¡ficos.

``ControladorAnimacion`` no depende de Tkinter para su lÃ³gica: guarda el
Ã­ndice, avanza, retrocede y programa el siguiente cuadro con ``after``.
"""

import tkinter as tk


# Milisegundos entre pasos. La velocidad se elige desde la barra.
VELOCIDADES = {
    "Lento": 1200,
    "Normal": 650,
    "RÃ¡pido": 260,
}


class ControladorAnimacion:
    """Ãndice y temporizador de una lista de pasos.

    El Ã­ndice arranca en el Ãºltimo paso al configurar la lista, para que el
    resultado completo quede visible despuÃ©s de calcular. ``reiniciar`` vuelve
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

    # ------------------------------------------------------------------ configuraciÃ³n
    def configurar(self, pasos, inicial=None):
        """Cambia la lista de pasos y se ubica en el Ãºltimo por defecto."""
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

    # ------------------------------------------------------------------ navegaciÃ³n
    def ir_a(self, indice, notificar=True):
        """Salta a un Ã­ndice vÃ¡lido; fuera de rango se recorta."""
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
        """Avanza un paso. Devuelve False si ya estaba en el Ãºltimo."""
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

    # Nombres equivalentes, Ãºtiles para tests y para otras vistas.
    avanzar = siguiente
    retroceder = anterior

    def reiniciar(self):
        """Vuelve al primer paso y detiene la reproducciÃ³n."""
        self.pausar()
        if self.pasos:
            self.indice = 0
        else:
            self.indice = -1
        self._notificar()
        return self.indice

    # ------------------------------------------------------------------ reproducciÃ³n
    def reproducir(self):
        """Arranca o continÃºa la reproducciÃ³n con ``after``."""
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
        """Detiene el temporizador; no cambia el Ã­ndice."""
        self.reproduciendo = False
        if self._after_id is not None and self.maestro is not None:
            try:
                self.maestro.after_cancel(self._after_id)
            except (tk.TclError, ValueError):
                pass
        self._after_id = None

    def alternar(self):
        """Reproduce o pausa segÃºn el estado actual."""
        if self.reproduciendo:
            self.pausar()
            self._notificar()
            return False
        return self.reproducir()

    def set_velocidad(self, nombre):
        """Cambia el intervalo entre pasos ('Lento', 'Normal' o 'RÃ¡pido')."""
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

