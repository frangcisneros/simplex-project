"""
Core Simplex algorithm implementation.
Contains the main SimplexSolver class following Single Responsibility Principle.
"""

from typing import Dict, Any, List
import numpy as np
from simplex_solver.utils.tableau import Tableau
from simplex_solver.logging_system import logger
from simplex_solver.config import AlgorithmConfig
from simplex_solver.core.sensitivity import SensitivityAnalyzer


class SimplexSolver:
    """
    Implementa el método Simplex para resolver problemas de programación lineal.

    Esta clase se centra únicamente en la lógica del algoritmo, delegando
    las operaciones de entrada/salida y las preocupaciones de la interfaz de usuario a otros módulos.
    """

    def __init__(self):
        """
        Inicializa el solver Simplex con configuraciones predeterminadas.
        """
        self.tableau = Tableau()
        self.max_iterations = AlgorithmConfig.MAX_ITERATIONS
        self.steps = []  # Historial de pasos para la generación de reportes en PDF
        self.verbose_level = 0  # Nivel de verbosidad para registrar iteraciones
        self._last_result = None  # Almacena el último resultado para análisis de sensibilidad
        self._original_c = None  # Coeficientes originales de la función objetivo
        self._original_b = None  # Valores originales del lado derecho de las restricciones

    def _get_basic_solution(self, maximize: bool) -> tuple:
        """
        Obtiene la solución básica del problema actual en el tableau.

        Args:
            maximize: Indica si el problema es de maximización (True) o minimización (False).

        Returns:
            tuple: Un diccionario con las variables básicas y su valor, y el valor óptimo.
        """
        try:
            sol, val = self.tableau.get_solution(maximize)
            # Asegura un orden consistente de las variables (x1, x2, ...)
            ordered = {k: sol.get(k, 0.0) for k in sorted(sol.keys(), key=lambda s: int(s[1:]))}
            return ordered, float(val)
        except Exception as e:
            # Manejo de errores para evitar interrupciones en la ejecución
            logger.debug(f"_get_basic_solution: fallo al extraer solución: {e}")
            try:
                n = self.tableau.num_vars
                fallback = {f"x{i+1}": 0.0 for i in range(n)}
                return fallback, 0.0
            except Exception:
                return {}, 0.0

    def _solve_phase(self, maximize: bool) -> Dict[str, Any]:
        """
        Resuelve una fase del método Simplex.

        Args:
            maximize: True para maximización, False para minimización.

        Returns:
            dict: Un diccionario con el estado, número de iteraciones y mensajes opcionales.
        """
        iteration = 0
        logger.debug(f"Iniciando fase del método Simplex (maximize={maximize})")

        while iteration < self.max_iterations - 1:
            iteration += 1
            logger.debug(f"Iteración {iteration}: Verificando optimalidad")

            # Verifica si la solución actual es óptima
            is_optimal = self.tableau.is_optimal(maximize)

            if is_optimal:
                logger.info(f"Solución óptima encontrada en la iteración {iteration}")

                if self.verbose_level > 0:
                    logger.info(
                        "Condición de optimalidad alcanzada: no hay coeficientes en la fila objetivo que mejoren la función"
                    )

                if self.verbose_level > 1:
                    try:
                        final_solution, final_value = self._get_basic_solution(maximize)
                        solution_str = ", ".join(
                            [f"{var}={val:.4f}" for var, val in final_solution.items()]
                        )
                        logger.info(
                            f"Solución final de la fase: {solution_str}, Valor óptimo: {final_value:.4f}"
                        )
                    except Exception as e:
                        logger.debug(f"No se pudo registrar la solución final: {e}")

                return {"status": "optimal", "iterations": iteration}

            # Encuentra la variable entrante
            entering_col = self.tableau.get_entering_variable(maximize)

            if entering_col == -1:
                logger.info("No se encontró variable entrante - solución óptima")
                return {"status": "optimal", "iterations": iteration}

            logger.debug(f"Variable entrante: columna {entering_col + 1}")
            if self.verbose_level > 1:
                logger.info(f"Variable entrante: columna {entering_col + 1}")

            # Verifica si el problema es no acotado
            if self.tableau.is_unbounded(entering_col):
                logger.warning(f"Problema no acotado detectado en la iteración {iteration}")
                return {
                    "status": "unbounded",
                    "message": "El problema es no acotado",
                    "iterations": iteration,
                }

            # Encuentra la variable saliente
            leaving_row, pivot = self.tableau.get_leaving_variable(entering_col)

            if leaving_row == -1:
                logger.error(f"No se pudo encontrar variable saliente en la iteración {iteration}")
                return {
                    "status": "error",
                    "message": "No se pudo encontrar variable saliente",
                    "iterations": iteration,
                }

            logger.debug(f"Variable saliente: fila {leaving_row + 1}, pivote: {pivot:.4f}")
            if self.verbose_level > 1:
                logger.info(f"Variable saliente: fila {leaving_row + 1}, pivote: {pivot:.4f}")

            # Almacena el paso para el reporte en PDF
            self.steps.append(
                {
                    "iteration": iteration,
                    "tableau": (
                        self.tableau.tableau.copy() if self.tableau.tableau is not None else None
                    ),
                    "basic_vars": self.tableau.basic_vars.copy(),
                    "entering_var": entering_col,
                    "leaving_var": self.tableau.basic_vars[leaving_row],
                    "pivot_coords_next": {
                        "entering_col": entering_col,
                        "leaving_row": leaving_row,
                    },
                }
            )

            # Realiza el pivoteo
            self.tableau.pivot(entering_col, leaving_row)
            logger.debug(f"Pivote completado: [{leaving_row}, {entering_col}]")

            # Registra solución intermedia si verbose_level > 1
            if self.verbose_level > 1:
                try:
                    solution_dict, current_value = self._get_basic_solution(maximize)
                    solution_str = ", ".join(
                        [f"{var}={val:.4f}" for var, val in solution_dict.items()]
                    )
                    logger.info(
                        f"Iteración {iteration} - Solución básica: {solution_str}, Valor actual: {current_value:.4f}"
                    )
                except Exception as e:
                    logger.debug(f"No se pudo registrar solución intermedia: {e}")

            if iteration > AlgorithmConfig.SAFETY_ITERATION_LIMIT:
                logger.warning(
                    f"Demasiadas iteraciones ({iteration}), deteniendo en el límite de seguridad"
                )
                return {"status": "error", "message": "Demasiadas iteraciones"}

        logger.error(f"Se alcanzó el máximo de iteraciones: {self.max_iterations}")
        return {
            "status": "error",
            "message": "Demasiadas iteraciones",
            "iterations": iteration,
        }

    def solve(
        self,
        c: list,
        A: list,
        b: list,
        constraint_types: list,
        maximize: bool = True,
        verbose_level: int = 0,
    ) -> Dict[str, Any]:
        """
        Resuelve un problema de programación lineal utilizando el método Simplex.

        Args:
            c: Coeficientes de la función objetivo.
            A: Matriz de coeficientes de las restricciones.
            b: Vector del lado derecho de las restricciones.
            constraint_types: Tipos de restricciones ('<=', '>=', '=').
            maximize: True para maximizar, False para minimizar.
            verbose_level: Nivel de verbosidad (0=silencioso, 1=información básica, 2=iteraciones detalladas).

        Returns:
            dict: Un diccionario con la solución, valor óptimo, estado y número de iteraciones.
        """
        self.verbose_level = verbose_level

        logger.info(
            f"Iniciando solver - Variables: {len(c)}, Restricciones: {len(A)}, "
            f"Tipo: {'MAX' if maximize else 'MIN'}"
        )
        self.steps.clear()  # Limpia el historial de pasos

        # Almacena los datos originales para análisis de sensibilidad
        self._original_c = np.array(c)
        self._original_b = np.array(b)
        self._maximize = maximize

        # Construye el tableau inicial
        self.tableau.build_initial_tableau(c, A, b, constraint_types, maximize)
        logger.debug("Tableau inicial construido")

        total_iterations = 0
        phase1_iterations = 0

        # Fase 1: Si hay variables artificiales
        if self.tableau.artificial_vars:
            if self.verbose_level > 0:
                logger.info(
                    f"Iniciando Fase 1 - Variables artificiales: {len(self.tableau.artificial_vars)}"
                )
            else:
                logger.debug(
                    f"Iniciando Fase 1 - Variables artificiales: {len(self.tableau.artificial_vars)}"
                )

            phase1_result = self._solve_phase(maximize)
            phase1_iterations = phase1_result["iterations"]
            total_iterations += phase1_iterations

            if phase1_result["status"] != "optimal":
                logger.warning(f"Fase 1 no óptima: {phase1_result['status']}")
                return {**phase1_result, "iterations": total_iterations}

            # Verifica factibilidad
            if (
                self.tableau.tableau is not None
                and abs(self.tableau.tableau[-1, -1]) > 1e-10
                or self.tableau.has_artificial_vars_in_basis()
            ):
                logger.warning("Problema infactible detectado en la Fase 1")
                return {
                    "status": "infeasible",
                    "message": "El problema no tiene solución factible",
                    "iterations": total_iterations,
                }

            if self.verbose_level > 0:
                logger.info(f"Fase 1 completada exitosamente en {phase1_iterations} iteraciones")
            else:
                logger.debug(f"Fase 1 completada exitosamente en {phase1_iterations} iteraciones")

            # Prepara la Fase 2
            if self.verbose_level > 0:
                logger.info("Iniciando Fase 2")
            else:
                logger.debug("Iniciando Fase 2")

            self.tableau.setup_phase2(np.array(c), maximize)

        # Fase 2 (o fase única)
        if not self.tableau.artificial_vars:
            if self.verbose_level > 0:
                logger.info("Resolviendo en una sola fase (sin variables artificiales)")
            else:
                logger.debug("Resolviendo en una sola fase (sin variables artificiales)")

        phase2_result = self._solve_phase(maximize)
        total_iterations += phase2_result["iterations"]

        if phase2_result["status"] == "optimal":
            solution, optimal_value = self.tableau.get_solution(maximize)
            logger.info(
                f"Solución óptima encontrada - Valor: {optimal_value:.6f}, "
                f"Iteraciones totales: {total_iterations}"
            )

            # Almacena el estado final para el reporte
            self.steps.append(
                {
                    "iteration": total_iterations,
                    "tableau": (
                        self.tableau.tableau.copy() if self.tableau.tableau is not None else None
                    ),
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

            # Almacena el resultado para análisis de sensibilidad
            self._last_result = result

            # Incluir análisis de sensibilidad automáticamente
            try:
                logger.info("Calculando análisis de sensibilidad...")
                sensitivity = self.get_sensitivity_analysis()
                result["sensitivity_analysis"] = sensitivity
                logger.info("Análisis de sensibilidad incluido en el resultado")
            except Exception as e:
                logger.warning(f"No se pudo calcular el análisis de sensibilidad: {e}")
                result["sensitivity_analysis"] = None

            return result
        else:
            return {**phase2_result, "iterations": total_iterations}

    def get_sensitivity_analysis(self) -> Dict[str, Any]:
        """
        Realiza un análisis de sensibilidad sobre la solución óptima.

        Este método calcula:
        - Precios sombra: Valor marginal de cada restricción.
        - Rangos de optimalidad: Rangos permitidos para los coeficientes de la función objetivo.
        - Rangos de factibilidad: Rangos permitidos para los valores del lado derecho.

        Returns:
            dict: Un diccionario que contiene precios sombra, rangos de optimalidad y rangos de factibilidad.

        Raises:
            ValueError: Si no existe una solución óptima o el solver no ha sido ejecutado.
        """
        # Valida que exista una solución óptima
        if self._last_result is None:
            raise ValueError(
                "El análisis de sensibilidad solo está disponible después de resolver un problema. "
                "Por favor, llame a solve() primero."
            )

        if self._last_result["status"] != "optimal":
            raise ValueError(
                f"El análisis de sensibilidad solo está disponible para soluciones óptimas. "
                f"Estado actual: {self._last_result['status']}"
            )

        logger.info("Realizando análisis de sensibilidad...")

        # Valida el estado interno (no debería fallar si se pasaron las validaciones anteriores)
        assert self.tableau.tableau is not None, "El tableau es None"
        assert self._original_c is not None, "Los coeficientes originales son None"
        assert self._original_b is not None, "Los valores originales son None"

        # Crea el analizador de sensibilidad
        analyzer = SensitivityAnalyzer(
            tableau=self.tableau.tableau,
            basic_vars=self.tableau.basic_vars,
            num_vars=self.tableau.num_vars,
            num_constraints=len(self._original_b),
        )

        # Realiza el análisis
        analysis = analyzer.analyze(self._original_c, self._original_b)

        logger.info("Análisis de sensibilidad completado")
        return analysis
