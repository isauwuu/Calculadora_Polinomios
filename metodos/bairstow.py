import cmath
import math

from core.config import (
    EPS_DEFAULT, MAX_ITER_DEFAULT,
    validar_epsilon, validar_max_iter, convergio,
)
from core.errores import EntradaInvalida, NoConverge
from core.polinomio import Polinomio
from core.resultado import Resultado

# El determinante se considera casi nulo comparado con los términos que lo forman.
_DET_REL = 1e-14
_MAX_PERTURBACIONES = 5
_TOL_REAL = 1e-9


# ---------------------------------------------------------------------------
# Horner cuadrático y raíces del factor
# ---------------------------------------------------------------------------

def _horner_cuadratico_float(
    coef: list[float], r: float, s: float, mejorado: bool = False
) -> list[float]:
    """Doble Horner cuadrático para el factor x² - r·x - s.

    coef va de menor a mayor grado y ya es float. Devuelve la fila b:
    b[n]...b[2] son el cociente y b[1], b[0] el resto b1·x + b0.

    Con `mejorado=True` se usa la variante del apunte (pág. 39-40), que
    suma también r·b1 en b0. Al converger b1 = b0 = 0 y el factor es el
    mismo; la variante mejorada suele converger antes cuando hay raíces
    múltiples.
    """
    n = len(coef) - 1
    b = [0.0] * (n + 1)
    b[n] = coef[n]
    if n >= 1:
        b[n - 1] = coef[n - 1] + r * b[n]
    for i in range(n - 2, 0, -1):
        b[i] = coef[i] + r * b[i + 1] + s * b[i + 2]
    # Defensivo: b[2] solo existe si n >= 2
    if mejorado and n >= 2:
        b[0] = coef[0] + r * b[1] + s * b[2]
    else:
        b[0] = coef[0] + s * b[2]
    return b


def _raices_cuadraticas(a0: float, a1: float, a2: float) -> list[complex]:
    """Raíces de a2·x² + a1·x + a0 = 0 con cmath (sirve para Disc < 0).

    Fórmula estándar: x = (-a1 ± √(a1² - 4·a2·a0)) / (2·a2).
    Ojo: NO usamos la FormulaCuad del pseudocódigo del apunte, que tiene
    un bug en el signo del discriminante. Esta es la versión correcta.
    """
    discriminante = a1 * a1 - 4.0 * a2 * a0
    raiz = cmath.sqrt(discriminante)
    return [
        complex((-a1 + raiz) / (2.0 * a2)),
        complex((-a1 - raiz) / (2.0 * a2)),
    ]


def _raices_factor(r: float, s: float) -> list[complex]:
    """Raíces de x² - r·x - s = 0: (r ± √(r² + 4s)) / 2.

    Se apoya en _raices_cuadraticas con a2=1, a1=-r, a0=-s.
    """
    return _raices_cuadraticas(-s, -r, 1.0)


def es_raiz_real(z: complex) -> bool:
    """Decide si una raíz compleja es real usando tolerancia, no imag == 0."""
    return math.isclose(complex(z).imag, 0.0, abs_tol=_TOL_REAL)


def _limpiar_raiz(z: complex) -> complex:
    """Pone en cero la parte imaginaria cuando es ruido numérico."""
    z = complex(z)
    if es_raiz_real(z):
        return complex(z.real, 0.0)
    return z


# ---------------------------------------------------------------------------
# Refinamiento de (r, s)
# ---------------------------------------------------------------------------

def _validar_inicio(r0, s0) -> tuple[float, float]:
    """Convierte r0 y s0 a float finito."""
    try:
        r0 = float(r0)
        s0 = float(s0)
    except (TypeError, ValueError):
        raise EntradaInvalida("Los valores iniciales r0 y s0 deben ser números.")
    if not (math.isfinite(r0) and math.isfinite(s0)):
        raise EntradaInvalida("Los valores iniciales r0 y s0 deben ser finitos.")
    return r0, s0


