#!/usr/bin/env python3
"""
Script para resolver problemas de Simplex con IA desde el menú contextual de Windows.
Este script se ejecuta cuando el usuario hace clic derecho en un archivo .txt y selecciona la opción de IA.
"""

import sys
import os
from pathlib import Path

# Obtener el directorio raíz del proyecto (padre de context_menu)
PROJECT_ROOT = Path(__file__).parent.parent  # Calcula la ruta del directorio raíz del proyecto.
sys.path.insert(
    0, str(PROJECT_ROOT)
)  # Agrega el directorio raíz al PATH para importar módulos personalizados.


def solve_from_file_with_ai(filepath):
    """
    Resuelve un problema de Simplex desde un archivo usando IA/NLP.

    Args:
        filepath: Ruta completa al archivo .txt con el problema.
    """
    try:
        print("=" * 70)
        print("SIMPLEX SOLVER - Resolución con IA")
        print("=" * 70)
        print(f"\nArchivo: {filepath}\n")

        # Importar módulos necesarios
        from simplex_solver.main import ApplicationOrchestrator, create_parser

        # Ofrecer generar PDF antes de resolver
        print("¿Desea generar un reporte en PDF al finalizar?")
        respuesta = input("(S/N): ").strip().upper()
        generate_pdf = respuesta == "S"

        # Construir argumentos para el solver
        args = ["--nlp", filepath]

        if generate_pdf:
            # Generar nombre del PDF basado en el archivo original
            filepath_obj = Path(filepath)
            pdf_name = filepath_obj.stem + "_solucion_ia.pdf"
            args.extend(["--pdf", pdf_name])
            print(f"\nSe generará el PDF: {pdf_name}")

        # Crear parser y procesar argumentos
        parser = create_parser()
        parsed_args = parser.parse_args(args)

        # Ejecutar el flujo completo con el orquestador
        print("\n" + "=" * 70)
        orchestrator = ApplicationOrchestrator()
        orchestrator.run(parsed_args)

        print("\n" + "=" * 70)
        print("Proceso completado exitosamente")
        print("=" * 70)

    except FileNotFoundError as e:
        # Manejo de errores si el archivo no existe
        print(f"\nERROR: No se encontró el archivo: {e}")
        input("\nPresione Enter para salir...")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\nProceso interrumpido por el usuario")
        input("\nPresione Enter para salir...")
        sys.exit(0)
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
    solve_from_file_with_ai(filepath)  # Llama a la función principal para resolver el problema.
