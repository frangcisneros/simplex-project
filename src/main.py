#!/usr/bin/env python3
"""
Simplex Solver - Programa principal.
Coordina los módulos para resolver problemas de programación lineal.
"""

import sys
import argparse
from solver import SimplexSolver
from file_parser import FileParser
from user_interface import UserInterface


def main():
    """Función principal del programa."""
    parser = create_parser()
    args = parser.parse_args()
    
    try:
        # Obtener datos del problema
        if args.filename:
            c, A, b, constraint_types, maximize = FileParser.parse_file(args.filename)
            print(f"=== SIMPLEX SOLVER - Resolviendo archivo: {args.filename} ===\n")
        elif args.interactive or len(sys.argv) == 1:
            c, A, b, constraint_types, maximize = UserInterface.interactive_input()
        else:
            parser.print_help()
            sys.exit(1)
        
        # Mostrar problema
        UserInterface.display_problem(c, A, b, constraint_types, maximize)
        
        # Resolver problema
        solver = SimplexSolver()
        result = solver.solve(c, A, b, constraint_types, maximize)
        
        # Mostrar resultados
        UserInterface.display_result(result)
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


def create_parser() -> argparse.ArgumentParser:
    """Crea y configura el parser de argumentos de línea de comandos."""
    parser = argparse.ArgumentParser(
        description="Simplex Solver - Resuelve problemas de programación lineal"
    )
    parser.add_argument(
        "filename", nargs="?", help="Archivo con el problema a resolver"
    )
    parser.add_argument(
        "--interactive", "-i", action="store_true", help="Modo interactivo"
    )
    return parser


if __name__ == "__main__":
    main()