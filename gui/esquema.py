"""Construcción de esquemas (Ruffini / Horner / Horner doble / división larga)."""

from fractions import Fraction

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


def _division_larga(a, d, titulo, nota, nom_p, nom_d):
    """División larga estándar (como en el cuaderno)."""
    n, m = len(a) - 1, len(d) - 1
    cur = {n - i: v for i, v in enumerate(a) if v != 0}
    dividendo = dict(cur)
    cociente = [Fraction(0)] * (n - m + 1)
    pasos = []

    while cur and max(cur) >= m:
        gc = max(cur)
        q = cur[gc] / d[0]
        g = gc - m
        cociente[n - m - g] = q
        prod = {m - i + g: dv * q for i, dv in enumerate(d) if dv != 0}
        nuevo = dict(cur)
        for e, v in prod.items():
            r = nuevo.get(e, Fraction(0)) - v
            if r == 0:
                nuevo.pop(e, None)
            else:
                nuevo[e] = r
        pasos.append({"q": q, "grado": g, "prod": {e: -v for e, v in prod.items()}, "resto": nuevo})
        cur = nuevo

    resto = [cur.get(e, Fraction(0)) for e in range(max(cur), -1, -1)] if cur else [Fraction(0)]
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
    mon = [c / lead for c in d]
    mult = [-mon[j] for j in range(1, m + 1)]
    w = list(a)
    prods = [[""] * (n + 1) for _ in range(m)]

    for k in range(n - m + 1):
        q = w[k]
        for j in range(1, m + 1):
            p = q * mult[j - 1]
            prods[j - 1][k + j] = fmt(p)
            w[k + j] += p

    nq = n - m + 1
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


def esquema_evaluacion_directa(coef, alpha):
    a = _limpiar(coef)
    alpha = Fraction(alpha)
    n = len(a) - 1
    pot, term = [], []
    total = Fraction(0)
    sumandos = []
    for i, c in enumerate(a):
        e = n - i
        t = c * alpha ** e
        total += t
        pot.append(fmt(alpha ** e))
        term.append(fmt(t))
        cs = f"({fmt(c)})" if c < 0 else fmt(c)
        if e == 0:
            sumandos.append(cs)
        elif e == 1:
            sumandos.append(f"{cs}·({fmt(alpha)})")
        else:
            sumandos.append(f"{cs}·({fmt(alpha)}){_sup(e)}")

    filas = [
        {"etiqueta": "aᵢ", "celdas": [fmt(c) for c in a], "tipo": "datos"},
        {"etiqueta": "αⁱ", "celdas": pot, "tipo": "producto"},
        {"etiqueta": "aᵢ·αⁱ", "celdas": term, "tipo": "producto"},
    ]
    esq = {
        "tipo": "matricial", "titulo": "Evaluación directa", "filas": filas,
        "cociente": None, "resto": None,
        "nota": f"P(α) = suma de la última fila = {fmt(total)}",
        "cabecera": [("", f"P(x) = {poly_texto(a)}"),
                     ("", f"α = {fmt(alpha)}")],
        "identidad": [(f"P({fmt(alpha)})", "p"), (" = ", "t"), (" + ".join(sumandos), "t"),
                      (" = ", "t"), (fmt(total), "r")],
        "q_txt": None, "r_txt": fmt(total),
    }
    return esq, total


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