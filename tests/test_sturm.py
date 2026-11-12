"""Tests de metodos/sturm.py contra los ejemplos del apunte.
Convención: coef[i] = coeficiente de x^i  (menor→mayor grado).
"""
from fractions import Fraction
import pytest

from core.polinomio import Polinomio
from core.errores import EntradaInvalida
from metodos.sturm import (
    sucesion_sturm, contar_raices, separar_raices, cambios_signo,
)


# --- Polinomios de referencia ---
# Caso 1 apunte (pág. 27-30): 4x⁴ - 5x² + 1 = (x-1)(x+1)(2x-1)(2x+1)
# Raíces: 1, -1, 1/2, -1/2 (todas simples)
P_caso1 = Polinomio([1, 0, -5, 0, 4])

# Caso 2 apunte (pág. 29-32): x⁵ - 3x⁴ - x³ + 11x² - 12x + 4 = (x+2)(x-1)³(x-2)
# Raíces: -2 (simple), 1 (triple), 2 (simple)
P_caso2 = Polinomio([4, -12, 11, -1, -3, 1])

# Lineal simple: x - 1
P_lineal = Polinomio([-1, 1])


# ====================================================================
# cambios_signo
# ====================================================================

def test_cambios_signo_basico():
    assert cambios_signo([1, -1, 1]) == 2


def test_cambios_signo_sin_cambios():
    assert cambios_signo([1, 1, 1]) == 0


def test_cambios_signo_salteando_ceros():
    """Un cero NO cuenta como signo: se saltea."""
    assert cambios_signo([1, 0, -1]) == 1
    assert cambios_signo([1, 0, 0, -1]) == 1
    assert cambios_signo([1, 0, -1, 0, 1]) == 2


def test_cambios_signo_todo_cero():
    assert cambios_signo([0, 0, 0]) == 0


def test_cambios_signo_lista_vacia():
    assert cambios_signo([]) == 0


# ====================================================================
# Sucesión de Sturm — Caso 1 del apunte
# ====================================================================

def test_sucesion_caso1_apunte():
    """La sucesión debe coincidir con el apunte (pág. 28):
    [4x⁴-5x²+1, 16x³-10x, 5x²-2, 18x, 2]."""
    r = sucesion_sturm(P_caso1)
    coefs = [list(p.coef) for p in r.valor]
    assert coefs == [
        [Fraction(1), Fraction(0), Fraction(-5), Fraction(0), Fraction(4)],
        [Fraction(0), Fraction(-10), Fraction(0), Fraction(16)],
        [Fraction(-2), Fraction(0), Fraction(5)],
        [Fraction(0), Fraction(18)],
        [Fraction(2)],
    ]


def test_sucesion_caso1_sin_avisos():
    """No hay raíces múltiples: no debe haber avisos."""
    r = sucesion_sturm(P_caso1)
    assert r.avisos == []


def test_sucesion_caso1_termina_en_constante():
    """El último P_m debe ser no nulo de grado 0 (constante)."""
    r = sucesion_sturm(P_caso1)
    ultimo = r.valor[-1]
    assert ultimo.grado == 0
    assert ultimo.coef[0] != 0


def test_sucesion_pasos_tienen_estructura():
    r = sucesion_sturm(P_caso1)
    for i, paso in enumerate(r.pasos):
        assert paso["i"] == i
        assert "coef" in paso
        assert isinstance(paso["coef"], list)


# ====================================================================
# Sucesión de Sturm — Caso 2 del apunte (raíces múltiples)
# ====================================================================

def test_sucesion_caso2_detecta_multiples():
    """x⁵ - 3x⁴ - x³ + 11x² - 12x + 4 tiene raíces múltiples.
    Debe avisar y rehacer la sucesión con Q = P / mcd(P, P')."""
    r = sucesion_sturm(P_caso2)
    assert len(r.avisos) == 1
    assert "múltiples" in r.avisos[0].lower()


def test_sucesion_caso2_menciona_p4_cero():
    """El aviso debe decir en qué índice aparece P_m = 0."""
    r = sucesion_sturm(P_caso2)
    assert "P_4" in r.avisos[0] or "P4" in r.avisos[0]


def test_sucesion_caso2_simplificada_termina_bien():
    """La forma simplificada también debe terminar en constante."""
    r = sucesion_sturm(P_caso2, simplificada=True)
    ultimo = r.valor[-1]
    assert ultimo.grado == 0
    assert ultimo.coef[0] != 0


# ====================================================================
# contar_raices — Caso 1 del apunte
# ====================================================================

def test_contar_raices_caso1_apunte_intervalo_completo():
    """En (-2, 2) están las 4 raíces (-1, -1/2, 1/2, 1)."""
    r = contar_raices(P_caso1, -2, 2)
    assert r.valor == 4


def test_contar_raices_caso1_positivas():
    """En (0, 2) están 1/2 y 1."""
    assert contar_raices(P_caso1, 0, 2).valor == 2


def test_contar_raices_caso1_negativas():
    """En (-2, 0) están -1 y -1/2."""
    assert contar_raices(P_caso1, -2, 0).valor == 2


def test_contar_raices_sin_raices_en_intervalo():
    """En (3, 5) no hay raíces."""
    assert contar_raices(P_caso1, 3, 5).valor == 0


def test_contar_raices_pasos_tienen_estructura():
    r = contar_raices(P_caso1, -2, 2)
    for paso in r.pasos:
        assert "i" in paso
        assert "coef" in paso
        assert "signo_a" in paso
        assert "signo_b" in paso
        assert paso["signo_a"] in (-1, 0, 1)
        assert paso["signo_b"] in (-1, 0, 1)


