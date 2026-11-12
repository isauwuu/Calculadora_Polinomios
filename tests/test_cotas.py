"""Tests de metodos/cotas.py contra los ejemplos del apunte.
Convención: coef[i] = coeficiente de x^i  (menor→mayor grado).

Nota: para cotas con raíz k-ésima (k ≥ 2), el código redondea a milésimas
hacia arriba, por eso se usa pytest.approx con abs=0.01.
"""
from fractions import Fraction
import pytest

from core.polinomio import Polinomio
from metodos.cotas import (
    lagrange, laguerre, newton_cotas, cota_implicacion, todas_las_cotas,
    _normalizar, _polinomio_inverso, _polinomio_negativo,
    _polinomio_negativo_inverso, _sin_raices_positivas, _techo_raiz_k,
)


# --- Polinomios de referencia ---
# P_ap(x) = 3x⁴ - 11x³ - 6x² + 44x - 24
P_ap = Polinomio([-24, 44, -6, -11, 3])

# P_sturm(x) = 4x⁴ - 5x² + 1 = (x+1)(x+1/2)(x-1)(x-1/2)
P_sturm = Polinomio([1, 0, -5, 0, 4])

# P_sin_pos(x) = x² + 1 (no tiene raíces positivas)
P_sin_pos = Polinomio([1, 0, 1])

# P_const(x) = 5
P_const = Polinomio([5])

# P_lineal(x) = 2x - 1
P_lineal = Polinomio([-1, 2])


# ====================================================================
# Helpers internos
# ====================================================================

def test_normalizar_positivo_no_cambia():
    p = Polinomio([1, 2, 3])
    assert _normalizar(p).coef == p.coef


def test_normalizar_negativo_cambia_signo():
    p = Polinomio([1, 2, -3])
    n = _normalizar(p)
    assert n.coef == [-1, -2, 3]
    assert n.coef[-1] > 0


def test_sin_raices_positivas_verdadero():
    assert _sin_raices_positivas(P_sin_pos) is True


def test_sin_raices_positivas_falso():
    assert _sin_raices_positivas(P_ap) is False


def test_polinomio_inverso_invierte_coeficientes():
    """P(1/y) · y^n invierte los coeficientes."""
    p = Polinomio([1, 2, 3])   # 1 + 2x + 3x²
    q = _polinomio_inverso(p)   # y³·P(1/y) = 1·y² + 2·y + 3
    assert q.coef == [3, 2, 1]


def test_polinomio_negativo_signo_alternado():
    """P(-y): cambian de signo los coeficientes de grado impar."""
    p = Polinomio([1, 2, 3, 4])   # 1 + 2x + 3x² + 4x³
    q = _polinomio_negativo(p)    # 1 - 2y + 3y² - 4y³
    assert q.coef == [1, -2, 3, -4]


def test_techo_raiz_k_k1_es_exacto():
    """Para k=1, no se redondea."""
    assert _techo_raiz_k(Fraction(44, 24), 1) == Fraction(44, 24)


def test_techo_raiz_k_k2_es_cota_superior():
    """Para k=2, el resultado al cuadrado debe ser >= el valor original."""
    valor = Fraction(44, 3)
    cota = _techo_raiz_k(valor, 2)
    assert cota * cota >= valor


def test_techo_raiz_k_k3_es_cota_superior():
    valor = Fraction(11, 24)
    cota = _techo_raiz_k(valor, 3)
    assert cota * cota * cota >= valor


# ====================================================================
# Lagrange: valores del apunte
# ====================================================================

def test_lagrange_sup_pos_apunte():
    assert lagrange(P_ap).valor["sup_pos"] == Fraction(9)


def test_lagrange_inf_pos_apunte():
    assert lagrange(P_ap).valor["inf_pos"] == Fraction(6, 17)


def test_lagrange_inf_neg_apunte_aproximado():
    """El apunte da -4.83. Tu código da -483/100 exacto (k=2, denominador 100)."""
    v = float(lagrange(P_ap).valor["inf_neg"])
    assert v == pytest.approx(-4.83, abs=0.01)


def test_lagrange_sup_neg_apunte_aproximado():
    """El apunte da -0.565. Tu código da -250/443 ≈ -0.5643."""
    v = float(lagrange(P_ap).valor["sup_neg"])
    assert v == pytest.approx(-0.565, abs=0.01)


def test_lagrange_polinomio_sturm_sup_pos():
    """4x⁴ - 5x² + 1: coefs high→low [4, 0, -5, 0, 1].
    Primer negativo en k=2 (coef -5), A = 5.
    Lagrange: 1 + (5/4)^(1/2) ≈ 2.118 (no 2.25 — ese valor es de implicación)."""
    v = lagrange(P_sturm).valor["sup_pos"]
    assert float(v) == pytest.approx(1 + (5/4) ** 0.5, abs=0.01)


# ====================================================================
# Laguerre: valores del apunte
# ====================================================================

def test_laguerre_valores_apunte():
    r = laguerre(P_ap)
    assert r.valor["sup_pos"] == Fraction(5)
    assert r.valor["inf_pos"] == Fraction(1, 2)
    assert r.valor["inf_neg"] == Fraction(-3)
    assert r.valor["sup_neg"] == Fraction(-1)


