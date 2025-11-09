"""
Módulo de compatibilidad retroactiva para SimplexSolver.
Este módulo asegura la compatibilidad con el código existente que importa desde solver.py.
El nuevo código debe importar desde simplex_solver.core.algorithm.
"""

from simplex_solver.core.algorithm import SimplexSolver

__all__ = ["SimplexSolver"]
