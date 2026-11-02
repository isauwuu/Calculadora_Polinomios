class ErrorNumerico(Exception):
    """Clase base que maneja la GUI."""
    def __init__(self, mensaje, pasos=None):
        super().__init__(mensaje)
        self.pasos = pasos or []  # lo que se alcanzó a calcular


class DivisionPorCero(ErrorNumerico):
    pass


class NoConverge(ErrorNumerico):
    pass


class PolinomioInvalido(ErrorNumerico):
    pass


class EntradaInvalida(ErrorNumerico):
    pass


class ToleranciaInvalida(EntradaInvalida):
    pass