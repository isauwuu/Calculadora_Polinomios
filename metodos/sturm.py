import math
from fractions import Fraction

from core.errores import EntradaInvalida
from core.polinomio import Polinomio
from core.resultado import Resultado
from metodos.division import dividir
from metodos.evaluacion import horner_fraction


# Máximo de subdivisiones sucesivas antes de avisar que no se pudo aislar.
_MAX_PROFUNDIDAD = 200


# ---------------------------------------------------------------------------
# Utilidades exactas
# ---------------------------------------------------------------------------

def _es_cero(p: Polinomio) -> bool:
    """True si todos los coeficientes son 0 (polinomio nulo)."""
    return all(c == 0 for c in p.coef)


def _normalizar(p: Polinomio) -> Polinomio:
    """Escala P por una constante positiva para limpiar los denominadores.

    Multiplicar por una constante positiva no cambia las raíces ni los signos,
    que es todo lo que necesita Sturm. El apunte usa este recurso para que la
    sucesión quede con coeficientes enteros. No se divide por el mcd: así se
    reproducen exactamente los coeficientes de los ejemplos del apunte.
    """
    if _es_cero(p):
        return Polinomio([0])

    mcm = 1
    for c in p.coef:
        mcm = math.lcm(mcm, c.denominator)
    return Polinomio([Fraction(int(c * mcm)) for c in p.coef])


def _resto_de_sturm(resto: Polinomio) -> Polinomio:
    """Devuelve -resto escalado por una constante positiva (nunca por una negativa).

    El apunte define P_k = -resto[P_{k-2} div P_{k-1}] y permite multiplicar
    por una constante positiva para limpiar fracciones. Primero se aplica el
    signo negativo y después se normaliza con un factor positivo.
    """
    negativo = Polinomio([-c for c in resto.coef])
    return _normalizar(negativo)


def _evaluar(p: Polinomio, x: Fraction) -> Fraction:
    """Evalúa P(x) con Horner exacto (se reutiliza la función existente)."""
    return horner_fraction(p, x).valor


def _signo(valor) -> int:
    """Devuelve 1, -1 o 0 según el signo del valor."""
    if valor > 0:
        return 1
    if valor < 0:
        return -1
    return 0


def _cambios_de_signos(signos) -> int:
    """Cuenta cambios entre signos consecutivos, salteando los ceros."""
    no_nulos = [s for s in signos if s != 0]
    return sum(1 for a, b in zip(no_nulos, no_nulos[1:]) if a * b < 0)


def cambios_signo(valores) -> int:
    """Cuenta los cambios de signo de una lista de valores, ignorando ceros.

    Es la función auxiliar que usa el teorema de Sturm para calcular ncs(a)
    y ncs(b). Un cero no cuenta como signo: se saltea.
    """
    return _cambios_de_signos([_signo(v) for v in valores])


# ---------------------------------------------------------------------------
# Construcción de la sucesión
# ---------------------------------------------------------------------------

def _sucesion_estandar(p: Polinomio) -> tuple[list[Polinomio], bool, Polinomio | None, int | None]:
    """Arma la sucesión de Sturm estándar.

    Devuelve (sucesión, hay_raices_multiples, mcd, indice_del_cero). Si el
    último resto es 0, el último polinomio no nulo es el mcd(P, P') y sus
    raíces son las múltiples de P. En ese caso no se agrega el polinomio nulo
    a la lista, pero se informa en qué índice aparecería (P_m = 0).
    """
    sucesion = [p]
    if p.grado == 0:
        return sucesion, False, None, None

    sucesion.append(p.derivada())

    while True:
        actual = sucesion[-1]
        if actual.grado == 0:
            return sucesion, False, None, None

        _, resto = dividir(sucesion[-2], actual).valor
        if _es_cero(resto):
            # P_m = 0: el último no nulo es mcd(P, P').
            return sucesion, True, actual, len(sucesion)
        sucesion.append(_resto_de_sturm(resto))


def _sucesion_simplificada(p: Polinomio, sucesion: list[Polinomio], mcd: Polinomio) -> list[Polinomio]:
    """Forma 1 del apunte: q_i = P_i / mcd(P, P').

    Se normaliza cada cociente por una constante positiva para que quede con
    coeficientes enteros. Eso no cambia ningún signo ni el conteo de Sturm.
    """
    simplificada = []
    for q in sucesion:
        cociente, _ = dividir(q, mcd).valor
        simplificada.append(_normalizar(cociente))
    return simplificada


