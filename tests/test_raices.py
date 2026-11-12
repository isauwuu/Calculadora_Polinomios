"""Tests de metodos/raices.py: raíces enteras, racionales, multiplicidad y factorización.
Convención: coef[i] = coeficiente de x^i  (menor→mayor grado).
"""
from fractions import Fraction
import pytest

from core.polinomio import Polinomio
from metodos.raices import (
    raices_enteras,
    raices_racionales,
    divisores,
    factorizacion_string,
)


# ====================================================================
# Polinomios de referencia (coef low→high)
# ====================================================================
# P_ap(x) = 3x⁴ - 11x³ - 6x² + 44x - 24   (Ejemplo del apunte)
P_ap = Polinomio([-24, 44, -6, -11, 3])

# P_cub(x) = x³ - 6x² + 11x - 6 = (x-1)(x-2)(x-3)
P_cub = Polinomio([-6, 11, -6, 1])

# P_cuad(x) = 2x² - 5x + 2 = (2x-1)(x-2)
P_cuad = Polinomio([2, -5, 2])

# P_x2(x) = x²
P_x2 = Polinomio([0, 0, 1])

# P_xm2(x) = x² - 2  (raíces ±√2, ninguna racional)
P_xm2 = Polinomio([-2, 0, 1])

# P_xmas1(x) = x² + 1  (sin raíces reales)
P_xmas1 = Polinomio([1, 0, 1])

# P_const(x) = 5  (grado 0, sin raíces)
P_const = Polinomio([5])

# P_sturm2(x) = x⁵ - 3x⁴ - x³ + 11x² - 12x + 4 = (x+2)(x-1)³(x-2)
# (caso 2 de Sturm en el apunte)
P_sturm2 = Polinomio([4, -12, 11, -1, -3, 1])


# ====================================================================
# divisores
# ====================================================================

def test_divisores_positivo():
    assert divisores(12) == [-12, -6, -4, -3, -2, -1, 1, 2, 3, 4, 6, 12]


def test_divisores_negativo():
    assert divisores(-12) == divisores(12)


def test_divisores_cero():
    assert divisores(0) == []


def test_divisores_uno():
    assert divisores(1) == [-1, 1]


def test_divisores_primo():
    assert divisores(7) == [-7, -1, 1, 7]


# ====================================================================
# raices_enteras — ejemplos del apunte
# ====================================================================

def test_enteras_ejemplo_apunte():
    """3x⁴ - 11x³ - 6x² + 44x - 24 tiene 3 raíces enteras: -2, 2, 3."""
    r = raices_enteras(P_ap).valor
    assert r == [Fraction(-2), Fraction(2), Fraction(3)]


def test_enteras_cubica_factorizable():
    r = raices_enteras(P_cub).valor
    assert r == [Fraction(1), Fraction(2), Fraction(3)]


def test_enteras_cuadratica_con_racional_no_entera():
    """2x² - 5x + 2 = (2x-1)(x-2): solo 2 es entera."""
    r = raices_enteras(P_cuad).valor
    assert r == [Fraction(2)]


def test_enteras_sin_raices_enteras():
    r = raices_enteras(P_xm2).valor
    assert r == []


def test_enteras_x2_raiz_doble_cero():
    """x² tiene raíz doble en 0. Se devuelve UNA vez (raíces distintas)."""
    r = raices_enteras(P_x2).valor
    assert r == [Fraction(0)]


def test_enteras_x3_mas_2x2():
    """x³ + 2x² = x²(x+2). Raíces distintas: 0, -2."""
    P = Polinomio([0, 0, 2, 1])
    r = raices_enteras(P).valor
    assert r == [Fraction(-2), Fraction(0)]


def test_enteras_constante_no_cero():
    """P(x) = 5: no tiene raíces."""
    r = raices_enteras(P_const).valor
    assert r == []


def test_enteras_polinomio_nulo():
    r = raices_enteras(Polinomio([0]))
    assert r.valor == []
    assert len(r.avisos) == 1
    assert "infinitas" in r.avisos[0].lower()


def test_enteras_lineal_con_raiz_entera():
    r = raices_enteras(Polinomio([-4, 2])).valor   # 2x - 4 = 2(x-2)
    assert r == [Fraction(2)]


def test_enteras_lineal_sin_raiz_entera():
    r = raices_enteras(Polinomio([-1, 2])).valor   # 2x - 1
    assert r == []


# ====================================================================
# raices_racionales — ejemplos del apunte
# ====================================================================

def test_racionales_ejemplo_apunte_las_4():
    """Corrección v2: las CUATRO raíces son racionales (2/3, 2, 3, -2)."""
    r = raices_racionales(P_ap).valor
    assert r == [Fraction(-2), Fraction(2, 3), Fraction(2), Fraction(3)]


def test_racionales_cuadratica_con_racional():
    r = raices_racionales(P_cuad).valor
    assert r == [Fraction(1, 2), Fraction(2)]


def test_racionales_lineal_racional():
    r = raices_racionales(Polinomio([-1, 2])).valor   # 2x - 1
    assert r == [Fraction(1, 2)]


