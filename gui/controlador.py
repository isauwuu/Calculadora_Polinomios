"""Capa fina entre la interfaz y el núcleo matemático.

No importa tkinter: recibe texto, valida, llama a ``metodos/`` y devuelve un
``Resultado``. Los imports de los métodos se hacen dentro de cada función para
que una pestaña pueda avisar "Método aún no disponible" sin romper la ventana.
"""

import importlib
import cmath
import math
from fractions import Fraction

from core.config import EPS_DEFAULT, MAX_ITER
from core.errores import EntradaInvalida, PolinomioInvalido, ToleranciaInvalida
from core.numeros import parsear_coeficientes, parsear_numero
from core.polinomio import Polinomio
from core.resultado import Resultado
from gui.formato import formatear_fraccion, formatear_polinomio


# ---------------------------------------------------------------------------
# Utilidades de importación y validación
# ---------------------------------------------------------------------------

def _metodo(modulo, nombre):
    """Importa una función de ``metodos/`` o lanza un error entendible."""
    try:
        mod = importlib.import_module(modulo)
        return getattr(mod, nombre)
    except (ImportError, AttributeError) as exc:
        raise EntradaInvalida(f"Método aún no disponible: {modulo}.{nombre}.") from exc


def leer_polinomio(texto):
    """Convierte el texto de coeficientes en un Polinomio."""
    if texto is None or not str(texto).strip():
        raise PolinomioInvalido("Ingresá los coeficientes del polinomio.")
    return Polinomio.desde_texto(str(texto))


def coeficientes_float(texto):
    """Coeficientes como float para graficar (no se usa para resolver)."""
    return leer_polinomio(texto).a_float()


def _a_float(texto, nombre):
    if texto is None or not str(texto).strip():
        raise EntradaInvalida(f"Ingresá {nombre}.")
    try:
        valor = float(parsear_numero(str(texto)))
    except EntradaInvalida:
        raise
    except (TypeError, ValueError, ZeroDivisionError, OverflowError):
        raise EntradaInvalida(f"{nombre.capitalize()} debe ser un número.")
    if not math.isfinite(valor):
        raise EntradaInvalida(f"{nombre.capitalize()} debe ser un número finito.")
    return valor


def parsear_racional(texto, nombre="el valor"):
    """Número exacto (entero, decimal o fracción) como Fraction."""
    if texto is None or not str(texto).strip():
        raise EntradaInvalida(f"Ingresá {nombre}.")
    return parsear_numero(str(texto))


def parsear_entero_positivo(texto, nombre="el máximo de iteraciones"):
    valor = _a_float(texto, nombre)
    if not valor.is_integer() or valor <= 0:
        raise EntradaInvalida(f"{nombre.capitalize()} debe ser un entero positivo.")
    return int(valor)


def parsear_tolerancia(texto):
    valor = _a_float(texto, "la tolerancia ε")
    if valor <= 0:
        raise ToleranciaInvalida("La tolerancia ε debe ser un número positivo y finito.")
    return valor


def _parametros_racionales(texto, cantidad, nombres):
    if texto is None or not str(texto).strip():
        raise EntradaInvalida(f"Ingresá los parámetros del divisor ({', '.join(nombres)}).")
    valores = parsear_coeficientes(str(texto))
    if len(valores) != cantidad:
        raise EntradaInvalida(
            f"El divisor necesita {cantidad} valor(es): {', '.join(nombres)}."
        )
    return valores


# ---------------------------------------------------------------------------
# Pestaña 1: evaluar y dividir
# ---------------------------------------------------------------------------

def evaluar(texto, alpha, metodo):
    """Evalúa P en alpha con el método elegido (exacto, Fraction)."""
    p = leer_polinomio(texto)
    a = parsear_racional(alpha, "el punto α")
    clave = str(metodo).strip().lower()
    if "doble" in clave:
        f = _metodo("metodos.evaluacion", "horner_doble_fraction")
    elif "directa" in clave:
        f = _metodo("metodos.evaluacion", "evaluacion_directa")
    elif "horner" in clave:
        f = _metodo("metodos.evaluacion", "horner_fraction")
    else:
        raise EntradaInvalida("Elegí una operación de evaluación válida.")
    return f(p, a)


