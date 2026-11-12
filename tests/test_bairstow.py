"""Tests de metodos/bairstow.py contra el ejemplo del apunte."""
import cmath
import math
import pytest

from core.polinomio import Polinomio
from core.errores import EntradaInvalida, NoConverge
from metodos.bairstow import (
    bairstow, es_raiz_real, _limpiar_raiz, _raices_cuadraticas,
)


# --- Polinomios de referencia ---
# P_ap(x) = x⁴ + 5x³ + 15x² + 5x - 26  → raíces 1, -2, -2+3i, -2-3i
P_ap = Polinomio([-26, 5, 15, 5, 1])

# P_cero(x) = x·P_ap(x) = x⁵ + 5x⁴ + 15x³ + 5x² - 26x  → raíces 0, 1, -2, -2±3i
P_cero = Polinomio([0, -26, 5, 15, 5, 1])

# P_doble(x) = (x-1)²(x+2) = x³ - 3x + 2  → raíces 1 (doble), -2
P_doble = Polinomio([2, -3, 0, 1])

# P_cuad(x) = x² + x - 2 = (x-1)(x+2)  → raíces 1, -2
P_cuad = Polinomio([-2, 1, 1])

# P_lineal(x) = x - 5
P_lineal = Polinomio([-5, 1])

# P_const(x) = 5
P_const = Polinomio([5])


def _tiene_raiz(raices, esperada, tol=1e-3):
    """True si alguna raíz está a menos de `tol` de la esperada."""
    return any(abs(z - esperada) < tol for z in raices)


# ====================================================================
# Helper: raíces cuadráticas y real/complejo
# ====================================================================

def test_raices_cuadraticas_discriminante_positivo():
    """x² - 3x + 2 = 0 → raíces 1, 2 (reales)."""
    r = _raices_cuadraticas(2, -3, 1)
    assert _tiene_raiz(r, complex(1, 0))
    assert _tiene_raiz(r, complex(2, 0))


def test_raices_cuadraticas_discriminante_negativo():
    """x² + 1 = 0 → raíces ±i (complejas)."""
    r = _raices_cuadraticas(1, 0, 1)
    assert _tiene_raiz(r, complex(0, 1))
    assert _tiene_raiz(r, complex(0, -1))


def test_raices_cuadraticas_discriminante_cero():
    """x² - 2x + 1 = 0 → raíz doble 1."""
    r = _raices_cuadraticas(1, -2, 1)
    assert abs(r[0] - r[1]) < 1e-10
    assert abs(r[0] - 1) < 1e-10


def test_es_raiz_real_true():
    assert es_raiz_real(complex(3, 0)) is True


def test_es_raiz_real_true_con_ruido():
    """Ruido numérico en la parte imaginaria no cuenta como complejo."""
    assert es_raiz_real(complex(3, 1e-12)) is True


def test_es_raiz_real_false():
    assert es_raiz_real(complex(-2, 3)) is False


def test_limpiar_raiz_real():
    z = _limpiar_raiz(complex(3, 1e-15))
    assert z.imag == 0.0


def test_limpiar_raiz_compleja_no_cambia():
    z = _limpiar_raiz(complex(-2, 3))
    assert z == complex(-2, 3)


# ====================================================================
# Ejemplo del apunte
# ====================================================================

def test_bairstow_ejemplo_apunte_4_raices():
    """P = x⁴ + 5x³ + 15x² + 5x - 26, r0=1, s0=-1.
    Raíces: 1, -2, -2+3i, -2-3i."""
    r = bairstow(P_ap, r0=1, s0=-1, eps=1e-3)
    assert r.convergio is True
    assert len(r.valor) == 4
    assert _tiene_raiz(r.valor, complex(1, 0))
    assert _tiene_raiz(r.valor, complex(-2, 0))
    assert _tiene_raiz(r.valor, complex(-2, 3))
    assert _tiene_raiz(r.valor, complex(-2, -3))


def test_bairstow_ejemplo_apunte_complejas_conjugadas():
    """Las raíces complejas deben venir en pares conjugados."""
    r = bairstow(P_ap, r0=1, s0=-1, eps=1e-3)
    complejas = [z for z in r.valor if not es_raiz_real(z)]
    assert len(complejas) == 2
    z1, z2 = complejas
    assert math.isclose(z1.real, z2.real, abs_tol=1e-6)
    assert math.isclose(z1.imag, -z2.imag, abs_tol=1e-6)


def test_bairstow_ejemplo_apunte_pasos_tienen_estructura():
    r = bairstow(P_ap, r0=1, s0=-1, eps=1e-3)
    for paso in r.pasos:
        assert "factor" in paso
        assert "iter" in paso
        assert "r" in paso
        assert "s" in paso
        assert "dr" in paso
        assert "ds" in paso
        assert "perturbado" in paso


# ====================================================================
# Raíces reales vs complejas
# ====================================================================

def test_bairstow_cuadratica_con_raices_reales():
    """x² + x - 2 = (x-1)(x+2) → raíces 1, -2."""
    r = bairstow(P_cuad, r0=1, s0=-1, eps=1e-6)
    assert len(r.valor) == 2
    assert _tiene_raiz(r.valor, complex(1, 0), tol=1e-6)
    assert _tiene_raiz(r.valor, complex(-2, 0), tol=1e-6)
    # Ninguna tiene parte imaginaria
    assert all(es_raiz_real(z) for z in r.valor)


