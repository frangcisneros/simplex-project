"""
Tests for MAXIMIZATION problems using the Simplex method.
Contains exercises with 2 and 3 variables with different constraint types.
Converted from unittest to pytest with fixtures.
"""

import pytest
from simplex_solver.solver import SimplexSolver
from simplex_solver.user_interface import UserInterface


# ==================== 2-Variable Maximization Tests ====================


def test_max_2vars_only_less_equal(solver, ui, simple_max_problem, check_optimal, check_feasible):
    """Maximization with 2 variables and only <= constraints."""
    c = simple_max_problem["c"]
    A = simple_max_problem["A"]
    b = simple_max_problem["b"]
    constraint_types = simple_max_problem["constraint_types"]
    maximize = simple_max_problem["maximize"]

    # Display problem
    ui.display_problem(c, A, b, constraint_types, maximize)

    # Solve
    result = solver.solve(c, A, b, constraint_types, maximize)

    # Display result
    ui.display_result(result)

    # Verify
    check_optimal(result, ["x1", "x2"])
    check_feasible(result, A, b, constraint_types)


def test_max_2vars_with_greater_equal(solver, ui, max_problem_with_ge, check_optimal):
    """Maximization with 2 variables and >= constraints."""
    c = max_problem_with_ge["c"]
    A = max_problem_with_ge["A"]
    b = max_problem_with_ge["b"]
    constraint_types = max_problem_with_ge["constraint_types"]
    maximize = max_problem_with_ge["maximize"]

    ui.display_problem(c, A, b, constraint_types, maximize)
    result = solver.solve(c, A, b, constraint_types, maximize)
    ui.display_result(result)

    check_optimal(result, ["x1", "x2"])


def test_max_2vars_with_equal(solver, ui, max_problem_with_equality, check_optimal):
    """Maximization with 2 variables and = constraint."""
    c = max_problem_with_equality["c"]
    A = max_problem_with_equality["A"]
    b = max_problem_with_equality["b"]
    constraint_types = max_problem_with_equality["constraint_types"]
    maximize = max_problem_with_equality["maximize"]

    ui.display_problem(c, A, b, constraint_types, maximize)
    result = solver.solve(c, A, b, constraint_types, maximize)
    ui.display_result(result)

    check_optimal(result, ["x1", "x2"])


# ==================== 3-Variable Maximization Tests ====================


def test_max_3vars_mixed_constraints(solver, ui, max_3vars_mixed, check_optimal):
    """Maximization with 3 variables and mixed constraints."""
    c = max_3vars_mixed["c"]
    A = max_3vars_mixed["A"]
    b = max_3vars_mixed["b"]
    constraint_types = max_3vars_mixed["constraint_types"]
    maximize = max_3vars_mixed["maximize"]

    ui.display_problem(c, A, b, constraint_types, maximize)
    result = solver.solve(c, A, b, constraint_types, maximize)
    ui.display_result(result)

    check_optimal(result, ["x1", "x2", "x3"])


def test_max_3vars_only_less_equal(solver, ui, check_optimal):
    """Maximization with 3 variables and only <= constraints."""
    c = [5, 4, 3]
    A = [[2, 3, 1], [4, 1, 2], [3, 4, 2]]
    b = [5, 11, 8]
    constraint_types = ["<=", "<=", "<="]
    maximize = True

    ui.display_problem(c, A, b, constraint_types, maximize)
    result = solver.solve(c, A, b, constraint_types, maximize)
    ui.display_result(result)

    check_optimal(result, ["x1", "x2", "x3"])


# ==================== All Constraint Types Test ====================


def test_max_2vars_all_constraint_types(solver, ui, check_optimal):
    """Maximization with 2 variables using all constraint types."""
    c = [6, 8]
    A = [[1, 1], [2, 1], [1, 0], [0, 1]]
    b = [10, 4, 2, 8]
    constraint_types = ["<=", ">=", "=", "<="]
    maximize = True

    ui.display_problem(c, A, b, constraint_types, maximize)
    result = solver.solve(c, A, b, constraint_types, maximize)
    ui.display_result(result)

    check_optimal(result, ["x1", "x2"])


# ==================== Parametrized Tests ====================


@pytest.mark.parametrize(
    "c,A,b,constraint_types,description",
    [
        (
            [3, 2],
            [[2, 1], [1, 1], [1, 0]],
            [100, 80, 40],
            ["<=", "<=", "<="],
            "Simple 2-var max with <=",
        ),
        (
            [4, 3],
            [[2, 1], [1, 2], [1, 0], [0, 1]],
            [10, 8, 6, 5],
            [">=", ">=", "<=", "<="],
            "2-var max with >= and <=",
        ),
        (
            [5, 4, 3],
            [[2, 3, 1], [4, 1, 2], [3, 4, 2]],
            [5, 11, 8],
            ["<=", "<=", "<="],
            "3-var max with <=",
        ),
    ],
)
def test_maximization_problems_parametrized(solver, c, A, b, constraint_types, description):
    """Parametrized test for various maximization problems."""
    result = solver.solve(c, A, b, constraint_types, maximize=True)

    assert result["status"] == "optimal", f"Failed for: {description}"
    assert "optimal_value" in result
    assert result["optimal_value"] >= 0
