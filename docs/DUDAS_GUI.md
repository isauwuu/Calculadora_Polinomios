# Dudas y decisiones de la interfaz

## Pestaña 1: tablas de Ruffini

- **Tarjeta derecha.** En la pestaña 1 no se dibuja el gráfico: la tarjeta
  derecha muestra el esquema de Ruffini/Horner y la tabla vertical del centro
  queda como detalle de los pasos del `Resultado`.
- **Widget propio.** La tabla se dibuja en un `Canvas` (`gui/ruffini.py`)
  porque `Treeview` no permite resaltar celdas sueltas ni apilar dos esquemas
  de Ruffini con la fila de productos y la de sumas. Tiene scroll vertical y
  horizontal; el ancho de cada columna se adapta al texto para no cortar
  números.
- **Orden de entrada.** Las funciones de `tabla_ruffini*` aceptan un
  `Polinomio`, el texto del usuario o una lista de coeficientes de MAYOR a
  menor grado. La inversión se hace una sola vez, al construir el `Polinomio`.
- **Animación.** El controlador común arranca en el último paso para que el
  resultado completo quede visible después de calcular; `Reiniciar` vuelve a
  la primera columna. La tabla se llena columna por columna resaltando las
  celdas de producto y suma.

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
- **Animación de la bisección.** `separar_raices` devuelve solo los intervalos
  finales, no los estados intermedios. Para animar la subdivisión se agregó
  `biseccion_sturm` en `gui/controlador.py`: usa `contar_raices` del núcleo y
  elige puntos de corte que no sean raíz, sin duplicar el algoritmo de Sturm.
  La tabla de la pestaña no se resalta porque sus filas son los polinomios de
  la sucesión, no los subintervalos de la bisección.
- **Extremos que son raíz.** No se busca otro intervalo automáticamente: se
  muestran los pasos calculados y el aviso del núcleo para que el usuario
  elija extremos válidos.

## Pestaña 6: Bairstow

- **Formato de las raíces.** La tarjeta redondea a seis decimales y muestra
  como entero un valor que está a menos de `1e-5` de un entero; las tablas
  conservan los siete decimales del diseño. Es solo presentación: el valor
  completo sigue en `Resultado.valor`.
- **Raíces por factor.** `gui/controlador.py` calcula las raíces de
  `x² − r·x − s` con `raices_del_factor` (la misma fórmula del núcleo, con
  `cmath.sqrt`) y las anota en la última fila de cada factor. En cada paso
  también guarda `raices_actuales` para animar cómo se mueven los dos rombos
  del factor actual en el plano complejo.
- **Movimiento de `(r, s)`.** No se dibuja el par en un eje aparte: se muestra
  el texto `r`/`s` de la iteración y las raíces del factor se mueven en el
  plano complejo, que es la interpretación visual directa del par. Las raíces
  finales de cada factor se revelan cuando termina su refinamiento; las que
  extrae la deflación final aparecen en el último paso.
- **Tabla compacta.** Muestra factor, iteración, `r`, `s` y las raíces. Los
  pasos `dr` y `ds` quedan en `Resultado.pasos` y se resumen en la línea de
  error de la tarjeta: el diseño no los pide en la tabla y no entran con siete
  decimales en el ancho disponible.

## Animaciones y gráficos

- **Controlador común.** `gui/animacion.py` concentra índice, play/pausa,
  anterior/siguiente, reiniciar y velocidad (lento/normal/rápido). Usa solo
  `after()`; al cambiar de pestaña, limpiar o recalcular se cancela el `after`
  pendiente.
- **Zoom, paneo y hover.** Se agregaron a `gui/graficos.py` con la rueda del
  mouse, arrastre y el botón `Restablecer vista`. El hover muestra `x` y
  `P(x)` sobre la curva y el dato del punto bajo el mouse. En Bairstow se
  elige la anotación del eje real o del plano complejo según dónde esté el
  cursor.
- **Clic en el gráfico (Newton/Halley).** Solo completa el campo `x0`; no
  dispara el cálculo. El usuario presiona `Calcular` para iterar.
- **Tabla y animación.** Cuando las filas de la tabla corresponden a los pasos
  (pestañas 2, 3, 4 y 6), la fila del paso activo se resalta y un clic en una
  fila salta a ese paso. En Sturm se animan las bandas de la bisección y no se
  resaltan filas porque no hay correspondencia uno a uno.
