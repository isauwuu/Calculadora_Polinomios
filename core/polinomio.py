from dataclasses import dataclass
from fractions import Fraction
from core.errores import PolinomioInvalido
from core.numeros import parsear_coeficientes, parsear_numero


@dataclass
class Polinomio:
    coef: list  # coef[i] acompaña a x^i (de menor a mayor grado)

    def __post_init__(self):
        """Se ejecuta automáticamente tras el __init__ de la dataclass."""
        # 1. Convertir cada coeficiente a Fraction de forma segura
        self.coef = [
            c if isinstance(c, Fraction) else parsear_numero(str(c))
            for c in self.coef
        ]

        # 2. Recortar ceros sobrantes de mayor grado (al final de la lista)
        while len(self.coef) > 1 and self.coef[-1] == 0:
            self.coef.pop()

        # 3. Validar que el polinomio no quede vacío
        if not self.coef:
            raise PolinomioInvalido("El polinomio está vacío.")

    @property
    def grado(self) -> int:
        return len(self.coef) - 1

    @classmethod
    def desde_texto(cls, texto: str):
        """Crea el polinomio parseando la entrada del usuario (de mayor a menor grado)."""
        coeficientes = parsear_coeficientes(texto)

        if not coeficientes:
            raise PolinomioInvalido("El polinomio está vacío.")

        # Los ceros a la izquierda no pueden ser el coeficiente principal.
        while coeficientes and coeficientes[0] == 0:
            coeficientes.pop(0)

        if not coeficientes:
            raise PolinomioInvalido("El coeficiente principal no puede ser 0.")

        # Invertir para que quede de menor a mayor grado internamente
        coeficientes.reverse()
        return cls(coeficientes)

    def derivada(self):
        """Calcula la derivada analítica del polinomio."""
        if self.grado == 0:
            return Polinomio([Fraction(0)])
        coef_derivada = [c * i for i, c in enumerate(self.coef)][1:]
        return Polinomio(coef_derivada)

    def a_float(self) -> list[float]:
        """Devuelve una copia de los coeficientes como float (para iterativos/gráficos)."""
        return [float(c) for c in self.coef]

    def __str__(self) -> str:
        """Representación legible del polinomio, de mayor a menor grado."""
        terminos = []

        for i in range(self.grado, -1, -1):
            c = self.coef[i]
            if c == 0 and self.grado > 0:
                continue

            # Signo: el primer término no lleva espacios ni "+"
            if i == self.grado:
                signo = "" if c >= 0 else "-"
            else:
                signo = " + " if c >= 0 else " - "

            val_abs = abs(c)
            if i == 0:
                part = str(val_abs)
            else:
                if val_abs == 1:
                    num_str = ""
                elif val_abs.denominator == 1:
                    num_str = str(val_abs)
                else:
                    num_str = f"({val_abs})"  # evita ambigüedad: (1/2)x^2
                part = f"{num_str}x" if i == 1 else f"{num_str}x^{i}"

            terminos.append(f"{signo}{part}")

        return "".join(terminos) if terminos else "0"