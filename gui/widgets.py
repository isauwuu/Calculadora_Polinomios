"""Widgets propios de la interfaz: tarjetas, campos, botones, pestañas y tablas."""

import tkinter as tk
from tkinter import ttk

from gui import imagenes
from gui.estilo import (
    AMBER,
    AMBER_B,
    AMBER_L,
    BG,
    BLUE_L,
    CARD,
    FIELD,
    FIELD_B,
    GREEN,
    GREEN_B,
    GREEN_D,
    GREEN_L,
    INK,
    LINE,
    MUTED,
    NAVY,
    ORANGE,
    RED,
    RED_B,
    RED_L,
)


class Card(tk.Canvas):
    """Tarjeta con borde redondeado y sombra suave."""

    def __init__(
        self,
        master,
        r=16,
        fill=CARD,
        outline=LINE,
        shadow=True,
        outer=BG,
        deco=None,
        pad=14,
        use_inner=True,
        autoheight=False,
    ):
        super().__init__(master, bg=outer, highlightthickness=0, bd=0)
        self.r = r
        self.fill = fill
        self.outline = outline
        self.shadow = shadow
        self.outer = outer
        self.deco = deco
        self.m = 8 if shadow else 0
        self.pad = pad + self.m
        self.autoheight = autoheight
        self._alto_auto = None
        self._alto_job = None
        self._alto_intentos = 0
        self._size = None
        self._imagen = None
        self._ventanas = []
        self.inner = None
        if use_inner:
            self.inner = tk.Frame(self, bg=fill)
            self.add(
                self.inner,
                lambda w, h: (
                    self.pad,
                    self.pad - 4,
                    max(w - 2 * self.pad, 1),
                    max(h - 2 * self.pad + 4, 1),
                ),
            )
            if autoheight:
                self.configure(height=1)
                self.inner.bind("<Configure>", self._al_configurar_inner, add="+")
        self.bind("<Configure>", self._al_configurar)

    def add(self, frame, boxfn):
        self._ventanas.append((self.create_window(0, 0, window=frame, anchor="nw"), boxfn))

    def _al_configurar(self, evento):
        if evento.width < 2 or evento.height < 2:
            return
        if (evento.width, evento.height) == self._size:
            return
        self._size = (evento.width, evento.height)
        self._pintar(evento.width, evento.height)

    def _al_configurar_inner(self, _evento=None):
        if not self.autoheight or self.inner is None:
            return
        requerido = self.inner.winfo_reqheight()
        alto = max(requerido + 2 * self.pad - 4, 36)
        if self._alto_auto is None or abs(alto - self._alto_auto) >= 2:
            self._alto_auto = alto
            self.configure(height=alto)

    def actualizar_alto(self):
        if not self.autoheight:
            return
        self._al_configurar_inner()
        self._alto_intentos = 8
        self._programar_alto()

    def _programar_alto(self):
        if self._alto_job is not None:
            try:
                self.after_cancel(self._alto_job)
            except tk.TclError:
                pass
        try:
            self._alto_job = self.after(40, self._revisar_alto)
        except tk.TclError:
            self._alto_job = None

    def _revisar_alto(self):
        self._alto_job = None
        if not self.winfo_exists():
            return
        anterior = self._alto_auto
        self._al_configurar_inner()
        if self._alto_auto != anterior:
            self._alto_intentos = max(self._alto_intentos, 4)
        self._alto_intentos -= 1
        if self._alto_intentos > 0:
            self._programar_alto()

    def _pintar(self, w, h):
        pil = imagenes.rounded_image(
            w, h, self.r, self.fill, self.outline, 1, self.m, self.shadow, self.outer, self.deco
        )
        self._imagen = imagenes.photo(pil)
        self.delete("fondo")
        self.create_image(0, 0, image=self._imagen, anchor="nw", tags="fondo")
        self.tag_lower("fondo")
        for ventana, boxfn in self._ventanas:
            x, y, ancho, alto = boxfn(w, h)
            self.coords(ventana, x, y)
            self.itemconfigure(ventana, width=max(ancho, 1), height=max(alto, 1))

    def set_colors(self, fill, outline=None, deco=None):
        self.fill = fill
        self.outline = outline
        self.deco = deco
        if self.inner is not None:
            self.inner.configure(bg=fill)
        if self._size is not None:
            self._pintar(*self._size)

    def redibujar(self):
        if self._size is not None:
            self._pintar(*self._size)