def dividir(texto, tipo_divisor, parametros):
    """Divide P por el divisor elegido y devuelve (cociente, resto) en ``valor``."""
    p = leer_polinomio(texto)
    tipo = str(tipo_divisor).strip().lower().replace("²", "2")

    if "general" in tipo:
        d = leer_polinomio(parametros)
        f = _metodo("metodos.division", "dividir")
        return f(p, d)

    if tipo.startswith("a") and "x2" in tipo:
        a, b, c = _parametros_racionales(parametros, 3, ("a", "b", "c"))
        f = _metodo("metodos.division", "dividir_por_cuadratico")
        return f(p, a, b, c)

    if "x2" in tipo:
        a, b = _parametros_racionales(parametros, 2, ("a", "b"))
        f = _metodo("metodos.division", "horner_cuadratico")
        return f(p, a, b)

    if tipo.startswith("a"):
        a, b = _parametros_racionales(parametros, 2, ("a", "b"))
        f = _metodo("metodos.division", "dividir_por_ax_mas_b")
        return f(p, a, b)

    b = _parametros_racionales(parametros, 1, ("b",))[0]
    f = _metodo("metodos.division", "dividir_por_x_mas_b")
    return f(p, b)


# ---------------------------------------------------------------------------
# Pestaña 1: esquemas de Ruffini/Horner para dibujar (solo presentación)
# ---------------------------------------------------------------------------

def _como_polinomio(valor):
    """Acepta un Polinomio, el texto del usuario o coeficientes de mayor a menor."""
    if isinstance(valor, Polinomio):
        return valor
    if isinstance(valor, str):
        return Polinomio.desde_texto(valor)
    return Polinomio(list(reversed(list(valor))))


def _texto_polinomio(coeficientes_alto):
    """Polinomio legible a partir de coeficientes de mayor a menor."""
    if not coeficientes_alto:
        return "0"
    return formatear_polinomio(list(reversed(coeficientes_alto)))


def _texto(valor):
    if valor is None:
        return ""
    if isinstance(valor, Fraction):
        return formatear_fraccion(valor)
    return str(valor)


def tabla_ruffini(polinomio, alpha):
    """Arma la tabla clásica de Ruffini de P dividido por (x - α).

    ``polinomio`` puede ser un ``Polinomio``, el texto de coeficientes o una
    lista de coeficientes de MAYOR a menor grado (como se escribe en la GUI).
    Devuelve las tres filas numéricas (``fila1``, ``fila2`` y ``fila3``) y el
    cociente/resto. La fila 1 son los coeficientes, la fila 2 los productos
    α·b_i (la primera celda es None) y la fila 3 las sumas.
    """
    p = _como_polinomio(polinomio)
    a = Fraction(alpha)
    fila1 = list(reversed(p.coef))
    fila2 = [None] * len(fila1)
    fila3 = [Fraction(0)] * len(fila1)
    fila3[0] = fila1[0]

    calculos = ["coeficiente principal"]
    for j in range(1, len(fila1)):
        fila2[j] = a * fila3[j - 1]
        fila3[j] = fila1[j] + fila2[j]
        calculos.append(
            f"{_texto(a)}·{_texto(fila3[j - 1])} + {_texto(fila1[j])} = "
            f"{_texto(fila3[j])}"
        )

    return {
        "alpha": a,
        "fila1": fila1,
        "fila2": fila2,
        "productos": fila2,
        "fila3": fila3,
        "suma": fila3,
        "cociente": fila3[:-1],
        "resto": fila3[-1],
        "calculos": calculos,
    }


def tabla_ruffini_doble(polinomio, alpha):
    """Dos esquemas de Ruffini apilados: P(α) y P'(α)."""
    p = _como_polinomio(polinomio)
    primera = tabla_ruffini(p, alpha)
    if p.grado == 0:
        return {
            "primera": primera,
            "segunda": None,
            "p_alpha": primera["resto"],
            "dp_alpha": Fraction(0),
        }

    # El cociente de la primera pasada es el polinomio que se evalúa de nuevo.
    cociente = Polinomio(list(reversed(primera["cociente"])))
    segunda = tabla_ruffini(cociente, alpha)
    return {
        "primera": primera,
        "segunda": segunda,
        "p_alpha": primera["resto"],
        "dp_alpha": segunda["resto"],
    }


