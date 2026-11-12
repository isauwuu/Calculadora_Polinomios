from fractions import Fraction
from core.errores import DivisionPorCero
from core.polinomio import Polinomio
from core.resultado import Resultado
from metodos.evaluacion import horner_fraction


def dividir_por_x_menos_b(p: Polinomio, b) -> Resultado:
    """Divide P(x) por (x - b) con Horner (equivalente al Algoritmo 2 del apunte,
    que usa (x + b): dividir_por_x_menos_b(p, b) ≡ Alg2(p, -b)).

    Convención de la GUI y del teorema del resto:
      - Dividir por (x - 2) → b = 2.
      - Dividir por (x + 3) → b = -3.

    valor = (cociente: Polinomio, resto: Fraction).  P = (x - b) * Q + R
    """
    base = horner_fraction(p, Fraction(b))
    res = base.pasos[0]["b"]
    cociente = Polinomio(res[1:]) if p.grado >= 1 else Polinomio([0])
    return Resultado(valor=(cociente, res[0]), pasos=base.pasos)


def dividir_por_ax_mas_b(p: Polinomio, a, b) -> Resultado:
    """Divide P(x) por (a*x + b) (Algoritmo 3 del apunte: HornerGral).

    (a*x + b) = a·(x + b/a) = a·(x - (-b/a)), así que aplicamos Horner con
    -b/a y después dividimos el cociente por 'a'.

    valor = (cociente: Polinomio, resto: Fraction).
    """
    a = Fraction(a)
    b = Fraction(b)
    if a == 0:
        raise DivisionPorCero("El coeficiente de x en (a*x + b) no puede ser 0.")
    base = dividir_por_x_menos_b(p, -b / a)
    q, resto = base.valor
    cociente = Polinomio([c / a for c in q.coef])
    return Resultado(valor=(cociente, resto), pasos=base.pasos)


def horner_cuadratico(p: Polinomio, a, b) -> Resultado:
    """Divide P(x) por (x^2 + a x + b) con el esquema de Horner cuadrático (exacto).
    c[n] = coef[n];  c[n-1] = coef[n-1] - a*c[n];
    c[i] = coef[i] - a*c[i+1] - b*c[i+2]  (i = n-2 .. 1);  c[0] = coef[0] - b*c[2]
    valor = (cociente: Polinomio, resto: Polinomio R1(x) = c[1]*x + c[0]).
    """
    a = Fraction(a)
    b = Fraction(b)
    coef = p.coef
    n = p.grado
    if n < 2:  # grado menor que el del divisor
        return Resultado(valor=(Polinomio([0]), Polinomio(list(coef))), pasos=[])
    c = [Fraction(0)] * (n + 1)
    c[n] = coef[n]
    c[n - 1] = coef[n - 1] - a * c[n]
    for i in range(n - 2, 0, -1):
        c[i] = coef[i] - a * c[i + 1] - b * c[i + 2]
    c[0] = coef[0] - b * c[2]  # en la última columna no se resta a*c[1]
    paso = {"a": a, "b": b, "coef": list(coef), "c": c}
    return Resultado(valor=(Polinomio(c[2:]), Polinomio([c[0], c[1]])), pasos=[paso])


def dividir_por_cuadratico(p: Polinomio, a, b, c) -> Resultado:
    """Divide P(x) por (ax^2 + bx + c). valor = (cociente, resto), ambos Polinomio.
    Si a = 1 se usa el esquema de Horner cuadrático del apunte (x^2 + bx + c).
    Si a es distinto de 1 se usa la división general (Algoritmo 5).
    """
    a = Fraction(a)
    if a == 0:
        raise DivisionPorCero("El coeficiente 'a' de ax^2 + bx + c no puede ser 0.")
    if a == 1:
        return horner_cuadratico(p, b, c)
    else:
        return dividir(p, Polinomio([c, b, a]))


def dividir(p: Polinomio, d: Polinomio) -> Resultado:
    """División general P / D, exacta(fraction).
    valor = (cociente: Polinomio, resto: Polinomio).  P = D * Q + R
    Cada paso guarda el término del cociente y cómo queda el resto.
    """
    if d.grado == 0 and d.coef[0] == 0:
        raise DivisionPorCero("No se puede dividir por el polinomio nulo.")
    resto = list(p.coef)
    gd = d.grado
    if p.grado < gd:
        return Resultado(valor=(Polinomio([0]), Polinomio(resto)), pasos=[])
    q = [Fraction(0)] * (p.grado - gd + 1)
    pasos = []
    for k in range(p.grado - gd, -1, -1):
        factor = resto[k + gd] / d.coef[gd]
        q[k] = factor
        for j in range(gd + 1):
            resto[k + j] -= factor * d.coef[j]
        pasos.append({"k": k, "factor": factor, "resto": list(resto)})
    r = resto[:gd] or [Fraction(0)]
    return Resultado(valor=(Polinomio(q), Polinomio(r)), pasos=pasos)
