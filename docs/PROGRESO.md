# Progreso del núcleo matemático

Rama de trabajo: una rama por método (`feat/raices`, `feat/newton-halley`,
`feat/diagnostico`, `feat/cotas`, `feat/sturm`, `feat/bairstow`).

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
| Newton-Raphson-Horner | completo | `tests/test_newton_halley.py` |
| Halley | completo | `tests/test_newton_halley.py` |
| Diagnóstico de iterativos | completo | `tests/test_diagnostico.py` |
| Cotas: Lagrange, Laguerre, Newton e implicación | completo | `tests/test_cotas.py` |
| Sturm: sucesión, conteo y separación | completo | `tests/test_sturm.py` |
| Bairstow: factores cuadráticos y raíces complejas | completo | `tests/test_bairstow.py` (22 tests) |

- `core/config.py`: se agregó `convergio(dx, x, eps)` con el criterio mixto
  `|dx| <= eps * max(1, |x|)` y se usa en Newton, Halley y Bairstow.
- Newton: pasos `n, x, p, dp, x_sig, dx`; el ejemplo del apunte da
  `2.49086366` en 4 iteraciones con `eps = 1e-3`.
- Halley: pasos `n, x, p, dp, d2p, x_sig, dx` con `d2p = P''` completa.
  En el mismo ejemplo converge en menos iteraciones que Newton.
- Sturm: sucesión `P0=P`, `P1=P'`, `Pk = -resto(P_{k-2}/P_{k-1})`, limpiando
  denominadores solo con constantes positivas. El caso 1 reproduce
  `P2=5x^2-2`, `P3=18x`, `P4=2`. Si aparece un resto nulo se detecta el mcd,
  se informa `P_m = 0` y se rehace con `Q = P/mcd(P,P')`; la forma simplificada
  reproduce `Q0..Q3` del caso 2. El conteo usa `ncs(a)-ncs(b)` (ver DUDAS) y
  los extremos que son raíz lanzan `EntradaInvalida` con la tabla de signos.
  La separación subdivide con aritmética exacta y evita puntos de corte que
  sean raíz.
- Bairstow: factor `x^2 - r*x - s`, doble Horner cuadrático y sistema 2x2 de
  Newton. Si el determinante es casi nulo perturba `(r, s)`; prueba varios
  arranques y, si el Horner estándar no converge, la variante mejorada de la
  pág. 39 del apunte. Extrae las potencias de `x` antes de iterar, deflacta
  cada factor y resuelve la cuadrática final con `cmath`. El ejemplo
  `x^4 + 5x^3 + 15x^2 + 5x - 26` da `1, -2, -2 ± 3i` en 5 iteraciones con
  `eps = 1e-3`; el primer paso coincide con la pág. 35 del apunte. Las raíces
  reales se limpian con `math.isclose(imag, 0, abs_tol=1e-9)`, nunca con
  `imag == 0`.

## Resultado de las pruebas

`python -m pytest -q` → **94 tests pasan**. Incluye ejemplos del apunte,
comparaciones contra `numpy.roots` (solo en tests), raíces en 0, polinomios
con fracciones, parámetros inválidos y `NoConverge` con `.pasos`.

## Limitaciones conocidas

- Bairstow con raíces múltiples converge linealmente y la precisión de la
  raíz va como `sqrt(eps)`; con `eps` muy chico puede agotar `MAX_ITER`
  (por ejemplo `(x - 1)^4` con `eps <= 1e-8`). La variante mejorada del
  apunte ayuda, pero no elimina la singularidad del Jacobiano en el factor
  múltiple. Ver `docs/DUDAS.md`.
