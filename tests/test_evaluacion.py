"""Tests de metodos/evaluacion.py contra los ejemplos del apunte.
Convención: coef[i] = coeficiente de x^i  (menor→mayor grado).
"""
from fractions import Fraction
import pytest

from core.polinomio import Polinomio
from metodos.evaluacion import (
    evaluacion_directa,
    horner_fraction,
    horner_float,
    horner_doble_fraction,
    horner_doble_float,
    horner3_float,
)


# --- Polinomios de referencia (coef low→high) ---
# P1(x) = x³ - 2x² + x - 3   (Ejemplo 1 y 2)
P1 = Polinomio([-3, 1, -2, 1])
# P6(x) = x³ - 5x - 3        (Ejemplo 6)
P6 = Polinomio([-3, -5, 0, 1])


# ====================================================================
# Ejemplo 1 del apunte: P(x) = x³ - 2x² + x - 3,  P(2) = -1
# ====================================================================

def test_evaluacion_directa_ej1():
    r = evaluacion_directa(P1, 2)
    assert r.valor == Fraction(-1)


def test_horner_fraction_ej1():
    r = horner_fraction(P1, 2)
    assert r.valor == Fraction(-1)


def test_horner_float_ej1():
    r = horner_float(P1, 2)
    assert r.valor == pytest.approx(-1.0)


# ====================================================================
# Ejemplo 6 del apunte: P(x) = x³ - 5x - 3 en x0 = 2
#   P(2) = -5,  P'(2) = 7,  P''(2) = 12
# ====================================================================

def test_horner_doble_fraction_ej6():
    P, dP = horner_doble_fraction(P6, 2).valor
    assert P == Fraction(-5)
    assert dP == Fraction(7)


def test_horner_doble_float_ej6():
    P, dP = horner_doble_float(P6.a_float(), 2.0)
    assert P == pytest.approx(-5.0)
    assert dP == pytest.approx(7.0)


def test_horner3_float_ej6_devuelve_p_doble_prima_completa():
    """Anexo B: horner3_float debe devolver P'' completa (no P''/2).

    P6''(x) = 6x  →  P6''(2) = 12.
    La versión literal del Alg. 8 del apunte devuelve P''/2 = 6; este test
    verifica que NO tenemos ese bug.
    """
    P, dP, d2P = horner3_float(P6.a_float(), 2.0)
    assert P == pytest.approx(-5.0)
    assert dP == pytest.approx(7.0)
    assert d2P == pytest.approx(12.0)   # NO 6.0


# ====================================================================
# Casos borde: polinomio constante y grado 1
# ====================================================================

def test_evaluacion_directa_constante():
    assert evaluacion_directa(Polinomio([7]), 5).valor == Fraction(7)


def test_horner_fraction_constante():
    assert horner_fraction(Polinomio([7]), 5).valor == Fraction(7)


def test_horner_float_constante():
    assert horner_float(Polinomio([7]), 5).valor == pytest.approx(7.0)


def test_horner_doble_fraction_constante():
    """P(x) = 7 → P(5) = 7, P'(5) = 0."""
    P, dP = horner_doble_fraction(Polinomio([7]), 5).valor
    assert P == Fraction(7)
    assert dP == Fraction(0)


def test_horner_doble_float_constante():
    P, dP = horner_doble_float([7.0], 5.0)
    assert P == pytest.approx(7.0)
    assert dP == pytest.approx(0.0)


def test_horner3_float_constante():
    P, dP, d2P = horner3_float([7.0], 5.0)
    assert P == pytest.approx(7.0)
    assert dP == pytest.approx(0.0)
    assert d2P == pytest.approx(0.0)


def test_horner_doble_grado_1():
    """P(x) = 2x + 3 → P(4) = 11, P'(4) = 2."""
    P, dP = horner_doble_fraction(Polinomio([3, 2]), 4).valor
    assert P == Fraction(11)
    assert dP == Fraction(2)


# ====================================================================
# Consistencia entre variantes
# ====================================================================

def test_horner_fraction_y_float_coinciden():
    alpha = Fraction("2.4908637")
    v_frac = horner_fraction(P6, alpha).valor
    v_flt = horner_float(P6, float(alpha)).valor
    assert float(v_frac) == pytest.approx(v_flt, abs=1e-12)


def test_evaluacion_directa_y_horner_fraction_coinciden():
    for alpha in [0, 1, -1, 2, -2, Fraction(3, 2), Fraction(-5, 3)]:
        v_dir = evaluacion_directa(P1, alpha).valor
        v_hor = horner_fraction(P1, alpha).valor
        assert v_dir == v_hor, f"alpha = {alpha}"


def test_horner_doble_fraction_y_float_coinciden():
    alpha = Fraction("1.5")
    p_f, dp_f = horner_doble_fraction(P6, alpha).valor
    p_fl, dp_fl = horner_doble_float(P6.a_float(), float(alpha))
    assert float(p_f) == pytest.approx(p_fl, abs=1e-12)
    assert float(dp_f) == pytest.approx(dp_fl, abs=1e-12)


def test_horner3_float_dp_igual_a_horner_doble_float():
    """horner3 debe devolver el mismo P y P' que horner_doble_float."""
    x = 1.7
    p1, dp1 = horner_doble_float(P6.a_float(), x)
    p3, dp3, _ = horner3_float(P6.a_float(), x)
    assert p1 == pytest.approx(p3)
    assert dp1 == pytest.approx(dp3)


# ====================================================================
# Verificación cruzada con numpy (referencia independiente)
# ====================================================================

def test_horner_vs_numpy():
    np = pytest.importorskip("numpy")
    x = 1.2345
    v_propio = horner_float(P1, x).valor
    # numpy espera coeficientes de MAYOR a MENOR
    v_numpy = float(np.polyval(list(reversed(P1.a_float())), x))
    assert v_propio == pytest.approx(v_numpy, abs=1e-12)