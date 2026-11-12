import math
import sys
from core.errores import ToleranciaInvalida, EntradaInvalida
from core import mensajes

MAX_ITER_DEFAULT = 1000
MAX_ITER_TOPE    = 100_000
EPS_DEFAULT      = 1e-6
EPS_MAQUINA      = sys.float_info.epsilon   # ~2.22e-16


def validar_epsilon(eps) -> float:
    try:
        eps = float(eps)
    except (TypeError, ValueError):
        raise ToleranciaInvalida(mensajes.TOLERANCIA_MAYOR_CERO)
    if eps <= 0:
        raise ToleranciaInvalida(mensajes.TOLERANCIA_MAYOR_CERO)
    if eps < EPS_MAQUINA:
        raise ToleranciaInvalida(mensajes.TOLERANCIA_MAQUINA)
    return eps


def validar_max_iter(n) -> int:
    try:
        n = int(n)
    except (TypeError, ValueError):
        raise EntradaInvalida(mensajes.MAX_ITER_INVALIDO)
    if n <= 0:
        raise EntradaInvalida(mensajes.MAX_ITER_POSITIVO)
    if n > MAX_ITER_TOPE:
        raise EntradaInvalida(mensajes.MAX_ITER_TOPE.format(tope=MAX_ITER_TOPE))
    return n


def convergio(dx, x, eps) -> bool:
    """|dx| <= eps * max(1, |x|). Usar x = x_nuevo (el punto al que se llega)."""
    try:
        dx, x, eps = float(dx), float(x), float(eps)
    except (TypeError, ValueError):
        return False
    if not (math.isfinite(dx) and math.isfinite(x) and math.isfinite(eps)):
        return False
    return abs(dx) <= eps * max(1.0, abs(x))