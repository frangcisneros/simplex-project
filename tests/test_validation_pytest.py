"""
Pruebas para el sistema de validación de entradas del solver Simplex.
Convertido de unittest a pytest con fixtures.
"""

import pytest
import math
from simplex_solver.input_validator import InputValidator


# ==================== Fixtures ====================


@pytest.fixture
def validator():
    """Devuelve la clase InputValidator (utiliza métodos estáticos)."""
    return InputValidator


# ==================== Pruebas de Problemas Válidos ====================


def test_valid_problem(validator):
    """Un problema válido debe pasar todas las validaciones."""
    c = [3, 2, 4]
    A = [[2, 1, 1], [1, 3, 2], [1, 1, 0]]
    b = [8, 12, 4]
    constraint_types = [">=", ">=", ">="]
    maximize = False

    is_valid, message = validator.validate_problem(c, A, b, constraint_types, maximize)
    assert is_valid
    assert "válido" in message.lower() or "correcto" in message.lower()


# ==================== Pruebas de Entradas Inválidas ====================


def test_empty_objective(validator):
    """Una función objetivo vacía debe ser rechazada."""
    c = []
    A = [[1, 2]]
    b = [5]
    constraint_types = ["<="]
    maximize = True

    is_valid, message = validator.validate_problem(c, A, b, constraint_types, maximize)
    assert not is_valid
    assert "objetivo" in message.lower()


def test_nan_coefficients(validator):
    """Los coeficientes NaN deben ser rechazados."""
    c = [3, float("nan"), 2]
    A = [[1, 2, 3]]
    b = [5]
    constraint_types = ["<="]
    maximize = True

    is_valid, message = validator.validate_problem(c, A, b, constraint_types, maximize)
    assert not is_valid
    assert "finito" in message.lower()


def test_infinite_values(validator):
    """Los valores infinitos deben ser rechazados."""
    c = [3, float("inf")]
    A = [[1, 2]]
    b = [5]
    constraint_types = ["<="]
    maximize = True

    is_valid, message = validator.validate_problem(c, A, b, constraint_types, maximize)
    assert not is_valid
    assert "finito" in message.lower()


# ==================== Pruebas de Consistencia de Restricciones ====================


def test_inconsistent_constraints(validator):
    """Un número inconsistente de restricciones debe ser rechazado."""
    c = [3, 2]
    A = [[1, 2], [2, 1]]  # 2 restricciones
    b = [5]  # 1 término independiente
    constraint_types = ["<=", "<="]  # 2 tipos
    maximize = True

    is_valid, message = validator.validate_problem(c, A, b, constraint_types, maximize)
    assert not is_valid
    assert "inconsistente" in message.lower()


def test_all_zero_coefficients(validator):
    """Los coeficientes completamente nulos deben ser rechazados."""
    c = [0, 0, 0]
    A = [[1, 2, 3]]
    b = [5]
    constraint_types = ["<="]
    maximize = True

    is_valid, message = validator.validate_problem(c, A, b, constraint_types, maximize)
    assert not is_valid
    assert "cero" in message.lower()


def test_contradictory_constraints(validator):
    """Las restricciones contradictorias deben ser detectadas."""
    c = [3, 2]
    A = [[1, 1], [1, 1]]
    b = [5, 10]
    constraint_types = ["<=", ">="]  # Contradictorias: x1+x2 <=5 y x1+x2 >=10
    maximize = True

    is_valid, message = validator.validate_problem(c, A, b, constraint_types, maximize)
    assert not is_valid
    assert "contradictorias" in message.lower()


def test_infeasible_problem(validator):
    """Un problema obviamente infactible debe ser detectado."""
    c = [1, 1]
    A = [[-1, -1], [-2, -1]]
    b = [5, 8]
    constraint_types = [">=", ">="]  # -x1-x2 >=5 con x1,x2>=0 es imposible
    maximize = False

    is_valid, message = validator.validate_problem(c, A, b, constraint_types, maximize)
    assert not is_valid
    assert "infactible" in message.lower()


