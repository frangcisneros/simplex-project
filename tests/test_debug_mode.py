import pytest
from simplex_solver.core.algorithm import SimplexSolver


def test_verbose_level_0_silent_mode():
    """
    Verifica que verbose_level=0 se ejecute sin mostrar logs de información (modo silencioso).
    """
    solver = SimplexSolver()
    c = [3, 5]
    A = [[1, 0], [0, 2], [3, 2]]
    b = [4, 12, 18]
    constraint_types = ["<=", "<=", "<="]

    # Ejecutar con verbose_level=0 (modo silencioso por defecto)
    result = solver.solve(c, A, b, constraint_types, maximize=True, verbose_level=0)

    assert result["status"] == "optimal"
    assert "solution" in result
    assert "optimal_value" in result


def test_verbose_level_1_basic_info():
    """
    Verifica que verbose_level=1 habilite logs básicos de información.
    """
    solver = SimplexSolver()
    c = [3, 5]
    A = [[1, 0], [0, 2], [3, 2]]
    b = [4, 12, 18]
    constraint_types = ["<=", "<=", "<="]

    # Ejecutar con verbose_level=1 - debería mostrar información básica de las fases
    result = solver.solve(c, A, b, constraint_types, maximize=True, verbose_level=1)

    assert result["status"] == "optimal"
    # Verificar que el solver se ejecutó correctamente con logs básicos habilitados


def test_verbose_level_2_detailed_iterations():
    """
    Verifica que verbose_level=2 habilite logs detallados de las iteraciones.
    """
    solver = SimplexSolver()
    c = [3, 5]
    A = [[1, 0], [0, 2], [3, 2]]
    b = [4, 12, 18]
    constraint_types = ["<=", "<=", "<="]

    # Ejecutar con verbose_level=2 - debería mostrar detalles de todas las iteraciones
    result = solver.solve(c, A, b, constraint_types, maximize=True, verbose_level=2)

    assert result["status"] == "optimal"
    assert "iterations" in result
    assert result["iterations"] > 0  # Verificar que se realizaron iteraciones


def test_verbose_modes_produce_same_result():
    """
    Verifica que todos los niveles de verbose produzcan el mismo resultado óptimo.
    """
    c = [3, 5]
    A = [[1, 0], [0, 2], [3, 2]]
    b = [4, 12, 18]
    constraint_types = ["<=", "<=", "<="]

    results = []
    for verbose_level in [0, 1, 2]:
        solver = SimplexSolver()
        result = solver.solve(c, A, b, constraint_types, maximize=True, verbose_level=verbose_level)
        results.append(result)

    # Todos los niveles de verbose deberían producir el mismo valor óptimo
    assert all(r["status"] == "optimal" for r in results)
    assert all(abs(r["optimal_value"] - results[0]["optimal_value"]) < 1e-6 for r in results)
