"""Figuras de matplotlib embebidas en Tkinter, sin pyplot."""

import math
import tkinter as tk

import matplotlib

matplotlib.use("TkAgg")
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib.lines import Line2D
from matplotlib.ticker import MaxNLocator

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


def rango_x(coeficientes, puntos, pad=0.12):
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
    ax.grid(alpha=0.3, lw=0.6, color=LINE)
    ax.tick_params(labelsize=10, colors="#52636D", length=0)
    for nombre, spine in ax.spines.items():
        spine.set_visible(nombre in ("left", "bottom"))
        spine.set_color(LINE)
    if titulo:
        ax.set_title(titulo, fontsize=11, color=INK, loc="left", pad=3)


def dibujar_curva(ax, coeficientes, xlim=None, puntos=None, color=PLOT, etiqueta="P(x)"):
    """Dibuja P(x) y devuelve (xs, ys). No usa la GUI para calcular resultados."""
    if xlim is None:
        xlim = rango_x(coeficientes, puntos or [])

    span = xlim[1] - xlim[0]
    x_dibujo_min = xlim[0] - span * 0.2
    x_dibujo_max = xlim[1] + span * 0.2

    xs = np.linspace(x_dibujo_min, x_dibujo_max, 1000)
    ys = evaluar_curva(coeficientes, xs)

    linea = ax.plot(xs, ys, color=color, lw=2.0, label=etiqueta, zorder=3)[0]

    # Marcamos ambos ejes (X e Y) con líneas oscuras
    ax.axhline(0, color=INK, lw=1.0, zorder=1)
    ax.axvline(0, color=INK, lw=1.0, zorder=1)

    ax.set_xlim(*xlim)

    ys_visibles = evaluar_curva(coeficientes, np.linspace(xlim[0], xlim[1], 500))
    _ajustar_y(ax, ys_visibles)

    # --- REDIBUJADO DINÁMICO INFALIBLE ---
    def _actualizar_curva(event_ax):
        # Evitamos bucles infinitos
        if getattr(linea, '_actualizando', False):
            return

        # Cada vez que cambie el eje X, recalculamos para cubrir exactamente lo que se ve + un margen
        x0, x1 = event_ax.get_xlim()
        nueva_span = x1 - x0
        nuevo_min = x0 - nueva_span * 0.2
        nuevo_max = x1 + nueva_span * 0.2

        nuevos_xs = np.linspace(nuevo_min, nuevo_max, 1000)
        nuevos_ys = evaluar_curva(coeficientes, nuevos_xs)

        linea._actualizando = True
        linea.set_data(nuevos_xs, nuevos_ys)
        linea._actualizando = False

    # Desconectamos el callback anterior si existe para no acumular eventos
    if hasattr(ax, '_callback_id_curva'):
        ax.callbacks.disconnect(ax._callback_id_curva)

    # Conectamos el nuevo callback y guardamos su ID
    ax._callback_id_curva = ax.callbacks.connect("xlim_changed", _actualizar_curva)
    # -------------------------------------

    return xs, ys


_ESTILOS_LEYENDA = (
    "color",
    "linestyle",
    "linewidth",
    "alpha",
    "marker",
    "markersize",
    "markerfacecolor",
    "markeredgecolor",
    "markeredgewidth",
)


