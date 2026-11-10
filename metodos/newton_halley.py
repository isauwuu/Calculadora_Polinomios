import math

from core.config import EPS_DEFAULT, MAX_ITER, convergio
from core.errores import DivisionPorCero, EntradaInvalida, ToleranciaInvalida
from core.polinomio import Polinomio
from core.resultado import Resultado
from metodos.diagnostico import analizar
from metodos.evaluacion import horner_doble_float, horner3_float


def _validar_parametros(eps, max_iter) -> tuple[float, int]:
    """Convierte y valida epsilon y el máximo de iteraciones."""
    try:
        eps = float(eps)
    except (TypeError, ValueError):
        raise ToleranciaInvalida("La tolerancia epsilon debe ser un número positivo.")
    if not math.isfinite(eps) or eps <= 0:
        raise ToleranciaInvalida("La tolerancia epsilon debe ser un número positivo y finito.")

    try:
        max_iter = int(max_iter)
    except (TypeError, ValueError):
        raise EntradaInvalida("El máximo de iteraciones debe ser un entero positivo.")
    if max_iter <= 0:
        raise EntradaInvalida("El máximo de iteraciones debe ser un entero positivo.")
    return eps, max_iter


def _validar_x0(x0) -> float:
    try:
        x = float(x0)
    except (TypeError, ValueError):
        raise EntradaInvalida("El punto inicial x0 debe ser un número.")
    if not math.isfinite(x):
        raise DivisionPorCero("El punto inicial x0 no es un valor finito.")
    return x


def _resultado_no_converge(x: float, pasos: list[dict], max_iter: int, eps: float) -> Resultado:
    error = abs(pasos[-1]["dx"]) if pasos else None
    return Resultado(
        valor=x,
        iteraciones=max_iter,
        error=error,
        convergio=False,
        pasos=pasos,
        diagnostico=analizar(pasos, eps),
        avisos=[
            f"No se alcanzó la tolerancia en {max_iter} iteraciones. "
            "Probá otro x0 o revisá si hay ciclo o raíz múltiple."
        ],
    )


def newton(p: Polinomio, x0, eps=EPS_DEFAULT, max_iter=MAX_ITER) -> Resultado:
    """Método de Newton-Raphson para polinomios (Algoritmo 7 del apunte).

    Usa Horner doble: P(xn) y P'(xn) en una sola pasada. La iteración es
        xn+1 = xn - P(xn) / P'(xn)
    y se detiene con el criterio mixto |dx| <= eps * max(1, |xn|).

    Cada paso guarda n, x, p, dp, x_sig y dx. dx es el paso que sale de esa
    fila; x_sig es el x de la fila siguiente (o el valor final).
    """
    eps, max_iter = _validar_parametros(eps, max_iter)
    x = _validar_x0(x0)
    coef = p.a_float()  # una sola conversión a float, fuera del bucle
    pasos: list[dict] = []

    for n in range(max_iter):
        px, dpx = horner_doble_float(coef, x)

        if not (math.isfinite(px) and math.isfinite(dpx)):
            raise DivisionPorCero(
                f"Valor no finito al evaluar en x = {x}. Probá otro punto inicial.",
                pasos=pasos,
            )
        if dpx == 0:
            raise DivisionPorCero(
                f"La derivada vale 0 en x = {x}: la tangente es horizontal. "
                "Probá otro punto inicial.",
                pasos=pasos,
            )

        dx = px / dpx
        x_sig = x - dx
        if not math.isfinite(x_sig):
            raise DivisionPorCero(
                f"El método produjo un valor no finito en x = {x}. Probá otro punto inicial.",
                pasos=pasos,
            )

        pasos.append({"n": n, "x": x, "p": px, "dp": dpx, "x_sig": x_sig, "dx": dx})

        if convergio(dx, x, eps):
            return Resultado(
                valor=x_sig,
                iteraciones=n + 1,
                error=abs(dx),
                convergio=True,
                pasos=pasos,
                diagnostico=analizar(pasos, eps),
            )
        x = x_sig

    return _resultado_no_converge(x, pasos, max_iter, eps)


def halley(p: Polinomio, x0, eps=EPS_DEFAULT, max_iter=MAX_ITER) -> Resultado:
    """Método de Halley para polinomios (Algoritmo 8 del apunte).

    Usa Horner triple: P(xn), P'(xn) y P''(xn). La fórmula es
        xn+1 = xn - 2 P P' / (2 (P')^2 - P P'')
    con P'' completa (no P''/2). Se guarda d2p = P''(xn) en cada paso.

    Igual que Newton, agotar las iteraciones devuelve convergio=False con los
    pasos; una derivada nula o un valor no finito lanza DivisionPorCero.
    """
    eps, max_iter = _validar_parametros(eps, max_iter)
    x = _validar_x0(x0)
    coef = p.a_float()
    pasos: list[dict] = []

    for n in range(max_iter):
        px, dpx, d2px = horner3_float(coef, x)

        if not (math.isfinite(px) and math.isfinite(dpx) and math.isfinite(d2px)):
            raise DivisionPorCero(
                f"Valor no finito al evaluar en x = {x}. Probá otro punto inicial.",
                pasos=pasos,
            )
        if dpx == 0:
            raise DivisionPorCero(
                f"La derivada vale 0 en x = {x}: la tangente es horizontal. "
                "Probá otro punto inicial.",
                pasos=pasos,
            )

        denominador = 2.0 * dpx * dpx - px * d2px
        if denominador == 0:
            raise DivisionPorCero(
                f"El denominador de Halley vale 0 en x = {x}. Probá otro punto inicial.",
                pasos=pasos,
            )

        dx = (2.0 * px * dpx) / denominador
        x_sig = x - dx
        if not math.isfinite(x_sig):
            raise DivisionPorCero(
                f"El método produjo un valor no finito en x = {x}. Probá otro punto inicial.",
                pasos=pasos,
            )

        pasos.append(
            {
                "n": n,
                "x": x,
                "p": px,
                "dp": dpx,
                "d2p": d2px,
                "x_sig": x_sig,
                "dx": dx,
            }
        )

        if convergio(dx, x, eps):
            return Resultado(
                valor=x_sig,
                iteraciones=n + 1,
                error=abs(dx),
                convergio=True,
                pasos=pasos,
                diagnostico=analizar(pasos, eps),
            )
        x = x_sig

    return _resultado_no_converge(x, pasos, max_iter, eps)
