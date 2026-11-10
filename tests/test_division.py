from fractions import Fraction
import pytest
from core.errores import DivisionPorCero
from core.polinomio import Polinomio
from metodos.division import (
    dividir, dividir_por_ax_mas_b, dividir_por_cuadratico,
    dividir_por_x_mas_b, horner_cuadratico,
)


def reconstruir(d, q, r):
    """D*Q + R, coeficiente a coeficiente."""
    prod = [Fraction(0)] * (d.grado + q.grado + 1)
    for i, dc in enumerate(d.coef):
        for j, qc in enumerate(q.coef):
            prod[i + j] += dc * qc
    for i, rc in enumerate(r.coef):
        prod[i] += rc
    return Polinomio(prod).coef


def test_ejemplo2_por_x_mas_b():
    p = Polinomio.desde_texto("1 -2 1 -3")
    q, r = dividir_por_x_mas_b(p, -2).valor
    assert q.coef == [1, 0, 1]
    assert r == -1


def test_x_mas_b_sobre_constante():
    q, r = dividir_por_x_mas_b(Polinomio.desde_texto("7"), -3).valor
    assert q.coef == [0]
    assert r == 7


def test_ejemplo3_por_3x_menos_2():
    p = Polinomio.desde_texto("3 -2 3 -3")
    q, r = dividir_por_ax_mas_b(p, 3, -2).valor
    assert q.coef == [1, 0, 1]
    assert r == -1


def test_ejemplo4_horner_cuadratico():
    p = Polinomio.desde_texto("1 -3 0 -1 1")          # x^4 - 3x^3 - x + 1
    q, r = horner_cuadratico(p, 2, -3).valor          # x^2 + 2x - 3
    assert q.coef == [13, -5, 1]
    assert r.coef == [40, -42]


def test_horner_cuadratico_grado_2():
    p = Polinomio.desde_texto("1 2 -3")               # justo el divisor
    q, r = horner_cuadratico(p, 2, -3).valor
    assert q.coef == [1]
    assert r.coef == [0]


def test_horner_cuadratico_grado_menor():
    p = Polinomio.desde_texto("2 1")
    q, r = horner_cuadratico(p, 2, -3).valor
    assert q.coef == [0]
    assert r.coef == [1, 2]


def test_cuadratico_con_a_distinto_de_1():
    p = Polinomio.desde_texto("1 -3 0 -1 1")
    d = Polinomio([-6, 4, 2])                         # 2x^2 + 4x - 6
    q, r = dividir_por_cuadratico(p, 2, 4, -6).valor
    assert reconstruir(d, q, r) == p.coef
    assert q.coef == [Fraction(13, 2), Fraction(-5, 2), Fraction(1, 2)]
    assert r.coef == [40, -42]


def test_division_general_exacta():
    p = Polinomio.desde_texto("1 -3 2")
    q, r = dividir(p, Polinomio.desde_texto("1 -1")).valor
    assert q.coef == [-2, 1]
    assert r.coef == [0]


def test_grado_menor_que_divisor():
    p = Polinomio.desde_texto("1 1")
    q, r = dividir(p, Polinomio.desde_texto("1 0 0")).valor
    assert q.coef == [0]
    assert r.coef == [1, 1]


def test_cuadratico_coincide_con_division_general():
    p = Polinomio.desde_texto("3 -11 -6 44 -24")
    d = Polinomio.desde_texto("1 2 -3")
    q1, r1 = horner_cuadratico(p, 2, -3).valor
    q2, r2 = dividir(p, d).valor
    assert q1.coef == q2.coef
    assert r1.coef == r2.coef


def test_divisores_nulos():
    p = Polinomio.desde_texto("1 1")
    with pytest.raises(DivisionPorCero):
        dividir(p, Polinomio([0]))
    with pytest.raises(DivisionPorCero):
        dividir_por_ax_mas_b(p, 0, 1)
    with pytest.raises(DivisionPorCero):
        dividir_por_cuadratico(p, 0, 1, 1)


def test_identidad_p_igual_dq_mas_r():
    p = Polinomio.desde_texto("2 -1/2 0 7")
    d = Polinomio.desde_texto("1 1/3 -2")
    q, r = dividir(p, d).valor
    assert reconstruir(d, q, r) == p.coef


def test_x_mas_b_con_b_positivo():
    p = Polinomio.desde_texto("1 0 0 1")              # x^3 + 1 = (x + 1)(x^2 - x + 1)
    q, r = dividir_por_x_mas_b(p, 1).valor
    assert q.coef == [1, -1, 1]
    assert r == 0


def test_cuadratico_monico_usa_horner_cuadratico():
    p = Polinomio.desde_texto("1 -3 0 -1 1")
    q, r = dividir_por_cuadratico(p, 1, 2, -3).valor      # x^2 + 2x - 3
    assert q.coef == [13, -5, 1]
    assert r.coef == [40, -42]