def _preparar_sucesion(
    p: Polinomio, simplificada: bool
) -> tuple[list[Polinomio], bool, Polinomio | None, int | None, list[str]]:
    """Elige la sucesión que se debe usar para aplicar el teorema.

    - Sin raíces múltiples: la sucesión estándar.
    - Con raíces múltiples: se rehace a partir de Q = P / mcd(P, P'). Si
      `simplificada` es True se usa la forma 1 (q_i = P_i / M); si no, la
      forma 2 (sucesión estándar calculada desde Q).
    """
    if p.grado == 0:
        if _es_cero(p):
            raise EntradaInvalida("El polinomio nulo tiene infinitas raíces: Sturm no se puede aplicar.")
        return [p], False, None, None, ["Un polinomio constante no tiene raíces."]

    estandar, multiplees, mcd, cero_en = _sucesion_estandar(p)
    if not multiplees:
        return estandar, False, None, None, []

    aviso = (
        f"P_{cero_en} = 0: hay raíces múltiples. "
        "Se rehace la sucesión con Q = P / mcd(P, P')."
    )

    if simplificada:
        return _sucesion_simplificada(p, estandar, mcd), True, mcd, cero_en, [aviso]

    cociente, _ = dividir(p, mcd).valor
    q = _normalizar(cociente)
    nueva, _, _, _ = _sucesion_estandar(q)
    return nueva, True, mcd, cero_en, [aviso]


def sucesion_sturm(p: Polinomio, simplificada: bool = False) -> Resultado:
    """Calcula la sucesión de Sturm de P (issue #9).

    P0 = P, P1 = P' y P_k = -resto[P_{k-2} div P_{k-1}], multiplicando cada
    resto por una constante positiva para limpiar fracciones. Si aparece
    P_m = 0 hay raíces múltiples y se rehace la sucesión con
    Q = P / mcd(P, P'), usando la forma simplificada o la estándar.

    valor = lista de Polinomio de la sucesión.
    pasos = un diccionario por polinomio con i y sus coeficientes.
    """
    sucesion, _, _, _, avisos = _preparar_sucesion(p, simplificada)

    pasos = [{"i": i, "coef": list(q.coef)} for i, q in enumerate(sucesion)]
    return Resultado(
        valor=sucesion,
        iteraciones=max(0, len(sucesion) - 1),
        pasos=pasos,
        avisos=avisos,
    )


# ---------------------------------------------------------------------------
# Aplicación del teorema
# ---------------------------------------------------------------------------

def _validar_intervalo(a, b) -> tuple[Fraction, Fraction]:
    """Convierte a, b a Fraction y exige a < b."""
    try:
        a = Fraction(a)
        b = Fraction(b)
    except (TypeError, ValueError, ZeroDivisionError, OverflowError):
        raise EntradaInvalida("Los extremos del intervalo deben ser números racionales finitos.")

    if a >= b:
        raise EntradaInvalida("El extremo inferior a debe ser menor que el extremo superior b.")
    return a, b


def _tabla_signos(sucesion: list[Polinomio], a: Fraction, b: Fraction, intervalo=None) -> tuple[list[dict], int, int]:
    """Evalúa la sucesión en a y b y arma las filas de la tabla de signos.

    Cada fila guarda i, los coeficientes de P_i y su signo en a y en b.
    Devuelve (pasos, ncs(a), ncs(b)).
    """
    pasos = []
    signos_a = []
    signos_b = []
    for i, q in enumerate(sucesion):
        va = _evaluar(q, a)
        vb = _evaluar(q, b)
        sa = _signo(va)
        sb = _signo(vb)
        fila = {"i": i, "coef": list(q.coef), "signo_a": sa, "signo_b": sb}
        if intervalo is not None:
            fila["intervalo"] = intervalo
        pasos.append(fila)
        signos_a.append(sa)
        signos_b.append(sb)
    return pasos, _cambios_de_signos(signos_a), _cambios_de_signos(signos_b)


def _verificar_extremos(p: Polinomio, a: Fraction, b: Fraction, pasos: list[dict]) -> None:
    """Avisa si un extremo es raíz: ahí el conteo de Sturm es ambiguo."""
    if _evaluar(p, a) == 0:
        raise EntradaInvalida(
            f"P({a}) = 0: el extremo inferior es raíz. Elegí un intervalo que no empiece en una raíz.",
            pasos=pasos,
        )
    if _evaluar(p, b) == 0:
        raise EntradaInvalida(
            f"P({b}) = 0: el extremo superior es raíz. Elegí un intervalo que no termine en una raíz.",
            pasos=pasos,
        )