def _handle_visible(handle):
    """Devuelve un proxy visible con el mismo estilo para la leyenda.

    Los artistas de la animación arrancan ocultos a propósito; si se pasan
    tal cual, matplotlib dibuja el símbolo de la leyenda en blanco.
    """
    if handle.get_visible():
        return handle
    proxy = Line2D([], [])
    for atributo in _ESTILOS_LEYENDA:
        try:
            valor = getattr(handle, f"get_{atributo}")()
            getattr(proxy, f"set_{atributo}")(valor)
        except (AttributeError, TypeError, ValueError):
            continue
    proxy.set_visible(True)
    return proxy


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

        self.al_clic = None
        self._coef_actual = None
        self._puntos_hover = []
        self._hover_art = None
        self._xlim_base = None
        self._ylim_base = None
        self._arrastre = None
        self._movido = False
        self._hover = None
        self.widget.bind("<Leave>", self._salir)
        self.canvas.mpl_connect("button_press_event", self._presionar)
        self.canvas.mpl_connect("motion_notify_event", self._mover)
        self.canvas.mpl_connect("button_release_event", self._soltar)
        self.canvas.mpl_connect("scroll_event", self._rueda)
        self.limpiar()

    def limpiar(self, mensaje="Ingresá los datos y presioná Calcular."):
        self.ax.clear()
        self.ax.set_facecolor(CARD)
        self.ax.axis("off")
        self.ax.text(
            0.5, 0.5, mensaje,
            transform=self.ax.transAxes,
            ha="center", va="center",
            fontsize=11, color=MUTED, wrap=True,
        )
        self._coef_actual = None
        self._puntos_hover = []
        self._hover_art = None
        self._xlim_base = None
        self._ylim_base = None
        self.canvas.draw_idle()

    def preparar(self, titulo=None):
        self.ax.clear()
        self.ax.axis("on")
        estilizar(self.ax, titulo)
        self._puntos_hover = []
        self._hover_art = self.ax.annotate(
            "",
            xy=(0, 0),
            xytext=(12, 12),
            textcoords="offset points",
            fontsize=9.5, color=INK,
            bbox=dict(boxstyle="round,pad=0.25", fc="white", ec=LINE, alpha=0.94),
            visible=False, zorder=20,
        )
        return self.ax

    def dibujar(self, coeficientes, xlim=None, puntos=None, titulo=None, etiqueta="P(x)"):
        self._coef_actual = list(coeficientes)
        self.preparar(titulo)
        xs, ys = dibujar_curva(self.ax, coeficientes, xlim, puntos, PLOT, etiqueta)
        return xs, ys

    def punto(self, x, y, etiqueta=None, color=ORANGE, marker="o", mfc=None, ms=7, mew=1.2, axes=None):
        ax = axes if axes is not None else self.ax
        linea = ax.plot(
            [float(x)], [0.0],
            marker="o", color=GREEN,
            markerfacecolor=GREEN,
            markeredgewidth=1.8, markersize=10,
            markeredgecolor=color,
            linestyle="none", label=etiqueta, zorder=6,
        )[0]
        self._puntos_hover.append((ax, float(x), float(y), etiqueta or "punto", linea))
        return linea

    def raiz(self, x, etiqueta="Raíz", axes=None):
        ax = axes if axes is not None else self.ax
        linea = ax.plot(
            [float(x)], [0.0],
            marker="o", color=GREEN, markerfacecolor=GREEN,
            markeredgecolor="white", markeredgewidth=1.6, markersize=11,
            linestyle="none", label=etiqueta, zorder=7,
        )[0]
        self._puntos_hover.append((ax, float(x), 0.0, etiqueta or "raíz", linea))
        return linea

    def finalizar(self, leyenda=True, ubicacion="best"):
        self.figura.subplots_adjust(left=0.12, right=0.98, top=0.86, bottom=0.15)
        if leyenda:
            handles, labels = self.ax.get_legend_handles_labels()
            if handles:
                self.ax.legend(fontsize=9.5, frameon=False, loc=ubicacion)
        self._xlim_base = self.ax.get_xlim()
        self._ylim_base = self.ax.get_ylim()
        self.canvas.draw_idle()

    def reset_vista(self):
        if self._xlim_base is None or self._ylim_base is None:
            return
        self.ax.set_xlim(*self._xlim_base)
        self.ax.set_ylim(*self._ylim_base)
        self.canvas.draw_idle()

    def redibujar(self):
        self.canvas.draw_idle()

    def _presionar(self, evento):
        if evento.button != 1:
            return
        if evento.xdata is None or evento.ydata is None:
            return
        ejes = evento.inaxes if evento.inaxes is not None else self.ax
        self._arrastre = (evento.x, evento.y, ejes.get_xlim(), ejes.get_ylim(), ejes)
        self._movido = False

    def _mover(self, evento):
        if self._arrastre is not None:
            x0, y0, xlim, ylim, ejes = self._arrastre
            dx = evento.x - x0
            dy = evento.y - y0
            if abs(dx) > 2 or abs(dy) > 2:
                self._movido = True
            ancho = max(self.widget.winfo_width(), 1)
            alto = max(self.widget.winfo_height(), 1)
            x_span = (xlim[1] - xlim[0]) * dx / ancho
            y_span = (ylim[1] - ylim[0]) * dy / alto
            ejes.set_xlim(xlim[0] - x_span, xlim[1] - x_span)
            ejes.set_ylim(ylim[0] - y_span, ylim[1] - y_span)
            self.canvas.draw_idle()
            return
        self._mostrar_hover(evento)

    def _soltar(self, evento):
        if evento.button != 1:
            return
        if self._arrastre is None:
            return
        arrastre = self._arrastre
        self._arrastre = None
        if not self._movido and self.al_clic is not None and evento.xdata is not None and evento.ydata is not None:
            self.al_clic(float(evento.xdata))
        if not self._movido:
            arrastre[4].set_xlim(*arrastre[2])
            arrastre[4].set_ylim(*arrastre[3])
            self.canvas.draw_idle()

    def _rueda(self, evento):
        delta = 120 if evento.button == "up" else -120
        self._rueda_boton(evento, delta)
        return "break"

    def _rueda_boton(self, evento, delta):
        if evento.xdata is None or evento.ydata is None:
            return
        ejes = evento.inaxes if evento.inaxes is not None else self.ax
        factor = 0.8 if delta > 0 else 1.25
        x, y = float(evento.xdata), float(evento.ydata)
        x0, x1 = ejes.get_xlim()
        y0, y1 = ejes.get_ylim()
        ejes.set_xlim(x - (x - x0) * factor, x + (x1 - x) * factor)
        ejes.set_ylim(y - (y - y0) * factor, y + (y1 - y) * factor)
        self.canvas.draw_idle()

    def _salir(self, _evento=None):
        if self._hover_art is not None:
            self._hover_art.set_visible(False)
            self.canvas.draw_idle()

    def _mostrar_hover(self, evento):
        if self._hover_art is None or evento.xdata is None or evento.ydata is None:
            return
        ejes = evento.inaxes
        if ejes is None or ejes not in self.figura.axes:
            ejes = self.ax
        x = float(evento.xdata)
        y = float(evento.ydata)
        texto = ""
        punto = None
        for ax_punto, px, py, etiqueta, artista in self._puntos_hover:
            if ax_punto is not ejes or not artista.get_visible():
                continue
            try:
                xp, yp = ejes.transData.transform((px, py))
            except (TypeError, ValueError):
                continue
            if math.hypot(xp - evento.x, yp - evento.y) <= 13:
                punto = (px, py, etiqueta)
                break

        if punto is not None:
            px, py, etiqueta = punto
            texto = f"{etiqueta}: ({formatear_float(px)}, {formatear_float(py)})"
            self._hover_art.xy = (px, py)
        elif ejes is self.ax and self._coef_actual is not None:
            valor = float(np.polyval(_coef_desc(self._coef_actual), x))
            try:
                xp, yp = ejes.transData.transform((x, valor))
            except (TypeError, ValueError):
                return
            if math.hypot(xp - evento.x, yp - evento.y) <= 24:
                texto = f"x = {formatear_float(x)} · P(x) = {formatear_float(valor)}"
                self._hover_art.xy = (x, valor)
            else:
                texto = f"x = {formatear_float(x)}"

        if texto:
            self._hover_art.set_text(texto)
            self._hover_art.set_visible(True)
            self.canvas.draw_idle()
        else:
            self._hover_art.set_visible(False)
            self.canvas.draw_idle()

    def cerrar(self):
        try:
            self.figura.clear()
            self.widget.destroy()
        except tk.TclError:
            pass


