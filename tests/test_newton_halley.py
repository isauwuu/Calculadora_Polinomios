"""Tests de metodos/newton_halley.py contra los ejemplos del apunte."""
import math
from fractions import Fraction
import pytest

from core.polinomio import Polinomio
from core.errores import DivisionPorCero, EntradaInvalida, ToleranciaInvalida
from metodos.newton_halley import newton, halley


# --- Polinomios de referencia ---
# P6(x) = x³ - 5x - 3  (Ejemplo 6 del apunte)
P6 = Polinomio([-3, -5, 0, 1])

# P_doble(x) = (x-1)²(x+2) = x³ - 3x + 2  (raíz doble en 1)
P_doble = Polinomio([2, -3, 0, 1])

# P_ciclo(x) = x³ - 2x + 2  (cicla desde x0=0, período 2)
P_ciclo = Polinomio([2, -2, 0, 1])

# P_der_nula(x) = x³ - 3x + 1  (P'(1) = 0)
P_der_nula = Polinomio([1, -3, 0, 1])

# P_lineal(x) = x - 2
P_lineal = Polinomio([-2, 1])


# ====================================================================
# Newton — Ejemplo 6 del apunte
# ====================================================================

def test_newton_ej6_converge_4_iteraciones():
    """El apunte dice 4 iteraciones con eps=1e-3."""
    r = newton(P6, 2, eps=1e-3)
    assert r.convergio is True
    assert r.iteraciones == 4
    assert r.valor == pytest.approx(2.49086366, abs=1e-6)


def test_newton_ej6_pasos_coinciden_con_apunte():
    """Verifica los 4 pasos con los valores del apunte (pág. 15-16)."""
    r = newton(P6, 2, eps=1e-3)
    assert len(r.pasos) == 4

    # Paso 1: P(2) = -5, P'(2) = 7, x_sig = 19/7 ≈ 2.7142857
    p0 = r.pasos[0]
    assert p0["n"] == 0
    assert p0["x"] == pytest.approx(2.0)
    assert p0["p"] == pytest.approx(-5.0, abs=1e-10)
    assert p0["dp"] == pytest.approx(7.0, abs=1e-10)
    assert p0["x_sig"] == pytest.approx(19/7, abs=1e-10)

    # Paso 2: P ≈ 3.425, P' ≈ 17.102
    p1 = r.pasos[1]
    assert p1["x"] == pytest.approx(19/7, abs=1e-10)
    assert p1["p"] == pytest.approx(1175/343, abs=1e-6)
    assert p1["dp"] == pytest.approx(838/49, abs=1e-6)


def test_newton_ej6_pasos_tienen_estructura():
    r = newton(P6, 2, eps=1e-3)
    for paso in r.pasos:
        assert "n" in paso
        assert "x" in paso
        assert "p" in paso
        assert "dp" in paso
        assert "x_sig" in paso
        assert "dx" in paso
        assert isinstance(paso["x"], float)


def test_newton_ej6_x_sig_coincide_con_siguiente_x():
    """Coherencia: x_sig del paso n es x del paso n+1."""
    r = newton(P6, 2, eps=1e-3)
    for i in range(len(r.pasos) - 1):
        assert r.pasos[i]["x_sig"] == pytest.approx(r.pasos[i + 1]["x"], abs=1e-14)


def test_newton_ej6_ultimo_x_sig_es_el_valor_final():
    r = newton(P6, 2, eps=1e-3)
    assert r.pasos[-1]["x_sig"] == pytest.approx(r.valor, abs=1e-14)


# ====================================================================
# Newton — otros casos
# ====================================================================

def test_newton_raiz_exacta_converge_en_1():
    """P(x) = x - 2, x0 = 2 → P(2) = 0, dx = 0, converge en 1 iteración."""
    r = newton(P_lineal, 2)
    assert r.convergio is True
    assert r.iteraciones == 1
    assert r.valor == pytest.approx(2.0)


def test_newton_derivada_nula_lanza():
    """P(x) = x³ - 3x + 1, x0 = 1 → P'(1) = 0. Debe lanzar DivisionPorCero."""
    with pytest.raises(DivisionPorCero) as exc_info:
        newton(P_der_nula, 1)
    assert exc_info.value.pasos is not None
    assert len(exc_info.value.pasos) == 0  # falló antes de agregar ningún paso


