from fractions import Fraction

import pytest

from core.errores import EntradaInvalida, PolinomioInvalido
from core.polinomio import Polinomio
from gui import controlador
from metodos.evaluacion import horner_fraction


def test_raices_enteras_ejemplo_apunte():
    texto = "3 -11 -6 44 -24"
    resultado = controlador.raices(texto, "Enteras")
    p = Polinomio.desde_texto(texto)

    assert resultado.valor == [Fraction(-2), Fraction(2), Fraction(3)]
    assert all({"candidato", "valor", "es_raiz"} <= set(paso) for paso in resultado.pasos)
    for paso in resultado.pasos:
        assert paso["valor"] == horner_fraction(p, paso["candidato"]).valor
        assert paso["es_raiz"] == (paso["valor"] == 0)


def test_raices_racionales_incluye_la_raiz_fraccionaria():
    resultado = controlador.raices("3 -11 -6 44 -24", "Racionales")

    assert resultado.valor == [
        Fraction(-2),
        Fraction(2, 3),
        Fraction(2),
        Fraction(3),
    ]
    paso = next(p for p in resultado.pasos if p["candidato"] == Fraction(2, 3))
    assert paso["es_raiz"] is True
    assert paso["p"] == 2 and paso["q"] == 3


def test_raices_ambas_deduplica_y_marca_el_origen():
    resultado = controlador.raices("3 -11 -6 44 -24", "Ambas")

    assert resultado.valor == [
        Fraction(-2),
        Fraction(2, 3),
        Fraction(2),
        Fraction(3),
    ]
    candidatos = [paso["candidato"] for paso in resultado.pasos]
    assert len(candidatos) == len(set(candidatos))

    por_candidato = {paso["candidato"]: paso for paso in resultado.pasos}
    assert por_candidato[Fraction(2)]["tipo"] == "entera y racional"
    assert por_candidato[Fraction(2, 3)]["tipo"] == "racional"
    assert por_candidato[Fraction(2, 3)]["p"] == 2
    assert por_candidato[Fraction(2, 3)]["q"] == 3


def test_valor_mostrado_es_p_del_candidato_y_no_q():
    # x^3 - 2x = x(x^2 - 2). El núcleo busca sobre Q = x^2 - 2; la tabla
    # debe mostrar P(candidato), no Q(candidato).
    texto = "1 0 -2 0"
    p = Polinomio.desde_texto(texto)
    resultado = controlador.raices(texto, "Enteras")

    valores = {paso["candidato"]: paso["valor"] for paso in resultado.pasos}
    assert valores[Fraction(2)] == Fraction(4)
    assert valores[Fraction(-2)] == Fraction(-4)
    assert valores[Fraction(1)] == Fraction(-1)
    assert valores[Fraction(-1)] == Fraction(1)
    for candidato, valor in valores.items():
        assert valor == horner_fraction(p, candidato).valor


def test_raices_con_fracciones_y_raiz_cero():
    resultado = controlador.raices("1 -3/2 1/2", "Racionales")
    assert resultado.valor == [Fraction(1, 2), Fraction(1)]

    cero = controlador.raices("1 0 -1 0", "Ambas")  # x^3 - x
    assert cero.valor == [Fraction(-1), Fraction(0), Fraction(1)]
    paso_cero = next(p for p in cero.pasos if p["candidato"] == 0)
    assert paso_cero["es_raiz"] is True


def test_factorizar_raices_recupera_multiplicidad():
    info = controlador.factorizar_raices("1 -3 3 -1", [Fraction(1)])

    assert info["factores"] == [Fraction(1), Fraction(1), Fraction(1)]
    assert info["residual"].coef == [Fraction(1)]


def test_factorizar_raices_con_cero_y_coeficiente_principal():
    info = controlador.factorizar_raices(
        "1 0 -1 0", [Fraction(-1), Fraction(0), Fraction(1)]
    )
    assert info["factores"] == [Fraction(-1), Fraction(0), Fraction(1)]
    assert info["residual"].coef == [Fraction(1)]

    info = controlador.factorizar_raices(
        "3 -11 -6 44 -24",
        [Fraction(-2), Fraction(2, 3), Fraction(2), Fraction(3)],
    )
    assert info["factores"] == [
        Fraction(-2),
        Fraction(2, 3),
        Fraction(2),
        Fraction(3),
    ]
    assert info["residual"].coef == [Fraction(3)]


def test_factorizar_raices_sin_raices_no_modifica_el_residual():
    info = controlador.factorizar_raices("1 0 1", [])
    assert info["factores"] == []
    assert info["residual"].coef == [Fraction(1), Fraction(0), Fraction(1)]

    info = controlador.factorizar_raices("1 0 -1", [Fraction(2)])
    assert info["factores"] == []
    assert info["residual"].coef == [Fraction(-1), Fraction(0), Fraction(1)]


def test_raices_entradas_invalidas():
    with pytest.raises(PolinomioInvalido):
        controlador.raices("", "Ambas")
    with pytest.raises(EntradaInvalida):
        controlador.raices("1 0 -1", "otro")
