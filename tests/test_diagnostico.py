import math

from core.polinomio import Polinomio
from metodos.diagnostico import analizar
from metodos.newton_halley import newton


def _pasos(xs, dxs):
    return [{"x": x, "dx": dx} for x, dx in zip(xs, dxs)]


def test_analizar_ciclo_de_periodo_2():
    pasos = _pasos([0.0, 1.0, 0.0, 1.0, 0.0], [1.0, -1.0, 1.0, -1.0, 1.0])
    d = analizar(pasos, 1e-6)

    assert d["ciclo"] == (0, 2, 2)
    assert 0 in d["filas_rojas"]
    assert 2 in d["filas_rojas"]


def test_analizar_ciclo_con_newton():
    p = Polinomio.desde_texto("1 0 -2 2")
    r = newton(p, 0, eps=1e-6, max_iter=10)

    assert r.convergio is False
    assert r.diagnostico["ciclo"] is not None
    assert r.diagnostico["ciclo"][2] == 2


def test_analizar_error_creciente():
    d = analizar(_pasos([1, 2, 3, 4], [0.1, 0.01, 0.02, 0.04]), 1e-6)

    assert d["creciente"] is True
    assert d["filas_rojas"] == [1, 2, 3]


def test_analizar_convergencia_lineal():
    d = analizar(_pasos([1, 2, 3, 4, 5], [1.0, 0.8, 0.4, 0.2, 0.1]), 1e-6)

    assert d["creciente"] is False
    assert d["ratio_lineal"] == 0.5


def test_analizar_raiz_doble_newton():
    p = Polinomio.desde_texto("1 0 -3 2")
    r = newton(p, 2, eps=1e-6)

    assert r.diagnostico["ratio_lineal"] is not None
    assert 0.4 < r.diagnostico["ratio_lineal"] < 0.65


def test_analizar_lista_vacia_o_mal_formada_no_lanza():
    vacio = {"ciclo": None, "creciente": False, "ratio_lineal": None, "filas_rojas": []}
    assert analizar([]) == vacio
    assert analizar(None) == vacio
    assert analizar([{}, {"x": "no es número", "dx": "tampoco"}]) == vacio
    assert analizar(_pasos([1, 2, 3, 4], [1, math.nan, 2, 3]))["creciente"] is False
