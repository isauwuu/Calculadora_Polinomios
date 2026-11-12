"""Pestaña 5: sucesión de Sturm, conteo y separación de raíces."""

import tkinter as tk

from gui import controlador
from gui.estilo import AMBER_L, CARD, GREEN_L, INK, LINE, MUTED, NAVY, ORANGE
from gui.formato import (
    formatear_fraccion,
    formatear_intervalo,
    formatear_polinomio,
    formatear_signo,
)
from gui.graficos import texto_referencia
from gui.pestanas.base import PestanaBase


class PestanaSturm(PestanaBase):
    titulo_tabla = "Sucesión de Sturm"
    subtitulo_tabla = "(signos en los extremos)"

    def construir_entrada(self, parent):
        self.v_coef = tk.StringVar(value="4, 0, -5, 0, 1")
        self.v_a = tk.StringVar(value="-2")
        self.v_b = tk.StringVar(value="2")
        self.v_modo = tk.StringVar(value="Estándar")

        self.campo(
            parent,
            "Coeficientes (de mayor a menor grado)",
            self.v_coef,
            "Acepta enteros, decimales y fracciones: 3/2",
        )
        self.campo(parent, "Extremo inferior  a", self.v_a)
        self.campo(parent, "Extremo superior  b", self.v_b)
        self.segmentado(
            parent,
            "Sucesión",
            self.v_modo,
            ["Estándar", "Simplificada"],
        )
        tk.Label(
            parent,
            text=(
                "El intervalo es abierto: (a, b).\n"
                "Ningún extremo puede ser raíz de P."
            ),
            font=self.fuentes.small,
            bg=CARD,
            fg=MUTED,
            justify="left",
            anchor="w",
            wraplength=230,
        ).pack(fill="x", pady=(10, 0))
        self._configurar_columnas()

    # ------------------------------------------------------------------ columnas
    def _configurar_columnas(self):
        self.tabla.configurar(
            [
                ("i", "i", 34, "center"),
                ("polinomio", "P_i(x)", 220, "w"),
                ("signo_a", "Signo en a", 82, "center"),
                ("signo_b", "Signo en b", 82, "center"),
            ]
        )

    # ------------------------------------------------------------------ cálculo
    def _calcular(self):
        self._texto_coef = self.v_coef.get()
        self._coef = controlador.coeficientes_float(self._texto_coef)
        self._modo = self.v_modo.get()
        self._a = controlador.parsear_racional(self.v_a.get(), "el extremo a")
        self._b = controlador.parsear_racional(self.v_b.get(), "el extremo b")
        return controlador.sturm(
            self._texto_coef,
            self.v_a.get(),
            self.v_b.get(),
            simplificada=self._modo.startswith("Simpl"),
        )

    # ------------------------------------------------------------------ filas
    def _filas(self, pasos):
        return [
            {
                "i": str(paso.get("i", "")),
                "polinomio": formatear_polinomio(paso.get("coef", [])),
                "signo_a": formatear_signo(paso.get("signo_a")),
                "signo_b": formatear_signo(paso.get("signo_b")),
            }
            for paso in pasos
        ]

    def _tags(self, filas, pasos):
        etiquetas = []
        for i, paso in enumerate(pasos):
            if paso.get("signo_a") == 0 or paso.get("signo_b") == 0:
                etiquetas.append(("cero",))
            elif i % 2:
                etiquetas.append(("odd",))
            else:
                etiquetas.append(())
        return etiquetas

    # ------------------------------------------------------------------ resultado
    def _mostrar_resultado(self, resultado):
        cantidad = resultado.valor["cantidad"]
        intervalos = resultado.valor["intervalos"]
        filas = self._filas(resultado.pasos)
        self.tabla.cargar(filas, self._tags(filas, resultado.pasos))
        self._mostrar_tarjeta()

        intervalo = formatear_intervalo(self._a, self._b)
        if cantidad == 0:
            principal = f"Sin raíces en {intervalo}"
        else:
            sustantivo = "raíz" if cantidad == 1 else "raíces"
            principal = f"{cantidad} {sustantivo} en {intervalo}"

        if intervalos:
            detalle = "Aisladas: " + ", ".join(
                formatear_intervalo(a, b) for a, b in intervalos
            )
        else:
            cantidad_polinomios = len(resultado.pasos)
            sustantivo = "polinomio" if cantidad_polinomios == 1 else "polinomios"
            detalle = f"Sturm {self._modo.lower()} · {cantidad_polinomios} {sustantivo}."

        self.resultado.lbl_principal.configure(
            font=self.fuentes.big if len(principal) <= 34 else self.fuentes.h2
        )
        self.resultado.mostrar(
            principal,
            detalle,
            texto_referencia(self._coef),
            tono="amber" if resultado.avisos else "verde",
        )
        self._estados_sturm = []
        try:
            datos = controlador.biseccion_sturm(
                self._texto_coef,
                self.v_a.get(),
                self.v_b.get(),
                simplificada=self._modo.startswith("Simpl"),
            )
            self._estados_sturm = datos.get("estados", [])
        except Exception:
            # La animación es opcional: si falla, queda el resultado estático.
            self._estados_sturm = []
        self._dibujar(intervalos)
        self._animar([{"i": i} for i in range(len(self._estados_sturm))])

    def _mensaje_exito(self, resultado):
        cantidad = resultado.valor["cantidad"]
        intervalos = resultado.valor["intervalos"]
        intervalo = formatear_intervalo(self._a, self._b)
        if cantidad == 0:
            return f"Sturm: no hay raíces distintas en {intervalo}."
        sustantivo = "raíz distinta" if cantidad == 1 else "raíces distintas"
        mensaje = f"Sturm: {cantidad} {sustantivo} en {intervalo}."
        if len(intervalos) == 1:
            mensaje += " Intervalo aislado."
        elif intervalos:
            mensaje += f" {len(intervalos)} intervalos aislados."
        return mensaje

    # ------------------------------------------------------------------ gráfico
    def _dibujar(self, intervalos):
        a, b = float(self._a), float(self._b)
        titulo = f"P(x) = {self._texto_coef.strip()[:42]}"
        self.grafico.dibujar(self._coef, puntos=[a, b], titulo=titulo)
        ax = self.grafico.ax

        ax.axvspan(a, b, color=AMBER_L, alpha=0.5, label="Intervalo (a, b)", zorder=1)
        for x, nombre, valor in ((a, "a", self._a), (b, "b", self._b)):
            ax.axvline(
                x,
                color=ORANGE,
                lw=1.1,
                ls="--",
                label=f"{nombre} = {formatear_fraccion(valor)}",
                zorder=2,
            )

        self._artistas_sturm = []
        self._texto_sturm = ax.text(
            0.02,
            0.98,
            "",
            transform=ax.transAxes,
            ha="left",
            va="top",
            fontsize=7,
            color=MUTED,
            zorder=10,
        )

        if not self._estados_sturm:
            # Sin estados de bisección queda la separación final calculada.
            for i, (izq, der) in enumerate(intervalos):
                ax.axvspan(
                    float(izq),
                    float(der),
                    color=GREEN_L,
                    alpha=0.9,
                    label="Raíz aislada" if i == 0 else None,
                    zorder=1,
                )
        self.grafico.finalizar(ubicacion="best")

    def _aplicar_paso(self, indice):
        """Muestra la bisección acumulada hasta el paso activo.

        La tabla de esta pestaña es la sucesión de Sturm, no los subintervalos:
        por eso no se resalta una fila, solo se redibujan las bandas.
        """
        for artista in getattr(self, "_artistas_sturm", []):
            try:
                artista.remove()
            except (ValueError, AttributeError):
                pass
        self._artistas_sturm = []
        self.tabla.quitar_seleccion()

        texto = getattr(self, "_texto_sturm", None)
        if texto is not None:
            texto.set_text("")

        if indice < 0 or not self._estados_sturm:
            self.grafico.redibujar()
            return

        indice = min(indice, len(self._estados_sturm) - 1)
        estado = self._estados_sturm[indice]
        ax = self.grafico.ax

        for x, y, cantidad in estado.get("intervalos", []):
            if cantidad <= 0:
                continue
            x, y = float(x), float(y)
            color = GREEN_L if cantidad == 1 else AMBER_L
            self._artistas_sturm.append(
                ax.axvspan(x, y, color=color, alpha=0.85, zorder=1)
            )
            sustantivo = "raíz" if cantidad == 1 else "raíces"
            self._artistas_sturm.append(
                ax.text(
                    (x + y) / 2.0,
                    0.96,
                    f"{cantidad} {sustantivo}",
                    transform=ax.get_xaxis_transform(),
                    ha="center",
                    va="top",
                    fontsize=7,
                    color=NAVY,
                    bbox=dict(
                        boxstyle="round,pad=0.18",
                        fc="white",
                        ec=LINE,
                        alpha=0.88,
                    ),
                    zorder=10,
                )
            )

        division = estado.get("division")
        if division:
            self._artistas_sturm.append(
                ax.axvline(
                    float(division[2]),
                    color=NAVY,
                    lw=1.0,
                    ls="--",
                    zorder=4,
                )
            )
        if texto is not None:
            texto.set_text(
                f"Bisección de Sturm · paso {indice + 1}/{len(self._estados_sturm)}"
            )
        self.grafico.redibujar()

    def _mostrar_pasos_error(self, pasos):
        self._configurar_columnas()
        filas = self._filas(pasos)
        self.tabla.cargar(filas, self._tags(filas, pasos))
