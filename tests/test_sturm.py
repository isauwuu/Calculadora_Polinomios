import math
from fractions import Fraction

import numpy as np
import pytest

from core.errores import EntradaInvalida
from core.polinomio import Polinomio
from metodos.sturm import (
    cambios_signo,
    contar_raices,
    separar_raices,
    sucesion_sturm,
)


def _coefs(resultado):
    return [p.coef for p in resultado.valor]


def test_cambios_signo_saltea_ceros():
    assert cambios_signo([1, 0, -1]) == 1
    assert cambios_signo([-1, 2, -3, 0, 4]) == 3
    assert cambios_signo([0, 0, 0]) == 0
    assert cambios_signo([]) == 0
    assert cambios_signo([2, 3, 4]) == 0


def test_sucesion_sturm_caso_1_apunte():
    # 4x^4 - 5x^2 + 1
    p = Polinomio.desde_texto("4 0 -5 0 1")
    r = sucesion_sturm(p)

    assert _coefs(r) == [
        [Fraction(1), Fraction(0), Fraction(-5), Fraction(0), Fraction(4)],
        [Fraction(0), Fraction(-10), Fraction(0), Fraction(16)],
        [Fraction(-2), Fraction(0), Fraction(5)],
        [Fraction(0), Fraction(18)],
        [Fraction(2)],
    ]
    assert r.avisos == []
    assert [paso["i"] for paso in r.pasos] == [0, 1, 2, 3, 4]
    assert all("coef" in paso for paso in r.pasos)


def test_sucesion_sturm_caso_2_simplificada_apunte():
    # x^5 - 3x^4 - x^3 + 11x^2 - 12x + 4
    p = Polinomio.desde_texto("1 -3 -1 11 -12 4")
    r = sucesion_sturm(p, simplificada=True)

    assert _coefs(r) == [
        [Fraction(4), Fraction(-4), Fraction(-1), Fraction(1)],
        [Fraction(-12), Fraction(-2), Fraction(5)],
        [Fraction(-32), Fraction(23)],
        [Fraction(1)],
    ]
    assert r.avisos
    assert "P_4 = 0" in r.avisos[0]


def test_sucesion_caso_2_detecta_el_cero_y_rehace_la_sucesion():
    p = Polinomio.desde_texto("1 -3 -1 11 -12 4")
    estandar = sucesion_sturm(p)

    # La forma 2 arranca con Q = P / mcd(P, P'), que tiene las mismas
    # raíces pero simples.
    assert estandar.valor[0].coef == [Fraction(4), Fraction(-4), Fraction(-1), Fraction(1)]
    assert estandar.valor[-1].grado == 0
    assert estandar.avisos and "P_4 = 0" in estandar.avisos[0]


def test_simplificada_igual_a_estandar_si_no_hay_multiples():
    p = Polinomio.desde_texto("1 0 -7 6")
    normal = sucesion_sturm(p)
    simplificada = sucesion_sturm(p, simplificada=True)

    assert _coefs(normal) == _coefs(simplificada)
    assert normal.avisos == simplificada.avisos == []


def test_contar_raices_caso_1_apunte():
    p = Polinomio.desde_texto("4 0 -5 0 1")

    assert contar_raices(p, -2, 2).valor == 4
    assert contar_raices(p, Fraction(-3, 2), Fraction(-3, 4)).valor == 1  # -1
    assert contar_raices(p, Fraction(-2, 5), Fraction(2, 5)).valor == 0
    assert contar_raices(p, Fraction(1, 4), 2).valor == 2                # 1/2 y 1


def test_tabla_de_signos_caso_1():
    p = Polinomio.desde_texto("4 0 -5 0 1")
    r = contar_raices(p, -2, 2)

    assert len(r.pasos) == 5
    for paso in r.pasos:
        assert {"i", "coef", "signo_a", "signo_b"} <= set(paso)

    assert [paso["signo_a"] for paso in r.pasos] == [1, -1, 1, -1, 1]
    assert [paso["signo_b"] for paso in r.pasos] == [1, 1, 1, 1, 1]
    # ncs(-2) = 4 y ncs(2) = 0; el teorema usa ncs(a) - ncs(b).
    assert r.valor == 4


def test_contar_raices_caso_2_raiz_multiple_cuenta_distintas():
    p = Polinomio.desde_texto("1 -3 -1 11 -12 4")

    assert contar_raices(p, -5, 5).valor == 3
    assert contar_raices(p, -5, 0).valor == 1   # -2
    assert contar_raices(p, 0, Fraction(3, 2)).valor == 1  # 1 (triple)
    assert contar_raices(p, Fraction(3, 2), 5).valor == 1  # 2
    assert contar_raices(p, -5, 5).avisos