def contar_raices(
    p: Polinomio, a, b, simplificada: bool = False
) -> Resultado:
    """Cuenta las raíces reales distintas de P en el intervalo (a, b).

    Aplica el teorema de Sturm: cantidad = ncs(a) - ncs(b), donde ncs es el
    número de cambios de signo de la sucesión evaluada en el extremo (el ncs
    baja al pasar por una raíz). Los extremos no pueden ser raíz
    (P(a)·P(b) != 0). Si hay raíces múltiples se usa automáticamente la
    sucesión rehecha a partir de Q = P / mcd(P, P').

    valor = cantidad de raíces distintas en el intervalo.
    pasos = tabla de signos, una fila por P_i.
    """
    a, b = _validar_intervalo(a, b)
    sucesion, _, _, _, avisos = _preparar_sucesion(p, simplificada)
    pasos, ncs_a, ncs_b = _tabla_signos(sucesion, a, b)
    _verificar_extremos(p, a, b, pasos)

    return Resultado(
        valor=ncs_a - ncs_b,
        iteraciones=len(sucesion) - 1,
        pasos=pasos,
        avisos=avisos,
    )


def _punto_no_raiz(p: Polinomio, a: Fraction, b: Fraction) -> Fraction:
    """Elige un punto interior de (a, b) que no sea raíz de P.

    Se prueban el punto medio y luego fracciones con denominadores potencias
    de 2. Como P tiene finitas raíces, siempre se encuentra uno.
    """
    for nivel in range(1, 21):
        denominador = 2 ** nivel
        for numerador in range(1, denominador, 2):
            punto = a + (b - a) * Fraction(numerador, denominador)
            if _evaluar(p, punto) != 0:
                return punto
    raise EntradaInvalida("No se pudo elegir un punto de subdivisión que no sea raíz.")


def separar_raices(
    p: Polinomio, a, b, simplificada: bool = False
) -> Resultado:
    """Aísla cada raíz real de P en un subintervalo disjunto (issue #10).

    Parte del intervalo (a, b) y lo subdivide mientras haya más de una raíz.
    Los extremos no pueden ser raíz y los puntos de corte se eligen de modo
    que tampoco lo sean, para que el conteo de Sturm nunca sea ambiguo.

    valor = lista de intervalos (a_i, b_i), cada uno con una sola raíz.
    pasos = tablas de signos de los intervalos finales (con la clave
            "intervalo" para identificarlas).
    """
    a, b = _validar_intervalo(a, b)
    sucesion, _, _, _, avisos = _preparar_sucesion(p, simplificada)

    pasos_iniciales, _, _ = _tabla_signos(sucesion, a, b)
    _verificar_extremos(p, a, b, pasos_iniciales)

    def contar(x: Fraction, y: Fraction) -> int:
        _, ncs_x, ncs_y = _tabla_signos(sucesion, x, y)
        return ncs_x - ncs_y

    total = contar(a, b)
    intervalos: list[tuple[Fraction, Fraction]] = []
    pendientes: list[tuple[Fraction, Fraction, int, int]] = [(a, b, total, 0)]

    while pendientes:
        x, y, cantidad, profundidad = pendientes.pop()
        if cantidad == 0:
            continue
        if cantidad == 1:
            intervalos.append((x, y))
            continue
        if profundidad >= _MAX_PROFUNDIDAD:
            raise EntradaInvalida(
                "No se pudieron aislar todas las raíces: hay raíces demasiado próximas.",
                pasos=pasos_iniciales,
            )

        punto = _punto_no_raiz(p, x, y)
        cantidad_izq = contar(x, punto)
        cantidad_der = cantidad - cantidad_izq

        # Se apilan derecha e izquierda para procesar primero la izquierda.
        if cantidad_der:
            pendientes.append((punto, y, cantidad_der, profundidad + 1))
        if cantidad_izq:
            pendientes.append((x, punto, cantidad_izq, profundidad + 1))

    intervalos.sort()

    pasos = []
    for x, y in intervalos:
        tabla, _, _ = _tabla_signos(sucesion, x, y, intervalo=(x, y))
        pasos.extend(tabla)

    return Resultado(
        valor=intervalos,
        iteraciones=len(intervalos),
        pasos=pasos,
        avisos=avisos,
    )