def test_racionales_sin_raices_racionales():
    """x² - 2 tiene raíces reales ±√2, no racionales."""
    r = raices_racionales(P_xm2).valor
    assert r == []


def test_racionales_x2_mas_1_vacio():
    """x² + 1 no tiene raíces reales ni racionales."""
    r = raices_racionales(P_xmas1).valor
    assert r == []


def test_racionales_x2_raiz_doble_cero():
    r = raices_racionales(P_x2).valor
    assert r == [Fraction(0)]


def test_racionales_constante_no_cero():
    r = raices_racionales(P_const).valor
    assert r == []


# ====================================================================
# Invariante: enteras ⊆ racionales
# ====================================================================

@pytest.mark.parametrize("P", [P_ap, P_cub, P_cuad, P_x2, P_xm2, P_xmas1, P_const])
def test_invariante_enteras_subset_racionales(P):
    """Toda raíz entera es una raíz racional. Debe cumplirse siempre."""
    ent = set(raices_enteras(P).valor)
    rac = set(raices_racionales(P).valor)
    assert ent <= rac, f"enteras {ent} no están contenidas en racionales {rac}"


# ====================================================================
# Formato de Resultado (lo que consume la GUI)
# ====================================================================

def test_pasos_tienen_formato_correcto_enteras():
    r = raices_enteras(P_ap)
    for paso in r.pasos:
        assert "candidato" in paso
        assert "valor" in paso
        assert "es_raiz" in paso
        assert isinstance(paso["candidato"], Fraction)
        assert isinstance(paso["valor"], Fraction)
        assert isinstance(paso["es_raiz"], bool)


def test_pasos_tienen_p_y_q_en_racionales():
    r = raices_racionales(P_ap)
    for paso in r.pasos:
        assert "candidato" in paso
        assert "valor" in paso
        assert "es_raiz" in paso
        assert "p" in paso
        assert "q" in paso
        # La fracción debe coincidir con p/q
        assert paso["candidato"] == Fraction(paso["p"], paso["q"])


def test_iteraciones_es_cantidad_de_pasos():
    r = raices_enteras(P_cub)
    assert r.iteraciones == len(r.pasos)


def test_convergio_es_true_siempre():
    """Los métodos exactos no convergen: siempre terminan."""
    assert raices_enteras(P_ap).convergio is True
    assert raices_racionales(P_ap).convergio is True


# ====================================================================
# Raíces duplicadas: no se repiten en `valor`
# ====================================================================

def test_raiz_doble_cero_no_duplica():
    """x² tiene raíz 0 con multiplicidad 2, pero se devuelve una vez en valor."""
    r = raices_enteras(P_x2).valor
    assert r.count(Fraction(0)) == 1


def test_raiz_doble_uno_no_duplica():
    """(x-1)² = x² - 2x + 1 → se devuelve [1], no [1, 1]."""
    P = Polinomio([1, -2, 1])
    r = raices_enteras(P).valor
    assert r == [Fraction(1)]


def test_raiz_triple_uno_no_duplica():
    """(x-1)³ = x³ - 3x² + 3x - 1 → se devuelve [1], no [1, 1, 1]."""
    P = Polinomio([-1, 3, -3, 1])
    r = raices_enteras(P).valor
    assert r == [Fraction(1)]


# ====================================================================
# Coeficientes racionales: se manejan con mcm
# ====================================================================

def test_racionales_con_coeficientes_fraccionarios():
    """P(x) = (1/2)x - 1 = 0 → x = 2."""
    P = Polinomio([Fraction(-1), Fraction(1, 2)])
    r = raices_enteras(P).valor
    assert r == [Fraction(2)]


def test_racionales_con_coeficientes_fraccionarios_racional():
    """P(x) = (1/2)x - 1/3 = 0 → x = 2/3."""
    P = Polinomio([Fraction(-1, 3), Fraction(1, 2)])
    r = raices_racionales(P).valor
    assert r == [Fraction(2, 3)]


# ====================================================================
# Multiplicidad de raíces
# ====================================================================

def test_multiplicidad_x2_cero_doble():
    """x² → raíz 0 con multiplicidad 2."""
    r = raices_enteras(P_x2)
    assert r.valor == [Fraction(0)]
    assert r.multiplicidades == {Fraction(0): 2}


def test_multiplicidad_cuadratica_x_menos_1_al_cuadrado():
    """(x-1)² = x² - 2x + 1 → raíz 1 con multiplicidad 2."""
    P = Polinomio([1, -2, 1])
    r = raices_enteras(P)
    assert r.valor == [Fraction(1)]
    assert r.multiplicidades[Fraction(1)] == 2


def test_multiplicidad_cubica_x_menos_1_al_cubo():
    """(x-1)³ = x³ - 3x² + 3x - 1 → raíz 1 con multiplicidad 3."""
    P = Polinomio([-1, 3, -3, 1])
    r = raices_enteras(P)
    assert r.valor == [Fraction(1)]
    assert r.multiplicidades[Fraction(1)] == 3


