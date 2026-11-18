"""Construcción de esquemas (Ruffini / Horner / Horner doble / división larga)."""

from fractions import Fraction

from core.polinomio import Polinomio
from metodos.division import dividir, horner_cuadratico
from metodos.evaluacion import horner_fraction

_SUP = "⁰¹²³⁴⁵⁶⁷⁸⁹"


def fmt(x):
    x = Fraction(x)
    s = str(x.numerator) if x.denominator == 1 else f"{x.numerator}/{x.denominator}"
    return s.replace("-", "−")


def _sup(e):
    return "".join(_SUP[int(ch)] for ch in str(e))


def _limpiar(coef):
    c = [Fraction(v) for v in coef]
    while len(c) > 1 and c[0] == 0:
        c.pop(0)
    return c


def poly_texto(coef, var="x"):
    """Texto de un polinomio con coeficientes de mayor a menor grado."""
    c = [Fraction(v) for v in coef]
    n = len(c) - 1
    partes = []
    for i, v in enumerate(c):
        if v == 0:
            continue
        e = n - i
        mag = abs(v)
        if e == 0:
            cuerpo = fmt(mag)
        else:
            k = "" if mag == 1 else (fmt(mag) if mag.denominator == 1 else f"({fmt(mag)})")
            cuerpo = k + var + ("" if e == 1 else _sup(e))
        signo = "−" if v < 0 else "+"
        partes.append((signo, cuerpo))
    if not partes:
        return "0"
    s, cuerpo = partes[0]
    out = ("−" if s == "−" else "") + cuerpo
    for s, cuerpo in partes[1:]:
        out += f" {s} {cuerpo}"
    return out


def termino(c, e, primero=False):
    c = Fraction(c)
    if c == 0:
        return ""
    mag = abs(c)
    if e == 0:
        cuerpo = fmt(mag)
    else:
        k = "" if mag == 1 else (fmt(mag) if mag.denominator == 1 else f"({fmt(mag)})")
        cuerpo = k + "x" + ("" if e == 1 else _sup(e))
    if primero:
        return ("−" if c < 0 else "") + cuerpo
    return f"{'−' if c < 0 else '+'} {cuerpo}"


def _identidad(a, d, cociente, resto, nom_c="Q"):
    c_txt = poly_texto(cociente) if cociente else "0"
    r_txt = poly_texto(resto) if len(resto) > 1 else fmt(resto[0])
    partes = [
        (poly_texto(a), "p"), (" = (", "t"), (poly_texto(d), "d"), (")·(", "t"),
        (c_txt, "q"), (") + (", "t"), (r_txt, "r"), (")", "t"),
    ]
    return partes, c_txt, r_txt


def _a_polinomio(coef_alto):
    """Polinomio de `metodos` a partir de coeficientes de mayor a menor grado."""
    return Polinomio(list(reversed(coef_alto)))


def _division_larga(a, d, titulo, nota, nom_p, nom_d):
    """División larga estándar (como en el cuaderno)."""
    n, m = len(a) - 1, len(d) - 1
    resultado = dividir(_a_polinomio(a), _a_polinomio(d))
    q_poly, r_poly = resultado.valor
    cociente = list(reversed(q_poly.coef))
    resto = list(reversed(r_poly.coef))
    dividendo = {n - i: v for i, v in enumerate(a) if v != 0}

    pasos = []
    for paso in resultado.pasos:
        factor = paso["factor"]
        if factor == 0:
            continue
        g = paso["k"]
        prod = {m - j + g: -(dv * factor) for j, dv in enumerate(d) if dv != 0}
        nuevo = {e: v for e, v in enumerate(paso["resto"]) if v != 0}
        pasos.append({"q": factor, "grado": g, "prod": prod, "resto": nuevo})

    ident, c_txt, r_txt = _identidad(a, d, cociente, resto)
    esq = {
        "tipo": "larga", "n": n, "m": m,
        "dividendo": dividendo, "divisor": d,
        "pasos": pasos, "cociente_coef": cociente, "resto": resto,
        "titulo": titulo, "nota": nota,
        "cabecera": [("", f"{nom_p}(x) = {poly_texto(a)}"),
                     ("", f"{nom_d}(x) = {poly_texto(d)}")],
        "identidad": ident, "q_txt": c_txt, "r_txt": r_txt,
    }
    return esq, cociente, resto


