"""Tests de la capa core. Ejecutar con: python -m pytest tests/ -v"""
from fractions import Fraction
import pytest

from core.polinomio import Polinomio
from core.numeros import parsear_numero, es_finito
from core.config import validar_epsilon, validar_max_iter
from core.errores import PolinomioInvalido, ToleranciaInvalida, EntradaInvalida


# ---------- Orden interno ----------
def test_orden_interno_menor_a_mayor():
    p = Polinomio.desde_texto("1, 2, 3")
    assert p.coef == [Fraction(3), Fraction(2), Fraction(1)]
    assert p.grado == 2


# ---------- B1: polinomio nulo ----------
@pytest.mark.parametrize("entrada", ["0", "0, 0", "0, 0, 0"])
def test_desde_texto_rechaza_polinomio_nulo(entrada):
    with pytest.raises(PolinomioInvalido):
        Polinomio.desde_texto(entrada)


def test_desde_expresion_rechaza_polinomio_nulo():
    with pytest.raises(PolinomioInvalido):
        Polinomio.desde_expresion("0")


# ---------- B2: notación científica ----------
def test_parsear_numero_notacion_cientifica():
    assert parsear_numero("1e-3") == Fraction(1, 1000)
    assert parsear_numero("2.5E2") == Fraction(250, 1)


# ---------- B3: epsilon y max_iter ----------
@pytest.mark.parametrize("eps", [0, -1e-3, 1e-30])
def test_validar_epsilon_rechaza_invalidos(eps):
    with pytest.raises(ToleranciaInvalida):
        validar_epsilon(eps)


def test_validar_epsilon_acepta_valido():
    assert validar_epsilon(1e-6) == 1e-6


def test_validar_max_iter_acepta_valido():
    assert validar_max_iter(100) == 100


@pytest.mark.parametrize("n", [0, -5, 10**7])
def test_validar_max_iter_rechaza_invalidos(n):
    with pytest.raises(EntradaInvalida):
        validar_max_iter(n)


# ---------- B4: es_finito robusto ----------
def test_es_finito_float_normal():
    assert es_finito(1.5) is True


def test_es_finito_infinito():
    assert es_finito(float("inf")) is False


def test_es_finito_int_gigante():
    # El caso que crasheaba: int de 400 dígitos
    assert es_finito(10**400) is False


def test_es_finito_fraction_gigante():
    assert es_finito(Fraction(10**400, 1)) is False


def test_es_finito_texto():
    assert es_finito("abc") is False