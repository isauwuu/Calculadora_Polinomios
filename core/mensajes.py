"""Todos los textos de error y avisos del programa, en un solo lugar."""

# --- Validación de entrada ---
POLINOMIO_VACIO        = "El polinomio está vacío."
COEF_PRINCIPAL_CERO    = "El coeficiente principal no puede ser 0."
ENTRADA_NO_NUMERO      = "'{texto}' no es un número válido. Se aceptan enteros, decimales (.) y fracciones como 3/2."
EXPONENTE_INVALIDO     = "Exponente inválido en el término '{term}'."
TERMINO_AMBIGUO        = "Término ambiguo: '{term}'."
SIN_TERMINOS           = "No se encontraron términos válidos en el polinomio."
EXP_NEGATIVO           = "Un polinomio no puede contener exponentes negativos."

# --- Tolerancia y máximo de iteraciones ---
TOLERANCIA_MAYOR_CERO  = "La tolerancia ε debe ser un número mayor a 0."
TOLERANCIA_MAQUINA     = "La tolerancia ε no puede ser menor que el épsilon de máquina (~2.2e-16)."
MAX_ITER_INVALIDO      = "El máximo de iteraciones debe ser un entero."
MAX_ITER_POSITIVO      = "El máximo de iteraciones debe ser mayor a 0."
MAX_ITER_TOPE          = "El máximo de iteraciones no puede superar {tope}."

# --- Iterativos: NO convergencia (v2: se devuelven como AVISO, no como excepción) ---
AVISO_NO_CONVERGE_ITER = "Se agotaron las {n} iteraciones sin alcanzar ε. El resultado mostrado es la última aproximación."
AVISO_CICLO            = "El método quedó atrapado en un ciclo de período {periodo} (x entre {x_min:.6g} y {x_max:.6g}). Probá otro punto inicial."
AVISO_CRECIENTE        = "El error creció durante las últimas iteraciones: el método puede estar divergiendo."
AVISO_CONV_LINEAL      = "El error baja a razón casi constante: posible raíz múltiple. Newton pierde su velocidad cuadrática."
AVISO_BAIRSTOW_DET_CERO = "En la iteración {i} del factor {factor}, el determinante se anuló. Se aplicó la perturbación (r+1, s+1) del apunte."

# --- Errores que SÍ detienen (llevan .pasos adjuntos) ---
DIVISION_POR_CERO_X    = "La derivada vale 0 en x = {x}: la tangente es horizontal y no corta el eje. Probá otro punto inicial."
NO_CONVERGE_NO_FINITO  = "El método divergió: se obtuvo un valor no finito (inf o NaN). Revisá el polinomio o el x0."
NO_CONVERGE_BAIRSTOW   = "Bairstow no logró extraer un factor cuadrático en {n} iteraciones."