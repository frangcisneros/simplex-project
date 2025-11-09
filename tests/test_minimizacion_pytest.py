"""
Pruebas para problemas de MINIMIZACIÓN utilizando el método Simplex.
Contiene ejercicios con 2 y 3 variables con diferentes tipos de restricciones.
Convertido de unittest a pytest con fixtures.
"""

import pytest
from simplex_solver.solver import SimplexSolver
from simplex_solver.user_interface import UserInterface


# ==================== Pruebas de Minimización con 2 Variables ====================


def test_min_2vars_only_greater_equal(solver, ui, simple_min_problem, check_optimal):
    """Minimización con 2 variables y solo restricciones >=."""
    c = simple_min_problem["c"]
    A = simple_min_problem["A"]
    b = simple_min_problem["b"]
    constraint_types = simple_min_problem["constraint_types"]
    maximize = simple_min_problem["maximize"]

    # Mostrar el problema
    ui.display_problem(c, A, b, constraint_types, maximize)

    # Resolver el problema
    result = solver.solve(c, A, b, constraint_types, maximize)

    # Mostrar el resultado
    ui.display_result(result)

    # Verificar resultados
    check_optimal(result, ["x1", "x2"])


def test_min_2vars_with_less_equal(solver, ui, check_optimal):
    """Minimización con 2 variables y restricciones <=."""
    c = [2, 5]
    A = [[1, 2], [3, 1], [1, 0], [0, 1]]
    b = [4, 3, 5, 4]
    constraint_types = [">=", ">=", "<=", "<="]
    maximize = False

    # Mostrar el problema
    ui.display_problem(c, A, b, constraint_types, maximize)

    # Resolver el problema
    result = solver.solve(c, A, b, constraint_types, maximize)

    # Mostrar el resultado
    ui.display_result(result)

    # Verificar resultados
    check_optimal(result, ["x1", "x2"])


def test_min_2vars_with_equal(solver, ui, check_optimal):
    """Minimización con 2 variables y una restricción =."""
    c = [4, 3]
    A = [[2, 1], [1, 1], [1, 0]]
    b = [10, 6, 8]
    constraint_types = ["=", ">=", "<="]
    maximize = False

    # Mostrar el problema
    ui.display_problem(c, A, b, constraint_types, maximize)

    # Resolver el problema
    result = solver.solve(c, A, b, constraint_types, maximize)

    # Mostrar el resultado
    ui.display_result(result)

    # Verificar resultados
    check_optimal(result, ["x1", "x2"])


# ==================== Pruebas de Minimización con 3 Variables ====================


def test_min_3vars_mixed_constraints(solver, ui, check_optimal):
    """Minimización con 3 variables y restricciones mixtas."""
    c = [1, 2, 3]
    A = [[1, 1, 1], [2, 1, 1], [1, 2, 1]]
    b = [6, 10, 8]
    constraint_types = [">=", "<=", "="]
    maximize = False

    # Mostrar el problema
    ui.display_problem(c, A, b, constraint_types, maximize)

    # Resolver el problema
    result = solver.solve(c, A, b, constraint_types, maximize)

    # Mostrar el resultado
    ui.display_result(result)

    # Verificar resultados
    check_optimal(result, ["x1", "x2", "x3"])


def test_min_3vars_only_greater_equal(solver, ui, min_3vars_only_ge, check_optimal):
    """Minimización con 3 variables y solo restricciones >=."""
    c = min_3vars_only_ge["c"]
    A = min_3vars_only_ge["A"]
    b = min_3vars_only_ge["b"]
    constraint_types = min_3vars_only_ge["constraint_types"]
    maximize = min_3vars_only_ge["maximize"]

    # Mostrar el problema
    ui.display_problem(c, A, b, constraint_types, maximize)

    # Resolver el problema
    result = solver.solve(c, A, b, constraint_types, maximize)

    # Mostrar el resultado
    ui.display_result(result)

    # Verificar resultados
    check_optimal(result, ["x1", "x2", "x3"])


# ==================== Prueba con Todos los Tipos de Restricciones ====================


def test_min_2vars_all_constraint_types(solver, ui, check_optimal):
    """Minimización con 2 variables utilizando todos los tipos de restricciones."""
    c = [5, 6]
    A = [[1, 1], [2, 1], [1, 0], [0, 1]]
    b = [5, 12, 3, 2]
    constraint_types = [">=", "<=", "=", ">="]
    maximize = False

    # Mostrar el problema
    ui.display_problem(c, A, b, constraint_types, maximize)

    # Resolver el problema
    result = solver.solve(c, A, b, constraint_types, maximize)

    # Mostrar el resultado
    ui.display_result(result)

    # Verificar resultados
    check_optimal(result, ["x1", "x2"])


# ==================== Problema Clásico de Dieta ====================


def test_min_diet_problem(solver, ui, diet_problem, check_optimal):
    """Problema clásico de dieta - minimización."""
    c = diet_problem["c"]
    A = diet_problem["A"]
    b = diet_problem["b"]
    constraint_types = diet_problem["constraint_types"]
    maximize = diet_problem["maximize"]

    # Mostrar el problema
    ui.display_problem(c, A, b, constraint_types, maximize)

    # Resolver el problema
    result = solver.solve(c, A, b, constraint_types, maximize)

    # Mostrar el resultado
    ui.display_result(result)

    # Verificar resultados
    check_optimal(result, ["x1", "x2"])


# ==================== Pruebas Parametrizadas ====================


@pytest.mark.parametrize(
    "c,A,b,constraint_types,description",
    [
        (
            [3, 2],
            [[2, 1], [1, 1]],
            [6, 4],
            [">=", ">="],
            "Minimización simple con 2 variables y >=",
        ),
        (
            [2, 5],
            [[1, 2], [3, 1], [1, 0], [0, 1]],
            [4, 3, 5, 4],
            [">=", ">=", "<=", "<="],
            "Minimización con 2 variables y restricciones >= y <=",
        ),
        (
            [2, 1, 3],
            [[1, 1, 1], [2, 1, 1], [1, 2, 1]],
            [3, 4, 5],
            [">=", ">=", ">="],
            "Minimización con 3 variables y >=",
        ),
    ],
)
def test_minimization_problems_parametrized(solver, c, A, b, constraint_types, description):
    """Prueba parametrizada para varios problemas de minimización."""
    # Resolver el problema
    result = solver.solve(c, A, b, constraint_types, maximize=False)

    # Verificar resultados
    assert result["status"] == "optimal", f"Falló para: {description}"
    assert "optimal_value" in result
    # Para minimización, el valor óptimo debe ser finito
    assert result["optimal_value"] != float("inf")
