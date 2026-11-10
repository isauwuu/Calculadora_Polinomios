import math

import numpy as np
import pytest

from core.config import convergio
from core.errores import DivisionPorCero, EntradaInvalida, ToleranciaInvalida
from core.polinomio import Polinomio
from metodos.newton_halley import halley, newton


def test_convergio_mixto():
    assert convergio(1e-7, 0.0, 1e-6)
    assert convergio(1e-4, 1e6, 1e-6)      # tolerancia relativa al tamaño de x
    assert not convergio(1e-4, 0.0, 1e-6)
    assert not convergio(float("nan"), 1.0, 1e-6)


def test_newton_ejemplo_apunte():
    p = Polinomio.desde_texto("1 0 -5 -3")
    r = newton(p, 2, eps=1e-3)

    assert r.convergio is True
    assert r.iteraciones == 4
    assert r.valor == pytest.approx(2.4908637, abs=1e-7)
    assert r.error == pytest.approx(0.0002877, abs=1e-7)
    assert len(r.pasos) == 4

    # Paso 2 del diseño: n=2, x=2,5139789, P=0,318678, P'=13,96027
    paso2 = r.pasos[2]
    assert paso2["n"] == 2
    assert paso2["x"] == pytest.approx(2.5139789, abs=1e-7)
    assert paso2["p"] == pytest.approx(0.318678, abs=1e-6)
    assert paso2["dp"] == pytest.approx(13.96027, abs=1e-5)

    for paso in r.pasos:
        assert set(paso) == {"n", "x", "p", "dp", "x_sig", "dx"}

    # Coherencia: x_sig de una fila es el x de la siguiente.
    for actual, siguiente in zip(r.pasos, r.pasos[1:]):
        assert actual["x_sig"] == siguiente["x"]
    assert r.pasos[-1]["x_sig"] == r.valor
    assert r.error == abs(r.pasos[-1]["dx"])


def test_newton_contra_numpy():
    p = Polinomio.desde_texto("1 0 -5 -3")
    r = newton(p, 2, eps=1e-12)
    raices = np.roots([1, 0, -5, -3])
    assert min(abs(r.valor - raiz) for raiz in raices) < 1e-10


def test_newton_ciclo_no_converge():
    p = Polinomio.desde_texto("1 0 -2 2")  # x^3 - 2x + 2
    r = newton(p, 0, eps=1e-6, max_iter=10)

    assert r.convergio is False
    assert r.iteraciones == 10
    assert r.avisos
    xs = [paso["x"] for paso in r.pasos]
    assert xs[:6] == pytest.approx([0.0, 1.0, 0.0, 1.0, 0.0, 1.0])


def test_newton_raiz_doble_convergencia_lineal():
    p = Polinomio.desde_texto("1 0 -3 2")  # (x - 1)^2 (x + 2)
    r = newton(p, 2, eps=1e-6)

    assert r.convergio is True
    assert 15 <= r.iteraciones <= 30
    assert r.valor == pytest.approx(1.0, abs=1e-5)

    errores = [abs(paso["dx"]) for paso in r.pasos]
    razones = [errores[i + 1] / errores[i] for i in range(len(errores) - 6, len(errores) - 1)]
    assert all(0.4 < razon < 0.65 for razon in razones)


def test_newton_derivada_nula():
    p = Polinomio.desde_texto("1 0 -3 1")  # x^3 - 3x + 1
    with pytest.raises(DivisionPorCero) as exc:
        newton(p, 1, eps=1e-6)
    assert isinstance(exc.value.pasos, list)
    assert exc.value.pasos == []  # falla en el primer paso


def test_newton_punto_inicial_no_finito():
    p = Polinomio.desde_texto("1 0 -5 -3")
    with pytest.raises(DivisionPorCero):
        newton(p, math.inf)


def test_halley_mas_rapido_que_newton():
    p = Polinomio.desde_texto("1 0 -5 -3")
    rn = newton(p, 2, eps=1e-6)
    rh = halley(p, 2, eps=1e-6)

    assert rh.convergio is True
    assert rh.iteraciones < rn.iteraciones
    assert rh.valor == pytest.approx(2.490863615361032, abs=1e-12)
    assert len(rh.pasos) == rh.iteraciones

    for paso in rh.pasos:
        assert set(paso) == {"n", "x", "p", "dp", "d2p", "x_sig", "dx"}
        # d2p es P'' completa: para x^3 - 5x - 3, P'' = 6x
        assert paso["d2p"] == pytest.approx(6 * paso["x"], abs=1e-10)


def test_halley_derivada_nula():
    p = Polinomio.desde_texto("1 0 -3 1")
    with pytest.raises(DivisionPorCero) as exc:
        halley(p, 1, eps=1e-6)
    assert exc.value.pasos == []


def test_parametros_invalidos():
    p = Polinomio.desde_texto("1 0 -5 -3")
    for eps in (0, -1e-6, math.inf, float("nan"), "abc"):
        with pytest.raises(ToleranciaInvalida):
            newton(p, 2, eps=eps)
        with pytest.raises(ToleranciaInvalida):
            halley(p, 2, eps=eps)

    with pytest.raises(EntradaInvalida):
        newton(p, 2, max_iter=0)
    with pytest.raises(EntradaInvalida):
        halley(p, 2, max_iter=-3)


def test_newton_valor_no_finito():
    # Coeficientes enormes: P(1e308) desborda a inf.
    p = Polinomio([1e308, 1e308, 1e308])
    with pytest.raises(DivisionPorCero):
        newton(p, 1e308)