def _arranques(r0: float, s0: float) -> list[tuple[float, float]]:
    """Arranque pedido por el usuario y algunos de respaldo, sin repetidos."""
    candidatos = [
        (r0, s0),
        (1.0, -1.0),
        (-1.0, 1.0),
        (0.0, 0.0),
        (1.0, 1.0),
        (-1.0, -1.0),
        (0.5, 0.5),
        (-0.5, -0.5),
    ]
    unicos = []
    for r, s in candidatos:
        if not any(
            math.isclose(r, otro_r, rel_tol=0.0, abs_tol=1e-12)
            and math.isclose(s, otro_s, rel_tol=0.0, abs_tol=1e-12)
            for otro_r, otro_s in unicos
        ):
            unicos.append((r, s))
    return unicos


def _refinar_factor(
    coef: list[float],
    r: float,
    s: float,
    eps: float,
    max_iter: int,
    factor: int,
    mejorado: bool = False,
) -> tuple[bool, float, float, list[dict]]:
    """Refina (r, s) para que x² - r·x - s sea factor de P.

    Usa el doble Horner cuadrático del apunte y el sistema 2x2 de Newton.
    Si el determinante es casi nulo perturba (r, s) y sigue; si no logra
    converger en max_iter devuelve ok=False con los pasos calculados.
    """
    pasos: list[dict] = []
    perturbaciones = 0

    for it in range(1, max_iter + 1):
        b = _horner_cuadratico_float(coef, r, s, mejorado)
        c = _horner_cuadratico_float(b, r, s, mejorado)

        if not all(math.isfinite(v) for v in b + c):
            return False, r, s, pasos

        det = c[2] * c[2] - c[1] * c[3]
        escala = max(1.0, abs(c[2] * c[2]), abs(c[1] * c[3]))

        if not math.isfinite(det) or abs(det) <= _DET_REL * escala:
            if perturbaciones >= _MAX_PERTURBACIONES:
                return False, r, s, pasos
            # Perturbación positiva y determinista: no hay corrección de Newton.
            dr = 1e-3 * (1.0 + abs(r))
            ds = -1e-3 * (1.0 + abs(s))
            pasos.append({
                "factor": factor, "iter": it, "r": r, "s": s,
                "dr": dr, "ds": ds, "perturbado": True,
            })
            r += dr
            s += ds
            perturbaciones += 1
            continue

        dr = (-b[1] * c[2] + b[0] * c[3]) / det
        ds = (-b[0] * c[2] + b[1] * c[1]) / det

        if not (math.isfinite(dr) and math.isfinite(ds)):
            return False, r, s, pasos

        r_sig = r + dr
        s_sig = s + ds
        pasos.append({
            "factor": factor, "iter": it, "r": r, "s": s,
            "dr": dr, "ds": ds, "perturbado": False,
        })

        if not (math.isfinite(r_sig) and math.isfinite(s_sig)):
            return False, r, s, pasos

        r, s = r_sig, s_sig
        if convergio(dr, r, eps) and convergio(ds, s, eps):
            return True, r, s, pasos

    return False, r, s, pasos


def _deflactar(coef: list[float], r: float, s: float) -> list[float]:
    """Divide P por x² - r·x - s y devuelve el cociente en float."""
    b = _horner_cuadratico_float(coef, r, s)
    return b[2:]


# ---------------------------------------------------------------------------
# API pública
# ---------------------------------------------------------------------------

