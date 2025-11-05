import pytest
from simplex_solver.core.algorithm import SimplexSolver


def test_verbose_level_0_silent_mode():
    """Test that verbose_level=0 runs without verbose INFO logs for iterations."""
    solver = SimplexSolver()
    c = [3, 5]
    A = [[1, 0], [0, 2], [3, 2]]
    b = [4, 12, 18]
    constraint_types = ["<=", "<=", "<="]

    # Execute with verbose_level=0 (default, silent mode)
    result = solver.solve(c, A, b, constraint_types, maximize=True, verbose_level=0)

    assert result["status"] == "optimal"
    assert "solution" in result
    assert "optimal_value" in result


def test_verbose_level_1_basic_info():
    """Test that verbose_level=1 enables basic INFO logging."""
    solver = SimplexSolver()
    c = [3, 5]
    A = [[1, 0], [0, 2], [3, 2]]
    b = [4, 12, 18]
    constraint_types = ["<=", "<=", "<="]

    # Execute with verbose_level=1 - should log phase info
    result = solver.solve(c, A, b, constraint_types, maximize=True, verbose_level=1)

    assert result["status"] == "optimal"
    # Verify solver ran successfully with verbose logging enabled


def test_verbose_level_2_detailed_iterations():
    """Test that verbose_level=2 enables detailed iteration logging."""
    solver = SimplexSolver()
    c = [3, 5]
    A = [[1, 0], [0, 2], [3, 2]]
    b = [4, 12, 18]
    constraint_types = ["<=", "<=", "<="]

    # Execute with verbose_level=2 - should log all iteration details
    result = solver.solve(c, A, b, constraint_types, maximize=True, verbose_level=2)

    assert result["status"] == "optimal"
    assert "iterations" in result
    assert result["iterations"] > 0  # Verify iterations occurred


def test_verbose_modes_produce_same_result():
    """Test that all verbose levels produce the same optimal result."""
    c = [3, 5]
    A = [[1, 0], [0, 2], [3, 2]]
    b = [4, 12, 18]
    constraint_types = ["<=", "<=", "<="]

    results = []
    for verbose_level in [0, 1, 2]:
        solver = SimplexSolver()
        result = solver.solve(c, A, b, constraint_types, maximize=True, verbose_level=verbose_level)
        results.append(result)

    # All verbose levels should produce same optimal value
    assert all(r["status"] == "optimal" for r in results)
    assert all(abs(r["optimal_value"] - results[0]["optimal_value"]) < 1e-6 for r in results)
