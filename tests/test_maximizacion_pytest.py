"""
Pruebas para problemas de MAXIMIZACIÓN utilizando el método Simplex.
Contiene ejercicios con 2 y 3 variables con diferentes tipos de restricciones.
Convertido de unittest a pytest con fixtures.
"""

import pytest
from simplex_solver.solver import SimplexSolver
from simplex_solver.user_interface import UserInterface


# ==================== Pruebas de Maximización con 2 Variables ====================


def test_max_2vars_only_less_equal(solver, ui, simple_max_problem, check_optimal, check_feasible):
    """Maximización con 2 variables y solo restricciones <=."""
    c = simple_max_problem["c"]
    A = simple_max_problem["A"]
    b = simple_max_problem["b"]
    constraint_types = simple_max_problem["constraint_types"]
    maximize = simple_max_problem["maximize"]

    # Mostrar el problema
    ui.display_problem(c, A, b, constraint_types, maximize)

    # Resolver el problema
    result = solver.solve(c, A, b, constraint_types, maximize)

    # Mostrar el resultado
    ui.display_result(result)

    # Verificar resultados
    check_optimal(result, ["x1", "x2"])
    check_feasible(result, A, b, constraint_types)


def test_max_2vars_with_greater_equal(solver, ui, max_problem_with_ge, check_optimal):
    """Maximización con 2 variables y restricciones >=."""
    c = max_problem_with_ge["c"]
    A = max_problem_with_ge["A"]
    b = max_problem_with_ge["b"]
    constraint_types = max_problem_with_ge["constraint_types"]
    maximize = max_problem_with_ge["maximize"]

    # Mostrar el problema
    ui.display_problem(c, A, b, constraint_types, maximize)

    # Resolver el problema
    result = solver.solve(c, A, b, constraint_types, maximize)

    # Mostrar el resultado
    ui.display_result(result)

    # Verificar resultados
    check_optimal(result, ["x1", "x2"])


def test_max_2vars_with_equal(solver, ui, max_problem_with_equality, check_optimal):
    """Maximización con 2 variables y una restricción =."""
    c = max_problem_with_equality["c"]
    A = max_problem_with_equality["A"]
    b = max_problem_with_equality["b"]
    constraint_types = max_problem_with_equality["constraint_types"]
    maximize = max_problem_with_equality["maximize"]

    # Mostrar el problema
    ui.display_problem(c, A, b, constraint_types, maximize)

    # Resolver el problema
    result = solver.solve(c, A, b, constraint_types, maximize)

    # Mostrar el resultado
    ui.display_result(result)

    # Verificar resultados
    check_optimal(result, ["x1", "x2"])


# ==================== Pruebas de Maximización con 3 Variables ====================


def test_max_3vars_mixed_constraints(solver, ui, max_3vars_mixed, check_optimal):
    """Maximización con 3 variables y restricciones mixtas."""
    c = max_3vars_mixed["c"]
    A = max_3vars_mixed["A"]
    b = max_3vars_mixed["b"]
    constraint_types = max_3vars_mixed["constraint_types"]
    maximize = max_3vars_mixed["maximize"]

    # Mostrar el problema
    ui.display_problem(c, A, b, constraint_types, maximize)

    # Resolver el problema
    result = solver.solve(c, A, b, constraint_types, maximize)

    # Mostrar el resultado
    ui.display_result(result)

    # Verificar resultados
    check_optimal(result, ["x1", "x2", "x3"])


def test_max_3vars_only_less_equal(solver, ui, check_optimal):
    """Maximización con 3 variables y solo restricciones <=."""
    c = [5, 4, 3]
    A = [[2, 3, 1], [4, 1, 2], [3, 4, 2]]
    b = [5, 11, 8]
    constraint_types = ["<=", "<=", "<="]
    maximize = True

    # Mostrar el problema
    ui.display_problem(c, A, b, constraint_types, maximize)

    # Resolver el problema
    result = solver.solve(c, A, b, constraint_types, maximize)

    # Mostrar el resultado
    ui.display_result(result)

    # Verificar resultados
    check_optimal(result, ["x1", "x2", "x3"])


# ==================== Prueba con Todos los Tipos de Restricciones ====================


def test_max_2vars_all_constraint_types(solver, ui, check_optimal):
    """Maximización con 2 variables utilizando todos los tipos de restricciones."""
    c = [6, 8]
    A = [[1, 1], [2, 1], [1, 0], [0, 1]]
    b = [10, 4, 2, 8]
    constraint_types = ["<=", ">=", "=", "<="]
    maximize = True

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
            [[2, 1], [1, 1], [1, 0]],
            [100, 80, 40],
            ["<=", "<=", "<="],
            "Maximización simple con 2 variables y <=",
        ),
        (
            [4, 3],
            [[2, 1], [1, 2], [1, 0], [0, 1]],
            [10, 8, 6, 5],
            [">=", ">=", "<=", "<="],
            "Maximización con 2 variables y restricciones >= y <=",
        ),
        (
            [5, 4, 3],
            [[2, 3, 1], [4, 1, 2], [3, 4, 2]],
            [5, 11, 8],
            ["<=", "<=", "<="],
            "Maximización con 3 variables y <=",
        ),
    ],
)
def test_maximization_problems_parametrized(solver, c, A, b, constraint_types, description):
    """Prueba parametrizada para varios problemas de maximización."""
    # Resolver el problema
    result = solver.solve(c, A, b, constraint_types, maximize=True)

    # Verificar resultados
    assert result["status"] == "optimal", f"Falló para: {description}"
    assert "optimal_value" in result
    assert result["optimal_value"] >= 0
