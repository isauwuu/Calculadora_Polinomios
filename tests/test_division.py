"""Tests de metodos/division.py contra los ejemplos del apunte.
Convención: coef[i] = coeficiente de x^i  (menor→mayor grado).

El divisor lineal se llama dividir_por_x_menos_b: si el divisor es (x - b),
b se pasa TAL CUAL (b=2 para x-2, b=-3 para x+3).
"""
from fractions import Fraction
import pytest

from core.polinomio import Polinomio
from core.errores import DivisionPorCero
from metodos.division import (
    dividir_por_x_menos_b,
    dividir_por_ax_mas_b,
    horner_cuadratico,
    dividir_por_cuadratico,
    dividir,
)


# --- Polinomios de referencia (coef low→high) ---
# P2(x) = x³ - 2x² + x - 3       (Ejemplos 1 y 2)
P2 = Polinomio([-3, 1, -2, 1])
# P3(x) = 3x³ - 2x² + 3x - 3     (Ejemplo 3)
P3 = Polinomio([-3, 3, -2, 3])
# P4(x) = x⁴ - 3x³ - x + 1       (Ejemplo 4)
P4 = Polinomio([1, -1, 0, -3, 1])
# P_div(x) = (x - 1)(x - 2)(x + 3) = x³ - 7x + 6   (para división exacta)
P_div = Polinomio([6, -7, 0, 1])


# ====================================================================
# Ejemplo 2: P / (x - 2) → C(x) = x² + 1, R = -1
# ====================================================================

def test_dividir_por_x_menos_b_ej2():
    # Divisor (x - 2) → b = 2, se pasa TAL CUAL
    c, r = dividir_por_x_menos_b(P2, 2).valor
    assert c.coef == [Fraction(1), Fraction(0), Fraction(1)]   # x² + 1
    assert r == Fraction(-1)


# ====================================================================
# División exacta por (x + 3) → b = -3  y por (x - 1) → b = 1
# P_div(x) = x³ - 7x + 6 = (x - 1)(x - 2)(x + 3)
# ====================================================================

def test_dividir_por_x_menos_b_signo_negativo():
    c, r = dividir_por_x_menos_b(P_div, -3).valor
    # cociente (x - 1)(x - 2) = x² - 3x + 2  → coef low→high [2, -3, 1]
    assert c.coef == [Fraction(2), Fraction(-3), Fraction(1)]
    assert r == Fraction(0)


def test_dividir_por_x_menos_b_division_exacta_x_menos_1():
    c, r = dividir_por_x_menos_b(P_div, 1).valor
    # cociente (x - 2)(x + 3) = x² + x - 6  → coef low→high [-6, 1, 1]
    assert c.coef == [Fraction(-6), Fraction(1), Fraction(1)]
    assert r == Fraction(0)


# ====================================================================
# Ejemplo 3: P / (3x - 2) → C(x) = x² + 1, R = -1
# ====================================================================

def test_dividir_por_ax_mas_b_ej3():
    # Divisor 3x - 2 → a = 3, b = -2
    c, r = dividir_por_ax_mas_b(P3, 3, -2).valor
    assert c.coef == [Fraction(1), Fraction(0), Fraction(1)]   # x² + 1
    assert r == Fraction(-1)


def test_dividir_por_ax_mas_b_con_a_cero_lanza():
    with pytest.raises(DivisionPorCero):
        dividir_por_ax_mas_b(P3, 0, 5)


# ====================================================================
# Ejemplo 4: P / (x² + 2x - 3) → C = x² - 5x + 13, R = -42x + 40
# ====================================================================

def test_horner_cuadratico_ej4():
    # Divisor x² + 2x - 3 → a = 2, b = -3
    c, r = horner_cuadratico(P4, 2, -3).valor
    assert c.coef == [Fraction(13), Fraction(-5), Fraction(1)]     # x² - 5x + 13
    assert r.coef == [Fraction(40), Fraction(-42)]                 # -42x + 40


def test_horner_cuadratico_grado_menor_que_divisor():
    """Si P tiene grado < 2, el cociente es 0 y el resto es P."""
    p = Polinomio([3, -2])   # -2x + 3
    c, r = horner_cuadratico(p, 1, 1).valor
    assert c.es_cero
    assert r.coef == [Fraction(3), Fraction(-2)]


