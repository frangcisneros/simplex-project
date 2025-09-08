#!/usr/bin/env python3
"""
Simplex Solver - Resuelve problemas de programación lineal usando el método simplex.
"""

import sys
import argparse
import numpy as np
from typing import List, Tuple, Optional, Dict, Any


class SimplexSolver:
    """Implementación del método simplex para resolver problemas de programación lineal."""

    def __init__(self):
        self.tableau: Optional[np.ndarray] = None
        self.variables: List[str] = []
        self.solution: Dict[str, float] = {}

    def solve(
        self,
        c: List[float],
        A: List[List[float]],
        b: List[float],
        maximize: bool = True,
    ) -> Dict[str, Any]:
        """
        Resuelve un problema de programación lineal usando el método simplex.

        Args:
            c: Coeficientes de la función objetivo
            A: Matriz de coeficientes de las restricciones
            b: Vector de términos independientes
            maximize: True para maximizar, False para minimizar

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
        while True:
            iteration += 1
            print(f"\n--- Iteración {iteration} ---")

            # Verificar si la solución es óptima
            if maximize:
                optimal_condition = np.all(self.tableau[-1, :-1] >= 0)
                entering_col = int(np.argmin(self.tableau[-1, :-1]))
            else:
                optimal_condition = np.all(self.tableau[-1, :-1] <= 0)
                entering_col = int(np.argmax(self.tableau[-1, :-1]))

            if optimal_condition:
                print("Solución óptima encontrada!")
                break

            # Variable que entra ya fue calculada arriba

            # Verificar si el problema es no acotado
            if np.all(self.tableau[:-1, entering_col] <= 0):
                return {"status": "unbounded", "message": "El problema es no acotado"}

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

            # Actualizar variables básicas
            basic_vars[leaving_row] = entering_col

            # Operaciones de pivoteo
            self.tableau[leaving_row] /= pivot

            for i in range(m + 1):
                if i != leaving_row:
                    self.tableau[i] -= (
                        self.tableau[i, entering_col] * self.tableau[leaving_row]
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
            "status": "optimal",
            "solution": solution,
            "optimal_value": optimal_value,
            "iterations": iteration,
        }

    def _print_tableau(self):
        """Imprime el tableau actual de forma legible."""
        if self.tableau is not None:
            print("Tableau:")
            for row in self.tableau:
                print("  " + "  ".join(f"{val:8.2f}" for val in row))
            print()


def parse_file(
    filename: str,
) -> Tuple[List[float], List[List[float]], List[float], bool]:
    """
    Lee un archivo con el formato del problema de programación lineal.

    Formato esperado:
    MAXIMIZE (o MINIMIZE)
    c1 c2 c3 ... (coeficientes de la función objetivo)
    SUBJECT TO
    a11 a12 a13 ... <= b1
    a21 a22 a23 ... <= b2
    ...
    """
    try:
        with open(filename, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f.readlines() if line.strip()]

        maximize = True
        if lines[0].upper() == "MINIMIZE":
            maximize = False
        elif lines[0].upper() != "MAXIMIZE":
            raise ValueError("Primera línea debe ser MAXIMIZE o MINIMIZE")

        # Coeficientes de la función objetivo
        c = list(map(float, lines[1].split()))

        # Buscar "SUBJECT TO"
        subject_to_idx = -1
        for i, line in enumerate(lines):
            if "SUBJECT TO" in line.upper():
                subject_to_idx = i
                break

        if subject_to_idx == -1:
            raise ValueError("No se encontró 'SUBJECT TO'")

        # Leer restricciones
        A = []
        b = []

        for line in lines[subject_to_idx + 1 :]:
            if "<=" in line:
                parts = line.split("<=")
                coeffs = list(map(float, parts[0].split()))
                rhs = float(parts[1])
                A.append(coeffs)
                b.append(rhs)
            else:
                print(
                    f"Advertencia: línea ignorada (solo se soportan restricciones <=): {line}"
                )

        return c, A, b, maximize

    except FileNotFoundError:
        print(f"Error: No se pudo encontrar el archivo {filename}")
        sys.exit(1)
    except Exception as e:
        print(f"Error al leer el archivo: {e}")
        sys.exit(1)


def interactive_input() -> Tuple[List[float], List[List[float]], List[float], bool]:
    """Modo interactivo para ingresar el problema."""
    print("=== SIMPLEX SOLVER - Modo Interactivo ===\n")

    # Tipo de optimización
    while True:
        opt_type = input("¿Desea maximizar o minimizar? (max/min): ").lower().strip()
        if opt_type in ["max", "maximize", "maximizar"]:
            maximize = True
            break
        elif opt_type in ["min", "minimize", "minimizar"]:
            maximize = False
            break
        else:
            print("Por favor ingrese 'max' o 'min'")

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
