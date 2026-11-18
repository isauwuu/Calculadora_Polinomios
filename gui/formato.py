"""Formato de números para tablas, tarjetas y títulos.

La interfaz no resuelve ningún método: este módulo solo presenta los valores
que devuelve el núcleo. Las fracciones exactas se muestran como p/q y los
floats con siete decimales, como pide el diseño.
"""

import math
import re
from fractions import Fraction

from core.polinomio import Polinomio

DECIMALES = 7
_SUPERINDICES = str.maketrans("0123456789", "⁰¹²³⁴⁵⁶⁷⁸⁹")


def con_superindices(texto):
    """Convierte x^2, x^10, etc. en x², x¹⁰ usando Unicode."""
    return re.sub(r"\^(\d+)", lambda m: m.group(1).translate(_SUPERINDICES), texto)


def formatear_float(valor, decimales=DECIMALES):
    """Float con la cantidad de decimales pedida (o '—' si no es finito)."""
    try:
        numero = float(valor)
    except (TypeError, ValueError):
        return "—"
    if not math.isfinite(numero):
        return "—"
    if abs(numero) < 0.5 * (10 ** (-decimales)):
        numero = 0.0
    return f"{numero:.{decimales}f}"


def formatear_cientifico(valor, decimales=2):
    """Notación científica breve para la línea de error de los iterativos."""
    try:
        numero = float(valor)
    except (TypeError, ValueError):
        return "—"
    if not math.isfinite(numero):
        return "—"
    return f"{numero:.{decimales}e}"


def formatear_fraccion(valor):
    """Fracción exacta como p/q; los enteros se muestran sin denominador."""
    if isinstance(valor, complex):
        return formatear_complejo(valor)
    try:
        fraccion = Fraction(valor)
    except (TypeError, ValueError, ZeroDivisionError):
        return str(valor)
    if fraccion.denominator == 1:
        return str(fraccion.numerator)
    return f"{fraccion.numerator}/{fraccion.denominator}"


def formatear_complejo(valor, decimales=DECIMALES):
    """Complejo como 'a + bi'; si la parte imaginaria es ruido, solo 'a'."""
    z = complex(valor)
    real = formatear_float(z.real, decimales)
    imag = formatear_float(abs(z.imag), decimales)
    if math.isclose(z.imag, 0.0, abs_tol=1e-9):
        return real
    if math.isclose(z.real, 0.0, abs_tol=1e-12):
        return f"{'-' if z.imag < 0 else ''}{imag}i"
    signo = "+" if z.imag >= 0 else "-"
    return f"{real} {signo} {imag}i"


def formatear_polinomio(coeficientes):
    """Polinomio legible a partir de coeficientes de menor a mayor grado."""
    try:
        return str(Polinomio(list(coeficientes)))
    except (TypeError, ValueError, ZeroDivisionError):
        return "—"