def tabla_ruffini_cuadratica(polinomio, a, b):
    """Esquema de Horner cuadrático para el divisor x² + a·x + b.

    Sigue exactamente las fórmulas de ``metodos.division.horner_cuadratico``:
        c[n] = coef[n]
        c[n-1] = coef[n-1] - a·c[n]
        c[i] = coef[i] - a·c[i+1] - b·c[i+2]
        c[0] = coef[0] - b·c[2]
    El cociente es c[2:] y el resto c[1]·x + c[0]. Se agregan las dos filas
    de productos para poder dibujar el esquema del apunte.
    """
    p = _como_polinomio(polinomio)
    a = Fraction(a)
    b = Fraction(b)
    n = p.grado
    coef = p.coef

    if n < 2:
        return {
            "tipo": "cuadratica",
            "grado_menor": True,
            "a": a,
            "b": b,
            "fila1": list(reversed(coef)),
            "fila2": [None] * len(coef),
            "fila3": [None] * len(coef),
            "productos_a": [None] * len(coef),
            "productos_b": [None] * len(coef),
            "suma": [None] * len(coef),
            "cociente": [],
            "resto": list(reversed(coef)),
            "calculos": ["El grado de P es menor que el del divisor."],
        }

    c = [Fraction(0)] * (n + 1)
    c[n] = coef[n]
    c[n - 1] = coef[n - 1] - a * c[n]
    for i in range(n - 2, 0, -1):
        c[i] = coef[i] - a * c[i + 1] - b * c[i + 2]
    c[0] = coef[0] - b * c[2]

    fila1 = list(reversed(coef))
    suma = list(reversed(c))
    productos_a = [None] * (n + 1)
    productos_b = [None] * (n + 1)
    calculos = []

    for j, i in enumerate(range(n, -1, -1)):
        if i + 1 <= n:
            productos_a[j] = -a * c[i + 1]
        if i + 2 <= n:
            productos_b[j] = -b * c[i + 2]

        if i == n:
            calculos.append("baja el coeficiente principal")
        elif i == n - 1:
            calculos.append(
                f"{_texto(fila1[j])} − {_texto(a)}·{_texto(c[i + 1])} = "
                f"{_texto(c[i])}"
            )
        elif i == 0:
            calculos.append(
                f"{_texto(fila1[j])} − {_texto(b)}·{_texto(c[i + 2])} = "
                f"{_texto(c[i])}"
            )
        else:
            calculos.append(
                f"{_texto(fila1[j])} − {_texto(a)}·{_texto(c[i + 1])} − "
                f"{_texto(b)}·{_texto(c[i + 2])} = {_texto(c[i])}"
            )

    return {
        "tipo": "cuadratica",
        "grado_menor": False,
        "a": a,
        "b": b,
        "fila1": fila1,
        "fila2": productos_a,
        "productos_a": productos_a,
        "productos_b": productos_b,
        "fila3": suma,
        "suma": suma,
        "cociente": list(reversed(c[2:])),
        "resto": [c[1], c[0]],
        "calculos": calculos,
    }


def tabla_ruffini_cuadratica_normalizada(polinomio, a, b, c):
    """Ruffini cuadrático para ax² + bx + c, normalizando por a.

    P / (a·x² + b·x + c) = (1/a) · P / (x² + (b/a)·x + c/a).
    Se dibuja el esquema del divisor mónico y se divide el cociente por a.
    """
    p = _como_polinomio(polinomio)
    a = Fraction(a)
    if a == 0:
        raise EntradaInvalida("El coeficiente 'a' de ax² + bx + c no puede ser 0.")
    b = Fraction(b)
    c = Fraction(c)
    base = tabla_ruffini_cuadratica(p, b / a, c / a)
    base["normalizada"] = a
    base["cociente_sin_normalizar"] = list(base["cociente"])
    base["cociente"] = [coef / a for coef in base["cociente"]]
    return base


def tabla_ruffini_ax_mas_b(polinomio, a, b):
    """Ruffini para ax + b: α = −b/a y el cociente se divide por a."""
    p = _como_polinomio(polinomio)
    a = Fraction(a)
    if a == 0:
        raise EntradaInvalida("El coeficiente 'a' de ax + b no puede ser 0.")
    b = Fraction(b)
    base = tabla_ruffini(p, -b / a)
    base["normalizada"] = a
    base["cociente_sin_normalizar"] = list(base["cociente"])
    base["cociente"] = [coef / a for coef in base["cociente"]]
    return base