def test_mismatched_variables(validator):
    """Un número inconsistente de variables debe ser rechazado."""
    c = [3, 2]  # 2 variables
    A = [[1]]  # 1 coeficiente (deberían ser 2)
    b = [5]
    constraint_types = ["<="]
    maximize = True

    is_valid, message = validator.validate_problem(c, A, b, constraint_types, maximize)
    assert not is_valid
    assert "coincide" in message.lower()


def test_negative_equality_rhs(validator):
    """Las restricciones de igualdad con términos independientes negativos deben ser rechazadas."""
    c = [3, 2]
    A = [[1, 1]]
    b = [-5]  # Término independiente negativo en igualdad
    constraint_types = ["="]
    maximize = True

    is_valid, message = validator.validate_problem(c, A, b, constraint_types, maximize)
    assert not is_valid
    assert "negativo" in message.lower()


# ==================== Pruebas de Validación de Soluciones ====================


def test_solution_validation_feasible(validator):
    """Una solución factible debe pasar la validación."""
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
    """Una solución infactible debe ser detectada."""
    A = [[2, 1], [1, 2]]
    b = [8, 8]
    constraint_types = ["<=", "<="]

    solution_infeasible = {"x1": 10.0, "x2": 10.0}  # Viola restricciones
    is_feasible, errors = validator.validate_solution_feasibility(
        solution_infeasible, A, b, constraint_types
    )
    assert not is_feasible
    assert len(errors) > 0


# ==================== Pruebas Parametrizadas ====================


@pytest.mark.parametrize(
    "c,A,b,constraint_types,maximize,should_pass,expected_error_keyword",
    [
        # Casos válidos
        ([3, 2], [[1, 1]], [5], ["<="], True, True, None),
        ([1, 2, 3], [[1, 1, 1], [2, 1, 0]], [10, 5], ["<=", ">="], False, True, None),
        # Casos inválidos
        ([], [[1, 2]], [5], ["<="], True, False, "objetivo"),
        ([0, 0], [[1, 1]], [5], ["<="], True, False, "cero"),
        ([1, 2], [[1]], [5], ["<="], True, False, "coincide"),
        ([1, 2], [[1, 1]], [-5], ["="], True, False, "negativo"),
    ],
)
def test_validation_parametrized(
    validator, c, A, b, constraint_types, maximize, should_pass, expected_error_keyword
):
    """Pruebas parametrizadas para validación de problemas."""
    is_valid, message = validator.validate_problem(c, A, b, constraint_types, maximize)

    if should_pass:
        assert is_valid, f"Se esperaba válido pero se obtuvo: {message}"
    else:
        assert not is_valid, f"Se esperaba inválido pero la validación pasó"
        if expected_error_keyword:
            assert (
                expected_error_keyword in message.lower()
            ), f"Se esperaba '{expected_error_keyword}' en el mensaje de error"


# ==================== Casos Límite ====================


def test_single_variable_problem(validator):
    """Un problema con una sola variable debe ser válido."""
    c = [5]
    A = [[1]]
    b = [10]
    constraint_types = ["<="]
    maximize = True

    is_valid, message = validator.validate_problem(c, A, b, constraint_types, maximize)
    assert is_valid


def test_large_coefficients(validator):
    """Coeficientes grandes pero finitos deben ser válidos."""
    c = [1e6, 2e6]
    A = [[1e5, 2e5]]
    b = [1e7]
    constraint_types = ["<="]
    maximize = True

    is_valid, message = validator.validate_problem(c, A, b, constraint_types, maximize)
    assert is_valid


def test_very_small_coefficients(validator):
    """Coeficientes muy pequeños pero no nulos deben ser válidos."""
    c = [1e-6, 2e-6]
    A = [[1e-5, 2e-5]]
    b = [1e-4]
    constraint_types = ["<="]
    maximize = True

    is_valid, message = validator.validate_problem(c, A, b, constraint_types, maximize)
    assert is_valid