class GraficoBairstow(GraficoSimple):
    """Figura con P(x) en la recta real y, al costado, el plano complejo."""

    _ANCHOS = [1.5, 1.0]

    def __init__(self, master, pestana=None):
        super().__init__(master, pestana)
        self.artistas_raices = []
        self._hover_art1 = None
        self._hover_art2 = None
        self._xlim_base2 = None
        self._ylim_base2 = None
        self._handles_base_real = []
        self._labels_base_real = []
        self._handles_base_comp = []
        self._labels_base_comp = []
        self.figura.clear()
        self.ax = self.figura.add_subplot(111)
        self.ax2 = None
        self.limpiar()

    def limpiar(self, mensaje="Ingresá los datos y presioná Calcular."):
        self.figura.clear()
        self.ax = self.figura.add_subplot(111)
        self.ax2 = None
        self.ax.set_facecolor(CARD)
        self.ax.axis("off")
        self.figura.text(
            0.5, 0.5, mensaje,
            ha="center", va="center",
            fontsize=11, color=MUTED,
        )
        self._coef_actual = None
        self._puntos_hover = []
        self._hover_art = None
        self._hover_art1 = None
        self._hover_art2 = None
        self._xlim_base = None
        self._ylim_base = None
        self._xlim_base2 = None
        self._ylim_base2 = None
        self.artistas_raices = []
        self._handles_base_real = []
        self._labels_base_real = []
        self._handles_base_comp = []
        self._labels_base_comp = []
        self.canvas.draw_idle()

    def _anotacion(self, ax):
        return ax.annotate(
            "",
            xy=(0, 0),
            xytext=(12, 12),
            textcoords="offset points",
            fontsize=9.5,
            color=INK,
            bbox=dict(boxstyle="round,pad=0.25", fc="white", ec=LINE, alpha=0.94),
            visible=False,
            zorder=20,
        )

    def leyenda_real(self, extra_handles=(), extra_labels=()):
        """Leyenda del gráfico real combinando los manuales con los extras."""
        if self.ax is None:
            return
        handles = list(self._handles_base_real)
        labels = list(self._labels_base_real)
        for handle, label in zip(extra_handles, extra_labels):
            if label not in labels:
                handles.append(_handle_visible(handle))
                labels.append(label)
        if not handles:
            return
        self.ax.legend(
            handles, labels,
            fontsize=9.5, frameon=False, loc="upper left",
        )

    def leyenda_plano(self, extra_handles=(), extra_labels=()):
        """Leyenda del plano complejo combinando los manuales con los extras."""
        if self.ax2 is None:
            return
        handles = list(self._handles_base_comp)
        labels = list(self._labels_base_comp)

        for handle, label in zip(extra_handles, extra_labels):
            if label not in labels:
                handles.append(_handle_visible(handle))
                labels.append(label)

        extras_h, extras_l = self.ax2.get_legend_handles_labels()
        for h, l in zip(extras_h, extras_l):
            if l not in labels:
                handles.append(h)
                labels.append(l)

        if not handles:
            return
        self.ax2.legend(
            handles, labels,
            fontsize=8.5, frameon=False, loc="upper center",
            bbox_to_anchor=(0.5, -0.24), borderaxespad=0.0,
            handletextpad=0.4, labelspacing=0.3,
        )

    def dibujar_raices(self, coeficientes, raices, mostrar=True):
        """Dibuja la curva y, si hay raíces complejas, el plano complejo al lado."""
        self.figura.clear()
        raices = [complex(z) for z in raices]

        reales = [z.real for z in raices if math.isclose(z.imag, 0.0, abs_tol=1e-9)]
        complejas = [z for z in raices if not math.isclose(z.imag, 0.0, abs_tol=1e-9)]

        if complejas:
            gs = self.figura.add_gridspec(
                1, 2, width_ratios=self._ANCHOS,
                left=0.09, right=0.98, top=0.88, bottom=0.17, wspace=0.30,
            )
            ax_real = self.figura.add_subplot(gs[0])
            ax_comp = self.figura.add_subplot(gs[1])
        else:
            ax_real = self.figura.add_subplot(111)
            ax_comp = None
            self.figura.subplots_adjust(left=0.12, right=0.98, top=0.86, bottom=0.15)

        xlim = rango_x(coeficientes, reales)
        self.ax = ax_real
        dibujar_curva(ax_real, coeficientes, xlim, reales, PLOT, "P(x)")
        estilizar(ax_real, "P(x) y raíces reales")

        # Handles manuales para el gráfico principal
        self._handles_base_real = [Line2D([0], [0], color=PLOT, lw=2.0)]
        self._labels_base_real = ["P(x)"]
        if reales:
            self._handles_base_real.append(Line2D([0], [0], marker="o", color=GREEN, markerfacecolor=GREEN,
                                                  markeredgewidth=1.6, markersize=8, linestyle="none"))
            self._labels_base_real.append("Raíces reales")

        self.leyenda_real()

        if ax_comp is not None:
            estilizar(ax_comp, "Plano complejo")
            ax_comp.axhline(0, color=INK, lw=0.6, zorder=1)
            ax_comp.axvline(0, color=INK, lw=0.6, zorder=1)

            valores = [abs(z.real) for z in raices] + [abs(z.imag) for z in raices]
            limite = max([1.5] + [v * 1.25 + 0.5 for v in valores])
            ax_comp.set_xlim(-limite, limite)
            ax_comp.set_ylim(-limite, limite)
            ax_comp.set_aspect("equal", adjustable="box")
            ax_comp.set_anchor("N")
            ax_comp.xaxis.set_major_locator(MaxNLocator(nbins=5))
            ax_comp.yaxis.set_major_locator(MaxNLocator(nbins=5))
            ax_comp.tick_params(labelsize=9)
            ax_comp.set_xlabel("Re", fontsize=9, color=MUTED, labelpad=2)
            ax_comp.set_ylabel("Im", fontsize=9, color=MUTED, labelpad=4, rotation=0)
            self.ax2 = ax_comp
            self._hover_art2 = self._anotacion(ax_comp)

            self._handles_base_comp = []
            self._labels_base_comp = []
            if reales:
                self._handles_base_comp.append(Line2D([0], [0], marker="o", color=GREEN, markerfacecolor=GREEN,
                                           markeredgewidth=1.5, markersize=6, linestyle="none"))
                self._labels_base_comp.append("Reales")
            if complejas:
                self._handles_base_comp.append(Line2D([0], [0], marker="s", color=ORANGE, markerfacecolor=ORANGE,
                                           markersize=6, linestyle="none"))
                self._labels_base_comp.append("Complejas")
        else:
            self.ax2 = None
            self._hover_art2 = None
            self._handles_base_comp = []
            self._labels_base_comp = []

        self._coef_actual = list(coeficientes)
        self._puntos_hover = []
        self._hover_art1 = self._anotacion(ax_real)
        self._hover_art = self._hover_art1
        self.artistas_raices = []

        for z in raices:
            artistas = []
            if math.isclose(z.imag, 0.0, abs_tol=1e-9):
                linea_real = ax_real.plot(
                    [z.real], [0.0],
                    marker="o", color=GREEN, markerfacecolor=GREEN,
                    markeredgewidth=1.6, markersize=8, linestyle="none",
                    visible=mostrar, zorder=6,
                )[0]
                artistas.append(linea_real)
                self._puntos_hover.append((ax_real, z.real, 0.0, "Raíz real", linea_real))

                if self.ax2 is not None:
                    linea_comp = self.ax2.plot(
                        [z.real], [0.0],
                        marker="o", color=GREEN, markerfacecolor=GREEN,
                        markeredgewidth=1.5, markersize=6, linestyle="none",
                        visible=mostrar, zorder=5,
                    )[0]
                    artistas.append(linea_comp)
                    self._puntos_hover.append((self.ax2, z.real, 0.0, "Raíz real", linea_comp))
            else:
                if self.ax2 is not None:
                    linea_comp = self.ax2.plot(
                        [z.real], [z.imag],
                        marker="s", color=ORANGE, markerfacecolor=ORANGE,
                        markersize=6, linestyle="none",
                        visible=mostrar, zorder=5,
                    )[0]
                    artistas.append(linea_comp)
                    self._puntos_hover.append((self.ax2, z.real, z.imag, "Raíz compleja", linea_comp))
            self.artistas_raices.append(artistas)

        self.leyenda_plano()

        self._xlim_base = ax_real.get_xlim()
        self._ylim_base = ax_real.get_ylim()
        self._xlim_base2 = self.ax2.get_xlim() if self.ax2 else None
        self._ylim_base2 = self.ax2.get_ylim() if self.ax2 else None
        self.canvas.draw_idle()

    def reset_vista(self):
        if self._xlim_base is not None:
            self.ax.set_xlim(*self._xlim_base)
            self.ax.set_ylim(*self._ylim_base)
        if self._xlim_base2 is not None and self.ax2 is not None:
            self.ax2.set_xlim(*self._xlim_base2)
            self.ax2.set_ylim(*self._ylim_base2)
        self.canvas.draw_idle()

    def _mostrar_hover(self, evento):
        if evento.inaxes is self.ax2 and self.ax2 is not None:
            self._hover_art = self._hover_art2
        else:
            self._hover_art = self._hover_art1
        super()._mostrar_hover(evento)

    def _salir(self, _evento=None):
        for artista in (self._hover_art1, self._hover_art2):
            if artista is not None:
                artista.set_visible(False)
        self.canvas.draw_idle()