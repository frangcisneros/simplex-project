"""
Script principal que integra NLP con el solver simplex existente.
Proporciona interfaz de línea de comandos para usar el pipeline completo.
"""

import sys
import argparse
import logging
import json
from pathlib import Path

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from nlp import (
    NLPConnectorFactory,
    ConfigurableNLPConnector,
    SolverType,
    NLPModelType,
    DefaultSettings,
)
from solver import main as original_main


def setup_logging(verbose: bool = False):
    """Configura logging para la aplicación."""
    level = logging.DEBUG if verbose else logging.INFO

    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%H:%M:%S",
    )

    # Reducir verbosidad de transformers si no está en modo debug
    if not verbose:
        logging.getLogger("transformers").setLevel(logging.ERROR)
        logging.getLogger("torch").setLevel(logging.ERROR)


def nlp_mode(args):
    """Modo NLP: procesa texto en lenguaje natural."""
    print("=== SIMPLEX SOLVER - Modo NLP ===\n")

    setup_logging(args.verbose)
    logger = logging.getLogger(__name__)

    try:
        # Crear conector
        logger.info("Inicializando conector NLP...")

        # Mapear nombre del modelo a NLPModelType
        model_map = {
            "llama3.1:8b": NLPModelType.LLAMA3_1_8B,
            "qwen2.5:14b": NLPModelType.QWEN2_5_14B,
            "mistral:7b": NLPModelType.MISTRAL_7B,
        }

        selected_model = model_map.get(args.model, NLPModelType.QWEN2_5_14B)

        print(f"Usando modelo: {args.model}")
        if args.model == "qwen2.5:14b":
            print(
                "  (Especializado en matemáticas - recomendado para problemas complejos)"
            )

        connector = NLPConnectorFactory.create_connector(
            solver_type=SolverType.SIMPLEX,
            use_mock_nlp=args.mock_nlp,
            nlp_model_type=selected_model,
        )

        # Verificar estado del conector
        health = connector.health_check()
        print(f"Estado del conector: {health['overall_status']}")

        if health["overall_status"] == "unhealthy":
            print("Error: El conector NLP no está funcionando correctamente.")
            if args.verbose:
                print("Detalles:", json.dumps(health, indent=2))
            return

        # Obtener texto del problema
        if args.text:
            problem_text = args.text
        elif args.file:
            try:
                with open(args.file, "r", encoding="utf-8") as f:
                    problem_text = f.read().strip()
            except FileNotFoundError:
                print(f"Error: No se encontró el archivo {args.file}")
                return
        else:
            print("Ingrese la descripción del problema de optimización:")
            print(
                "(Puede usar múltiples líneas, termine con Ctrl+D en Unix o Ctrl+Z en Windows)"
            )
            problem_text = sys.stdin.read().strip()

        if not problem_text:
            print("Error: No se proporcionó texto del problema.")
            return

        print("\n" + "=" * 60)
        print("PROBLEMA A PROCESAR:")
        print("=" * 60)
        print(problem_text)
        print("=" * 60)

        # Procesar con NLP
        print("\nProcesando con NLP...")
        result = connector.process_and_solve(problem_text)

        # Mostrar resultados
        print("\n" + "=" * 60)
        print("RESULTADO:")
        print("=" * 60)

        if result["success"]:
            print("✓ Procesamiento exitoso!")

            # Mostrar análisis de estructura
            if "structure_analysis" in result:
                struct = result["structure_analysis"]
                print(f"\nAnálisis de estructura del problema:")
                print(f"  Tipo detectado: {struct['detected_type']}")
                print(
                    f"  Variables: extraídas={struct['extracted_variables']}, "
                    f"esperadas={struct['expected_variables']}"
                )

                if not struct["structure_valid"]:
                    print("\n⚠️ ADVERTENCIAS DE ESTRUCTURA:")
                    for warning in struct["warnings"]:
                        print(f"  - {warning}")
                    print(
                        "\nNOTA: El sistema intentó resolver con las variables extraídas."
                    )
                else:
                    print("  ✓ Estructura válida")

            # Mostrar problema extraído
            if args.verbose and "extracted_problem" in result:
                problem = result["extracted_problem"]
                print(f"\nProblema extraído:")
                print(f"  Tipo: {problem['objective_type']}")
                print(f"  Coeficientes objetivo: {problem['objective_coefficients']}")
                print(f"  Restricciones: {len(problem['constraints'])}")
                if problem.get("variable_names"):
                    print(f"  Variables: {problem['variable_names']}")

            # Mostrar solución
            solution = result["solution"]
            if solution.get("status") == "optimal":
                print(f"\nSolución óptima encontrada:")
                print(f"  Valor óptimo: {solution['optimal_value']:.4f}")
                print(f"  Iteraciones: {solution.get('iterations', 'N/A')}")

                print("\nVariables:")
                if "named_solution" in solution:
                    for var, value in solution["named_solution"].items():
                        print(f"  {var} = {value:.4f}")
                else:
                    for var, value in solution["solution"].items():
                        print(f"  {var} = {value:.4f}")
            else:
                print(f"\nEstado: {solution.get('status', 'error')}")
                print(f"Mensaje: {solution.get('message', 'Sin mensaje')}")

            # Información adicional
            if args.verbose:
                print(f"\nInformación adicional:")
                print(f"  Confianza NLP: {result.get('nlp_confidence', 'N/A')}")
                print(f"  Tiempo total: {result.get('processing_time', 0):.2f}s")

                if "pipeline_steps" in result:
                    print("  Pasos del pipeline:")
                    for step, status in result["pipeline_steps"].items():
                        print(f"    {step}: {status}")

        else:
            print("✗ Error en el procesamiento")
            print(f"Error: {result.get('error', 'Error desconocido')}")
            print(f"Paso fallido: {result.get('step_failed', 'Desconocido')}")

            if "validation_errors" in result:
                print("\nErrores de validación:")
                for error in result["validation_errors"]:
                    print(f"  - {error}")

            if "structure_warnings" in result and result["structure_warnings"]:
                print("\nAdvertencias de estructura:")
                for warning in result["structure_warnings"]:
                    print(f"  - {warning}")

    except KeyboardInterrupt:
        print("\n\nProcesamiento cancelado por el usuario.")
    except Exception as e:
        logger.error(f"Error inesperado: {e}")
        print(f"\nError inesperado: {e}")
        if args.verbose:
            import traceback

            traceback.print_exc()


