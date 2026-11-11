"""Punto de entrada de la calculadora de raíces de polinomios."""

import ctypes

from gui.app import App


def activar_dpi_windows():
    """Evita que Windows escale la ventana y deforme las imágenes de Pillow."""
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        try:
            ctypes.windll.user32.SetProcessDPIAware()
        except Exception:
            pass


def main():
    activar_dpi_windows()
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
