"""
Módulo principal del algoritmo simplex.
Contiene la lógica de iteración y control del método simplex.
"""

from typing import Dict, Any
import numpy as np
from tableau import Tableau


class SimplexSolver:
    """Implementa el método simplex para resolver problemas de programación lineal."""
    
    def __init__(self):
        self.tableau = Tableau()
        self.max_iterations = 100
    
    def solve(self, c: list, A: list, b: list, constraint_types: list, maximize: bool = True) -> Dict[str, Any]:
        """
        Resuelve un problema de programación lineal usando el método simplex.
        """
        # Construir tableau inicial
        self.tableau.build_initial_tableau(c, A, b, constraint_types, maximize)
        
        print("Tableau inicial:")
        self.tableau.print_tableau()
        
        total_iterations = 0
        phase1_iterations = 0
        
        # Fase 1: Si hay variables artificiales
        if self.tableau.artificial_vars:
            print("\n=== FASE 1: Eliminando variables artificiales ===")
            phase1_result = self._solve_phase(maximize)
            phase1_iterations = phase1_result["iterations"]
            total_iterations += phase1_iterations
            
            if phase1_result["status"] != "optimal":
                return {**phase1_result, "iterations": total_iterations}
            
            # Verificar factibilidad
            if abs(self.tableau.tableau[-1, -1]) > 1e-10 or self.tableau.has_artificial_vars_in_basis():
                return {
                    "status": "infeasible",
                    "message": "El problema no tiene solución factible",
                    "iterations": total_iterations
                }
            
            print(f"\nFase 1 completada en {phase1_iterations} iteraciones")
            print("Valor de la función objetivo de Fase 1:", self.tableau.tableau[-1, -1])
            
            # Preparar Fase 2
            print("\n=== FASE 2: Optimizando función objetivo original ===")
            self.tableau.setup_phase2(np.array(c), maximize)
            print("Tableau inicial para Fase 2:")
            self.tableau.print_tableau()
        
        # Fase 2 (o única fase)
        print("\n=== FASE 2: Optimizando función objetivo original ===")
        phase2_result = self._solve_phase(maximize)
        total_iterations += phase2_result["iterations"]
        
        if phase2_result["status"] == "optimal":
            solution, optimal_value = self.tableau.get_solution(maximize)
            result = {
                "status": "optimal",
                "solution": solution,
                "optimal_value": optimal_value,
                "iterations": total_iterations,
            }
            if self.tableau.artificial_vars:
                result["phase1_iterations"] = phase1_iterations
            return result
        else:
            return {**phase2_result, "iterations": total_iterations}
    
    def _solve_phase(self, maximize: bool) -> Dict[str, Any]:
        """Resuelve una fase del método simplex."""
        iteration = 0
        
        while iteration < self.max_iterations:
            iteration += 1
            print(f"\n--- Iteración {iteration} ---")
            
            # Verificar optimalidad
            is_optimal = self.tableau.is_optimal(maximize)
            
            if is_optimal:
                print("¡Solución óptima de la fase encontrada!")
                return {"status": "optimal", "iterations": iteration}
            
            # Encontrar variable que entra
            entering_col = self.tableau.get_entering_variable(maximize)
            
            if entering_col == -1:
                print("No se encontró variable para entrar - solución óptima")
                return {"status": "optimal", "iterations": iteration}
            
            print(f"Variable que entra: columna {entering_col + 1}")

            # Verificar si el problema es no acotado
            if self.tableau.is_unbounded(entering_col):
                print("⚠️ [DEBUG] Resultado: columna sin coeficientes positivos → UNBOUNDED detectado")
                return {
                    "status": "unbounded",
                    "message": "El problema es no acotado",
                    "iterations": iteration
                }

            # Encontrar variable que sale
            leaving_row, pivot = self.tableau.get_leaving_variable(entering_col)
            
            if leaving_row == -1:
                return {
                    "status": "error",
                    "message": "No se pudo encontrar variable para salir",
                    "iterations": iteration
                }
            
            print(f"Variable que sale: fila {leaving_row + 1}")
            print(f"Elemento pivote: {pivot:.4f}")
            
            # Realizar pivoteo
            self.tableau.pivot(entering_col, leaving_row)
            
            print("Tableau después del pivoteo:")
            self.tableau.print_tableau()
        
        return {
            "status": "error", 
            "message": "Demasiadas iteraciones",
            "iterations": iteration
        }