def detect_file_format(filename):
    """
    Detecta si un archivo es formato clásico de Simplex o lenguaje natural.

    Returns:
        'classic' si es formato MAXIMIZE/MINIMIZE
        'nlp' si es lenguaje natural
    """
    try:
        with open(filename, "r", encoding="utf-8") as f:
            first_line = f.readline().strip().upper()
            # Si empieza con MAXIMIZE o MINIMIZE, es formato clásico
            if first_line in ["MAXIMIZE", "MINIMIZE"]:
                return "classic"
            # Caso especial: archivos en carpeta nlp/ son siempre lenguaje natural
            if "nlp" in str(Path(filename).parts):
                return "nlp"
            # Si la primera línea es larga (>50 caracteres), probablemente es lenguaje natural
            if len(first_line) > 50:
                return "nlp"
            # Por defecto, asumir lenguaje natural si no parece formato clásico
            return "nlp"
    except Exception:
        return "nlp"  # En caso de error, asumir lenguaje natural


def main():
    parser = argparse.ArgumentParser(
        description="Simplex Solver con capacidades NLP",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:

  # Modo automático - detecta el formato del archivo
  python nlp_simplex.py ejemplos/nlp/problema_complejo.txt
  python nlp_simplex.py ejemplos/maximizar_basico.txt

  # Modo NLP con texto directo
  python nlp_simplex.py --text "Maximizar 2x + 3y sujeto a x + y <= 10"
  
  # Modo NLP explícito con archivo
  python nlp_simplex.py --nlp --file problema.txt
  
  # Modo NLP interactivo
  python nlp_simplex.py --nlp
  
  # Modo de prueba (mock NLP)
  python nlp_simplex.py --nlp --mock --text "cualquier texto"
  
  # Modo tradicional (formato clásico)
  python nlp_simplex.py --classic archivo.txt
        """,
    )

    # Argumentos para modo tradicional
    parser.add_argument(
        "filename",
        nargs="?",
        help="Archivo con el problema (detección automática de formato)",
    )
    parser.add_argument(
        "--interactive", "-i", action="store_true", help="Modo interactivo tradicional"
    )

    # Argumentos para modo NLP
    parser.add_argument(
        "--nlp", action="store_true", help="Forzar modo NLP (lenguaje natural)"
    )
    parser.add_argument("--text", "-t", type=str, help="Texto del problema (modo NLP)")
    parser.add_argument(
        "--file", "-f", type=str, help="Archivo con texto del problema (modo NLP)"
    )
    parser.add_argument(
        "--mock-nlp", "--mock", action="store_true", help="Usar NLP mock para pruebas"
    )
    parser.add_argument(
        "--model",
        "-m",
        type=str,
        choices=["llama3.1:8b", "qwen2.5:14b", "mistral:7b"],
        default="qwen2.5:14b",
        help="Modelo de IA a usar (default: qwen2.5:14b, mejor para matemáticas)",
    )

    # Argumento para forzar modo clásico
    parser.add_argument(
        "--classic",
        "-c",
        action="store_true",
        help="Forzar modo clásico (MAXIMIZE/MINIMIZE)",
    )

    # Argumentos generales
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Modo verboso (más información)"
    )

    args = parser.parse_args()

    # Determinar modo de operación
    if args.nlp or args.text or args.file or args.mock_nlp:
        # Modo NLP explícito
        nlp_mode(args)
    elif args.classic:
        # Modo clásico forzado
        original_main()
    elif args.filename:
        # Detectar automáticamente el formato del archivo
        file_format = detect_file_format(args.filename)

        if file_format == "nlp":
            # Archivo de lenguaje natural - usar modo NLP
            print(f"=== SIMPLEX SOLVER - Detectado: Lenguaje Natural ===")
            print(f"Archivo: {args.filename}\n")
            # Crear args equivalentes para nlp_mode
            args.file = args.filename
            nlp_mode(args)
        else:
            # Archivo formato clásico - usar solver original
            print(f"=== SIMPLEX SOLVER - Detectado: Formato Clásico ===")
            print(f"Archivo: {args.filename}\n")
            original_main()
    elif args.interactive or len(sys.argv) == 1:
        # Modo tradicional - usar solver original
        original_main()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
