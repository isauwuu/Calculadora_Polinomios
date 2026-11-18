"""Pestaña 2: raíces enteras y racionales exactas."""

import tkinter as tk

from gui import controlador
from gui.estilo import CARD, GREEN, MUTED, NAVY
from gui.formato import con_superindices, formatear_fraccion, formatear_polinomio
from gui.pestanas.base import PestanaBase
from gui.widgets import Card


class PestanaEnterasRacionales(PestanaBase):
    titulo_tabla = "Resultado"
    subtitulo_tabla = "(raíces y factorización)"
    usa_animacion = False
    pie_en_grafico = False  # <--- Ahora el resultado va al centro
    tarjeta_polinomio = True

    def construir_entrada(self, parent):
        self.v_coef = tk.StringVar(value="3, -11, -6, 44, -24")
        self.v_modo = tk.StringVar(value="Ambas")
        self._ultimo_resultado = None

        self.campo(
            parent,
            "Coeficientes (de mayor a menor grado)",
            self.v_coef,
            "Acepta enteros, decimales y fracciones: 3/2",
        )
        self.segmentado(
            parent,
            "Buscar raíces",
            self.v_modo,
            ["Enteras", "Racionales", "Ambas"],
            on_change=self._cambiar_modo,
        )
        tk.Label(
            parent,
            text=(
                "Enteras: divisores del término independiente.\n"
                "Racionales: criterio de Gauss p/q.\n"
                "Ambas: busca todos los candidatos posibles."
            ),
            font=self.fuentes.small,
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

            # Panel de raíces (ocupa el espacio central, expandiéndose si es necesario)
            self.panel_raices = tk.Frame(self.card_centro.inner, bg=CARD)
            self.panel_raices.pack(fill="both", expand=True)

            # Panel de factorización (se ubica justo arriba de la tarjeta de resultado)
            self.panel_factorizacion = tk.Frame(self.card_centro.inner, bg=CARD)
            self.panel_factorizacion.pack(side="bottom", fill="x", pady=(10, 0))

    def _cambiar_modo(self):
        """Filtra la vista actual sin necesidad de volver a calcular."""
        if self._ultimo_resultado:
            self._dibujar_panel(self._ultimo_resultado.pasos, self._ultimo_resultado.valor)
            self._dibujar(self._ultimo_resultado.valor, self._ultimo_resultado.pasos)
            self._actualizar_factorizacion(self._ultimo_resultado.valor)

    def _calcular(self):
        self._texto_coef = self.v_coef.get()
        self._modo = self.v_modo.get()
        self._coef = controlador.coeficientes_float(self._texto_coef)
        return controlador.raices(self._texto_coef, self._modo)

    def _mostrar_resultado(self, resultado):
        self._ultimo_resultado = resultado
        self._mostrar_tarjeta()
        self._dibujar_panel(resultado.pasos, resultado.valor)

        raices = list(resultado.valor)
        if raices:
            principal = "Raíces encontradas:" if len(raices) > 1 else "Raíz encontrada:"
            detalle = ", ".join(formatear_fraccion(r) for r in raices)
            sustantivo = "raíces exactas" if len(raices) > 1 else "raíz exacta"
            referencia = f"{len(raices)} {sustantivo}"
            tono = "verde"
        else:
            principal = f"Sin raíces {self._etiqueta_negativa()}"
            cantidad = len(resultado.pasos)
            sustantivo = "candidato probado" if cantidad == 1 else "candidatos probados"
            detalle = f"{cantidad} {sustantivo} con Horner."
            referencia = ""
            tono = "amber" if resultado.avisos else "verde"

        self.resultado.lbl_principal.configure(
            font=self.fuentes.big if len(principal) <= 34 else self.fuentes.h2
        )
        self.resultado.mostrar(principal, detalle, referencia, tono=tono)
        self._dibujar(raices, resultado.pasos)
        self._actualizar_factorizacion(raices)

    def _actualizar_factorizacion(self, raices):
        for w in self.panel_factorizacion.winfo_children():
            w.destroy()

        if raices:
            texto_fact = self._factorizacion(raices)
            tk.Label(
                self.panel_factorizacion, text="Factorización del polinomio",
                font=self.fuentes.small, bg=CARD, fg=MUTED, anchor="w"
            ).pack(anchor="w")
            # Fuente grande y texto con caracteres Unicode matemáticos
            tk.Label(
                self.panel_factorizacion, text=texto_fact,
                font=self.fuentes.h2, bg=CARD, fg=NAVY,
                wraplength=450, justify="left", anchor="w"
            ).pack(anchor="w", pady=(4, 0))
        self.card_centro.actualizar_alto()

    def _dibujar_panel(self, pasos, raices):
        for widget in self.panel_raices.winfo_children():
            widget.destroy()

        # Filtrar según el modo seleccionado
        modo = self.v_modo.get()
        if modo.startswith("Enter"):
            pasos_f = [p for p in pasos if p["candidato"].denominator == 1]
        elif modo.startswith("Rac"):
            pasos_f = [p for p in pasos if p["candidato"].denominator != 1]
        else:
            pasos_f = pasos

        encontradas = [p for p in pasos_f if p["es_raiz"]]
        descartados = [p for p in pasos_f if not p["es_raiz"]]

        enteras = [p for p in encontradas if p["candidato"].denominator == 1]
        racionales = [p for p in encontradas if p["candidato"].denominator != 1]

        a0 = self._coef[0]
        an = self._coef[-1]
        wrap = 450

        card_raices = Card(
            self.panel_raices, r=12, fill="#F4FBF7", outer=CARD,
            shadow=False, pad=12, autoheight=True,
        )
        card_raices.pack(fill="x", pady=(0, 10))

        tk.Label(
            card_raices.inner, text="Raíces exactas encontradas",
            font=self.fuentes.h3, bg="#F4FBF7", fg=GREEN, anchor="w",
        ).pack(anchor="w", pady=(0, 6))

        if not encontradas:
            tk.Label(
                card_raices.inner, text="Ninguna raíz coincide en este modo.",
                font=self.fuentes.normal, bg="#F4FBF7", fg=MUTED, anchor="w",
            ).pack(anchor="w")
        else:
            if enteras:
                self._chips(card_raices.inner, "Enteras", enteras)
            if racionales:
                self._chips(card_raices.inner, "Racionales", racionales)

        frame_desc = tk.Frame(card_raices.inner, bg="#F4FBF7")
        frame_desc.pack(fill="x", pady=(8, 0))

        if descartados:
            valores = set(p["candidato"] for p in descartados)
            agrupados = []

            # Evitar Set changed size during iteration
            for v in list(valores):
                if v not in valores:
                    continue
                if v == 0:
                    agrupados.append((v, "0"))
                elif -v in valores:
                    agrupados.append((abs(v), f"±{formatear_fraccion(abs(v))}"))
                    valores.remove(-v)
                else:
                    agrupados.append((v, formatear_fraccion(v)))

            ent_desc = sorted([(val, txt) for val, txt in agrupados if val.denominator == 1], key=lambda x: x[0])
            rac_desc = sorted([(val, txt) for val, txt in agrupados if val.denominator != 1], key=lambda x: x[0])

            textos_ent = [txt for val, txt in ent_desc]
            textos_rac = [txt for val, txt in rac_desc]

            if textos_ent:
                tk.Label(
                    frame_desc, text=f"Enteros descartados: {', '.join(textos_ent)}",
                    font=self.fuentes.small, bg="#F4FBF7", fg="#D64545",
                    wraplength=wrap, justify="left", anchor="w"
                ).pack(anchor="w", pady=(2, 0))
            if textos_rac:
                tk.Label(
                    frame_desc, text=f"Racionales descartados: {', '.join(textos_rac)}",
                    font=self.fuentes.small, bg="#F4FBF7", fg="#D64545",
                    wraplength=wrap, justify="left", anchor="w"
                ).pack(anchor="w", pady=(2, 0))

        card_raices.actualizar_alto()
        self.card_centro.actualizar_alto()

    def _chips(self, parent, prefijo, encontradas):
        frame = tk.Frame(parent, bg="#F4FBF7")
        frame.pack(fill="x", pady=(3, 0))
        tk.Label(
            frame, text=f"{prefijo}:", font=self.fuentes.normal,
            bg="#F4FBF7", fg=MUTED, anchor="w",
        ).grid(row=0, column=0, columnspan=4, sticky="w")
        for i, paso in enumerate(encontradas):
            tk.Label(
                frame, text=formatear_fraccion(paso["candidato"]),
                font=self.fuentes.bold, bg=GREEN, fg="white", padx=10, pady=2,
            ).grid(row=1 + i // 4, column=i % 4, sticky="w", padx=(0, 6), pady=2)

    def _factorizacion(self, raices):
        try:
            info = controlador.factorizar_raices(self._texto_coef, raices)
        except Exception:
            return con_superindices(formatear_polinomio(self._coef))
        partes = []
        residual = info["residual"]
        if residual.grado == 0:
            coeficiente = residual.coef[0]
            if coeficiente != 1:
                partes.append(formatear_fraccion(coeficiente))
        for r in info["factores"]:
            if r == 0:
                partes.append("x")
            elif r > 0:
                partes.append(f"(x - {formatear_fraccion(r)})")
            else:
                partes.append(f"(x + {formatear_fraccion(-r)})")
        if residual.grado > 0:
            partes.append(f"({formatear_polinomio(residual.coef)})")

        texto = " · ".join(partes) if partes else formatear_polinomio(self._coef)
        return con_superindices(texto)

    def _etiqueta_negativa(self):
        if self._modo.startswith("Enter"):
            return "enteras"
        if self._modo.startswith("Rac"):
            return "racionales"
        return "enteras ni racionales"

    def _dibujar(self, raices, pasos):
        flotantes = [float(r) for r in raices]

        # El polinomio va en la tarjeta de arriba, con superíndices Unicode
        self._mostrar_polinomio(self._coef)

        self.grafico.dibujar(self._coef, puntos=flotantes, titulo="")
        ax = self.grafico.ax

        if raices:
            ax.plot(
                [float(r) for r in raices], [0.0]*len(raices),
                marker="o", color=GREEN, markerfacecolor=GREEN,
                markeredgewidth=1.5, markersize=8,
                linestyle="none", label="Raíces exactas",
                visible=True, zorder=7,
            )
        self.grafico.finalizar(ubicacion="best")

    def _mostrar_pasos_error(self, pasos):
        pass