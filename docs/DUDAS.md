# Dudas y decisiones pendientes

## Ya conocidas (no resolver por cuenta propia)

1. **Halley: P'' o P''/2.** El pseudocódigo del apunte llama `HornerDoble(c, n-1, xn)`
   y usa `d2P` como si fuera `P''`; en realidad ese valor es `P''/2`. La fórmula
   escrita en el apunte usa `P''` completa. Decisión conservadora: usar `P''`
   completa (`horner3_float` ya devuelve `P''`) y guardar `d2p = P''` en los pasos.
   Confirmar con el profesor.
2. **Convención de signos de Bairstow.** El apunte usa `x^2 - r*x - s`; el TP pide
   `x^2 + p*x + q`. Decisión: el núcleo trabaja con `(r, s)` y la conversión
   `p = -r`, `q = -s` se hará en un solo lugar (GUI). Confirmar.
3. **MAX_ITER.** `core/config.py` tiene `MAX_ITER = 60`; el apunte usa 200 para
   Bairstow. Confirmar el valor con el profesor.
4. **Halley y el signo de Horner.** El pseudocódigo llama a Horner con `xn` donde
   correspondería dividir por `(x - xn)` (pasar `-xn`). Decisión: usar
   `horner3_float`, que evalúa directamente en `xn`, sin pasar por la división.

## Decisiones tomadas por ambigüedad

- **Cotas con raíces no exactas.** Lagrange y Newton pueden dar raíces k-ésimas
  irracionales. Para no perder la exactitud de `Fraction`, se calcula una cota
  racional superior conservadora con denominador 1000 (siempre ≥ el valor real).
  Es una cota válida, no necesariamente la más ajustada. Los tests comparan con
  `float` y tolerancia.
- **Separación de raíces.** Si un extremo del intervalo es raíz, `contar_raices`
  y `separar_raices` lanzan `EntradaInvalida` con los pasos calculados. Si un
  punto de subdivisión es raíz, no se avisa: se prueba otro punto interior
  (medios, cuartos, octavos, ...) hasta encontrar uno que no lo sea. Así los
  extremos de todos los subintervalos quedan siempre fuera del conjunto de
  raíces. Confirmar si el profe prefiere otro criterio.
- **Fórmula del conteo de Sturm.** El texto del apunte dice
  `nº raíces = ncs(b) - ncs(a)`, pero su tabla del caso 1 da `ncs(-2)=4` y
  `ncs(2)=0`, con lo que la fórmula correcta es `ncs(a) - ncs(b)`. Decisión:
  usar `ncs(a) - ncs(b)`, que además coincide con el teorema estándar
  (`V(a) - V(b)`). Confirmar con el profesor.
- **Escala de la sucesión de Sturm.** Para limpiar fracciones se multiplica cada
  resto por el mcm de los denominadores (constante positiva), sin dividir por
  el mcd. Así se reproducen exactamente los coeficientes del apunte
  (`P2=5x^2-2`, `P3=18x`, `P4=2`). La forma simplificada también se escala con
  constantes positivas, lo que no cambia ningún signo.
- **Raíces repetidas en enteras/racionales.** `raices_enteras` y
  `raices_racionales` devuelven raíces distintas (un candidato se informa una
  sola vez), no con multiplicidad.
- **`divisores`.** Se mantiene en `metodos/raices_enteras.py` (ya estaba hecho) y
  `metodos/raices.py` lo reexporta para no duplicar lógica.
- **Error en código existente.** `Polinomio.__post_init__` recorta ceros
  modificando la lista recibida (no hace copia). No se corrige por indicación
  del AGENTS.md; se deja anotado.
- **Fórmula de las raíces del factor de Bairstow.** El apunte (pág. 34) escribe
  `x_1,2 = (-r ± sqrt(r^2 - 4s)) / 2`, pero eso corresponde a `x^2 + r*x + s`.
  Con el factor que usa todo el método, `x^2 - r*x - s`, la fórmula correcta es
  `(r ± sqrt(r^2 + 4s)) / 2`. Decisión: usar la fórmula coherente con el
  factor; el código la implementa en `_raices_factor`. Confirmar con el
  profesor.
- **Dos variantes de Horner cuadrático en Bairstow.** El ejemplo principal
  (pág. 35) usa el Horner estándar, con `b0 = a0 + s*b2`; la mejora de la
  pág. 39 agrega `r*b1` y cambia los pasos. Decisión: intentar primero la
  variante estándar (así el ejemplo del apunte reproduce sus valores) y, si
  ningún arranque converge, probar la variante mejorada. Si el profesor pide
  una sola, se puede fijar con un parámetro o eliminar la otra.
- **Raíces en 0 en Bairstow.** Antes de iterar se extraen todas las potencias
  de `x` (una raíz 0 por cada una) y se trabaja con el polinomio restante. Así
  se evita arrancar con `s = 0`, donde el sistema de Newton queda degenerado,
  y se devuelven las raíces 0 con su multiplicidad. Si el polinomio es
  `x^k`, no se itera: se devuelven las `k` raíces 0.
- **Raíces múltiples en Bairstow.** Es una limitación numérica conocida del
  método: en un factor múltiple el Jacobiano se anula y la convergencia pasa
  a ser lineal, con error en la raíz del orden de `sqrt(eps)`. Con `eps` muy
  chico puede agotar `MAX_ITER` (por ejemplo `(x - 1)^4` con `eps <= 1e-8`);
  la variante mejorada ayuda pero no elimina el problema. No se considera un
  error de implementación. Para raíces múltiples exactas conviene usar las
  raíces enteras/racionales o Sturm. Confirmar si el profesor espera otro
  tratamiento.
- **Pasos de `NoConverge` en Bairstow.** La excepción lleva los pasos del
  último intento (el último arranque/variante probado), no los de todos los
  intentos anteriores, para no repetir filas con el mismo `factor` e `iter`.
  Si la GUI necesita ver todos los intentos, habría que agregar una clave
  extra o acumularlos con otro criterio.
