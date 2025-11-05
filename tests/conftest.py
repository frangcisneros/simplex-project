"""
Pytest configuration and shared fixtures for Simplex Solver tests.
"""

import pytest
from simplex_solver.solver import SimplexSolver
from simplex_solver.user_interface import UserInterface


# ==================== Solver Fixtures ====================


@pytest.fixture
def solver():
    """Create a fresh SimplexSolver instance."""
    return SimplexSolver()


@pytest.fixture
def ui():
    """Create a UserInterface instance."""
    return UserInterface()


# ==================== Test Data Fixtures ====================


@pytest.fixture
def simple_max_problem():
    """Simple 2-variable maximization problem with only <= constraints."""
    return {
        "c": [3, 2],
        "A": [[2, 1], [1, 1], [1, 0]],
        "b": [100, 80, 40],
        "constraint_types": ["<=", "<=", "<="],
        "maximize": True,
    }


@pytest.fixture
def simple_min_problem():
    """Simple 2-variable minimization problem with >= constraints."""
    return {
        "c": [3, 2],
        "A": [[2, 1], [1, 1]],
        "b": [6, 4],
        "constraint_types": [">=", ">="],
        "maximize": False,
    }


@pytest.fixture
def max_problem_with_ge():
    """Maximization with >= and <= constraints."""
    return {
        "c": [4, 3],
        "A": [[2, 1], [1, 2], [1, 0], [0, 1]],
        "b": [10, 8, 6, 5],
        "constraint_types": [">=", ">=", "<=", "<="],
        "maximize": True,
    }


@pytest.fixture
def max_problem_with_equality():
    """Maximization with equality constraint."""
    return {
        "c": [2, 5],
        "A": [[1, 1], [2, 1], [1, 0]],
        "b": [8, 12, 6],
        "constraint_types": ["=", "<=", "<="],
        "maximize": True,
    }


@pytest.fixture
def max_3vars_mixed():
    """3-variable maximization with mixed constraint types."""
    return {
        "c": [3, 2, 4],
        "A": [[1, 1, 1], [2, 1, 3], [1, 2, 1]],
        "b": [10, 6, 8],
        "constraint_types": ["<=", ">=", "="],
        "maximize": True,
    }


@pytest.fixture
def min_3vars_only_ge():
    """3-variable minimization with only >= constraints."""
    return {
        "c": [2, 1, 3],
        "A": [[1, 1, 1], [2, 1, 1], [1, 2, 1]],
        "b": [3, 4, 5],
        "constraint_types": [">=", ">=", ">="],
        "maximize": False,
    }


@pytest.fixture
def diet_problem():
    """Classic diet minimization problem."""
    return {
        "c": [2, 3],
        "A": [[2, 1], [1, 2], [1, 1]],
        "b": [4, 5, 6],
        "constraint_types": [">=", ">=", "="],
        "maximize": False,
    }


# ==================== Helper Functions ====================


def assert_optimal_solution(result, expected_vars=None):
    """
    Helper to assert a result has optimal status and valid solution.

    Args:
        result: Solver result dict
        expected_vars: Optional list of expected variable names
    """
    assert result["status"] == "optimal"
    assert "optimal_value" in result
    assert "solution" in result
    assert "iterations" in result

    if expected_vars:
        for var in expected_vars:
            assert var in result["solution"]


def assert_solution_feasible(result, A, b, constraint_types, tol=1e-6):
    """
    Verify that a solution satisfies all constraints.

    Args:
        result: Solver result dict
        A: Constraint matrix
        b: RHS vector
        constraint_types: List of constraint types
        tol: Tolerance for floating point comparison
    """
    if result["status"] != "optimal":
        return

    solution = result["solution"]
    n_vars = len(A[0]) if A else 0

    # Extract values in order
    x = []
    for i in range(1, n_vars + 1):
        var_name = f"x{i}"
        x.append(solution.get(var_name, 0.0))

    # Check each constraint
    for i, (row, rhs, ctype) in enumerate(zip(A, b, constraint_types)):
        lhs = sum(coeff * val for coeff, val in zip(row, x))

        if ctype == "<=":
            assert lhs <= rhs + tol, f"Constraint {i}: {lhs} > {rhs}"
        elif ctype == ">=":
            assert lhs >= rhs - tol, f"Constraint {i}: {lhs} < {rhs}"
        elif ctype == "=":
            assert abs(lhs - rhs) <= tol, f"Constraint {i}: {lhs} != {rhs}"


# Make helpers available as fixtures too
@pytest.fixture
def check_optimal():
    """Fixture that returns the assert_optimal_solution function."""
    return assert_optimal_solution


@pytest.fixture
def check_feasible():
    """Fixture that returns the assert_solution_feasible function."""
    return assert_solution_feasible
