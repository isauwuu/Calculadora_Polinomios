from dataclasses import dataclass
from fractions import Fraction

from core.errores import PolinomioInvalido
from core.numeros import parsear_coeficientes

@dataclass
class Polinomio:
    coef: list  # coef[i] acompaña a x^i (de menor a mayor grado)

    @property
    def grado(self) -> int:
        return len(self.coef) - 1

    @classmethod
    def desde_texto(cls, texto: str):
        """Crea el polinomio invirtiendo la entrada del usuario."""
        coeficientes = parsear_coeficientes(texto)

        if not coeficientes:
            raise PolinomioInvalido("El polinomio está vacío.")

        # Eliminar ceros a la izquierda que escribió el usuario (que serían el mayor grado)
        while coeficientes and coeficientes[0] == 0:
            coeficientes.pop(0)

        if not coeficientes:
            raise PolinomioInvalido("El coeficiente principal no puede ser 0.")

        # Invertir la lista para que quede de menor a mayor grado
        coeficientes.reverse()
        return cls(coeficientes)

    def derivada(self):
        if self.grado == 0:
            return Polinomio([Fraction(0)])
        # Multiplica cada coef por su grado (índice i) y recorta el término independiente [1:]
        coef_derivada = [c * i for i, c in enumerate(self.coef)][1:]
        return Polinomio(coef_derivada)