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
        self.coef = [parsear_numero(str(c)) if not isinstance(c, Fraction) else c for c in self.coef]

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
        coeficientes = parsear_coeficientes(texto)
        if not coeficientes:
            raise PolinomioInvalido("El polinomio está vacío.")
        coeficientes.reverse()
        return cls(coeficientes)

    def derivada(self):
        if self.grado == 0:
            return Polinomio([Fraction(0)])
        coef_derivada = [c * i for i, c in enumerate(self.coef)][1:]
        return Polinomio(coef_derivada)

    def a_float(self) -> list[float]:
        #Devuelve una copia de los coeficientes convertidos a float (para iterativos/gráficos)
        return [float(c) for c in self.coef]

    def __str__(self) -> str:
        """Representación bonita del polinomio (de mayor a menor grado para leer fácil)."""
        terminos = []
        # Recorremos de mayor a menor grado
        for i in range(self.grado, -1, -1):
            c = self.coef[i]
            if c == 0 and self.grado > 0:
                continue

            # Manejo de signos y espacios
            signo = " + " if c > 0 else " - "
            if i == self.grado:
                signo = "" if c > 0 else "-"

            val_abs = abs(c)

            # Parte numérica y literal
            if i == 0:
                part = f"{val_abs}" if val_abs != 0 or self.grado == 0 else ""
            elif i == 1:
                num_str = "" if val_abs == 1 else str(val_abs)
                part = f"{num_str}x"
            else:
                num_str = "" if val_abs == 1 else str(val_abs)
                part = f"{num_str}x^{i}"

            if part:
                terminos.append(f"{signo}{part}")

        return "".join(terminos) if terminos else "0"