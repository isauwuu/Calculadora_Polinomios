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

## Interfaz gráfica (2026-11-11)

Ramas: `feat/gui-base`, `feat/gui-newton`, `feat/gui-p1`, ... (sin push ni
merge a `main`). El núcleo no se modifica.

### Completo

- Base visual: encabezado, barra de seis pestañas, tres tarjetas, tabla
  genérica, tarjeta de resultado, banner de avisos, barra de estado y DPI
  awareness en Windows.
- Controlador sin Tkinter para las seis pestañas; los métodos se importan
  dentro de cada función.
- Pestaña 4 (Newton y Halley): tabla con `P''` en Halley, filas rojas del
  diagnóstico, banner de ciclo/convergencia lineal, tarjeta con la raíz y
  gráfico con iteraciones. Probada con `x^3 - 5x - 3`, x0 = 2, eps = 1e-3
  (2.4908637 en 4 iteraciones), Halley, ciclo y derivada nula.
- Pestaña 1 (Evaluar y dividir): evaluación directa, Horner, Horner doble y
  división por `x + b`, `ax + b`, `x² + ax + b`, `ax² + bx + c` y polinomio
  general. Tabla con el esquema exacto (`Fraction`), cociente/resto en la
  tarjeta y gráfico con α y la raíz del divisor.
- Pestaña 2 (Enteras y racionales): modo Enteras/Racionales/Ambas, tabla de
  candidatos con `P(candidato)` exacto, fila verde para las raíces, tarjeta
  con las raíces y la factorización con multiplicidad, y gráfico con las
  raíces marcadas. `gui/controlador.py` deduplica los candidatos en modo
  Ambas y recalcula el valor sobre el polinomio original cuando hay raíz 0.
  Probada con `3x^4 - 11x^3 - 6x^2 + 44x - 24` (enteras y racionales), `x^3 - x`,
  `x^2 + 1`, `2x^3`, polinomios con fracciones y entradas inválidas.
- Pestaña 3 (Cotas): tabla comparativa de Lagrange, Laguerre, Newton e
  implicación con las cuatro cotas exactas; tarjeta con la intersección más
  ajustada y gráfico con las bandas de raíces positivas y negativas.
  Probada con `3x^4 - 11x^3 - 6x^2 + 44x - 24`, `x^2 + 1`, `x^3`, constante
  y entradas inválidas.
- Pestaña 5 (Sturm): sucesión estándar o simplificada, tabla con `P_i` y sus
  signos en `a` y `b`, cantidad de raíces distintas en el intervalo y lista
  de intervalos aislados; si un extremo es raíz se muestran los pasos y el
  aviso. Gráfico con el intervalo sombreado y las raíces aisladas. Probada
  con `4x^4 - 5x^2 + 1`, el ejemplo con raíz triple, `x^2 + 1`, constantes y
  extremos inválidos.

### Pendiente

- Pestaña 6 (sigue con el contenido temporal).
- Revisión visual final y `docs/DUDAS_GUI.md`.

### Pruebas de la interfaz

- `tests/test_controlador.py`: tests de las pestañas 2, 3, 5 y 6 (modos,
  deduplicación, valores exactos, multiplicidad, cotas, Sturm, Bairstow y
  entradas inválidas). Total del proyecto: **111 tests** (`python -m pytest -q`).
- Prueba funcional con Tkinter: se construyó `App`, se seleccionaron las
  pestañas 2, 3 y 5, se ejecutaron los ejemplos y se verificaron filas,
  tarjeta, estado, banner y gráfico sin errores.

