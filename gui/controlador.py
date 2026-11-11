"""Capa fina entre la interfaz y el núcleo matemático.

No importa tkinter: recibe texto, valida, llama a ``metodos/`` y devuelve un
``Resultado``. Los imports de los métodos se hacen dentro de cada función para
que una pestaña pueda avisar "Método aún no disponible" sin romper la ventana.
"""

import importlib
import math
from fractions import Fraction

from core.config import EPS_DEFAULT, MAX_ITER
from core.errores import EntradaInvalida, PolinomioInvalido, ToleranciaInvalida
from core.numeros import parsear_coeficientes, parsear_numero
from core.polinomio import Polinomio
from core.resultado import Resultado


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


# ---------------------------------------------------------------------------
# Pestaña 6: Bairstow
# ---------------------------------------------------------------------------

def _anotar_raices_por_factor(pasos):
    """Agrega las raíces del factor en la última fila de cada factor."""
    copia = [dict(paso) for paso in pasos]
    grupos = {}
    for i, paso in enumerate(copia):
        grupos.setdefault(paso.get("factor"), []).append(i)
    try:
        from metodos.bairstow import _raices_factor
    except ImportError:
        return copia

    for indices in grupos.values():
        ultimo = copia[indices[-1]]
        try:
            r = ultimo["r"] + ultimo["dr"]
            s = ultimo["s"] + ultimo["ds"]
            ultimo["raices_factor"] = tuple(_raices_factor(r, s))
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
    "coeficientes_float",
    "cotas",
    "dividir",
    "evaluar",
    "factorizar_raices",
    "leer_polinomio",
    "newton_halley",
    "parsear_entero_positivo",
    "parsear_racional",
    "parsear_tolerancia",
    "raices",
    "sturm",
]
