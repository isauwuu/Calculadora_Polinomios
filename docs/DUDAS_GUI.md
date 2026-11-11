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