# ====================================================================
# contar_raices — Caso 2 (múltiples)
# ====================================================================

def test_contar_raices_caso2_cuenta_distintas():
    """x⁵ - 3x⁴ - x³ + 11x² - 12x + 4 tiene 3 raíces DISTINTAS: -2, 1, 2.
    Aunque 1 tiene multiplicidad 3, el conteo de Sturm devuelve 3."""
    r = contar_raices(P_caso2, -5, 5)
    assert r.valor == 3


def test_contar_raices_caso2_avisa_multiples():
    r = contar_raices(P_caso2, -5, 5)
    assert len(r.avisos) == 1
    assert "múltiples" in r.avisos[0].lower()


def test_contar_raices_caso2_en_intervalo_estrecho():
    """En (-3, 0) está solo -2."""
    assert contar_raices(P_caso2, -3, 0).valor == 1


# ====================================================================
# Errores de intervalo
# ====================================================================

def test_a_mayor_que_b_lanza():
    with pytest.raises(EntradaInvalida):
        contar_raices(P_caso1, 2, -2)


def test_intervalo_degenerado_lanza():
    with pytest.raises(EntradaInvalida):
        contar_raices(P_caso1, 1, 1)


def test_extremo_inferior_es_raiz_lanza():
    """P_caso1(-1) = 0. No se puede empezar en una raíz."""
    with pytest.raises(EntradaInvalida):
        contar_raices(P_caso1, -1, 2)


def test_extremo_superior_es_raiz_lanza():
    """P_caso1(1) = 0. No se puede terminar en una raíz."""
    with pytest.raises(EntradaInvalida):
        contar_raices(P_caso1, -2, 1)


def test_polinomio_nulo_lanza():
    with pytest.raises(EntradaInvalida):
        contar_raices(Polinomio([0]), -1, 1)


# ====================================================================
# separar_raices — Caso 1
# ====================================================================

def test_separar_raices_caso1_cuatro_intervalos():
    """Las 4 raíces deben quedar aisladas en 4 intervalos disjuntos."""
    r = separar_raices(P_caso1, -2, 2)
    assert len(r.valor) == 4


def test_separar_raices_caso1_cada_intervalo_tiene_una_raiz():
    """Verifica que cada subintervalo contenga exactamente 1 raíz."""
    r = separar_raices(P_caso1, -2, 2)
    raices = [Fraction(-1), Fraction(-1, 2), Fraction(1, 2), Fraction(1)]
    for a, b in r.valor:
        assert a < b
        dentro = sum(1 for x in raices if a < x < b)
        assert dentro == 1, f"Intervalo ({a}, {b}) tiene {dentro} raíces"


def test_separar_raices_caso1_ordenados():
    """Los intervalos deben venir ordenados de menor a mayor."""
    r = separar_raices(P_caso1, -2, 2)
    assert r.valor == sorted(r.valor)


def test_separar_raices_caso1_disjuntos():
    """Los intervalos no deben superponerse."""
    r = separar_raices(P_caso1, -2, 2)
    for i in range(len(r.valor) - 1):
        assert r.valor[i][1] <= r.valor[i + 1][0]


def test_separar_raices_sin_raices_devuelve_vacio():
    assert separar_raices(P_caso1, 3, 5).valor == []


# ====================================================================
# separar_raices — Caso 2 (múltiples)
# ====================================================================

def test_separar_raices_caso2_tres_intervalos():
    """Con raíces múltiples, la sucesión se rehace y se separan las distintas."""
    r = separar_raices(P_caso2, -5, 5)
    assert len(r.valor) == 3


def test_separar_raices_caso2_avisa_multiples():
    r = separar_raices(P_caso2, -5, 5)
    assert len(r.avisos) == 1


# ====================================================================
# Consistencia entre contar_raices y separar_raices
# ====================================================================

@pytest.mark.parametrize("a,b,esperado", [
    (-3, 3, 4), (-2, 2, 4), (0, 2, 2), (-2, 0, 2),
    (Fraction(3, 5), Fraction(3, 2), 1),
])
def test_count_igual_a_len_separate(a, b, esperado):
    """contar_raices y len(separar_raices) deben coincidir SIEMPRE."""
    count = contar_raices(P_caso1, Fraction(a), Fraction(b)).valor
    sep = separar_raices(P_caso1, Fraction(a), Fraction(b)).valor
    assert count == esperado
    assert len(sep) == count


# ====================================================================
# Casos borde
# ====================================================================

def test_polinomio_lineal_una_raiz():
    """x - 1 tiene 1 raíz en (0, 2)."""
    assert contar_raices(P_lineal, 0, 2).valor == 1


def test_polinomio_constante_sin_raices():
    """P(x) = 5: no tiene raíces en ningún intervalo."""
    assert contar_raices(Polinomio([5]), -10, 10).valor == 0


# ====================================================================
# Verificación cruzada con numpy (referencia independiente)
# ====================================================================

def test_contar_raices_caso1_vs_numpy():
    np = pytest.importorskip("numpy")
    raices_np = np.roots([float(c) for c in reversed(P_caso1.coef)])
    reales = [r.real for r in raices_np
              if abs(r.imag) < 1e-6 and -2 < r.real < 2]
    assert contar_raices(P_caso1, -2, 2).valor == len(reales)