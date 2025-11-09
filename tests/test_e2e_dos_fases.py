"""
Test end-to-end para el Método de Dos Fases del Simplex.
Verifica que el solver maneje correctamente problemas con restricciones >= y =.
"""

import pytest
from simplex_solver.file_parser import FileParser
from simplex_solver.core.algorithm import SimplexSolver


class TestDosFasesE2E:
    """
    Tests de integración para el Método de Dos Fases.
    """

    def test_dos_fases_basic_feasible(self):
        """
        Verifica que el Método de Dos Fases resuelve correctamente un problema factible.

        Problema:
        MIN 3x1 + 2x2 + x3
        s.a.
        2x1 + x2 + x3 >= 4
        x1 + 2x2 + x3 >= 3
        x1 + x2 + 2x3 = 5
        """
        # Parsear archivo
        c, A, b, constraint_types, maximize = FileParser.parse_file(
            "ejemplos/ejemplo_dos_fases.txt"
        )

        # Verificar parseo correcto
        assert not maximize, "Debe ser minimización"
        assert len(A) == 3, "Debe haber 3 restricciones"
        assert constraint_types.count(">=") == 2, "Debe haber 2 restricciones >="
        assert constraint_types.count("=") == 1, "Debe haber 1 restricción ="

        # Resolver con Simplex
        solver = SimplexSolver()
        result = solver.solve(c, A, b, constraint_types, maximize, verbose_level=0)

        # Verificar que encuentra solución
        assert (
            result["status"] == "optimal"
        ), f"Debe encontrar solución óptima, obtuvo: {result['status']}"

        # Verificar que tiene valor óptimo razonable
        assert "optimal_value" in result, "Debe tener valor óptimo"
        assert result["optimal_value"] is not None, "Valor óptimo no debe ser None"

        # Verificar que tiene solución
        assert "solution" in result, "Debe tener solución"
        assert result["solution"] is not None, "Solución no debe ser None"

        # Verificar que pasó por Fase 1
        assert "phase1_iterations" in result, "Debe haber información de Fase 1"
        assert result["phase1_iterations"] > 0, "Fase 1 debe ejecutar al menos 1 iteración"

        # Verificar que todas las variables son no negativas
        for var, val in result["solution"].items():
            assert val >= -1e-6, f"Variable {var} debe ser no negativa, valor: {val}"

    def test_dos_fases_verify_constraints_satisfied(self):
        """
        Verifica que la solución del Método de Dos Fases satisface todas las restricciones.
        """
        c, A, b, constraint_types, maximize = FileParser.parse_file(
            "ejemplos/ejemplo_dos_fases.txt"
        )

        solver = SimplexSolver()
        result = solver.solve(c, A, b, constraint_types, maximize, verbose_level=0)

        assert result["status"] == "optimal", "Debe encontrar solución óptima"

        # Extraer valores de variables
        solution = result["solution"]
        x_values = [solution.get(f"x{i+1}", 0.0) for i in range(len(c))]

        # Verificar cada restricción
        for i, (row, rhs, const_type) in enumerate(zip(A, b, constraint_types)):
            lhs = sum(coef * val for coef, val in zip(row, x_values))

            if const_type == ">=":
                assert (
                    lhs >= rhs - 1e-6
                ), f"Restricción {i+1} ({const_type}): {lhs:.4f} no satisface >= {rhs}"
            elif const_type == "=":
                assert (
                    abs(lhs - rhs) < 1e-6
                ), f"Restricción {i+1} ({const_type}): {lhs:.4f} no satisface = {rhs}"
            elif const_type == "<=":
                assert (
                    lhs <= rhs + 1e-6
                ), f"Restricción {i+1} ({const_type}): {lhs:.4f} no satisface <= {rhs}"

    def test_dos_fases_with_minimization_problem(self):
        """
        Verifica que el Método de Dos Fases funciona correctamente con problemas de minimización.
        """
        c, A, b, constraint_types, maximize = FileParser.parse_file(
            "ejemplos/ejemplo_minimizacion.txt"
        )

        solver = SimplexSolver()
        result = solver.solve(c, A, b, constraint_types, maximize, verbose_level=0)

        # Este problema debería resolverse exitosamente
        assert result["status"] == "optimal", "Debe encontrar solución óptima"
        assert result["optimal_value"] >= 0, "Valor óptimo debe ser no negativo"

    def test_dos_fases_iteration_count(self):
        """
        Verifica que el contador de iteraciones funciona correctamente en el Método de Dos Fases.
        """
        c, A, b, constraint_types, maximize = FileParser.parse_file(
            "ejemplos/ejemplo_dos_fases.txt"
        )

        solver = SimplexSolver()
        result = solver.solve(c, A, b, constraint_types, maximize, verbose_level=0)

        assert result["status"] == "optimal", "Debe encontrar solución óptima"

        # Verificar iteraciones
        assert "iterations" in result, "Debe tener contador de iteraciones"
        assert result["iterations"] > 0, "Debe haber al menos 1 iteración"

        # Si hay Fase 1, verificar su contador
        if "phase1_iterations" in result:
            total_iterations = result["iterations"]
            phase1_iterations = result["phase1_iterations"]
            assert (
                phase1_iterations <= total_iterations
            ), "Iteraciones de Fase 1 no pueden exceder total"

    def test_dos_fases_with_verbose_output(self):
        """
        Verifica que el solver funciona correctamente con diferentes niveles de verbosidad.
        """
        c, A, b, constraint_types, maximize = FileParser.parse_file(
            "ejemplos/ejemplo_dos_fases.txt"
        )

        # Probar con cada nivel de verbosidad
        for verbose_level in [0, 1, 2]:
            solver = SimplexSolver()
            result = solver.solve(c, A, b, constraint_types, maximize, verbose_level=verbose_level)

            assert result["status"] == "optimal", f"Debe resolver en verbose_level={verbose_level}"
            # El resultado debe ser consistente independientemente del nivel de verbosidad
            assert result["optimal_value"] is not None, "Debe tener valor óptimo"

    def test_dos_fases_solution_format(self):
        """
        Verifica que el formato de la solución generada sea correcto.
        """
        c, A, b, constraint_types, maximize = FileParser.parse_file(
            "ejemplos/ejemplo_dos_fases.txt"
        )

        solver = SimplexSolver()
        result = solver.solve(c, A, b, constraint_types, maximize, verbose_level=0)

        assert result["status"] == "optimal", "Debe encontrar solución óptima"

        # Verificar estructura de la solución
        solution = result["solution"]
        assert isinstance(solution, dict), "Solución debe ser un diccionario"

        # Verificar que tiene exactamente el número correcto de variables
        num_original_vars = len(c)
        # La solución debe tener variables x1, x2, ..., xn
        for i in range(1, num_original_vars + 1):
            var_name = f"x{i}"
            assert var_name in solution, f"Variable {var_name} debe estar en la solución"

        # Verificar que no hay variables artificiales en la solución final
        for var_name in solution.keys():
            assert var_name.startswith("x"), f"Variable {var_name} tiene formato inválido"

    def test_dos_fases_steps_recorded(self):
        """
        Verifica que se registran los pasos necesarios para la generación de reportes.
        """
        c, A, b, constraint_types, maximize = FileParser.parse_file(
            "ejemplos/ejemplo_dos_fases.txt"
        )

        solver = SimplexSolver()
        result = solver.solve(c, A, b, constraint_types, maximize, verbose_level=0)

        assert result["status"] == "optimal", "Debe encontrar solución óptima"

        # Verificar que tiene pasos registrados
        assert "steps" in result, "Debe tener pasos registrados"
        assert len(result["steps"]) > 0, "Debe haber al menos un paso registrado"

        # Verificar estructura del primer paso
        first_step = result["steps"][0]
        assert "iteration" in first_step, "Paso debe tener número de iteración"
        assert "tableau" in first_step, "Paso debe tener tableau"
        assert "basic_vars" in first_step, "Paso debe tener variables básicas"


