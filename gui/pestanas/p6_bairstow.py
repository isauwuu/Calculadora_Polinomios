"""Pestaña 6: factores cuadráticos de Bairstow y raíces reales/complejas."""

import tkinter as tk

from gui import controlador
from gui.estilo import CARD, MUTED
from gui.formato import formatear_cientifico, formatear_float
from gui.graficos import GraficoBairstow, raices_referencia
from gui.pestanas.base import PestanaBase


def _numero_breve(valor):
    """Redondea para la tarjeta: enteros limpios y hasta seis decimales."""
    numero = round(float(valor), 6)
    if abs(numero - round(numero)) < 1e-5:
        return str(int(round(numero)))
    texto = f"{numero:.6f}".rstrip("0").rstrip(".")
    return "0" if texto in ("", "-0") else texto


def _raiz_breve(valor):
    """Raíz compleja legible, sin ruido numérico en la parte imaginaria."""
    z = complex(valor)
    real = _numero_breve(z.real)
    if abs(z.imag) <= 1e-9:
        return real
    imaginaria = _numero_breve(abs(z.imag))
    if abs(z.real) <= 1e-12:
        return f"{'-' if z.imag < 0 else ''}{imaginaria}i"
    signo = "+" if z.imag >= 0 else "-"
    return f"{real} {signo} {imaginaria}i"


class PestanaBairstow(PestanaBase):
    titulo_tabla = "Factores cuadráticos"
    subtitulo_tabla = "(r, s y raíces del factor)"
    grafico_clase = GraficoBairstow

    def construir_entrada(self, parent):
        self.v_coef = tk.StringVar(value="1, 5, 15, 5, -26")
        self.v_r0 = tk.StringVar(value="1")
        self.v_s0 = tk.StringVar(value="-1")
        self.v_eps = tk.StringVar(value="1e-3")
        self.v_max = tk.StringVar(value="100")

        self.campo(
            parent,
            "Coeficientes (de mayor a menor grado)",
            self.v_coef,
            "Acepta enteros, decimales y fracciones: 3/2",
        )
        self.campo(parent, "Valor inicial  r₀", self.v_r0)
        self.campo(parent, "Valor inicial  s₀", self.v_s0)
        self.campo(parent, "Tolerancia  ε", self.v_eps)
        self.campo(parent, "Máximo de iteraciones", self.v_max)
        tk.Label(
            parent,
            text=(
                "Busca factores x² − r·x − s.\n"
                "Al final resuelve las raíces reales y complejas."
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
                ("factor", "Factor", 52, "center"),
                ("iter", "Iter", 44, "center"),
                ("r", "r", 92, "e"),
                ("s", "s", 92, "e"),
                ("raices", "Raíces del factor", 140, "w"),
            ]
        )

    # ------------------------------------------------------------------ cálculo
    def _calcular(self):
        self._texto_coef = self.v_coef.get()
        self._coef = controlador.coeficientes_float(self._texto_coef)
        return controlador.bairstow(
            self._texto_coef,
            self.v_r0.get(),
            self.v_s0.get(),
            self.v_eps.get(),
            self.v_max.get(),
        )

    # ------------------------------------------------------------------ filas
    def _filas(self, pasos):
        filas = []
        for paso in pasos:
            raices = paso.get("raices_factor", ())
            filas.append(
                {
                    "factor": str(paso.get("factor", "")),
                    "iter": str(paso.get("iter", "")),
                    "r": formatear_float(paso.get("r")),
                    "s": formatear_float(paso.get("s")),
                    "raices": ", ".join(_raiz_breve(z) for z in raices),
                }
            )
        return filas

    def _tags(self, filas, pasos):
        ultimos = {}
        for i, paso in enumerate(pasos):
            ultimos[paso.get("factor")] = i

        etiquetas = []
        for i, paso in enumerate(pasos):
            if paso.get("perturbado"):
                etiquetas.append(("perturbado",))
            elif i == ultimos.get(paso.get("factor")):
                etiquetas.append(("final",))
            elif i % 2:
                etiquetas.append(("odd",))
            else:
                etiquetas.append(())
        return etiquetas

    # ------------------------------------------------------------------ resultado
    def _mostrar_resultado(self, resultado):
        raices = list(resultado.valor or [])
        filas = self._filas(resultado.pasos)
        self.tabla.cargar(filas, self._tags(filas, resultado.pasos))
        self._mostrar_tarjeta()

        if raices:
            principal = "Raíces: " + ", ".join(_raiz_breve(z) for z in raices)
        else:
            principal = "Sin raíces"

        if resultado.iteraciones:
            detalle = f"Bairstow · {resultado.iteraciones} iteraciones"
        else:
            detalle = "Bairstow · resolución directa"
        if resultado.error is not None:
            detalle += f" · error final {formatear_cientifico(resultado.error)}"

        self.resultado.lbl_principal.configure(
            font=self.fuentes.big if len(principal) <= 34 else self.fuentes.h2
        )
        self.resultado.mostrar(
            principal,
            detalle,
            self._referencia(),
            tono="amber" if resultado.avisos else "verde",
        )
        self._dibujar(raices)

    def _referencia(self):
        raices = raices_referencia(self._coef)
        if not raices:
            return "numpy.roots: sin raíces."
        ordenadas = sorted(raices, key=lambda z: (round(z.real, 6), round(z.imag, 6)))
        mostradas = ", ".join(_raiz_breve(z) for z in ordenadas[:6])
        if len(ordenadas) > 6:
            mostradas += ", …"
        return f"Referencia numpy.roots: {mostradas}"

    def _mensaje_exito(self, resultado):
        raices = list(resultado.valor or [])
        if not raices:
            return "Bairstow: el polinomio no tiene raíces."
        reales = sum(1 for z in raices if abs(complex(z).imag) <= 1e-9)
        complejas = len(raices) - reales
        partes = []
        if reales:
            partes.append(f"{reales} {'real' if reales == 1 else 'reales'}")
        if complejas:
            partes.append(f"{complejas} {'compleja' if complejas == 1 else 'complejas'}")
        sustantivo = "raíz" if len(raices) == 1 else "raíces"
        proceso = (
            f"en {resultado.iteraciones} iteraciones"
            if resultado.iteraciones
            else "resolución directa"
        )
        return (
            f"Bairstow: {len(raices)} {sustantivo} "
            f"({', '.join(partes)}), {proceso}."
        )

    # ------------------------------------------------------------------ gráfico
    def _dibujar(self, raices):
        if not raices:
            self.grafico.limpiar("No hay raíces para mostrar.")
            return
        self.grafico.dibujar_raices(self._coef, raices)

    def _mostrar_pasos_error(self, pasos):
        self._configurar_columnas()
        filas = self._filas(pasos)
        self.tabla.cargar(filas, self._tags(filas, pasos))
