"""
Módulo de Análisis de Sensibilidad para el método Simplex.

Calcula Precios Sombra, Rangos de Optimalidad y Rangos de Factibilidad
después de encontrar una solución óptima.
"""

from typing import Dict, Tuple, Optional, Any
import numpy as np
from simplex_solver.logging_system import logger


class SensitivityAnalyzer:
    """
    Realiza análisis de sensibilidad sobre un tableau óptimo del método Simplex.

    Responsabilidades:
    - Calcular precios sombra (valores duales)
    - Determinar rangos de optimalidad para los coeficientes de la función objetivo
    - Determinar rangos de factibilidad para los valores del lado derecho (RHS)
    """

    def __init__(self, tableau: np.ndarray, basic_vars: list, num_vars: int, num_constraints: int):
        """
        Inicializa el analizador de sensibilidad.

        Args:
            tableau: El tableau óptimo del método Simplex.
            basic_vars: Lista de índices de variables básicas.
            num_vars: Número de variables de decisión originales.
            num_constraints: Número de restricciones (excluyendo no negatividad).
        """
        self.tableau = tableau
        self.basic_vars = basic_vars
        self.num_vars = num_vars
        self.num_constraints = num_constraints
        logger.debug(
            f"SensitivityAnalyzer inicializado: {num_vars} variables, {num_constraints} restricciones"
        )

    def calculate_shadow_prices(self) -> Dict[str, float]:
        """
        Calcula los precios sombra (valores duales) para cada restricción.

        Los precios sombra representan el valor marginal de relajar cada restricción.
        Se extraen de los coeficientes de las variables de holgura en la fila objetivo.

        Returns:
            dict: Diccionario que mapea los nombres de las restricciones a sus precios sombra.
        """
        logger.debug("Calculando precios sombra...")
        shadow_prices = {}

        # La fila de la función objetivo es la última fila del tableau
        obj_row = self.tableau[-1, :]

        # Los precios sombra son los negativos de los coeficientes de las variables de holgura
        # en la fila objetivo. Las variables de holgura comienzan después de las variables de decisión.
        for i in range(self.num_constraints):
            slack_col = self.num_vars + i
            shadow_price = -obj_row[slack_col]
            constraint_name = f"restriccion_{i + 1}"
            shadow_prices[constraint_name] = float(shadow_price)
            logger.debug(f"Precio sombra para {constraint_name}: {shadow_price:.6f}")

        return shadow_prices

    def calculate_optimality_ranges(self, original_c: np.ndarray) -> Dict[str, Tuple[float, float]]:
        """
        Calcula los rangos de optimalidad para los coeficientes de la función objetivo.

        Para cada variable de decisión, determina el rango [c_min, c_max] dentro del cual
        el coeficiente puede variar sin cambiar la base óptima.

        Args:
            original_c: Coeficientes originales de la función objetivo.

        Returns:
            dict: Diccionario que mapea los nombres de las variables a tuplas (min, max).
        """
        logger.debug("Calculando rangos de optimalidad...")
        opt_ranges = {}

        for j in range(self.num_vars):
            var_name = f"x{j + 1}"
            c_current = original_c[j]

            # Verifica si la variable está en la base
            if j in self.basic_vars:
                # Variable básica: calcula el rango a partir de los costos reducidos de las variables no básicas
                min_delta, max_delta = self._calculate_basic_var_range(j)
            else:
                # Variable no básica: usa directamente el costo reducido
                min_delta, max_delta = self._calculate_nonbasic_var_range(j)

            c_min = c_current + min_delta
            c_max = c_current + max_delta

            opt_ranges[var_name] = (float(c_min), float(c_max))
            logger.debug(f"Rango de optimalidad para {var_name}: [{c_min:.4f}, {c_max:.4f}]")

        return opt_ranges

    def _calculate_basic_var_range(self, var_index: int) -> Tuple[float, float]:
        """
        Calcula el rango para el coeficiente de una variable básica.

        Args:
            var_index: Índice de la variable básica.

        Returns:
            tuple: (min_delta, max_delta) para el cambio del coeficiente.
        """
        # Encuentra en qué fila esta variable es básica
        try:
            row = self.basic_vars.index(var_index)
        except ValueError:
            logger.warning(f"Variable {var_index} no encontrada en las variables básicas")
            return (float("-inf"), float("inf"))

        # Obtiene la columna de esta variable en el tableau
        var_column = self.tableau[:, var_index]

        # Para una variable básica, se analiza cómo cambiar su coeficiente
        # afectaría los costos reducidos de las variables no básicas
        obj_row = self.tableau[-1, :]

        min_delta = float("-inf")
        max_delta = float("inf")

        # Verifica cada columna de variable no básica
        for j in range(self.num_vars):
            if j not in self.basic_vars:
                # Coeficiente en el tableau para esta variable no básica en la fila de la variable básica
                a_ij = self.tableau[row, j]
                reduced_cost = obj_row[j]

                if abs(a_ij) > 1e-10:
                    # Delta debe mantener el costo reducido >= 0 (para maximización)
                    # reduced_cost - delta * a_ij >= 0
                    # delta <= reduced_cost / a_ij (si a_ij > 0)
                    # delta >= reduced_cost / a_ij (si a_ij < 0)
                    ratio = reduced_cost / a_ij

                    if a_ij > 0:
                        max_delta = min(max_delta, ratio)
                    else:
                        min_delta = max(min_delta, ratio)

        return (min_delta, max_delta)

    def _calculate_nonbasic_var_range(self, var_index: int) -> Tuple[float, float]:
        """
        Calcula el rango para el coeficiente de una variable no básica.

        Args:
            var_index: Índice de la variable no básica.

        Returns:
            tuple: (min_delta, max_delta) para el cambio del coeficiente.
        """
        # Para una variable no básica, el costo reducido indica cuánto
        # debe cambiar el coeficiente para entrar en la base
        obj_row = self.tableau[-1, :]
        reduced_cost = obj_row[var_index]

        # Para maximización: la variable puede aumentar en reduced_cost antes de entrar en la base
        # Puede disminuir indefinidamente sin afectar la optimalidad
        min_delta = float("-inf")
        max_delta = reduced_cost

        return (min_delta, max_delta)

    def calculate_feasibility_ranges(
        self, original_b: np.ndarray
    ) -> Dict[str, Tuple[float, float]]:
        """
        Calcula los rangos de factibilidad para los valores del lado derecho (RHS).

        Para cada restricción, determina el rango [b_min, b_max] dentro del cual
        el RHS puede variar sin cambiar la base óptima.

        Args:
            original_b: Valores originales del RHS.

        Returns:
            dict: Diccionario que mapea los nombres de las restricciones a tuplas (min, max).
        """
        logger.debug("Calculando rangos de factibilidad...")
        feas_ranges = {}

        # Extrae el RHS actual (valores de solución) del tableau
        current_rhs = self.tableau[
            :-1, -1
        ]  # Todas las filas excepto la de la función objetivo, última columna

        for i in range(self.num_constraints):
            constraint_name = f"restriccion_{i + 1}"
            b_current = original_b[i]

            # Calcula cuánto puede cambiar cada variable básica
            # cuando perturbamos el valor RHS de la i-ésima restricción
            min_delta, max_delta = self._calculate_rhs_range(i)

            b_min = b_current + min_delta
            b_max = b_current + max_delta

            feas_ranges[constraint_name] = (float(b_min), float(b_max))
            logger.debug(
                f"Rango de factibilidad para {constraint_name}: [{b_min:.4f}, {b_max:.4f}]"
            )

        return feas_ranges

    def _calculate_rhs_range(self, constraint_index: int) -> Tuple[float, float]:
        """
        Calcula el rango para el valor RHS de una restricción.

        Args:
            constraint_index: Índice de la restricción.

        Returns:
            tuple: (min_delta, max_delta) para el cambio del RHS.
        """
        # El índice de la restricción corresponde a una columna de variable de holgura
        slack_col = self.num_vars + constraint_index

        # Obtiene la columna para esta variable de holgura
        slack_column = self.tableau[:-1, slack_col]  # Excluye la fila de la función objetivo

        # Valores actuales del RHS (valores básicos de solución)
        current_rhs = self.tableau[:-1, -1]

        min_delta = float("-inf")
        max_delta = float("inf")

        # Para cada variable básica, calcula el ratio
        for row in range(len(current_rhs)):
            a_i = slack_column[row]
            b_i = current_rhs[row]

            if abs(a_i) > 1e-10:
                # Cuando aumentamos RHS en delta, la variable básica cambia en delta * a_i
                # Necesitamos: b_i + delta * a_i >= 0
                # delta >= -b_i / a_i (si a_i > 0)
                # delta <= -b_i / a_i (si a_i < 0)
                ratio = -b_i / a_i

                if a_i > 0:
                    min_delta = max(min_delta, ratio)
                else:
                    max_delta = min(max_delta, ratio)

        return (min_delta, max_delta)

    def analyze(self, original_c: np.ndarray, original_b: np.ndarray) -> Dict[str, Dict[str, Any]]:
        """
        Realiza un análisis completo de sensibilidad.

        Args:
            original_c: Coeficientes originales de la función objetivo.
            original_b: Valores originales del RHS.

        Returns:
            dict: Diccionario que contiene precios sombra, rangos de optimalidad y rangos de factibilidad.
        """
        logger.info("Realizando análisis completo de sensibilidad...")

        analysis = {
            "shadow_prices": self.calculate_shadow_prices(),
            "optimality_ranges": self.calculate_optimality_ranges(original_c),
            "feasibility_ranges": self.calculate_feasibility_ranges(original_b),
        }

        logger.info("Análisis de sensibilidad completado exitosamente")
        return analysis