def _seccion_ruffini(datos, etiqueta_alpha, titulo=None, nota="", cuadratica=False):
    """Convierte las filas numéricas de Ruffini en una sección para la vista."""
    fila1 = datos["fila1"]
    fila2 = datos.get("productos_a", datos["fila2"]) if cuadratica else datos["fila2"]
    fila3 = datos["fila3"]
    ancho = len(fila1) + 1
    filas = [
        {
            "valores": [""] + [_texto(v) for v in fila1],
            "tipo": "coef",
            "calculos": [""] + list(datos["calculos"]),
        },
        {
            "valores": [etiqueta_alpha] + ["" if v is None else _texto(v) for v in fila2],
            "tipo": "producto",
            "calculos": [""] * ancho,
        },
    ]
    if cuadratica:
        productos_b = datos.get("productos_b", [None] * len(fila1))
        filas.append(
            {
                "valores": ["−b·c"] + ["" if v is None else _texto(v) for v in productos_b],
                "tipo": "producto",
                "calculos": [""] * ancho,
            }
        )
    filas.append(
        {
            "valores": [""] + [_texto(v) for v in fila3],
            "tipo": "suma",
            "separador_arriba": True,
            "calculos": [""] + list(datos["calculos"]),
        }
    )

    # Las celdas de resto son las últimas de la fila de sumas. En el esquema
    # cuadrático el resto tiene grado 1 y ocupa las dos últimas columnas.
    ultima = len(filas) - 1
    resto = [(ultima, len(fila1))] if not cuadratica else [
        (ultima, len(fila1) - 1),
        (ultima, len(fila1)),
    ]
    return {
        "titulo": titulo,
        "columnas": None,
        "filas": filas,
        "resto": resto,
        "cociente": [(ultima, j) for j in range(1, len(fila1))],
        "nota": nota,
    }


def _seccion_tabla(columnas, filas, titulo=None, nota=""):
    return {
        "titulo": titulo,
        "columnas": list(columnas),
        "filas": list(filas),
        "nota": nota,
    }


def _esquema_evaluacion_directa(pasos):
    filas = []
    for paso in pasos:
        filas.append(
            {
                "valores": [
                    str(paso["i"]),
                    _texto(paso["coef"]),
                    _texto(paso["potencia"]),
                    _texto(paso["termino"]),
                    _texto(paso["acumulado"]),
                ],
                "tipo": "normal",
                "calculos": [
                    f"grado {paso['i']}",
                    _texto(paso["coef"]),
                    f"α^{paso['i']} = {_texto(paso['potencia'])}",
                    f"{_texto(paso['coef'])}·{_texto(paso['potencia'])} = {_texto(paso['termino'])}",
                    f"suma acumulada = {_texto(paso['acumulado'])}",
                ],
            }
        )
    return _seccion_tabla(
        ["i", "Coef", "α^i", "Coef · α^i", "Acumulado"],
        filas,
        nota="Evaluación directa: se suman los términos uno por uno.",
    )


def esquema_evaluacion(texto, alpha, metodo):
    """Devuelve las secciones y los pasos de animación de la pestaña 1."""
    p = leer_polinomio(texto)
    a = parsear_racional(alpha, "el punto α")
    clave = str(metodo).strip().lower()

    if clave.startswith("directa"):
        resultado = evaluar(texto, alpha, metodo)
        seccion = _esquema_evaluacion_directa(resultado.pasos)
        pasos = [{"seccion": 0, "fila": i} for i in range(len(resultado.pasos))]
        return {"secciones": [seccion], "pasos": pasos}

    if "doble" in clave:
        datos = tabla_ruffini_doble(p, a)
        primera = _seccion_ruffini(
            datos["primera"],
            f"α = {_texto(a)}",
            "P(α)",
            f"P(α) = {_texto(datos['p_alpha'])}",
        )
        if datos["segunda"] is not None:
            segunda = _seccion_ruffini(
                datos["segunda"],
                f"α = {_texto(a)}",
                "P'(α)",
                f"P'(α) = {_texto(datos['dp_alpha'])}",
            )
            secciones = [primera, segunda]
            pasos = [
                {"seccion": 0, "columna": j, "filas": [0, 1, 2]}
                for j in range(1, len(datos["primera"]["fila1"]) + 1)
            ]
            pasos += [
                {"seccion": 1, "columna": j, "filas": [0, 1, 2]}
                for j in range(1, len(datos["segunda"]["fila1"]) + 1)
            ]
        else:
            secciones = [primera]
            pasos = [
                {"seccion": 0, "columna": j, "filas": [0, 1, 2]}
                for j in range(1, len(datos["primera"]["fila1"]) + 1)
            ]
        return {"secciones": secciones, "pasos": pasos}

    datos = tabla_ruffini(p, a)
    seccion = _seccion_ruffini(
        datos,
        f"α = {_texto(a)}",
        nota=f"Cociente: {_texto_polinomio(datos['cociente'])} · "
        f"Resto = P(α) = {_texto(datos['resto'])}",
    )
    pasos = [
        {"seccion": 0, "columna": j, "filas": [0, 1, 2]}
        for j in range(1, len(datos["fila1"]) + 1)
    ]
    return {"secciones": [seccion], "pasos": pasos}


