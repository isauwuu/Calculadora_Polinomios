"""Pestaña 5: separación de raíces reales por el teorema de Sturm."""

import base64
import io
import re
import tkinter as tk
from fractions import Fraction

from core.resultado import Resultado
from gui import controlador
from gui.estilo import CARD, GREEN, GREEN_L, MUTED, NAVY, INK
from gui.formato import formatear_fraccion, formatear_polinomio
from gui.pestanas.base import PestanaBase
from gui.widgets import Card

_SUPERINDICES = str.maketrans("0123456789", "⁰¹²³⁴⁵⁶⁷⁸⁹")
_SUBINDICES = str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉")


def con_superindices(texto):
    """Convierte x^2, x^10, etc. en x², x¹⁰ usando Unicode."""
    return re.sub(r"\^(\d+)", lambda m: m.group(1).translate(_SUPERINDICES), texto)


def subindice(n):
    """Convierte 0, 1, 12 en ₀, ₁, ₁₂ usando Unicode."""
    return str(n).translate(_SUBINDICES)


def latex_polinomio(coef):
    """Polinomio (coeficientes de menor a mayor grado) en sintaxis mathtext."""
    terminos = []
    for k in range(len(coef) - 1, -1, -1):
        c = Fraction(coef[k]).limit_denominator(10 ** 6)
        if c == 0:
            continue
        a = abs(c)
        if k == 0 or a != 1:
            if a.denominator == 1:
                num = str(a.numerator)
            else:
                num = r"\frac{%d}{%d}" % (a.numerator, a.denominator)
        else:
            num = ""
        var = "" if k == 0 else ("x" if k == 1 else "x^{%d}" % k)
        terminos.append(("-" if c < 0 else "+", num + var))
    if not terminos:
        return "0"
    signo, texto = terminos[0]
    out = ("-" if signo == "-" else "") + texto
    for signo, texto in terminos[1:]:
        out += f" {signo} {texto}"
    return out


