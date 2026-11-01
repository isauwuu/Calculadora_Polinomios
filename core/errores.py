class ErrorNumerico(Exception):
    """Clase base q maneja la gui"""
    def __init__(self, mensaje, pasos=None):
        super().__init__(mensaje)
        self.pasos = pasos or []  # Guarda lo que se alcanzó a calcular

class DivisionPorCero(ErrorNumerico):
    pass

class NoConverge(ErrorNumerico):
    pass

class PolinomioInvalido(ErrorNumerico):
    pass

class EntradaInvalida(ErrorNumerico):
    pass
class ToleranciaInvalida(ErrorNumerico):
    pass