"""Pestaña 6: factores cuadráticos de Bairstow y raíces reales/complejas."""

import tkinter as tk

from gui import controlador
from gui.estilo import CARD, MUTED, NAVY
from gui.formato import formatear_cientifico, formatear_float
from gui.graficos import GraficoBairstow
from gui.pestanas.base import PestanaBase


def _numero_breve(valor):
    numero = round(float(valor), 6)
    if abs(numero - round(numero)) < 1e-5:
        return str(int(round(numero)))
    texto = f"{numero:.6f}".rstrip("0").rstrip(".")
    return "0" if texto in ("", "-0") else texto


def _raiz_breve(valor):
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
    pie_en_grafico = False
    tarjeta_polinomio = True

    def construir_entrada(self, parent):
        self.tabla.max_filas = 12
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
        self.fila_campos(
            parent,
            [
                lambda col: self.campo(col, "Valor inicial  r₀", self.v_r0),
                lambda col: self.campo(col, "Valor inicial  s₀", self.v_s0),
            ],
        )
        self.fila_campos(
            parent,
            [
                lambda col: self.campo(col, "Tolerancia  ε", self.v_eps),
                lambda col: self.campo(col, "Máximo de iteraciones", self.v_max),
            ],
        )
        tk.Label(
            parent,
            text="Factor x² − r·x − s · raíces reales y complejas",
            font=self.fuentes.small,
            bg=CARD,
            fg=MUTED,
            justify="left",
            anchor="w",
            wraplength=300,
        ).pack(fill="x", pady=(10, 0))
        self._configurar_columnas()

    def _configurar_columnas(self):
        self.tabla.configurar(
            [
                ("factor", "Factor", 64, "center"),
                ("iter", "Iteración i", 70, "center"),
                ("r", "rᵢ", 88, "center"),
                ("s", "sᵢ", 88, "center"),
                ("raices", "Raíces", 136, "w"),
            ],
            estirar=True,
        )

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

    def _filas(self, pasos, raices=()):
        filas = []
        for paso in pasos:
            raices_factor = paso.get("raices_factor", ())
            filas.append(
                {
                    "factor": str(paso.get("factor", "")),
                    "iter": str(paso.get("iter", "")),
                    "r": formatear_float(paso.get("r")),
                    "s": formatear_float(paso.get("s")),
                    "raices": ", ".join(_raiz_breve(z) for z in raices_factor),
                }
            )

        if raices:
            cubiertas = sum(len(p.get("raices_factor", ())) for p in pasos)
            restantes = list(raices)[self._raices_en_cero() + cubiertas:]
            if restantes:
                filas.append(
                    {
                        "factor": "Resto",
                        "iter": "—",
                        "r": "—",
                        "s": "—",
                        "raices": ", ".join(_raiz_breve(z) for z in restantes),
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

        while len(etiquetas) < len(filas):
            etiquetas.append(("final",))
        return etiquetas

    def _mostrar_resultado(self, resultado):
        raices = list(resultado.valor or [])
        filas = self._filas(resultado.pasos, raices)
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

        if len(principal) <= 34:
            fuente = self.fuentes.big
        elif len(principal) <= 70:
            fuente = self.fuentes.h2
        else:
            fuente = self.fuentes.bold
        self.resultado.lbl_principal.configure(font=fuente)
        self.resultado.mostrar(
            principal,
            detalle,
            "Factores cuadráticos reales/complejos",
            tono="amber" if resultado.avisos else "verde",
        )
        self._dibujar(raices, resultado.pasos)
        self._animar([{"i": i} for i in range(len(resultado.pasos))])

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

    def _dibujar(self, raices, pasos):
        self._mostrar_polinomio(self._coef)

        if not raices:
            self.grafico.limpiar("No hay raíces para mostrar.")
            self._pasos_bairstow = []
            self._grupos_raices = []
            self._prueba_raices = []
            self._estela_factor = []
            self._prueba_reales = []
            return

        self._pasos_bairstow = list(pasos or [])
        self.grafico.dibujar_raices(
            self._coef, raices, mostrar=not self._pasos_bairstow
        )
        ax2 = self.grafico.ax2

        self._prueba_reales = []
        for _ in range(2):
            linea = self.grafico.ax.plot(
                [], [], marker="D", color=NAVY, markerfacecolor=NAVY,
                markeredgewidth=1.1, markersize=7, linestyle="none",
                zorder=8
            )[0]
            linea.set_visible(False)
            self._prueba_reales.append(linea)

        if ax2 is not None:
            self._prueba_raices = []
            for _ in range(2):
                linea = ax2.plot(
                    [], [], marker="D", color=NAVY, markerfacecolor=NAVY,
                    markeredgewidth=1.1, markersize=7, linestyle="none",
                    zorder=8
                )[0]
                linea.set_visible(False)
                self._prueba_raices.append(linea)

            self._estela_factor = [
                ax2.plot(
                    [], [], color=NAVY, lw=0.9, ls=":", alpha=0.7,
                    visible=False, zorder=4
                )[0] for _ in range(2)
            ]
            self.grafico.leyenda_plano(
                [self._prueba_raices[0], self._estela_factor[0]],
                ["Raíces del factor", "Trayectoria del factor"],
            )
        else:
            self._prueba_raices = []
            self._estela_factor = []

        if self._hay_raices_reales_en_pasos():
            self.grafico.leyenda_real(
                [self._prueba_reales[0]], ["Raíz real del factor"]
            )

        self._ultimo_por_factor = {}
        self._factor_actual = None
        self._grupos_raices = []
        if not self._pasos_bairstow:
            return

        n_cero = self._raices_en_cero()
        offset = 0
        if n_cero:
            grupo = list(range(0, min(n_cero, len(raices))))
            self._grupos_raices.append((-1, grupo))
            offset = len(grupo)

        ultimo_paso = {}
        for i, paso in enumerate(self._pasos_bairstow):
            ultimo_paso[paso.get("factor")] = i
        self._ultimo_por_factor = dict(ultimo_paso)
        for factor in sorted(ultimo_paso, key=lambda f: (f is None, f)):
            grupo = list(range(offset, min(offset + 2, len(raices))))
            if not grupo:
                break
            self._grupos_raices.append((ultimo_paso[factor], grupo))
            offset += len(grupo)

        if offset < len(raices):
            self._grupos_raices.append(
                (len(self._pasos_bairstow) - 1, list(range(offset, len(raices))))
            )

    def _hay_raices_reales_en_pasos(self):
        """True si alguna iteración tiene raíces reales que se puedan animar."""
        for paso in getattr(self, "_pasos_bairstow", []):
            for z in paso.get("raices_actuales") or ():
                try:
                    if abs(complex(z).imag) <= 1e-9:
                        return True
                except (TypeError, ValueError):
                    continue
        return False

    def _raices_en_cero(self):
        coef = list(self._coef)
        cantidad = 0
        while len(coef) > 1 and coef[0] == 0:
            coef.pop(0)
            cantidad += 1
        return cantidad

    def _aplicar_paso(self, indice):
        super()._aplicar_paso(indice)
        if not getattr(self, "_pasos_bairstow", []):
            return

        visibles = set()
        if indice >= 0:
            for fin, grupo in self._grupos_raices:
                if fin <= indice:
                    visibles.update(grupo)
        for i, artistas in enumerate(
            getattr(self.grafico, "artistas_raices", [])
        ):
            visible = i in visibles
            for artista in artistas:
                artista.set_visible(visible)

        for artista in getattr(self, "_prueba_raices", []):
            artista.set_visible(False)
        for artista in getattr(self, "_prueba_reales", []):
            artista.set_visible(False)
        for linea in getattr(self, "_estela_factor", []):
            linea.set_visible(False)

        if indice < 0 or indice >= len(self._pasos_bairstow):
            self.grafico.redibujar()
            return

        paso = self._pasos_bairstow[indice]
        factor = paso.get("factor")

        if indice == getattr(self, "_ultimo_por_factor", {}).get(factor):
            self.grafico.redibujar()
            return

        raices_siguientes = self._raices_siguientes(paso)
        for artista, z in zip(self._prueba_raices, raices_siguientes):
            artista.set_data([z.real], [z.imag])
            artista.set_visible(True)

        for artista, z in zip(getattr(self, "_prueba_reales", []), raices_siguientes):
            if abs(z.imag) <= 1e-9:
                artista.set_data([z.real], [0.0])
                artista.set_visible(True)

        trayectorias = [([], []), ([], [])]
        for anterior in self._pasos_bairstow[: indice + 1]:
            if anterior.get("factor") != factor:
                continue
            for k, z in enumerate(self._raices_siguientes(anterior)[:2]):
                trayectorias[k][0].append(z.real)
                trayectorias[k][1].append(z.imag)

        for linea, (xs, ys) in zip(getattr(self, "_estela_factor", []), trayectorias):
            if len(xs) > 1:
                linea.set_data(xs, ys)
                linea.set_visible(True)

        self.grafico.redibujar()

    @staticmethod
    def _raices_siguientes(paso):
        """Raíces del factor con (r + dr, s + ds): la estimación tras la iteración."""
        try:
            return list(
                controlador.raices_del_factor(
                    paso["r"] + paso["dr"], paso["s"] + paso["ds"]
                )
            )
        except (KeyError, TypeError, ValueError):
            return list(paso.get("raices_actuales") or ())

    def _mostrar_pasos_error(self, pasos):
        self._configurar_columnas()
        filas = self._filas(pasos)
        self.tabla.cargar(filas, self._tags(filas, pasos))