class PestanaSturm(PestanaBase):
    titulo_tabla = "Sturm: sucesión y signos"
    subtitulo_tabla = ""
    usa_animacion = False
    pie_en_grafico = False

    def construir_entrada(self, parent):
        self.v_coef = tk.StringVar(value="4, 0, -5, 0, 1")

        self.campo(
            parent, "Coeficientes (de mayor a menor grado)", self.v_coef,
            "Acepta enteros, decimales y fracciones: 3/2",
        )

        tk.Label(
            parent,
            text=(
                "Se calcula la sucesión de Sturm, se acotan las raíces reales "
                "y se subdividen los intervalos hasta separar cada raíz.\n"
                "Aritmética exacta (fracciones)"
            ),
            font=self.fuentes.small, bg=CARD, fg=MUTED,
            justify="left", anchor="w", wraplength=300
        ).pack(fill="x", pady=(12, 0))

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

    def _construir_esquema(self):
        """Reemplazamos el layout por uno más compacto sin espacios vacíos."""
        super()._construir_esquema()

        if self.usa_tabla:
            self.tabla.pack_forget()

            self.frame_sucesion = tk.Frame(self.card_centro.inner, bg=CARD)
            self.frame_sucesion.pack(side="top", fill="x", pady=(0, 6))

            self.tabla.pack(side="top", fill="x")

            self.panel_info = tk.Frame(self.card_centro.inner, bg=CARD)
            self.panel_info.pack(side="top", fill="x", pady=(8, 0))

    # ------------------------------------------------------------------
    # Cálculo: cotas + subdivisión (controlador.biseccion_sturm)
    # ------------------------------------------------------------------
    @staticmethod
    def _a_fraccion(x):
        if isinstance(x, Fraction):
            return x
        if isinstance(x, int):
            return Fraction(x)
        return Fraction(x).limit_denominator(10 ** 6)

    @staticmethod
    def _txt(x):
        return str(x.numerator) if x.denominator == 1 else f"{x.numerator}/{x.denominator}"

    def _separar_raices(self):
        """Cotas de las raíces y subdivisión hasta una raíz por intervalo.

        La subdivisión la hace ``controlador.biseccion_sturm``; acá solo se
        toma el estado final y se arma la tabla con los extremos resultantes.
        """
        ajustado = controlador.cotas(self._texto_coef).valor["ajustado"]

        extremos = []
        for clave in ("neg", "pos"):
            if ajustado[clave]:
                a, b = (self._a_fraccion(x) for x in ajustado[clave])
                extremos.append((a, b))

        if not extremos:
            if ajustado["cero_es_raiz"]:
                raise ValueError("La única raíz real del polinomio es 0.")
            raise ValueError("Las cotas indican que el polinomio no tiene raíces reales.")

        intervalos, puntos, avisos = [], [], []
        for a, b in extremos:
            res = controlador.biseccion_sturm(self._texto_coef, self._txt(a), self._txt(b))
            for x, y, c in res["estados"][-1]["intervalos"]:
                if c == 1:
                    intervalos.append((x, y))
                else:
                    avisos.append(
                        "No se pudo separar cada raíz en su propio intervalo "
                        "(hay raíces muy cercanas o múltiples)."
                    )
                for p in (x, y):
                    if p not in puntos:
                        puntos.append(p)

        puntos.sort()
        texto = ", ".join(self._txt(x) for x in puntos)
        tabla = controlador.tabla_signos_sturm(self._texto_coef, texto, simplificada=False)
        return tabla, intervalos, list(dict.fromkeys(avisos))

    def _calcular(self):
        self._texto_coef = self.v_coef.get()

        tabla, intervalos, avisos = self._separar_raices()

        multiples = any("múltiples" in a for a in tabla["avisos"])
        original = None
        if multiples:
            f_original = getattr(controlador, "sucesion_estandar_sturm", None)
            if f_original is not None:
                try:
                    original = f_original(self._texto_coef)
                except Exception:
                    original = None

        datos = {
            "tabla": tabla,
            "intervalos": intervalos,
            "p": controlador.leer_polinomio(self._texto_coef),
            "multiples": multiples,
            "original": original,
        }
        return Resultado(valor=datos, avisos=list(tabla["avisos"]) + avisos)

    def _mostrar_resultado(self, resultado):
        datos = resultado.valor
        tabla = datos["tabla"]
        intervalos = datos["intervalos"]
        p = datos["p"]

        self._dibujar_sucesion(datos)
        self._llenar_tabla(tabla)
        self._mostrar_tarjeta()

        cant = len(intervalos)
        if cant == 0:
            principal = "Sin raíces reales"
            detalle = "Ningún intervalo contiene una sola raíz."
            tono = "amber"
        else:
            multiples = datos["multiples"]
            if cant == 1:
                principal = "1 raíz real distinta" if multiples else "1 raíz real simple"
            else:
                principal = (
                    f"{cant} raíces reales distintas" if multiples
                    else f"{cant} raíces reales simples"
                )
            detalle = "Raíces en: " + ", ".join(
                f"({formatear_fraccion(a)}, {formatear_fraccion(b)})" for a, b in intervalos
            )
            tono = "amber" if resultado.avisos else "verde"

        self.resultado.lbl_principal.configure(font=self.fuentes.big)
        self.resultado.mostrar(
            principal,
            detalle,
            "Método exacto (Teorema de Sturm)",
            tono=tono
        )
        self._dibujar(p, intervalos)

    def _imagen_latex(self, latex, color, tam=13):
        """Renderiza texto mathtext a PNG y lo devuelve como PhotoImage (o None)."""
        try:
            from matplotlib.backends.backend_agg import FigureCanvasAgg
            from matplotlib.figure import Figure

            fig = Figure(dpi=100)
            FigureCanvasAgg(fig)
            fig.text(0, 0, f"${latex}$", fontsize=tam, color=color)
            buf = io.BytesIO()
            fig.savefig(buf, format="png", bbox_inches="tight",
                        pad_inches=0.04, transparent=True)
            return tk.PhotoImage(data=base64.b64encode(buf.getvalue()))
        except Exception:
            return None

    def _fila_latex(self, parent, latex, fallback):
        img = self._imagen_latex(latex, INK)
        if img is not None:
            self._imagenes.append(img)
            lbl = tk.Label(parent, image=img, bg=CARD, anchor="w")
        else:
            lbl = tk.Label(parent, text=fallback, font=self.fuentes.normal,
                           bg=CARD, fg=INK, anchor="w")
        lbl.pack(anchor="w", pady=1)

    def _bloque_sucesion(self, titulo, sucesion, letra, cero_en=None, mcd=None):
        tk.Label(
            self.frame_sucesion, text=titulo,
            font=self.fuentes.bold, bg=CARD, fg=NAVY,
            anchor="w", justify="left", wraplength=430,
        ).pack(anchor="w", pady=(6, 3))

        for i, pol in enumerate(sucesion):
            self._fila_latex(
                self.frame_sucesion,
                f"{letra}_{{{i}}}(x) = " + latex_polinomio(pol.coef),
                f"{letra}{subindice(i)}(x) = "
                + con_superindices(formatear_polinomio(pol.coef)),
            )
        if cero_en is not None:
            self._fila_latex(
                self.frame_sucesion, f"{letra}_{{{cero_en}}}(x) = 0",
                f"{letra}{subindice(cero_en)}(x) = 0",
            )
        if mcd is not None:
            self._fila_latex(
                self.frame_sucesion,
                r"\mathrm{mcd}(P, P^{\prime}) = " + latex_polinomio(mcd.coef),
                "mcd(P, P') = " + con_superindices(formatear_polinomio(mcd.coef)),
            )

    def _dibujar_sucesion(self, datos):
        """Dibuja la sucesión (y la rehecha, si hubo raíces múltiples)."""
        for w in self.frame_sucesion.winfo_children():
            w.destroy()
        self._imagenes = []

        sucesion = datos["tabla"]["sucesion"]
        original = datos["original"]

        if not datos["multiples"]:
            self._bloque_sucesion("Sucesión de polinomios:", sucesion, "P")
            return

        if original is not None:
            self._bloque_sucesion(
                "Sucesión de Sturm de P (el resto se anula: hay raíces múltiples):",
                original["sucesion"], "P",
                cero_en=original["cero_en"], mcd=original["mcd"],
            )
        self._bloque_sucesion(
            "Sucesión rehecha desde Q = P / mcd(P, P′):", sucesion, "g",
        )

    def _llenar_tabla(self, tabla):
        puntos = tabla["puntos"]
        sucesion = tabla["sucesion"]

        columnas = [("pol", "x", 48, "w")]
        for i, pt in enumerate(puntos):
            columnas.append((f"pt_{i}", formatear_fraccion(pt), 54, "center"))

        self.tabla.configurar(columnas, estirar=True)

        filas = []
        for r, _pol in enumerate(sucesion):
            fila = {"pol": f"P{subindice(r)}"}
            for c, signo in enumerate(tabla["signos"][r]):
                fila[f"pt_{c}"] = "+" if signo > 0 else ("-" if signo < 0 else "0")
            filas.append(fila)

        fila_ncs = {"pol": "NCS"}
        for c, n in enumerate(tabla["ncs"]):
            fila_ncs[f"pt_{c}"] = str(n)
        filas.append(fila_ncs)

        tags = [("odd",) if i % 2 else () for i in range(len(sucesion))]
        tags.append(("final",))
        self.tabla.cargar(filas, tags)

        for w in self.panel_info.winfo_children():
            w.destroy()

        tk.Label(
            self.panel_info, text="Raíces en (a, b) = NCS(a) − NCS(b)",
            font=self.fuentes.small, bg=CARD, fg=MUTED, anchor="w"
        ).pack(anchor="w")
        tk.Label(
            self.panel_info,
            text="Los extremos son las cotas de las raíces; los puntos intermedios salen de subdividir hasta separarlas.",
            font=self.fuentes.small, bg=CARD, fg=MUTED, anchor="w",
            justify="left", wraplength=430,
        ).pack(anchor="w", pady=(2, 0))

    def _dibujar(self, p, intervalos):
        self._mostrar_polinomio(p.coef)

        self.grafico.dibujar(p.a_float(), titulo="")
        ax = self.grafico.ax

        for i, (a, b) in enumerate(intervalos):
            ax.axvspan(
                float(a), float(b), color=GREEN_L, alpha=0.55, zorder=1,
                label="Intervalo con raíz" if i == 0 else None,
            )

        for a, b in intervalos:
            ax.plot([float(a), float(b)], [0, 0], marker="o", color=GREEN,
                    markerfacecolor=GREEN, markersize=6, linestyle="none", zorder=5)

        self.grafico.finalizar(ubicacion="best")

    def _mensaje_exito(self, resultado):
        return "Cálculo de Sturm completado."