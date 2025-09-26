"""
Módulo principal del algoritmo simplex.
Contiene la lógica de iteración y control del método simplex.
"""

from typing import Dict, Any
from .tableau import Tableau


class SimplexSolver:
    """Implementa el método simplex para resolver problemas de programación lineal."""
    
    def __init__(self):
        self.tableau = Tableau()
        self.max_iterations = 50
    
    def solve(self, c: list, A: list, b: list, maximize: bool = True) -> Dict[str, Any]:
        """
        Resuelve un problema de programación lineal usando el método simplex.
        
        Args:
            c: Coeficientes de la función objetivo
            A: Matriz de coeficientes de las restricciones
            b: Vector de términos independientes
            maximize: True para maximizar, False para minimizar
            
        Returns:
            Diccionario con la solución y metadatos del proceso
        """
        # Construir tableau inicial
        self.tableau.build_initial_tableau(c, A, b, maximize)
        
        print("Tableau inicial:")
        self.tableau.print_tableau()
        
        iteration = 0
        while iteration <= self.max_iterations:
            iteration += 1
            print(f"\n--- Iteración {iteration} ---")
            
            # Verificar optimalidad
            if self.tableau.is_optimal(maximize):
                print("Solución óptima encontrada!")
                return self._build_optimal_result(iteration, maximize)
            
            # Encontrar variable que entra
            entering_col = self.tableau.get_entering_variable(maximize)
            
            # Verificar si el problema es no acotado
            if self.tableau.is_unbounded(entering_col):
                return {
                    "status": "unbounded", 
                    "message": "El problema es no acotado",
                    "iterations": iteration
                }
            
            # Encontrar variable que sale
            leaving_row, pivot = self.tableau.get_leaving_variable(entering_col)
            
            print(f"Variable que entra: x{entering_col + 1}")
            print(f"Variable que sale: x{self.tableau.basic_vars[leaving_row] + 1}")
            print(f"Elemento pivote: {pivot}")
            
            # Realizar pivoteo
            self.tableau.pivot(entering_col, leaving_row)
            
            print("Tableau después del pivoteo:")
            self.tableau.print_tableau()
        
        return {
            "status": "error", 
            "message": "Demasiadas iteraciones",
            "iterations": iteration
        }
    
    def _build_optimal_result(self, iterations: int, maximize: bool) -> Dict[str, Any]:
        """Construye el diccionario de resultado para solución óptima."""
        solution, optimal_value = self.tableau.get_solution(maximize)
        
        return {
            "status": "optimal",
            "solution": solution,
            "optimal_value": optimal_value,
            "iterations": iterations,
        }