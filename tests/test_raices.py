from fractions import Fraction

import pytest

from core.polinomio import Polinomio
from metodos.raices import divisores, raices_enteras, raices_racionales


def test_divisores():
    d100 = divisores(-100)
    assert len(d100) == 18
    assert d100 == sorted(d100)
    assert len(set(d100)) == 18
    assert divisores(1) == [-1, 1]
    assert divisores(0) == []


def test_raices_enteras_ejemplo_apunte():
    # 3x^4 - 11x^3 - 6x^2 + 44x - 24
    p = Polinomio.desde_texto("3 -11 -6 44 -24")
    r = raices_enteras(p)
    assert r.valor == [Fraction(-2), Fraction(2), Fraction(3)]
    # un paso por cada candidato probado
    assert r.pasos
    assert all({"candidato", "valor", "es_raiz"} <= set(paso) for paso in r.pasos)
    assert all(paso["es_raiz"] == (paso["valor"] == 0) for paso in r.pasos)


def test_raices_racionales_ejemplo_apunte():
    # Las cuatro raíces son racionales: -2, 2/3, 2, 3.
    p = Polinomio.desde_texto("3 -11 -6 44 -24")
    r = raices_racionales(p)
    assert r.valor == [Fraction(-2), Fraction(2, 3), Fraction(2), Fraction(3)]
    assert all({"candidato", "valor", "es_raiz", "p", "q"} <= set(paso) for paso in r.pasos)
    # p/q del paso coincide con el candidato (ya reducido por Fraction)
    assert all(Fraction(paso["p"], paso["q"]) == paso["candidato"] for paso in r.pasos)


def test_raiz_cero_en_enteras_y_racionales():
    p = Polinomio.desde_texto("1 0 -1 0")  # x^3 - x
    assert raices_enteras(p).valor == [Fraction(-1), Fraction(0), Fraction(1)]
    assert raices_racionales(p).valor == [Fraction(-1), Fraction(0), Fraction(1)]


def test_polinomio_sin_raices_reales_racionales():
    p = Polinomio.desde_texto("1 0 1")  # x^2 + 1
    assert raices_enteras(p).valor == []
    assert raices_racionales(p).valor == []


def test_polinomio_con_fracciones():
    # x^2 - (3/2)x + 1/2 = (x - 1)(x - 1/2)
    p = Polinomio.desde_texto("1 -3/2 1/2")
    assert raices_enteras(p).valor == [Fraction(1)]
    assert raices_racionales(p).valor == [Fraction(1, 2), Fraction(1)]


def test_polinomio_constante():
    assert raices_enteras(Polinomio([5])).valor == []
    assert raices_racionales(Polinomio([5])).valor == []
    cero = Polinomio([0])
    r_ent = raices_enteras(cero)
    r_rac = raices_racionales(cero)
    assert r_ent.valor == []
    assert r_rac.valor == []
    assert r_ent.avisos and r_rac.avisos


def test_polinomio_solo_potencia_de_x():
    # 2x^3: la única raíz distinta es 0 (se informa una vez)
    p = Polinomio([0, 0, 0, 2])
    assert raices_enteras(p).valor == [Fraction(0)]
    assert raices_racionales(p).valor == [Fraction(0)]
    # el paso de la raíz 0 está marcado como raíz
    assert raices_racionales(p).pasos[0]["es_raiz"] is True


def test_candidatos_negativos_y_coeficiente_principal_negativo():
    # -x^2 + 1 = -(x - 1)(x + 1)
    p = Polinomio.desde_texto("-1 0 1")
    assert raices_enteras(p).valor == [Fraction(-1), Fraction(1)]
    assert raices_racionales(p).valor == [Fraction(-1), Fraction(1)]


def test_raices_enteras_sin_mutar_el_polinomio():
    p = Polinomio.desde_texto("1 0 -1")
    antes = list(p.coef)
    raices_enteras(p)
    raices_racionales(p)
    assert p.coef == antes
