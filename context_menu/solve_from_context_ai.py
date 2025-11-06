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

try:
    # Importar módulos necesarios para la resolución con IA
    from simplex_solver.nlp import NLPConnectorFactory, NLPModelType
    from simplex_solver.reporting_pdf import generate_pdf
except ImportError as e:
    # Manejo de errores si los módulos no están disponibles
    print("=" * 70)
    print("ERROR: No se pudieron importar los módulos necesarios")
    print("=" * 70)
    print(f"Error: {e}")
    print("\nAsegúrese de que el proyecto está instalado correctamente.")
    input("\nPresione Enter para salir...")
    sys.exit(1)


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
        print(f"\nArchivo: {filepath}")
        print("\nLeyendo archivo y procesando con modelo de lenguaje natural...")

        # Leer el contenido del archivo
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        if not content.strip():
            # Validar que el archivo no esté vacío
            print("\nERROR: El archivo está vacío")
            input("\nPresione Enter para salir...")
            sys.exit(1)

        print("\nContenido del archivo:")
        print("-" * 70)
        print(content)  # Muestra el contenido del archivo para referencia.
        print("-" * 70)

        # Crear conector NLP
        print("\nConectando con modelo de IA...")
        try:
            connector = NLPConnectorFactory.create_connector(
                NLPModelType.LLAMA3_1_8B
            )  # Inicializa el modelo de IA.
        except Exception as e:
            # Manejo de errores al conectar con el modelo de IA
            print(f"\nERROR al conectar con el modelo de IA: {e}")
            print("\nAsegúrese de que:")
            print("  1. Ollama está instalado y ejecutándose.")
            print("  2. El modelo llama3.1:8b está descargado.")
            print("\nPuede verificar con: ollama list")
            print("Puede descargar el modelo con: ollama pull llama3.1:8b")
            input("\nPresione Enter para salir...")
            sys.exit(1)

        # Procesar y resolver con IA
        print("\nProcesando problema con IA...")
        result = connector.process_and_solve(
            content
        )  # Procesa el contenido del archivo con el modelo de IA.

        # Mostrar resultados
        print("\n" + "=" * 70)
        print("RESULTADOS")
        print("=" * 70)

        if result.get("success"):
            print("\nProblema resuelto exitosamente\n")

            if "message" in result and result["message"]:
                print(f"Mensaje: {result['message']}\n")

            solution = result.get("solution", {})

            if "optimal_value" in solution:
                print(f"Valor óptimo: {solution['optimal_value']}")

            if "variables" in solution and solution["variables"]:
                print("\nVariables:")
                for var_name, var_value in solution["variables"].items():
                    print(f"   {var_name} = {var_value}")

            if "problem_type" in solution:
                print(f"\nTipo de problema: {solution['problem_type']}")

            # Ofrecer generar PDF
            print("\n¿Desea generar un reporte en PDF?")
            respuesta = input("(S/N): ").strip().upper()

            if respuesta == "S":
                # Generar nombre del PDF basado en el archivo original
                filepath_obj = Path(filepath)
                pdf_name = filepath_obj.stem + "_solucion_ia.pdf"
                pdf_path = filepath_obj.parent / pdf_name

                print(f"\nGenerando PDF: {pdf_path}")
                try:
                    # Adaptar el resultado para generate_pdf
                    pdf_result = {
                        "status": "optimal",
                        "optimal_value": solution.get("optimal_value"),
                        "solution": solution.get("variables", {}),
                        "iterations": solution.get("iterations", 0),
                        "maximize": "maximiz" in solution.get("problem_type", "").lower(),
                    }
                    output_path = generate_pdf(pdf_result, str(pdf_path))
                    print(f"PDF generado exitosamente en: {output_path}")
                except Exception as e:
                    print(f"Error al generar PDF: {e}")

        else:
            # Manejo de errores si el problema no se pudo resolver
            print("\nNo se pudo resolver el problema\n")
            if "message" in result:
                print(f"Mensaje: {result['message']}")
            if "error" in result:
                print(f"Error: {result['error']}")

        print("=" * 70)
        print("\nProceso completado")

    except FileNotFoundError as e:
        # Manejo de errores si el archivo no existe
        print(f"\nERROR: No se encontró el archivo: {e}")
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
    solve_from_file_with_ai(filepath)  # Llama a la función principal para resolver el problema.
