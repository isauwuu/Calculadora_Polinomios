# Calculadora de Polinomios

Aplicación de escritorio para el cálculo, análisis y visualización de raíces de polinomios. Proyecto final integrador de la cátedra de Programación Numérica (UNSa, 2026).

## Ejecución rápida (Windows)

El proyecto incluye una versión compilada que no requiere tener Python instalado. Para abrirla, ejecutá el archivo ubicado en:

```text
dist/RaicesDePolinomios/RaicesDePolinomios.exe
```

## Ejecución desde el código fuente

1. Clonar el repositorio:
```bash
git clone <url-del-repositorio>
cd Calculadora_Polinomios
```

2. Instalar las dependencias necesarias:
```bash
pip install matplotlib pytest
```

3. Iniciar la aplicación:
```bash
python gui/main.py
```

4. Correr las pruebas unitarias:
```bash
pytest
```

## Funcionalidades

* **Evaluación y división:** evaluación directa, Horner simple, Horner doble/triple, división por binomios $(x \pm b)$ y $(ax \pm b)$, división cuadrática y división general euclídea.
* **Raíces exactas:** búsqueda de raíces enteras y racionales mediante el Teorema de Gauss usando aritmética fraccionaria exacta (`fractions.Fraction`).
* **Cotas:** cálculo de cotas de raíces reales por Lagrange, Laguerre y Newton.
* **Métodos iterativos:** aproximación de raíces con Newton-Raphson y Halley en punto flotante (`float64`), con tablas paso a paso y animación de convergencia.
* **Separación de raíces:** construcción de la sucesión de Sturm, detección de raíces múltiples mediante MCD y aislamiento por bisección.
* **Raíces complejas:** extracción de factores cuadráticos mediante el método de Bairstow con deflación.

## Estructura del proyecto

* `core/`: clase `Polinomio`, parseo de entradas, manejo de tolerancias, excepciones personalizadas y contenedor `Resultado`.
* `metodos/`: implementación pura de los algoritmos numéricos sin dependencias de la interfaz.
* `gui/`: interfaz gráfica desarrollada en Tkinter, controlador, gráficos con Matplotlib y animaciones.
* `tests/`: batería de pruebas unitarias.

## Equipo (TUPEROS)

* Belén Isabella Cacharani Escobar
* Ricardo Agustín Quispe
* Enzo Fabián Tejerina
* Bruno Leandro Joel Acevedo
