"""
Módulo para interacción con el usuario.
Contiene funciones para entrada interactiva y visualización de resultados.
"""

import sys
from typing import List, Tuple

# Agregar import del validador

from src.input_validator import InputValidator


class UserInterface:
    """Maneja la interacción con el usuario y visualización de resultados."""

    @staticmethod
    def interactive_input() -> (
        Tuple[List[float], List[List[float]], List[float], List[str], bool]
    ):
        """Recoge entrada del problema de forma interactiva."""
        print("=== SIMPLEX SOLVER - Modo Interactivo ===\n")

        maximize = UserInterface._get_optimization_type()
        c = UserInterface._get_objective_function()
        A, b, constraint_types = UserInterface._get_constraints(len(c))

        # Validar el problema completo
        is_valid, error_msg = InputValidator.validate_problem(
            c, A, b, constraint_types, maximize
        )
        if not is_valid:
            print(f"\n ERROR EN ENTRADA: {error_msg}")
            print("Por favor, corrija los datos e intente nuevamente.")
            sys.exit(1)

        return c, A, b, constraint_types, maximize

    @staticmethod
    def _get_optimization_type() -> bool:
        """Solicita el tipo de optimización al usuario."""
        while True:
            opt_type = (
                input("¿Desea maximizar o minimizar? (max/min): ").lower().strip()
            )
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
                c_input = input(
                    "Coeficientes de la función objetivo (separados por espacios): "
                )
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
                    print(
                        "Error: Todos los coeficientes de la función objetivo son cero"
                    )
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
        """Solicita las restricciones al usuario."""
        print(
            f"\nIngrese las restricciones (formato: a1 a2 ... a{num_vars} [<=|>=|=] b):"
        )
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
                    print(
                        "Error: Las restricciones de igualdad no pueden tener RHS negativo"
                    )
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
        """Muestra el problema formateado."""
        print("\n" + "=" * 50)
        print("PROBLEMA A RESOLVER:")
        print("=" * 50)

        # Primero validar el problema antes de mostrar
        is_valid, error_msg = InputValidator.validate_problem(
            c, A, b, constraint_types, maximize
        )
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
        """Muestra los resultados de la optimización."""
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
        elif result["status"] == "infeasible":
            print("Estado: Problema no factible")
            print(f"Mensaje: {result['message']}")
        elif result["status"] == "unbounded":
            print("Estado: Problema no acotado")
            print(f"Mensaje: {result['message']}")
        else:
            print("Estado: Error en la resolución")
            print(f"Mensaje: {result['message']}")
