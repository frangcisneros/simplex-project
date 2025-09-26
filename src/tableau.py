"""
Módulo para operaciones con el tableau simplex.
Contiene la lógica de construcción y manipulación del tableau.
"""

import numpy as np
from typing import List, Tuple, Optional

class Tableau:
    """Clase para manejar las operaciones del tableau simplex."""
    
    def __init__(self):
        self.tableau: Optional[np.ndarray] = None
        self.basic_vars: List[int] = []
        self.num_vars: int = 0
        self.num_constraints: int = 0
    
    def build_initial_tableau(self, c: List[float], A: List[List[float]], 
                            b: List[float], maximize: bool = True) -> None:
        """
        Construye el tableau inicial para el problema simplex.
        
        Args:
            c: Coeficientes de la función objetivo
            A: Matriz de coeficientes de restricciones
            b: Términos independientes de restricciones
            maximize: True para maximización, False para minimización
        """
        c_arr = np.array(c, dtype=float)
        A_arr = np.array(A, dtype=float)
        b_arr = np.array(b, dtype=float)
        
        m, n = A_arr.shape
        self.num_vars = n
        self.num_constraints = m
        
        # Agregar variables de holgura
        slack_matrix = np.eye(m)
        A_extended = np.hstack([A_arr, slack_matrix])
        
        # Configurar coeficientes de la función objetivo
        c_tableau = -c_arr if maximize else c_arr
        c_extended = np.hstack([c_tableau, np.zeros(m)])
        
        # Construir tableau completo
        self.tableau = np.zeros((m + 1, n + m + 1))
        self.tableau[:-1, :-1] = A_extended
        self.tableau[:-1, -1] = b_arr
        self.tableau[-1, :-1] = c_extended
        
        # Variables básicas iniciales (variables de holgura)
        self.basic_vars = list(range(n, n + m))
    
    def is_optimal(self, maximize: bool) -> bool:
        """Verifica si la solución actual es óptima."""
        if maximize:
            return np.all(self.tableau[-1, :-1] >= 0)
        else:
            return np.all(self.tableau[-1, :-1] <= 0)
    
    def get_entering_variable(self, maximize: bool) -> int:
        """Encuentra la variable que entra a la base."""
        if maximize:
            return int(np.argmin(self.tableau[-1, :-1]))
        else:
            return int(np.argmax(self.tableau[-1, :-1]))
    
    def is_unbounded(self, entering_col: int) -> bool:
        """Verifica si el problema es no acotado."""
        return np.all(self.tableau[:-1, entering_col] <= 0)
    
    def get_leaving_variable(self, entering_col: int) -> Tuple[int, float]:
        """
        Encuentra la variable que sale de la base y el elemento pivote.
        
        Returns:
            Tuple con (índice de fila pivote, valor del pivote)
        """
        ratios = []
        for i in range(self.num_constraints):
            if self.tableau[i, entering_col] > 0:
                ratios.append(self.tableau[i, -1] / self.tableau[i, entering_col])
            else:
                ratios.append(float("inf"))
        
        leaving_row = int(np.argmin(ratios))
        pivot = self.tableau[leaving_row, entering_col]
        
        return leaving_row, pivot
    
    def pivot(self, entering_col: int, leaving_row: int) -> None:
        """Realiza la operación de pivoteo."""
        pivot = self.tableau[leaving_row, entering_col]
        
        # Actualizar variables básicas
        self.basic_vars[leaving_row] = entering_col
        
        # Normalizar fila pivote
        self.tableau[leaving_row] /= pivot
        
        # Actualizar otras filas
        for i in range(self.num_constraints + 1):
            if i != leaving_row:
                self.tableau[i] -= self.tableau[i, entering_col] * self.tableau[leaving_row]
    
    def get_solution(self, maximize: bool) -> Tuple[dict, float]:
        """Extrae la solución del tableau actual."""
        solution = {}
        
        # Inicializar todas las variables en cero
        for i in range(self.num_vars):
            solution[f"x{i+1}"] = 0.0
        
        # Asignar valores de variables básicas
        for i, var in enumerate(self.basic_vars):
            if var < self.num_vars:  # Solo variables originales
                solution[f"x{var+1}"] = float(self.tableau[i, -1])
        
        optimal_value = float(self.tableau[-1, -1])
        if not maximize:
            optimal_value = -optimal_value
        
        return solution, optimal_value
    
    def print_tableau(self) -> None:
        """Imprime el tableau actual de forma legible."""
        if self.tableau is not None:
            print("Tableau:")
            for row in self.tableau:
                print("  " + "  ".join(f"{val:8.2f}" for val in row))
            print()