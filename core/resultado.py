from dataclasses import dataclass, field

@dataclass
class Resultado:
    valor: object                                   # raiz, cociente, raices (complex), sucesion
    iteraciones: int = 0
    error: float | None = None                      # almacena el valor del error de la ultima iteracion
    convergio: bool = True
    pasos: list = field(default_factory=list)       # lista de diccionarios, es la única fuente de información que alimenta simultáneamente a la tabla de la interfaz, el gráfico, la animación y el pedido al asistente de IA.
    avisos: list = field(default_factory=list)      # textos para el usuario
    diagnostico: dict = field(default_factory=dict) # lo llena diagnostico.py  Estos  ultimos campos capaz sean prescindibles, ver dsp !!