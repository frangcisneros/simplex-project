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
        logging.getLogger("transformers").setLevel(logging.WARNING)
        logging.getLogger("torch").setLevel(logging.WARNING)


def nlp_mode(args):
    """Modo NLP: procesa texto en lenguaje natural."""
    print("=== SIMPLEX SOLVER - Modo NLP ===\n")

    setup_logging(args.verbose)
    logger = logging.getLogger(__name__)

    try:
        # Crear conector
        logger.info("Inicializando conector NLP...")

        # Seleccionar modelo según argumentos
        model_type = NLPModelType.FLAN_T5_SMALL  # Por defecto
        if args.model:
            model_map = {
                "t5-small": NLPModelType.FLAN_T5_SMALL,
                "t5-base": NLPModelType.FLAN_T5_BASE,
                "mistral": NLPModelType.MISTRAL_7B,
                "llama2": NLPModelType.LLAMA2_7B,
            }
            model_type = model_map.get(args.model, NLPModelType.FLAN_T5_SMALL)

        connector = NLPConnectorFactory.create_connector(
            nlp_model_type=model_type,
            solver_type=SolverType.SIMPLEX,
            use_mock_nlp=args.mock_nlp,
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

    except KeyboardInterrupt:
        print("\n\nProcesamiento cancelado por el usuario.")
    except Exception as e:
        logger.error(f"Error inesperado: {e}")
        print(f"\nError inesperado: {e}")
        if args.verbose:
            import traceback

            traceback.print_exc()


def main():
    parser = argparse.ArgumentParser(
        description="Simplex Solver con capacidades NLP",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:

  # Modo tradicional (archivos)
  python nlp_simplex.py archivo.txt

  # Modo NLP con texto directo
  python nlp_simplex.py --nlp --text "Maximizar 2x + 3y sujeto a x + y <= 10"
  
  # Modo NLP con archivo de texto
  python nlp_simplex.py --nlp --file problema.txt
  
  # Modo NLP interactivo
  python nlp_simplex.py --nlp
  
  # Usar modelo específico
  python nlp_simplex.py --nlp --model t5-base --text "..."
  
  # Modo de prueba (mock NLP)
  python nlp_simplex.py --nlp --mock --text "cualquier texto"
        """,
    )

    # Argumentos para modo tradicional
    parser.add_argument(
        "filename", nargs="?", help="Archivo con el problema (modo tradicional)"
    )
    parser.add_argument(
        "--interactive", "-i", action="store_true", help="Modo interactivo tradicional"
    )

    # Argumentos para modo NLP
    parser.add_argument(
        "--nlp", action="store_true", help="Usar procesamiento de lenguaje natural"
    )
    parser.add_argument("--text", "-t", type=str, help="Texto del problema (modo NLP)")
    parser.add_argument(
        "--file", "-f", type=str, help="Archivo con texto del problema (modo NLP)"
    )
    parser.add_argument(
        "--model",
        "-m",
        type=str,
        choices=["t5-small", "t5-base", "mistral", "llama2"],
        help="Modelo NLP a usar",
    )
    parser.add_argument(
        "--mock-nlp", "--mock", action="store_true", help="Usar NLP mock para pruebas"
    )

    # Argumentos generales
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Modo verboso (más información)"
    )

    args = parser.parse_args()

    # Determinar modo de operación
    if args.nlp or args.text or args.file or args.mock_nlp:
        # Modo NLP
        nlp_mode(args)
    elif args.filename or args.interactive or len(sys.argv) == 1:
        # Modo tradicional - usar solver original
        original_main()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