def _esquema_division_general(resultado):
    filas = []
    for paso in resultado.pasos:
        filas.append(
            {
                "valores": [
                    str(paso["k"]),
                    _texto(paso["factor"]),
                    formatear_polinomio(paso["resto"]),
                ],
                "tipo": "normal",
                "calculos": [
                    f"grado del cociente: {paso['k']}",
                    f"factor = {_texto(paso['factor'])}",
                    f"resto parcial = {formatear_polinomio(paso['resto'])}",
                ],
            }
        )
    cociente, resto = resultado.valor
    return _seccion_tabla(
        ["k", "Factor", "Resto parcial"],
        filas,
        nota=f"Cociente: {cociente} · Resto: {resto}",
    )


def esquema_division(texto, tipo_divisor, parametros):
    """Devuelve las secciones y los pasos de animación de la pestaña 1."""
    p = leer_polinomio(texto)
    tipo = str(tipo_divisor).strip().lower().replace("²", "2")

    if "general" in tipo:
        resultado = dividir(texto, tipo_divisor, parametros)
        seccion = _esquema_division_general(resultado)
        pasos = [{"seccion": 0, "fila": i} for i in range(len(resultado.pasos))]
        return {"secciones": [seccion], "pasos": pasos}

    if tipo.startswith("a") and "x2" in tipo:
        a, b, c = _parametros_racionales(parametros, 3, ("a", "b", "c"))
        datos = tabla_ruffini_cuadratica_normalizada(p, a, b, c)
        nota = (
            f"Divisor normalizado: x² + {_texto(Fraction(b, 1) / Fraction(a))}·x + "
            f"{_texto(Fraction(c, 1) / Fraction(a))}. "
            f"El cociente del esquema se divide por a = {_texto(Fraction(a))}."
        )
        seccion = _seccion_ruffini(
            datos,
            "−b/a, −c/a",
            nota=nota + " · Cociente: " + _texto_polinomio(datos["cociente"]),
            cuadratica=True,
        )
        pasos = [
            {"seccion": 0, "columna": j, "filas": [0, 1, 2, 3]}
            for j in range(1, len(datos["fila1"]) + 1)
        ]
        return {"secciones": [seccion], "pasos": pasos}

    if "x2" in tipo:
        a, b = _parametros_racionales(parametros, 2, ("a", "b"))
        datos = tabla_ruffini_cuadratica(p, a, b)
        if datos.get("grado_menor"):
            seccion = _seccion_tabla(
                ["Coeficiente"],
                [{"valores": [_texto(v)], "tipo": "normal"} for v in datos["fila1"]],
                nota="El grado de P es menor que el del divisor: C(x) = 0 y R(x) = P(x).",
            )
            return {"secciones": [seccion], "pasos": []}
        seccion = _seccion_ruffini(
            datos,
            "−a, −b",
            nota=f"Cociente: {_texto_polinomio(datos['cociente'])} · "
            f"Resto: {_texto_polinomio(datos['resto'])}",
            cuadratica=True,
        )
        pasos = [
            {"seccion": 0, "columna": j, "filas": [0, 1, 2, 3]}
            for j in range(1, len(datos["fila1"]) + 1)
        ]
        return {"secciones": [seccion], "pasos": pasos}

    if tipo.startswith("a"):
        a, b = _parametros_racionales(parametros, 2, ("a", "b"))
        datos = tabla_ruffini_ax_mas_b(p, a, b)
        alpha = -Fraction(b) / Fraction(a)
        seccion = _seccion_ruffini(
            datos,
            f"α = {_texto(alpha)}",
            nota=f"α = −b/a = {_texto(alpha)}. Cociente final = "
            f"{_texto_polinomio(datos['cociente'])} · Resto = {_texto(datos['resto'])}",
        )
        pasos = [
            {"seccion": 0, "columna": j, "filas": [0, 1, 2]}
            for j in range(1, len(datos["fila1"]) + 1)
        ]
        return {"secciones": [seccion], "pasos": pasos}

    b = _parametros_racionales(parametros, 1, ("b",))[0]
    datos = tabla_ruffini(p, -Fraction(b))
    seccion = _seccion_ruffini(
        datos,
        f"α = −b = {_texto(-Fraction(b))}",
        nota=f"Cociente: {_texto_polinomio(datos['cociente'])} · "
        f"Resto: {_texto(datos['resto'])}",
    )
    pasos = [
        {"seccion": 0, "columna": j, "filas": [0, 1, 2]}
        for j in range(1, len(datos["fila1"]) + 1)
    ]
    return {"secciones": [seccion], "pasos": pasos}


