"""Smoke tests de las seis pestañas: calculan y recorren la animación.

Se saltean si Tkinter no puede abrir una ventana (por ejemplo, un servidor sin
pantalla). No comprueban estética: solo que calcular y animar no lance
excepciones y que la vista tenga contenido (tabla, esquema o panel).
"""

import tkinter as tk

import pytest

from gui.app import App
from gui.widgets import TablaPasos


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


def _detener_animacion(pagina):
    """Cancela el temporizador para recorrer los pasos a mano en el test."""
    job = getattr(pagina, "_anim_job", None)
    if job is not None:
        try:
            pagina.after_cancel(job)
        except tk.TclError:
            pass
        pagina._anim_job = None


def _revisar(pagina, ventana):
    ventana.update()
    assert pagina.tabla.filas() > 0
    _detener_animacion(pagina)
    total = len(pagina._pasos_animados)
    assert total > 0
    for indice in (0, total // 2, total - 1):
        pagina._aplicar_paso(indice)
    ventana.update()
    # Simula elegir un paso como si se hubiera hecho clic en la tabla: antes
    # esto realimentaba la animación y congelaba la ventana.
    pagina._elegir_paso(0)
    ventana.update()


def _revisar_estatica(pagina, ventana):
    """Pestañas sin animación: la tabla debe quedar cargada."""
    ventana.update()
    assert pagina.tabla.filas() > 0
    pagina._elegir_paso(0)
    ventana.update()


def _revisar_ruffini(pagina, ventana):
    """La pestaña 1 ya no tiene tabla de pasos: solo el esquema de Ruffini."""
    ventana.update()
    assert pagina.tabla is None
    assert pagina.esquema._esquemas


def _revisar_raices(pagina, ventana):
    """La pestaña 2 reemplaza la tabla por el panel de raíces."""
    ventana.update()
    assert pagina.panel_raices.winfo_children()
    assert pagina._resultado_visible


def _revisar_cotas(pagina, ventana):
    """La pestaña 3 reemplaza la tabla por las tarjetas de cada mtodo."""
    ventana.update()
    assert len(pagina.panel_tarjetas.winfo_children()) >= 3
    assert pagina._resultado_visible


def test_smoke_pestana_1_todos_los_esquemas(app):
    pagina = app.paginas[0]
    app._mostrar_pagina(0)

    for metodo in ("Directa", "Horner", "Horner doble"):
        pagina.v_modo.set("Evaluar")
        pagina.v_metodo.set(metodo)
        pagina.calcular()
        _revisar_ruffini(pagina, app)

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
        _revisar_ruffini(pagina, app)


def test_smoke_pestana_2_candidatos(app):
    pagina = app.paginas[1]
    app._mostrar_pagina(1)

    for modo in ("Enteras", "Racionales", "Ambas"):
        pagina.v_modo.set(modo)
        pagina.calcular()
        _revisar_raices(pagina, app)


def test_smoke_pestana_3_cotas(app):
    pagina = app.paginas[2]
    app._mostrar_pagina(2)
    pagina.calcular()
    _revisar_cotas(pagina, app)


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
    _revisar_estatica(pagina, app)
    assert pagina.frame_sucesion.winfo_children()
    assert pagina.panel_info.winfo_children()


def test_smoke_pestana_6_bairstow(app):
    pagina = app.paginas[5]
    app._mostrar_pagina(5)
    pagina.calcular()
    _revisar(pagina, app)

    assert len(pagina.grafico.artistas_raices) == len(pagina._coef) - 1
    pagina._aplicar_paso(len(pagina._pasos_animados) - 1)
    assert all(
        artista.get_visible()
        for artistas in pagina.grafico.artistas_raices
        for artista in artistas
    )


def test_tabla_no_arrastra_la_vista_si_el_usuario_scrollea(app):
    """La animación no debe devolver el scroll a la fila activa."""
    tabla = TablaPasos(app, app.fuentes, height=4, max_filas=4)
    try:
        tabla.configurar([("n", "n", 40, "center")])
        filas = [{"n": str(i)} for i in range(20)]
        tabla.cargar(filas)

        llamadas = []
        original = tabla.tree.see
        tabla.tree.see = llamadas.append
        try:
            tabla.seleccionar(0)
            assert len(llamadas) == 1

            tabla._yview_usuario("moveto", 0.0)
            tabla.seleccionar(19)
            assert len(llamadas) == 1

            tabla.cargar(filas)
            tabla.seleccionar(19)
            assert len(llamadas) == 2
        finally:
            tabla.tree.see = original
    finally:
        tabla.destroy()
