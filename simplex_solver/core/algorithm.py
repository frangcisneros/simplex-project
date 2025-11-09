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
        self._find_alternative_solutions = True  # Flag para buscar soluciones alternativas

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

            # Buscar soluciones alternativas
            alternative_solutions = []
            if self._find_alternative_solutions:
                logger.info("Buscando soluciones alternativas óptimas...")
                alternative_solutions = self._find_alternative_optimal_solutions(
                    maximize, solution, optimal_value, total_iterations
                )

            # Construir lista de soluciones (primera + alternativas)
            all_solutions = [solution]
            if alternative_solutions:
                all_solutions.extend(alternative_solutions)
                logger.info(
                    f"Se encontraron {len(alternative_solutions)} soluciones alternativas óptimas"
                )

            result = {
                "status": "optimal",
                "solution": solution,  # Mantener compatibilidad hacia atrás
                "solutions": all_solutions,  # Nueva estructura: lista de todas las soluciones
                "optimal_value": optimal_value,
                "iterations": total_iterations,
                "steps": self.steps,
                "n_original_vars": self.tableau.num_vars,
                "has_alternative_solutions": len(alternative_solutions) > 0,
                "num_alternative_solutions": len(alternative_solutions),
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

    def _find_alternative_optimal_solutions(
        self,
        maximize: bool,
        first_solution: Dict[str, float],
        optimal_value: float,
        current_iterations: int,
    ) -> List[Dict[str, float]]:
        """
        Encuentra soluciones alternativas óptimas pivoteando sobre variables no básicas
        con costo reducido cero.

        El método funciona de la siguiente manera:
        1. Identifica todas las variables no básicas con costo reducido cero
        2. Para cada una, guarda el estado actual del tableau
        3. Realiza un pivoteo con esa variable como entrante
        4. Extrae la nueva solución básica (que tendrá el mismo valor objetivo)
        5. Restaura el tableau al estado original para probar la siguiente variable

        Args:
            maximize: True para maximización, False para minimización.
            first_solution: La primera solución óptima encontrada.
            optimal_value: El valor objetivo óptimo.
            current_iterations: Número actual de iteraciones (para logging).

        Returns:
            Lista de diccionarios, cada uno representando una solución alternativa óptima.
            La lista está vacía si no hay soluciones alternativas.

        Note:
            Este método preserva el estado del tableau, restaurándolo después de
            explorar cada alternativa.
        """
        alternative_solutions = []

        # Verificar que el tableau esté inicializado
        if self.tableau.tableau is None:
            logger.warning("Tableau no inicializado, no se pueden buscar soluciones alternativas")
            return alternative_solutions

        # Identificar variables no básicas con costo reducido cero
        zero_cost_vars = self.tableau.get_non_basic_zero_reduced_cost_vars(maximize)

        if not zero_cost_vars:
            logger.debug("No se encontraron variables no básicas con costo reducido cero")
            return alternative_solutions

        logger.info(
            f"Encontradas {len(zero_cost_vars)} variables candidatas para soluciones alternativas"
        )

        # Guardar el estado original del tableau
        original_tableau = self.tableau.tableau.copy()
        original_basic_vars = self.tableau.basic_vars.copy()

        for entering_col in zero_cost_vars:
            try:
                # Restaurar tableau al estado óptimo original antes de cada pivoteo
                self.tableau.tableau = original_tableau.copy()
                self.tableau.basic_vars = original_basic_vars.copy()

                logger.debug(
                    f"Explorando solución alternativa con variable entrante: columna {entering_col}"
                )

                # Verificar si el pivoteo es posible (no unbounded)
                if self.tableau.is_unbounded(entering_col):
                    logger.debug(f"Variable {entering_col} produce problema no acotado, omitiendo")
                    continue

                # Encontrar variable saliente
                leaving_row, pivot = self.tableau.get_leaving_variable(entering_col)

                if leaving_row == -1:
                    logger.debug(
                        f"No se pudo encontrar variable saliente para columna {entering_col}"
                    )
                    continue

                logger.debug(
                    f"Pivoteando: entrante={entering_col}, saliente={self.tableau.basic_vars[leaving_row]}"
                )

                # Realizar pivoteo
                self.tableau.pivot(entering_col, leaving_row)

                # Extraer la nueva solución
                alt_solution, alt_value = self.tableau.get_solution(maximize)

                # Verificar que el valor objetivo se mantiene (dentro de tolerancia)
                if abs(alt_value - optimal_value) < AlgorithmConfig.NUMERICAL_TOLERANCE:
                    # Verificar que la solución es diferente de la primera y de las ya encontradas
                    if self._is_different_solution(
                        alt_solution, first_solution
                    ) and not self._solution_exists(alt_solution, alternative_solutions):
                        alternative_solutions.append(alt_solution)
                        logger.info(
                            f"Solución alternativa #{len(alternative_solutions)} encontrada con valor {alt_value:.6f}"
                        )
                    else:
                        logger.debug("Solución duplicada o idéntica a la primera, omitiendo")
                else:
                    logger.warning(
                        f"Pivoteo produjo valor diferente: {alt_value:.6f} vs {optimal_value:.6f}"
                    )

            except Exception as e:
                logger.warning(
                    f"Error al explorar solución alternativa con variable {entering_col}: {e}"
                )
                continue

        # Restaurar tableau al estado óptimo original
        self.tableau.tableau = original_tableau
        self.tableau.basic_vars = original_basic_vars

        return alternative_solutions

    def _is_different_solution(
        self, solution1: Dict[str, float], solution2: Dict[str, float]
    ) -> bool:
        """
        Compara dos soluciones para determinar si son significativamente diferentes.

        Args:
            solution1: Primera solución a comparar.
            solution2: Segunda solución a comparar.

        Returns:
            True si las soluciones son diferentes (al menos una variable difiere
            más allá de la tolerancia numérica), False si son esencialmente iguales.
        """
        # Verificar que tengan las mismas variables
        if set(solution1.keys()) != set(solution2.keys()):
            return True

        # Comparar cada variable
        for var in solution1:
            diff = abs(solution1[var] - solution2[var])
            if diff > AlgorithmConfig.NUMERICAL_TOLERANCE:
                return True

        return False

    def _solution_exists(
        self, solution: Dict[str, float], solution_list: List[Dict[str, float]]
    ) -> bool:
        """
        Verifica si una solución ya existe en una lista de soluciones.

        Args:
            solution: Solución a buscar.
            solution_list: Lista de soluciones donde buscar.

        Returns:
            True si la solución ya existe en la lista, False en caso contrario.
        """
        for existing_solution in solution_list:
            if not self._is_different_solution(solution, existing_solution):
                return True
        return False
