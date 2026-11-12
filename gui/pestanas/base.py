"""Pestaña base: esquema de tres tarjetas, tabla, resultado y barra de estado."""

import tkinter as tk
from tkinter import ttk
import traceback

from core.errores import EntradaInvalida, ErrorNumerico, PolinomioInvalido
from gui.animacion import BarraAnimacion
from gui.estilo import BG, CARD, GREEN, INK, NAVY
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

    def __init__(self, master, app, grafico_clase=None):
        super().__init__(master, bg=BG)
        self.app = app
        self.fuentes = app.fuentes
        self._vars_entrada = []
        self._primer_entry = None
        self._resultado_visible = False
        self._banner_visible = False
        self._pasos_animados = []

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=27, uniform="tarjetas")
        self.grid_columnconfigure(1, weight=41, uniform="tarjetas")
        self.grid_columnconfigure(2, weight=32, uniform="tarjetas")

        if grafico_clase is not None:
            self.grafico_clase = grafico_clase

        self._construir_esquema()
        self.construir_entrada(self.entrada)
        self._crear_botones(self.entrada)
        self.tabla.al_elegir_paso = self._elegir_paso

        self._bind_enter(self)
        self.after_idle(self._grafico_inicial)

    # ------------------------------------------------------------------ estructura
    def _construir_esquema(self):
        self.card_entrada = Card(self, r=16, fill=CARD, outer=BG)
        self.card_entrada.grid(row=0, column=0, sticky="nsew", padx=(0, 5), pady=(6, 0))
        self.entrada = tk.Frame(self.card_entrada.inner, bg=CARD)
        self._encabezado(self.card_entrada.inner, "sparkle", "Entrada").pack(
            anchor="w", pady=(0, 3)
        )
        self.entrada.pack(fill="both", expand=True)

        self.card_centro = Card(self, r=16, fill=CARD, outer=BG)
        self.card_centro.grid(row=0, column=1, sticky="nsew", padx=5, pady=(6, 0))
        centro = self.card_centro.inner
        self._encabezado(centro, "table", self.titulo_tabla, self.subtitulo_tabla).pack(
            anchor="w", pady=(0, 6)
        )

        # El pie se reserva abajo antes que la tabla para que los avisos y el
        # resultado no desplacen la tabla al aparecer.
        self.pie = tk.Frame(centro, bg=CARD)
        self.pie.pack(side="bottom", fill="x")
        self.banner = Banner(self.pie, self.fuentes)
        self.resultado = TarjetaResultado(self.pie, self.fuentes)

        self.tabla = TablaPasos(centro, self.fuentes)
        self.tabla.pack(fill="both", expand=True)

        self.card_grafico = Card(self, r=16, fill=CARD, outer=BG, deco="blobs")
        self.card_grafico.grid(row=0, column=2, sticky="nsew", padx=(5, 0), pady=(6, 0))
        derecho = self.card_grafico.inner
        encabezado = self._encabezado(derecho, self.icono_derecha, self.titulo_derecha)
        encabezado.pack(anchor="w", fill="x", pady=(0, 3))
        if self.usa_grafico:
            self._crear_boton_reset(encabezado)
        self.animacion_host = tk.Frame(derecho, bg=CARD)
        self.animacion_host.pack(side="bottom", fill="x", pady=(6, 0))
        self.barra = BarraAnimacion(
            self.animacion_host,
            self.fuentes,
            al_cambiar=self._paso_animacion,
        )
        self.barra.pack(fill="x")
        self.derecho_host = tk.Frame(derecho, bg=CARD)
        self.derecho_host.pack(fill="both", expand=True)
        self._crear_derecha(self.derecho_host)

    def _crear_derecha(self, host):
        """Crea el contenido de la tarjeta derecha (gráfico por defecto)."""
        clase = self.grafico_clase
        self.grafico = clase(host, self)
        self.grafico.pack(fill="both", expand=True)

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
            height=28,
        )
        self.boton_reset.configure(width=124)
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
        contenedor.pack(fill="x", pady=(7, 0))
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
                wraplength=230,
            ).pack(fill="x", pady=(3, 0))
        self._vars_entrada.append(variable)
        if self._primer_entry is None:
            self._primer_entry = entrada
        return entrada

    def combo(self, parent, etiqueta, variable, valores, on_change=None):
        contenedor = tk.Frame(parent, bg=CARD)
        contenedor.pack(fill="x", pady=(7, 0))
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
        contenedor.pack(fill="x", pady=(7, 0))
        tk.Label(
            contenedor,
            text=etiqueta,
            font=self.fuentes.label,
            bg=CARD,
            fg="#17303F",
            anchor="w",
        ).pack(fill="x", pady=(0, 4))
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
        fila = tk.Frame(parent, bg=CARD)
        fila.pack(side="bottom", fill="x", pady=(14, 0))
        fila.columnconfigure(0, weight=5, uniform="botones")
        fila.columnconfigure(1, weight=4, uniform="botones")
        RButton(
            fila,
            "Calcular",
            self.calcular,
            GREEN,
            "white",
            "#25804B",
            icon=self.app.iconos["play"],
            font=self.fuentes.button,
        ).grid(row=0, column=0, sticky="ew", padx=(0, 8))
        RButton(
            fila,
            "Limpiar",
            self.limpiar,
            "#F8FAF9",
            "#17303F",
            "#EDF2EF",
            outline="#CFDAD4",
            icon=self.app.iconos["trash"],
            font=self.fuentes.button,
        ).grid(row=0, column=1, sticky="ew")

    # ------------------------------------------------------------------ cálculo y errores
    def calcular(self, evento=None):
        """Único punto que atrapa errores de entrada, cálculo e internos."""
        self.barra.detener()
        self._pasos_animados = []
        self.tabla.limpiar()
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
            self.barra.configurar([])
            self._ocultar_tarjeta()
            self.tabla.limpiar()
            self._limpiar_grafico("Ocurrió un error interno.")
            self._estado("error", "Error interno. Revisá la consola.")
            return

        try:
            self._mostrar_avisos(resultado)
            self._mostrar_resultado(resultado)
            self._estado(self._tipo_estado(resultado), self._mensaje_exito(resultado))
        except Exception:
            traceback.print_exc()
            self._estado("error", "Error interno al mostrar el resultado. Revisá la consola.")

    def _manejar_error(self, exc, tono):
        self._pasos_animados = []
        self.barra.configurar([])
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

    def _mostrar_tarjeta(self):
        if not self._resultado_visible:
            self.resultado.pack(fill="x", pady=(12, 0))
            self._resultado_visible = True

    def _ocultar_tarjeta(self):
        if self._resultado_visible:
            self.resultado.pack_forget()
            self._resultado_visible = False

    def _ocultar_banner(self):
        if self._banner_visible:
            self.banner.pack_forget()
            self._banner_visible = False

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
        """Carga los pasos en la barra común; por defecto muestra el último."""
        self._pasos_animados = list(pasos or [])
        self.barra.configurar(self._pasos_animados, inicial=inicial)

    def _paso_animacion(self, indice):
        try:
            self._aplicar_paso(indice)
        except Exception:
            # Una animación nunca debe tumbar el resultado ya calculado.
            traceback.print_exc()

    def _aplicar_paso(self, indice):
        """Comportamiento común: resaltar la fila del paso en la tabla."""
        if 0 <= indice < len(self._pasos_animados):
            self.tabla.seleccionar(indice)
        else:
            self.tabla.quitar_seleccion()

    def _elegir_paso(self, indice):
        if self._pasos_animados and 0 <= indice < len(self._pasos_animados):
            self.barra.controlador.ir_a(indice)
            self.barra._actualizar()

    def _limpiar_derecha(self, mensaje):
        """Limpia el gráfico o la tabla de Ruffini, según la pestaña."""
        contenido = getattr(self, "grafico", None) or getattr(self, "ruffini", None)
        if contenido is not None:
            contenido.limpiar(mensaje)

    def _limpiar_grafico(self, mensaje):
        self._limpiar_derecha(mensaje)

    def _redibujar_derecha(self):
        contenido = getattr(self, "grafico", None) or getattr(self, "ruffini", None)
        if contenido is not None:
            contenido.redibujar()

    def _grafico_inicial(self):
        self._limpiar_derecha("Ingresá los datos y presioná Calcular.")

    def _estado(self, tipo, mensaje):
        self.app.estado(tipo, mensaje)

    # ------------------------------------------------------------------ limpiar / teclado
    def limpiar(self, evento=None):
        self.barra.detener()
        self._pasos_animados = []
        self.barra.configurar([])
        for variable in self._vars_entrada:
            variable.set("")
        self.tabla.limpiar()
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
        self.after_idle(self.barra.redibujar)

    def al_ocultar(self):
        """Cancela la reproducción pendiente al cambiar de pestaña."""
        self.barra.detener()

    def cerrar(self):
        self.barra.cerrar()
        contenido = getattr(self, "grafico", None) or getattr(self, "ruffini", None)
        if contenido is not None:
            contenido.cerrar()