class REntry(tk.Canvas):
    """Campo de texto con borde redondeado y foco verde."""

    def __init__(self, master, var, font, bg=CARD, height=40):
        super().__init__(master, height=height, bg=bg, highlightthickness=0, bd=0, width=1)
        self.bgc = bg
        self.foco = False
        self._size = None
        self.entry = tk.Entry(
            self, textvariable=var, font=font, relief="flat", bd=0, bg=FIELD, fg=INK,
            insertbackground=INK, highlightthickness=0, selectbackground="#CFE3D8",
            selectforeground=INK,
        )
        self._ventana = self.create_window(13, height // 2, window=self.entry, anchor="w")
        self.bind("<Configure>", self._al_configurar)
        self.entry.bind("<FocusIn>", lambda _: self._set_foco(True))
        self.entry.bind("<FocusOut>", lambda _: self._set_foco(False))

    def _al_configurar(self, evento):
        self._size = (evento.width, evento.height)
        self._dibujar()

    def _set_foco(self, valor):
        self.foco = valor
        self._dibujar()

    def _dibujar(self):
        if not self._size:
            return
        w, h = self._size
        pil = imagenes.rounded_image(
            w, h, 11, FIELD, GREEN if self.foco else FIELD_B, 2 if self.foco else 1,
            0, False, self.bgc,
        )
        self._imagen = imagenes.photo(pil)
        self.delete("fondo")
        self.create_image(0, 0, image=self._imagen, anchor="nw", tags="fondo")
        self.tag_lower("fondo")
        self.itemconfigure(self._ventana, width=max(w - 28, 10))


class RButton(tk.Canvas):
    """Botón redondeado con ícono opcional y efecto hover."""

    def __init__(self, master, text, command, fill, fg, hover, outline=None, icon=None, font=None, bg=CARD, height=44):
        super().__init__(master, height=height, bg=bg, highlightthickness=0, bd=0, cursor="hand2")
        self.t = text
        self.cmd = command
        self.fill = fill
        self.fg = fg
        self.hover = hover
        self.outline = outline
        self.icon = icon
        self.font = font
        self.bgc = bg
        self._size = None
        self._hov = False
        self._imagen = None
        self.habilitado = True
        self.bind("<Configure>", self._al_configurar)
        self.bind("<Enter>", lambda _: self._hover(True))
        self.bind("<Leave>", lambda _: self._hover(False))
        self.bind("<ButtonRelease-1>", self._click)

    def _al_configurar(self, evento):
        self._size = (evento.width, evento.height)
        self._dibujar()

    def _hover(self, valor):
        self._hov = valor
        self._dibujar()

    def _click(self, _evento=None):
        if self.cmd and self.habilitado:
            self.cmd()

    def set_habilitado(self, valor):
        self.habilitado = bool(valor)
        try:
            self.configure(cursor="hand2" if self.habilitado else "arrow")
        except tk.TclError:
            pass
        self._dibujar()

    def set_texto(self, texto):
        self.t = texto
        self._dibujar()

    def _dibujar(self):
        if not self._size:
            return
        w, h = self._size
        color = self.hover if (self._hov and self.habilitado) else self.fill
        pil = imagenes.rounded_image(w, h, 12, color, self.outline, 1, 0, False, self.bgc)
        self._imagen = imagenes.photo(pil)
        self.delete("all")
        self.create_image(0, 0, image=self._imagen, anchor="nw")
        ancho_icono = self.icon.width() if self.icon else 0
        gap = 8 if self.icon else 0
        texto = self.t
        total = ancho_icono + gap + self.font.measure(texto)
        x0 = (w - total) / 2
        if self.icon:
            self.create_image(x0, h / 2, image=self.icon, anchor="w")
        self.create_text(
            x0 + ancho_icono + gap, h / 2, text=texto, anchor="w", font=self.font,
            fill=self.fg if self.habilitado else "#93A29B",
        )


class Seg(tk.Canvas):
    """Selector segmentado con íconos de radio."""

    def __init__(self, master, options, var, font, bg=CARD, height=40, on_change=None):
        super().__init__(master, height=height, bg=bg, highlightthickness=0, bd=0, cursor="hand2")
        self.opts = list(options)
        self.var = var
        self.font = font
        self.bgc = bg
        self._size = None
        self.cb = on_change
        self.on = imagenes.photo(imagenes.icon_image("radio_on", 16))
        self.off = imagenes.photo(imagenes.icon_image("radio_off", 16))
        self._imgs = []
        self.bind("<Configure>", self._al_configurar)
        self.bind("<ButtonRelease-1>", self._click)
        self.var.trace_add("write", lambda *_: self._dibujar())

    def _al_configurar(self, evento):
        self._size = (evento.width, evento.height)
        self._dibujar()

    def _bounds(self):
        w, h = self._size
        n = len(self.opts)
        gap = 7
        base = [self.font.measure(o) + 36 for o in self.opts]
        disponible = max(w - gap * (n - 1), n * 20)
        total = sum(base) or 1
        if total <= disponible:
            extra = (disponible - total) / n
            anchos = [b + extra for b in base]
        else:
            factor = disponible / total
            anchos = [b * factor for b in base]
        resultado = []
        x = 0
        for ancho in anchos:
            resultado.append((x, ancho))
            x += ancho + gap
        return resultado

    def _click(self, evento):
        for i, (x, ancho) in enumerate(self._bounds()):
            if x <= evento.x <= x + ancho:
                self.var.set(self.opts[i])
                self._dibujar()
                if self.cb:
                    self.cb()
                return

    def _dibujar(self):
        if not self._size:
            return
        w, h = self._size
        self.delete("all")
        self._imgs = []
        for i, opcion in enumerate(self.opts):
            seleccionada = self.var.get() == opcion
            x, ancho = self._bounds()[i]
            pil = imagenes.rounded_image(
                ancho, h, 11, NAVY if seleccionada else FIELD,
                None if seleccionada else FIELD_B, 1, 0, False, self.bgc
            )
            img = imagenes.photo(pil)
            self._imgs.append(img)
            self.create_image(x, 0, image=img, anchor="nw")
            self.create_image(x + 13, h / 2, image=self.on if seleccionada else self.off, anchor="w")
            self.create_text(
                x + 34, h / 2, text=opcion, anchor="w", font=self.font,
                fill="white" if seleccionada else INK,
            )


class Pill(tk.Canvas):
    """Etiqueta compacta con fondo redondeado (para avisos breves)."""

    def __init__(self, master, text, icon, font, fill, outline, fg, bg=CARD, height=34):
        self.font = font
        ancho = icon.width() + 8 + font.measure(text) + 32
        super().__init__(master, width=ancho, height=height, bg=bg, highlightthickness=0, bd=0)
        self._imagen = imagenes.photo(imagenes.rounded_image(ancho, height, 11, fill, outline, 1, 0, False, bg))
        self.create_image(0, 0, image=self._imagen, anchor="nw")
        self.create_image(14, height / 2, image=icon, anchor="w")
        self.create_text(14 + icon.width() + 8, height / 2, text=text, anchor="w", font=font, fill=fg)


class TabBar(tk.Frame):
    """Barra de seis pestañas con círculo numerado y subrayado verde."""

    def __init__(self, master, labels, font, on_select):
        super().__init__(master, bg=BG)
        self.cvs = []
        self.on_select = on_select
        self.labels = list(labels)
        self.font = font
        self.sel = 0
        self._imgs = []
        for i, label in enumerate(self.labels):
            ancho = font.measure(label) + 66
            cv = tk.Canvas(self, width=ancho, height=48, bg=BG, highlightthickness=0, bd=0, cursor="hand2")
            cv.grid(row=0, column=i, padx=(0, 7))
            cv.bind("<ButtonRelease-1>", lambda _, i=i: self.select(i))
            self.cvs.append((cv, ancho))
        self.select(0, fire=False)

    def select(self, i, fire=True):
        self.sel = i
        self._imgs = []
        for k, (cv, ancho) in enumerate(self.cvs):
            seleccionada = k == i
            img = imagenes.photo(imagenes.tab_image(ancho, 48, seleccionada))
            self._imgs.append(img)
            cv.delete("all")
            cv.create_image(0, 0, image=img, anchor="nw")
            cv.create_text(26, 23, text=str(k + 1), font=self.font, fill=NAVY if seleccionada else GREEN_D)
            cv.create_text(44, 23, text=self.labels[k], anchor="w", font=self.font, fill="white" if seleccionada else INK)
        if fire:
            self.on_select(i)


class TablaPasos(tk.Frame):
    """Tabla genérica con alto según las filas y barras solo si hacen falta."""

    def __init__(self, master, fuentes, height=8, max_filas=12):
        super().__init__(master, bg=CARD)
        self.fuentes = fuentes
        self._columnas = []
        self.max_filas = max_filas
        self._barra_pendiente = None
        self._v_visible = False
        self._h_visible = False
        self.tree = ttk.Treeview(
            self, show="headings", style="Calc.Treeview", selectmode="browse",
            height=min(height, max_filas),
        )
        self.marco_v = tk.Frame(self, bg=CARD, width=8)
        self.marco_v.pack_propagate(False)
        self.marco_h = tk.Frame(self, bg=CARD, height=8)
        self.marco_h.pack_propagate(False)
        self.vscroll = ttk.Scrollbar(self.marco_v, orient="vertical", command=self.tree.yview, style="Vertical.TScrollbar")
        self.vscroll.pack(fill="both", expand=True)
        self.hscroll = ttk.Scrollbar(self.marco_h, orient="horizontal", command=self.tree.xview, style="Horizontal.TScrollbar")
        self.hscroll.pack(fill="both", expand=True)
        self.scroll = self.vscroll
        self.tree.configure(yscrollcommand=self._actualizar_yview, xscrollcommand=self._actualizar_xview)
        self.tree.grid(row=0, column=0, sticky="nsew")
        self.marco_v.grid(row=0, column=1, sticky="ns")
        self.marco_h.grid(row=1, column=0, sticky="ew")
        self.marco_v.grid_remove()
        self.marco_h.grid_remove()
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        self.tree.tag_configure("odd", background="#F5F9F7")
        self.tree.tag_configure("raiz", background=GREEN_L, foreground=GREEN_D)
        self.tree.tag_configure("final", background=GREEN_L, foreground=GREEN_D, font=fuentes.mono_bold)
        self.tree.tag_configure("roja", background=RED_L, foreground=RED)
        self.tree.tag_configure("alerta", background=AMBER_L, foreground=AMBER)
        self.tree.tag_configure("perturbado", background=AMBER_L, foreground=AMBER)
        self.tree.tag_configure("cero", background=AMBER_L, foreground=AMBER)
        self.tree.tag_configure("resto", background=BLUE_L, foreground=NAVY)
        self.al_elegir_paso = None
        self.tree.bind("<ButtonRelease-1>", self._al_clic)
        self.tree.bind("<KeyRelease>", self._al_tecla)
        self.tree.bind("<Configure>", lambda _: self._programar_barras(), add="+")

    def configurar(self, columnas, estirar=True):
        self.limpiar()
        self._columnas = list(columnas)
        claves = [c[0] for c in self._columnas]
        self.tree["columns"] = claves
        for clave, titulo, ancho, alineacion in self._columnas:
            self.tree.heading(clave, text=titulo, anchor="center")
            self.tree.column(clave, width=ancho, minwidth=ancho if not estirar else max(40, ancho // 2), anchor=alineacion, stretch=estirar)

    def cargar(self, filas, tags=None):
        self.limpiar()
        if not self._columnas:
            return
        for i, fila in enumerate(filas):
            valores = [fila.get(c[0], "") for c in self._columnas]
            if tags is not None:
                etiquetas = tags[i]
            else:
                etiquetas = ("odd",) if i % 2 else ()
            self.tree.insert("", "end", values=valores, tags=etiquetas)
        self.tree.configure(height=max(1, min(len(filas), self.max_filas)))
        hijos = self.tree.get_children()
        if hijos:
            self.tree.yview_moveto(0)
            self.tree.xview_moveto(0)
        self._programar_barras()

    def limpiar(self):
        hijos = self.tree.get_children()
        if hijos:
            self.tree.delete(*hijos)
        self.tree.configure(height=1)
        self._programar_barras()

    def _actualizar_yview(self, first, last):
        self.vscroll.set(first, last)
        self._programar_barras()

    def _actualizar_xview(self, first, last):
        self.hscroll.set(first, last)
        self._programar_barras()

    def _programar_barras(self):
        if self._barra_pendiente is not None:
            return
        try:
            self._barra_pendiente = self.after_idle(self._actualizar_barras)
        except tk.TclError:
            self._barra_pendiente = None

    def _actualizar_barras(self):
        self._barra_pendiente = None
        try:
            x0, x1 = self.tree.xview()
            y0, y1 = self.tree.yview()
        except tk.TclError:
            return
        mostrar_v = not (y0 <= 0.001 and y1 >= 0.999)
        mostrar_h = not (x0 <= 0.001 and x1 >= 0.999)
        cambio = False
        if mostrar_v != self._v_visible:
            self._v_visible = mostrar_v
            if mostrar_v:
                self.marco_v.grid()
            else:
                self.marco_v.grid_remove()
            cambio = True
        if mostrar_h != self._h_visible:
            self._h_visible = mostrar_h
            if mostrar_h:
                self.marco_h.grid()
            else:
                self.marco_h.grid_remove()
            cambio = True
        if cambio:
            self._programar_barras()

    def filas(self):
        return len(self.tree.get_children())

    def seleccionar(self, indice):
        hijos = self.tree.get_children()
        if 0 <= indice < len(hijos):
            item = hijos[indice]
            self.tree.selection_set(item)
            self.tree.focus(item)
            self.tree.see(item)
        else:
            seleccion = self.tree.selection()
            if seleccion:
                self.tree.selection_remove(*seleccion)

    def quitar_seleccion(self):
        self.seleccionar(-1)

    def _al_clic(self, evento=None):
        if self.al_elegir_paso is None:
            return
        fila = self.tree.identify_row(evento.y) if evento is not None else ""
        if not fila:
            return
        try:
            indice = self.tree.index(fila)
        except tk.TclError:
            return
        self.al_elegir_paso(indice)

    def _al_tecla(self, evento=None):
        if self.al_elegir_paso is None or evento is None:
            return
        if evento.keysym not in ("Up", "Down", "Home", "End", "Prior", "Next"):
            return
        seleccion = self.tree.selection()
        if not seleccion:
            return
        try:
            indice = self.tree.index(seleccion[0])
        except tk.TclError:
            return
        self.al_elegir_paso(indice)


# Colores por rol: p = dividendo / dato, d = divisor, q = cociente, r = resto, t = neutro
ROL_COLOR = {"p": "#1B5E20", "d": INK, "q": NAVY, "r": ORANGE, "t": INK}


class TextoRico(tk.Text):
    """Texto de solo lectura con partes de colores. contenido = str o [(texto, rol), ...].
    El alto se ajusta solo según las líneas que ocupa."""

    def __init__(self, master, font, bg):
        # CAMBIO CLAVE: wrap="char" para que corte polinomios largos y no se salgan de la tarjeta
        super().__init__(master, font=font, bg=bg, fg=INK, relief="flat", bd=0,
                         highlightthickness=0, wrap="char", height=1, width=1,
                         cursor="arrow", state="disabled", takefocus=0, padx=0, pady=0)
        for rol, color in ROL_COLOR.items():
            self.tag_configure(rol, foreground=color)
        self.bind("<Configure>", lambda _: self._ajustar(), add="+")

    def poner(self, contenido, bg, fg):
        self.tag_configure("plano", foreground=fg)
        if isinstance(contenido, str):
            contenido = [(contenido, "plano")] if contenido else []
        self.configure(state="normal", bg=bg)
        self.delete("1.0", "end")
        for texto, rol in contenido:
            self.insert("end", texto, rol)
        self.configure(state="disabled")
        self._ajustar()

    def _ajustar(self):
        try:
            self.update_idletasks()
            n = self.count("1.0", "end-1c", "displaylines")
            filas = max(1, n[0] if n else 1)
        except tk.TclError:
            filas = 1
        if int(self.cget("height")) != filas:
            self.configure(height=filas)


class TarjetaResultado(Card):
    """Tarjeta verde (o ámbar) con el valor principal y la verificación.
    principal y detalle aceptan str o lista de (texto, rol) con colores por rol."""

    def __init__(self, master, fuentes):
        super().__init__(master, r=14, fill=GREEN_L, outline=GREEN_B, shadow=False,
                         outer=CARD, pad=16, autoheight=True)
        self.fuentes = fuentes
        self._icono_ok = imagenes.photo(imagenes.icon_image("check", 22, GREEN))
        self._icono_warn = imagenes.photo(imagenes.icon_image("warn", 22, AMBER))
        self._labels = []

        fila = tk.Frame(self.inner, bg=GREEN_L)
        fila.pack(anchor="w")
        self.lbl_icono = tk.Label(fila, image=self._icono_ok, bg=GREEN_L)
        self.lbl_icono.pack(side="left")
        self.lbl_titulo = tk.Label(fila, text="Resultado", font=fuentes.h3, bg=GREEN_L, fg=INK)
        self.lbl_titulo.pack(side="left", padx=(8, 0))
        self._labels.extend([fila, self.lbl_icono, self.lbl_titulo])

        self.lbl_principal = TextoRico(self.inner, fuentes.big, GREEN_L)
        self.lbl_principal.pack(fill="x", pady=(3, 0))
        self.lbl_detalle = TextoRico(self.inner, fuentes.bold, GREEN_L)
        self.lbl_detalle.pack(fill="x", pady=(4, 0))
        self.lbl_ref = tk.Label(self.inner, text="", font=fuentes.hint, bg=GREEN_L,
                                fg="#4F7A62", anchor="w", justify="left", wraplength=380)
        self.lbl_ref.pack(anchor="w", pady=(4, 0))
        self._labels.append(self.lbl_ref)
        self.inner.bind("<Configure>", self._ajustar_wrap)

    def _ajustar_wrap(self, evento):
        self.lbl_ref.configure(wraplength=max(evento.width - 8, 180))

    def mostrar(self, principal, detalle="", referencia="", tono="verde"):
        # Forzamos siempre el color verde
        fill, outline, color_principal = GREEN_L, GREEN_B, NAVY
        icono = self._icono_ok

        self.set_colors(fill, outline)
        for widget in self._labels:
            widget.configure(bg=fill)
        self.lbl_icono.configure(image=icono, bg=fill)
        self.lbl_titulo.configure(bg=fill, fg=INK)
        self.lbl_principal.poner(principal, fill, color_principal)
        self.lbl_detalle.poner(detalle, fill, INK)
        self.lbl_ref.configure(text=referencia, bg=fill, fg="#4F7A62")
        self.actualizar_alto()


class Banner(Card):
    """Banner de avisos y errores, con texto además del color."""

    def __init__(self, master, fuentes):
        super().__init__(
            master, r=12, fill=AMBER_L, outline=AMBER_B, shadow=False, outer=CARD,
            pad=12, autoheight=True,
        )
        self.fuentes = fuentes
        self._icono_amber = imagenes.photo(imagenes.icon_image("warn", 17, AMBER))
        self._icono_rojo = imagenes.photo(imagenes.icon_image("warn", 17, RED))
        self._labels = []
        fila = tk.Frame(self.inner, bg=AMBER_L)
        fila.pack(fill="x")
        self.lbl_icono = tk.Label(fila, image=self._icono_amber, bg=AMBER_L)
        self.lbl_icono.pack(side="left", anchor="n")
        self.lbl_texto = tk.Label(
            fila, text="", font=fuentes.normal, bg=AMBER_L, fg=AMBER,
            justify="left", anchor="w", wraplength=360,
        )
        self.lbl_texto.pack(side="left", padx=(7, 0), fill="x", expand=True)
        self._labels.extend([fila, self.lbl_icono, self.lbl_texto])
        self.inner.bind("<Configure>", self._ajustar_wrap)

    def _ajustar_wrap(self, evento):
        self.lbl_texto.configure(wraplength=max(evento.width - 32, 160))

    def mostrar(self, texto, tono="advertencia"):
        if tono == "error":
            fill, outline, color = RED_L, RED_B, RED
            icono = self._icono_rojo
        else:
            fill, outline, color = AMBER_L, AMBER_B, AMBER
            icono = self._icono_amber
        self.set_colors(fill, outline)
        for widget in self._labels:
            widget.configure(bg=fill)
        self.lbl_icono.configure(image=icono, bg=fill)
        self.lbl_texto.configure(text=texto, fg=color, bg=fill)
        self.actualizar_alto()