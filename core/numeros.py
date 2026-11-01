from fractions import Fraction
import math
from core.errores import EntradaInvalida


def parsear_numero(texto: str) -> Fraction:
    """Convierte un texto ('3/2', '-5', '1.5') a una fracción exacta."""
    try:
        return Fraction(texto.strip())
    except ValueError:
        raise EntradaInvalida(f"'{texto}' no es un número válido. Se aceptan enteros, decimales y fracciones como 3/2.")


def parsear_coeficientes(texto: str) -> list[Fraction]:
    """Convierte una cadena separada por comas o espacios en una lista de fracciones."""
    if not texto.strip():
        return []
    # Reemplaza comas por espacios y separa por espacios
    partes = texto.replace(',', ' ').split()
    return [parsear_numero(p) for p in partes]


def es_finito(numero: float) -> bool:
    """Verifica que un float no sea infinito ni NaN (útil para detectar overflow)."""
    return math.isfinite(numero)