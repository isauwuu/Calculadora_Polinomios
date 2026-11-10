# Progreso del núcleo matemático

Rama de trabajo: `feat/raices` (una rama por método).

## Diagnóstico inicial (2026-11-10)

Documentación leída de `pdf/` (el AGENTS.md habla de `docs/apunte.pdf` y
`docs/diseno_v2.pdf`; los archivos reales son `pdf/Raices de Polinomios2.pdf` y
`pdf/Diseno_Proyecto_Raices_Polinomios_v2.pdf`).

### Completo

- `core/`: errores, config, numeros, polinomio, resultado.
- `metodos/evaluacion.py`: evaluación directa, Horner exacto y en float, Horner
  doble y triple.
- `metodos/division.py`: división por `(x + b)`, por `(ax + b)`, Horner
  cuadrático, división por cuadrático y división general.
- `metodos/raices_enteras.py`: auxiliar `divisores(x)`.
- Tests existentes de core, evaluación y división.

### Falta

- `metodos/raices.py`: raíces enteras y racionales exactas (issue #4).
- `metodos/newton_halley.py`: Newton-Raphson-Horner y Halley (issues #8 y #14).
- `metodos/diagnostico.py`: ciclo, error creciente, convergencia lineal (#15).
- `metodos/cotas.py`: Lagrange, Laguerre, Newton e implicación (#5, #6, #7).
- `metodos/sturm.py`: sucesión estándar/simplificada y separación (#9, #10).
- `metodos/bairstow.py`: factores cuadráticos y raíces complejas (#16).
- Pruebas de todos esos métodos y `docs/DUDAS.md`.

### Decisiones y ambigüedades

- Los pasos siguen el formato fijo del diseño v2 (sección 3.2).
- Criterio de parada mixto para iterativos:
  `abs(dx) <= eps * max(1.0, abs(x))`.
- Halley usa `P''` completa en la fórmula; `horner3_float` ya devuelve `P''`.
- Bairstow usa el factor `x^2 - r*x - s`; la interfaz convertirá a
  `x^2 + p*x + q` con `p = -r`, `q = -s`.
- Las cotas se devuelven como `Fraction`; cuando la raíz k-ésima no es exacta
  se usa una cota racional superior conservadora (ver `docs/DUDAS.md`).
- Las dudas abiertas se registran en `docs/DUDAS.md`.

## Registro por método

| Método | Estado | Tests |
|---|---|---|
| Raíces enteras y racionales | completo | `tests/test_raices.py` (10 tests) |
