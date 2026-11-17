"""Pestaña 1: evaluar un polinomio y dividirlo."""

import tkinter as tk
from fractions import Fraction

from core.errores import EntradaInvalida
from core.resultado import Resultado
from gui import controlador
from gui.estilo import CARD
from gui.pestanas.base import PestanaBase
from gui.ruffini import TablaEsquema
from gui.esquema import (
    esquema_division, esquema_horner_doble, fmt, poly_texto,
)


def _resumen(items):
    return {"tipo": "resumen", "items": items}


class PestanaEvaluarDividir(PestanaBase):
    titulo_derecha = "Esquema"
    icono_derecha = "chart"
    usa_grafico = False
    usa_tabla = False
    usa_animacion = False

    DIVISORES = ["x + b", "ax + b", "x² + ax + b", "Polinomio general"]
    EJEMPLOS = {
        "x + b": "-2",
        "ax + b": "2, -4",
        "x² + ax + b": "1, 0",
        "Polinomio general": "1, -2",
    }

    def construir_entrada(self, parent):
        self.v_coef = tk.StringVar(value="3, -11, 0, 10, -3")
        self.v_alpha = tk.StringVar(value="2")
        self.v_modo = tk.StringVar(value="Evaluar")
        self.v_metodo = tk.StringVar(value="Horner")
        self.v_divisor = tk.StringVar(value="Polinomio general")
        self.v_params = tk.StringVar(value="1, -2")

        self.campo(parent, "Coeficientes (de mayor a menor grado)", self.v_coef,
                   "Acepta enteros, decimales y fracciones: 3/2")
        self.segmentado(parent, "Operación", self.v_modo, ["Evaluar", "Dividir"])

        self.host_opciones = tk.Frame(parent, bg=CARD)
        self.host_opciones.pack(fill="x")

        self.panel_evaluar = tk.Frame(self.host_opciones, bg=CARD)
        self.campo(self.panel_evaluar, "Punto α", self.v_alpha)
        self.segmentado(self.panel_evaluar, "Método", self.v_metodo,
                        ["Horner", "Horner doble"])

        self.panel_dividir = tk.Frame(self.host_opciones, bg=CARD)
        self.fila_campos(self.panel_dividir, [
            lambda col: self.combo(col, "Divisor", self.v_divisor, self.DIVISORES,
                                   on_change=self._cambiar_divisor),
            lambda col: self.campo(col, "Parámetros", self.v_params),
        ])

        self._cambiar_modo() # Configurar estado inicial
        self.v_modo.trace_add("write", lambda *_: self._cambiar_modo())

    def _crear_derecha(self, host):
        self.esquema = TablaEsquema(host, self.fuentes)
        self.esquema.pack(fill="both", expand=True)

    def _cambiar_modo(self):
        # Ocultar ambos
        self.panel_evaluar.pack_forget()
        self.panel_dividir.pack_forget()

        # Mostrar el correcto
        if self.v_modo.get() == "Evaluar":
            self.panel_evaluar.pack(fill="x")
        else:
            self.panel_dividir.pack(fill="x")

        # Forzar actualización de layout en la tarjeta superior
        self.host_opciones.update_idletasks()
        w = self.host_opciones
        while w:
            if hasattr(w, "actualizar_alto"):
                w.actualizar_alto()
                break
            w = w.master

        # Forzar redibujado del esquema si ya había un cálculo previo
        if hasattr(self, "_salida") and self._salida:
            self.esquema.mostrar(self._salida["esquemas"])

    def _cambiar_divisor(self):
        self.v_params.set(self.EJEMPLOS.get(self.v_divisor.get(), ""))

    def _divisor_coef(self, tipo, params):
        v = controlador.parsear_coeficientes(params)
        if tipo == "x + b":
            if len(v) != 1: raise EntradaInvalida("Para x + b ingresá un solo valor: b.")
            return [Fraction(1), v[0]]
        if tipo == "ax + b":
            if len(v) != 2: raise EntradaInvalida("Para ax + b ingresá: a, b.")
            if v[0] == 0: raise EntradaInvalida("a no puede ser 0.")
            return [v[0], v[1]]
        if tipo.startswith("x²"):
            if len(v) != 2: raise EntradaInvalida("Para x² + ax + b ingresá: a, b.")
            return [Fraction(1), v[0], v[1]]
        if len(v) < 2: raise EntradaInvalida("El divisor general necesita al menos 2 coeficientes.")
        if v[0] == 0: raise EntradaInvalida("El coeficiente principal del divisor no puede ser 0.")
        return list(v)

    def _calcular(self):
        self._modo = self.v_modo.get()
        self._metodo = self.v_metodo.get()
        coef = [Fraction(c) for c in controlador.parsear_coeficientes(self.v_coef.get())]
        if not coef:
            raise EntradaInvalida("Ingresá los coeficientes del polinomio.")
        self._p_texto = poly_texto(coef)

        try:
            if self._modo == "Evaluar":
                datos = self._calcular_evaluar(coef)
            else:
                datos = self._calcular_dividir(coef)
            return Resultado(valor=datos)
        except ValueError as e:
            raise EntradaInvalida(str(e))

    def _calcular_evaluar(self, coef):
        alpha = Fraction(controlador.parsear_racional(self.v_alpha.get(), "el punto α"))
        self._alpha = alpha
        a = fmt(alpha)

        if self._metodo == "Horner":
            esq, q, r = esquema_division(
                coef, [1, -alpha], "Esquema de Horner",
                f"Se divide por x − α con α = {a}: el resto de la división es P({a}).",
                nom_dividendo="P", larga=False)
            resumen = _resumen([
                (f"Resto  P({a}) =", fmt(r[0]), "p"),
                ("Cociente  Q(x) =", esq["q_txt"], "q"),
            ])
            return {
                "esquemas": [esq, resumen],
                "principal_rico": [(f"P({a}) = {fmt(r[0])}", "p"), ("\nQ(x) = ", "q"), (esq["q_txt"], "q")],
                "detalle_rico": "",
                "mensaje": f"Horner: P(α) = {fmt(r[0])}.",
            }

        esquemas, p, dp = esquema_horner_doble(coef, alpha)
        items = [
            (f"Resto  P({a}) =", fmt(p), "p"),
            ("Cociente  Q(x) =", esquemas[0]["q_txt"], "q"),
            (f"Derivada  P′({a}) = Q({a}) =", fmt(dp), "p"),
        ]
        detalle = [
            ("Q(x) = ", "q"), (esquemas[0]["q_txt"], "q"),
            (f"\nP′({a}) = {fmt(dp)}", "p"),
        ]
        if len(esquemas) > 1:
            items.append(("Cociente  S(x) =", esquemas[1]["q_txt"], "q"))
            detalle += [("\nS(x) = ", "q"), (esquemas[1]["q_txt"], "q")]
        return {
            "esquemas": esquemas + [_resumen(items)],
            "principal_rico": [(f"P({a}) = {fmt(p)}", "p"), ("\nQ(x) = ", "q"), (esquemas[0]["q_txt"], "q")],
            "detalle_rico": [(f"P′({a}) = ", "p"), (fmt(dp), "p")],
            "mensaje": f"Horner doble: P(α) = {fmt(p)}, P'(α) = {fmt(dp)}.",
        }

    def _calcular_dividir(self, coef):
        tipo = self.v_divisor.get()
        div = self._divisor_coef(tipo, self.v_params.get())

        esq, cociente, resto = esquema_division(
            coef, div, "División de polinomios", larga=(tipo == "Polinomio general"))

        d_txt = poly_texto(div)
        c_txt = esq["q_txt"]
        r_txt = esq["r_txt"]

        resumen = _resumen([
            ("Cociente  C(x) =", c_txt, "q"),
            ("Resto  R(x) =", r_txt, "p"),
        ])
        grado_c = len(cociente) - 1 if cociente else 0
        return {
            "esquemas": [esq, resumen],
            "principal_rico": [("P(x) = ", "p"), (self._p_texto, "p"), ("\nC(x) = ", "q"), (c_txt, "q")],
            "detalle_rico": [("R(x) = ", "p"), (r_txt, "p")],
            "mensaje": f"División por {d_txt}: cociente de grado {grado_c}, resto {r_txt}.",
        }

    def _mostrar_resultado(self, resultado):
        r = resultado.valor
        self._salida = r
        self._mostrar_tarjeta()
        self.esquema.mostrar(r["esquemas"])
        self.resultado.mostrar(r["principal_rico"], r["detalle_rico"], "")

    def _mensaje_exito(self, resultado):
        return resultado.valor["mensaje"]