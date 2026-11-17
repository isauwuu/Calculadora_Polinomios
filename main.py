"""Punto de entrada de la calculadora de raíces de polinomios."""

import ctypes
import os
import sys

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


def ruta_recurso(ruta_relativa):
    """Devuelve la ruta correcta tanto en Python normal como en el .exe de PyInstaller."""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, ruta_relativa)


def main():
    activar_dpi_windows()
    app = App()

    # --- PONER EL ICONO A LA VENTANA ---
    try:
        app.iconbitmap(ruta_recurso("mi_icono.ico"))
    except Exception as e:
        print("No se pudo cargar el icono:", e)
    # -----------------------------------

    app.mainloop()


if __name__ == "__main__":
    main()