# ---------------------------------------------------------------------------
# Pestaña 2: raíces enteras y racionales
# ---------------------------------------------------------------------------

def _sin_repetidos(textos):
    vistos = set()
    resultado = []
    for texto in textos:
        if texto and texto not in vistos:
            vistos.add(texto)
            resultado.append(texto)
    return resultado


def factorizar_raices(texto, raices):
    """Divide P por (x - r) tantas veces como aparezca cada raíz exacta.

    Devuelve ``{"factores": [Fraction], "residual": Polinomio}`` donde
    ``factores`` repite cada raíz según su multiplicidad y ``residual`` es lo
    que queda cuando ya no se puede dividir exactamente. La GUI solo arma el
    texto de la factorización; la cuenta la hace esta capa.
    """
    p = leer_polinomio(texto)
    dividir_lineal = _metodo("metodos.division", "dividir_por_x_mas_b")
    factores = []
    q = p
    for raiz in raices:
        r = Fraction(raiz)
        while q.grado >= 1:
            cociente, resto = dividir_lineal(q, -r).valor
            if resto != 0:
                break
            factores.append(r)
            q = cociente
    return {"factores": factores, "residual": q}


def _valores_en_p(p, pasos):
    """Reemplaza el valor de cada paso por ``P(candidato)``.

    El núcleo evalúa el polinomio sin los factores ``x`` (``Q``) para buscar
    las raíces distintas de 0. Para la tabla conviene mostrar el valor real en
    el polinomio original, sobre todo cuando ``P`` tiene una raíz en 0.
    """
    horner = _metodo("metodos.evaluacion", "horner_fraction")
    resultado = []
    for paso in pasos:
        copia = dict(paso)
        valor = horner(p, Fraction(copia["candidato"])).valor
        copia["valor"] = valor
        copia["es_raiz"] = valor == 0
        resultado.append(copia)
    return resultado


def raices(texto, modo="Ambas"):
    """Raíces enteras, racionales o ambas, exactas."""
    p = leer_polinomio(texto)
    clave = str(modo).strip().lower()
    f_enteras = _metodo("metodos.raices", "raices_enteras")
    f_racionales = _metodo("metodos.raices", "raices_racionales")

    if clave.startswith("enter"):
        resultado = f_enteras(p)
        resultado.pasos = _valores_en_p(p, resultado.pasos)
        return resultado
    if clave.startswith("rac"):
        resultado = f_racionales(p)
        resultado.pasos = _valores_en_p(p, resultado.pasos)
        return resultado
    if not clave.startswith("amb"):
        raise EntradaInvalida("Elegí un modo de búsqueda válido.")

    resultado_enteras = f_enteras(p)
    resultado_racionales = f_racionales(p)

    # La tabla de "ambas" muestra cada candidato una sola vez y conserva p/q
    # cuando el candidato también proviene del criterio de Gauss.
    por_candidato = {}
    for paso in resultado_enteras.pasos:
        candidato = Fraction(paso["candidato"])
        por_candidato[candidato] = {**paso, "tipo": "entera"}
    for paso in resultado_racionales.pasos:
        candidato = Fraction(paso["candidato"])
        if candidato in por_candidato:
            por_candidato[candidato] = {**paso, "tipo": "entera y racional"}
        else:
            por_candidato[candidato] = {**paso, "tipo": "racional"}

    pasos = _valores_en_p(p, [por_candidato[c] for c in sorted(por_candidato)])
    valor = sorted(set(resultado_enteras.valor) | set(resultado_racionales.valor))
    avisos = _sin_repetidos(resultado_enteras.avisos + resultado_racionales.avisos)
    return Resultado(
        valor=valor,
        iteraciones=len(pasos),
        pasos=pasos,
        avisos=avisos,
    )


# ---------------------------------------------------------------------------
# Pestaña 3: cotas
# ---------------------------------------------------------------------------