class TestDosFasesInfeasible:
    """
    Tests para problemas infactibles utilizando el Método de Dos Fases.
    """

    def test_detects_infeasible_problem(self):
        """
        Verifica que el Método de Dos Fases detecte correctamente problemas infactibles.

        Este test utiliza un ejemplo de problema infactible y verifica que el solver
        detecte que no hay solución factible en la Fase 1.
        """
        c, A, b, constraint_types, maximize = FileParser.parse_file(
            "ejemplos/ejemplo_infactible.txt"
        )

        solver = SimplexSolver()
        result = solver.solve(c, A, b, constraint_types, maximize, verbose_level=0)

        # Debe detectar infactibilidad
        assert (
            result["status"] == "infeasible"
        ), f"Debe detectar infactibilidad, obtuvo: {result['status']}"
        assert "message" in result, "Debe incluir mensaje de error"

    def test_infeasible_no_solution_in_result(self):
        """
        Verifica que un problema infactible no devuelva solución ni valor óptimo.
        """
        c, A, b, constraint_types, maximize = FileParser.parse_file(
            "ejemplos/ejemplo_infactible.txt"
        )

        solver = SimplexSolver()
        result = solver.solve(c, A, b, constraint_types, maximize, verbose_level=0)

        assert result["status"] == "infeasible", "Debe ser infactible"
        # No debe haber solución ni valor óptimo
        assert "solution" not in result or result.get("solution") is None, "No debe tener solución"
        assert (
            "optimal_value" not in result or result.get("optimal_value") is None
        ), "No debe tener valor óptimo"
