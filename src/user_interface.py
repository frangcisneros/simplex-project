"""
Módulo para interacción con el usuario.
Contiene funciones para entrada interactiva y visualización de resultados.
"""

import sys
from typing import List, Tuple


class UserInterface:
    """Maneja la interacción con el usuario y visualización de resultados."""
    
    @staticmethod
    def interactive_input() -> Tuple[List[float], List[List[float]], List[float], bool]:
        """Recoge entrada del problema de forma interactiva."""
        print("=== SIMPLEX SOLVER - Modo Interactivo ===\n")
        
        maximize = UserInterface._get_optimization_type()
        c = UserInterface._get_objective_function()
        A, b = UserInterface._get_constraints(len(c))
        
        return c, A, b, maximize
    
    @staticmethod
    def _get_optimization_type() -> bool:
        """Solicita el tipo de optimización al usuario."""
        while True:
            opt_type = input("¿Desea maximizar o minimizar? (max/min): ").lower().strip()
            if opt_type in ["max", "maximize", "maximizar"]:
                return True
            elif opt_type in ["min", "minimize", "minimizar"]:
                return False
            else:
                print("Por favor ingrese 'max' o 'min'")
    
    @staticmethod
    def _get_objective_function() -> List[float]:
        """Solicita la función objetivo al usuario."""
        while True:
            try:
                c_input = input("Coeficientes (separados por espacios): ")
                c = list(map(float, c_input.split()))
                if c:
                    return c
                print("Error: Debe ingresar al menos un coeficiente")
            except ValueError:
                print("Error: Ingrese números válidos separados por espacios")
    
    @staticmethod
    def _get_constraints(num_vars: int) -> Tuple[List[List[float]], List[float]]:
        """Solicita las restricciones al usuario."""
        print(f"\nIngrese las restricciones (formato: a1 a2 ... a{num_vars} <= b):")
        print("Escriba 'fin' cuando termine")
        
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
        
        return A, b
    
    @staticmethod
    def display_problem(c: List[float], A: List[List[float]], b: List[float], maximize: bool) -> None:
        """Muestra el problema formateado."""
        print("\n" + "=" * 50)
        print("PROBLEMA A RESOLVER:")
        print("=" * 50)
        
        obj_type = "Maximizar" if maximize else "Minimizar"
        print(f"{obj_type}: ", end="")
        
        # Mostrar función objetivo
        for i, coeff in enumerate(c):
            if i == 0:
                print(f"{coeff}x{i+1}", end="")
            else:
                sign = " + " if coeff >= 0 else " "
                print(f"{sign}{coeff}x{i+1}", end="")
        print()
        
        # Mostrar restricciones
        print("\nSujeto a:")
        for i, (row, rhs) in enumerate(zip(A, b)):
            print(f"  ", end="")
            for j, coeff in enumerate(row):
                if j == 0:
                    print(f"{coeff}x{j+1}", end="")
                else:
                    sign = " + " if coeff >= 0 else " "
                    print(f"{sign}{coeff}x{j+1}", end="")
            print(f" <= {rhs}")
        
        print("  xi >= 0 para todo i")
        print("=" * 50)
    
    @staticmethod
    def display_result(result: dict) -> None:
        """Muestra los resultados de la optimización."""
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