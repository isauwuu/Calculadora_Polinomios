"""Pestaña 4: Newton-Raphson-Horner y Halley."""

import re
import tkinter as tk

from gui import controlador
from gui.estilo import CARD, NAVY
from gui.formato import formatear_float, formatear_polinomio
from gui.graficos import texto_referencia
from gui.pestanas.base import PestanaBase
from gui.widgets import Card

_SUPERINDICES = str.maketrans("0123456789", "⁰¹²³⁴⁵⁶⁷⁸⁹")


def con_superindices(texto):
    """Convierte x^2, x^10, etc. en x², x¹⁰ usando Unicode."""
    return re.sub(r"\^(\d+)", lambda m: m.group(1).translate(_SUPERINDICES), texto)


class PestanaNewtonHalley(PestanaBase):
    titulo_tabla = "Iteraciones"
    subtitulo_tabla = ""
    pie_en_grafico = False

    def construir_entrada(self, parent):
        self.tabla.max_filas = 6
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
        self.fila_campos(
            parent,
            [
                lambda col: self.campo(col, "Punto inicial  x₀", self.v_x0),
                lambda col: self.campo(col, "Tolerancia  ε", self.v_eps),
            ],
        )
        self.campo(parent, "Máximo de iteraciones", self.v_max)
        self.segmentado(parent, "Método", self.v_metodo, ["Newton", "Halley"])

        # Aclaraciones para la defensa
        tk.Label(
            parent,
            text=(
                "Newton usa Horner doble (P y P').\n"
                "Halley usa Horner triple (P, P' y P'').\n"
                "Criterio de parada: |xᵢ₊₁ - xᵢ| < ε"
            ),
            font=self.fuentes.small, bg=CARD, fg="#6A7B86",
            justify="left", anchor="w", wraplength=300
        ).pack(fill="x", pady=(12, 0))

        self._configurar_columnas("Newton")

    def _crear_derecha(self, host):
        """Tarjeta con el polinomio arriba del gráfico."""
        self.card_poli = Card(
            host, r=12, fill="#F4FBF7", outer=CARD,
            shadow=False, pad=8, autoheight=True,
        )
        self.card_poli.pack(fill="x", padx=20, pady=(8, 6))

        self.lbl_polinomio = tk.Label(
            self.card_poli.inner, text="", font=self.fuentes.h2,
            bg="#F4FBF7", fg=NAVY, anchor="center", justify="center",
            wraplength=420,
        )
        self.lbl_polinomio.pack(fill="x")
        self.card_poli.actualizar_alto()

        super()._crear_derecha(host)

    def _mostrar_polinomio(self, coef):
        texto = con_superindices(formatear_polinomio(coef))
        self.lbl_polinomio.configure(text=f"P(x) = {texto}")
        self.card_poli.actualizar_alto()

    def _configurar_columnas(self, metodo):
        # Usamos caracteres Unicode para los subíndices y evitar los {}
        columnas = [
            ("n", "n", 40, "center"),
            ("xn", "xₙ", 100, "center"),
            ("p", "P(xₙ)", 100, "center"),
            ("dp", "P'(xₙ)", 100, "center"),
        ]
        if str(metodo).lower().startswith("halley"):
            columnas.append(("d2p", "P''(xₙ)", 100, "center"))

        # Columna final con la notación matemática exacta
        columnas.append(("dx", "|xᵢ₊₁ - xᵢ|", 140, "center"))

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
                f"error final {formatear_float(resultado.error, 8)}"
            )
        else:
            detalle = (
                f"No convergió en {resultado.iteraciones} iteraciones · "
                f"|xᵢ₊₁ - xᵢ| final {formatear_float(resultado.error, 8)}"
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
        self._mostrar_polinomio(self._coef)

        puntos = [paso["x"] for paso in resultado.pasos]
        if resultado.valor is not None:
            puntos.append(resultado.valor)

        self.grafico.dibujar(self._coef, puntos=puntos, titulo="")
        ax = self.grafico.ax
        self._puntos_iteracion = []
        self._lineas_iteracion = []
        self._curvas_halley = []

        # CREAMOS LOS ARTISTAS VISIBLES (para que la leyenda los detecte)
        for i, paso in enumerate(resultado.pasos):
            punto = ax.plot(
                [paso["x"]],
                [paso["p"]],
                marker="o",
                color="#F4A83A",
                markersize=5,
                linestyle="none",
                label="Puntos de iteración" if i == 0 else None,
                visible=True,
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
                visible=True,
                label="Tangente" if i == 0 else None,
                zorder=2,
            )[0]
            self._lineas_iteracion.append(linea)

            if "d2p" in paso:
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
                    visible=True,
                    label="Parábola osculadora" if i == 0 else None,
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
                markerfacecolor="#2F9A5B",
                markeredgewidth=1.8,
                markersize=10,
                linestyle="none",
                label="Raíz aproximada",
                visible=True,
                zorder=7,
            )[0]

        self.grafico.al_clic = self._elegir_x0

        # 1. Generamos la leyenda con los artistas visibles
        self.grafico.finalizar(ubicacion="best")

        # 2. Ocultamos todo inmediatamente para que la animación empiece desde cero
        self._aplicar_paso(-1)

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