"""
Simplex Solver - Main program.
Coordinates modules to solve linear programming problems.
"""

import sys
import argparse
import os
import time
import json
from typing import Tuple, List, Dict, Any, Optional
from simplex_solver.solver import SimplexSolver
from simplex_solver.file_parser import FileParser
from simplex_solver.user_interface import UserInterface
from simplex_solver.input_validator import InputValidator
from simplex_solver.reporting_pdf import generate_pdf
from simplex_solver.logging_system import logger, LogLevel
from simplex_solver.problem_history import show_history_menu
from simplex_solver.config import Messages, Defaults


class ProblemData:
    """Encapsula los datos de un problema de programación lineal."""

    def __init__(
        self,
        c: List[float],
        A: List[List[float]],
        b: List[float],
        constraint_types: List[str],
        maximize: bool,
        filename: str = "",
        file_content: str = "",
    ):
        self.c = c
        self.A = A
        self.b = b
        self.constraint_types = constraint_types
        self.maximize = maximize
        self.filename = filename
        self.file_content = file_content


class ApplicationOrchestrator:
    """
    Orquesta el flujo completo de la aplicación.

    Responsabilidades separadas:
    - Cargar problemas desde diferentes fuentes
    - Validar problemas
    - Resolver problemas
    - Gestionar salida (reportes, historial)
    """

    def __init__(self):
        self.solver = SimplexSolver()

    def run(self, args: argparse.Namespace) -> None:
        """
        Ejecuta el flujo completo de la aplicación.

        Args:
            args: Argumentos parseados de línea de comandos
        """
        start_time = time.time()

        try:
            # Cargar problema
            problem = self._load_problem(args)
            if problem is None:
                return

            # Validar problema
            self._validate_problem(problem)

            # Mostrar problema
            UserInterface.display_problem(
                problem.c, problem.A, problem.b, problem.constraint_types, problem.maximize
            )

            # Resolver problema
            result, solve_time = self._solve_problem(problem)

            # Validar solución
            self._validate_solution(result, problem)

            # Mostrar resultados
            UserInterface.display_result(result)

            # Gestionar salidas
            self._handle_output(result, problem, args, solve_time)

            # Resumen final
            total_time = (time.time() - start_time) * 1000
            logger.info(f"Ejecución completada en {total_time:.2f} ms")

        except KeyboardInterrupt:
            logger.warning("Ejecución interrumpida por el usuario (Ctrl+C)")
            print(Messages.USER_INTERRUPTED)
            sys.exit(0)
        except Exception as e:
            logger.critical(f"Error crítico en la ejecución: {str(e)}", exception=e)
            print(Messages.CRITICAL_ERROR.format(error=e))
            print("El programa se ha detenido debido a un error.")
            sys.exit(1)
        finally:
            logger.end_session()

    def _load_problem(self, args: argparse.Namespace) -> Optional[ProblemData]:
        """
        Carga un problema desde la fuente especificada.

        Returns:
            ProblemData o None si el usuario canceló
        """
        # Opción para ver historial
        if args.history:
            logger.info("Modo: Visualización de historial")
            temp_file = show_history_menu()
            if temp_file:
                print(f"\n=== RE-RESOLVIENDO PROBLEMA DEL HISTORIAL ===\n")
                logger.info(f"Re-resolviendo problema desde archivo temporal: {temp_file}")
                args.filename = temp_file
            else:
                return None

        # Cargar desde archivo
        if args.filename:
            return self._load_from_file(args.filename)

        # Cargar desde entrada interactiva
        elif args.interactive or len(sys.argv) == 1:
            return self._load_from_interactive()

        # Sin entrada válida
        else:
            logger.warning("No se proporcionaron argumentos válidos")
            create_parser().print_help()
            sys.exit(1)

    def _load_from_file(self, filename: str) -> ProblemData:
        """Carga un problema desde un archivo."""
        print(f"=== SIMPLEX SOLVER - Resolviendo archivo: {filename} ===\n")
        logger.info(f"Modo: Resolución desde archivo '{filename}'")

        c, A, b, constraint_types, maximize = FileParser.parse_file(filename)

        # Leer contenido del archivo para historial
        file_content = ""
        try:
            with open(filename, "r", encoding="utf-8") as f:
                file_content = f.read()
        except (IOError, OSError, UnicodeDecodeError) as e:
            logger.warning(f"No se pudo leer contenido del archivo para historial: {e}")

        return ProblemData(c, A, b, constraint_types, maximize, filename, file_content)

    def _load_from_interactive(self) -> ProblemData:
        """Carga un problema desde entrada interactiva."""
        logger.info("Modo: Entrada interactiva")
        c, A, b, constraint_types, maximize = UserInterface.interactive_input()
        return ProblemData(
            c,
            A,
            b,
            constraint_types,
            maximize,
            Defaults.INTERACTIVE_FILENAME,
            Defaults.EMPTY_FILE_CONTENT,
        )

    def _validate_problem(self, problem: ProblemData) -> None:
        """
        Valida un problema antes de resolverlo.

        Raises:
            SystemExit: Si el problema no es válido
        """
        print(f"\n{Messages.VALIDATING}")
        logger.info("Iniciando validación del problema")
        logger.debug(f"Variables: {len(problem.c)}, Restricciones: {len(problem.A)}")

        is_valid, error_msg = InputValidator.validate_problem(
            problem.c, problem.A, problem.b, problem.constraint_types, problem.maximize
        )

        if not is_valid:
            logger.error(f"Validación fallida: {error_msg}")
            print(Messages.VALIDATION_FAILED.format(error=error_msg))
            print("El problema no puede ser resuelto. Por favor, corrija los datos.")
            sys.exit(1)

        logger.info("Problema validado correctamente")
        print(Messages.VALIDATION_SUCCESS)

    def _solve_problem(self, problem: ProblemData) -> Tuple[Dict[str, Any], float]:
        """
        Resuelve un problema de programación lineal.

        Returns:
            Tupla (resultado, tiempo_ms)
        """
        print(f"\n{Messages.SOLVING}")
        logger.info("Iniciando resolución del problema")

        solve_start = time.time()
        result = self.solver.solve(
            problem.c, problem.A, problem.b, problem.constraint_types, problem.maximize
        )
        solve_time = (time.time() - solve_start) * 1000

        # Log del evento
        logger.log_solver_event(
            event_type="solve_complete",
            problem_type="maximización" if problem.maximize else "minimización",
            num_variables=len(problem.c),
            num_constraints=len(problem.A),
            iterations=result.get("iterations", 0),
            execution_time_ms=solve_time,
            status=result.get("status", "unknown"),
            optimal_value=result.get("optimal_value", 0.0),
        )
        logger.info(
            f"Resolución completada en {solve_time:.2f} ms - Estado: {result.get('status')}"
        )

        # Adjuntar datos del problema al resultado para reportes
        result.setdefault("c", problem.c)
        result.setdefault("A", problem.A)
        result.setdefault("b", problem.b)
        result.setdefault("constraint_types", problem.constraint_types)
        result.setdefault("maximize", problem.maximize)

        return result, solve_time

    def _validate_solution(self, result: Dict[str, Any], problem: ProblemData) -> None:
        """Valida la factibilidad de una solución óptima."""
        if result.get("status") != "optimal":
            return

        print(f"\n{Messages.VALIDATING_SOLUTION}")
        logger.debug("Validando factibilidad de la solución óptima")

        is_feasible, errors = InputValidator.validate_solution_feasibility(
            result["solution"], problem.A, problem.b, problem.constraint_types
        )

        if not is_feasible:
            logger.warning(f"Solución no factible: {errors}")
            print(Messages.SOLUTION_NOT_FEASIBLE)
            for error in errors:
                print(f"   - {error}")
        else:
            logger.info("Solución validada como factible")
            print(Messages.SOLUTION_FEASIBLE)

    def _handle_output(
        self,
        result: Dict[str, Any],
        problem: ProblemData,
        args: argparse.Namespace,
        solve_time: float,
    ) -> None:
        """Gestiona las salidas: historial y reportes PDF."""
        # Guardar en historial
        if result.get("status") == "optimal" and problem.filename:
            self._save_to_history(result, problem, solve_time)

        # Generar PDF
        if getattr(args, "pdf", None) and result.get("status") == "optimal":
            self._generate_pdf_report(result, args.pdf)

    def _save_to_history(
        self, result: Dict[str, Any], problem: ProblemData, solve_time: float
    ) -> None:
        """Guarda el problema resuelto en el historial."""
        logger.info("Guardando problema en historial")

        # Preparar variables de solución en formato JSON
        solution_vars = {}
        if "solution" in result:
            for i, val in enumerate(result["solution"], 1):
                solution_vars[f"x{i}"] = val

        logger.save_problem_to_history(
            file_path=problem.filename,
            file_content=problem.file_content,
            problem_type="maximización" if problem.maximize else "minimización",
            num_variables=len(problem.c),
            num_constraints=len(problem.A),
            iterations=result.get("iterations", 0),
            execution_time_ms=solve_time,
            status=result.get("status", "unknown"),
            optimal_value=result.get("optimal_value", 0.0),
            solution_variables=json.dumps(solution_vars),
        )

    def _generate_pdf_report(self, result: Dict[str, Any], pdf_filename: str) -> None:
        """Genera un reporte PDF de la solución."""
        logger.info(f"Generando reporte PDF: {pdf_filename}")
        output_path = generate_pdf(result, pdf_filename)
        logger.info(f"Reporte PDF generado exitosamente: {output_path}")
        print(Messages.PDF_GENERATED.format(path=output_path))


def main():
    """Función principal del programa."""
    logger.info("=== Iniciando Simplex Solver ===")
    logger.debug(f"Argumentos de línea de comandos: {' '.join(sys.argv)}")

    parser = create_parser()
    args = parser.parse_args()

    orchestrator = ApplicationOrchestrator()
    orchestrator.run(args)


def create_parser() -> argparse.ArgumentParser:
    """Crea y configura el parser de argumentos de línea de comandos."""
    parser = argparse.ArgumentParser(
        description="Simplex Solver - Resuelve problemas de programación lineal"
    )
    parser.add_argument("filename", nargs="?", help="Archivo con el problema a resolver")
    parser.add_argument("--interactive", "-i", action="store_true", help="Modo interactivo")
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