def test_multiplicidad_apunte_todas_simples():
    """3x⁴ - 11x³ - 6x² + 44x - 24 → 4 raíces simples (mult 1 cada una)."""
    r = raices_racionales(P_ap)
    assert all(m == 1 for m in r.multiplicidades.values())
    assert len(r.multiplicidades) == 4


def test_multiplicidad_sturm_caso2_raiz_triple():
    """x⁵ - 3x⁴ - x³ + 11x² - 12x + 4 = (x+2)(x-1)³(x-2).
    Raíces: -2 (mult 1), 1 (mult 3), 2 (mult 1)."""
    r = raices_enteras(P_sturm2)
    assert r.multiplicidades[Fraction(-2)] == 1
    assert r.multiplicidades[Fraction(1)] == 3
    assert r.multiplicidades[Fraction(2)] == 1


def test_multiplicidad_cero_y_otra_mezcladas():
    """x²(x-1) = x³ - x² → 0 con mult 2, 1 con mult 1."""
    P = Polinomio([0, 0, -1, 1])
    r = raices_enteras(P)
    assert r.multiplicidades[Fraction(0)] == 2
    assert r.multiplicidades[Fraction(1)] == 1


def test_multiplicidad_racional_no_entera():
    """(2x-1)² = 4x² - 4x + 1 → raíz 1/2 con multiplicidad 2.
    Solo la encuentra raices_racionales, no raices_enteras."""
    P = Polinomio([1, -4, 4])
    assert raices_enteras(P).valor == []
    r = raices_racionales(P)
    assert r.valor == [Fraction(1, 2)]
    assert r.multiplicidades[Fraction(1, 2)] == 2


def test_multiplicidad_suma_no_excede_grado():
    """Σ multiplicidades nunca puede superar el grado del polinomio."""
    for P in [P_ap, P_cub, P_sturm2,
              Polinomio([-1, 3, -3, 1]),
              Polinomio([0, 0, -1, 1])]:
        r = raices_racionales(P)
        suma = sum(r.multiplicidades.values())
        assert suma <= P.grado, f"suma {suma} > grado {P.grado} en {P}"


def test_multiplicidad_suma_igual_grado_cuando_factoriza_completo():
    """Si todas las raíces son racionales, Σ multiplicidades == grado."""
    for P in [P_ap, P_cub, P_sturm2,
              Polinomio([-1, 3, -3, 1]),
              Polinomio([0, 0, -1, 1]),
              Polinomio([1, -2, 1])]:
        r = raices_racionales(P)
        suma = sum(r.multiplicidades.values())
        assert suma == P.grado, f"suma {suma} != grado {P.grado} en {P}"


def test_multiplicidad_vacia_en_polinomio_sin_raices():
    """x² + 1 no tiene raíces racionales → multiplicidades = {}."""
    r = raices_racionales(P_xmas1)
    assert r.valor == []
    assert r.multiplicidades == {}


# ====================================================================
# factorizacion_string
# ====================================================================

def test_factorizacion_apunte():
    """3x⁴ - 11x³ - 6x² + 44x - 24 = 3(x+2)(x-2/3)(x-2)(x-3)."""
    r = raices_racionales(P_ap)
    s = factorizacion_string(P_ap, r.multiplicidades)
    assert "3" in s
    assert "(x + 2)" in s
    assert "(x - 2/3)" in s
    assert "(x - 2)" in s
    assert "(x - 3)" in s


def test_factorizacion_con_multiplicidad():
    """(x-1)³ = (x-1)^3."""
    P = Polinomio([-1, 3, -3, 1])
    r = raices_enteras(P)
    s = factorizacion_string(P, r.multiplicidades)
    assert s == "(x - 1)^3"


def test_factorizacion_con_resto_no_factorizable():
    """(x-1)(x²+1) = x³ - x² + x - 1. Solo 1 es raíz racional;
    queda el resto (x² + 1) al final."""
    P = Polinomio([-1, 1, -1, 1])
    r = raices_racionales(P)
    s = factorizacion_string(P, r.multiplicidades)
    assert "(x - 1)" in s
    assert "x^2 + 1" in s


def test_factorizacion_sin_raices():
    """x² + 1 no tiene raíces racionales: factorizacion_string = str(p)."""
    r = raices_racionales(P_xmas1)
    s = factorizacion_string(P_xmas1, r.multiplicidades)
    assert s == str(P_xmas1)


def test_factorizacion_x_cuando_raiz_es_cero():
    """x·(x-2) = x² - 2x → factorización contiene 'x' y '(x - 2)'."""
    P = Polinomio([0, -2, 1])
    r = raices_enteras(P)
    s = factorizacion_string(P, r.multiplicidades)
    assert "x" in s
    assert "(x - 2)" in s


def test_factorizacion_multiplicidad_cero_y_raiz():
    """x²(x - 1) = x³ - x² → 'x^2' y '(x - 1)'."""
    P = Polinomio([0, 0, -1, 1])
    r = raices_enteras(P)
    s = factorizacion_string(P, r.multiplicidades)
    assert "x^2" in s
    assert "(x - 1)" in s