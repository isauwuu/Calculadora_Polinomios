from fractions import Fraction

import pytest

from core.polinomio import Polinomio
from metodos.cotas import (
    cota_implicacion,
    lagrange,
    laguerre,
    newton_cotas,
    todas_las_cotas,
)


def _bounds(resultado):
    return {k: float(v) for k, v in resultado.valor.items()}


def _contiene(resultado, raiz: float) -> bool:
    b = _bounds(resultado)
    if raiz > 0:
        return b["inf_pos"] - 1e-12 <= raiz <= b["sup_pos"] + 1e-12
    if raiz < 0:
        return b["inf_neg"] - 1e-12 <= raiz <= b["sup_neg"] + 1e-12
    return True  # el 0 no es ni positivo ni negativo


def test_lagrange_ejemplo_apunte():
    p = Polinomio.desde_texto("3 -11 -6 44 -24")
    r = lagrange(p)

    assert r.valor["sup_pos"] == Fraction(9)
    assert r.valor["inf_pos"] == Fraction(6, 17)
    assert isinstance(r.valor["sup_neg"], Fraction)
    assert r.valor["inf_neg"] == Fraction(-483, 100)
    assert r.valor["inf_neg"] < -2 < r.valor["sup_neg"]
    assert len(r.pasos) == 4


def test_laguerre_ejemplo_apunte():
    p = Polinomio.desde_texto("3 -11 -6 44 -24")
    r = laguerre(p)

    assert r.valor == {
        "inf_pos": Fraction(1, 2),
        "sup_pos": Fraction(5),
        "inf_neg": Fraction(-3),
        "sup_neg": Fraction(-1),
    }


def test_newton_cotas_ejemplo_apunte():
    p = Polinomio.desde_texto("3 -11 -6 44 -24")
    r = newton_cotas(p)

    assert r.valor == {
        "inf_pos": Fraction(1, 2),
        "sup_pos": Fraction(4),
        "inf_neg": Fraction(-3),
        "sup_neg": Fraction(-1),
    }


def test_cota_implicacion():
    # 4x^4 - 5x^2 + 1: |r| <= 1 + 5/4 = 2.25
    p = Polinomio.desde_texto("4 0 -5 0 1")
    r = cota_implicacion(p)

    assert r.valor["sup_pos"] == Fraction(9, 4)
    assert r.valor["inf_neg"] == Fraction(-9, 4)
    assert r.valor["inf_pos"] == 0
    assert r.valor["sup_neg"] == 0
    for raiz in (-1, -0.5, 0.5, 1):
        assert _contiene(r, raiz)


def test_todas_las_cotas_contienen_las_raices_del_ejemplo():
    p = Polinomio.desde_texto("3 -11 -6 44 -24")
    raices = (-2, 2 / 3, 2, 3)
    for nombre, r in todas_las_cotas(p).items():
        for raiz in raices:
            assert _contiene(r, raiz), (nombre, raiz, r.valor)


def test_cotas_no_positivas_son_cero():
    # x^2 + 1 no tiene raíces reales; Lagrange/Laguerre/Newton no acotan
    # raíces positivas ni negativas.
    p = Polinomio.desde_texto("1 0 1")
    for r in (lagrange(p), laguerre(p), newton_cotas(p)):
        assert r.valor == {
            "inf_pos": 0,
            "sup_pos": 0,
            "inf_neg": 0,
            "sup_neg": 0,
        }


def test_coeficiente_principal_negativo_da_las_mismas_cotas():
    p = Polinomio.desde_texto("-3 11 6 -44 24")  # -P del ejemplo
    for f in (lagrange, laguerre, newton_cotas):
        assert f(p).valor == f(Polinomio.desde_texto("3 -11 -6 44 -24")).valor


def test_polinomio_constante_y_nulo():
    for f in (lagrange, laguerre, newton_cotas, cota_implicacion):
        cero = f(Polinomio([0])).valor
        assert cero == {"inf_pos": 0, "sup_pos": 0, "inf_neg": 0, "sup_neg": 0}
        constante = f(Polinomio([5])).valor
        assert constante == {"inf_pos": 0, "sup_pos": 0, "inf_neg": 0, "sup_neg": 0}


def test_lagrange_cota_racional_conservadora():
    # x^2 - 2: la cota superior es 1 + sqrt(2), irracional. Se devuelve una
    # fracción >= 1 + sqrt(2).
    p = Polinomio.desde_texto("1 0 -2")
    r = lagrange(p)
    assert isinstance(r.valor["sup_pos"], Fraction)
    assert float(r.valor["sup_pos"]) >= 1 + 2 ** 0.5
    assert _contiene(r, 2 ** 0.5)
    assert _contiene(r, -(2 ** 0.5))
