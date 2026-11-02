import pytest
from fractions import Fraction
from core.numeros import parsear_numero
from core.polinomio import Polinomio
from core.config import epsilon_por_cifras
from core.errores import EntradaInvalida, PolinomioInvalido, ToleranciaInvalida


def test_parsear_numero_valido():
    assert parsear_numero("3/2") == Fraction(3, 2)


def test_parsear_numero_invalido():
    with pytest.raises(EntradaInvalida):
        parsear_numero("1/0")
    with pytest.raises(EntradaInvalida):
        parsear_numero("a")


def test_polinomio_desde_texto_invalido():
    with pytest.raises(PolinomioInvalido):
        Polinomio.desde_texto("")
    with pytest.raises(PolinomioInvalido):
        Polinomio.desde_texto("0 0")


def test_polinomio_coeficientes_y_derivada():
    p = Polinomio.desde_texto("0, 1, -3")
    assert p.coef == [Fraction(-3), Fraction(1)]

    p_derivada = Polinomio.desde_texto("3 0 -5 0").derivada()
    assert p_derivada.coef == [Fraction(-5), Fraction(0), Fraction(9)]  # 9x^2 - 5


def test_epsilon_por_cifras():
    assert epsilon_por_cifras(3) == pytest.approx(0.005)

    with pytest.raises(ToleranciaInvalida):
        epsilon_por_cifras(0)

    with pytest.raises(ToleranciaInvalida):
        epsilon_por_cifras(16)