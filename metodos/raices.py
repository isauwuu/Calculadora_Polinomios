import math
from fractions import Fraction

from core.polinomio import Polinomio
from core.resultado import Resultado
from metodos.evaluacion import horner_fraction
from metodos.division import dividir_por_x_menos_b


def divisores(x: int) -> list[int]:
    """Devuelve todos los divisores enteros (positivos y negativos) de x."""
    x = abs(x)
    if x == 0:
        return []
    encontrados: set[int] = set()
    for i in range(1, math.isqrt(x) + 1):
        if x % i == 0:
            encontrados.update([i, -i, x // i, -(x // i)])
    return sorted(encontrados)


def _coeficientes_enteros(p: Polinomio) -> list[int]:
    """Multiplica P por el mcm de los denominadores (las raíces no cambian)."""
    mcm = 1
    for c in p.coef:
        mcm = math.lcm(mcm, c.denominator)
    return [(c * mcm).numerator for c in p.coef]


def _sacar_factores_x(p: Polinomio) -> tuple[int, Polinomio]:
    """Devuelve (multiplicidad del factor x, polinomio cociente)."""
    coef = list(p.coef)
    multiplicidad = 0
    while len(coef) > 1 and coef[0] == 0:
        coef.pop(0)
        multiplicidad += 1
    return multiplicidad, Polinomio(coef)


def _resultado_sin_raices(motivo: str | None = None) -> Resultado:
    avisos = [motivo] if motivo else []
    return Resultado(valor=[], avisos=avisos)


def _multiplicidad(p: Polinomio, r: Fraction) -> int:
    """Cuenta cuántas veces (x - r) divide a p. Asume que p(r) == 0.

    Con Fracciones, el resto se compara con == 0 (sin tolerancias).
    Devuelve el mayor m tal que p es divisible por (x - r)^m.
    """
    if p.grado == 0:
        return 0
    count = 0
    q = p
    while q.grado >= 1 and count < p.grado:
        c, resto = dividir_por_x_menos_b(q, r).valor
        if resto != 0:
            break
        count += 1
        q = c
    return count


def raices_enteras(p: Polinomio) -> Resultado:
    """Raíces enteras de P con el teorema del resto y Horner exacto.

    Si a0 = 0, primero se extrae la raíz 0 (con su multiplicidad).
    Las raíces se devuelven DISTINTAS (sin repetir); la multiplicidad de
    cada una queda en `Resultado.multiplicidades`.
    """
    if p.grado == 0:
        if p.coef[0] == 0:
            return _resultado_sin_raices("El polinomio nulo tiene infinitas raíces.")
        return _resultado_sin_raices()

    multiplicidad_cero, q = _sacar_factores_x(p)
    pasos: list[dict] = []
    raices: list[Fraction] = []
    multiplicidades: dict[Fraction, int] = {}

    if multiplicidad_cero > 0:
        cero = Fraction(0)
        raices.append(cero)
        multiplicidades[cero] = multiplicidad_cero
        pasos.append({"candidato": cero, "valor": cero, "es_raiz": True})

    if q.grado == 0:
        return Resultado(
            valor=sorted(raices),
            iteraciones=len(pasos),
            pasos=pasos,
            multiplicidades=multiplicidades,
        )

    a0 = _coeficientes_enteros(q)[0]
    for candidato in divisores(a0):
        valor = horner_fraction(q, candidato).valor
        es_raiz = valor == 0
        pasos.append({
            "candidato": Fraction(candidato),
            "valor": valor,
            "es_raiz": es_raiz,
        })
        if es_raiz:
            r = Fraction(candidato)
            raices.append(r)
            multiplicidades[r] = _multiplicidad(q, r)

    return Resultado(
        valor=sorted(raices),
        iteraciones=len(pasos),
        pasos=pasos,
        multiplicidades=multiplicidades,
    )


def raices_racionales(p: Polinomio) -> Resultado:
    """Raíces racionales de P con el criterio de Gauss (exacto).

    Las raíces se devuelven DISTINTAS (sin repetir); la multiplicidad de
    cada una queda en `Resultado.multiplicidades`.
    """
    if p.grado == 0:
        if p.coef[0] == 0:
            return _resultado_sin_raices("El polinomio nulo tiene infinitas raíces.")
        return _resultado_sin_raices()

    multiplicidad_cero, q = _sacar_factores_x(p)
    pasos: list[dict] = []
    raices: list[Fraction] = []
    multiplicidades: dict[Fraction, int] = {}

    if multiplicidad_cero > 0:
        cero = Fraction(0)
        raices.append(cero)
        multiplicidades[cero] = multiplicidad_cero
        pasos.append({
            "candidato": cero, "valor": cero, "es_raiz": True, "p": 0, "q": 1,
        })

    if q.grado == 0:
        return Resultado(
            valor=sorted(raices),
            iteraciones=len(pasos),
            pasos=pasos,
            multiplicidades=multiplicidades,
        )

    coef = _coeficientes_enteros(q)
    a0, an = coef[0], coef[-1]

    candidatos: set[Fraction] = set()
    for numerador in divisores(a0):
        for denominador in divisores(an):
            if denominador > 0:
                candidatos.add(Fraction(numerador, denominador))

    for candidato in sorted(candidatos):
        valor = horner_fraction(q, candidato).valor
        es_raiz = valor == 0
        pasos.append({
            "candidato": candidato,
            "valor": valor,
            "es_raiz": es_raiz,
            "p": candidato.numerator,
            "q": candidato.denominator,
        })
        if es_raiz:
            raices.append(candidato)
            multiplicidades[candidato] = _multiplicidad(q, candidato)

    return Resultado(
        valor=sorted(raices),
        iteraciones=len(pasos),
        pasos=pasos,
        multiplicidades=multiplicidades,
    )


def factorizacion_string(p: Polinomio, multiplicidades: dict[Fraction, int]) -> str:
    """Factoriza P sobre Q: P(x) = C · Π (x - r)^m · R(x).

    - C: constante resultante (coef principal que queda tras dividir).
    - Π (x - r)^m: factores lineales de cada raíz conocida.
    - R(x): lo que no se pudo factorizar (grado 0 si todas las raíces son
      racionales; si no, queda como polinomio residual).

    Devuelve un string listo para mostrar en la pestaña 2.
    """
    if not multiplicidades:
        return str(p)

    q = p
    for r, m in multiplicidades.items():
        for _ in range(m):
            q, _ = dividir_por_x_menos_b(q, r).valor

    partes: list[str] = []

    # Factores lineales ordenados por valor de raíz
    for r in sorted(multiplicidades):
        m = multiplicidades[r]
        if r == 0:
            base = "x"
        elif r > 0:
            base = f"(x - {r})"
        else:
            base = f"(x + {-r})"
        partes.append(f"{base}^{m}" if m > 1 else base)

    # Resto: constante C (si C≠1) o polinomio residual
    if q.grado == 0:
        if q.coef[0] != 1:
            partes.insert(0, str(q.coef[0]))
    else:
        partes.append(f"({q})")

    return " · ".join(partes)