def bairstow(
    p: Polinomio,
    r0=0.0,
    s0=0.0,
    eps=EPS_DEFAULT,
    max_iter=MAX_ITER_DEFAULT,
) -> Resultado:
    """Método de Bairstow: factores cuadráticos y raíces reales/complejas.

    Trabaja con el factor x² - r·x - s (Algoritmo de Bairstow del apunte).
    Para cada factor refina (r, s) con el doble Horner cuadrático y el sistema
    de Newton; si el determinante es casi nulo perturba (r, s), y si un
    arranque no converge prueba otros. Si ningún arranque converge con el
    Horner estándar, prueba la variante mejorada del apunte. Después deflacta
    P y repite hasta que el cociente sea lineal o cuadrático, que se resuelve
    con cmath. Las potencias de x (raíces en 0) se extraen antes de iterar.

    Convención: el factor es x² - r·x - s. Para el TP (x² + p·x + q):
    r = -p, s = -q. Esa conversión se hace en la GUI, no acá.

    valor = lista de raíces complejas (las reales tienen parte imaginaria 0).
    pasos = un diccionario por iteración con factor, iter, r, s, dr, ds y
            perturbado.
    """
    eps = validar_epsilon(eps)
    max_iter = validar_max_iter(max_iter)
    r0, s0 = _validar_inicio(r0, s0)

    coef = p.a_float()  # una sola conversión a float, fuera de los bucles
    grado = p.grado

    if grado == 0:
        if p.coef[0] == 0:
            return Resultado(valor=[], avisos=["El polinomio nulo tiene infinitas raíces."])
        return Resultado(valor=[], avisos=["Un polinomio constante no tiene raíces."])

    # Si el término independiente es 0, x es factor. Se extraen todas las
    # potencias de x antes de Bairstow: evita arrancar con s = 0, donde el
    # sistema de Newton queda degenerado.
    raices: list[complex] = []
    avisos: list[str] = []
    while len(coef) > 1 and coef[0] == 0:
        raices.append(complex(0.0, 0.0))
        coef = coef[1:]
    if raices:
        avisos.append(f"Se extrajeron {len(raices)} raíz(es) en 0 antes de buscar factores.")

    grado = len(coef) - 1
    if grado == 0:
        avisos.append("Después de extraer las raíces en 0, el polinomio es constante.")
        return Resultado(valor=raices, avisos=avisos)

    if grado == 1:
        raiz = complex(-coef[0] / coef[1], 0.0)
        avisos.append("El factor restante es lineal: se resolvió directamente.")
        return Resultado(valor=raices + [_limpiar_raiz(raiz)], avisos=avisos)

    if grado == 2:
        cuadraticas = [_limpiar_raiz(z) for z in _raices_cuadraticas(coef[0], coef[1], coef[2])]
        avisos.append("El factor restante es cuadrático: se resolvió directamente.")
        return Resultado(valor=raices + cuadraticas, avisos=avisos)

    pasos: list[dict] = []
    trabajo = list(coef)
    factor = 1
    uso_arranque_alternativo = False
    uso_variante_mejorada = False
    hubo_perturbacion = False

    while len(trabajo) - 1 > 2:
        ok = False
        pasos_intento: list[dict] = []
        # Primero el doble Horner estándar. Si ningún arranque converge, se
        # prueba la variante mejorada de la página 39.
        for mejorado in (False, True):
            for indice, (ri, si) in enumerate(_arranques(r0, s0)):
                ok, r, s, pasos_intento = _refinar_factor(
                    trabajo, ri, si, eps, max_iter, factor, mejorado
                )
                if ok:
                    if indice > 0:
                        uso_arranque_alternativo = True
                    if mejorado:
                        uso_variante_mejorada = True
                    break
            if ok:
                break

        if not ok:
            raise NoConverge(
                f"Bairstow no logró extraer el factor cuadrático {factor}. "
                "Probá otros valores iniciales de r0 y s0 o más iteraciones.",
                pasos=pasos_intento,
            )

        pasos.extend(pasos_intento)
        if any(paso["perturbado"] for paso in pasos_intento):
            hubo_perturbacion = True

        raices.extend(_raices_factor(r, s))
        trabajo = _deflactar(trabajo, r, s)
        factor += 1

    grado_restante = len(trabajo) - 1
    if grado_restante == 2:
        raices.extend(_raices_cuadraticas(trabajo[0], trabajo[1], trabajo[2]))
    elif grado_restante == 1:
        raices.append(complex(-trabajo[0] / trabajo[1], 0.0))

    raices = [_limpiar_raiz(z) for z in raices]

    if uso_arranque_alternativo:
        avisos.append("El arranque inicial no convergió; se usó un arranque alternativo.")
    if uso_variante_mejorada:
        avisos.append("Se usó la variante mejorada del Horner cuadrático para converger.")
    if hubo_perturbacion:
        avisos.append("Se perturbó (r, s) porque el determinante era casi nulo.")

    error = None
    if pasos:
        error = max(abs(pasos[-1]["dr"]), abs(pasos[-1]["ds"]))

    return Resultado(
        valor=raices,
        iteraciones=len(pasos),
        error=error,
        convergio=True,
        pasos=pasos,
        avisos=avisos,
    )