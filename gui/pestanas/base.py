"""Pestaña base: esquema de tres tarjetas, tabla, resultado y barra de estado."""

import tkinter as tk
from tkinter import ttk
import traceback

from core.errores import EntradaInvalida, ErrorNumerico, PolinomioInvalido
from gui.estilo import BG, CARD, GREEN, INK, NAVY
from gui.formato import con_superindices, formatear_polinomio
from gui.graficos import GraficoSimple
from gui.widgets import (
    Banner,
    Card,
    RButton,
    REntry,
    Seg,
    TablaPasos,
    TarjetaResultado,
)


class PestanaBase(tk.Frame):
    """Esqueleto común a las seis pestañas.

    Las subclases implementan ``construir_entrada``, ``_calcular``,
    ``_mostrar_resultado`` y, si hace falta, ``_mostrar_pasos_error``.
    """

    titulo_tabla = "Pasos"
    subtitulo_tabla = "(campo 'pasos' del Resultado)"
    grafico_clase = GraficoSimple
    titulo_derecha = "Gráfico"
    icono_derecha = "chart"
    usa_grafico = True
    usa_tabla = True
    usa_animacion = True
    pie_en_grafico = False
    tarjeta_polinomio = False

    def __init__(self, master, app, grafico_clase=None):
        super().__init__(master, bg=BG)
        self.app = app
        self.fuentes = app.fuentes
        self._vars_entrada = []
        self._primer_entry = None
        self._resultado_visible = False
        self._banner_visible = False
        self._pasos_animados = []
        self._anim_job = None
        self._scroll_centro_visible = False
        self._scroll_centro_activo = False
        self.tabla = None

        self.grid_rowconfigure(0, weight=1)
        # La entrada mantiene un ancho cómodo y el espacio extra va al gráfico.
        self.grid_columnconfigure(0, minsize=370, weight=0)
        self.grid_columnconfigure(1, weight=38)
        self.grid_columnconfigure(2, weight=42)

        if grafico_clase is not None:
            self.grafico_clase = grafico_clase

        self._construir_esquema()
        self.construir_entrada(self.entrada)
        self._crear_botones(self.entrada)

        self._bind_enter(self)
        self.after_idle(self._grafico_inicial)

    # ------------------------------------------------------------------ estructura
    def _construir_esquema(self):
        self.card_entrada = Card(self, r=16, fill=CARD, outer=BG, autoheight=True)
        self.card_entrada.grid(row=0, column=0, sticky="new", padx=(0, 5), pady=(6, 0))
        self.entrada = tk.Frame(self.card_entrada.inner, bg=CARD)
        self._encabezado(self.card_entrada.inner, "sparkle", "Entrada").pack(
            anchor="w", pady=(0, 3)
        )
        self.entrada.pack(fill="both", expand=True)

        if self.usa_tabla:
            # La columna central puede superar el alto de la ventana (por
            # ejemplo, una sucesión de Sturm larga). Se envuelve en un canvas
            # para que aparezca una barra vertical solo cuando haga falta.
            self.centro_host = tk.Frame(self, bg=BG)
            self.centro_host.grid(row=0, column=1, sticky="nsew", padx=5, pady=(6, 0))
            self.centro_host.grid_rowconfigure(0, weight=1)
            self.centro_host.grid_columnconfigure(0, weight=1)
            self.centro_canvas = tk.Canvas(
                self.centro_host, bg=BG, highlightthickness=0, bd=0
            )
            self.centro_canvas.grid(row=0, column=0, sticky="nsew")
            self.marco_scroll_centro = tk.Frame(
                self.centro_host, bg=BG, width=8
            )
            self.marco_scroll_centro.pack_propagate(False)
            self.scroll_centro = ttk.Scrollbar(
                self.marco_scroll_centro,
                orient="vertical",
                command=self.centro_canvas.yview,
                style="Vertical.TScrollbar",
            )
            self.scroll_centro.pack(fill="both", expand=True)
            self.marco_scroll_centro.grid(row=0, column=1, sticky="ns")
            self.marco_scroll_centro.grid_remove()
            self.centro_canvas.configure(yscrollcommand=self._scroll_centro_yview)

            self.card_centro = Card(
                self.centro_canvas, r=16, fill=CARD, outer=BG, autoheight=True
            )
            self._centro_win = self.centro_canvas.create_window(
                0, 0, window=self.card_centro, anchor="nw"
            )
            self.centro_canvas.bind(
                "<Configure>", self._actualizar_scroll_centro, add="+"
            )
            self.card_centro.bind(
                "<Configure>", self._actualizar_scroll_centro, add="+"
            )
            centro = self.card_centro.inner
            self._encabezado(
                centro, "table", self.titulo_tabla, self.subtitulo_tabla
            ).pack(anchor="w", pady=(0, 6))

            # El pie se reserva abajo antes que la tabla para que los avisos y
            # el resultado no desplacen la tabla al aparecer.
            if not self.pie_en_grafico:
                self._crear_pie(centro)
            self.tabla = TablaPasos(centro, self.fuentes)
            self.tabla.pack(fill="x")
            self.tabla.al_elegir_paso = self._elegir_paso

        self.card_grafico = Card(self, r=16, fill=CARD, outer=BG)
        if self.usa_tabla:
            self.card_grafico.grid(
                row=0, column=2, sticky="nsew", padx=(5, 0), pady=(6, 0)
            )
        else:
            # Sin tabla central, la tarjeta derecha ocupa todo el ancho libre.
            self.card_grafico.grid(
                row=0,
                column=1,
                columnspan=2,
                sticky="nsew",
                padx=(5, 0),
                pady=(6, 0),
            )
        derecho = self.card_grafico.inner
        encabezado = self._encabezado(derecho, self.icono_derecha, self.titulo_derecha)
        encabezado.pack(anchor="w", fill="x", pady=(0, 3))
        if self.usa_grafico:
            self._crear_boton_reset(encabezado)

        # El resultado se reserva antes del área del gráfico para que el pack
        # no lo aplaste cuando el gráfico se expande.
        if self.pie_en_grafico or not self.usa_tabla:
            self._crear_pie(derecho)

        self.derecho_host = tk.Frame(derecho, bg=CARD)
        self.derecho_host.pack(fill="both", expand=True)
        self._crear_derecha(self.derecho_host)

    def _crear_pie(self, parent):
        """Banner de avisos y tarjeta de resultado, al pie de la tarjeta."""
        self.pie = tk.Frame(parent, bg=CARD)
        self.pie.pack(side="bottom", fill="x")
        self.banner = Banner(self.pie, self.fuentes)
        self.resultado = TarjetaResultado(self.pie, self.fuentes)

    def _crear_derecha(self, host):
        """Crea el contenido de la tarjeta derecha (gráfico por defecto)."""
        if self.tarjeta_polinomio:
            self._crear_tarjeta_polinomio(host)
        clase = self.grafico_clase
        self.grafico = clase(host, self)
        self.grafico.pack(fill="both", expand=True)

    def _crear_tarjeta_polinomio(self, host):
        """Recuadro superior con el polinomio que se está analizando."""
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

    def _mostrar_polinomio(self, coef):
        texto = con_superindices(formatear_polinomio(coef))
        self.lbl_polinomio.configure(text=f"P(x) = {texto}")
        self.card_poli.actualizar_alto()

    def _scroll_centro_yview(self, first, last):
        self.scroll_centro.set(first, last)

    def _reiniciar_scroll_centro(self):
        if hasattr(self, "centro_canvas"):
            try:
                self.centro_canvas.yview_moveto(0)
            except tk.TclError:
                pass

    def _actualizar_scroll_centro(self, *_args):
        """Ajusta el scroll de la columna central y muestra la barra si sobra alto."""
        if not hasattr(self, "centro_canvas") or not self.centro_canvas.winfo_exists():
            return
        if self._scroll_centro_activo:
            return
        self._scroll_centro_activo = True
        try:
            ancho = max(self.centro_canvas.winfo_width(), 1)
            anterior = float(
                self.centro_canvas.itemcget(self._centro_win, "width") or 0
            )
            if abs(anterior - ancho) > 1:
                self.centro_canvas.itemconfigure(self._centro_win, width=ancho)
            alto_vista = self.centro_canvas.winfo_height()
            alto = max(
                self.card_centro.winfo_height(),
                self.card_centro.winfo_reqheight(),
                1,
            )
            self.centro_canvas.configure(scrollregion=(0, 0, ancho, alto))
            visible = alto_vista > 1 and alto > alto_vista + 1
            if visible != self._scroll_centro_visible:
                self._scroll_centro_visible = visible
                if visible:
                    self.marco_scroll_centro.grid()
                else:
                    self.marco_scroll_centro.grid_remove()
                    self.centro_canvas.yview_moveto(0)
                # Al aparecer o desaparecer la barra cambia el ancho disponible.
                self.after(50, self._actualizar_scroll_centro)
        finally:
            self._scroll_centro_activo = False

    def _crear_boton_reset(self, encabezado):
        """Botón compacto para volver a la vista inicial del gráfico."""
        self.boton_reset = RButton(
            encabezado,
            "Restablecer vista",
            self._reset_vista,
            "#F8FAF9",
            INK,
            "#EDF2EF",
            outline="#CFDAD4",
            font=self.fuentes.small,
            height=30,
        )
        self.boton_reset.configure(width=152)
        self.boton_reset.pack(side="right", padx=(4, 0))

    def _reset_vista(self):
        grafico = getattr(self, "grafico", None)
        if grafico is not None:
            grafico.reset_vista()

    def _encabezado(self, parent, icono, texto, subtitulo=None):
        fila = tk.Frame(parent, bg=CARD)
        tk.Label(fila, image=self.app.iconos[icono], bg=CARD).pack(side="left")
        tk.Label(fila, text=texto, font=self.fuentes.h2, bg=CARD, fg=NAVY).pack(
            side="left", padx=(8, 0)
        )
        if subtitulo:
            tk.Label(
                fila,
                text=subtitulo,
                font=self.fuentes.small,
                bg=CARD,
                fg="#6A7B86",
            ).pack(side="left", padx=(8, 0), pady=(4, 0))
        return fila

    # ------------------------------------------------------------------ helpers de entrada
    def campo(self, parent, etiqueta, variable, hint=None):
        contenedor = tk.Frame(parent, bg=CARD)
        contenedor.pack(fill="x", pady=(5, 0))
        return self._campo_interior(contenedor, etiqueta, variable, hint)

    def _campo_interior(self, contenedor, etiqueta, variable, hint=None):
        """Etiqueta, entrada y ayuda dentro de un contenedor ya ubicado."""
        tk.Label(
            contenedor,
            text=etiqueta,
            font=self.fuentes.label,
            bg=CARD,
            fg="#17303F",
            anchor="w",
        ).pack(fill="x", pady=(0, 3))
        entrada = REntry(contenedor, variable, self.fuentes.entry)
        entrada.pack(fill="x")
        if hint:
            tk.Label(
                contenedor,
                text=hint,
                font=self.fuentes.hint,
                bg=CARD,
                fg="#6A7B86",
                anchor="w",
                justify="left",
                wraplength=300,
            ).pack(fill="x", pady=(3, 0))
        self._vars_entrada.append(variable)
        if self._primer_entry is None:
            self._primer_entry = entrada
        return entrada

    def fila_campos(self, parent, constructores, gap=10):
        """Ubica dos o más campos en una fila para ahorrar alto."""
        fila = tk.Frame(parent, bg=CARD)
        fila.pack(fill="x", pady=(5, 0))
        for i, constructor in enumerate(constructores):
            columna = tk.Frame(fila, bg=CARD)
            columna.grid(
                row=0,
                column=i,
                sticky="new",
                padx=(0, gap) if i < len(constructores) - 1 else 0,
            )
            fila.columnconfigure(i, weight=1, uniform="fila_campos")
            constructor(columna)
        return fila

    def combo(self, parent, etiqueta, variable, valores, on_change=None):
        contenedor = tk.Frame(parent, bg=CARD)
        contenedor.pack(fill="x", pady=(5, 0))
        tk.Label(
            contenedor,
            text=etiqueta,
            font=self.fuentes.label,
            bg=CARD,
            fg="#17303F",
            anchor="w",
        ).pack(fill="x", pady=(0, 3))
        caja = ttk.Combobox(
            contenedor,
            textvariable=variable,
            values=list(valores),
            state="readonly",
            style="Calc.TCombobox",
            font=self.fuentes.normal,
        )
        caja.pack(fill="x")
        if on_change:
            caja.bind("<<ComboboxSelected>>", lambda _: on_change())
        return caja

    def segmentado(self, parent, etiqueta, variable, opciones, on_change=None):
        contenedor = tk.Frame(parent, bg=CARD)
        contenedor.pack(fill="x", pady=(5, 0))
        tk.Label(
            contenedor,
            text=etiqueta,
            font=self.fuentes.label,
            bg=CARD,
            fg="#17303F",
            anchor="w",
        ).pack(fill="x", pady=(0, 3))
        selector = Seg(
            contenedor,
            opciones,
            variable,
            self.fuentes.normal,
            on_change=on_change,
        )
        selector.pack(fill="x")
        return selector

    def _crear_botones(self, parent):
        # Van inmediatamente después de los campos, sin empujarlos al fondo.
        fila = tk.Frame(parent, bg=CARD)
        fila.pack(fill="x", pady=(12, 0))
        fila.columnconfigure(0, weight=5, uniform="botones")
        fila.columnconfigure(1, weight=4, uniform="botones")
        calcular = RButton(
            fila,
            "Calcular",
            self.calcular,
            GREEN,
            "white",
            "#25804B",
            icon=self.app.iconos["play"],
            font=self.fuentes.button,
        )
        calcular.configure(width=160)
        calcular.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        limpiar = RButton(
            fila,
            "Limpiar",
            self.limpiar,
            "#F8FAF9",
            "#17303F",
            "#EDF2EF",
            outline="#CFDAD4",
            icon=self.app.iconos["trash"],
            font=self.fuentes.button,
        )
        limpiar.configure(width=150)
        limpiar.grid(row=0, column=1, sticky="ew")

    # ------------------------------------------------------------------ cálculo y errores
    def calcular(self, evento=None):
        """Único punto que atrapa errores de entrada, cálculo e internos."""
        if self._anim_job is not None:
            self.after_cancel(self._anim_job)
            self._anim_job = None
        self._pasos_animados = []
        if self.tabla is not None:
            self.tabla.limpiar()
        self._reiniciar_scroll_centro()
        self._ocultar_tarjeta()
        self._ocultar_banner()
        try:
            resultado = self._calcular()
        except (EntradaInvalida, PolinomioInvalido) as exc:
            self._manejar_error(exc, "advertencia")
            return
        except ErrorNumerico as exc:
            self._manejar_error(exc, "error")
            return
        except Exception:
            traceback.print_exc()
            self._pasos_animados = []
            self._ocultar_tarjeta()
            if self.tabla is not None:
                self.tabla.limpiar()
            self._limpiar_grafico("Ocurrió un error interno.")
            self._estado("error", "Error interno. Revisá la consola.")
            return

        try:
            self._mostrar_avisos(resultado)
            self._mostrar_resultado(resultado)
            self._estado(self._tipo_estado(resultado), self._mensaje_exito(resultado))
            self._actualizar_alto_paneles()
        except Exception:
            traceback.print_exc()
            self._estado("error", "Error interno al mostrar el resultado. Revisá la consola.")

    def _manejar_error(self, exc, tono):
        self._pasos_animados = []
        if getattr(exc, "pasos", None):
            self._mostrar_pasos_error(exc.pasos)
        self._ocultar_tarjeta()
        self._limpiar_grafico("No hay gráfico para esta entrada.")
        mensaje = str(exc)
        if getattr(exc, "pasos", None):
            mensaje += " Se muestran los pasos calculados hasta el error."
        self._mostrar_banner(mensaje, tono)
        if tono == "advertencia":
            self._estado("advertencia", f"Atención: {exc}")
        else:
            self._estado("error", f"Error: {exc}")

    def _mostrar_pasos_error(self, pasos):
        """Las pestañas que pueden fallar a mitad de camino muestran lo hecho."""
        return None

    # ------------------------------------------------------------------ avisos y resultado
    def _mostrar_avisos(self, resultado):
        textos = list(resultado.avisos)
        diagnostico = resultado.diagnostico or {}
        ciclo = diagnostico.get("ciclo")
        if ciclo:
            desde, hasta, periodo = ciclo
            textos.append(
                f"Ciclo detectado entre las filas {desde + 1} y {hasta + 1} "
                f"(período {periodo})."
            )
        if diagnostico.get("creciente"):
            textos.append("El error |dx| creció en las últimas iteraciones.")
        razon = diagnostico.get("ratio_lineal")
        if razon is not None:
            textos.append(
                f"Convergencia lineal (posible raíz múltiple): razón ≈ {razon:.3f}."
            )
        if not resultado.convergio and not textos:
            textos.append("El método no alcanzó la tolerancia pedida.")
        textos = list(dict.fromkeys(t for t in textos if t))
        if textos:
            self._mostrar_banner(" · ".join(textos), "advertencia")

    def _mostrar_banner(self, texto, tono="advertencia"):
        self.banner.mostrar(texto, tono)
        if not self._banner_visible:
            self.banner.pack(fill="x", pady=(10, 0))
            self._banner_visible = True
        self.banner.actualizar_alto()
        self._actualizar_alto_paneles()

    def _mostrar_tarjeta(self):
        if not self._resultado_visible:
            self.resultado.pack(fill="x", pady=(12, 0))
            self._resultado_visible = True
        self.resultado.actualizar_alto()
        self._actualizar_alto_paneles()

    def _ocultar_tarjeta(self):
        if self._resultado_visible:
            self.resultado.pack_forget()
            self._resultado_visible = False
            self._actualizar_alto_paneles()

    def _ocultar_banner(self):
        if self._banner_visible:
            self.banner.pack_forget()
            self._banner_visible = False
            self._actualizar_alto_paneles()

    def _actualizar_alto_paneles(self):
        for nombre in ("card_entrada", "card_centro", "card_grafico"):
            card = getattr(self, nombre, None)
            if card is not None:
                card.actualizar_alto()

    def _tipo_estado(self, resultado):
        diagnostico = resultado.diagnostico or {}
        alerta = (
            bool(resultado.avisos)
            or not resultado.convergio
            or bool(diagnostico.get("ciclo"))
            or bool(diagnostico.get("creciente"))
            or diagnostico.get("ratio_lineal") is not None
        )
        return "advertencia" if alerta else "ok"

    def _mensaje_exito(self, resultado):
        return "Cálculo completado."

    def _mostrar_resultado(self, resultado):
        raise NotImplementedError

    def _calcular(self):
        raise NotImplementedError

    # ------------------------------------------------------------------ animación
    def _animar(self, pasos, inicial=None):
        """Inicia la animación automática paso a paso al presionar Calcular."""
        self._pasos_animados = list(pasos or [])

        if self._anim_job is not None:
            self.after_cancel(self._anim_job)
            self._anim_job = None

        if not getattr(self, "usa_animacion", True) or not self._pasos_animados:
            if self.tabla is not None:
                self.tabla.quitar_seleccion()
            return

        self._anim_indice = 0
        MS_PASO = 300

        def _tick():
            if self._anim_indice < len(self._pasos_animados):
                self._aplicar_paso(self._anim_indice)
                self._anim_indice += 1
                self._anim_job = self.after(MS_PASO, _tick)
            else:
                self._anim_job = None

        _tick()

    def _aplicar_paso(self, indice):
        """Comportamiento común: resaltar la fila del paso en la tabla."""
        if self.tabla is None:
            return
        if 0 <= indice < len(self._pasos_animados):
            self.tabla.seleccionar(indice)
        else:
            self.tabla.quitar_seleccion()

    def _elegir_paso(self, indice):
        pass

    def _limpiar_grafico(self, mensaje):
        """Limpia el gráfico o la tabla de Ruffini, según la pestaña."""
        contenido = getattr(self, "grafico", None) or getattr(self, "ruffini", None)
        if contenido is not None:
            contenido.limpiar(mensaje)

    def _redibujar_derecha(self):
        contenido = getattr(self, "grafico", None) or getattr(self, "ruffini", None)
        if contenido is not None:
            contenido.redibujar()

    def _grafico_inicial(self):
        self._limpiar_grafico("Ingresá los datos y presioná Calcular.")

    def _estado(self, tipo, mensaje):
        self.app.estado(tipo, mensaje)

    # ------------------------------------------------------------------ limpiar / teclado
    def limpiar(self, evento=None):
        if self._anim_job is not None:
            self.after_cancel(self._anim_job)
            self._anim_job = None
        self._pasos_animados = []
        for variable in self._vars_entrada:
            variable.set("")
        if self.tabla is not None:
            self.tabla.limpiar()
        self._reiniciar_scroll_centro()
        self._ocultar_tarjeta()
        self._ocultar_banner()
        self._limpiar_grafico("Ingresá los datos y presioná Calcular.")
        self._estado("ok", "Listo. Ingresá los datos y presioná Calcular.")
        if self._primer_entry is not None:
            self._primer_entry.entry.focus_set()
        return "break"

    def _bind_enter(self, widget):
        for hijo in widget.winfo_children():
            if isinstance(hijo, (tk.Entry, ttk.Entry, ttk.Combobox)):
                hijo.bind("<Return>", self._al_enter)
            self._bind_enter(hijo)

    def _al_enter(self, evento=None):
        self.calcular()
        return "break"

    def al_mostrar(self):
        self.after_idle(self._redibujar_derecha)

    def al_ocultar(self):
        if self._anim_job is not None:
            self.after_cancel(self._anim_job)
            self._anim_job = None

    def cerrar(self):
        if self._anim_job is not None:
            self.after_cancel(self._anim_job)
            self._anim_job = None
        contenido = getattr(self, "grafico", None) or getattr(self, "ruffini", None)
        if contenido is not None:
            contenido.cerrar()