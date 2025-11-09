#!/usr/bin/env python3
"""
Script para resolver problemas de Simplex desde el menú contextual de Windows.
Este script se ejecuta cuando el usuario hace clic derecho en un archivo .txt.
"""

import sys
import os
from pathlib import Path

# Obtener el directorio raíz del proyecto (parent de context_menu)
PROJECT_ROOT = Path(__file__).parent.parent  # Calcula la ruta del directorio raíz del proyecto.
sys.path.insert(
    0, str(PROJECT_ROOT)
)  # Agrega el directorio raíz al PATH para importar módulos personalizados.

# Importar módulos necesarios del proyecto
from simplex_solver.solver import SimplexSolver
from simplex_solver.file_parser import FileParser
from simplex_solver.user_interface import UserInterface
from simplex_solver.input_validator import InputValidator
from simplex_solver.reporting_pdf import generate_pdf


def solve_from_file(filepath):
    """
    Resuelve un problema de Simplex desde un archivo.

    Args:
        filepath: Ruta completa al archivo .txt con el problema.
    """
    try:
        print("=" * 70)
        print(f"SIMPLEX SOLVER - Menú Contextual")
        print("=" * 70)
        print(f"\nArchivo: {filepath}")
        print(f"\nLeyendo y validando problema...")

        # Parsear archivo
        c, A, b, constraint_types, maximize = FileParser.parse_file(
            filepath
        )  # Extrae los datos del problema desde el archivo.

        # Validar el problema
        is_valid, error_msg = InputValidator.validate_problem(
            c, A, b, constraint_types, maximize
        )  # Verifica que el problema sea válido.
        if not is_valid:
            print(f"\nERROR: {error_msg}")
            print("El problema no puede ser resuelto. Por favor, corrija los datos.")
            input("\nPresione Enter para salir...")
            sys.exit(1)

        print("Problema validado correctamente")

        # Mostrar problema
        print("\n" + "=" * 70)
        UserInterface.display_problem(
            c, A, b, constraint_types, maximize
        )  # Muestra el problema en un formato legible.
        print("=" * 70)

        # Resolver problema
        print("\nResolviendo problema...")
        solver = SimplexSolver()  # Instancia el solver de Simplex.
        result = solver.solve(c, A, b, constraint_types, maximize)  # Resuelve el problema.

        # Adjuntar datos útiles al resultado
        result.setdefault("c", c)  # Agrega el vector de costos al resultado si no está presente.
        result.setdefault(
            "A", A
        )  # Agrega la matriz de restricciones al resultado si no está presente.
        result.setdefault("b", b)  # Agrega el vector de recursos al resultado si no está presente.
        result.setdefault(
            "constraint_types", constraint_types
        )  # Agrega los tipos de restricciones al resultado si no están presentes.
        result.setdefault(
            "maximize", maximize
        )  # Agrega el tipo de optimización (maximizar/minimizar) al resultado si no está presente.

        # Validar la solución si es óptima
        if result.get("status") == "optimal":
            is_feasible, errors = InputValidator.validate_solution_feasibility(
                result["solution"], A, b, constraint_types
            )  # Verifica que la solución sea factible.
            if not is_feasible:
                print("\nADVERTENCIA: La solución podría no ser factible:")
                for error in errors:
                    print(f"   - {error}")
            else:
                print("\nSolución validada como factible")

        # Mostrar resultados
        print("\n" + "=" * 70)
        print("RESULTADOS")
        print("=" * 70)
        UserInterface.display_result(result)  # Muestra los resultados de la solución.
        print("=" * 70)

        # Ofrecer generar PDF
        if result.get("status") == "optimal":
            print("\n¿Desea generar un reporte en PDF?")
            respuesta = input("(S/N): ").strip().upper()

            if respuesta == "S":
                # Generar nombre del PDF basado en el archivo original
                filepath_obj = Path(filepath)
                pdf_name = (
                    filepath_obj.stem + "_solucion.pdf"
                )  # Genera un nombre para el archivo PDF.
                pdf_path = filepath_obj.parent / pdf_name

                print(f"\nGenerando PDF: {pdf_path}")
                output_path = generate_pdf(
                    result, str(pdf_path)
                )  # Genera el archivo PDF con los resultados.
                print(f"PDF generado exitosamente en: {output_path}")

        print("\nProceso completado")

    except FileNotFoundError as e:
        # Manejo de errores si el archivo no existe
        print(f"\nERROR: No se encontró el archivo: {e}")
        input("\nPresione Enter para salir...")
        sys.exit(1)
    except ValueError as e:
        # Manejo de errores si el archivo tiene un formato incorrecto
        print(f"\nERROR en el formato del archivo: {e}")
        input("\nPresione Enter para salir...")
        sys.exit(1)
    except Exception as e:
        # Manejo de errores inesperados
        print(f"\nERROR inesperado: {e}")
        import traceback

        traceback.print_exc()  # Muestra el stack trace del error para depuración.
        input("\nPresione Enter para salir...")
        sys.exit(1)

    # Pausa para que el usuario pueda ver los resultados
    input("\nPresione Enter para salir...")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        # Validar que se pase un archivo como argumento
        print("ERROR: No se proporcionó un archivo.")
        print("Este script debe ejecutarse con un archivo como argumento.")
        input("\nPresione Enter para salir...")
        sys.exit(1)

    filepath = sys.argv[
        1
    ]  # Obtiene la ruta del archivo desde los argumentos de la línea de comandos.
    solve_from_file(filepath)  # Llama a la función principal para resolver el problema.
