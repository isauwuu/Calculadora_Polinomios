"""Pruebas de las tablas de Ruffini/Horner de la pestaña 1.

La interfaz solo dibuja: los valores se comparan contra el núcleo exacto
(``horner_fraction`` y ``dividir_por_cuadratico``) y contra los ejemplos del
apunte.
"""

from fractions import Fraction

import pytest

from core.errores import EntradaInvalida
from core.polinomio import Polinomio
from gui import controlador
from metodos.evaluacion import horner_fraction


def test_ruffini_ejemplo_apunte():
    # x^3 - 5x - 3 dividido por (x - 2): cociente x^2 + 2x - 1 y resto -5.
    datos = controlador.tabla_ruffini("1 0 -5 -3", 2)

    assert datos["fila1"] == [Fraction(1), Fraction(0), Fraction(-5), Fraction(-3)]
    assert datos["fila2"] == [None, Fraction(2), Fraction(4), Fraction(-2)]
    assert datos["fila3"] == [Fraction(1), Fraction(2), Fraction(-1), Fraction(-5)]
    assert datos["cociente"] == [Fraction(1), Fraction(2), Fraction(-1)]
    assert datos["resto"] == Fraction(-5)


def test_ruffini_resto_coincide_con_horner():
    p = Polinomio.desde_texto("3 -11 -6 44 -24")
    for alpha in (Fraction(-2), Fraction(2, 3), Fraction(2), Fraction(3)):
        datos = controlador.tabla_ruffini(p, alpha)
        assert datos["resto"] == horner_fraction(p, alpha).valor


def test_ruffini_alpha_fraccionario():
    # x^3 - 2x^2 - x + 2 dividido por (x - 3/2).
    datos = controlador.tabla_ruffini("1 -2 -1 2", Fraction(3, 2))

    assert datos["fila3"] == [
        Fraction(1),
        Fraction(-1, 2),
        Fraction(-7, 4),
        Fraction(-5, 8),
    ]
    assert datos["resto"] == Fraction(-5, 8)


def test_ruffini_con_coeficientes_cero():
    # x^3 - 8 dividido por (x - 2): cociente x^2 + 2x + 4 y resto 0.
    datos = controlador.tabla_ruffini([1, 0, 0, -8], 2)

    assert datos["fila1"] == [Fraction(1), Fraction(0), Fraction(0), Fraction(-8)]
    assert datos["fila3"] == [Fraction(1), Fraction(2), Fraction(4), Fraction(0)]
    assert datos["cociente"] == [Fraction(1), Fraction(2), Fraction(4)]
    assert datos["resto"] == 0


def test_ruffini_acepta_polinomio_y_texto():
    p = Polinomio.desde_texto("1 0 -5 -3")
    desde_polinomio = controlador.tabla_ruffini(p, 2)
    desde_texto = controlador.tabla_ruffini("1 0 -5 -3", 2)
    assert desde_polinomio == desde_texto


def test_ruffini_doble():
    # P(2) y P'(2) para x^3 - 5x - 3: P(2) = -5, P'(2) = 7.
    datos = controlador.tabla_ruffini_doble("1 0 -5 -3", 2)

    assert datos["p_alpha"] == Fraction(-5)
    assert datos["dp_alpha"] == Fraction(7)
    assert datos["segunda"]["fila3"] == [Fraction(1), Fraction(4), Fraction(7)]


def test_ruffini_ax_mas_b_normaliza_el_cociente():
    # (3x^3 - 2x^2 + 3x - 3) / (3x - 2) = x^2 + 1 con resto -1.
    datos = controlador.tabla_ruffini_ax_mas_b("3 -2 3 -3", 3, -2)

    assert datos["resto"] == Fraction(-1)
    assert datos["cociente_sin_normalizar"] == [
        Fraction(3),
        Fraction(0),
        Fraction(3),
    ]
    assert datos["cociente"] == [Fraction(1), Fraction(0), Fraction(1)]
    assert datos["normalizada"] == 3


def test_ruffini_ax_mas_b_rechaza_a_cero():
    with pytest.raises(EntradaInvalida):
        controlador.tabla_ruffini_ax_mas_b("1 0 -5 -3", 0, 2)


def test_horner_cuadratico_ejemplo_apunte():
    # x^4 - 3x^3 - x + 1 entre x^2 + 2x - 3.
    datos = controlador.tabla_ruffini_cuadratica("1 -3 0 -1 1", 2, -3)

    assert datos["cociente"] == [Fraction(1), Fraction(-5), Fraction(13)]
    assert datos["resto"] == [Fraction(-42), Fraction(40)]
    assert datos["productos_a"][1] == Fraction(-2)
    assert datos["productos_b"][2] == Fraction(3)


def test_horner_cuadratico_normalizado():
    # Mismo ejemplo dividido por 2x^2 + 4x - 6.
    datos = controlador.tabla_ruffini_cuadratica_normalizada(
        "1 -3 0 -1 1", 2, 4, -6
    )

    assert datos["cociente_sin_normalizar"] == [
        Fraction(1),
        Fraction(-5),
        Fraction(13),
    ]
    assert datos["cociente"] == [
        Fraction(1, 2),
        Fraction(-5, 2),
        Fraction(13, 2),
    ]
    assert datos["resto"] == [Fraction(-42), Fraction(40)]
    assert datos["normalizada"] == 2


def test_horner_cuadratico_grado_menor():
    datos = controlador.tabla_ruffini_cuadratica("2 1", 2, -3)
    assert datos["grado_menor"] is True
    assert datos["resto"] == [Fraction(2), Fraction(1)]


@pytest.mark.parametrize("metodo", ["Directa", "Horner", "Horner doble"])
def test_esquema_evaluacion_tiene_secciones_y_pasos(metodo):
    esquema = controlador.esquema_evaluacion("1 0 -5 -3", "2", metodo)

    assert esquema["secciones"]
    assert esquema["pasos"]
    for seccion in esquema["secciones"]:
        assert seccion["filas"]
        for fila in seccion["filas"]:
            assert "valores" in fila


@pytest.mark.parametrize(
    ("tipo", "parametros"),
    [
        ("x + b", "-2"),
        ("ax + b", "2, -4"),
        ("x\u00b2 + ax + b", "1, 0"),
        ("ax\u00b2 + bx + c", "1, 0, -4"),
        ("Polinomio general", "1, -2"),
    ],
)
def test_esquema_division_todos_los_tipos(tipo, parametros):
    esquema = controlador.esquema_division("1 -2 1 -3", tipo, parametros)

    assert esquema["secciones"]
    assert esquema["pasos"]
