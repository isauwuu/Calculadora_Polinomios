import math
from fractions import Fraction

from core.polinomio import Polinomio
from core.resultado import Resultado
from metodos.evaluacion import horner_fraction
from metodos.raices_enteras import divisores  # se reexporta para no duplicar


def _coeficientes_enteros(p: Polinomio) -> list[int]:
    """Multiplica P por el mcm de los denominadores (las raíces no cambian)."""
    mcm = 1
    for c in p.coef:
        mcm = math.lcm(mcm, c.denominator)
    return [int(c * mcm) for c in p.coef]


def _sacar_factores_x(p: Polinomio) -> tuple[int, Polinomio]:
    """Devuelve (multiplicidad del factor x, polinomio cociente).

    Si el término independiente es 0, el 0 es raíz. Se quitan todos los
    factores x para buscar las demás raíces con el criterio de Gauss.
    """
    coef = list(p.coef)
    multiplicidad = 0
    while len(coef) > 1 and coef[0] == 0:
        coef.pop(0)
        multiplicidad += 1
    return multiplicidad, Polinomio(coef)


def _resultado_sin_raices(motivo: str | None = None) -> Resultado:
    avisos = [motivo] if motivo else []
    return Resultado(valor=[], avisos=avisos)


def raices_enteras(p: Polinomio) -> Resultado:
    """Raíces enteras de P con el teorema del resto y Horner exacto.

    Si P tiene coeficientes racionales se multiplica por el mcm de los
    denominadores para trabajar con enteros. Los candidatos son los divisores
    del término independiente. Si a0 = 0, primero se extrae la raíz 0.
    """
    if p.grado == 0:
        if p.coef[0] == 0:
            return _resultado_sin_raices("El polinomio nulo tiene infinitas raíces.")
        return _resultado_sin_raices()

    multiplicidad_cero, q = _sacar_factores_x(p)
    pasos: list[dict] = []
    raices: list[Fraction] = []

    if multiplicidad_cero > 0:
        raices.append(Fraction(0))
        pasos.append({"candidato": Fraction(0), "valor": Fraction(0), "es_raiz": True})

    if q.grado == 0:
        # P(x) = c * x^m: la única raíz es 0.
        return Resultado(valor=sorted(raices), iteraciones=len(pasos), pasos=pasos)

    a0 = _coeficientes_enteros(q)[0]
    for candidato in divisores(a0):
        valor = horner_fraction(q, candidato).valor
        es_raiz = valor == 0
        pasos.append(
            {
                "candidato": Fraction(candidato),
                "valor": valor,
                "es_raiz": es_raiz,
            }
        )
        if es_raiz:
            raices.append(Fraction(candidato))

    return Resultado(valor=sorted(raices), iteraciones=len(pasos), pasos=pasos)


def raices_racionales(p: Polinomio) -> Resultado:
    """Raíces racionales de P con el criterio de Gauss (exacto).

    Con coeficientes enteros, los candidatos son p/q con p divisor del término
    independiente y q divisor positivo del coeficiente principal. Fraction
    reduce automáticamente y un set elimina los repetidos.
    """
    if p.grado == 0:
        if p.coef[0] == 0:
            return _resultado_sin_raices("El polinomio nulo tiene infinitas raíces.")
        return _resultado_sin_raices()

    multiplicidad_cero, q = _sacar_factores_x(p)
    pasos: list[dict] = []
    raices: list[Fraction] = []

    if multiplicidad_cero > 0:
        raices.append(Fraction(0))
        pasos.append(
            {
                "candidato": Fraction(0),
                "valor": Fraction(0),
                "es_raiz": True,
                "p": 0,
                "q": 1,
            }
        )

    if q.grado == 0:
        return Resultado(valor=sorted(raices), iteraciones=len(pasos), pasos=pasos)

    coef = _coeficientes_enteros(q)
    a0, an = coef[0], coef[-1]

    candidatos: set[Fraction] = set()
    for numerador in divisores(a0):
        for denominador in divisores(abs(an)):
            if denominador > 0:
                candidatos.add(Fraction(numerador, denominador))

    for candidato in sorted(candidatos):
        valor = horner_fraction(q, candidato).valor
        es_raiz = valor == 0
        pasos.append(
            {
                "candidato": candidato,
                "valor": valor,
                "es_raiz": es_raiz,
                "p": candidato.numerator,
                "q": candidato.denominator,
            }
        )
        if es_raiz:
            raices.append(candidato)

    return Resultado(valor=sorted(raices), iteraciones=len(pasos), pasos=pasos)
