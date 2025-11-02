"""
Simplex Solver - Programa principal.
Coordina los módulos para resolver problemas de programación lineal.
"""

import sys
import argparse
import os
import time
import json
from solver import SimplexSolver
from file_parser import FileParser
from src.user_interface import UserInterface
from input_validator import InputValidator  # Nuevo import
from reporting_pdf import generate_pdf
from logging_system import logger, LogLevel
from problem_history import show_history_menu


def main():
    """Función principal del programa."""
    start_time = time.time()
    logger.info("=== Iniciando Simplex Solver ===")
    logger.debug(f"Argumentos de línea de comandos: {' '.join(sys.argv)}")

    parser = create_parser()
    args = parser.parse_args()

    try:
        # Opción para ver historial
        if args.history:
            logger.info("Modo: Visualización de historial")
            temp_file = show_history_menu()
            if temp_file:
                # Usuario quiere re-resolver un problema del historial
                print(f"\n=== RE-RESOLVIENDO PROBLEMA DEL HISTORIAL ===\n")
                logger.info(
                    f"Re-resolviendo problema desde archivo temporal: {temp_file}"
                )
                args.filename = temp_file
            else:
                # Usuario salió del menú de historial
                logger.end_session()
                return

        # Obtener datos del problema
        if args.filename:
            print(f"=== SIMPLEX SOLVER - Resolviendo archivo: {args.filename} ===\n")
            logger.info(f"Modo: Resolución desde archivo '{args.filename}'")
            c, A, b, constraint_types, maximize = FileParser.parse_file(args.filename)

            # Leer contenido del archivo para guardarlo en historial
            try:
                with open(args.filename, "r", encoding="utf-8") as f:
                    file_content = f.read()
            except:
                file_content = ""

        elif args.interactive or len(sys.argv) == 1:
            logger.info("Modo: Entrada interactiva")
            c, A, b, constraint_types, maximize = UserInterface.interactive_input()
            file_content = ""  # No hay archivo en modo interactivo
            args.filename = "interactive_input"
        else:
            logger.warning("No se proporcionaron argumentos válidos")
            parser.print_help()
            sys.exit(1)

        # Validar el problema antes de resolver
        print("\n Validando problema...")
        logger.info("Iniciando validación del problema")
        logger.debug(f"Variables: {len(c)}, Restricciones: {len(A)}")
        is_valid, error_msg = InputValidator.validate_problem(
            c, A, b, constraint_types, maximize
        )
        if not is_valid:
            logger.error(f"Validación fallida: {error_msg}")
            print(f"ERROR: {error_msg}")
            print("El problema no puede ser resuelto. Por favor, corrija los datos.")
            sys.exit(1)
        logger.info("Problema validado correctamente")
        print("Problema validado correctamente")

        # Mostrar problema
        UserInterface.display_problem(c, A, b, constraint_types, maximize)

        # Resolver problema
        print("\n Resolviendo problema...")
        logger.info("Iniciando resolución del problema")
        solve_start = time.time()
        solver = SimplexSolver()
        result = solver.solve(c, A, b, constraint_types, maximize)
        solve_time = (time.time() - solve_start) * 1000  # en milisegundos

        # Log del evento del solver
        logger.log_solver_event(
            event_type="solve_complete",
            problem_type="maximización" if maximize else "minimización",
            num_variables=len(c),
            num_constraints=len(A),
            iterations=result.get("iterations", 0),
            execution_time_ms=solve_time,
            status=result.get("status"),
            optimal_value=result.get("optimal_value"),
        )
        logger.info(
            f"Resolución completada en {solve_time:.2f} ms - Estado: {result.get('status')}"
        )

        # Adjuntar datos útiles a result para que el generador de reportes tenga contexto
        result.setdefault("c", c)
        result.setdefault("A", A)
        result.setdefault("b", b)
        result.setdefault("constraint_types", constraint_types)
        result.setdefault("maximize", maximize)

        # Validar la solución si es óptima
        if result.get("status") == "optimal":
            print("\n Validando factibilidad de la solución...")
            logger.debug("Validando factibilidad de la solución óptima")
            is_feasible, errors = InputValidator.validate_solution_feasibility(
                result["solution"], A, b, constraint_types
            )
            if not is_feasible:
                logger.warning(f"Solución no factible: {errors}")
                print("ADVERTENCIA: La solución podría no ser factible:")
                for error in errors:
                    print(f"   - {error}")
            else:
                logger.info("Solución validada como factible")
                print("Solución validada como factible")

        # Mostrar resultados
        UserInterface.display_result(result)

        # Guardar en historial si la solución es óptima
        if result.get("status") == "optimal" and args.filename:
            logger.info("Guardando problema en historial")

            # Preparar variables de solución en formato JSON
            solution_vars = {}
            if "solution" in result:
                for i, val in enumerate(result["solution"], 1):
                    solution_vars[f"x{i}"] = val

            logger.save_problem_to_history(
                file_path=args.filename,
                file_content=file_content,
                problem_type="maximización" if maximize else "minimización",
                num_variables=len(c),
                num_constraints=len(A),
                iterations=result.get("iterations", 0),
                execution_time_ms=solve_time,
                status=result.get("status"),
                optimal_value=result.get("optimal_value"),
                solution_variables=json.dumps(solution_vars),
            )

        # Generar PDF si el usuario lo solicitó y la solución es óptima
        if getattr(args, "pdf", None) and result.get("status") == "optimal":
            logger.info(f"Generando reporte PDF: {args.pdf}")
            output_path = generate_pdf(result, args.pdf)
            logger.info(f"Reporte PDF generado exitosamente: {output_path}")

        # Resumen final
        total_time = (time.time() - start_time) * 1000
        logger.info(f"Ejecución completada en {total_time:.2f} ms")
        logger.end_session()

    except KeyboardInterrupt:
        logger.warning("Ejecución interrumpida por el usuario (Ctrl+C)")
        print("\n\n⚠️  Ejecución interrumpida por el usuario")
        logger.end_session()
        sys.exit(0)
    except Exception as e:
        logger.critical(f"Error crítico en la ejecución: {str(e)}", exception=e)
        print(f"\n ERROR: {e}")
        print("El programa se ha detenido debido a un error.")
        logger.end_session()
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
    parser.add_argument(
        "--pdf",
        "-p",
        metavar="archivo.pdf",
        help="Generar PDF con el paso a paso y la solución",
    )
    parser.add_argument(
        "--history",
        "-H",
        action="store_true",
        help="Ver historial de problemas resueltos",
    )
    return parser


if __name__ == "__main__":
    main()
