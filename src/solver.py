"""
Módulo principal del algoritmo simplex.
Contiene la lógica de iteración y control del método simplex.
"""

from typing import Dict, Any
import numpy as np
from tableau import Tableau
from typing import List, Tuple, Optional, Dict, Any
from copy import deepcopy
from src.debug import Debug


class SimplexSolver:
    """Implementa el método simplex para resolver problemas de programación lineal."""
    
    def __init__(self):
        self.tableau = Tableau()
        self.max_iterations = 100
        self.steps = []     # Historial de pasos para PDF
    
    def _solve_phase(self, maximize: bool) -> Dict[str, Any]:
        """Resuelve una fase del método simplex."""
        self.tableau: Optional[np.ndarray] = None
        self.variables: List[str] = []
        self.solution: Dict[str, float] = {}

    def solve(
        self,
        c: List[float],
        A: List[List[float]],
        b: List[float],
        maximize: bool = True,
        debug: Optional[Debug] = None,   # recibe debug
    ) -> Dict[str, Any]:
        """
        Resuelve un problema de programación lineal usando el método simplex.

        Args:
            c: Coeficientes de la función objetivo
            A: Matriz de coeficientes de las restricciones
            b: Vector de términos independientes
            maximize: True para maximizar, False para minimizar
            debug: Instancia de Debug para trazar las iteraciones

        Returns:
            dict: Diccionario con la solución y el valor óptimo
        """
        # Convertir a arrays de numpy
        c_arr = np.array(c, dtype=float)
        A_arr = np.array(A, dtype=float)
        b_arr = np.array(b, dtype=float)

        # Construir el tableau inicial
        m, n = A_arr.shape

        # Agregar variables de holgura
        slack_matrix = np.eye(m)
        A_extended = np.hstack([A_arr, slack_matrix])

        # Para el tableau simplex:
        # - Maximización: coeficientes van negados (-c)
        # - Minimización: coeficientes van positivos (c)
        if maximize:
            c_tableau = -c_arr
        else:
            c_tableau = c_arr

        # Agregar función objetivo al tableau
        c_extended = np.hstack([c_tableau, np.zeros(m)])

        # Crear el tableau completo
        self.tableau = np.zeros((m + 1, n + m + 1))
        self.tableau[:-1, :-1] = A_extended
        self.tableau[:-1, -1] = b_arr
        self.tableau[-1, :-1] = c_extended

        # Variables básicas iniciales (variables de holgura)
        basic_vars = list(range(n, n + m))

        print("Tableau inicial:")
        self._print_tableau()

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
            
            # Guardar el tableau antes del pivoteo para el reporte
            tableau_before= self.tableau.tableau.copy()
            # Encontrar la variable que sale (fila pivote)
            ratios = []
            for i in range(m):
                if self.tableau[i, entering_col] > 0:
                    ratios.append(self.tableau[i, -1] / self.tableau[i, entering_col])
                else:
                    ratios.append(float("inf"))

            leaving_row = int(np.argmin(ratios))
            pivot = self.tableau[leaving_row, entering_col]

            print(f"Variable que entra: x{entering_col + 1}")
            print(f"Variable que sale: x{basic_vars[leaving_row] + 1}")
            print(f"Elemento pivote: {pivot}")

            # Log "before pivot"
            if debug:
                debug.log_iteration(
                    iteration,
                    deepcopy(self.tableau),
                    entering=entering_name,
                    leaving=leaving_name,
                    pivot=pivot,
                    ratios=ratios,
                    z=current_z,
                    msg="before pivot",
                )

            # Actualizar variables básicas
            basic_vars[leaving_row] = entering_col

            # Operaciones de pivoteo
            self.tableau[leaving_row] /= pivot

            for i in range(m + 1):
                if i != leaving_row:
                    self.tableau[i] -= (
                        self.tableau[i, entering_col] * self.tableau[leaving_row]
                    )

            # Realizar pivoteo
            self.tableau.pivot(entering_col, leaving_row)
            
            print("Tableau después del pivoteo:")
            self._print_tableau()

            if iteration > 50:  # Prevenir bucles infinitos
                return {"status": "error", "message": "Demasiadas iteraciones"}
        
        # Log "after pivot"
            if debug:
                debug.log_iteration(
                    iteration,
                    deepcopy(self.tableau),
                    entering=entering_name,
                    leaving=leaving_name,
                    pivot=pivot,
                    ratios=ratios,
                    z=new_z,
                    msg="after pivot",
                )

            print("Tableau después del pivoteo:")
            self._print_tableau()

            if iteration > 50:  # Prevenir bucles infinitos
                return {"status": "error", "message": "Demasiadas iteraciones"}

        # Construir la solución
        solution = {}
        for i in range(n):
            solution[f"x{i+1}"] = 0.0

        for i, var in enumerate(basic_vars):
            if var < n:  # Solo variables originales
                solution[f"x{var+1}"] = float(self.tableau[i, -1])

        optimal_value = float(self.tableau[-1, -1])
        # Para minimización, cambiar el signo del valor del tableau
        if not maximize:
            optimal_value = -optimal_value

        return {
            "status": "error", 
            "message": "Demasiadas iteraciones",
            "iterations": iteration
        }
    
    def solve(self, c: list, A: list, b: list, constraint_types: list, maximize: bool = True) -> Dict[str, Any]:
        """
        Resuelve un problema de programación lineal usando el método simplex.
        """
        self.steps.clear() # Limpiar historial de pasos

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
                "steps": self.steps
            }
            if self.tableau.artificial_vars:
                result["phase1_iterations"] = phase1_iterations
            return result
        else:
            return {**phase2_result, "iterations": total_iterations}

    # Función objetivo
    print("\nIngrese los coeficientes de la función objetivo:")
    while True:
        try:
            c_input = input("Coeficientes (separados por espacios): ")
            c = list(map(float, c_input.split()))
            break
        except ValueError:
            print("Error: Ingrese números válidos separados por espacios")

    num_vars = len(c)
    print(f"Variables detectadas: {num_vars} (x1, x2, ..., x{num_vars})")

    # Restricciones
    print(f"\nIngrese las restricciones (formato: a1 a2 ... a{num_vars} <= b):")
    print("Escriba 'fin' cuando termine de ingresar restricciones")

    A = []
    b = []

    while True:
        constraint = input(f"Restricción {len(A) + 1}: ").strip()
        if constraint.lower() == "fin":
            break

        try:
            if "<=" not in constraint:
                print("Error: Use el formato 'a1 a2 ... <= b'")
                continue

            parts = constraint.split("<=")
            coeffs = list(map(float, parts[0].split()))
            rhs = float(parts[1])

            if len(coeffs) != num_vars:
                print(f"Error: Debe ingresar {num_vars} coeficientes")
                continue

            A.append(coeffs)
            b.append(rhs)

        except ValueError:
            print("Error: Formato inválido. Use números válidos.")

    if not A:
        print("Error: Debe ingresar al menos una restricción")
        sys.exit(1)

    return c, A, b, maximize


