"""Halley no debe declarar convergencia en un punto que no es raíz.

Los puntos críticos (P' = 0) son puntos fijos de la iteración de Halley, porque
dx = 2·P·P' / (2P'² − P·P'') tiende a 0 cuando P' → 0. El criterio
|dx| ≤ eps·max(1,|x|) se cumple sin que P sea cero. Pasa con x0 a menos de ~eps
de cualquier punto crítico (también en (x−5)²−2 partiendo de 5+1e-9) y con
polinomios sin raíces reales (x²+1). Newton no tiene ese problema.

Reproducción mínima:
    halley(Polinomio.desde_expresion("x^2 - 2"), 1e-8)   # eps por defecto = 1e-6
    -> convergio=True, valor=3e-08, P(valor) = -2   (las raíces son ±1.41421)
"""
import math

import pytest

from core.errores import DivisionPorCero
from core.polinomio import Polinomio
from metodos.evaluacion import horner_float
from metodos.newton_halley import newton, halley

" P6(x) = x³ - 5x - 3      puntos críticos en ±sqrt(5/3)"
P6 = Polinomio([-3, -5, 0, 1])
" x² - 2  punto crítico en 0"
X2_MENOS_2 = Polinomio([-2, 0, 1])
XC = math.sqrt(5 / 3)

TOL_RESIDUO = 1e-3

" (polinomio, x0) — x0 pegado a un punto crítico"
CASOS = [
    pytest.param(P6, XC + 1e-8, id="P6-cerca-de-+xc"),
    pytest.param(P6, -XC + 1e-8, id="P6-cerca-de--xc"),
    pytest.param(X2_MENOS_2, 1e-8, id="x2-2-cerca-de-0"),
]


def _correr(metodo, p, x0):
    
    try:
        return metodo(p, x0)
    except DivisionPorCero:
        return None


def _residuo(p, x):

    return abs(horner_float(p, x).valor)


@pytest.mark.xfail(
    strict=True,
    reason="Bug: Halley declara convergencia en puntos críticos (P'=0) sin que P sea 0",
)
@pytest.mark.parametrize("p, x0", CASOS)
def test_halley_no_declara_convergencia_fuera_de_una_raiz(p, x0):
    r = _correr(halley, p, x0)
    if r is None or not r.convergio:
        return
    assert _residuo(p, r.valor) < TOL_RESIDUO, (
        f"{p}, x0={x0}: Halley dice convergio=True con "
        f"valor={r.valor} pero |P(valor)|={_residuo(p, r.valor):.3g}"
    )


@pytest.mark.parametrize("p, x0", CASOS)
def test_newton_no_tiene_el_problema(p, x0):
    r = _correr(newton, p, x0)
    if r is None or not r.convergio:
        return
    assert _residuo(p, r.valor) < TOL_RESIDUO
