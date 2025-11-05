import pytest
from simplex_solver.core.algorithm import SimplexSolver


def test_verbose_complex_minimization_problem():
    """Test verbose mode with a complex minimization problem."""
    solver = SimplexSolver()

    # Problema de minimización (más complejo)
    # Min Z = 2x1 + 3x2 + x3
    # Sujeto a:
    #   x1 + x2 + x3 >= 4
    #   2x1 + x2 + 3x3 >= 6
    #   x1, x2, x3 >= 0
    c = [2, 3, 1]
    A = [[1, 1, 1], [2, 1, 3]]
    b = [4, 6]
    constraint_types = [">=", ">="]

    # Execute with verbose_level=2 to see all details
    result = solver.solve(c, A, b, constraint_types, maximize=False, verbose_level=2)

    # Verify solution is valid
    assert result["status"] == "optimal", "El solver no devolvió una solución óptima"
    assert all(
        var.startswith("x") for var in result["solution"].keys()
    ), "Las variables deben tener formato x1, x2..."
    assert "iterations" in result
    assert result["iterations"] > 0


def test_verbose_level_0_minimization():
    """Test that verbose_level=0 works with minimization problems."""
    solver = SimplexSolver()

    c = [2, 3, 1]
    A = [[1, 1, 1], [2, 1, 3]]
    b = [4, 6]
    constraint_types = [">=", ">="]

    result = solver.solve(c, A, b, constraint_types, maximize=False, verbose_level=0)

    assert result["status"] == "optimal"
    assert abs(result["optimal_value"] - 4.0) < 1e-6  # Expected optimal value


def test_two_phase_problem_with_verbose():
    """Test verbose mode with a problem requiring two-phase simplex."""
    solver = SimplexSolver()

    # Problem with >= constraints (requires Phase 1)
    c = [1, 1]
    A = [[1, 1], [2, 1]]
    b = [3, 4]
    constraint_types = [">=", ">="]

    result = solver.solve(c, A, b, constraint_types, maximize=False, verbose_level=1)

    assert result["status"] == "optimal"
    assert "phase1_iterations" in result  # Should have Phase 1
    assert result["phase1_iterations"] > 0