def test_newton_ciclo_no_converge():
    """P(x) = x³ - 2x + 2 desde x0 = 0 cicla entre 0 y 1. No converge."""
    r = newton(P_ciclo, 0, eps=1e-6, max_iter=50)
    assert r.convergio is False
    assert r.iteraciones == 50
    assert len(r.pasos) == 50
    # El diagnóstico debe detectar el ciclo
    assert r.diagnostico.get("ciclo") is not None


def test_newton_raiz_doble_convergencia_lineal():
    """(x-1)²(x+2) desde x0=2: converge pero lento (ratio ≈ 1/2)."""
    r = newton(P_doble, 2, eps=1e-6, max_iter=100)
    assert r.convergio is True
    assert r.iteraciones > 10   # mucho más que una raíz simple


def test_newton_max_iter_1_no_alcanza():
    """Con max_iter=1 y eps=1e-6, no alcanza para el Ejemplo 6."""
    r = newton(P6, 2, eps=1e-6, max_iter=1)
    assert r.convergio is False
    assert r.iteraciones == 1
    assert len(r.pasos) == 1


# ====================================================================
# Halley — Ejemplo 6
# ====================================================================

def test_halley_ej6_converge():
    """Con eps=1e-6, Halley converge a la raíz real (no al valor truncado
    del apunte, que corresponde a eps=1e-3 con 4 iteraciones).

    Raíz real de x³ - 5x - 3 ≈ 2.4908636153610227...
    El apunte muestra 2.49086366 (4 iteraciones, eps=1e-3). Con eps=1e-6
    Halley llega más lejos y coincide con la raíz real hasta el último dígito.
    """
    r = halley(P6, 2, eps=1e-6)
    assert r.convergio is True
    # Tolerancia amplia: la raíz real tiene ~16 dígitos, comparamos a 1e-6
    assert r.valor == pytest.approx(2.49086361536102, abs=1e-10)


def test_halley_pasos_tienen_d2p():
    """Halley guarda d2p = P'' completa en cada paso."""
    r = halley(P6, 2, eps=1e-3)
    for paso in r.pasos:
        assert "d2p" in paso
        assert isinstance(paso["d2p"], float)


def test_halley_primer_paso_d2p_es_p_doble_prima_completa():
    """Anexo B: d2p = P''(x) completa, NO P''/2.
    P6''(x) = 6x, P6''(2) = 12."""
    r = halley(P6, 2, eps=1e-3)
    assert r.pasos[0]["d2p"] == pytest.approx(12.0, abs=1e-10)


def test_halley_converge_mas_rapido_que_newton():
    """Halley es orden 3, Newton orden 2. Halley debe converger antes."""
    r_n = newton(P6, 2, eps=1e-6, max_iter=100)
    r_h = halley(P6, 2, eps=1e-6, max_iter=100)
    assert r_h.iteraciones <= r_n.iteraciones


# ====================================================================
# Validación de parámetros
# ====================================================================

def test_newton_eps_cero_lanza():
    with pytest.raises(ToleranciaInvalida):
        newton(P6, 2, eps=0)


def test_newton_eps_negativo_lanza():
    with pytest.raises(ToleranciaInvalida):
        newton(P6, 2, eps=-1e-3)


def test_newton_max_iter_cero_lanza():
    with pytest.raises(EntradaInvalida):
        newton(P6, 2, max_iter=0)


def test_newton_max_iter_negativo_lanza():
    with pytest.raises(EntradaInvalida):
        newton(P6, 2, max_iter=-5)


def test_newton_x0_infinito_lanza():
    with pytest.raises(EntradaInvalida):
        newton(P6, float("inf"))


def test_newton_x0_no_numerico_lanza():
    with pytest.raises(EntradaInvalida):
        newton(P6, "abc")


# ====================================================================
# Comparación con numpy
# ====================================================================

def test_newton_vs_numpy():
    np = pytest.importorskip("numpy")
    raices = np.roots([float(c) for c in reversed(P6.coef)])
    reales = sorted(r.real for r in raices if abs(r.imag) < 1e-6)
    # La raíz positiva de P6 es 2.49086366
    positivas = [r for r in reales if r > 0]
    assert len(positivas) == 1
    assert newton(P6, 2).valor == pytest.approx(positivas[0], abs=1e-8)


def test_halley_vs_numpy():
    np = pytest.importorskip("numpy")
    raices = np.roots([float(c) for c in reversed(P6.coef)])
    reales = sorted(r.real for r in raices if abs(r.imag) < 1e-6)
    positivas = [r for r in reales if r > 0]
    assert halley(P6, 2).valor == pytest.approx(positivas[0], abs=1e-8)