# ====================================================================
# dividir_por_cuadratico: Horner cuadrático si a=1, general si a≠1
# ====================================================================

def test_dividir_por_cuadratico_con_a_1_usa_horner():
    c, r = dividir_por_cuadratico(P4, 1, 2, -3).valor
    assert c.coef == [Fraction(13), Fraction(-5), Fraction(1)]
    assert r.coef == [Fraction(40), Fraction(-42)]


def test_dividir_por_cuadratico_con_a_3_usa_general():
    """(3x² + 6x - 9) = 3·(x² + 2x - 3). El cociente queda dividido por 3."""
    c, r = dividir_por_cuadratico(P4, 3, 6, -9).valor
    assert c.coef == [Fraction(13, 3), Fraction(-5, 3), Fraction(1, 3)]
    assert r.coef == [Fraction(40), Fraction(-42)]


def test_dividir_por_cuadratico_con_a_cero_lanza():
    with pytest.raises(DivisionPorCero):
        dividir_por_cuadratico(P4, 0, 1, 1)


# ====================================================================
# División general
# ====================================================================

def test_dividir_general_ej2():
    d = Polinomio([-2, 1])   # x - 2
    c, r = dividir(P2, d).valor
    assert c.coef == [Fraction(1), Fraction(0), Fraction(1)]
    # R = -1; el grado del resto puede ser ≤ 0 o la lista puede quedar vacía
    assert r.coef in ([Fraction(-1)], [Fraction(-1), Fraction(0)])


def test_dividir_general_ej4():
    d = Polinomio([-3, 2, 1])   # x² + 2x - 3
    c, r = dividir(P4, d).valor
    assert c.coef == [Fraction(13), Fraction(-5), Fraction(1)]
    assert r.coef == [Fraction(40), Fraction(-42)]


def test_dividir_por_polinomio_nulo_lanza():
    with pytest.raises(DivisionPorCero):
        dividir(P2, Polinomio([0]))


def test_dividir_grado_menor_devuelve_cociente_cero():
    p = Polinomio([1, 2])
    c, r = dividir(p, P4).valor
    assert c.es_cero
    assert r.coef == [Fraction(1), Fraction(2)]


# ====================================================================
# Integridad: P = D·Q + R  (verificado en varios puntos)
# ====================================================================

def _evaluar(coefs, x):
    """Evalúa P(x) con Horner; coefs en orden [a0, a1, ...] (coef de x^i)."""
    resultado = Fraction(0)
    for c in reversed(coefs):
        resultado = resultado * x + c
    return resultado


def test_identidad_P_igual_DQ_mas_R_division_general():
    d = Polinomio([-3, 2, 1])   # x² + 2x - 3
    c, r = dividir(P4, d).valor
    for x in [Fraction(0), Fraction(1), Fraction(-1),
              Fraction(5, 2), Fraction(-7, 3)]:
        pv = _evaluar(P4.coef, x)
        dv = _evaluar(d.coef, x)
        qv = _evaluar(c.coef, x)
        rv = _evaluar(r.coef, x)
        assert pv == dv * qv + rv, f"falla en x = {x}"


def test_identidad_P_igual_DQ_mas_R_horner_cuadratico():
    c, r = horner_cuadratico(P4, 2, -3).valor
    for x in [Fraction(0), Fraction(1), Fraction(-2), Fraction(3, 4)]:
        pv = _evaluar(P4.coef, x)
        dv = _evaluar([-3, 2, 1], x)   # x² + 2x - 3
        qv = _evaluar(c.coef, x)
        rv = _evaluar(r.coef, x)
        assert pv == dv * qv + rv, f"falla en x = {x}"


def test_identidad_P_igual_DQ_mas_R_x_menos_b():
    c, r = dividir_por_x_menos_b(P2, 2).valor
    for x in [Fraction(0), Fraction(3), Fraction(-1), Fraction(5, 2)]:
        pv = _evaluar(P2.coef, x)
        dv = x - 2                       # (x - 2)
        qv = _evaluar(c.coef, x)
        assert pv == dv * qv + r