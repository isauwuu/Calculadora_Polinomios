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


def test_cotas_ejemplo_apunte():
    resultado = controlador.cotas("3 -11 -6 44 -24")

    assert resultado.valor["lagrange"]["sup_pos"] == Fraction(9)
    assert resultado.valor["lagrange"]["inf_pos"] == Fraction(6, 17)
    assert resultado.valor["laguerre"]["sup_pos"] == Fraction(5)
    assert resultado.valor["newton"]["sup_pos"] == Fraction(4)

    ajustado = resultado.valor["ajustado"]
    assert ajustado["sin_raices"] is False
    assert ajustado["cero_es_raiz"] is False
    assert ajustado["inf"] == Fraction(-3)
    assert ajustado["sup"] == Fraction(4)
    assert ajustado["neg"] == (Fraction(-3), Fraction(-1))
    assert ajustado["pos"] == (Fraction(1, 2), Fraction(4))

    assert len(resultado.pasos) == 13
    assert {paso["metodo"] for paso in resultado.pasos} == {
        "lagrange",
        "laguerre",
        "newton",
        "implicacion",
    }


def test_cotas_sin_raices_reales_y_con_raiz_cero():
    sin_reales = controlador.cotas("1 0 1")
    assert sin_reales.valor["ajustado"]["sin_raices"] is True
    assert sin_reales.valor["ajustado"]["cero_es_raiz"] is False
    assert sin_reales.valor["implicacion"]["sup_pos"] == Fraction(2)

    con_cero = controlador.cotas("1 0 0 0")
    assert con_cero.valor["ajustado"]["sin_raices"] is True
    assert con_cero.valor["ajustado"]["cero_es_raiz"] is True
    assert any("0 es raíz" in aviso for aviso in con_cero.avisos)

    constante = controlador.cotas("5")
    assert constante.valor["ajustado"]["sin_raices"] is True
    assert any("constante" in aviso for aviso in constante.avisos)


def test_sturm_ejemplo_apunte():
    resultado = controlador.sturm("4 0 -5 0 1", "-2", "2")

    assert resultado.valor["cantidad"] == 4
    assert len(resultado.valor["intervalos"]) == 4
    assert resultado.iteraciones == 4
    assert len(resultado.pasos) == 5
    assert [paso["signo_a"] for paso in resultado.pasos] == [1, -1, 1, -1, 1]
    assert [paso["signo_b"] for paso in resultado.pasos] == [1, 1, 1, 1, 1]
    assert all("intervalo" not in paso for paso in resultado.pasos)

    for a, b in resultado.valor["intervalos"]:
        assert a < b


def test_sturm_raices_multiples_y_extremo_que_es_raiz():
    resultado = controlador.sturm("1 -3 -1 11 -12 4", "-5", "5")
    assert resultado.valor["cantidad"] == 3
    assert any("múltiples" in aviso for aviso in resultado.avisos)

    with pytest.raises(EntradaInvalida) as exc:
        controlador.sturm("4 0 -5 0 1", "-1", "2")
    assert exc.value.pasos
    assert any(paso["signo_a"] == 0 for paso in exc.value.pasos)


def test_sturm_intervalo_invalido():
    with pytest.raises(EntradaInvalida):
        controlador.sturm("1 0 -1", "1", "1")
    with pytest.raises(EntradaInvalida):
        controlador.sturm("1 0 -1", "2", "1")


def test_bairstow_ejemplo_apunte():
    resultado = controlador.bairstow("1 5 15 5 -26", "1", "-1", "1e-3", "100")

    esperadas = [1 + 0j, -2 + 0j, -2 + 3j, -2 - 3j]
    assert len(resultado.valor) == len(esperadas)
    for esperada in esperadas:
        assert min(abs(z - esperada) for z in resultado.valor) < 2e-6
    assert resultado.convergio is True
    assert resultado.iteraciones == 5
    assert len(resultado.pasos) == 5

    ultimo = resultado.pasos[-1]
    assert "raices_factor" in ultimo
    assert len(ultimo["raices_factor"]) == 2
    for paso in resultado.pasos:
        assert {"factor", "iter", "r", "s", "dr", "ds", "perturbado"} <= set(paso)


def test_bairstow_raiz_cero_y_resolucion_directa():
    con_cero = controlador.bairstow("1 0 -1 0", "0", "0", "1e-9", "100")
    assert any(abs(z) < 1e-7 for z in con_cero.valor)
    assert any("en 0" in aviso for aviso in con_cero.avisos)

    cuadratica = controlador.bairstow("1 0 1", "0", "0", "1e-9", "100")
    assert sorted(z.imag for z in cuadratica.valor) == [-1.0, 1.0]
    assert cuadratica.pasos == []
    assert cuadratica.avisos


def test_bairstow_no_converge_con_pasos_y_entradas_invalidas():
    from core.errores import NoConverge, ToleranciaInvalida

    with pytest.raises(NoConverge) as exc:
        controlador.bairstow("1 5 15 5 -26", "1", "-1", "1e-12", "1")
    assert exc.value.pasos

    with pytest.raises(ToleranciaInvalida):
        controlador.bairstow("1 0 1", "0", "0", "0", "10")
    with pytest.raises(EntradaInvalida):
        controlador.bairstow("1 0 1", "0", "0", "1e-6", "0")
