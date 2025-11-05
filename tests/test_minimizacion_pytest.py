"""
Tests for MINIMIZATION problems using the Simplex method.
Contains exercises with 2 and 3 variables with different constraint types.
Converted from unittest to pytest with fixtures.
"""

import pytest
from simplex_solver.solver import SimplexSolver
from simplex_solver.user_interface import UserInterface


# ==================== 2-Variable Minimization Tests ====================


def test_min_2vars_only_greater_equal(solver, ui, simple_min_problem, check_optimal):
    """Minimization with 2 variables and only >= constraints."""
    c = simple_min_problem["c"]
    A = simple_min_problem["A"]
    b = simple_min_problem["b"]
    constraint_types = simple_min_problem["constraint_types"]
    maximize = simple_min_problem["maximize"]

    ui.display_problem(c, A, b, constraint_types, maximize)
    result = solver.solve(c, A, b, constraint_types, maximize)
    ui.display_result(result)

    check_optimal(result, ["x1", "x2"])


def test_min_2vars_with_less_equal(solver, ui, check_optimal):
    """Minimization with 2 variables and <= constraints."""
    c = [2, 5]
    A = [[1, 2], [3, 1], [1, 0], [0, 1]]
    b = [4, 3, 5, 4]
    constraint_types = [">=", ">=", "<=", "<="]
    maximize = False

    ui.display_problem(c, A, b, constraint_types, maximize)
    result = solver.solve(c, A, b, constraint_types, maximize)
    ui.display_result(result)

    check_optimal(result, ["x1", "x2"])


def test_min_2vars_with_equal(solver, ui, check_optimal):
    """Minimization with 2 variables and = constraint."""
    c = [4, 3]
    A = [[2, 1], [1, 1], [1, 0]]
    b = [10, 6, 8]
    constraint_types = ["=", ">=", "<="]
    maximize = False

    ui.display_problem(c, A, b, constraint_types, maximize)
    result = solver.solve(c, A, b, constraint_types, maximize)
    ui.display_result(result)

    check_optimal(result, ["x1", "x2"])


# ==================== 3-Variable Minimization Tests ====================


def test_min_3vars_mixed_constraints(solver, ui, check_optimal):
    """Minimization with 3 variables and mixed constraints."""
    c = [1, 2, 3]
    A = [[1, 1, 1], [2, 1, 1], [1, 2, 1]]
    b = [6, 10, 8]
    constraint_types = [">=", "<=", "="]
    maximize = False

    ui.display_problem(c, A, b, constraint_types, maximize)
    result = solver.solve(c, A, b, constraint_types, maximize)
    ui.display_result(result)

    check_optimal(result, ["x1", "x2", "x3"])


def test_min_3vars_only_greater_equal(solver, ui, min_3vars_only_ge, check_optimal):
    """Minimization with 3 variables and only >= constraints."""
    c = min_3vars_only_ge["c"]
    A = min_3vars_only_ge["A"]
    b = min_3vars_only_ge["b"]
    constraint_types = min_3vars_only_ge["constraint_types"]
    maximize = min_3vars_only_ge["maximize"]

    ui.display_problem(c, A, b, constraint_types, maximize)
    result = solver.solve(c, A, b, constraint_types, maximize)
    ui.display_result(result)

    check_optimal(result, ["x1", "x2", "x3"])


# ==================== All Constraint Types Test ====================


def test_min_2vars_all_constraint_types(solver, ui, check_optimal):
    """Minimization with 2 variables using all constraint types."""
    c = [5, 6]
    A = [[1, 1], [2, 1], [1, 0], [0, 1]]
    b = [5, 12, 3, 2]
    constraint_types = [">=", "<=", "=", ">="]
    maximize = False

    ui.display_problem(c, A, b, constraint_types, maximize)
    result = solver.solve(c, A, b, constraint_types, maximize)
    ui.display_result(result)

    check_optimal(result, ["x1", "x2"])


# ==================== Classic Diet Problem ====================


def test_min_diet_problem(solver, ui, diet_problem, check_optimal):
    """Classic diet problem - minimization."""
    c = diet_problem["c"]
    A = diet_problem["A"]
    b = diet_problem["b"]
    constraint_types = diet_problem["constraint_types"]
    maximize = diet_problem["maximize"]

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
            [[2, 1], [1, 1]],
            [6, 4],
            [">=", ">="],
            "Simple 2-var min with >=",
        ),
        (
            [2, 5],
            [[1, 2], [3, 1], [1, 0], [0, 1]],
            [4, 3, 5, 4],
            [">=", ">=", "<=", "<="],
            "2-var min with >= and <=",
        ),
        (
            [2, 1, 3],
            [[1, 1, 1], [2, 1, 1], [1, 2, 1]],
            [3, 4, 5],
            [">=", ">=", ">="],
            "3-var min with >=",
        ),
    ],
)
def test_minimization_problems_parametrized(solver, c, A, b, constraint_types, description):
    """Parametrized test for various minimization problems."""
    result = solver.solve(c, A, b, constraint_types, maximize=False)

    assert result["status"] == "optimal", f"Failed for: {description}"
    assert "optimal_value" in result
    # For minimization, optimal value should be finite
    assert result["optimal_value"] != float("inf")
