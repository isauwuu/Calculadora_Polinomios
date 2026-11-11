"""Pestaña 3: cotas superior e inferior de las raíces reales."""

import tkinter as tk

from gui import controlador
from gui.estilo import AMBER_L, CARD, GREEN_L, MUTED
from gui.formato import formatear_fraccion
from gui.graficos import texto_referencia
from gui.pestanas.base import PestanaBase


class PestanaCotas(PestanaBase):
    titulo_tabla = "Cotas por método"
    subtitulo_tabla = "(valores exactos)"

    METODOS = (
        ("lagrange", "Lagrange"),
        ("laguerre", "Laguerre"),
        ("newton", "Newton"),
        ("implicacion", "Implicación"),
    )

    def construir_entrada(self, parent):
        self.v_coef = tk.StringVar(value="3, -11, -6, 44, -24")

        self.campo(
            parent,
            "Coeficientes (de mayor a menor grado)",
            self.v_coef,
            "Acepta enteros, decimales y fracciones: 3/2",
        )
        tk.Label(
            parent,
            text=(
                "Cada método acota las raíces positivas (+) y las negativas (−).\n"
                "La tarjeta muestra la intersección más ajustada."
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
                ("metodo", "Método", 100, "w"),
                ("inf_pos", "Inf. (+)", 80, "e"),
                ("sup_pos", "Sup. (+)", 80, "e"),
                ("inf_neg", "Inf. (−)", 80, "e"),
                ("sup_neg", "Sup. (−)", 80, "e"),
            ]
        )

    # ------------------------------------------------------------------ cálculo
    def _calcular(self):
        self._texto_coef = self.v_coef.get()
        self._coef = controlador.coeficientes_float(self._texto_coef)
        return controlador.cotas(self._texto_coef)

    # ------------------------------------------------------------------ filas
    def _filas(self, valor):
        filas = []
        for clave, nombre in self.METODOS:
            cotas = valor.get(clave, {})
            inf_pos, sup_pos = self._par(cotas, "inf_pos", "sup_pos")
            inf_neg, sup_neg = self._par(cotas, "inf_neg", "sup_neg")
            filas.append(
                {
                    "metodo": nombre,
                    "inf_pos": inf_pos,
                    "sup_pos": sup_pos,
                    "inf_neg": inf_neg,
                    "sup_neg": sup_neg,
                }
            )
        return filas

    def _par(self, cotas, clave_inf, clave_sup):
        """Muestra '—' cuando el método no acota raíces de ese signo."""
        inf = cotas.get(clave_inf, 0)
        sup = cotas.get(clave_sup, 0)
        if inf == 0 and sup == 0:
            return "—", "—"
        return formatear_fraccion(inf), formatear_fraccion(sup)

    def _tags(self, filas):
        return [("odd",) if i % 2 else () for i in range(len(filas))]

    # ------------------------------------------------------------------ resultado
    def _mostrar_resultado(self, resultado):
        valor = resultado.valor
        filas = self._filas(valor)
        self.tabla.cargar(filas, self._tags(filas))
        self._mostrar_tarjeta()

        ajustado = valor["ajustado"]
        tono = "amber" if resultado.avisos else "verde"
        if ajustado["sin_raices"]:
            if ajustado["cero_es_raiz"]:
                principal = "Raíz: 0"
                detalle = "P(0) = 0 · sin raíces positivas ni negativas."
            else:
                principal = "Sin raíces reales"
                detalle = "Ningún método acota raíces positivas ni negativas."
        else:
            principal = f"Cotas: {self._intervalo(ajustado['inf'], ajustado['sup'])}"
            partes = []
            if ajustado["neg"]:
                partes.append("Negativas: " + self._intervalo(*ajustado["neg"]))
            if ajustado["pos"]:
                partes.append("Positivas: " + self._intervalo(*ajustado["pos"]))
            detalle = " · ".join(partes)

        self.resultado.lbl_principal.configure(
            font=self.fuentes.big if len(principal) <= 34 else self.fuentes.h2
        )
        self.resultado.mostrar(
            principal,
            detalle,
            texto_referencia(self._coef),
            tono=tono,
        )
        self._dibujar(ajustado)

    def _intervalo(self, a, b):
        return f"[{formatear_fraccion(a)}, {formatear_fraccion(b)}]"

    def _mensaje_exito(self, resultado):
        ajustado = resultado.valor["ajustado"]
        if ajustado["sin_raices"]:
            if ajustado["cero_es_raiz"]:
                return "Las cotas no acotan raíces positivas ni negativas; la raíz real es 0."
            return "Los métodos no encontraron raíces positivas ni negativas."
        partes = []
        if ajustado["neg"]:
            partes.append("negativas " + self._intervalo(*ajustado["neg"]))
        if ajustado["pos"]:
            partes.append("positivas " + self._intervalo(*ajustado["pos"]))
        return (
            f"Intervalo más ajustado: {self._intervalo(ajustado['inf'], ajustado['sup'])}"
            + (" · " + " · ".join(partes) if partes else "")
            + "."
        )

    # ------------------------------------------------------------------ gráfico
    def _dibujar(self, ajustado):
        puntos = []
        if not ajustado["sin_raices"]:
            for intervalo in (ajustado["neg"], ajustado["pos"]):
                if intervalo:
                    puntos.extend(float(x) for x in intervalo)
        elif ajustado["cero_es_raiz"]:
            puntos.append(0.0)

        titulo = f"P(x) = {self._texto_coef.strip()[:42]}"
        self.grafico.dibujar(self._coef, puntos=puntos, titulo=titulo)
        ax = self.grafico.ax

        if not ajustado["sin_raices"]:
            bandas = (
                (ajustado["neg"], AMBER_L, "Cotas negativas"),
                (ajustado["pos"], GREEN_L, "Cotas positivas"),
            )
            for intervalo, color, etiqueta in bandas:
                if not intervalo:
                    continue
                a, b = (float(x) for x in intervalo)
                ax.axvspan(a, b, color=color, alpha=0.85, label=etiqueta, zorder=1)
                for x in (a, b):
                    ax.axvline(x, color=MUTED, lw=0.8, ls=":", zorder=2)
        elif ajustado["cero_es_raiz"]:
            self.grafico.raiz(0.0, etiqueta="Raíz 0")

        self.grafico.finalizar(ubicacion="best")
