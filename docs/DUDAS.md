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
  y `separar_raices` lanzan `EntradaInvalida` con los pasos calculados. Si el
  punto medio de una subdivisión es raíz, también se avisa: el usuario debe
  elegir otro intervalo. Es la opción conservadora para no inventar un épsilon.
- **Raíces repetidas en enteras/racionales.** `raices_enteras` y
  `raices_racionales` devuelven raíces distintas (un candidato se informa una
  sola vez), no con multiplicidad.
- **`divisores`.** Se mantiene en `metodos/raices_enteras.py` (ya estaba hecho) y
  `metodos/raices.py` lo reexporta para no duplicar lógica.
- **Error en código existente.** `Polinomio.__post_init__` recorta ceros
  modificando la lista recibida (no hace copia). No se corrige por indicación
  del AGENTS.md; se deja anotado.
