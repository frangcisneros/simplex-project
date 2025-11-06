"""
Módulo para interacción con el usuario.
Contiene funciones para entrada interactiva y visualización de resultados.
"""

import sys
from typing import List, Tuple

# Importar el validador de entrada
from simplex_solver.input_validator import InputValidator


class UserInterface:
    """Clase que maneja la interacción con el usuario y la visualización de resultados."""

    @staticmethod
    def interactive_input() -> Tuple[List[float], List[List[float]], List[float], List[str], bool]:
        """
        Recoge la entrada del problema de forma interactiva.

        Retorna:
            Una tupla que contiene los coeficientes de la función objetivo, las restricciones,
            los valores del lado derecho, los tipos de restricciones y el tipo de optimización.
        """
        print("=== SIMPLEX SOLVER - Modo Interactivo ===\n")

        maximize = UserInterface._get_optimization_type()
        c = UserInterface._get_objective_function()
        A, b, constraint_types = UserInterface._get_constraints(len(c))

        # Validar el problema completo
        is_valid, error_msg = InputValidator.validate_problem(c, A, b, constraint_types, maximize)
        if not is_valid:
            print(f"\n ERROR EN ENTRADA: {error_msg}")
            print("Por favor, corrija los datos e intente nuevamente.")
            sys.exit(1)

        return c, A, b, constraint_types, maximize

    @staticmethod
    def _get_optimization_type() -> bool:
        """
        Solicita al usuario el tipo de optimización (maximizar o minimizar).

        Retorna:
            True si el usuario elige maximizar, False si elige minimizar.
        """
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
        """
        Solicita al usuario los coeficientes de la función objetivo.

        Retorna:
            Una lista de coeficientes de la función objetivo.
        """
        while True:
            try:
                c_input = input("Coeficientes de la función objetivo (separados por espacios): ")
                if not c_input.strip():
                    print("Error: Debe ingresar al menos un coeficiente")
                    continue

                c = list(map(float, c_input.split()))

                # Validación básica de la función objetivo
                if len(c) == 0:
                    print("Error: Debe ingresar al menos un coeficiente")
                    continue

                # Verificar que no todos los coeficientes sean cero
                if all(abs(coeff) < 1e-10 for coeff in c):
                    print("Error: Todos los coeficientes de la función objetivo son cero")
                    continue

                return c

            except ValueError:
                print("Error: Ingrese números válidos separados por espacios")
            except Exception as e:
                print(f"Error inesperado: {e}")

    @staticmethod
    def _get_constraints(
        num_vars: int,
    ) -> Tuple[List[List[float]], List[float], List[str]]:
        """
        Solicita al usuario las restricciones del problema.

        Parámetros:
            num_vars: Número de variables en el problema.

        Retorna:
            Una tupla que contiene las matrices de coeficientes, los valores del lado derecho
            y los tipos de restricciones.
        """
        print(f"\nIngrese las restricciones (formato: a1 a2 ... a{num_vars} [<=|>=|=] b):")
        print("Ejemplos: '2 1 <= 100' o '1 1 >= 20' o '1 0 = 5'")
        print("Escriba 'fin' cuando termine")

        A = []
        b = []
        constraint_types = []

        constraint_count = 0
        while True:
            constraint_count += 1
            constraint = input(f"Restricción {constraint_count}: ").strip()

            if constraint.lower() == "fin":
                if constraint_count == 1:
                    print("Error: Debe ingresar al menos una restricción")
                    continue
                break

            try:
                # Detectar tipo de restricción
                if "<=" in constraint:
                    parts = constraint.split("<=")
                    const_type = "<="
                elif ">=" in constraint:
                    parts = constraint.split(">=")
                    const_type = ">="
                elif "=" in constraint:
                    parts = constraint.split("=")
                    const_type = "="
                else:
                    print("Error: Use <=, >= o = en la restricción")
                    constraint_count -= 1
                    continue

                if len(parts) != 2:
                    print("Error: Formato inválido. Use 'a1 a2 ... <= b'")
                    constraint_count -= 1
                    continue

                # Limpiar y validar partes
                lhs_str = parts[0].strip()
                rhs_str = parts[1].strip()

                if not lhs_str or not rhs_str:
                    print("Error: Ambos lados de la restricción deben contener valores")
                    constraint_count -= 1
                    continue

                coeffs = list(map(float, lhs_str.split()))
                rhs = float(rhs_str)

                # Validar número de coeficientes
                if len(coeffs) != num_vars:
                    print(f"Error: Debe ingresar exactamente {num_vars} coeficientes")
                    constraint_count -= 1
                    continue

                # Validar que no todos los coeficientes sean cero
                if all(abs(coeff) < 1e-10 for coeff in coeffs):
                    print("Error: Todos los coeficientes de la restricción son cero")
                    constraint_count -= 1
                    continue

                # Validar RHS para restricciones de igualdad
                if const_type == "=" and rhs < 0:
                    print("Error: Las restricciones de igualdad no pueden tener RHS negativo")
                    constraint_count -= 1
                    continue

                A.append(coeffs)
                b.append(rhs)
                constraint_types.append(const_type)

                print(f"Restricción {constraint_count} agregada correctamente")

            except ValueError as e:
                print(f"Error: Formato inválido. Use números válidos. Detalles: {e}")
                constraint_count -= 1
            except Exception as e:
                print(f"Error inesperado: {e}")
                constraint_count -= 1

        return A, b, constraint_types

    @staticmethod
    def display_problem(
        c: List[float],
        A: List[List[float]],
        b: List[float],
        constraint_types: List[str],
        maximize: bool,
    ) -> None:
        """
        Muestra el problema de optimización en un formato legible.

        Parámetros:
            c: Coeficientes de la función objetivo.
            A: Matriz de coeficientes de las restricciones.
            b: Valores del lado derecho de las restricciones.
            constraint_types: Tipos de restricciones (<=, >=, =).
            maximize: True si el problema es de maximización, False si es de minimización.
        """
        print("\n" + "=" * 50)
        print("PROBLEMA A RESOLVER:")
        print("=" * 50)

        # Primero validar el problema antes de mostrar
        is_valid, error_msg = InputValidator.validate_problem(c, A, b, constraint_types, maximize)
        if not is_valid:
            print(f"PROBLEMA INVÁLIDO: {error_msg}")
            return

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
        for i, (row, rhs, const_type) in enumerate(zip(A, b, constraint_types)):
            print(f"  ", end="")
            for j, coeff in enumerate(row):
                if j == 0:
                    print(f"{coeff}x{j+1}", end="")
                else:
                    sign = " + " if coeff >= 0 else " "
                    print(f"{sign}{coeff}x{j+1}", end="")
            print(f" {const_type} {rhs}")

        print("  xi >= 0 para todo i")
        print("=" * 50)

    @staticmethod
    def display_result(result: dict) -> None:
        """
        Muestra los resultados de la optimización.

        Parámetros:
            result: Diccionario que contiene el estado y los resultados de la optimización.
        """
        print("\n" + "=" * 50)
        print("RESULTADO:")
        print("=" * 50)

        if result["status"] == "optimal":
            print("Estado: Solución óptima encontrada")
            print(f"Iteraciones: {result['iterations']}")
            if "phase1_iterations" in result:
                print(f"Iteraciones Fase 1: {result['phase1_iterations']}")
            print(f"Valor óptimo: {result['optimal_value']:.6f}")
            print("\n Solución:")
            for var, value in sorted(result["solution"].items()):
                print(f"  {var} = {value:.6f}")

            # Mostrar análisis de sensibilidad si está disponible
            if "sensitivity_analysis" in result and result["sensitivity_analysis"] is not None:
                UserInterface._display_sensitivity_analysis(result["sensitivity_analysis"])
        elif result["status"] == "infeasible":
            print("Estado: Problema no factible")
            print(f"Mensaje: {result['message']}")
        elif result["status"] == "unbounded":
            print("Estado: Problema no acotado")
            print(f"Mensaje: {result['message']}")
        else:
            print("Estado: Error en la resolución")
            print(f"Mensaje: {result['message']}")

        print("=" * 50)

    @staticmethod
    def _display_sensitivity_analysis(analysis: dict) -> None:
        """
        Muestra el análisis de sensibilidad de forma legible.

        Parámetros:
            analysis: Diccionario con el análisis de sensibilidad (precios sombra, rangos).
        """
        print("\n" + "=" * 50)
        print("ANÁLISIS DE SENSIBILIDAD:")
        print("=" * 50)

        # Precios Sombra
        if "shadow_prices" in analysis:
            print("\nPRECIOS SOMBRA (Valores Duales):")
            print("  (Cuánto cambia el valor óptimo por unidad adicional del recurso)")
            shadow_prices = analysis["shadow_prices"]
            for constraint, price in sorted(shadow_prices.items()):
                print(f"  {constraint}: {price:>10.6f}")

        # Rangos de Optimalidad
        if "optimality_ranges" in analysis:
            print("\nRANGOS DE OPTIMALIDAD:")
            print("  (Rangos donde los coeficientes de la F.O. mantienen la solución actual)")
            opt_ranges = analysis["optimality_ranges"]
            for var, (lower, upper) in sorted(opt_ranges.items()):
                if lower == float("-inf"):
                    lower_str = "-∞"
                else:
                    lower_str = f"{lower:.6f}"
                if upper == float("inf"):
                    upper_str = "+∞"
                else:
                    upper_str = f"{upper:.6f}"
                print(f"  {var}: [{lower_str}, {upper_str}]")

        # Rangos de Factibilidad
        if "feasibility_ranges" in analysis:
            print("\nRANGOS DE FACTIBILIDAD:")
            print("  (Rangos donde los valores RHS mantienen la misma base óptima)")
            feas_ranges = analysis["feasibility_ranges"]
            for constraint, (lower, upper) in sorted(feas_ranges.items()):
                if lower == float("-inf"):
                    lower_str = "-∞"
                else:
                    lower_str = f"{lower:.6f}"
                if upper == float("inf"):
                    upper_str = "+∞"
                else:
                    upper_str = f"{upper:.6f}"
                print(f"  {constraint}: [{lower_str}, {upper_str}]")

        print("=" * 50)
