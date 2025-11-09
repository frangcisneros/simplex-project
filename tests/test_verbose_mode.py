import pytest
from simplex_solver.core.algorithm import SimplexSolver


def test_verbose_complex_minimization_problem():
    """Prueba el modo verbose con un problema complejo de minimización."""
    solver = SimplexSolver()

    # Definición del problema de minimización (más complejo):
    # Min Z = 2x1 + 3x2 + x3
    # Sujeto a:
    #   x1 + x2 + x3 >= 4
    #   2x1 + x2 + 3x3 >= 6
    #   x1, x2, x3 >= 0
    c = [2, 3, 1]
    A = [[1, 1, 1], [2, 1, 3]]
    b = [4, 6]
    constraint_types = [">=", ">="]

    # Ejecutar con verbose_level=2 para ver todos los detalles
    result = solver.solve(c, A, b, constraint_types, maximize=False, verbose_level=2)

    # Verificar que la solución sea válida
    assert result["status"] == "optimal", "El solver no devolvió una solución óptima"
    assert all(
        var.startswith("x") for var in result["solution"].keys()
    ), "Las variables deben tener formato x1, x2..."
    assert "iterations" in result
    assert result["iterations"] > 0


def test_verbose_level_0_minimization():
    """Prueba que verbose_level=0 funcione con problemas de minimización."""
    solver = SimplexSolver()

    # Definición del problema de minimización
    c = [2, 3, 1]
    A = [[1, 1, 1], [2, 1, 3]]
    b = [4, 6]
    constraint_types = [">=", ">="]

    # Resolver el problema con verbose_level=0
    result = solver.solve(c, A, b, constraint_types, maximize=False, verbose_level=0)

    # Verificar que el resultado sea óptimo y el valor esperado
    assert result["status"] == "optimal"
    assert abs(result["optimal_value"] - 4.0) < 1e-6  # Valor óptimo esperado


def test_two_phase_problem_with_verbose():
    """Prueba el modo verbose con un problema que requiere el método simplex en dos fases."""
    solver = SimplexSolver()

    # Problema con restricciones >= (requiere Fase 1 del método simplex)
    c = [1, 1]
    A = [[1, 1], [2, 1]]
    b = [3, 4]
    constraint_types = [">=", ">="]

    # Resolver el problema con verbose_level=1
    result = solver.solve(c, A, b, constraint_types, maximize=False, verbose_level=1)

    # Verificar que el resultado sea óptimo y que se haya ejecutado la Fase 1
    assert result["status"] == "optimal"
    assert "phase1_iterations" in result  # Debe incluir iteraciones de la Fase 1
    assert result["phase1_iterations"] > 0
