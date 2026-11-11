"""Figuras de matplotlib embebidas en Tkinter, sin pyplot.

Cada pestaña crea su Figure una sola vez y la actualiza con clear/draw_idle.
La figura y los ejes quedan accesibles para sumar después interacción o
animación, que en esta etapa no se implementan.
"""

import math
import tkinter as tk

import matplotlib

matplotlib.use("TkAgg")
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from gui.estilo import CARD, GREEN, INK, LINE, MUTED, ORANGE, PLOT
from gui.formato import formatear_complejo, formatear_float


def configurar_fuente(familia):
    """Ajusta matplotlib a la misma familia de fuentes que Tkinter."""
    matplotlib.rcParams["font.family"] = [familia, "DejaVu Sans"]
    matplotlib.rcParams["mathtext.fontset"] = "dejavusans"


def _coef_desc(coeficientes):
    """Coeficientes de mayor a menor para numpy.polyval/np.roots."""
    return [float(c) for c in reversed(list(coeficientes))]


def evaluar_curva(coeficientes, xs):
    return np.polyval(_coef_desc(coeficientes), xs)


def rango_x(coeficientes, puntos, pad=0.18):
    """Elige un intervalo horizontal que contenga los puntos importantes."""
    valores = []
    for punto in puntos:
        try:
            valor = float(punto)
        except (TypeError, ValueError):
            continue
        if math.isfinite(valor):
            valores.append(valor)
    if not valores:
        valores = [-5.0, 5.0]

    lo, hi = min(valores), max(valores)
    if math.isclose(lo, hi, abs_tol=1e-12):
        extra = max(1.0, abs(lo) * 0.5)
        lo -= extra
        hi += extra
    span = hi - lo
    if lo > 0 and lo <= 2.0 * span:
        lo = 0.0
    if hi < 0 and -hi <= 2.0 * span:
        hi = 0.0
    span = hi - lo
    return lo - pad * span, hi + pad * span


def _ajustar_y(ax, ys):
    """Recorta valores extremos para que la curva se vea, sin perder el cero."""
    finitos = ys[np.isfinite(ys)]
    if finitos.size == 0:
        ax.set_ylim(-5, 5)
        return
    bajo, alto = np.percentile(finitos, [2, 98])
    bajo = min(float(bajo), 0.0)
    alto = max(float(alto), 0.0)
    span = alto - bajo
    if span < 1e-12:
        bajo -= 1.0
        alto += 1.0
        span = 2.0
    ax.set_ylim(bajo - 0.12 * span, alto + 0.12 * span)


def estilizar(ax, titulo=None):
    ax.set_facecolor(CARD)
    ax.grid(alpha=0.3, lw=0.5, color=LINE)
    ax.tick_params(labelsize=8, colors=MUTED, length=0)
    for nombre, spine in ax.spines.items():
        spine.set_visible(nombre in ("left", "bottom"))
        spine.set_color(LINE)
    if titulo:
        ax.set_title(titulo, fontsize=9, color=INK, loc="left", pad=5)


def dibujar_curva(ax, coeficientes, xlim=None, puntos=None, color=PLOT, etiqueta="P(x)"):
    """Dibuja P(x) y devuelve (xs, ys). No usa la GUI para calcular resultados."""
    if xlim is None:
        xlim = rango_x(coeficientes, puntos or [])
    xs = np.linspace(xlim[0], xlim[1], 500)
    ys = evaluar_curva(coeficientes, xs)
    ax.plot(xs, ys, color=color, lw=2.0, label=etiqueta, zorder=3)
    ax.axhline(0, color=INK, lw=0.8, zorder=1)
    ax.set_xlim(*xlim)
    _ajustar_y(ax, ys)
    return xs, ys


def raices_referencia(coeficientes):
    """Raíces de referencia para la línea de verificación (solo presentación)."""
    try:
        if len(coeficientes) < 2:
            return []
        return [complex(z) for z in np.roots(_coef_desc(coeficientes))]
    except (TypeError, ValueError, np.linalg.LinAlgError):
        return []


def texto_referencia(coeficientes, cercana=None, max_items=4):
    """Texto breve con la referencia numpy.roots."""
    raices = [z for z in raices_referencia(coeficientes) if math.isfinite(z.real) and math.isfinite(z.imag)]
    if not raices:
        return "numpy.roots: sin raíces."
    reales = sorted(z.real for z in raices if math.isclose(z.imag, 0.0, abs_tol=1e-9))
    if cercana is not None:
        candidatas = reales or raices
        elegida = min(candidatas, key=lambda z: abs(complex(z) - complex(cercana)))
        return f"Referencia numpy.roots: {formatear_complejo(elegida)}"
    if reales:
        mostradas = ", ".join(formatear_float(r) for r in reales[:max_items])
        if len(reales) > max_items:
            mostradas += ", …"
        return f"Referencia numpy.roots (raíces reales): {mostradas}"
    mostradas = ", ".join(formatear_complejo(z) for z in raices[:max_items])
    if len(raices) > max_items:
        mostradas += ", …"
    return f"Referencia numpy.roots: {mostradas}"


