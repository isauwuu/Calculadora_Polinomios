from fractions import Fraction

from core.polinomio import Polinomio
from core.resultado import Resultado
from metodos.evaluacion import horner_fraction

# Denominador para las cotas racionales cuando la raíz k-ésima no es exacta.
_DEN_COTA = 1000
# Tope de iteraciones para Laguerre y Newton; al superarlo, se respalda en Lagrange.
_MAX_BUSQUEDA = 100000


def _normalizar(p: Polinomio) -> Polinomio:
    """Multiplica por -1 si el coeficiente principal es negativo.

    Las raíces no cambian y los métodos de cotas suponen a_n > 0.
    """
    if p.coef[-1] < 0:
        return Polinomio([-c for c in p.coef])
    return p


def _sin_raices_positivas(p: Polinomio) -> bool:
    """Si todos los coeficientes son >= 0, P(x) > 0 para todo x > 0."""
    return all(c >= 0 for c in p.coef)


def _techo_raiz_k(valor: Fraction, k: int) -> Fraction:
    """Menor fracción m/1000 con (m/1000)^k >= valor.

    Es una cota superior racional conservadora. Para k = 1 el valor es exacto.
    Se calcula con enteros para no depender de errores de redondeo de float.
    """
    if valor <= 0:
        return Fraction(0)
    if k == 1:
        return valor

    objetivo = valor.numerator * (_DEN_COTA ** k)
    divisor = valor.denominator
    lo, hi = 0, 1
    while hi ** k * divisor < objetivo:
        hi *= 2
    while lo < hi:
        medio = (lo + hi) // 2
        if medio ** k * divisor >= objetivo:
            hi = medio
        else:
            lo = medio + 1
    return Fraction(lo, _DEN_COTA)


def _polinomio_inverso(p: Polinomio) -> Polinomio:
    """P(1/y) multiplicado por y^n: los coeficientes se invierten."""
    return Polinomio(list(reversed(p.coef)))


def _polinomio_negativo(p: Polinomio) -> Polinomio:
    """P(-y): cambian de signo los coeficientes de grado impar."""
    return Polinomio([c if i % 2 == 0 else -c for i, c in enumerate(p.coef)])


def _polinomio_negativo_inverso(p: Polinomio) -> Polinomio:
    """P(-1/y) multiplicado por y^n.

    Sustituyendo x = -1/y en P(x) = Σ a_i x^i y multiplicando por y^n:
        P(-1/y) · y^n = Σ a_i · (-1)^i · y^(n-i)
    Renombrando j = n - i:
        = Σ_j a_{n-j} · (-1)^(n-j) · y^j

    El coeficiente de y^j es a_{n-j} · (-1)^(n-j).
    (Si n es impar, el polinomio entero queda negado respecto de la fórmula
    sin el (-1)^n; eso es irrelevante para las raíces, pero lo incluimos para
    que el polinomio devuelto sea exactamente P(-1/y) · y^n.)
    """
    n = p.grado
    return Polinomio([p.coef[n - j] * ((-1) ** (n - j)) for j in range(n + 1)])


# ---------------------------------------------------------------------------
# Cota superior de las raíces positivas para cada método
# ---------------------------------------------------------------------------

def _sup_lagrange(p: Polinomio) -> tuple[Fraction, dict]:
    p = _normalizar(p)
    if _sin_raices_positivas(p):
        return Fraction(0), {"k": None, "A": Fraction(0), "a0": p.coef[-1]}

    # Coeficientes de mayor a menor, como en el apunte.
    coef = list(reversed(p.coef))
    a0 = coef[0]
    k = next(i for i, c in enumerate(coef) if c < 0)
    A = max(-c for c in coef if c < 0)
    cota = Fraction(1) + _techo_raiz_k(A / a0, k)
    return cota, {"k": k, "A": A, "a0": a0}


def _sup_laguerre(p: Polinomio) -> tuple[Fraction, dict]:
    """Menor L entero > 0 tal que el cociente y el resto de (x - L) sean > 0.

    Nota: cuando el resto es 0 y el cociente es positivo (apunte, sección 4.3),
    este código avanza a L+1 en vez de sumar una constante ≤ 1. La cota
    resultante sigue siendo válida (más conservadora).
    """
    p = _normalizar(p)
    if _sin_raices_positivas(p):
        return Fraction(0), {"L": None}

    for L in range(1, _MAX_BUSQUEDA):
        b = horner_fraction(p, L).pasos[0]["b"]  # b[0] resto, b[1:] cociente
        if all(c > 0 for c in b):
            return Fraction(L), {"L": L}

    # Respaldo: Lagrange siempre da una cota válida.
    cota, detalle = _sup_lagrange(p)
    return cota, {**detalle, "L": None, "respaldo": "lagrange"}


