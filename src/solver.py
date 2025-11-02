"""
Módulo principal del algoritmo simplex.
Contiene la lógica de iteración y control del método simplex.
"""

from typing import Dict, Any, List
import numpy as np
from src.tableau import Tableau
from src.logging_system import logger


class SimplexSolver:
    """Implementa el método simplex para resolver problemas de programación lineal."""

    def __init__(self):
        self.tableau = Tableau()
        self.max_iterations = 100
        self.steps = []  # Historial de pasos para PDF

    def _solve_phase(self, maximize: bool) -> Dict[str, Any]:
        """Resuelve una fase del método simplex."""
        iteration = 0
        logger.debug(f"Iniciando fase del simplex (maximize={maximize})")

        while iteration < self.max_iterations - 1:
            iteration += 1
            print(f"\n--- Iteración {iteration} ---")
            logger.debug(f"Iteración {iteration}: Verificando optimalidad")

            # Verificar optimalidad
            is_optimal = self.tableau.is_optimal(maximize)

            if is_optimal:
                print("¡Solución óptima de la fase encontrada!")
                logger.info(f"Solución óptima encontrada en iteración {iteration}")
                return {"status": "optimal", "iterations": iteration}

            # Encontrar variable que entra
            entering_col = self.tableau.get_entering_variable(maximize)

            if entering_col == -1:
                print("No se encontró variable para entrar - solución óptima")
                logger.info("No se encontró variable para entrar - solución óptima")
                return {"status": "optimal", "iterations": iteration}

            print(f"Variable que entra: columna {entering_col + 1}")
            logger.debug(f"Variable entrante: columna {entering_col + 1}")

            # Verificar si el problema es no acotado
            if self.tableau.is_unbounded(entering_col):
                logger.warning(
                    f"Problema no acotado detectado en iteración {iteration}"
                )
                return {
                    "status": "unbounded",
                    "message": "El problema es no acotado",
                    "iterations": iteration,
                }

            # Encontrar variable que sale
            leaving_row, pivot = self.tableau.get_leaving_variable(entering_col)

            if leaving_row == -1:
                logger.error(
                    f"No se pudo encontrar variable para salir en iteración {iteration}"
                )
                return {
                    "status": "error",
                    "message": "No se pudo encontrar variable para salir",
                    "iterations": iteration,
                }

            print(f"Variable que sale: fila {leaving_row + 1}")
            print(f"Elemento pivote: {pivot:.4f}")
            logger.debug(
                f"Variable saliente: fila {leaving_row + 1}, pivote: {pivot:.4f}"
            )

            # Guardar paso para reporte PDF
            self.steps.append(
                {
                    "iteration": iteration,
                    "tableau": self.tableau.tableau.copy(),
                    "basic_vars": self.tableau.basic_vars.copy(),
                    "entering_var": entering_col,
                    "leaving_var": self.tableau.basic_vars[leaving_row],
                    "pivot_coords_next": {
                        "entering_col": entering_col,
                        "leaving_row": leaving_row,
                    },
                }
            )

            # Realizar pivoteo
            self.tableau.pivot(entering_col, leaving_row)
            logger.debug(f"Pivoteo completado: [{leaving_row}, {entering_col}]")

            print("Tableau después del pivoteo:")
            self.tableau.print_tableau()

            if iteration > 50:  # Prevenir bucles infinitos
                logger.warning(f"Demasiadas iteraciones ({iteration}), deteniendo")
                return {"status": "error", "message": "Demasiadas iteraciones"}

        logger.error(f"Máximo de iteraciones alcanzado: {self.max_iterations}")
        return {
            "status": "error",
            "message": "Demasiadas iteraciones",
            "iterations": iteration,
        }

    def solve(
        self, c: list, A: list, b: list, constraint_types: list, maximize: bool = True
    ) -> Dict[str, Any]:
        """
        Resuelve un problema de programación lineal usando el método simplex.

        Args:
            c: Coeficientes de la función objetivo
            A: Matriz de coeficientes de las restricciones
            b: Vector de términos independientes
            constraint_types: Tipos de restricciones ('<=', '>=', '=')
            maximize: True para maximizar, False para minimizar

        Returns:
            dict: Diccionario con la solución y el valor óptimo
        """
        logger.info(
            f"Iniciando solver - Variables: {len(c)}, Restricciones: {len(A)}, Tipo: {'MAX' if maximize else 'MIN'}"
        )
        self.steps.clear()  # Limpiar historial de pasos

        # Construir tableau inicial
        self.tableau.build_initial_tableau(c, A, b, constraint_types, maximize)
        logger.debug("Tableau inicial construido")

        print("Tableau inicial:")
        self.tableau.print_tableau()

        total_iterations = 0
        phase1_iterations = 0

        # Fase 1: Si hay variables artificiales
        if self.tableau.artificial_vars:
            print("\n=== FASE 1: Eliminando variables artificiales ===")
            logger.info(
                f"Iniciando Fase 1 - Variables artificiales: {len(self.tableau.artificial_vars)}"
            )
            phase1_result = self._solve_phase(maximize)
            phase1_iterations = phase1_result["iterations"]
            total_iterations += phase1_iterations

            if phase1_result["status"] != "optimal":
                logger.warning(f"Fase 1 no óptima: {phase1_result['status']}")
                return {**phase1_result, "iterations": total_iterations}

            # Verificar factibilidad
            if (
                abs(self.tableau.tableau[-1, -1]) > 1e-10
                or self.tableau.has_artificial_vars_in_basis()
            ):
                logger.warning("Problema no factible detectado en Fase 1")
                return {
                    "status": "infeasible",
                    "message": "El problema no tiene solución factible",
                    "iterations": total_iterations,
                }

            print(f"\nFase 1 completada en {phase1_iterations} iteraciones")
            logger.info(
                f"Fase 1 completada exitosamente en {phase1_iterations} iteraciones"
            )
            print(
                "Valor de la función objetivo de Fase 1:", self.tableau.tableau[-1, -1]
            )

            # Preparar Fase 2
            print("\n=== FASE 2: Optimizando función objetivo original ===")
            logger.info("Iniciando Fase 2")
            self.tableau.setup_phase2(np.array(c), maximize)
            print("Tableau inicial para Fase 2:")
            self.tableau.print_tableau()

        # Fase 2 (o única fase)
        if not self.tableau.artificial_vars:
            print("\n=== RESOLVIENDO (Fase única) ===")
            logger.info("Resolviendo en fase única (sin variables artificiales)")

        phase2_result = self._solve_phase(maximize)
        total_iterations += phase2_result["iterations"]

        if phase2_result["status"] == "optimal":
            solution, optimal_value = self.tableau.get_solution(maximize)
            logger.info(
                f"Solución óptima encontrada - Valor: {optimal_value:.6f}, Iteraciones totales: {total_iterations}"
            )

            # Guardar estado final para reporte
            self.steps.append(
                {
                    "iteration": total_iterations,
                    "tableau": self.tableau.tableau.copy(),
                    "basic_vars": self.tableau.basic_vars.copy(),
                    "entering_var": None,
                    "leaving_var": None,
                    "pivot_coords_next": None,
                }
            )

            result = {
                "status": "optimal",
                "solution": solution,
                "optimal_value": optimal_value,
                "iterations": total_iterations,
                "steps": self.steps,
                "n_original_vars": self.tableau.num_vars,
            }
            if self.tableau.artificial_vars:
                result["phase1_iterations"] = phase1_iterations
            return result
        else:
            return {**phase2_result, "iterations": total_iterations}