def esquema_division(coef, divisor, titulo=None, nota=None, *,
                     nom_dividendo="P", nom_divisor="D", larga=None):
    a = _limpiar(coef)
    d = _limpiar(divisor)
    m = len(d) - 1
    n = len(a) - 1
    if m < 1 or d[0] == 0:
        raise ValueError("El divisor debe tener grado 1 o más.")
    if n < m:
        raise ValueError("El grado del dividendo debe ser mayor o igual al del divisor.")

    if larga is None:
        larga = m >= 3
    if larga:
        return _division_larga(a, d, titulo, nota, nom_dividendo, nom_divisor)

    # --- Esquema matricial (Ruffini / Horner) ---
    lead = d[0]
    p = _a_polinomio(a)
    nq = n - m + 1

    if m == 1:
        w = list(reversed(horner_fraction(p, -d[1] / lead).pasos[0]["b"]))
    elif m == 2:
        coef_h = horner_cuadratico(p, d[1] / lead, d[2] / lead).pasos[0]["c"]
        w = list(reversed(coef_h))
    else:
        q_poly, r_poly = dividir(p, _a_polinomio(d)).valor
        q_alto = list(reversed(q_poly.coef))
        r_alto = list(reversed(r_poly.coef))
        q_alto = [Fraction(0)] * (nq - len(q_alto)) + q_alto
        r_alto = [Fraction(0)] * (m - len(r_alto)) + r_alto
        w = [lead * v for v in q_alto] + r_alto

    mon = [c / lead for c in d]
    mult = [-mon[j] for j in range(1, m + 1)]
    prods = [[""] * (n + 1) for _ in range(m)]
    for j in range(1, m + 1):
        for k in range(nq):
            prods[j - 1][k + j] = fmt(w[k] * mult[j - 1])

    tabla_q = w[:nq]
    resto = w[nq:]
    cociente = [q / lead for q in tabla_q]

    filas = [{"etiqueta": "", "celdas": [fmt(v) for v in a], "tipo": "datos"}]
    for j in range(m):
        filas.append({"etiqueta": fmt(mult[j]), "celdas": prods[j], "tipo": "producto"})
    filas.append({"etiqueta": "", "celdas": [fmt(v) for v in w], "tipo": "resultado"})

    ident, c_txt, r_txt = _identidad(a, d, cociente, resto)
    esq = {
        "tipo": "matricial",
        "titulo": titulo,
        "filas": filas,
        "cociente": (0, nq - 1),
        "resto": (nq, n),
        "nota": nota,
        "etq_c": "C(x)",
        "etq_r": "R" if m == 1 else "R(x)",
        "cabecera": [("", f"{nom_dividendo}(x) = {poly_texto(a)}"),
                     ("", f"{nom_divisor}(x) = {poly_texto(d)}")],
        "identidad": ident, "q_txt": c_txt, "r_txt": r_txt,
    }
    if lead != 1:
        esq["etq_c"] = f"{fmt(lead)}·C(x)"
        aviso = f"Divisor no mónico: se dividió por {fmt(lead)}. El cociente verdadero es el de la tabla ÷ {fmt(lead)}."
        esq["nota"] = f"{nota}  {aviso}" if nota else aviso

    return esq, cociente, resto


def esquema_horner_doble(coef, alpha):
    """Devuelve (lista de esquemas, P(α), P'(α))."""
    alpha = Fraction(alpha)
    a_s = fmt(alpha)
    d_s = poly_texto([1, -alpha])

    e1, q1, r1 = esquema_division(
        coef, [1, -alpha],
        f"Horner doble · 1.ª división por ({d_s}): el resto es P({a_s})",
        nom_dividendo="P", larga=False)
    p_alpha = r1[0]
    e1["etq_c"], e1["etq_r"] = "Q(x)", f"P({a_s})"

    if len(q1) == 1:
        return [e1], p_alpha, q1[0]

    e2, q2, r2 = esquema_division(
        q1, [1, -alpha],
        f"Horner doble · 2.ª división por ({d_s}): el resto es Q({a_s}) = P′({a_s})",
        nom_dividendo="Q", larga=False)
    dp_alpha = r2[0]
    e2["etq_c"], e2["etq_r"] = "S(x)", f"P′({a_s})"

    return [e1, e2], p_alpha, dp_alpha