import math

import numpy as np
import pytest

from core.errores import EntradaInvalida, NoConverge, ToleranciaInvalida
from core.polinomio import Polinomio
from metodos.bairstow import bairstow, es_raiz_real


CLAVES_PASO = {"factor", "iter", "r", "s", "dr", "ds", "perturbado"}


def _misma_lista(esperadas, obtenidas, tol):
    """Compara dos listas de raíces sin importar el orden."""
    if len(esperadas) != len(obtenidas):
        return False
    restantes = list(obtenidas)
    for z in esperadas:
        indice = min(range(len(restantes)), key=lambda k: abs(restantes[k] - z))
        if abs(restantes[indice] - z) > tol:
            return False
        restantes.pop(indice)
    return True


def _complejo(real, imag=0.0):
    return complex(real, imag)


def test_bairstow_ejemplo_apunte():
    # x^4 + 5x^3 + 15x^2 + 5x - 26
    p = Polinomio.desde_texto("1 5 15 5 -26")
    r = bairstow(p, r0=1, s0=-1, eps=1e-3)

    assert r.convergio is True
    assert r.iteraciones == 5
    assert len(r.pasos) == 5
    esperadas = [_complejo(1), _complejo(-2), _complejo(-2, 3), _complejo(-2, -3)]
    assert _misma_lista(esperadas, r.valor, 2e-6)

    # Clasificación real/compleja con tolerancia, no con imag == 0.
    reales = [z for z in r.valor if es_raiz_real(z)]
    complejas = [z for z in r.valor if not es_raiz_real(z)]
    assert len(reales) == 2
    assert len(complejas) == 2
    assert all(z.imag == 0 for z in reales)
    assert _misma_lista([_complejo(-2, 3), _complejo(-2, -3)], complejas, 2e-6)

    # Primer paso del ejemplo principal del apunte (pág. 35).
    primero = r.pasos[0]
    assert set(primero) == CLAVES_PASO
    assert primero["factor"] == 1
    assert primero["iter"] == 1
    assert primero["r"] == pytest.approx(1.0)
    assert primero["s"] == pytest.approx(-1.0)
    assert primero["dr"] == pytest.approx(-1.9902439024390244)
    assert primero["ds"] == pytest.approx(4.678048780487805)
    assert primero["perturbado"] is False

    # La fila guarda (r, s) y el paso (dr, ds) que se aplica desde ahí.
    for actual, siguiente in zip(r.pasos, r.pasos[1:]):
        assert actual["r"] + actual["dr"] == pytest.approx(siguiente["r"])
        assert actual["s"] + actual["ds"] == pytest.approx(siguiente["s"])
    assert r.pasos[-1]["r"] + r.pasos[-1]["dr"] == pytest.approx(-1.0000003068, abs=1e-9)
    assert r.pasos[-1]["s"] + r.pasos[-1]["ds"] == pytest.approx(2.0000011823, abs=1e-9)
    assert r.error == pytest.approx(max(abs(r.pasos[-1]["dr"]), abs(r.pasos[-1]["ds"])))

    for paso in r.pasos:
        assert set(paso) == CLAVES_PASO
        assert isinstance(paso["factor"], int)
        assert isinstance(paso["iter"], int)
        assert isinstance(paso["perturbado"], bool)
        assert paso["factor"] == 1
        assert all(math.isfinite(paso[k]) for k in ("r", "s", "dr", "ds"))


def test_bairstow_mayor_precision_contra_numpy():
    p = Polinomio.desde_texto("1 5 15 5 -26")
    r = bairstow(p, r0=1, s0=-1, eps=1e-12)

    esperadas = list(np.roots([1, 5, 15, 5, -26]))
    assert _misma_lista(esperadas, r.valor, 1e-8)
    assert r.convergio is True


@pytest.mark.parametrize(
    "texto",
    [
        "1 0 0 -2",        # x^3 - 2
        "1 0 -5 -3",       # x^3 - 5x - 3
        "1 0 0 0 1",       # x^4 + 1
        "1 0 0 0 -1",      # x^4 - 1
        "1 -6 11 -6",      # (x - 1)(x - 2)(x - 3)
    ],
)
def test_bairstow_contra_numpy_roots(texto):
    p = Polinomio.desde_texto(texto)
    r = bairstow(p, eps=1e-8)

    esperadas = list(np.roots(list(reversed(p.a_float()))))
    assert _misma_lista(esperadas, r.valor, 1e-6)
    assert all(math.isfinite(z.real) and math.isfinite(z.imag) for z in r.valor)


@pytest.mark.parametrize(
    "raices",
    [
        [-2, 1, 4],
        [-1, 0, 3],
        [1 + 2j, 1 - 2j, -3],
        [-4 + 1j, -4 - 1j, 2 + 3j, 2 - 3j],
        [1 + 2j, 1 - 2j, 2 + 3j, 2 - 3j, -1, 5],
    ],
)
def test_bairstow_raices_conocidas_generadas_con_numpy(raices):
    # numpy solo se usa en tests para generar/comparar, nunca en el método.
    coeficientes_desc = np.poly(raices)
    assert np.max(np.abs(coeficientes_desc.imag)) < 1e-9
    coeficientes = [int(round(c.real)) for c in coeficientes_desc]

    # Polinomio guarda los coeficientes de menor a mayor grado.
    p = Polinomio(list(reversed(coeficientes)))
    r = bairstow(p, eps=1e-8)

    assert _misma_lista(raices, r.valor, 1e-5)


