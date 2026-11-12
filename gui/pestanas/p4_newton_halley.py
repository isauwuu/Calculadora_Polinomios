"""Pestaña 4: Newton-Raphson-Horner y Halley."""

import tkinter as tk

from gui import controlador
from gui.estilo import CARD
from gui.formato import formatear_cientifico, formatear_float
from gui.graficos import texto_referencia
from gui.pestanas.base import PestanaBase


class PestanaNewtonHalley(PestanaBase):
    titulo_tabla = "Iteraciones"
    subtitulo_tabla = "(campo 'pasos' del Resultado)"

    def construir_entrada(self, parent):
        self.v_coef = tk.StringVar(value="1, 0, -5, -3")
        self.v_x0 = tk.StringVar(value="2")
        self.v_eps = tk.StringVar(value="1e-3")
        self.v_max = tk.StringVar(value="100")
        self.v_metodo = tk.StringVar(value="Newton")

        self.campo(
            parent,
            "Coeficientes (de mayor a menor grado)",
            self.v_coef,
            "Acepta enteros, decimales y fracciones: 3/2",
        )
        self.campo(parent, "Punto inicial  x₀", self.v_x0)
        self.campo(parent, "Tolerancia  ε", self.v_eps)
        self.campo(parent, "Máximo de iteraciones", self.v_max)
        self.segmentado(parent, "Método", self.v_metodo, ["Newton", "Halley"])
        self._configurar_columnas("Newton")

    def _configurar_columnas(self, metodo):
        columnas = [
            ("n", "n", 30, "center"),
            ("xn", "x_n", 70, "e"),
            ("p", "P(x_n)", 72, "e"),
            ("dp", "P'(x_n)", 72, "e"),
        ]
        if str(metodo).lower().startswith("halley"):
            columnas.append(("d2p", "P''(x_n)", 72, "e"))
        columnas.append(("dx", "|dx|", 64, "e"))
        self.tabla.configurar(columnas)

    def _calcular(self):
        self._texto_coef = self.v_coef.get()
        self._coef = controlador.coeficientes_float(self._texto_coef)
        self._metodo = self.v_metodo.get()
        self._configurar_columnas(self._metodo)
        return controlador.newton_halley(
            self._texto_coef,
            self.v_x0.get(),
            self.v_eps.get(),
            self.v_max.get(),
            self._metodo,
        )

    def _filas(self, pasos):
        filas = []
        for paso in pasos:
            filas.append(
                {
                    "n": str(paso["n"]),
                    "xn": formatear_float(paso["x"]),
                    "p": formatear_float(paso["p"]),
                    "dp": formatear_float(paso["dp"]),
                    "d2p": formatear_float(paso.get("d2p", "—")),
                    "dx": formatear_float(abs(paso["dx"])),
                }
            )
        return filas

    def _tags(self, filas, resultado):
        rojas = set((resultado.diagnostico or {}).get("filas_rojas", []))
        etiquetas = []
        for i in range(len(filas)):
            if i in rojas:
                etiquetas.append(("roja",))
            elif i == len(filas) - 1 and resultado.convergio:
                etiquetas.append(("final",))
            elif i % 2:
                etiquetas.append(("odd",))
            else:
                etiquetas.append(())
        return etiquetas

    def _mostrar_resultado(self, resultado):
        filas = self._filas(resultado.pasos)
        self.tabla.cargar(filas, self._tags(filas, resultado))
        self._mostrar_tarjeta()

        tono = "verde" if resultado.convergio else "amber"
        if resultado.convergio:
            detalle = (
                f"{self._metodo} · {resultado.iteraciones} iteraciones · "
                f"error final {formatear_cientifico(resultado.error)}"
            )
        else:
            detalle = (
                f"No convergió en {resultado.iteraciones} iteraciones · "
                f"|dx| final {formatear_cientifico(resultado.error)}"
            )
        self.resultado.mostrar(
            f"x ≈ {formatear_float(resultado.valor)}",
            detalle,
            texto_referencia(self._coef, cercana=resultado.valor),
            tono=tono,
        )
        self._dibujar(resultado)
        self._animar([{"n": i} for i in range(len(resultado.pasos))])

    def _dibujar(self, resultado):
        """Dibuja la curva y prepara los artistas de cada iteración."""
        puntos = [paso["x"] for paso in resultado.pasos]
        if resultado.valor is not None:
            puntos.append(resultado.valor)
        titulo = f"P(x) = {self._texto_coef.strip()[:42]}"
        self.grafico.dibujar(self._coef, puntos=puntos, titulo=titulo)
        ax = self.grafico.ax
        self._puntos_iteracion = []
        self._lineas_iteracion = []
        self._curvas_halley = []

        for i, paso in enumerate(resultado.pasos):
            punto = ax.plot(
                [paso["x"]],
                [paso["p"]],
                marker="o",
                color="#F4A83A",
                markersize=5,
                linestyle="none",
                label="Iteraciones" if i == 0 else None,
                visible=False,
                zorder=6,
            )[0]
            self._puntos_iteracion.append(punto)

            linea = ax.plot(
                [paso["x"], paso["x_sig"]],
                [paso["p"], 0.0],
                color="#F4A83A",
                lw=0.9,
                ls="--",
                alpha=0.75,
                visible=False,
                zorder=2,
            )[0]
            self._lineas_iteracion.append(linea)

            if "d2p" in paso:
                # Parábola osculadora de Halley; se recorta al tramo del paso.
                xs = [
                    paso["x"] + (paso["x_sig"] - paso["x"]) * t / 24.0
                    for t in range(25)
                ]
                ys = [
                    paso["p"]
                    + paso["dp"] * (x - paso["x"])
                    + 0.5 * paso["d2p"] * (x - paso["x"]) ** 2
                    for x in xs
                ]
                curva = ax.plot(
                    xs,
                    ys,
                    color="#2F9A5B",
                    lw=1.0,
                    ls=":",
                    alpha=0.8,
                    visible=False,
                    zorder=3,
                )[0]
                self._curvas_halley.append(curva)
            else:
                self._curvas_halley.append(None)

        self._raiz_art = None
        if resultado.valor is not None:
            self._raiz_art = ax.plot(
                [resultado.valor],
                [0.0],
                marker="o",
                color="#2F9A5B",
                markerfacecolor="none",
                markeredgewidth=1.8,
                markersize=10,
                linestyle="none",
                label="Raíz aproximada",
                visible=False,
                zorder=7,
            )[0]

        self.grafico.al_clic = self._elegir_x0
        self.grafico.finalizar(ubicacion="best")

    def _aplicar_paso(self, indice):
        for i, punto in enumerate(getattr(self, "_puntos_iteracion", [])):
            visible = i <= indice
            punto.set_visible(visible)
            punto.set_markersize(8 if i == indice else 5)
            linea = self._lineas_iteracion[i]
            linea.set_visible(visible)
            linea.set_alpha(0.95 if i == indice else 0.45)
            curva = self._curvas_halley[i]
            if curva is not None:
                curva.set_visible(visible)
                curva.set_alpha(0.9 if i == indice else 0.35)
        if getattr(self, "_raiz_art", None) is not None:
            self._raiz_art.set_visible(indice >= len(self._puntos_iteracion) - 1)
        super()._aplicar_paso(indice)
        self.grafico.redibujar()

    def _elegir_x0(self, x):
        """Un clic en el gráfico completa x0, pero no calcula solo."""
        self.v_x0.set(formatear_float(x, 7))
        self._estado("ok", "x0 elegido en el gráfico. Presioná Calcular para iterar.")

    def _mostrar_pasos_error(self, pasos):
        self._configurar_columnas(self.v_metodo.get())
        filas = self._filas(pasos)
        self.tabla.cargar(filas, [("odd",) if i % 2 else () for i in range(len(filas))])

    def _mensaje_exito(self, resultado):
        if not resultado.convergio:
            return (
                f"{self._metodo}: no convergió en {resultado.iteraciones} iteraciones. "
                "Revisá el aviso y probá otro x0."
            )
        return (
            f"{self._metodo} convergió en {resultado.iteraciones} iteraciones: "
            f"x ≈ {formatear_float(resultado.valor)}."
        )