def test_bairstow_cuadratica_con_raices_complejas():
    """x² + x + 1 = 0 → raíces -1/2 ± √3/2 i."""
    P = Polinomio([1, 1, 1])
    r = bairstow(P, r0=0, s0=0, eps=1e-6)
    assert len(r.valor) == 2
    assert _tiene_raiz(r.valor, complex(-0.5, math.sqrt(3)/2), tol=1e-6)
    assert _tiene_raiz(r.valor, complex(-0.5, -math.sqrt(3)/2), tol=1e-6)


# ====================================================================
# Raíz en 0
# ====================================================================

def test_bairstow_polinomio_con_raiz_en_cero():
    """P = x·(x⁴ + 5x³ + 15x² + 5x - 26).
    Las raíces son 0, 1, -2, -2±3i."""
    r = bairstow(P_cero, r0=1, s0=-1, eps=1e-3)
    assert len(r.valor) == 5
    assert _tiene_raiz(r.valor, complex(0, 0))
    assert _tiene_raiz(r.valor, complex(1, 0))
    assert _tiene_raiz(r.valor, complex(-2, 0))
    assert _tiene_raiz(r.valor, complex(-2, 3))
    assert _tiene_raiz(r.valor, complex(-2, -3))


def test_bairstow_raiz_en_cero_multiplicidad():
    """P = x²·(x-1) = x³ - x² → raíces 0 (doble), 1."""
    P = Polinomio([0, 0, -1, 1])
    r = bairstow(P, r0=0, s0=0, eps=1e-6)
    assert len(r.valor) == 3
    assert sum(1 for z in r.valor if abs(z) < 1e-6) == 2  # 0 doble
    assert _tiene_raiz(r.valor, complex(1, 0))


# ====================================================================
# Raíz doble
# ====================================================================

def test_bairstow_raiz_doble_uno():
    """(x-1)²(x+2) = x³ - 3x + 2 → raíces 1 (doble), -2."""
    r = bairstow(P_doble, r0=0, s0=0, eps=1e-6)
    assert len(r.valor) == 3
    assert sum(1 for z in r.valor if abs(z - 1) < 1e-5) == 2
    assert _tiene_raiz(r.valor, complex(-2, 0))


# ====================================================================
# Casos borde (grado 0, 1, 2)
# ====================================================================

def test_bairstow_grado_0_constante():
    r = bairstow(P_const)
    assert r.valor == []


def test_bairstow_grado_0_nulo():
    r = bairstow(Polinomio([0]))
    assert r.valor == []
    assert len(r.avisos) >= 1


def test_bairstow_grado_1():
    """x - 5 → raíz 5."""
    r = bairstow(P_lineal)
    assert len(r.valor) == 1
    assert _tiene_raiz(r.valor, complex(5, 0))


def test_bairstow_grado_2_resuelve_directo():
    """Grado 2: no itera, resuelve directo. Sin pasos."""
    r = bairstow(P_cuad)
    assert r.pasos == []
    assert len(r.valor) == 2


# ====================================================================
# Comparación con numpy
# ====================================================================

def test_bairstow_vs_numpy_ejemplo_apunte():
    np = pytest.importorskip("numpy")
    esperadas = np.roots([float(c) for c in reversed(P_ap.coef)])
    r = bairstow(P_ap, r0=1, s0=-1, eps=1e-3)
    for exp in esperadas:
        assert _tiene_raiz(r.valor, complex(exp), tol=1e-3)


def test_bairstow_vs_numpy_polinomio_grado_5():
    """x⁵ - 3x⁴ - x³ + 11x² - 12x + 4 = (x+2)(x-1)³(x-2).

    Raíces: -2, 1 (triple), 2. Bairstow NO es exacto para raíces múltiples:
    la triple puede salir como 1 real + un par complejo con imag ~1e-4.
    Por eso comparamos contra numpy con tolerancia, en vez de exigir que
    todas las raíces tengan parte imaginaria exactamente 0.
    """
    P = Polinomio([4, -12, 11, -1, -3, 1])
    np = pytest.importorskip("numpy")
    esperadas = np.roots([float(c) for c in reversed(P.coef)])
    r = bairstow(P, r0=1, s0=-1, eps=1e-6)
    assert len(r.valor) == 5
    for exp in esperadas:
        assert _tiene_raiz(r.valor, complex(exp), tol=1e-3), \
            f"raíz esperada {exp} no encontrada en {r.valor}"

# ====================================================================
# Validación de entrada
# ====================================================================

def test_bairstow_r0_no_numerico_lanza():
    with pytest.raises(EntradaInvalida):
        bairstow(P_ap, r0="abc", s0=-1)


def test_bairstow_r0_infinito_lanza():
    with pytest.raises(EntradaInvalida):
        bairstow(P_ap, r0=float("inf"), s0=-1)


def test_bairstow_eps_invalido_lanza():
    from core.errores import ToleranciaInvalida
    with pytest.raises(ToleranciaInvalida):
        bairstow(P_ap, r0=1, s0=-1, eps=0)