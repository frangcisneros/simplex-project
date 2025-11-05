"""
Tests for the input validation system of the Simplex solver.
Converted from unittest to pytest with fixtures.
"""

import pytest
import math
from simplex_solver.input_validator import InputValidator


# ==================== Fixtures ====================


@pytest.fixture
def validator():
    """Return the InputValidator class (it uses static methods)."""
    return InputValidator


# ==================== Valid Problem Tests ====================


def test_valid_problem(validator):
    """Valid problem should pass all validations."""
    c = [3, 2, 4]
    A = [[2, 1, 1], [1, 3, 2], [1, 1, 0]]
    b = [8, 12, 4]
    constraint_types = [">=", ">=", ">="]
    maximize = False

    is_valid, message = validator.validate_problem(c, A, b, constraint_types, maximize)
    assert is_valid
    assert "válido" in message.lower() or "correcto" in message.lower()


# ==================== Invalid Input Tests ====================


def test_empty_objective(validator):
    """Empty objective function should be rejected."""
    c = []
    A = [[1, 2]]
    b = [5]
    constraint_types = ["<="]
    maximize = True

    is_valid, message = validator.validate_problem(c, A, b, constraint_types, maximize)
    assert not is_valid
    assert "objetivo" in message.lower()


def test_nan_coefficients(validator):
    """NaN coefficients should be rejected."""
    c = [3, float("nan"), 2]
    A = [[1, 2, 3]]
    b = [5]
    constraint_types = ["<="]
    maximize = True

    is_valid, message = validator.validate_problem(c, A, b, constraint_types, maximize)
    assert not is_valid
    assert "finito" in message.lower()


def test_infinite_values(validator):
    """Infinite values should be rejected."""
    c = [3, float("inf")]
    A = [[1, 2]]
    b = [5]
    constraint_types = ["<="]
    maximize = True

    is_valid, message = validator.validate_problem(c, A, b, constraint_types, maximize)
    assert not is_valid
    assert "finito" in message.lower()


# ==================== Constraint Consistency Tests ====================


def test_inconsistent_constraints(validator):
    """Inconsistent number of constraints should be rejected."""
    c = [3, 2]
    A = [[1, 2], [2, 1]]  # 2 constraints
    b = [5]  # 1 RHS
    constraint_types = ["<=", "<="]  # 2 types
    maximize = True

    is_valid, message = validator.validate_problem(c, A, b, constraint_types, maximize)
    assert not is_valid
    assert "inconsistente" in message.lower()


def test_all_zero_coefficients(validator):
    """All zero coefficients should be rejected."""
    c = [0, 0, 0]
    A = [[1, 2, 3]]
    b = [5]
    constraint_types = ["<="]
    maximize = True

    is_valid, message = validator.validate_problem(c, A, b, constraint_types, maximize)
    assert not is_valid
    assert "cero" in message.lower()


def test_contradictory_constraints(validator):
    """Contradictory constraints should be detected."""
    c = [3, 2]
    A = [[1, 1], [1, 1]]
    b = [5, 10]
    constraint_types = ["<=", ">="]  # Contradictory: x1+x2 <=5 and x1+x2 >=10
    maximize = True

    is_valid, message = validator.validate_problem(c, A, b, constraint_types, maximize)
    assert not is_valid
    assert "contradictorias" in message.lower()


def test_infeasible_problem(validator):
    """Obviously infeasible problem should be detected."""
    c = [1, 1]
    A = [[-1, -1], [-2, -1]]
    b = [5, 8]
    constraint_types = [">=", ">="]  # -x1-x2 >=5 with x1,x2>=0 is impossible
    maximize = False

    is_valid, message = validator.validate_problem(c, A, b, constraint_types, maximize)
    assert not is_valid
    assert "infactible" in message.lower()