def test_extremos_que_son_raiz_lanzan_entrada_invalida():
    p = Polinomio.desde_texto("4 0 -5 0 1")
    with pytest.raises(EntradaInvalida) as exc:
        contar_raices(p, -1, 2)
    assert exc.value.pasos
    assert any(paso["signo_a"] == 0 for paso in exc.value.pasos)

    with pytest.raises(EntradaInvalida):
        contar_raices(p, -2, 1)
    with pytest.raises(EntradaInvalida):
        separar_raices(p, -2, 1)


def test_intervalo_invalido():
    p = Polinomio.desde_texto("1 0 -1")
    for a, b in [(1, 1), (2, 1), ("a", 1), (0, math.inf), (float("nan"), 1), (None, 1)]:
        with pytest.raises(EntradaInvalida):
            contar_raices(p, a, b)
        with pytest.raises(EntradaInvalida):
            separar_raices(p, a, b)


def test_polinomio_constante_y_nulo():
    constante = Polinomio([5])
    secuencia = sucesion_sturm(constante)
    assert len(secuencia.valor) == 1
    assert secuencia.avisos
    assert contar_raices(constante, -2, 2).valor == 0
    assert separar_raices(constante, -2, 2).valor == []

    with pytest.raises(EntradaInvalida):
        sucesion_sturm(Polinomio([0]))
    with pytest.raises(EntradaInvalida):
        contar_raices(Polinomio([0]), -2, 2)


def test_sucesion_lineal_y_con_raiz_en_cero():
    lineal = Polinomio.desde_texto("1 -2")
    assert [q.coef for q in sucesion_sturm(lineal).valor] == [
        [Fraction(-2), Fraction(1)],
        [Fraction(1)],
    ]
    assert contar_raices(lineal, 1, 3).valor == 1

    # x^3 - x = x(x - 1)(x + 1)
    p = Polinomio.desde_texto("1 0 -1 0")
    assert contar_raices(p, -2, 2).valor == 3
    r = separar_raices(p, -2, 2)
    assert len(r.valor) == 3
    for a, b in r.valor:
        assert sum(a < raiz < b for raiz in (-1, 0, 1)) == 1


def test_separar_raices_caso_1_apunte():
    p = Polinomio.desde_texto("4 0 -5 0 1")
    r = separar_raices(p, -2, 2)

    assert len(r.valor) == 4
    raices = [Fraction(-1), Fraction(-1, 2), Fraction(1, 2), Fraction(1)]
    for a, b in r.valor:
        assert a < b
        assert sum(a < raiz < b for raiz in raices) == 1
        assert contar_raices(p, a, b).valor == 1
    for (_, b1), (a2, _) in zip(r.valor, r.valor[1:]):
        assert b1 <= a2

    # Cada intervalo final tiene su tabla de signos.
    assert r.pasos
    assert all(
        {"i", "coef", "signo_a", "signo_b", "intervalo"} <= set(paso)
        for paso in r.pasos
    )


def test_separar_raices_caso_2_apunte():
    p = Polinomio.desde_texto("1 -3 -1 11 -12 4")
    r = separar_raices(p, -5, 5)

    assert len(r.valor) == 3
    raices = [Fraction(-2), Fraction(1), Fraction(2)]
    for a, b in r.valor:
        assert sum(a < raiz < b for raiz in raices) == 1
        assert contar_raices(p, a, b).valor == 1
    assert r.avisos


def test_separar_sin_raices_reales():
    p = Polinomio.desde_texto("1 0 1")  # x^2 + 1
    r = separar_raices(p, -5, 5)
    assert r.valor == []
    assert r.pasos == []


def test_polinomio_con_fracciones():
    # x^2 - (3/2)x + 1/2 = (x - 1)(x - 1/2)
    p = Polinomio.desde_texto("1 -3/2 1/2")
    r = sucesion_sturm(p)
    assert r.valor[-1].grado == 0
    assert contar_raices(p, 0, 2).valor == 2

    intervalos = separar_raices(p, 0, 2).valor
    assert len(intervalos) == 2
    for a, b in intervalos:
        assert sum(a < raiz < b for raiz in (Fraction(1, 2), Fraction(1))) == 1


def test_conteo_contra_numpy():
    # x^4 - 10x^2 + 9 = (x^2 - 1)(x^2 - 9)
    p = Polinomio.desde_texto("1 0 -10 0 9")
    raices_numpy = np.roots([1, 0, -10, 0, 9])
    reales = [z.real for z in raices_numpy if abs(z.imag) < 1e-8]

    # numpy devuelve las raíces, no la cantidad: se comprueba que el conteo
    # de Sturm coincide con las reales dentro del intervalo.
    esperado = sum(-10 < r < 10 for r in reales)
    assert contar_raices(p, -10, 10).valor == esperado == 4
    assert len(separar_raices(p, -10, 10).valor) == esperado