def _sup_newton(p: Polinomio) -> tuple[Fraction, dict]:
    """Menor alpha > 0 con P, P', ..., P^(n) todas positivas en alpha."""
    p = _normalizar(p)
    if _sin_raices_positivas(p):
        return Fraction(0), {"alpha": None}

    # Sucesión P, P', P'', ..., constante.
    derivadas = []
    q = p
    while True:
        derivadas.append(q)
        if q.grado == 0:
            break
        q = q.derivada()

    for alpha in range(1, _MAX_BUSQUEDA):
        if all(horner_fraction(q, alpha).valor > 0 for q in derivadas):
            return Fraction(alpha), {"alpha": alpha}

    cota, detalle = _sup_lagrange(p)
    return cota, {**detalle, "alpha": None, "respaldo": "lagrange"}


def _cotas_con_metodo(p: Polinomio, sup_func, nombre: str) -> Resultado:
    """Aplica un método a P, P(-y), P(1/y) y P(-1/y)."""
    cero = Fraction(0)
    if p.grado == 0:
        return Resultado(
            valor={"inf_pos": cero, "sup_pos": cero, "inf_neg": cero, "sup_neg": cero},
            avisos=["Un polinomio constante no tiene raíces."] if p.coef[0] != 0 else [],
        )

    pasos = []

    sup_pos, det_sup_pos = sup_func(p)
    pasos.append({"cota": "sup_pos", "metodo": nombre, "valor": sup_pos, **det_sup_pos})

    # Cota inferior positiva: x = 1/y.
    sup_y_inv, det_inv = sup_func(_polinomio_inverso(p))
    inf_pos = cero if sup_y_inv == 0 else Fraction(1) / sup_y_inv
    pasos.append(
        {"cota": "inf_pos", "metodo": nombre, "valor": inf_pos, "sup_y": sup_y_inv, **det_inv}
    )

    # Raíces negativas: x = -y.
    sup_y_neg, det_neg = sup_func(_polinomio_negativo(p))
    inf_neg = -sup_y_neg
    pasos.append({"cota": "inf_neg", "metodo": nombre, "valor": inf_neg, **det_neg})

    # Cota superior negativa: x = -1/y.
    sup_y_neg_inv, det_neg_inv = sup_func(_polinomio_negativo_inverso(p))
    sup_neg = cero if sup_y_neg_inv == 0 else -Fraction(1) / sup_y_neg_inv
    pasos.append(
        {"cota": "sup_neg", "metodo": nombre, "valor": sup_neg, **det_neg_inv}
    )

    return Resultado(
        valor={
            "inf_pos": inf_pos,
            "sup_pos": sup_pos,
            "inf_neg": inf_neg,
            "sup_neg": sup_neg,
        },
        pasos=pasos,
    )


# ---------------------------------------------------------------------------
# API pública
# ---------------------------------------------------------------------------

def lagrange(p: Polinomio) -> Resultado:
    """Cotas de Lagrange (Algoritmo del apunte, sección 4.3).

    Cota superior positiva: 1 + (A/a_n)^(1/k), con k el índice del primer
    coeficiente negativo y A el mayor valor absoluto de los negativos.
    Las otras tres cotas salen de los cambios x = 1/y, x = -y y x = -1/y.
    """
    return _cotas_con_metodo(p, _sup_lagrange, "lagrange")


def laguerre(p: Polinomio) -> Resultado:
    """Cotas de Laguerre: menor L > 0 con cociente y resto positivos.

    Se prueba con Horner P(x) = (x - L) C(x) + R y se exige que todos los
    coeficientes de C y el resto R sean positivos.

    Si el resto es 0 y el cociente es positivo, este código avanza a L+1
    (el apunte permitiría sumar una constante ≤ 1). La cota sigue siendo válida.
    """
    return _cotas_con_metodo(p, _sup_laguerre, "laguerre")


def newton_cotas(p: Polinomio) -> Resultado:
    """Cotas de Newton: menor alpha > 0 con P, P', ..., P^(n) positivas.

    Se deriva hasta la constante y se evalúa toda la sucesión en alpha.
    """
    return _cotas_con_metodo(p, _sup_newton, "newton")


def cota_implicacion(p: Polinomio) -> Resultado:
    """Cota por implicación: si r es raíz, |r| <= 1 + max |a_i/a_n|.

    Devuelve el intervalo global [-B, B]. Es válida para raíces reales y
    complejas, pero no distingue el signo.
    """
    cero = Fraction(0)
    if p.grado == 0:
        return Resultado(
            valor={"inf_pos": cero, "sup_pos": cero, "inf_neg": cero, "sup_neg": cero},
            avisos=["Un polinomio constante no tiene raíces."] if p.coef[0] != 0 else [],
        )

    an = p.coef[-1]
    B = Fraction(1) + max(abs(c / an) for c in p.coef[:-1])
    valor = {"inf_pos": cero, "sup_pos": B, "inf_neg": -B, "sup_neg": cero}
    return Resultado(
        valor=valor,
        pasos=[{"cota": "global", "metodo": "implicacion", "B": B}],
    )


def todas_las_cotas(p: Polinomio) -> dict[str, Resultado]:
    """Ejecuta los cuatro métodos y devuelve un Resultado por método."""
    return {
        "lagrange": lagrange(p),
        "laguerre": laguerre(p),
        "newton": newton_cotas(p),
        "implicacion": cota_implicacion(p),
    }