def _intervalo_ajustado(resultados):
    """Intersección de las cotas de cada método (la más ajustada)."""
    valores = {clave: r.valor for clave, r in resultados.items() if r.valor}
    if not valores:
        return {"inf": Fraction(0), "sup": Fraction(0), "pos": None, "neg": None, "sin_raices": True}

    especificos = [valores[k] for k in ("lagrange", "laguerre", "newton") if k in valores]
    tiene_pos = any(v.get("sup_pos", 0) > 0 for v in especificos)
    tiene_neg = any(v.get("inf_neg", 0) < 0 for v in especificos)

    inf_pos = max(v.get("inf_pos", Fraction(0)) for v in valores.values())
    sup_pos = min(v.get("sup_pos", Fraction(0)) for v in valores.values())
    inf_neg = max(v.get("inf_neg", Fraction(0)) for v in valores.values())
    sup_neg = min(v.get("sup_neg", Fraction(0)) for v in valores.values())

    pos = (inf_pos, sup_pos) if tiene_pos else None
    neg = (inf_neg, sup_neg) if tiene_neg else None
    if pos is None and neg is None:
        return {
            "inf": Fraction(0),
            "sup": Fraction(0),
            "pos": None,
            "neg": None,
            "sin_raices": True,
        }

    inf = inf_neg if tiene_neg else inf_pos
    sup = sup_pos if tiene_pos else sup_neg
    return {"inf": inf, "sup": sup, "pos": pos, "neg": neg, "sin_raices": False}


def cotas(texto):
    """Aplica Lagrange, Laguerre, Newton e implicación y arma el resumen."""
    p = leer_polinomio(texto)
    f = _metodo("metodos.cotas", "todas_las_cotas")
    resultados = f(p)

    nombres = {
        "lagrange": "Lagrange",
        "laguerre": "Laguerre",
        "newton": "Newton",
        "implicacion": "Implicación",
    }
    pasos = []
    avisos = []
    for clave, resultado in resultados.items():
        avisos.extend(resultado.avisos)
        for paso in resultado.pasos:
            pasos.append(
                {"metodo": clave, "metodo_nombre": nombres.get(clave, clave), **paso}
            )

    valor = {clave: resultado.valor for clave, resultado in resultados.items()}
    ajustado = _intervalo_ajustado(resultados)
    ajustado["cero_es_raiz"] = p.coef[0] == 0
    valor["ajustado"] = ajustado

    if p.coef[0] == 0:
        avisos.append(
            "P(0) = 0: el 0 es raíz y queda fuera de las cotas de raíces "
            "positivas y negativas."
        )

    return Resultado(
        valor=valor,
        iteraciones=len(resultados),
        pasos=pasos,
        avisos=_sin_repetidos(avisos),
    )


# ---------------------------------------------------------------------------
# Pestaña 4: Newton y Halley
# ---------------------------------------------------------------------------

def newton_halley(texto, x0, eps_texto, max_iter_texto, metodo):
    """Ejecuta Newton-Raphson-Horner o Halley."""
    p = leer_polinomio(texto)
    x0 = float(parsear_racional(x0, "el punto inicial x0"))
    eps = parsear_tolerancia(eps_texto)
    max_iter = parsear_entero_positivo(max_iter_texto, "el máximo de iteraciones")
    clave = str(metodo).strip().lower()
    nombre = "halley" if clave.startswith("halley") else "newton"
    f = _metodo("metodos.newton_halley", nombre)
    return f(p, x0, eps, max_iter)


# ---------------------------------------------------------------------------
# Pestaña 5: Sturm
# ---------------------------------------------------------------------------

def sturm(texto, a_texto, b_texto, simplificada=False):
    """Cuenta y separa las raíces reales de P en (a, b) con Sturm."""
    p = leer_polinomio(texto)
    a = parsear_racional(a_texto, "el extremo a")
    b = parsear_racional(b_texto, "el extremo b")
    contar = _metodo("metodos.sturm", "contar_raices")
    separar = _metodo("metodos.sturm", "separar_raices")

    resultado_contar = contar(p, a, b, simplificada)
    resultado_separar = separar(p, a, b, simplificada)
    avisos = _sin_repetidos(resultado_contar.avisos + resultado_separar.avisos)

    return Resultado(
        valor={
            "cantidad": resultado_contar.valor,
            "intervalos": resultado_separar.valor,
        },
        iteraciones=resultado_contar.iteraciones,
        pasos=resultado_contar.pasos,
        avisos=avisos,
    )