class GraficoSimple(tk.Frame):
    """Figura de una sola curva para las pestañas 1 a 5."""

    def __init__(self, master, pestana=None):
        super().__init__(master, bg=CARD)
        self.pestana = pestana
        self.figura = Figure(figsize=(4.2, 3.2), dpi=100, facecolor=CARD)
        self.ax = self.figura.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figura, master=self)
        self.widget = self.canvas.get_tk_widget()
        self.widget.configure(bg=CARD, highlightthickness=0)
        self.widget.pack(fill="both", expand=True)
        self.limpiar()

    def limpiar(self, mensaje="Ingresá los datos y presioná Calcular."):
        self.ax.clear()
        self.ax.set_facecolor(CARD)
        self.ax.axis("off")
        self.ax.text(
            0.5,
            0.5,
            mensaje,
            transform=self.ax.transAxes,
            ha="center",
            va="center",
            fontsize=9,
            color=MUTED,
            wrap=True,
        )
        self.canvas.draw_idle()

    def preparar(self, titulo=None):
        self.ax.clear()
        self.ax.axis("on")
        estilizar(self.ax, titulo)
        return self.ax

    def dibujar(self, coeficientes, xlim=None, puntos=None, titulo=None, etiqueta="P(x)"):
        self.preparar(titulo)
        xs, ys = dibujar_curva(self.ax, coeficientes, xlim, puntos, PLOT, etiqueta)
        return xs, ys

    def punto(self, x, y, etiqueta=None, color=ORANGE, marker="o", mfc=None, ms=7, mew=1.2):
        self.ax.plot(
            [float(x)],
            [float(y)],
            marker=marker,
            color=color,
            markerfacecolor=mfc if mfc is not None else color,
            markeredgecolor=color,
            markeredgewidth=mew,
            markersize=ms,
            linestyle="none",
            label=etiqueta,
            zorder=6,
        )

    def raiz(self, x, etiqueta="Raíz"):
        self.ax.plot(
            [float(x)],
            [0.0],
            marker="o",
            color=GREEN,
            markerfacecolor="none",
            markeredgewidth=1.8,
            markersize=10,
            linestyle="none",
            label=etiqueta,
            zorder=7,
        )

    def finalizar(self, leyenda=True, ubicacion="best"):
        self.figura.subplots_adjust(left=0.11, right=0.97, top=0.86, bottom=0.14)
        if leyenda:
            handles, labels = self.ax.get_legend_handles_labels()
            if handles:
                self.ax.legend(fontsize=7, frameon=False, loc=ubicacion)
        self.canvas.draw_idle()

    def redibujar(self):
        self.canvas.draw_idle()

    def cerrar(self):
        try:
            self.figura.clear()
            self.widget.destroy()
        except tk.TclError:
            pass


class GraficoBairstow(GraficoSimple):
    """Figura doble: P(x) en la recta real y todas las raíces en el plano complejo."""

    def __init__(self, master, pestana=None):
        super().__init__(master, pestana)
        self.figura.clear()
        self.ax = self.figura.add_subplot(1, 2, 1)
        self.ax2 = self.figura.add_subplot(1, 2, 2)
        self.limpiar()

    def limpiar(self, mensaje="Ingresá los datos y presioná Calcular."):
        self.figura.clear()
        self.ax = self.figura.add_subplot(1, 2, 1)
        self.ax2 = self.figura.add_subplot(1, 2, 2)
        for ax in (self.ax, self.ax2):
            ax.set_facecolor(CARD)
            ax.axis("off")
        self.figura.text(
            0.5,
            0.5,
            mensaje,
            ha="center",
            va="center",
            fontsize=9,
            color=MUTED,
        )
        self.canvas.draw_idle()

    def dibujar_raices(self, coeficientes, raices):
        """Dibuja la curva real y el plano complejo con la clasificación pedida."""
        self.figura.clear()
        ax_real = self.figura.add_subplot(1, 2, 1)
        ax_comp = self.figura.add_subplot(1, 2, 2)

        reales = [z.real for z in raices if math.isclose(complex(z).imag, 0.0, abs_tol=1e-9)]
        complejas = [complex(z) for z in raices if not math.isclose(complex(z).imag, 0.0, abs_tol=1e-9)]

        xlim = rango_x(coeficientes, reales)
        xs, _ = dibujar_curva(ax_real, coeficientes, xlim, reales, PLOT, "P(x)")
        if reales:
            ax_real.plot(
                reales,
                [0.0] * len(reales),
                marker="o",
                color=GREEN,
                markerfacecolor="none",
                markeredgewidth=1.6,
                markersize=8,
                linestyle="none",
                label="Raíces reales",
                zorder=6,
            )
        estilizar(ax_real, "P(x) en la recta real")
        if reales:
            ax_real.legend(fontsize=6, frameon=False, loc="best")

        ax_comp.axhline(0, color=INK, lw=0.7)
        ax_comp.axvline(0, color=INK, lw=0.7)
        if reales:
            ax_comp.plot(
                reales,
                [0.0] * len(reales),
                marker="o",
                color=GREEN,
                markerfacecolor="none",
                markeredgewidth=1.5,
                markersize=7,
                linestyle="none",
                label="Reales",
                zorder=5,
            )
        if complejas:
            ax_comp.plot(
                [z.real for z in complejas],
                [z.imag for z in complejas],
                marker="s",
                color=ORANGE,
                markerfacecolor=ORANGE,
                markersize=6,
                linestyle="none",
                label="Complejas",
                zorder=5,
            )

        valores = [abs(z.real) for z in raices] + [abs(z.imag) for z in raices]
        limite = max([1.5] + [v * 1.25 + 0.5 for v in valores])
        ax_comp.set_xlim(-limite, limite)
        ax_comp.set_ylim(-limite, limite)
        ax_comp.set_aspect("equal", adjustable="box")
        estilizar(ax_comp, "Plano complejo")
        ax_comp.tick_params(labelsize=7)
        if raices:
            ax_comp.legend(fontsize=6, frameon=False, loc="best")

        self.figura.subplots_adjust(left=0.09, right=0.97, top=0.86, bottom=0.14, wspace=0.38)
        self.canvas.draw_idle()
        self.ax = ax_real
        self.ax2 = ax_comp
