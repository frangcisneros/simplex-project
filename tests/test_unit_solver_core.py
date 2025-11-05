import pytest
from unittest import mock

from simplex_solver.core.algorithm import SimplexSolver
from simplex_solver.utils.tableau import Tableau


def test_simple_optimal_solution():
    """Small maximization problem should return optimal status."""
    solver = SimplexSolver()

    c = [3, 2]
    A = [[2, 1], [1, 1], [1, 0]]
    b = [100, 80, 40]
    constraint_types = ["<=", "<=", "<="]

    result = solver.solve(c, A, b, constraint_types, maximize=True)

    assert result["status"] == "optimal"
    assert "optimal_value" in result
    assert result["optimal_value"] >= 0


def test_unbounded_detected_via_mock(monkeypatch):
    """Force an unbounded detection by patching tableau methods."""
    solver = SimplexSolver()

    # simple feasible-looking problem
    c = [1, 1]
    A = [[1, 0]]
    b = [1]
    constraint_types = ["<="]

    # Patch Tableau methods used by _solve_phase to force an unbounded result
    monkeypatch.setattr(Tableau, "is_optimal", lambda self, maximize: False)
    monkeypatch.setattr(Tableau, "get_entering_variable", lambda self, maximize: 0)
    monkeypatch.setattr(Tableau, "is_unbounded", lambda self, col: True)

    result = solver.solve(c, A, b, constraint_types, maximize=True)

    assert result["status"] == "unbounded"


def test_infeasible_detected_via_mock(monkeypatch):
    """Force infeasible detection by simulating artificial vars left in basis."""
    solver = SimplexSolver()

    # Use a constraint type that creates artificial variables
    c = [1, 1]
    A = [[1, 1]]
    b = [10]
    constraint_types = ["="]  # equality causes artificial var

    # Ensure phase1 runs: is_optimal False for phase1 and phase2
    monkeypatch.setattr(Tableau, "is_optimal", lambda self, maximize: False)
    # Simulate phase1 finishes but artificial vars remain
    monkeypatch.setattr(Tableau, "has_artificial_vars_in_basis", lambda self: True)

    result = solver.solve(c, A, b, constraint_types, maximize=True)

    assert result["status"] == "infeasible"
