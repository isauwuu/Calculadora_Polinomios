"""Widgets propios de la interfaz: tarjetas, campos, botones, pestañas y tablas."""

import tkinter as tk
from tkinter import ttk

from gui import imagenes
from gui.estilo import (
    AMBER,
    AMBER_B,
    AMBER_L,
    BG,
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
        pad=16,
        use_inner=True,
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
        self.bind("<Configure>", self._al_configurar)

    def add(self, frame, boxfn):
        """Agrega un frame interior que se reposiciona al redimensionar."""
        self._ventanas.append((self.create_window(0, 0, window=frame, anchor="nw"), boxfn))

    def _al_configurar(self, evento):
        if evento.width < 2 or evento.height < 2:
            return
        if (evento.width, evento.height) == self._size:
            return
        self._size = (evento.width, evento.height)
        self._pintar(evento.width, evento.height)

    def _pintar(self, w, h):
        pil = imagenes.rounded_image(
            w,
            h,
            self.r,
            self.fill,
            self.outline,
            1,
            self.m,
            self.shadow,
            self.outer,
            self.deco,
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
        """Cambia la paleta de la tarjeta (por ejemplo, resultado verde a ámbar)."""
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

    def __init__(self, master, var, font, bg=CARD, height=38):
        super().__init__(master, height=height, bg=bg, highlightthickness=0, bd=0)
        self.bgc = bg
        self.foco = False
        self._size = None
        self.entry = tk.Entry(
            self,
            textvariable=var,
            font=font,
            relief="flat",
            bd=0,
            bg=FIELD,
            fg=INK,
            insertbackground=INK,
            highlightthickness=0,
            selectbackground="#CFE3D8",
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
            w,
            h,
            11,
            FIELD,
            GREEN if self.foco else FIELD_B,
            2 if self.foco else 1,
            0,
            False,
            self.bgc,
        )
        self._imagen = imagenes.photo(pil)
        self.delete("fondo")
        self.create_image(0, 0, image=self._imagen, anchor="nw", tags="fondo")
        self.tag_lower("fondo")
        self.itemconfigure(self._ventana, width=max(w - 28, 10))


class RButton(tk.Canvas):
    """Botón redondeado con ícono opcional y efecto hover."""

    def __init__(
        self,
        master,
        text,
        command,
        fill,
        fg,
        hover,
        outline=None,
        icon=None,
        font=None,
        bg=CARD,
        height=42,
    ):
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
        self.bind("<Configure>", self._al_configurar)
        self.bind("<Enter>", lambda _: self._hover(True))
        self.bind("<Leave>", lambda _: self._hover(False))
        self.bind("<ButtonRelease-1>", lambda _: self.cmd() if self.cmd else None)

    def _al_configurar(self, evento):
        self._size = (evento.width, evento.height)
        self._dibujar()

    def _hover(self, valor):
        self._hov = valor
        self._dibujar()

    def _dibujar(self):
        if not self._size:
            return
        w, h = self._size
        color = self.hover if self._hov else self.fill
        pil = imagenes.rounded_image(w, h, 12, color, self.outline, 1, 0, False, self.bgc)
        self._imagen = imagenes.photo(pil)
        self.delete("all")
        self.create_image(0, 0, image=self._imagen, anchor="nw")
        ancho_icono = self.icon.width() if self.icon else 0
        gap = 8 if self.icon else 0
        total = ancho_icono + gap + self.font.measure(self.t)
        x0 = (w - total) / 2
        if self.icon:
            self.create_image(x0, h / 2, image=self.icon, anchor="w")
        self.create_text(
            x0 + ancho_icono + gap,
            h / 2,
            text=self.t,
            anchor="w",
            font=self.font,
            fill=self.fg,
        )


class Seg(tk.Canvas):
    """Selector segmentado con íconos de radio."""

    def __init__(self, master, options, var, font, bg=CARD, height=38, on_change=None):
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

    def _al_configurar(self, evento):
        self._size = (evento.width, evento.height)
        self._dibujar()

    def _bounds(self):
        w, h = self._size
        n = len(self.opts)
        gap = 8
        base = [self.font.measure(o) + 42 for o in self.opts]
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
                ancho, h, 11, NAVY if seleccionada else FIELD, None if seleccionada else FIELD_B, 1, 0, False, self.bgc
            )
            img = imagenes.photo(pil)
            self._imgs.append(img)
            self.create_image(x, 0, image=img, anchor="nw")
            self.create_image(x + 13, h / 2, image=self.on if seleccionada else self.off, anchor="w")
            self.create_text(
                x + 34,
                h / 2,
                text=opcion,
                anchor="w",
                font=self.font,
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
            ancho = font.measure(label) + 70
            cv = tk.Canvas(self, width=ancho, height=48, bg=BG, highlightthickness=0, bd=0, cursor="hand2")
            cv.grid(row=0, column=i, padx=(0, 8))
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
    """Tabla genérica: cada pestaña decide columnas y filas."""

    def __init__(self, master, fuentes, height=8):
        super().__init__(master, bg=CARD)
        self.fuentes = fuentes
        self._columnas = []
        self.tree = ttk.Treeview(
            self,
            show="headings",
            style="Calc.Treeview",
            selectmode="browse",
            height=height,
        )
        self.scroll = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=self.scroll.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        self.scroll.grid(row=0, column=1, sticky="ns")
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        self.tree.tag_configure("odd", background="#F5F9F7")
        self.tree.tag_configure("raiz", background=GREEN_L, foreground=GREEN_D)
        self.tree.tag_configure("final", background=GREEN_L, foreground=GREEN_D, font=fuentes.mono_bold)
        self.tree.tag_configure("roja", background=RED_L, foreground=RED)
        self.tree.tag_configure("alerta", background=AMBER_L, foreground=AMBER)
        self.tree.tag_configure("perturbado", background=AMBER_L, foreground=AMBER)
        self.tree.tag_configure("cero", background=AMBER_L, foreground=AMBER)

    def configurar(self, columnas):
        """columnas: lista de (clave, título, ancho, alineación)."""
        self.limpiar()
        self._columnas = list(columnas)
        claves = [c[0] for c in self._columnas]
        self.tree["columns"] = claves
        for clave, titulo, ancho, alineacion in self._columnas:
            self.tree.heading(clave, text=titulo, anchor="center")
            self.tree.column(clave, width=ancho, minwidth=max(40, ancho // 2), anchor=alineacion, stretch=True)

    def cargar(self, filas, tags=None):
        """Carga filas (lista de dicts) y, opcionalmente, tags por fila."""
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
        hijos = self.tree.get_children()
        if hijos:
            self.tree.yview_moveto(0)

    def limpiar(self):
        hijos = self.tree.get_children()
        if hijos:
            self.tree.delete(*hijos)

    def filas(self):
        return len(self.tree.get_children())


class TarjetaResultado(Card):
    """Tarjeta verde (o ámbar) con el valor principal y la verificación."""

    def __init__(self, master, fuentes):
        super().__init__(master, r=14, fill=GREEN_L, outline=GREEN_B, shadow=False, outer=CARD, pad=15)
        self.fuentes = fuentes
        self.configure(height=156)
        self._icono_ok = imagenes.photo(imagenes.icon_image("check", 22, GREEN))
        self._icono_warn = imagenes.photo(imagenes.icon_image("warn", 22, AMBER))
        self._labels = []

        fila = tk.Frame(self.inner, bg=GREEN_L)
        fila.pack(anchor="w")
        self.lbl_icono = tk.Label(fila, image=self._icono_ok, bg=GREEN_L)
        self.lbl_icono.pack(side="left")
        self.lbl_titulo = tk.Label(fila, text="Resultado", font=fuentes.bold, bg=GREEN_L, fg=INK)
        self.lbl_titulo.pack(side="left", padx=(8, 0))
        self._labels.extend([fila, self.lbl_icono, self.lbl_titulo])

        self.lbl_principal = tk.Label(
            self.inner, text="", font=fuentes.big, bg=GREEN_L, fg=NAVY, anchor="w", justify="left"
        )
        self.lbl_principal.pack(anchor="w", pady=(3, 0))
        self.lbl_detalle = tk.Label(
            self.inner,
            text="",
            font=fuentes.normal,
            bg=GREEN_L,
            fg=INK,
            anchor="w",
            justify="left",
            wraplength=380,
        )
        self.lbl_detalle.pack(anchor="w")
        self.lbl_ref = tk.Label(
            self.inner,
            text="",
            font=fuentes.hint,
            bg=GREEN_L,
            fg="#4F7A62",
            anchor="w",
            justify="left",
            wraplength=380,
        )
        self.lbl_ref.pack(anchor="w", pady=(2, 0))
        self._labels.extend([self.lbl_principal, self.lbl_detalle, self.lbl_ref])
        self.inner.bind("<Configure>", self._ajustar_wrap)

    def _ajustar_wrap(self, evento):
        ancho = max(evento.width - 8, 180)
        self.lbl_detalle.configure(wraplength=ancho)
        self.lbl_ref.configure(wraplength=ancho)

    def mostrar(self, principal, detalle="", referencia="", tono="verde"):
        if tono == "amber":
            fill, outline, color_icono, color_principal = AMBER_L, AMBER_B, AMBER, AMBER
            icono = self._icono_warn
        else:
            fill, outline, color_icono, color_principal = GREEN_L, GREEN_B, GREEN, NAVY
            icono = self._icono_ok
        self.set_colors(fill, outline)
        for widget in self._labels:
            widget.configure(bg=fill)
        self.lbl_icono.configure(image=icono, bg=fill)
        self.lbl_titulo.configure(bg=fill, fg=INK)
        self.lbl_principal.configure(text=principal, fg=color_principal, bg=fill)
        self.lbl_detalle.configure(text=detalle, fg=INK, bg=fill)
        self.lbl_ref.configure(text=referencia, bg=fill, fg="#4F7A62" if tono != "amber" else AMBER)


class Banner(Card):
    """Banner de avisos y errores, con texto además del color."""

    def __init__(self, master, fuentes):
        super().__init__(master, r=12, fill=AMBER_L, outline=AMBER_B, shadow=False, outer=CARD, pad=11)
        self.fuentes = fuentes
        self.configure(height=70)
        self._icono_amber = imagenes.photo(imagenes.icon_image("warn", 17, AMBER))
        self._icono_rojo = imagenes.photo(imagenes.icon_image("warn", 17, RED))
        self._labels = []
        fila = tk.Frame(self.inner, bg=AMBER_L)
        fila.pack(fill="x")
        self.lbl_icono = tk.Label(fila, image=self._icono_amber, bg=AMBER_L)
        self.lbl_icono.pack(side="left", anchor="n")
        self.lbl_texto = tk.Label(
            fila,
            text="",
            font=fuentes.small,
            bg=AMBER_L,
            fg=AMBER,
            justify="left",
            anchor="w",
            wraplength=360,
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
