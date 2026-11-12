from fractions import Fraction
import math
import re

from core import mensajes
from core.errores import EntradaInvalida, PolinomioInvalido

def parsear_numero(texto: str) -> Fraction:
    try:
        return Fraction(texto.strip())
    except (ValueError, ZeroDivisionError):
        try:
            return Fraction(str(float(texto)))
        except (ValueError, OverflowError):
            raise EntradaInvalida(mensajes.ENTRADA_NO_NUMERO.format(texto=texto))


def parsear_coeficientes(texto: str) -> list[Fraction]:
    """Convierte una cadena separada por comas o espacios en una lista de fracciones."""
    if not texto.strip():
        return []
    # Reemplaza comas por espacios y separa por espacios
    partes = texto.replace(',', ' ').split()
    return [parsear_numero(p) for p in partes]


def _parsear_termino(term: str) -> tuple[int, Fraction]:
    """Convierte un término individual (ej: '3x^2', '-x', '5') en (grado, coeficiente)."""
    if "x" not in term.lower():
        return 0, parsear_numero(term.strip("()"))

    partes = term.lower().split("x")
    coef_str = partes[0].strip(" *()")
    exp_str = partes[1].strip(" ^*()")

    # 1. Coeficiente
    if coef_str in ("", "+"):
        coef = Fraction(1)
    elif coef_str == "-":
        coef = Fraction(-1)
    else:
        coef = parsear_numero(coef_str)

    # 2. Exponente (grado)
    if not exp_str:
        grado = 1
    else:
        try:
            grado = int(exp_str)
            if grado < 0:
                raise ValueError
        except ValueError:
            raise PolinomioInvalido(f"Exponente inválido en el término '{term}'.")

    return grado, coef


def parsear_expresion(texto: str) -> list[Fraction]:
    """Parsea una expresión algebraica completa a una lista de coeficientes [a0, a1, ..., an]."""
    t = texto.strip().replace(" ", "").replace("**", "^")
    if not t:
        raise PolinomioInvalido("La expresión no puede estar vacía.")

    if re.search(r'[\^\*]+[ \t]*-', t):
        raise PolinomioInvalido("Un polinomio no puede contener exponentes negativos.")

    terminos = [term for term in t.replace("-", "+-").split("+") if term]
    coef_por_grado: dict[int, Fraction] = {}

    for term in terminos:
        grado, coef = _parsear_termino(term)
        coef_por_grado[grado] = coef_por_grado.get(grado, Fraction(0)) + coef

    if not coef_por_grado:
        raise PolinomioInvalido("No se encontraron términos válidos en el polinomio.")

    # Reconstruye [a0, a1, ..., an] rellenando los huecos con 0
    max_grado = max(coef_por_grado.keys())
    return [coef_por_grado.get(i, Fraction(0)) for i in range(max_grado + 1)]


def es_finito(numero) -> bool:
    """True si el número es finito. Acepta int, float, Fraction; nunca crashea."""
    try:
        return math.isfinite(float(numero))
    except (TypeError, ValueError, OverflowError):
        return False


