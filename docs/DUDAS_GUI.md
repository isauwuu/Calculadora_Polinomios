# Dudas y decisiones de la interfaz

## Pestaña 2: enteras y racionales

- **Valor mostrado en la tabla.** `metodos/raices.py` evalúa el polinomio sin
  los factores `x` (`Q = P / x^m`) cuando hay raíz 0, para buscar las raíces
  distintas de 0. La tabla de la GUI muestra `P(candidato)`, no `Q(candidato)`.
  Para eso `gui/controlador.py` recalcula el valor exacto con
  `horner_fraction` sobre el polinomio original. No se modificó el núcleo.
- **Multiplicidad.** El núcleo devuelve raíces distintas. La factorización de
  la tarjeta recupera la multiplicidad dividiendo exactamente por `(x - r)`
  con `dividir_por_x_mas_b`; si el profesor prefiere mostrar solo raíces
  distintas, alcanza con cambiar `factorizar_raices`.
- **Modo Ambas.** Se muestra cada candidato una sola vez. El origen se marca
  como `entera y racional`, `entera` o `racional`; cuando el candidato viene
  del criterio de Gauss se conservan `p` y `q` para la tabla.
- **Gráfico.** Las raíces marcadas son las exactas que devuelve el núcleo.
  `numpy.roots` se usa únicamente para la línea de referencia y para la curva,
  nunca para resolver.

## Pestaña 3: cotas

- **Cotas nulas.** Cuando un método devuelve `inf = sup = 0` para un signo, la
  tabla muestra `—`: significa que no acota raíces de ese signo. La implicación
  es global, así que se muestra como `[0, B]` y `[-B, 0]` aunque no distinga el
  signo de las raíces.
- **Intervalo ajustado.** Es la intersección de Lagrange, Laguerre y Newton.
  La raíz 0 se informa aparte con un aviso porque queda fuera de las cotas de
  raíces positivas y negativas.

## Pestaña 5: Sturm

- **Tabla y subintervalos.** La tabla muestra la sucesión evaluada en `(a, b)`,
  que es la que usa el teorema. Los intervalos aislados van en la tarjeta y se
  sombrean en el gráfico; no se repite la sucesión por cada subintervalo.
- **Extremos que son raíz.** No se busca otro intervalo automáticamente: se
  muestran los pasos calculados y el aviso del núcleo para que el usuario
  elija extremos válidos.

## Pestaña 6: Bairstow

- **Formato de las raíces.** La tarjeta redondea a seis decimales y muestra
  como entero un valor que está a menos de `1e-5` de un entero; las tablas
  conservan los siete decimales del diseño. Es solo presentación: el valor
  completo sigue en `Resultado.valor`.
- **Raíces por factor.** `gui/controlador.py` anota las raíces del factor en
  la última fila de cada factor con `_raices_factor` del núcleo, para no
  duplicar la resolución de la cuadrática en la interfaz.
- **Tabla compacta.** Muestra factor, iteración, `r`, `s` y las raíces. Los
  pasos `dr` y `ds` quedan en `Resultado.pasos` y se resumen en la línea de
  error de la tarjeta: el diseño no los pide en la tabla y no entran con siete
  decimales en el ancho disponible.