# ====================================================================
# Newton: valores del apunte
# ====================================================================

def test_newton_valores_apunte():
    r = newton_cotas(P_ap)
    assert r.valor["sup_pos"] == Fraction(4)
    assert r.valor["inf_pos"] == Fraction(1, 2)
    assert r.valor["inf_neg"] == Fraction(-3)
    assert r.valor["sup_neg"] == Fraction(-1)


# ====================================================================
# Implicación: valores del apunte
# ====================================================================

def test_implicacion_sturm_apunte():
    """4x⁴ - 5x² + 1: |r| ≤ 1 + max(0/4, 5/4, 0/4, 1/4) = 9/4 = 2.25."""
    r = cota_implicacion(P_sturm)
    assert r.valor["sup_pos"] == Fraction(9, 4)
    assert r.valor["inf_neg"] == Fraction(-9, 4)


def test_implicacion_simetrica():
    """La implicación da un intervalo simétrico [-B, B]."""
    r = cota_implicacion(P_ap)
    assert r.valor["sup_pos"] == -r.valor["inf_neg"]


# ====================================================================
# Invariante: las raíces reales caen dentro de las cotas
# ====================================================================

@pytest.mark.parametrize("metodo", [lagrange, laguerre, newton_cotas])
def test_cotas_contienen_raices_reales(metodo):
    """Las raíces reales de P_ap deben caer dentro de las cotas del metodo."""
    np = pytest.importorskip("numpy")
    raices_np = np.roots([float(c) for c in reversed(P_ap.coef)])
    reales = [r.real for r in raices_np if abs(r.imag) < 1e-6]

    r = metodo(P_ap)
    for raiz in reales:
        if raiz > 0:
            assert float(r.valor["inf_pos"]) <= raiz <= float(r.valor["sup_pos"]), \
                f"raíz {raiz} fuera de [{r.valor['inf_pos']}, {r.valor['sup_pos']}]"
        elif raiz < 0:
            assert float(r.valor["inf_neg"]) <= raiz <= float(r.valor["sup_neg"]), \
                f"raíz {raiz} fuera de [{r.valor['inf_neg']}, {r.valor['sup_neg']}]"


def test_implicacion_contiene_todas_las_raices_complejas():
    """La implicación contiene a TODAS las raíces (reales y complejas)."""
    np = pytest.importorskip("numpy")
    raices_np = np.roots([float(c) for c in reversed(P_ap.coef)])
    B = float(cota_implicacion(P_ap).valor["sup_pos"])
    for z in raices_np:
        assert abs(z) <= B + 1e-9


# ====================================================================
# Casos borde
# ====================================================================

def test_lagrange_grado_0():
    r = lagrange(P_const)
    assert r.valor["sup_pos"] == 0
    assert r.valor["inf_pos"] == 0


def test_laguerre_grado_0():
    r = laguerre(P_const)
    assert r.valor["sup_pos"] == 0


def test_newton_grado_0():
    r = newton_cotas(P_const)
    assert r.valor["sup_pos"] == 0


def test_implicacion_grado_0():
    r = cota_implicacion(P_const)
    assert r.valor["sup_pos"] == 0


def test_lagrange_sin_raices_positivas():
    """x² + 1 no tiene raíces positivas → cota superior positiva = 0."""
    r = lagrange(P_sin_pos)
    assert r.valor["sup_pos"] == 0


def test_lagrange_polinomio_con_principal_negativo():
    """-3x⁴ + 11x³ + 6x² - 44x + 24 tiene las mismas raíces que P_ap
    (multiplicado por -1), entonces las cotas deben coincidir."""
    P_neg = Polinomio([24, -44, 6, 11, -3])
    r_pos = lagrange(P_ap)
    r_neg = lagrange(P_neg)
    assert r_pos.valor["sup_pos"] == r_neg.valor["sup_pos"]


def test_todas_las_cotas_devuelve_cuatro_resultados():
    d = todas_las_cotas(P_ap)
    assert set(d.keys()) == {"lagrange", "laguerre", "newton", "implicacion"}
    for metodo, res in d.items():
        assert hasattr(res, "valor"), f"{metodo} no devolvió Resultado"


# ====================================================================
# Formato de Resultado (lo que consume la GUI)
# ====================================================================

def test_resultado_tiene_cuatro_cotas():
    r = lagrange(P_ap)
    for clave in ["inf_pos", "sup_pos", "inf_neg", "sup_neg"]:
        assert clave in r.valor
        assert isinstance(r.valor[clave], Fraction)


def test_pasos_tienen_estructura_correcta():
    r = lagrange(P_ap)
    assert len(r.pasos) == 4
    for paso in r.pasos:
        assert "cota" in paso
        assert "metodo" in paso
        assert "valor" in paso


def test_lagrange_pasos_tienen_k_y_A():
    r = lagrange(P_ap)
    paso_sup_pos = next(p for p in r.pasos if p["cota"] == "sup_pos")
    assert paso_sup_pos["k"] == 1   # primer negativo en índice 1 (coef -11 de x³)
    assert paso_sup_pos["A"] == 24  # max |negativos| = max(11, 6, 24) = 24