from core.errores import ToleranciaInvalida
# valor default
MAX_ITER = 60 #preguntar a nocera cuantas dice
EPS_DEFAULT = 1e-6 #de esta manera py representa la notacion cientifica, es equivalente a 1*10^-6

def epsilon_por_cifras(t: int) -> float:
    """Calcula epsilon (tolerancia) en función de t cifras de precisión."""
    if t <= 0:
        raise ToleranciaInvalida("Las cifras de precisión deben ser mayores a 0")

    # por arquitectura la maquina  no puede asegurar mas de 15 digitos de precision en floats, q es el tipo de dato q van a manejar los metodos iterativos (new,halley,bairstrow)
    if t > 15:
        raise ToleranciaInvalida(f"No se pueden garantizar {t} cifras. El máximo para este sistema es 15.")

    return 0.5 * (10 ** (1 - t))