"""Componentes principales del algoritmo Simplex.

Este módulo sirve como punto de entrada para los elementos esenciales del algoritmo Simplex.
Proporciona acceso a la clase principal encargada de ejecutar el método Simplex.
"""

# Importa la clase principal del algoritmo Simplex desde el submódulo correspondiente.
from simplex_solver.core.algorithm import SimplexSolver

# Define explícitamente los elementos públicos del módulo para evitar exportaciones accidentales.
# Esto asegura que solo los elementos listados en __all__ estén disponibles al importar el módulo.
__all__ = ["SimplexSolver"]