def biseccion_sturm(texto, a_texto, b_texto, simplificada=False):
    """Estados de la subdivisión de Sturm para animar la pestaña 5.

    No es un método nuevo: usa ``contar_raices`` y elige puntos de corte que
    no sean raíz, igual que ``separar_raices``. Devuelve una lista de estados;
    cada estado es la frontera de intervalos con su cantidad de raíces.
    """
    p = leer_polinomio(texto)
    a = parsear_racional(a_texto, "el extremo a")
    b = parsear_racional(b_texto, "el extremo b")
    contar = _metodo("metodos.sturm", "contar_raices")
    evaluar = _metodo("metodos.evaluacion", "horner_fraction")

    def valor_en(x):
        return evaluar(p, x).valor

    def punto_no_raiz(x, y):
        for nivel in range(1, 21):
            denominador = 2 ** nivel
            for numerador in range(1, denominador, 2):
                punto = x + (y - x) * Fraction(numerador, denominador)
                if valor_en(punto) != 0:
                    return punto
        raise EntradaInvalida("No se encontró un punto de corte que no sea raíz.")

    def cantidad(x, y):
        return contar(p, x, y, simplificada).valor

    total = cantidad(a, b)
    frontera = [(a, b, total, 0)]
    estados = [
        {
            "intervalos": [(x, y, c) for x, y, c, _d in frontera],
            "division": None,
        }
    ]

    while True:
        pendiente = next(
            (i for i, (_x, _y, c, _d) in enumerate(frontera) if c > 1),
            None,
        )
        if pendiente is None:
            break
        x, y, _cantidad, profundidad = frontera[pendiente]
        punto = punto_no_raiz(x, y)
        izquierda = cantidad(x, punto)
        derecha = _cantidad - izquierda
        hijos = []
        if izquierda:
            hijos.append((x, punto, izquierda, profundidad + 1))
        if derecha:
            hijos.append((punto, y, derecha, profundidad + 1))
        frontera[pendiente : pendiente + 1] = hijos
        estados.append(
            {
                "intervalos": [(ix, iy, c) for ix, iy, c, _d in frontera],
                "division": (x, y, punto),
            }
        )
        if len(estados) > 400:
            break

    return {"a": a, "b": b, "estados": estados}


# ---------------------------------------------------------------------------
# Pestaña 6: Bairstow
# ---------------------------------------------------------------------------

def raices_del_factor(r, s):
    """Raíces de x² − r·x − s, para dibujar el movimiento de (r, s).

    Es solo presentación: usa la misma fórmula que el núcleo, con floats.
    """
    try:
        discriminante = complex(float(r) ** 2 + 4.0 * float(s), 0.0)
        raiz = cmath.sqrt(discriminante)
        return [complex((float(r) + raiz) / 2.0), complex((float(r) - raiz) / 2.0)]
    except (TypeError, ValueError, OverflowError):
        return []


def _anotar_raices_por_factor(pasos):
    """Agrega las raíces del factor en la última fila de cada factor.

    También guarda en cada paso ``raices_actuales``: las raíces del factor
    cuadrático con el (r, s) de esa iteración, para animar su movimiento.
    """
    copia = [dict(paso) for paso in pasos]
    grupos = {}
    for i, paso in enumerate(copia):
        grupos.setdefault(paso.get("factor"), []).append(i)
        try:
            copia[i]["raices_actuales"] = tuple(
                raices_del_factor(paso["r"], paso["s"])
            )
        except (KeyError, TypeError, ValueError):
            copia[i]["raices_actuales"] = ()

    for indices in grupos.values():
        ultimo = copia[indices[-1]]
        try:
            r = ultimo["r"] + ultimo["dr"]
            s = ultimo["s"] + ultimo["ds"]
            ultimo["raices_factor"] = tuple(raices_del_factor(r, s))
        except (KeyError, TypeError, ValueError, ZeroDivisionError):
            pass
    return copia


def bairstow(texto, r0_texto, s0_texto, eps_texto, max_iter_texto):
    """Ejecuta Bairstow y anota las raíces que aporta cada factor."""
    p = leer_polinomio(texto)
    r0 = _a_float(r0_texto, "el valor inicial r0")
    s0 = _a_float(s0_texto, "el valor inicial s0")
    eps = parsear_tolerancia(eps_texto)
    max_iter = parsear_entero_positivo(max_iter_texto, "el máximo de iteraciones")
    f = _metodo("metodos.bairstow", "bairstow")
    resultado = f(p, r0, s0, eps, max_iter)
    resultado.pasos = _anotar_raices_por_factor(resultado.pasos)
    return resultado


# Valores por defecto reexportados para las pestañas.
__all__ = [
    "EPS_DEFAULT",
    "MAX_ITER",
    "bairstow",
    "biseccion_sturm",
    "coeficientes_float",
    "cotas",
    "dividir",
    "esquema_division",
    "esquema_evaluacion",
    "evaluar",
    "factorizar_raices",
    "leer_polinomio",
    "newton_halley",
    "parsear_entero_positivo",
    "parsear_racional",
    "parsear_tolerancia",
    "raices",
    "raices_del_factor",
    "sturm",
    "tabla_ruffini",
    "tabla_ruffini_ax_mas_b",
    "tabla_ruffini_cuadratica",
    "tabla_ruffini_cuadratica_normalizada",
    "tabla_ruffini_doble",
]
