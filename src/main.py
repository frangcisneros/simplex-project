"""
Simplex Solver - Programa principal.
Coordina los módulos para resolver problemas de programación lineal.
"""

import sys
import argparse
from solver import SimplexSolver
from file_parser import FileParser
from user_interface import UserInterface
from input_validator import InputValidator  # Nuevo import


def main():
    """Función principal del programa."""
    parser = create_parser()
    args = parser.parse_args()
    
    try:
        # Obtener datos del problema
        if args.filename:
            print(f"=== SIMPLEX SOLVER - Resolviendo archivo: {args.filename} ===\n")
            c, A, b, constraint_types, maximize = FileParser.parse_file(args.filename)
        elif args.interactive or len(sys.argv) == 1:
            c, A, b, constraint_types, maximize = UserInterface.interactive_input()
        else:
            parser.print_help()
            sys.exit(1)
        
        # Validar el problema antes de resolver
        print("\n🔍 Validando problema...")
        is_valid, error_msg = InputValidator.validate_problem(c, A, b, constraint_types, maximize)
        if not is_valid:
            print(f"❌ ERROR: {error_msg}")
            print("El problema no puede ser resuelto. Por favor, corrija los datos.")
            sys.exit(1)
        print("✅ Problema validado correctamente")
        
        # Mostrar problema
        UserInterface.display_problem(c, A, b, constraint_types, maximize)
        
        # Resolver problema
        print("\n⚙️ Resolviendo problema...")
        solver = SimplexSolver()
        result = solver.solve(c, A, b, constraint_types, maximize)
        
        # Validar la solución si es óptima
        if result["status"] == "optimal":
            print("\n🔍 Validando factibilidad de la solución...")
            is_feasible, errors = InputValidator.validate_solution_feasibility(
                result["solution"], A, b, constraint_types
            )
            if not is_feasible:
                print("⚠️ ADVERTENCIA: La solución podría no ser factible:")
                for error in errors:
                    print(f"   - {error}")
            else:
                print("✅ Solución validada como factible")
        
        # Mostrar resultados
        UserInterface.display_result(result)
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        print("El programa se ha detenido debido a un error.")
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