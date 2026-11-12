import math


def _diagnostico_vacio() -> dict:
    return {"ciclo": None, "creciente": False, "ratio_lineal": None, "filas_rojas": []}


def analizar(pasos, eps=1e-6) -> dict:
    """Analiza los pasos de un método iterativo. Función pura, nunca lanza.

    Devuelve:
      ciclo        (desde, hasta, periodo) si un x se repite, o None
      creciente    True si el error |dx| creció dos veces seguidas
      ratio_lineal razón constante si el error baja como una progresión
                   geométrica (señal típica de raíz múltiple), o None
      filas_rojas  índices de las filas a resaltar (ciclo o error creciente)

    El parámetro eps se mantiene por compatibilidad con la firma del diseño;
    las comparaciones de ciclo usan una tolerancia fija y conservadora.
    """
    d = _diagnostico_vacio()
    try:
        if not pasos:
            return d

        xs = [float(paso["x"]) for paso in pasos]

        # Ciclo: un x vuelve a un valor ya visto (no al inmediato anterior).
        for i in range(2, len(xs)):
            for j in range(i - 1):
                if math.isclose(xs[i], xs[j], rel_tol=1e-9, abs_tol=1e-12):
                    d["ciclo"] = (j, i, i - j)
                    d["filas_rojas"].extend([j, i])
                    break
            if d["ciclo"] is not None:
                break

        dxs = [abs(float(paso["dx"])) for paso in pasos]
        if len(dxs) >= 3 and dxs[-1] > dxs[-2] > dxs[-3]:
            d["creciente"] = True
            d["filas_rojas"].extend([len(dxs) - 3, len(dxs) - 2, len(dxs) - 1])

        if len(dxs) >= 4 and all(dxs[-k] > 0 for k in (1, 2, 3)):
            razones = [dxs[-1] / dxs[-2], dxs[-2] / dxs[-3]]
            if all(0.3 < r < 0.9 for r in razones) and abs(razones[0] - razones[1]) < 0.1:
                d["ratio_lineal"] = razones[0]

        # Sin repetidos y en orden, para que la GUI pinte cada fila una vez.
        d["filas_rojas"] = sorted(set(d["filas_rojas"]))
        return d
    except (KeyError, TypeError, ValueError, ZeroDivisionError, OverflowError):
        return _diagnostico_vacio()
