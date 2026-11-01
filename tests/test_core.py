import pytest
from fractions import Fraction
from core.numeros import parsear_numero
from core.polinomio import Polinomio
from core.errores import EntradaInvalida, PolinomioInvalido


def test_parsear_numero_valido():
    assert parsear_numero("3/2") == Fraction(3, 2)
    assert parsear_numero("1.5") == Fraction(3, 2)
    assert parsear_numero("-5") == Fraction(-5, 1)


def test_parsear_numero_invalido():
    with pytest.raises(EntradaInvalida):
        parsear_numero("abc")


def test_polinomio_normalizacion():
    # El usuario escribe "0, 0, 1, 2" (que matemáticamente es x + 2)
    # Internamente debe limpiarse y guardarse de menor a mayor: [2, 1]
    p = Polinomio.desde_texto("0, 0, 1, 2")
    assert p.coef == [Fraction(2), Fraction(1)]


def test_polinomio_vacio_o_nulo():
    with pytest.raises(PolinomioInvalido):
        Polinomio.desde_texto("")  # Vacío

    with pytest.raises(PolinomioInvalido):
        Polinomio.desde_texto("0, 0, 0")  # Solo ceros


def test_polinomio_grado_y_derivada():
    # P(x) = x^3 - 5x - 3
    p = Polinomio.desde_texto("1, 0, -5, -3")
    assert p.grado == 3

    # P'(x) = 3x^2 - 5
    # En el orden interno (menor a mayor grado) debe ser: [-5, 0, 3]
    dp = p.derivada()
    assert dp.coef == [Fraction(-5), Fraction(0), Fraction(3)]