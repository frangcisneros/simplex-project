"""
Backward compatibility wrapper for SimplexSolver.
This module maintains compatibility with existing code that imports from solver.py.
New code should import from simplex_solver.core.algorithm instead.
"""

from simplex_solver.core.algorithm import SimplexSolver

__all__ = ["SimplexSolver"]
