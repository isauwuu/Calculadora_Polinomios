"""Pestaña 1: evaluar un polinomio y dividirlo por un factor."""

import tkinter as tk
from fractions import Fraction

from core.errores import EntradaInvalida
from core.polinomio import Polinomio
from gui import controlador
from gui.estilo import CARD, GREEN, ORANGE
from gui.formato import (
    formatear_fraccion,
    formatear_polinomio,
    formatear_float,
)
from gui.graficos import evaluar_curva, raices_referencia, texto_referencia
from gui.pestanas.base import PestanaBase


class PestanaEvaluarDividir(PestanaBase):
    titulo_tabla = "Esquema de Horner"
    subtitulo_tabla = "(pasos del Resultado)"

    DIVISORES = [
        "x + b",
        "ax + b",
        "x² + ax + b",
        "ax² + bx + c",
        "Polinomio general",
    ]

    def construir_entrada(self, parent):
        self.v_coef = tk.StringVar(value="1, 0, -5, -3")
        self.v_alpha = tk.StringVar(value="2")
        self.v_modo = tk.StringVar(value="Evaluar")
        self.v_metodo = tk.StringVar(value="Horner")
        self.v_divisor = tk.StringVar(value="x + b")
        self.v_params = tk.StringVar(value="-2")

        self.campo(
            parent,
            "Coeficientes (de mayor a menor grado)",
            self.v_coef,
            "Acepta enteros, decimales y fracciones: 3/2",
        )
        self.campo(
            parent,
            "Punto α",
            self.v_alpha,
            "Se usa al evaluar. Si dividís, se marca igual en el gráfico.",
        )
        self.segmentado(
            parent,
            "Operación",
            self.v_modo,
            ["Evaluar", "Dividir"],
        )

        self.panel_evaluar = tk.Frame(parent, bg=CARD)
        self.segmentado(
            self.panel_evaluar,
            "Método de evaluación",
            self.v_metodo,
            ["Directa", "Horner", "Horner doble"],
        )
        self.panel_evaluar.pack(fill="x")

        self.panel_dividir = tk.Frame(parent, bg=CARD)
        self.combo(
            self.panel_dividir,
            "Divisor",
            self.v_divisor,
            self.DIVISORES,
            on_change=self._cambiar_divisor,
        )
        self.campo(
            self.panel_dividir,
            "Parámetros del divisor",
            self.v_params,
            "x + b: b  ·  ax + b: a, b  ·  x² + ax + b: a, b  ·  ax² + bx + c: a, b, c",
        )

        self._configurar_columnas("Evaluar", "Horner", "x + b")
        # El cambio de operación muestra el panel correspondiente, venga de un
        # clic en el selector o de una asignación desde el código.
        self.v_modo.trace_add("write", lambda *_: self._cambiar_modo())

    # ------------------------------------------------------------------ modo
    def _cambiar_modo(self):
        if self.v_modo.get() == "Evaluar":
            self.panel_dividir.pack_forget()
            self.panel_evaluar.pack(fill="x")
        else:
            self.panel_evaluar.pack_forget()
            self.panel_dividir.pack(fill="x")

    def _cambiar_divisor(self):
        """Ajusta parámetros de ejemplo al cambiar el tipo de divisor."""
        tipo = self.v_divisor.get()
        ejemplos = {
            "x + b": "-2",
            "ax + b": "2, -4",
            "x² + ax + b": "1, 0",
            "ax² + bx + c": "1, 0, -4",
            "Polinomio general": "1, -2",
        }
        self.v_params.set(ejemplos.get(tipo, ""))

    # ------------------------------------------------------------------ columnas
    def _configurar_columnas(self, modo, metodo=None, divisor=None):
        if modo == "Evaluar":
            if str(metodo).startswith("Directa"):
                self.tabla.configurar(
                    [
                        ("i", "i", 34, "center"),
                        ("coef", "Coeficiente", 86, "e"),
                        ("potencia", "α^i", 74, "e"),
                        ("termino", "Coef · α^i", 100, "e"),
                        ("acumulado", "Acumulado", 100, "e"),
                    ]
                )
            elif "doble" in str(metodo).lower():
                self.tabla.configurar(
                    [
                        ("i", "Grado i", 52, "center"),
                        ("a", "a_i", 78, "e"),
                        ("b", "b_i", 78, "e"),
                        ("c", "c_i", 78, "e"),
                    ]
                )
            else:
                self.tabla.configurar(
                    [
                        ("i", "Grado i", 52, "center"),
                        ("a", "a_i", 92, "e"),
                        ("b", "b_i", 92, "e"),
                    ]
                )
            return

        if "general" in str(divisor).lower():
            self.tabla.configurar(
                [
                    ("k", "k", 38, "center"),
                    ("factor", "Factor", 92, "e"),
                    ("resto", "Resto parcial", 230, "w"),
                ]
            )
        else:
            self.tabla.configurar(
                [
                    ("i", "Grado i", 52, "center"),
                    ("coef", "Coeficiente", 100, "e"),
                    ("esquema", "Esquema", 100, "e"),
                ]
            )

    # ------------------------------------------------------------------ cálculo
    def _calcular(self):
        self._modo = self.v_modo.get()
        self._metodo = self.v_metodo.get()
        self._tipo_divisor = self.v_divisor.get()
        self._params = self.v_params.get()
        self._texto_coef = self.v_coef.get()
        self._coef = controlador.coeficientes_float(self._texto_coef)
        self._configurar_columnas(self._modo, self._metodo, self._tipo_divisor)

        if self._modo == "Evaluar":
            self._alpha = controlador.parsear_racional(self.v_alpha.get(), "el punto α")
            return controlador.evaluar(self._texto_coef, self.v_alpha.get(), self._metodo)

        self._alpha = self._alpha_para_grafico()
        resultado = controlador.dividir(self._texto_coef, self._tipo_divisor, self._params)
        self._divisor_coef = self._coeficientes_divisor()
        self._divisor_texto = formatear_polinomio(self._divisor_coef)
        return resultado

    def _alpha_para_grafico(self):
        """α es opcional al dividir: si no es válido, el gráfico sigue sin él."""
        try:
            return controlador.parsear_racional(self.v_alpha.get(), "el punto α")
        except EntradaInvalida:
            return None

    def _coeficientes_divisor(self):
        """Coeficientes de menor a mayor grado del divisor elegido."""
        tipo = self._tipo_divisor
        if "general" in tipo.lower():
            return controlador.leer_polinomio(self._params).coef

        valores = controlador.parsear_coeficientes(self._params)
        if tipo == "x + b":
            return [valores[0], Fraction(1)]
        if tipo == "ax + b":
            return [valores[1], valores[0]]
        if tipo.startswith("x²"):
            return [valores[1], valores[0], Fraction(1)]
        if tipo.startswith("ax²"):
            return [valores[2], valores[1], valores[0]]
        return []

    # ------------------------------------------------------------------ filas
    def _filas(self, pasos):
        if self._modo == "Evaluar":
            return self._filas_evaluacion(pasos)
        return self._filas_division(pasos)

    def _filas_evaluacion(self, pasos):
        if self._metodo.startswith("Directa"):
            return [
                {
                    "i": str(paso["i"]),
                    "coef": formatear_fraccion(paso["coef"]),
                    "potencia": formatear_fraccion(paso["potencia"]),
                    "termino": formatear_fraccion(paso["termino"]),
                    "acumulado": formatear_fraccion(paso["acumulado"]),
                }
                for paso in pasos
            ]

        filas = []
        for paso in pasos:
            a = paso["a"]
            b = paso["b"]
            c = paso.get("c", [])
            for i in range(len(a) - 1, -1, -1):
                filas.append(
                    {
                        "i": str(i),
                        "a": formatear_fraccion(a[i]),
                        "b": formatear_fraccion(b[i]) if i < len(b) else "—",
                        "c": formatear_fraccion(c[i]) if i < len(c) else "—",
                    }
                )
        return filas

    def _filas_division(self, pasos):
        if "general" in self._tipo_divisor.lower():
            return [
                {
                    "k": str(paso["k"]),
                    "factor": formatear_fraccion(paso["factor"]),
                    "resto": formatear_polinomio(paso["resto"]),
                }
                for paso in pasos
            ]

        filas = []
        for paso in pasos:
            if "c" in paso:
                coef = paso["coef"]
                esquema = paso["c"]
            else:
                coef = paso["a"]
                esquema = paso["b"]
            for i in range(len(coef) - 1, -1, -1):
                filas.append(
                    {
                        "i": str(i),
                        "coef": formatear_fraccion(coef[i]),
                        "esquema": formatear_fraccion(esquema[i]) if i < len(esquema) else "—",
                    }
                )
        return filas

    def _tags(self, filas):
        etiquetas = []
        for i, fila in enumerate(filas):
            grado = int(fila.get("i", fila.get("k", -1)))
            if self._modo == "Dividir" and (
                ("general" in self._tipo_divisor.lower() and i == len(filas) - 1)
                or ("general" not in self._tipo_divisor.lower() and grado <= 0)
            ):
                etiquetas.append(("resto",))
            elif i % 2:
                etiquetas.append(("odd",))
            else:
                etiquetas.append(())
        return etiquetas

    # ------------------------------------------------------------------ resultado
    def _mostrar_resultado(self, resultado):
        filas = self._filas(resultado.pasos)
        self.tabla.cargar(filas, self._tags(filas))
        self._mostrar_tarjeta()
        if self._modo == "Evaluar":
            self._mostrar_evaluacion(resultado)
        else:
            self._mostrar_division(resultado)

    def _mostrar_evaluacion(self, resultado):
        if "doble" in self._metodo.lower():
            p_alpha, dp_alpha = resultado.valor
            principal = f"P(α) = {formatear_fraccion(p_alpha)}"
            detalle = f"P'(α) = {formatear_fraccion(dp_alpha)} · Horner doble"
            self._alpha_float = float(self._alpha)
            self._p_alpha_float = float(p_alpha)
            self._dp_alpha_float = float(dp_alpha)
        else:
            principal = f"P(α) = {formatear_fraccion(resultado.valor)}"
            if self._metodo.startswith("Directa"):
                detalle = f"Evaluación directa · {len(resultado.pasos)} términos"
            else:
                detalle = f"Horner · esquema de {len(self._coef)} coeficientes"
            self._alpha_float = float(self._alpha)
            self._p_alpha_float = float(resultado.valor)
            self._dp_alpha_float = None

        self.resultado.mostrar(
            principal,
            detalle,
            self._referencia_polyval(),
            tono="verde",
        )
        self._dibujar_evaluacion()

    def _referencia_polyval(self):
        try:
            valor = evaluar_curva(self._coef, [float(self._alpha)])[0]
            return f"Referencia numpy.polyval: {formatear_float(valor)}"
        except (TypeError, ValueError, OverflowError):
            return "Evaluación exacta con Fraction."

    def _mostrar_division(self, resultado):
        cociente, resto = resultado.valor
        texto_resto = (
            formatear_polinomio(resto.coef)
            if isinstance(resto, Polinomio)
            else formatear_fraccion(resto)
        )
        principal = f"C(x) = {cociente}"
        detalle = f"Resto R = {texto_resto} · divisor {self._divisor_texto}"
        self.resultado.mostrar(
            principal,
            detalle,
            "División exacta (Fraction) · P = divisor · C + R",
            tono="verde",
        )
        self._dibujar_division()

    def _mensaje_exito(self, resultado):
        if self._modo == "Evaluar":
            if "doble" in self._metodo.lower():
                return (
                    f"{self._metodo}: P(α) = {formatear_fraccion(resultado.valor[0])}, "
                    f"P'(α) = {formatear_fraccion(resultado.valor[1])}."
                )
            return f"{self._metodo}: P(α) = {formatear_fraccion(resultado.valor)}."
        cociente, resto = resultado.valor
        texto_resto = (
            formatear_polinomio(resto.coef)
            if isinstance(resto, Polinomio)
            else formatear_fraccion(resto)
        )
        return (
            f"División por {self._divisor_texto}: cociente de grado "
            f"{cociente.grado}, resto {texto_resto}."
        )

    # ------------------------------------------------------------------ gráfico
    def _dibujar_evaluacion(self):
        puntos = [self._alpha_float]
        titulo = f"P(x) = {self._texto_coef.strip()[:42]}"
        self.grafico.dibujar(self._coef, puntos=puntos, titulo=titulo)
        ax = self.grafico.ax
        ax.axvline(self._alpha_float, color="#9DB0A8", lw=0.9, ls=":", zorder=1)
        self.grafico.punto(
            self._alpha_float,
            self._p_alpha_float,
            etiqueta="(α, P(α))",
            color=ORANGE,
            ms=7,
        )
        if self._dp_alpha_float is not None:
            x0, x1 = ax.get_xlim()
            xs = [x0, x1]
            ys = [
                self._p_alpha_float + self._dp_alpha_float * (x - self._alpha_float)
                for x in xs
            ]
            ax.plot(xs, ys, color=GREEN, lw=1.4, ls="--", label="Tangente en α", zorder=4)
        self.grafico.finalizar(ubicacion="best")

    def _dibujar_division(self):
        puntos = []
        if self._alpha is not None:
            puntos.append(float(self._alpha))
        reales = []
        try:
            raices = raices_referencia(self._divisor_coef)
            reales = [
                z.real
                for z in raices
                if abs(z.imag) < 1e-9 and abs(z.real) < 1e6
            ]
        except (TypeError, ValueError, ZeroDivisionError):
            reales = []
        puntos.extend(reales)

        titulo = f"P(x) = {self._texto_coef.strip()[:38]}  ÷  {self._divisor_texto}"
        self.grafico.dibujar(self._coef, puntos=puntos, titulo=titulo)
        ax = self.grafico.ax
        if self._alpha is not None:
            ax.axvline(float(self._alpha), color="#9DB0A8", lw=0.9, ls=":", zorder=1)
            self.grafico.punto(
                float(self._alpha),
                float(evaluar_curva(self._coef, [float(self._alpha)])[0]),
                etiqueta="α",
                color=ORANGE,
                ms=6,
            )
        if reales:
            ax.plot(
                reales,
                [0.0] * len(reales),
                marker="x",
                color=GREEN,
                markersize=8,
                markeredgewidth=1.8,
                linestyle="none",
                label="Raíz del divisor",
                zorder=7,
            )
        self.grafico.finalizar(ubicacion="best")

    def _mostrar_pasos_error(self, pasos):
        self._configurar_columnas(self._modo, self._metodo, self._tipo_divisor)
        filas = self._filas(pasos)
        self.tabla.cargar(filas, self._tags(filas))
