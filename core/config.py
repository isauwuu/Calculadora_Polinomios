from core.errores import ToleranciaInvalida
import math
# valor default
MAX_ITER = 60 #preguntar a nocera cuantas dice
EPS_DEFAULT = 1e-6 #de esta manera py representa la notacion cientifica, es equivalente a 1*10^-6


def convergio(dx, x, eps) -> bool:
    """Criterio de parada mixto para los métodos iterativos.

    Compara el paso |dx| contra una tolerancia relativa al tamaño de x, con
    un piso de 1 para que también funcione cerca de 0:
        |dx| <= eps * max(1, |x|)
    """
    try:
        dx = float(dx)
        x = float(x)
        eps = float(eps)
    except (TypeError, ValueError):
        return False
    if not (math.isfinite(dx) and math.isfinite(x) and math.isfinite(eps)):
        return False
    return abs(dx) <= eps * max(1.0, abs(x))


def epsilon_por_cifras(t: int) -> float:
    """Calcula epsilon (tolerancia) en función de t cifras de precisión."""
    if t <= 0:
        raise ToleranciaInvalida("Las cifras de precisión deben ser mayores a 0")

    # por arquitectura la maquina  no puede asegurar mas de 15 digitos de precision en floats, q es el tipo de dato q van a manejar los metodos iterativos (new,halley,bairstrow)
    if t > 15:
        raise ToleranciaInvalida(f"No se pueden garantizar {t} cifras. El máximo para este sistema es 15.")

    return 0.5 * (10 ** (1 - t))