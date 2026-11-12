"""Pestaña 2: raíces enteras y racionales exactas."""

import tkinter as tk

from gui import controlador
from gui.estilo import CARD, GREEN, RED
from gui.formato import formatear_fraccion, formatear_polinomio
from gui.graficos import texto_referencia
from gui.pestanas.base import PestanaBase


class PestanaEnterasRacionales(PestanaBase):
    titulo_tabla = "Candidatos"
    subtitulo_tabla = "(verificados con Horner exacto)"

    def construir_entrada(self, parent):
        self.v_coef = tk.StringVar(value="3, -11, -6, 44, -24")
        self.v_modo = tk.StringVar(value="Ambas")

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
                "Ambas: muestra cada candidato una sola vez."
            ),
            font=self.fuentes.small,
            bg=CARD,
            fg="#6A7B86",
            justify="left",
            anchor="w",
            wraplength=230,
        ).pack(fill="x", pady=(10, 0))
        self._configurar_columnas("Ambas")

    def _cambiar_modo(self):
        """Ajusta las columnas y limpia la salida al cambiar de criterio."""
        self._configurar_columnas(self.v_modo.get())
        self._ocultar_tarjeta()
        self._ocultar_banner()
        self._limpiar_grafico("Ingresá los datos y presioná Calcular.")
        self._estado("ok", "Listo. Ingresá los datos y presioná Calcular.")

    # ------------------------------------------------------------------ columnas
    def _configurar_columnas(self, modo):
        if modo.startswith("Enter"):
            self.tabla.configurar(
                [
                    ("candidato", "Candidato", 90, "e"),
                    ("valor", "P(candidato)", 120, "e"),
                    ("es_raiz", "¿Raíz?", 60, "center"),
                ]
            )
        elif modo.startswith("Rac"):
            self.tabla.configurar(
                [
                    ("candidato", "p/q", 84, "e"),
                    ("p", "p", 56, "e"),
                    ("q", "q", 56, "e"),
                    ("valor", "P(p/q)", 110, "e"),
                    ("es_raiz", "¿Raíz?", 60, "center"),
                ]
            )
        else:
            self.tabla.configurar(
                [
                    ("candidato", "Candidato", 78, "e"),
                    ("tipo", "Origen", 120, "w"),
                    ("valor", "P(candidato)", 110, "e"),
                    ("es_raiz", "¿Raíz?", 68, "center"),
                ]
            )

    # ------------------------------------------------------------------ cálculo
    def _calcular(self):
        self._texto_coef = self.v_coef.get()
        self._modo = self.v_modo.get()
        self._coef = controlador.coeficientes_float(self._texto_coef)
        self._configurar_columnas(self._modo)
        return controlador.raices(self._texto_coef, self._modo)

    # ------------------------------------------------------------------ filas
    def _filas(self, pasos):
        filas = []
        for paso in pasos:
            filas.append(
                {
                    "candidato": formatear_fraccion(paso["candidato"]),
                    "p": str(paso.get("p", "")),
                    "q": str(paso.get("q", "")),
                    "tipo": paso.get("tipo", ""),
                    "valor": formatear_fraccion(paso["valor"]),
                    "es_raiz": "Sí" if paso["es_raiz"] else "No",
                }
            )
        return filas

    def _tags(self, filas, pasos):
        etiquetas = []
        for i, paso in enumerate(pasos):
            if paso["es_raiz"]:
                etiquetas.append(("raiz",))
            elif i % 2:
                etiquetas.append(("odd",))
            else:
                etiquetas.append(())
        return etiquetas

    # ------------------------------------------------------------------ resultado
    def _mostrar_resultado(self, resultado):
        filas = self._filas(resultado.pasos)
        self.tabla.cargar(filas, self._tags(filas, resultado.pasos))
        self._mostrar_tarjeta()

        raices = list(resultado.valor)
        if raices:
            principal = ("Raíz: " if len(raices) == 1 else "Raíces: ") + ", ".join(
                formatear_fraccion(r) for r in raices
            )
            detalle = f"Factorización: {self._factorizacion(raices)}"
            tono = "verde"
        else:
            principal = f"Sin raíces {self._etiqueta_negativa()}"
            cantidad = len(resultado.pasos)
            sustantivo = "candidato probado" if cantidad == 1 else "candidatos probados"
            detalle = f"{cantidad} {sustantivo} con Horner."
            tono = "amber" if resultado.avisos else "verde"

        # Si hay muchas raíces, la fuente grande desborda la tarjeta.
        self.resultado.lbl_principal.configure(
            font=self.fuentes.big if len(principal) <= 34 else self.fuentes.h2
        )
        self.resultado.mostrar(
            principal,
            detalle,
            texto_referencia(self._coef),
            tono=tono,
        )
        self._dibujar(raices, resultado.pasos)
        self._animar([{"i": i} for i in range(len(resultado.pasos))])

    def _factorizacion(self, raices):
        try:
            info = controlador.factorizar_raices(self._texto_coef, raices)
        except Exception:
            return formatear_polinomio(self._coef)
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
        return " · ".join(partes) if partes else formatear_polinomio(self._coef)

    def _mensaje_exito(self, resultado):
        if not resultado.valor:
            cantidad = len(resultado.pasos)
            sustantivo = "candidato" if cantidad == 1 else "candidatos"
            return (
                f"No se encontraron raíces {self._etiqueta_negativa()} entre "
                f"{cantidad} {sustantivo}."
            )
        cantidad = len(resultado.valor)
        sustantivo = "raíz" if cantidad == 1 else "raíces"
        verbo = "Se encontró" if cantidad == 1 else "Se encontraron"
        return (
            f"{verbo} {cantidad} {sustantivo} {self._etiqueta_positiva(cantidad)}: "
            + ", ".join(formatear_fraccion(r) for r in resultado.valor)
            + "."
        )

    def _etiqueta_positiva(self, cantidad=None):
        if self._modo.startswith("Enter"):
            return "entera" if cantidad == 1 else "enteras"
        if self._modo.startswith("Rac"):
            return "racional" if cantidad == 1 else "racionales"
        return "entera o racional" if cantidad == 1 else "enteras o racionales"

    def _etiqueta_negativa(self):
        if self._modo.startswith("Enter"):
            return "enteras"
        if self._modo.startswith("Rac"):
            return "racionales"
        return "enteras ni racionales"

    # ------------------------------------------------------------------ gráfico
    def _dibujar(self, raices, pasos):
        """Dibuja la curva y prepara un marcador por candidato probado."""
        flotantes = [float(r) for r in raices]
        titulo = f"P(x) = {self._texto_coef.strip()[:42]}"
        self.grafico.dibujar(self._coef, puntos=flotantes, titulo=titulo)
        ax = self.grafico.ax
        self._marcadores_candidatos = []
        hubo_rojo = False
        hubo_verde = False

        for paso in pasos:
            x = float(paso["candidato"])
            y = float(paso["valor"])
            es_raiz = bool(paso["es_raiz"])
            color = GREEN if es_raiz else RED
            etiqueta = None
            if es_raiz and not hubo_verde:
                etiqueta = "Candidato raíz"
                hubo_verde = True
            elif not es_raiz and not hubo_rojo:
                etiqueta = "Candidato descartado"
                hubo_rojo = True
            linea = ax.plot(
                [x],
                [y],
                marker="o",
                color=color,
                markerfacecolor="none" if es_raiz else color,
                markeredgewidth=1.5,
                markersize=6,
                linestyle="none",
                label=etiqueta,
                visible=False,
                zorder=7,
            )[0]
            self._marcadores_candidatos.append((linea, es_raiz))

        if not pasos:
            ax.text(
                0.5,
                0.92,
                f"Sin raíces {self._etiqueta_negativa()}",
                transform=ax.transAxes,
                ha="center",
                va="top",
                fontsize=8,
                color="#6A7B86",
            )
        self.grafico.finalizar(ubicacion="best")

    def _aplicar_paso(self, indice):
        """Muestra los candidatos probados hasta el paso activo."""
        super()._aplicar_paso(indice)
        for i, (linea, _es_raiz) in enumerate(
            getattr(self, "_marcadores_candidatos", [])
        ):
            visible = i <= indice
            linea.set_visible(visible)
            if i == indice:
                linea.set_markersize(9)
                linea.set_alpha(1.0)
            else:
                linea.set_markersize(5)
                linea.set_alpha(0.55)
        self.grafico.redibujar()

    def _mostrar_pasos_error(self, pasos):
        self._configurar_columnas(self._modo)
        filas = self._filas(pasos)
        self.tabla.cargar(filas, self._tags(filas, pasos))
