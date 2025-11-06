"""
Configuración de Pytest y fixtures compartidos para las pruebas del Simplex Solver.
"""

import pytest
from simplex_solver.solver import SimplexSolver
from simplex_solver.user_interface import UserInterface


# ==================== Fixtures para el Solver ====================


@pytest.fixture
def solver():
    """
    Crea una nueva instancia de SimplexSolver.

    Retorna:
        Una instancia de SimplexSolver.
    """
    return SimplexSolver()


@pytest.fixture
def ui():
    """
    Crea una nueva instancia de UserInterface.

    Retorna:
        Una instancia de UserInterface.
    """
    return UserInterface()


# ==================== Fixtures para Datos de Prueba ====================


@pytest.fixture
def simple_max_problem():
    """
    Problema simple de maximización con 2 variables y solo restricciones <=.

    Retorna:
        Un diccionario con los datos del problema.
    """
    return {
        "c": [3, 2],
        "A": [[2, 1], [1, 1], [1, 0]],
        "b": [100, 80, 40],
        "constraint_types": ["<=", "<=", "<="],
        "maximize": True,
    }


@pytest.fixture
def simple_min_problem():
    """
    Problema simple de minimización con 2 variables y restricciones >=.

    Retorna:
        Un diccionario con los datos del problema.
    """
    return {
        "c": [3, 2],
        "A": [[2, 1], [1, 1]],
        "b": [6, 4],
        "constraint_types": [">=", ">="],
        "maximize": False,
    }


@pytest.fixture
def max_problem_with_ge():
    """
    Problema de maximización con restricciones >= y <=.

    Retorna:
        Un diccionario con los datos del problema.
    """
    return {
        "c": [4, 3],
        "A": [[2, 1], [1, 2], [1, 0], [0, 1]],
        "b": [10, 8, 6, 5],
        "constraint_types": [">=", ">=", "<=", "<="],
        "maximize": True,
    }


@pytest.fixture
def max_problem_with_equality():
    """
    Problema de maximización con una restricción de igualdad.

    Retorna:
        Un diccionario con los datos del problema.
    """
    return {
        "c": [2, 5],
        "A": [[1, 1], [2, 1], [1, 0]],
        "b": [8, 12, 6],
        "constraint_types": ["=", "<=", "<="],
        "maximize": True,
    }


@pytest.fixture
def max_3vars_mixed():
    """
    Problema de maximización con 3 variables y tipos de restricciones mixtos.

    Retorna:
        Un diccionario con los datos del problema.
    """
    return {
        "c": [3, 2, 4],
        "A": [[1, 1, 1], [2, 1, 3], [1, 2, 1]],
        "b": [10, 6, 8],
        "constraint_types": ["<=", ">=", "="],
        "maximize": True,
    }


@pytest.fixture
def min_3vars_only_ge():
    """
    Problema de minimización con 3 variables y solo restricciones >=.

    Retorna:
        Un diccionario con los datos del problema.
    """
    return {
        "c": [2, 1, 3],
        "A": [[1, 1, 1], [2, 1, 1], [1, 2, 1]],
        "b": [3, 4, 5],
        "constraint_types": [">=", ">=", ">="],
        "maximize": False,
    }


@pytest.fixture
def diet_problem():
    """
    Problema clásico de minimización de dieta.

    Retorna:
        Un diccionario con los datos del problema.
    """
    return {
        "c": [2, 3],
        "A": [[2, 1], [1, 2], [1, 1]],
        "b": [4, 5, 6],
        "constraint_types": [">=", ">=", "="],
        "maximize": False,
    }


# ==================== Funciones Auxiliares ====================


def assert_optimal_solution(result, expected_vars=None):
    """
    Verifica que un resultado tenga estado óptimo y una solución válida.

    Args:
        result: Diccionario con el resultado del solver.
        expected_vars: Lista opcional de nombres de variables esperadas.
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
    Verifica que una solución satisface todas las restricciones.

    Args:
        result: Diccionario con el resultado del solver.
        A: Matriz de coeficientes de las restricciones.
        b: Vector del lado derecho.
        constraint_types: Lista de tipos de restricciones.
        tol: Tolerancia para comparación de punto flotante.
    """
    if result["status"] != "optimal":
        return

    solution = result["solution"]
    n_vars = len(A[0]) if A else 0

    # Extraer valores en orden
    x = []
    for i in range(1, n_vars + 1):
        var_name = f"x{i}"
        x.append(solution.get(var_name, 0.0))

    # Verificar cada restricción
    for i, (row, rhs, ctype) in enumerate(zip(A, b, constraint_types)):
        lhs = sum(coeff * val for coeff, val in zip(row, x))

        if ctype == "<=":
            assert lhs <= rhs + tol, f"Restricción {i}: {lhs} > {rhs}"
        elif ctype == ">=":
            assert lhs >= rhs - tol, f"Restricción {i}: {lhs} < {rhs}"
        elif ctype == "=":
            assert abs(lhs - rhs) <= tol, f"Restricción {i}: {lhs} != {rhs}"


# Hacer disponibles las funciones auxiliares como fixtures también
@pytest.fixture
def check_optimal():
    """
    Fixture que retorna la función assert_optimal_solution.

    Retorna:
        La función assert_optimal_solution.
    """
    return assert_optimal_solution


@pytest.fixture
def check_feasible():
    """
    Fixture que retorna la función assert_solution_feasible.

    Retorna:
        La función assert_solution_feasible.
    """
    return assert_solution_feasible
