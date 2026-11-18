"""Pestaña 3: cotas superior e inferior de las raíces reales."""

import tkinter as tk

from gui import controlador
from gui.estilo import AMBER_L, CARD, GREEN_L, MUTED, NAVY, GREEN
from gui.formato import formatear_fraccion
from gui.pestanas.base import PestanaBase
from gui.widgets import Card


class PestanaCotas(PestanaBase):
    titulo_tabla = "Cotas por método"
    subtitulo_tabla = "(valores exactos)"
    usa_animacion = False
    pie_en_grafico = False
    tarjeta_polinomio = True

    METODOS = (
        ("lagrange", "Lagrange"),
        ("laguerre", "Laguerre"),
        ("newton", "Newton"),
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
            font=self.fuentes.normal,
            bg=CARD,
            fg=MUTED,
            justify="left",
            anchor="w",
            wraplength=230,
        ).pack(fill="x", pady=(10, 0))

    def _construir_esquema(self):
        super()._construir_esquema()
        if self.usa_tabla:
            self.tabla.pack_forget()
            self.panel_tarjetas = tk.Frame(self.card_centro.inner, bg=CARD)
            self.panel_tarjetas.pack(side="top", fill="both", expand=True)
            self.panel_tarjetas.columnconfigure(0, weight=1)

    def _calcular(self):
        self._texto_coef = self.v_coef.get()
        self._coef = controlador.coeficientes_float(self._texto_coef)
        return controlador.cotas(self._texto_coef)

    def _mostrar_resultado(self, resultado):
        valor = resultado.valor
        self._mostrar_tarjeta()
        self._dibujar_tarjetas(valor)

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
            "",
            tono=tono,
        )
        self._dibujar(ajustado, valor)

    def _dibujar_tarjetas(self, valor):
        for widget in self.panel_tarjetas.winfo_children():
            widget.destroy()

        for i, (clave, nombre) in enumerate(self.METODOS):
            cotas = valor.get(clave, {})
            rango_pos = self._rango(cotas.get("inf_pos", 0), cotas.get("sup_pos", 0))
            rango_neg = self._rango(cotas.get("inf_neg", 0), cotas.get("sup_neg", 0))

            card = Card(
                self.panel_tarjetas, r=12, fill="#F8FAF9", outer=CARD,
                shadow=False, pad=12, autoheight=True,
            )
            card.grid(row=i, column=0, sticky="ew", pady=5)

            inner = card.inner

            tk.Label(
                inner, text=nombre, font=self.fuentes.h2,
                bg="#F8FAF9", fg=NAVY, anchor="w",
            ).pack(anchor="w", pady=(0, 6))

            grid = tk.Frame(inner, bg="#F8FAF9")
            grid.pack(fill="x")
            grid.columnconfigure(0, weight=1)
            grid.columnconfigure(1, weight=1)

            # Negativas en la columna 0 (Izquierda)
            tk.Label(
                grid, text="Negativas", font=self.fuentes.normal,
                bg="#F8FAF9", fg="#D64545", anchor="w",
            ).grid(row=0, column=0, sticky="w")
            tk.Label(
                grid, text=rango_neg, font=self.fuentes.bold,
                bg="#F8FAF9", fg="#17303F", anchor="w",
            ).grid(row=1, column=0, sticky="w", pady=(2, 0))

            # Positivas en la columna 1 (Derecha)
            tk.Label(
                grid, text="Positivas", font=self.fuentes.normal,
                bg="#F8FAF9", fg=GREEN, anchor="w",
            ).grid(row=0, column=1, sticky="w")
            tk.Label(
                grid, text=rango_pos, font=self.fuentes.bold,
                bg="#F8FAF9", fg="#17303F", anchor="w",
            ).grid(row=1, column=1, sticky="w", pady=(2, 0))

            card.actualizar_alto()

        self.card_centro.actualizar_alto()

    def _rango(self, inf, sup):
        if inf == 0 and sup == 0:
            return "—"
        return f"[{formatear_fraccion(inf)}, {formatear_fraccion(sup)}]"

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

    def _dibujar(self, ajustado, valor):
        self._mostrar_polinomio(self._coef)

        puntos = []
        if not ajustado["sin_raices"]:
            for intervalo in (ajustado["neg"], ajustado["pos"]):
                if intervalo:
                    puntos.extend(float(x) for x in intervalo)
        elif ajustado["cero_es_raiz"]:
            puntos.append(0.0)

        self.grafico.dibujar(self._coef, puntos=puntos, titulo="")
        ax = self.grafico.ax

        if not ajustado["sin_raices"]:
            for intervalo, color in ((ajustado["neg"], AMBER_L), (ajustado["pos"], GREEN_L)):
                if not intervalo: continue
                a, b = (float(x) for x in intervalo)
                ax.axvspan(a, b, color=color, alpha=0.9, visible=True, zorder=1)
                for x in (a, b):
                    ax.axvline(x, color=NAVY, lw=0.9, ls=":", visible=True, zorder=3)
        elif ajustado["cero_es_raiz"]:
            self.grafico.raiz(0.0, etiqueta="Raíz 0")

        ax.plot([], [], color=GREEN_L, lw=8, label="Intervalo acotado (+)")
        ax.plot([], [], color=AMBER_L, lw=8, label="Intervalo acotado (−)")
        self.grafico.finalizar(ubicacion="best")
        self.grafico.redibujar()