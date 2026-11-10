# se deben crear 2 horners doble(no se bien si otro de horner simple), uno q use fraction y otro q use float. para precision exacta(fraction) en la evaluacion normal
# el de float se va a usar en el metodo de newton-halley
from fractions import Fraction
from core.polinomio import Polinomio
from core.resultado import Resultado


# por las dudas D:
def evaluacion_directa(p: Polinomio, alpha) -> Resultado:
    alpha = Fraction(alpha)
    ac = Fraction(0)
    pasos = []
    n = p.grado
    coef = p.coef
    for i in range(n + 1):
        potencia = alpha ** i
        termino = coef[i] * potencia
        ac += termino
        pasos.append({"i": i, "coef": coef[i], "potencia": potencia, "termino": termino, "acumulado": ac})
    return Resultado(valor=ac, pasos=pasos)


def horner_fraction(p: Polinomio, alpha) -> Resultado:
    alpha = Fraction(alpha)
    a = p.coef
    n = p.grado
    b = [Fraction(0)] * (n + 1)  # lista [0,0,0,0...,0]
    b[n] = a[n]  # " baja " el coeficiente principal je
    for i in range(n - 1, -1, -1):  # si ponemos hasta 0 no entraria al b[0] D:
        b[i] = a[i] + (alpha * b[i + 1])
    paso = {"alpha": alpha, "a": list(a), "b": b}
    return Resultado(valor=b[0], pasos=[paso])


def horner_float(p: Polinomio, alpha: float) -> Resultado:
    a = p.a_float()
    alpha = float(alpha)  # nos aseguramos d q sea float por si mandan un entero D:
    n = p.grado
    b = [0.0] * (n + 1)  # lista [0,0...,0]
    b[n] = a[n]  # " baja " el coeficiente principal je
    for i in range(n - 1, -1, -1):  # si ponemos hasta 0 no entraria al b[0] D:
        b[i] = a[i] + (alpha * b[i + 1])
    paso = {"alpha": alpha, "a": list(a), "b": b}
    return Resultado(valor=b[0], pasos=[paso])


def horner_doble_fraction(p: Polinomio, alpha) -> Resultado:
    """Dos pasadas de Horner:
      b = Horner sobre P -> b[0] = P(alpha),  b[1:] = cociente Q
      c = Horner sobre Q (= b[1:])  -> c[0] = P'(alpha), c[1:] = cociente de Q
    Las dos filas tienen el mismo formato: [0] es el resto y [1:] el cociente.
    """
    alpha = Fraction(alpha)
    primera = horner_fraction(p, alpha)
    b = primera.pasos[0]["b"]  # obtiene el polinomio resultante de la primera pasada con horner
    if p.grado == 0:
        return Resultado(valor=(b[0], Fraction(0)), pasos=primera.pasos)
    segunda = horner_fraction(Polinomio(b[1:]), alpha)  # b[1:] le quita el primer elemento, o sea el resto
    paso = {"alpha": alpha, "a": list(p.coef), "b": b, "c": segunda.pasos[0]["b"]}
    return Resultado(valor=(b[0], segunda.valor), pasos=[paso])


def horner_doble_float(coef: list[float], x: float) -> tuple[float, float]:
    """Para Newton.
    newton llama al metodo ya con la lista convertida a floats, porq sino iteraria n veces y convertiria los coeficiente n veces tmb D:
    coef va de menor a mayor grado (usar p.a_float() una sola vez, afuera del bucle).
    """
    n = len(coef) - 1
    p = coef[n]
    dp = 0.0
    for i in range(n - 1, -1, -1):
        dp = dp * x + p
        p = p * x + coef[i]
    return p, dp


# para halley
def horner3_float(coef: list[float], x: float) -> tuple[float, float, float]:
    n = len(coef) - 1
    p = coef[n]
    dp = 0.0
    d2p = 0.0
    for i in range(n - 1, -1, -1):
        d2p = d2p * x + dp
        dp = dp * x + p
        p = p * x + coef[i]
    return p, dp, 2.0 * d2p
