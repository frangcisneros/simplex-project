import pytest
from unittest import mock

from simplex_solver.core.algorithm import SimplexSolver
from simplex_solver.utils.tableau import Tableau


def test_simple_optimal_solution():
    """Prueba un problema pequeño de maximización que debería devolver un estado óptimo."""
    solver = SimplexSolver()

    c = [3, 2]
    A = [[2, 1], [1, 1], [1, 0]]
    b = [100, 80, 40]
    constraint_types = ["<=", "<=", "<="]

    result = solver.solve(c, A, b, constraint_types, maximize=True)

    # Verificar que el resultado es óptimo
    assert result["status"] == "optimal"
    assert "optimal_value" in result
    assert result["optimal_value"] >= 0


def test_unbounded_detected_via_mock(monkeypatch):
    """Fuerza la detección de un problema no acotado mediante el parcheo de métodos de Tableau."""
    solver = SimplexSolver()

    # Problema simple que parece factible
    c = [1, 1]
    A = [[1, 0]]
    b = [1]
    constraint_types = ["<="]

    # Parchear métodos de Tableau utilizados por _solve_phase para forzar un resultado no acotado
    monkeypatch.setattr(Tableau, "is_optimal", lambda self, maximize: False)
    monkeypatch.setattr(Tableau, "get_entering_variable", lambda self, maximize: 0)
    monkeypatch.setattr(Tableau, "is_unbounded", lambda self, col: True)

    result = solver.solve(c, A, b, constraint_types, maximize=True)

    # Verificar que el estado detectado es "unbounded"
    assert result["status"] == "unbounded"


def test_infeasible_detected_via_mock(monkeypatch):
    """Fuerza la detección de un problema infactible simulando variables artificiales en la base."""
    solver = SimplexSolver()

    # Usar un tipo de restricción que crea variables artificiales
    c = [1, 1]
    A = [[1, 1]]
    b = [10]
    constraint_types = ["="]  # La igualdad causa variables artificiales

    # Asegurar que phase1 se ejecute: is_optimal False para phase1 y phase2
    monkeypatch.setattr(Tableau, "is_optimal", lambda self, maximize: False)
    # Simular que phase1 termina pero las variables artificiales permanecen
    monkeypatch.setattr(Tableau, "has_artificial_vars_in_basis", lambda self: True)

    result = solver.solve(c, A, b, constraint_types, maximize=True)

    # Verificar que el estado detectado es "infeasible"
    assert result["status"] == "infeasible"
