"""
Pruebas para la funcionalidad de Análisis de Sensibilidad.
Valida Precios Sombra, Rangos de Optimalidad y Rangos de Factibilidad.

Enfoque TDD:
1. ROJO: Esta prueba falla porque get_sensitivity_analysis() aún no existe.
2. VERDE: Implementar la funcionalidad.
3. REFACTORIZAR: Limpiar y optimizar.
"""

import pytest
from simplex_solver.solver import SimplexSolver


class TestSensitivityAnalysis:
    """Suite de pruebas para el análisis de sensibilidad después de encontrar la solución óptima."""

    def test_carpinteria_sensitivity_analysis(self):
        """
        Prueba de análisis de sensibilidad para el problema clásico de carpintería.

        Problema (Carpintería):
        MAX Z = 80*x1 + 50*x2
        Sujeto a:
            4*x1 + 2*x2 <= 200  (restriccion_1: Madera)
            1*x1 + 1*x2 <= 60   (restriccion_2: Trabajo)
            x1, x2 >= 0

        Solución óptima esperada:
            x1 = 40, x2 = 20, Z = 4200

        Análisis de Sensibilidad esperado:
        - Precios Sombra: valores duales de las restricciones
        - Rangos de Optimalidad: rangos de variación de coeficientes de la F.O.
        - Rangos de Factibilidad: rangos de variación del RHS de restricciones
        """
        solver = SimplexSolver()

        # Definición del problema de carpintería
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

        # Verificar Precios Sombra
        shadow_prices = analysis["shadow_prices"]
        assert "restriccion_1" in shadow_prices
        assert "restriccion_2" in shadow_prices

        # Valores esperados para este problema
        assert abs(shadow_prices["restriccion_1"] - 15.0) < 1e-6
        assert abs(shadow_prices["restriccion_2"] - 20.0) < 1e-6

        # Verificar Rangos de Optimalidad
        opt_ranges = analysis["optimality_ranges"]
        assert "x1" in opt_ranges
        assert "x2" in opt_ranges

        x1_range = opt_ranges["x1"]
        x2_range = opt_ranges["x2"]

        assert isinstance(x1_range, tuple)
        assert len(x1_range) == 2
        assert isinstance(x2_range, tuple)
        assert len(x2_range) == 2

        assert x1_range[0] <= 80 <= x1_range[1]
        assert x2_range[0] <= 50 <= x2_range[1]

        # Verificar Rangos de Factibilidad
        feas_ranges = analysis["feasibility_ranges"]
        assert "restriccion_1" in feas_ranges
        assert "restriccion_2" in feas_ranges

        r1_range = feas_ranges["restriccion_1"]
        r2_range = feas_ranges["restriccion_2"]

        assert isinstance(r1_range, tuple)
        assert len(r1_range) == 2
        assert isinstance(r2_range, tuple)
        assert len(r2_range) == 2

        assert r1_range[0] <= 200 <= r1_range[1]
        assert r2_range[0] <= 60 <= r2_range[1]

    def test_sensitivity_analysis_only_for_optimal_solution(self):
        """
        Prueba que el análisis de sensibilidad solo esté disponible para soluciones óptimas.
        """
        solver = SimplexSolver()

        # Definición de un problema no acotado
        c = [1, 1]
        A = [[-1, 1]]
        b = [1]
        constraint_types = ["<="]
        maximize = True

        result = solver.solve(c, A, b, constraint_types, maximize)

        # Verificar que el problema es no acotado
        assert result["status"] == "unbounded"

        # Intentar obtener análisis de sensibilidad debe lanzar un error
        # Como el resultado no es óptimo, _last_result no se guarda, por lo que será None
        with pytest.raises(
            ValueError,
            match="El análisis de sensibilidad solo está disponible después de resolver un problema",
        ):
            solver.get_sensitivity_analysis()

    def test_sensitivity_minimization_problem(self):
        """
        Prueba de análisis de sensibilidad para un problema de minimización.

        Problema:
        MIN Z = 3*x1 + 2*x2
        Sujeto a:
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

        # Verificar estructura del análisis
        assert "shadow_prices" in analysis
        assert "optimality_ranges" in analysis
        assert "feasibility_ranges" in analysis

        # Verificar Precios Sombra
        shadow_prices = analysis["shadow_prices"]
        assert "restriccion_1" in shadow_prices
        assert "restriccion_2" in shadow_prices

        # Verificar Rangos de Factibilidad
        feas_ranges = analysis["feasibility_ranges"]
        assert "restriccion_1" in feas_ranges
        assert "restriccion_2" in feas_ranges

    def test_sensitivity_included_in_result(self):
        """
        Prueba que el análisis de sensibilidad se incluya automáticamente en el resultado.
        """
        solver = SimplexSolver()

        # Definición del problema de carpintería
        c = [80, 50]
        A = [[4, 2], [1, 1]]
        b = [200, 60]
        constraint_types = ["<=", "<="]
        maximize = True

        # Resolver el problema
        result = solver.solve(c, A, b, constraint_types, maximize)

        # Verificar que la solución es óptima
        assert result["status"] == "optimal"

        # Verificar que el análisis de sensibilidad está incluido en el resultado
        assert "sensitivity_analysis" in result
        assert result["sensitivity_analysis"] is not None

        # Verificar que tiene la estructura correcta
        analysis = result["sensitivity_analysis"]
        assert "shadow_prices" in analysis
        assert "optimality_ranges" in analysis
        assert "feasibility_ranges" in analysis

        # Verificar algunos valores
        assert "restriccion_1" in analysis["shadow_prices"]
        assert "restriccion_2" in analysis["shadow_prices"]
        assert abs(analysis["shadow_prices"]["restriccion_1"] - 15.0) < 1e-6
        assert abs(analysis["shadow_prices"]["restriccion_2"] - 20.0) < 1e-6