def test_mismatched_variables(validator):
    """Inconsistent number of variables should be rejected."""
    c = [3, 2]  # 2 variables
    A = [[1]]  # 1 coefficient (should be 2)
    b = [5]
    constraint_types = ["<="]
    maximize = True

    is_valid, message = validator.validate_problem(c, A, b, constraint_types, maximize)
    assert not is_valid
    assert "coincide" in message.lower()


def test_negative_equality_rhs(validator):
    """Equality constraints with negative RHS should be rejected."""
    c = [3, 2]
    A = [[1, 1]]
    b = [-5]  # Negative RHS in equality
    constraint_types = ["="]
    maximize = True

    is_valid, message = validator.validate_problem(c, A, b, constraint_types, maximize)
    assert not is_valid
    assert "negativo" in message.lower()


# ==================== Solution Validation Tests ====================


def test_solution_validation_feasible(validator):
    """Feasible solution should pass validation."""
    A = [[2, 1], [1, 2]]
    b = [8, 8]
    constraint_types = ["<=", "<="]

    solution_feasible = {"x1": 2.0, "x2": 3.0}
    is_feasible, errors = validator.validate_solution_feasibility(
        solution_feasible, A, b, constraint_types
    )
    assert is_feasible
    assert len(errors) == 0


def test_solution_validation_infeasible(validator):
    """Infeasible solution should be detected."""
    A = [[2, 1], [1, 2]]
    b = [8, 8]
    constraint_types = ["<=", "<="]

    solution_infeasible = {"x1": 10.0, "x2": 10.0}  # Violates constraints
    is_feasible, errors = validator.validate_solution_feasibility(
        solution_infeasible, A, b, constraint_types
    )
    assert not is_feasible
    assert len(errors) > 0


# ==================== Parametrized Tests ====================


@pytest.mark.parametrize(
    "c,A,b,constraint_types,maximize,should_pass,expected_error_keyword",
    [
        # Valid cases
        ([3, 2], [[1, 1]], [5], ["<="], True, True, None),
        ([1, 2, 3], [[1, 1, 1], [2, 1, 0]], [10, 5], ["<=", ">="], False, True, None),
        # Invalid cases
        ([], [[1, 2]], [5], ["<="], True, False, "objetivo"),
        ([0, 0], [[1, 1]], [5], ["<="], True, False, "cero"),
        ([1, 2], [[1]], [5], ["<="], True, False, "coincide"),
        ([1, 2], [[1, 1]], [-5], ["="], True, False, "negativo"),
    ],
)
def test_validation_parametrized(
    validator, c, A, b, constraint_types, maximize, should_pass, expected_error_keyword
):
    """Parametrized validation tests."""
    is_valid, message = validator.validate_problem(c, A, b, constraint_types, maximize)

    if should_pass:
        assert is_valid, f"Expected valid but got: {message}"
    else:
        assert not is_valid, f"Expected invalid but validation passed"
        if expected_error_keyword:
            assert (
                expected_error_keyword in message.lower()
            ), f"Expected '{expected_error_keyword}' in error message"


# ==================== Edge Cases ====================


def test_single_variable_problem(validator):
    """Single variable problem should be valid."""
    c = [5]
    A = [[1]]
    b = [10]
    constraint_types = ["<="]
    maximize = True

    is_valid, message = validator.validate_problem(c, A, b, constraint_types, maximize)
    assert is_valid


def test_large_coefficients(validator):
    """Large but finite coefficients should be valid."""
    c = [1e6, 2e6]
    A = [[1e5, 2e5]]
    b = [1e7]
    constraint_types = ["<="]
    maximize = True

    is_valid, message = validator.validate_problem(c, A, b, constraint_types, maximize)
    assert is_valid


def test_very_small_coefficients(validator):
    """Very small but non-zero coefficients should be valid."""
    c = [1e-6, 2e-6]
    A = [[1e-5, 2e-5]]
    b = [1e-4]
    constraint_types = ["<="]
    maximize = True

    is_valid, message = validator.validate_problem(c, A, b, constraint_types, maximize)
    assert is_valid
