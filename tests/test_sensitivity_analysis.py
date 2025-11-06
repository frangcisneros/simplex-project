"""
Tests for Sensitivity Analysis functionality.
Validates Shadow Prices, Optimality Ranges, and Feasibility Ranges.

Following TDD approach:
1. RED: This test fails because get_sensitivity_analysis() doesn't exist yet
2. GREEN: Implement the functionality
3. REFACTOR: Clean up and optimize
"""

import pytest
from simplex_solver.solver import SimplexSolver


class TestSensitivityAnalysis:
    """Test suite for sensitivity analysis after finding optimal solution."""

    def test_carpinteria_sensitivity_analysis(self):
        """
        Test sensitivity analysis for the classic carpentry problem.

        Problem (Carpintería):
        MAX Z = 80*x1 + 50*x2
        Subject to:
            4*x1 + 2*x2 <= 200  (restriccion_1: Madera)
            1*x1 + 1*x2 <= 60   (restriccion_2: Trabajo)
            x1, x2 >= 0

        Expected optimal solution:
            x1 = 40, x2 = 20, Z = 4200

        Expected Sensitivity Analysis:
        - Shadow Prices: valores duales de las restricciones
        - Optimality Ranges: rangos de variación de coeficientes de la F.O.
        - Feasibility Ranges: rangos de variación del RHS de restricciones
        """
        solver = SimplexSolver()

        # Problema de carpintería
        c = [80, 50]
        A = [[4, 2], [1, 1]]
        b = [200, 60]
        constraint_types = ["<=", "<="]
        maximize = True

        # Resolver el problema
        result = solver.solve(c, A, b, constraint_types, maximize)

        # Verificar que la solución es óptima
        assert result["status"] == "optimal"
        assert abs(result["optimal_value"] - 4200) < 1e-6
        assert abs(result["solution"]["x1"] - 40) < 1e-6
        assert abs(result["solution"]["x2"] - 20) < 1e-6

        # PASO 1 (ROJO): Llamar al método que aún no existe
        # Esto debe fallar porque get_sensitivity_analysis() no está implementado
        analysis = solver.get_sensitivity_analysis()

        # Verificar estructura del resultado
        assert "shadow_prices" in analysis
        assert "optimality_ranges" in analysis
        assert "feasibility_ranges" in analysis

        # Verificar Shadow Prices (Precios Sombra)
        # Los precios sombra son los valores de las variables duales (yi)
        # en la fila objetivo para las columnas de holgura
        shadow_prices = analysis["shadow_prices"]
        assert "restriccion_1" in shadow_prices
        assert "restriccion_2" in shadow_prices

        # Para este problema específico:
        # Shadow price restriccion_1 (madera) = 15 (cada unidad extra de madera vale $15)
        # Shadow price restriccion_2 (trabajo) = 20 (cada hora extra vale $20)
        assert abs(shadow_prices["restriccion_1"] - 15.0) < 1e-6
        assert abs(shadow_prices["restriccion_2"] - 20.0) < 1e-6

        # Verificar Optimality Ranges (Rangos de Optimalidad)
        # Cuánto puede variar cada coeficiente de la F.O. sin cambiar la base óptima
        opt_ranges = analysis["optimality_ranges"]
        assert "x1" in opt_ranges
        assert "x2" in opt_ranges

        # Cada rango debe ser una tupla (min, max)
        x1_range = opt_ranges["x1"]
        x2_range = opt_ranges["x2"]

        assert isinstance(x1_range, tuple)
        assert len(x1_range) == 2
        assert isinstance(x2_range, tuple)
        assert len(x2_range) == 2

        # Los rangos deben incluir el valor actual
        assert x1_range[0] <= 80 <= x1_range[1]
        assert x2_range[0] <= 50 <= x2_range[1]

        # Verificar Feasibility Ranges (Rangos de Factibilidad)
        # Cuánto puede variar cada RHS sin cambiar la base óptima
        feas_ranges = analysis["feasibility_ranges"]
        assert "restriccion_1" in feas_ranges
        assert "restriccion_2" in feas_ranges

        # Cada rango debe ser una tupla (min, max)
        r1_range = feas_ranges["restriccion_1"]
        r2_range = feas_ranges["restriccion_2"]

        assert isinstance(r1_range, tuple)
        assert len(r1_range) == 2
        assert isinstance(r2_range, tuple)
        assert len(r2_range) == 2

        # Los rangos deben incluir el valor actual
        assert r1_range[0] <= 200 <= r1_range[1]
        assert r2_range[0] <= 60 <= r2_range[1]

    def test_sensitivity_analysis_only_for_optimal_solution(self):
        """
        Test that sensitivity analysis is only available for optimal solutions.
        """
        solver = SimplexSolver()

        # Problema no acotado
        c = [1, 1]
        A = [[-1, 1]]
        b = [1]
        constraint_types = ["<="]
        maximize = True

        result = solver.solve(c, A, b, constraint_types, maximize)

        # Este problema es no acotado
        assert result["status"] == "unbounded"

        # Intentar obtener análisis de sensibilidad debe lanzar un error
        with pytest.raises(ValueError, match="Sensitivity analysis is only available"):
            solver.get_sensitivity_analysis()

    def test_sensitivity_minimization_problem(self):
        """
        Test sensitivity analysis for a minimization problem.

        Problem:
        MIN Z = 3*x1 + 2*x2
        Subject to:
            2*x1 + 1*x2 >= 6
            1*x1 + 1*x2 >= 4
            x1, x2 >= 0
        """
        solver = SimplexSolver()

        c = [3, 2]
        A = [[2, 1], [1, 1]]
        b = [6, 4]
        constraint_types = [">=", ">="]
        maximize = False

        result = solver.solve(c, A, b, constraint_types, maximize)

        assert result["status"] == "optimal"

        # Obtener análisis de sensibilidad
        analysis = solver.get_sensitivity_analysis()

        # Verificar estructura
        assert "shadow_prices" in analysis
        assert "optimality_ranges" in analysis
        assert "feasibility_ranges" in analysis

        # Para problemas de minimización, los precios sombra son negativos
        # o tienen interpretación diferente
        shadow_prices = analysis["shadow_prices"]
        assert "restriccion_1" in shadow_prices
        assert "restriccion_2" in shadow_prices

        # Los rangos deben existir y ser válidos
        opt_ranges = analysis["optimality_ranges"]
        assert "x1" in opt_ranges
        assert "x2" in opt_ranges

        feas_ranges = analysis["feasibility_ranges"]
        assert "restriccion_1" in feas_ranges
        assert "restriccion_2" in feas_ranges
