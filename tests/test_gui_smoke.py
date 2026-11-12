"""Smoke tests de las seis pestañas: calculan y recorren la animación.

Se saltean si Tkinter no puede abrir una ventana (por ejemplo, un servidor sin
pantalla). No comprueban estética: solo que calcular y animar no lance
excepciones y que la tabla tenga filas.
"""

import tkinter as tk

import pytest

from gui.app import App


@pytest.fixture(scope="module")
def app():
    try:
        ventana = App()
    except tk.TclError as exc:
        pytest.skip(f"Tkinter no disponible: {exc}")
    ventana.withdraw()
    ventana.update()
    yield ventana
    try:
        ventana._cerrar()
    except tk.TclError:
        pass


def _revisar(pagina, ventana):
    ventana.update_idletasks()
    assert pagina.tabla.filas() > 0
    total = pagina.barra.controlador.total
    assert total > 0
    for indice in (0, total // 2, total - 1):
        pagina._aplicar_paso(indice)
    ventana.update_idletasks()


def test_smoke_pestana_1_todos_los_esquemas(app):
    pagina = app.paginas[0]
    app._mostrar_pagina(0)

    for metodo in ("Directa", "Horner", "Horner doble"):
        pagina.v_modo.set("Evaluar")
        pagina.v_metodo.set(metodo)
        pagina.calcular()
        _revisar(pagina, app)

    pagina.v_modo.set("Dividir")
    ejemplos = [
        ("x + b", "-2"),
        ("ax + b", "2, -4"),
        ("x\u00b2 + ax + b", "1, 0"),
        ("ax\u00b2 + bx + c", "1, 0, -4"),
        ("Polinomio general", "1, -2"),
    ]
    for tipo, parametros in ejemplos:
        pagina.v_divisor.set(tipo)
        pagina.v_params.set(parametros)
        pagina.calcular()
        _revisar(pagina, app)


def test_smoke_pestana_2_candidatos(app):
    pagina = app.paginas[1]
    app._mostrar_pagina(1)

    for modo in ("Enteras", "Racionales", "Ambas"):
        pagina.v_modo.set(modo)
        pagina.calcular()
        _revisar(pagina, app)


def test_smoke_pestana_3_cotas(app):
    pagina = app.paginas[2]
    app._mostrar_pagina(2)
    pagina.calcular()
    _revisar(pagina, app)


def test_smoke_pestana_4_newton_halley(app):
    pagina = app.paginas[3]
    app._mostrar_pagina(3)

    pagina.v_metodo.set("Newton")
    pagina.calcular()
    _revisar(pagina, app)

    # Un clic en el gráfico completa x0 pero no calcula solo.
    antes = pagina.v_x0.get()
    pagina._elegir_x0(1.25)
    assert pagina.v_x0.get() != antes


def test_smoke_pestana_5_sturm(app):
    pagina = app.paginas[4]
    app._mostrar_pagina(4)
    pagina.calcular()
    _revisar(pagina, app)
    assert pagina._estados_sturm


def test_smoke_pestana_6_bairstow(app):
    pagina = app.paginas[5]
    app._mostrar_pagina(5)
    pagina.calcular()
    _revisar(pagina, app)

    assert len(pagina.grafico.artistas_raices) == len(pagina._coef) - 1
    pagina._aplicar_paso(pagina.barra.controlador.total - 1)
    assert all(
        artista.get_visible()
        for artistas in pagina.grafico.artistas_raices
        for artista in artistas
    )