def main():
    parser = argparse.ArgumentParser(
        description="Simplex Solver - Resuelve problemas de programación lineal"
    )
    parser.add_argument(
        "filename", nargs="?", help="Archivo con el problema a resolver"
    )
    parser.add_argument(
        "--interactive", "-i", action="store_true", help="Modo interactivo"
    )
    parser.add_argument(
        "--debug", choices=["NONE", "L", "M", "XL"], default="NONE",
        help="Nivel de debug (NONE, L, M, XL)"
    )
    parser.add_argument(
        "--debug-out", help="Archivo JSON para guardar el trace de debug"
    )

    args = parser.parse_args()

    if args.filename:
        # Modo archivo
        print(f"=== SIMPLEX SOLVER - Resolviendo archivo: {args.filename} ===\n")
        c, A, b, maximize = parse_file(args.filename)
    elif args.interactive or len(sys.argv) == 1:
        # Modo interactivo
        c, A, b, maximize = interactive_input()
    else:
        parser.print_help()
        sys.exit(1)

    # Mostrar el problema
    print("\n" + "=" * 50)
    print("PROBLEMA A RESOLVER:")
    print("=" * 50)

    obj_type = "Maximizar" if maximize else "Minimizar"
    print(f"{obj_type}: ", end="")

    for i, coeff in enumerate(c):
        if i > 0 and coeff >= 0:
            print(" + ", end="")
        elif coeff < 0:
            print(" ", end="")
        print(f"{coeff}x{i+1}", end="")
    print()

    print("\nSujeto a:")
    for i, (row, rhs) in enumerate(zip(A, b)):
        print(f"  ", end="")
        for j, coeff in enumerate(row):
            if j > 0 and coeff >= 0:
                print(" + ", end="")
            elif coeff < 0:
                print(" ", end="")
            print(f"{coeff}x{j+1}", end="")
        print(f" <= {rhs}")

    print("  xi >= 0 para todo i")
    print("=" * 50)

    # Resolver
    solver = SimplexSolver()
    result = solver.solve(c, A, b, maximize)

    # Mostrar resultado
    print("\n" + "=" * 50)
    print("RESULTADO:")
    print("=" * 50)

    if result["status"] == "optimal":
        print("Estado: Solución óptima encontrada")
        print(f"Iteraciones: {result['iterations']}")
        print(f"Valor óptimo: {result['optimal_value']:.4f}")
        print("\nSolución:")
        for var, value in result["solution"].items():
            print(f"  {var} = {value:.4f}")
    else:
        print(f"Estado: {result['status']}")
        print(f"Mensaje: {result['message']}")


if __name__ == "__main__":
    main()
