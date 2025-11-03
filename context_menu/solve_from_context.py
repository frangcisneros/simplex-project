#!/usr/bin/env python3
"""
Script para resolver problemas de Simplex desde el menú contextual de Windows.
Este script se ejecuta cuando el usuario hace clic derecho en un archivo .txt.
"""

import sys
import os
from pathlib import Path

# Obtener el directorio raíz del proyecto (parent de context_menu)
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from simplex_solver.solver import SimplexSolver
from simplex_solver.file_parser import FileParser
from simplex_solver.user_interface import UserInterface
from simplex_solver.input_validator import InputValidator
from simplex_solver.reporting_pdf import generate_pdf


def solve_from_file(filepath):
    """
    Resuelve un problema de Simplex desde un archivo.

    Args:
        filepath: Ruta completa al archivo .txt con el problema
    """
    try:
        print("=" * 70)
        print(f"SIMPLEX SOLVER - Menú Contextual")
        print("=" * 70)
        print(f"\nArchivo: {filepath}")
        print(f"\nLeyendo y validando problema...")

        # Parsear archivo
        c, A, b, constraint_types, maximize = FileParser.parse_file(filepath)

        # Validar el problema
        is_valid, error_msg = InputValidator.validate_problem(c, A, b, constraint_types, maximize)
        if not is_valid:
            print(f"\n❌ ERROR: {error_msg}")
            print("El problema no puede ser resuelto. Por favor, corrija los datos.")
            input("\nPresione Enter para salir...")
            sys.exit(1)

        print("✓ Problema validado correctamente")

        # Mostrar problema
        print("\n" + "=" * 70)
        UserInterface.display_problem(c, A, b, constraint_types, maximize)
        print("=" * 70)

        # Resolver problema
        print("\n🔄 Resolviendo problema...")
        solver = SimplexSolver()
        result = solver.solve(c, A, b, constraint_types, maximize)

        # Adjuntar datos útiles al resultado
        result.setdefault("c", c)
        result.setdefault("A", A)
        result.setdefault("b", b)
        result.setdefault("constraint_types", constraint_types)
        result.setdefault("maximize", maximize)

        # Validar la solución si es óptima
        if result.get("status") == "optimal":
            is_feasible, errors = InputValidator.validate_solution_feasibility(
                result["solution"], A, b, constraint_types
            )
            if not is_feasible:
                print("\n⚠️  ADVERTENCIA: La solución podría no ser factible:")
                for error in errors:
                    print(f"   - {error}")
            else:
                print("\n✓ Solución validada como factible")

        # Mostrar resultados
        print("\n" + "=" * 70)
        print("RESULTADOS")
        print("=" * 70)
        UserInterface.display_result(result)
        print("=" * 70)

        # Ofrecer generar PDF
        if result.get("status") == "optimal":
            print("\n¿Desea generar un reporte en PDF?")
            respuesta = input("(S/N): ").strip().upper()

            if respuesta == "S":
                # Generar nombre del PDF basado en el archivo original
                filepath_obj = Path(filepath)
                pdf_name = filepath_obj.stem + "_solucion.pdf"
                pdf_path = filepath_obj.parent / pdf_name

                print(f"\n📄 Generando PDF: {pdf_path}")
                output_path = generate_pdf(result, str(pdf_path))
                print(f"✓ PDF generado exitosamente en: {output_path}")

        print("\n✓ Proceso completado")

    except FileNotFoundError as e:
        print(f"\n❌ ERROR: No se encontró el archivo: {e}")
        input("\nPresione Enter para salir...")
        sys.exit(1)
    except ValueError as e:
        print(f"\n❌ ERROR en el formato del archivo: {e}")
        input("\nPresione Enter para salir...")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR inesperado: {e}")
        import traceback

        traceback.print_exc()
        input("\nPresione Enter para salir...")
        sys.exit(1)

    # Pausa para que el usuario pueda ver los resultados
    input("\nPresione Enter para salir...")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("❌ ERROR: No se proporcionó un archivo.")
        print("Este script debe ejecutarse con un archivo como argumento.")
        input("\nPresione Enter para salir...")
        sys.exit(1)

    filepath = sys.argv[1]
    solve_from_file(filepath)
