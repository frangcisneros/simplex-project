"""
Módulo para operaciones con el tableau simplex.

Este módulo implementa la estructura de datos Tableau y todas las operaciones
necesarias para el Método Simplex, incluyendo el Método de Dos Fases para
problemas con restricciones de igualdad (=) y mayor o igual (>=).

Responsabilidades principales:
- Construcción del tableau inicial con variables de holgura, exceso y artificiales
- Implementación del Método de Dos Fases para manejar restricciones >= y =
- Operaciones de pivoteo y actualización del tableau
- Detección de condiciones de optimalidad, infactibilidad y no acotación
- Extracción de soluciones del tableau

Método de Dos Fases:
    Fase 1: Minimiza la suma de variables artificiales para encontrar una solución
            básica factible (SBF). Si el valor óptimo es 0, el problema es factible.
    Fase 2: Resuelve el problema original después de eliminar las variables artificiales.
"""

import numpy as np
from typing import List, Tuple, Optional, Dict
from simplex_solver.config import AlgorithmConfig


class Tableau:
    """
    Estructura de datos para el tableau simplex con soporte para Método de Dos Fases.

    El tableau representa el sistema de ecuaciones lineales del problema de programación
    lineal en forma estándar, incluyendo variables de holgura, exceso y artificiales.

    Attributes:
        tableau: Matriz numpy (m+1) x (n+1) donde:
                 - m filas representan restricciones
                 - 1 fila adicional para la función objetivo
                 - n columnas para variables (originales + holgura + exceso + artificiales)
                 - 1 columna adicional para el lado derecho (RHS)
        basic_vars: Lista de índices de variables básicas (una por restricción)
        artificial_vars: Lista de índices de variables artificiales añadidas
        num_vars: Número de variables originales del problema
        num_constraints: Número de restricciones del problema
        constraint_types: Lista de tipos de restricciones ('<=', '>=', '=')
        phase: Fase actual del algoritmo (1 o 2)
        original_c: Coeficientes originales de la función objetivo
        tol: Tolerancia numérica para comparaciones

    Convención de la última fila:
        La última fila del tableau representa los costos reducidos r_j = c_j - z_j:
        - En Fase 1: minimiza suma de variables artificiales
        - En Fase 2: optimiza función objetivo original
    """

    def __init__(self):
        """Inicializa un tableau vacío."""
        self.tableau: Optional[np.ndarray] = None
        self.basic_vars: List[int] = []
        self.artificial_vars: List[int] = []
        self.num_vars: int = 0
        self.num_constraints: int = 0
        self.constraint_types: List[str] = []  # '<=', '>=', '='
        self.phase: int = 1  # 1 para Fase 1, 2 para Fase 2
        self.original_c: Optional[np.ndarray] = None  # Coeficientes originales guardados
        self.tol: float = AlgorithmConfig.NUMERICAL_TOLERANCE

    def build_initial_tableau(
        self,
        c: List[float],
        A: List[List[float]],
        b: List[float],
        constraint_types: List[str],
        maximize: bool = True,
    ) -> None:
        """
        Construye el tableau inicial para el Método Simplex con Dos Fases.

        Este método prepara el tableau completo incluyendo:
        - Variables originales
        - Variables de holgura para restricciones <=
        - Variables de exceso y artificiales para restricciones >=
        - Variables artificiales para restricciones =

        Args:
            c: Coeficientes de la función objetivo (n elementos)
            A: Matriz de coeficientes de restricciones (m × n)
            b: Vector de términos independientes (m elementos)
            constraint_types: Lista de tipos ('<=', '>=', '=') para cada restricción
            maximize: True para maximización, False para minimización

        Proceso:
            1. Normaliza todas las restricciones para tener RHS >= 0
            2. Cuenta variables necesarias (holgura, exceso, artificiales)
            3. Construye el tableau con todas las columnas necesarias
            4. Configura variables básicas iniciales
            5. Inicializa función objetivo de Fase 1 si hay variables artificiales

        Raises:
            ValueError: Si hay tipos de restricción desconocidos

        Note:
            - Restricciones con b[i] < 0 se multiplican por -1 e invierten su tipo
            - Para >=: añade variable de exceso (-1) y artificial (+1)
            - Para =: añade solo variable artificial (+1)
            - Para <=: añade solo variable de holgura (+1)
        """
        # Normalizar entradas
        constraint_types = [s.strip() for s in constraint_types]

        c_arr = np.array(c, dtype=float)
        A_arr = np.array(A, dtype=float)
        b_arr = np.array(b, dtype=float)
        self.constraint_types = constraint_types
        self.original_c = c_arr.copy()

        m, n = A_arr.shape
        self.num_vars = n
        self.num_constraints = m

        # Si hay RHS negativo, multiplicar fila por -1 y voltear el tipo de restricción
        for i in range(m):
            if b_arr[i] < -self.tol:
                A_arr[i, :] *= -1
                b_arr[i] *= -1
                # invertir el tipo de restricción cuando sea <= o >=
                if constraint_types[i] == "<=":
                    constraint_types[i] = ">="
                elif constraint_types[i] == ">=":
                    constraint_types[i] = "<="
                # '=' queda igual

        # Recontar variables necesarias (usar los tipos ya normalizados)
        num_slack = constraint_types.count("<=")
        num_surplus = constraint_types.count(">=")
        num_artificial = constraint_types.count(">=") + constraint_types.count("=")

        total_vars = n + num_slack + num_surplus + num_artificial

        # Inicializar tableau (m restricciones + 1 fila objetivo)
        self.tableau = np.zeros((m + 1, total_vars + 1))
        self.tableau[:-1, :n] = A_arr  # Coeficientes originales
        self.tableau[:-1, -1] = b_arr  # Lado derecho

        # Configurar variables de holgura, exceso y artificiales
        slack_idx = n
        artificial_idx = n + num_slack + num_surplus
        self.basic_vars = []
        self.artificial_vars = []

        # Insertar columnas en orden: [originals | slack(s) for <= | surplus(s) for >= | artificial]
        for i, const_type in enumerate(constraint_types):
            if const_type == "<=":
                # Variable de holgura +1
                self.tableau[i, slack_idx] = 1.0
                self.basic_vars.append(slack_idx)
                slack_idx += 1

            elif const_type == ">=":
                # Variable de exceso (-1) y artificial (+1)
                # surplus column
                self.tableau[i, slack_idx] = -1.0
                # artificial column
                self.tableau[i, artificial_idx] = 1.0
                self.basic_vars.append(artificial_idx)
                self.artificial_vars.append(artificial_idx)
                slack_idx += 1
                artificial_idx += 1

            elif const_type == "=":
                # Variable artificial
                self.tableau[i, artificial_idx] = 1.0
                self.basic_vars.append(artificial_idx)
                self.artificial_vars.append(artificial_idx)
                artificial_idx += 1

            else:
                raise ValueError(f"Tipo de restricción desconocido: {const_type}")

        # Configurar función objetivo
        if self.artificial_vars:
            # Fase 1: Minimizar suma de variables artificiales (convención: la fila objetivo
            # contendrá los costes reducidos asociados a la función de fase 1)
            self.phase = 1
            self._setup_phase1_objective()
        else:
            # Fase única: función objetivo original
            self.phase = 2
            self._setup_original_objective(self.original_c)

    def _setup_phase1_objective(self):
        """
        Configura la función objetivo para la Fase 1 del Método de Dos Fases.

        Objetivo de Fase 1:
            Minimizar w = Σ(variables artificiales)

        La Fase 1 busca una solución básica factible (SBF) para el problema original.
        Si w* = 0 al terminar la Fase 1, entonces existe una SBF y el problema
        es factible. Si w* > 0, el problema es infactible.

        Proceso:
            1. Inicializa fila objetivo con costo 1 para cada variable artificial
            2. Resta cada fila de restricción que contiene una variable artificial básica
            3. Esto asegura que las variables básicas tengan costo reducido cero

        Note:
            La última fila del tableau representa costos reducidos: r_j = c_j - z_j
            Para variables no básicas en Fase 1, buscamos r_j < 0 para mejorar.
        """
        # Inicializar fila objetivo: minimizar suma de artificiales
        self.tableau[-1, :] = 0.0
        for art_var in self.artificial_vars:
            self.tableau[-1, art_var] = 1.0

        # Hacer cero los costos reducidos de variables básicas artificiales
        for i, basic_var in enumerate(self.basic_vars):
            if basic_var in self.artificial_vars:
                self.tableau[-1, :] -= self.tableau[i, :]

    def _setup_original_objective(self, c_arr: np.ndarray):
        """Configura la función objetivo original.

        CONVENCIÓN: la última fila almacena los costes reducidos r_j = c_j - z_j.
        Inicialmente z_j = 0, por lo tanto r_j = c_j.
        """
        # Inicialmente colocar c en la última fila (r_j = c_j)
        self.tableau[-1, :] = 0.0
        self.tableau[-1, : len(c_arr)] = c_arr

        # Hacer cero los coeficientes de las variables básicas en la función objetivo
        # restando las filas de las variables básicas multiplicadas por su coste
        for i, basic_var in enumerate(self.basic_vars):
            if basic_var < len(c_arr):  # Si la variable básica es una variable original
                coefficient = self.tableau[-1, basic_var]
                if abs(coefficient) > self.tol:
                    self.tableau[-1, :] -= coefficient * self.tableau[i, :]

    def setup_phase2(self, original_c: np.ndarray, maximize: bool):
        """
        Prepara el tableau para la Fase 2 del Método de Dos Fases.

        Después de que la Fase 1 encuentra una solución básica factible (SBF),
        este método:
        1. Elimina todas las columnas de variables artificiales
        2. Reconstruye la función objetivo usando los coeficientes originales
        3. Actualiza las variables básicas a los nuevos índices de columna
        4. Garantiza que las variables básicas tengan costo reducido cero

        Args:
            original_c: Vector de coeficientes originales de la función objetivo
            maximize: True para maximización, False para minimización

        Process:
            1. Identifica columnas a mantener (excluye artificiales)
            2. Filtra el tableau para eliminar columnas artificiales
            3. Actualiza índices de variables básicas al nuevo sistema
            4. Maneja variables básicas degeneradas (si alguna artificial fue básica)
            5. Reconstru ye fila objetivo con r_j = c_j - z_j
            6. Hace cero los costos reducidos de variables básicas

        Note:
            Si una variable artificial sigue siendo básica al final de Fase 1
            con valor > 0, el problema es infactible. Este método asume que
            la verificación de factibilidad ya se realizó.
        """
        self.phase = 2

        # Guardar mapa de columnas que se mantienen
        cols_to_keep = [i for i in range(self.tableau.shape[1]) if i not in self.artificial_vars]
        old_to_new = {old: new for new, old in enumerate(cols_to_keep)}

        # Filtrar la matriz
        self.tableau = self.tableau[:, cols_to_keep]

        # Recalcular índices de variables básicas (convertir índices viejos a nuevos)
        new_basic_vars = []
        for var in self.basic_vars:
            if var in old_to_new:
                new_basic_vars.append(old_to_new[var])
            else:
                # variable básica era artificial y fue eliminada -> situación degenerada
                new_basic_vars.append(-1)
        self.basic_vars = new_basic_vars

        # Si alguna básica quedó -1 (posición eliminada), buscaremos una columna que sea
        # una columna identidad en esa fila para poner como básica (heurística simple).
        for i, var in enumerate(self.basic_vars):
            if var == -1:
                # buscar columna j con tableau[i,j] == 1 y columna j tiene ceros en otras filas
                found = False
                for j in range(self.tableau.shape[1] - 1):
                    if abs(self.tableau[i, j] - 1.0) < self.tol and np.all(
                        np.abs(self.tableau[:, j] - np.eye(self.tableau.shape[0])[:, j]) < 1e-6
                    ):
                        self.basic_vars[i] = j
                        found = True
                        break
                if not found:
                    pass

        total_vars = self.tableau.shape[1] - 1

        # Reconstruir la fila objetivo r_j = c_j - z_j utilizando original_c
        new_obj_row = np.zeros(total_vars + 1)
        # colocar c_j en posiciones originales
        new_obj_row[: len(original_c)] = original_c
        self.tableau[-1, :] = new_obj_row

        # Hacer cero los coeficientes de las variables básicas (restar fila básica * coef)
        for i, basic_var in enumerate(self.basic_vars):
            if 0 <= basic_var < len(original_c):
                coefficient = self.tableau[-1, basic_var]
                if abs(coefficient) > self.tol:
                    self.tableau[-1, :] -= coefficient * self.tableau[i, :]

    def has_artificial_vars_in_basis(self) -> bool:
        """Verifica si hay variables artificiales en la base con valor positivo."""
        for i, basic_var in enumerate(self.basic_vars):
            if basic_var in self.artificial_vars and abs(self.tableau[i, -1]) > self.tol:
                return True
        return False

    def is_optimal(self, maximize: bool) -> bool:
        """Verifica si la solución actual es óptima.

        Con la convención r_j = c_j - z_j:
        - Para maximización: óptimo si todos r_j <= 0 (no hay r_j > 0).
        - Para minimización: óptimo si todos r_j >= 0 (no hay r_j < 0).
        """
        last_row = self.tableau[-1, :-1]
        if self.phase == 1:
            # Fase 1: estamos minimizando suma de artificiales -> óptimo si no hay coef negativos
            return np.all(last_row >= -self.tol)
        else:
            if maximize:
                return np.all(last_row <= self.tol)
            else:
                return np.all(last_row >= -self.tol)

    def get_entering_variable(self, maximize: bool) -> int:
        """Encuentra la variable que entra a la base (regla: mejor coeficiente).

        Para fase 1: buscamos coeficientes negativos (porque construimos la fila de fase1
        como suma de artificiales y restamos filas básicas).
        Para fase 2:
          - maximize: elegir columna con r_j > tol (máximo r_j)
          - minimize: elegir columna con r_j < -tol (mínimo r_j)
        Se aplica regla de Bland en empates (elegir índice menor).
        """
        last_row = self.tableau[-1, :-1]

        if self.phase == 1:
            candidates = [
                (i, val)
                for i, val in enumerate(last_row)
                if val < -self.tol and i not in self.artificial_vars
            ]
            if not candidates:
                return -1
            # elegir el más negativo
            chosen = min(candidates, key=lambda x: (x[1], x[0]))
            return chosen[0]
        else:
            if maximize:
                candidates = [(i, val) for i, val in enumerate(last_row) if val > self.tol]
                if not candidates:
                    return -1
                # elegir el más grande; en empates Bland (menor índice)
                max_val = max(val for _, val in candidates)
                best = [i for i, v in candidates if abs(v - max_val) < 1e-12]
                return min(best)
            else:
                # minimización: buscamos coeficientes negativos r_j < 0
                candidates = [(i, val) for i, val in enumerate(last_row) if val < -self.tol]
                if not candidates:
                    return -1
                min_val = min(val for _, val in candidates)
                best = [i for i, v in candidates if abs(v - min_val) < 1e-12]
                return min(best)

    def is_unbounded(self, entering_col: int) -> bool:
        """Verifica si el problema es no acotado (todas las entradas de la columna <= 0)."""
        return np.all(self.tableau[:-1, entering_col] <= self.tol)

    def get_leaving_variable(self, entering_col: int) -> Tuple[int, float]:
        """Encuentra la variable que sale de la base y el elemento pivote (ratio test).

        Devuelve (fila, pivot_val) o (-1, 0) si no hay fila candidata.
        """
        ratios = [float("inf")] * self.num_constraints
        for i in range(self.num_constraints):
            a_ij = self.tableau[i, entering_col]
            if a_ij > self.tol:
                ratio = self.tableau[i, -1] / a_ij
                if ratio >= -self.tol:
                    ratios[i] = ratio

        if all(r == float("inf") for r in ratios):
            return -1, 0.0

        # elegir la fila con ratio mínimo (si empates, regla de Bland: menor índice)
        leaving_row = int(np.argmin(ratios))
        pivot = self.tableau[leaving_row, entering_col]
        return leaving_row, pivot

    def pivot(self, entering_col: int, leaving_row: int) -> None:
        """Realiza la operación de pivoteo."""
        pivot = self.tableau[leaving_row, entering_col]
        if abs(pivot) < AlgorithmConfig.PIVOT_TOLERANCE:
            raise ZeroDivisionError(
                f"Pivote casi nulo ({pivot:.2e}) detectado durante pivoteo. "
                "Esto indica un problema mal condicionado en la formulación."
            )

        # Actualizar variables básicas
        self.basic_vars[leaving_row] = entering_col

        # Normalizar fila pivote
        self.tableau[leaving_row, :] /= pivot

        # Actualizar otras filas
        for i in range(self.num_constraints + 1):
            if i != leaving_row:
                factor = self.tableau[i, entering_col]
                if abs(factor) > self.tol:
                    self.tableau[i, :] -= factor * self.tableau[leaving_row, :]

    def get_solution(self, maximize: bool) -> Tuple[dict, float]:
        """Extrae la solución del tableau actual y calcula el valor óptimo con c^T x."""
        solution = {}

        # Inicializar todas las variables originales en cero
        for i in range(self.num_vars):
            solution[f"x{i+1}"] = 0.0

        # Asignar valores de variables básicas
        x = np.zeros(self.num_vars)
        for i, var in enumerate(self.basic_vars):
            if 0 <= var < self.num_vars:  # Solo variables originales
                x[var] = float(self.tableau[i, -1])
                solution[f"x{var+1}"] = float(self.tableau[i, -1])

        # Calcular valor óptimo con el c original guardado
        if self.original_c is None:
            optimal_value = float(self.tableau[-1, -1])  # fallback
        else:
            optimal_value = float(np.dot(self.original_c, x))

        return solution, optimal_value

    def print_tableau(self) -> None:
        """Imprime el tableau actual de forma legible."""
        if self.tableau is not None:
            phase_str = "Fase 1" if self.phase == 1 else "Fase 2"
            print(f"Tableau ({phase_str}):")
            for row in self.tableau:
                print("  " + "  ".join(f"{val:8.2f}" for val in row))
            print()
