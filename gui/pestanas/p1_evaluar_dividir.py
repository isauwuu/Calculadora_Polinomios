"""Pestaña 1: evaluar un polinomio y dividirlo por un factor."""

import tkinter as tk
from tkinter import ttk
from fractions import Fraction

from core.errores import EntradaInvalida
from core.polinomio import Polinomio
from gui import controlador
from gui.estilo import CARD
from gui.formato import formatear_fraccion, formatear_polinomio, formatear_float
from gui.graficos import GraficoSimple
from gui.pestanas.base import PestanaBase
from gui.ruffini import TablaEsquema


class PestanaEvaluarDividir(PestanaBase):
    titulo_derecha = "Visualización"
    icono_derecha = "chart"
    usa_grafico = True
    usa_tabla = False
    usa_animacion = False

    DIVISORES = [
        "x + b",
        "ax + b",
        "x² + ax + b",
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
        )
        self.segmentado(
            parent, "Operación", self.v_modo, ["Evaluar", "Dividir"]
        )

        # Un contenedor fijo evita que los paneles dinámicos queden debajo de
        # los botones al cambiar de operación.
        self.host_opciones = tk.Frame(parent, bg=CARD)
        self.host_opciones.pack(fill="x")

        self.panel_evaluar = tk.Frame(self.host_opciones, bg=CARD)
        self.segmentado(
            self.panel_evaluar, "Método de evaluación", self.v_metodo,
            ["Directa", "Horner", "Horner doble"],
        )
        self.panel_evaluar.pack(fill="x")

        self.panel_dividir = tk.Frame(self.host_opciones, bg=CARD)
        self.fila_campos(
            self.panel_dividir,
            [
                lambda col: self.combo(
                    col,
                    "Divisor",
                    self.v_divisor,
                    self.DIVISORES,
                    on_change=self._cambiar_divisor,
                ),
                lambda col: self.campo(col, "Parámetros", self.v_params),
            ],
        )

        self.v_modo.trace_add("write", lambda *_: self._cambiar_modo())

    def _crear_derecha(self, host):
        """Crea un Notebook con dos pestañas: Gráfico y Esquema."""
        self.notebook_interno = ttk.Notebook(host, style="Calc.TNotebook")
        self.notebook_interno.pack(fill="both", expand=True)

        # Pestaña 1: Gráfico
        self.frame_grafico = tk.Frame(self.notebook_interno, bg=CARD)
        self.grafico = GraficoSimple(self.frame_grafico, self)
        self.grafico.pack(fill="both", expand=True)
        self.notebook_interno.add(self.frame_grafico, text="  Gráfico  ")

        # Pestaña 2: Esquema
        self.frame_ruffini = tk.Frame(self.notebook_interno, bg=CARD)
        self.ruffini = TablaEsquema(self.frame_ruffini, self.fuentes)
        self.ruffini.pack(fill="both", expand=True)
        self.notebook_interno.add(self.frame_ruffini, text="  Esquema de Horner  ")

    def _cambiar_modo(self):
        if self.v_modo.get() == "Evaluar":
            self.panel_dividir.pack_forget()
            self.panel_evaluar.pack(fill="x")
            self.notebook_interno.select(0) # Muestra el gráfico
        else:
            self.panel_evaluar.pack_forget()
            self.panel_dividir.pack(fill="x")
            self.notebook_interno.select(1) # Muestra el esquema de Ruffini

    def _cambiar_divisor(self):
        tipo = self.v_divisor.get()
        ejemplos = {
            "x + b": "-2",
            "ax + b": "2, -4",
            "x² + ax + b": "1, 0",
            "Polinomio general": "1, -2",
        }
        self.v_params.set(ejemplos.get(tipo, ""))

    def _calcular(self):
        self._modo = self.v_modo.get()
        self._metodo = self.v_metodo.get()
        self._tipo_divisor = self.v_divisor.get()
        self._params = self.v_params.get()
        self._texto_coef = self.v_coef.get()
        self._coef = controlador.coeficientes_float(self._texto_coef)

        if self._modo == "Evaluar":
            self._alpha = controlador.parsear_racional(self.v_alpha.get(), "el punto α")
            return controlador.evaluar(self._texto_coef, self.v_alpha.get(), self._metodo)

        self._alpha = self._alpha_para_grafico()
        resultado = controlador.dividir(self._texto_coef, self._tipo_divisor, self._params)
        self._divisor_coef = self._coeficientes_divisor()
        self._divisor_texto = formatear_polinomio(self._divisor_coef)
        return resultado

    def _alpha_para_grafico(self):
        try:
            return controlador.parsear_racional(self.v_alpha.get(), "el punto α")
        except EntradaInvalida:
            return None

    def _coeficientes_divisor(self):
        tipo = self._tipo_divisor
        if "general" in tipo.lower():
            return controlador.leer_polinomio(self._params).coef

        valores = controlador.parsear_coeficientes(self._params)
        if tipo == "x + b": return [valores[0], Fraction(1)]
        if tipo == "ax + b": return [valores[1], valores[0]]
        if tipo.startswith("x²"): return [valores[1], valores[0], Fraction(1)]
        return []

    def _mostrar_resultado(self, resultado):
        self._mostrar_tarjeta()
        self._mostrar_esquema()
        self._dibujar_grafico()
        if self._modo == "Evaluar":
            self._mostrar_evaluacion(resultado)
        else:
            self._mostrar_division(resultado)

    def _mostrar_esquema(self):
        try:
            if self._modo == "Evaluar":
                esquema = controlador.esquema_evaluacion(
                    self._texto_coef, self.v_alpha.get(), self._metodo
                )
            else:
                esquema = controlador.esquema_division(
                    self._texto_coef, self._tipo_divisor, self._params
                )
        except EntradaInvalida:
            self.ruffini.limpiar("No se pudo dibujar el esquema.")
            return
        self.ruffini.mostrar(esquema)

    def _dibujar_grafico(self):
        """Dibuja la curva P(x) y marca el punto α si es válido."""
        puntos = []
        if self._alpha is not None:
            puntos.append(float(self._alpha))

        titulo = f"P(x) = {self._texto_coef.strip()[:30]}"
        self.grafico.dibujar(self._coef, puntos=puntos, titulo=titulo)

        if self._alpha is not None:
            try:
                from metodos.evaluacion import horner_float
                py = horner_float(Polinomio(self._coef), float(self._alpha)).valor
                self.grafico.punto(float(self._alpha), py, etiqueta="α", color="#F4A83A", ms=8)
            except Exception:
                pass

        self.grafico.finalizar(ubicacion="best")

    def _mostrar_evaluacion(self, resultado):
        if "doble" in self._metodo.lower():
            p_alpha, dp_alpha = resultado.valor
            principal = f"P(α) = {formatear_fraccion(p_alpha)}"
            detalle = f"P'(α) = {formatear_fraccion(dp_alpha)} · Horner doble"
        else:
            principal = f"P(α) = {formatear_fraccion(resultado.valor)}"
            if self._metodo.startswith("Directa"):
                detalle = f"Evaluación directa · {len(resultado.pasos)} términos"
            else:
                detalle = f"Horner · esquema de {len(self._coef)} coeficientes"

        self.resultado.mostrar(
            principal, detalle, "Cálculo exacto con Fraction", tono="verde"
        )

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
            principal, detalle, "División exacta · P = divisor · C + R", tono="verde"
        )

    def _mensaje_exito(self, resultado):
        if self._modo == "Evaluar":
            if "doble" in self._metodo.lower():
                return f"{self._metodo}: P(α) = {formatear_fraccion(resultado.valor[0])}, P'(α) = {formatear_fraccion(resultado.valor[1])}."
            return f"{self._metodo}: P(α) = {formatear_fraccion(resultado.valor)}."
        cociente, resto = resultado.valor
        texto_resto = formatear_polinomio(resto.coef) if isinstance(resto, Polinomio) else formatear_fraccion(resto)
        return f"División por {self._divisor_texto}: cociente de grado {cociente.grado}, resto {texto_resto}."