def test_bairstow_deflacta_y_numera_los_factores():
    # Grado 6: se extraen dos factores cuadráticos y queda una cuadrática final.
    raices = [1 + 1j, 1 - 1j, 2 + 2j, 2 - 2j, 3, 4]
    coeficientes_desc = np.poly(raices)
    coeficientes = [int(round(c.real)) for c in coeficientes_desc]
    p = Polinomio(list(reversed(coeficientes)))

    r = bairstow(p, eps=1e-8)

    assert _misma_lista(raices, r.valor, 1e-5)
    assert {paso["factor"] for paso in r.pasos} == {1, 2}
    for factor in (1, 2):
        iteraciones = [paso["iter"] for paso in r.pasos if paso["factor"] == factor]
        assert iteraciones == list(range(1, len(iteraciones) + 1))


def test_bairstow_polinomios_de_grado_uno_y_dos():
    lineal = bairstow(Polinomio.desde_texto("1 -3"), eps=1e-9)
    assert lineal.valor == pytest.approx([3 + 0j])
    assert lineal.pasos == []
    assert lineal.avisos

    cuadratica = bairstow(Polinomio.desde_texto("1 0 1"), eps=1e-9)  # x^2 + 1
    assert _misma_lista([1j, -1j], cuadratica.valor, 1e-12)
    assert cuadratica.pasos == []
    assert cuadratica.avisos

    con_fracciones = bairstow(Polinomio.desde_texto("1 -3/2 1/2"), eps=1e-9)
    assert _misma_lista([1 + 0j, 0.5 + 0j], con_fracciones.valor, 1e-12)


def test_bairstow_raiz_en_cero():
    # x^5 + 5x^4 + 15x^3 + 5x^2 - 26x tiene una raíz simple en 0.
    p = Polinomio.desde_texto("1 5 15 5 -26 0")
    r = bairstow(p, r0=1, s0=-1, eps=1e-8)

    esperadas = [0j, 1 + 0j, -2 + 0j, -2 + 3j, -2 - 3j]
    assert _misma_lista(esperadas, r.valor, 1e-6)
    assert any("en 0" in aviso for aviso in r.avisos)


def test_bairstow_potencias_de_x():
    # x^4: cuatro raíces en 0, sin iterar.
    r = bairstow(Polinomio.desde_texto("1 0 0 0 0"))
    assert r.valor == [0j, 0j, 0j, 0j]
    assert r.iteraciones == 0
    assert r.pasos == []
    assert r.avisos

    # x^3 - x = x(x - 1)(x + 1)
    r = bairstow(Polinomio.desde_texto("1 0 -1 0"))
    assert _misma_lista([0j, 1 + 0j, -1 + 0j], r.valor, 1e-7)


def test_bairstow_constante_y_nulo():
    constante = bairstow(Polinomio([5]))
    assert constante.valor == []
    assert constante.pasos == []
    assert constante.avisos

    nulo = bairstow(Polinomio([0]))
    assert nulo.valor == []
    assert any("infinitas" in aviso for aviso in nulo.avisos)


def test_bairstow_raiz_multiple_usa_variante_mejorada():
    # (x - 1)^3: el Horner estándar no converge y se usa la variante de la pág. 39.
    p = Polinomio.desde_texto("1 -3 3 -1")
    r = bairstow(p, eps=1e-6)

    assert r.convergio is True
    assert _misma_lista([1 + 0j, 1 + 0j, 1 + 0j], r.valor, 1e-4)
    assert any("mejorada" in aviso for aviso in r.avisos)


def test_bairstow_detecta_determinante_casi_nulo():
    p = Polinomio.desde_texto("1 0 0 0 -1")  # x^4 - 1
    r = bairstow(p, eps=1e-9)

    assert any(paso["perturbado"] for paso in r.pasos)
    assert any("perturb" in aviso for aviso in r.avisos)
    assert _misma_lista([1 + 0j, -1 + 0j, 1j, -1j], r.valor, 1e-7)


def test_bairstow_no_converge_lleva_pasos():
    p = Polinomio.desde_texto("1 5 15 5 -26")
    with pytest.raises(NoConverge) as exc:
        bairstow(p, r0=1, s0=-1, eps=1e-12, max_iter=1)

    assert exc.value.pasos
    for paso in exc.value.pasos:
        assert set(paso) == CLAVES_PASO


def test_bairstow_parametros_invalidos():
    p = Polinomio.desde_texto("1 5 15 5 -26")

    for eps in (0, -1e-6, math.inf, float("nan"), "abc"):
        with pytest.raises(ToleranciaInvalida):
            bairstow(p, eps=eps)

    for max_iter in (0, -2, "abc"):
        with pytest.raises(EntradaInvalida):
            bairstow(p, max_iter=max_iter)

    for r0, s0 in ((math.inf, 0), (0, math.nan), ("a", 0), (0, None)):
        with pytest.raises(EntradaInvalida):
            bairstow(p, r0=r0, s0=s0)


def test_es_raiz_real_usa_tolerancia():
    assert es_raiz_real(2 + 0j)
    assert es_raiz_real(2 + 1e-10j)
    assert not es_raiz_real(2 + 1e-6j)
    assert not es_raiz_real(1j)
