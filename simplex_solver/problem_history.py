"""
Gestor de Historial de Problemas Resueltos.
Permite visualizar y gestionar problemas resueltos previamente, así como re-resolverlos.
"""

import sqlite3
import os
import sys
import json
import tempfile
from datetime import datetime
from typing import List, Dict, Optional, Any
from tabulate import tabulate
from simplex_solver.logging_system import logger
from simplex_solver.ui import ConsoleColors


class ProblemHistory:
    """
    Clase para gestionar el historial de problemas resueltos.
    Proporciona métodos para consultar, buscar y re-resolver problemas almacenados.
    """

    def __init__(self):
        """
        Inicializa el gestor de historial y configura la ruta de la base de datos.
        """
        self.db_path = self._get_db_path()

    def _get_db_path(self) -> str:
        """
        Obtiene la ruta de la base de datos donde se almacena el historial.

        Returns:
            str: Ruta completa al archivo de la base de datos.
        """
        if getattr(sys, "frozen", False):
            app_data = os.getenv("APPDATA") or os.path.expanduser("~")
            log_dir = os.path.join(app_data, "SimplexSolver", "logs")
        else:
            log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")

        return os.path.join(log_dir, "simplex_logs.db")

    def get_all_problems(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Recupera todos los problemas almacenados en el historial.

        Args:
            limit: Número máximo de problemas a retornar.

        Returns:
            List[Dict[str, Any]]: Lista de problemas con sus detalles principales.
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        try:
            cursor.execute(
                """
                SELECT 
                    id, timestamp, file_name, file_path,
                    problem_type, num_variables, num_constraints,
                    iterations, execution_time_ms, status, optimal_value
                FROM problem_history
                ORDER BY timestamp DESC
                LIMIT ?
                """,
                (limit,),
            )

            problems = []
            for row in cursor.fetchall():
                problems.append(
                    {
                        "id": row["id"],
                        "timestamp": row["timestamp"],
                        "file_name": row["file_name"],
                        "file_path": row["file_path"],
                        "problem_type": row["problem_type"],
                        "num_variables": row["num_variables"],
                        "num_constraints": row["num_constraints"],
                        "iterations": row["iterations"],
                        "execution_time_ms": row["execution_time_ms"],
                        "status": row["status"],
                        "optimal_value": row["optimal_value"],
                    }
                )

            return problems
        finally:
            conn.close()

    def get_problem_by_id(self, problem_id: int) -> Optional[Dict[str, Any]]:
        """
        Recupera un problema específico del historial utilizando su ID.

        Args:
            problem_id: ID único del problema a recuperar.

        Returns:
            Optional[Dict[str, Any]]: Diccionario con los detalles completos del problema o None si no existe.
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        try:
            cursor.execute(
                """
                SELECT *
                FROM problem_history
                WHERE id = ?
                """,
                (problem_id,),
            )

            row = cursor.fetchone()
            if row:
                return {
                    "id": row["id"],
                    "session_id": row["session_id"],
                    "timestamp": row["timestamp"],
                    "file_name": row["file_name"],
                    "file_path": row["file_path"],
                    "file_content": row["file_content"],
                    "problem_type": row["problem_type"],
                    "num_variables": row["num_variables"],
                    "num_constraints": row["num_constraints"],
                    "iterations": row["iterations"],
                    "execution_time_ms": row["execution_time_ms"],
                    "status": row["status"],
                    "optimal_value": row["optimal_value"],
                    "solution_variables": row["solution_variables"],
                }
            return None
        finally:
            conn.close()

    def search_problems(self, keyword: str) -> List[Dict[str, Any]]:
        """
        Busca problemas en el historial utilizando una palabra clave.

        Args:
            keyword: Palabra clave para buscar en el nombre o ruta del archivo.

        Returns:
            List[Dict[str, Any]]: Lista de problemas que coinciden con la búsqueda.
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        try:
            cursor.execute(
                """
                SELECT 
                    id, timestamp, file_name, file_path,
                    problem_type, num_variables, num_constraints,
                    iterations, execution_time_ms, status, optimal_value
                FROM problem_history
                WHERE file_name LIKE ? OR file_path LIKE ?
                ORDER BY timestamp DESC
                LIMIT 50
                """,
                (f"%{keyword}%", f"%{keyword}%"),
            )

            problems = []
            for row in cursor.fetchall():
                problems.append(
                    {
                        "id": row["id"],
                        "timestamp": row["timestamp"],
                        "file_name": row["file_name"],
                        "file_path": row["file_path"],
                        "problem_type": row["problem_type"],
                        "num_variables": row["num_variables"],
                        "num_constraints": row["num_constraints"],
                        "iterations": row["iterations"],
                        "execution_time_ms": row["execution_time_ms"],
                        "status": row["status"],
                        "optimal_value": row["optimal_value"],
                    }
                )

            return problems
        finally:
            conn.close()

    def display_problems_table(self, problems: List[Dict[str, Any]]):
        """
        Muestra una tabla con los problemas almacenados en el historial.

        Args:
            problems: Lista de problemas a mostrar.
        """
        if not problems:
            print(
                f"\n{ConsoleColors.YELLOW}No se encontraron problemas en el historial.{ConsoleColors.RESET}\n"
            )
            return

        # Preparar datos para la tabla
        table_data = []
        for p in problems:
            # Formatear timestamp
            timestamp = p["timestamp"][:19] if p["timestamp"] else "N/A"

            # Formatear valor óptimo
            if p["optimal_value"] is not None:
                opt_val = f"{p['optimal_value']:.2f}"
            else:
                opt_val = "N/A"

            # Formatear tiempo
            if p["execution_time_ms"] is not None:
                exec_time = f"{p['execution_time_ms']:.2f}ms"
            else:
                exec_time = "N/A"

            # Acortar nombre de archivo si es muy largo
            file_name = p["file_name"]
            if len(file_name) > 30:
                file_name = file_name[:27] + "..."

            table_data.append(
                [
                    p["id"],
                    timestamp,
                    file_name,
                    p["problem_type"] or "N/A",
                    f"{p['num_variables'] or 0}/{p['num_constraints'] or 0}",
                    p["iterations"] or 0,
                    opt_val,
                    exec_time,
                    p["status"] or "N/A",
                ]
            )

        headers = [
            f"{ConsoleColors.BOLD}ID{ConsoleColors.RESET}",
            f"{ConsoleColors.BOLD}Fecha/Hora{ConsoleColors.RESET}",
            f"{ConsoleColors.BOLD}Archivo{ConsoleColors.RESET}",
            f"{ConsoleColors.BOLD}Tipo{ConsoleColors.RESET}",
            f"{ConsoleColors.BOLD}Var/Rest{ConsoleColors.RESET}",
            f"{ConsoleColors.BOLD}Iter{ConsoleColors.RESET}",
            f"{ConsoleColors.BOLD}Valor Ópt.{ConsoleColors.RESET}",
            f"{ConsoleColors.BOLD}Tiempo{ConsoleColors.RESET}",
            f"{ConsoleColors.BOLD}Estado{ConsoleColors.RESET}",
        ]

        print(f"\n{ConsoleColors.CYAN}{'=' * 120}{ConsoleColors.RESET}")
        print(
            f"{ConsoleColors.BOLD}{ConsoleColors.GREEN}HISTORIAL DE PROBLEMAS RESUELTOS{ConsoleColors.RESET}"
        )
        print(f"{ConsoleColors.CYAN}{'=' * 120}{ConsoleColors.RESET}\n")
        print(tabulate(table_data, headers=headers, tablefmt="grid"))
        print(f"\n{ConsoleColors.CYAN}Total: {len(problems)} problema(s){ConsoleColors.RESET}\n")

    def display_problem_detail(self, problem: Dict[str, Any]):
        """Muestra detalles completos de un problema."""
        print(f"\n{ConsoleColors.CYAN}{'=' * 80}{ConsoleColors.RESET}")
        print(
            f"{ConsoleColors.BOLD}{ConsoleColors.GREEN}DETALLES DEL PROBLEMA #{problem['id']}{ConsoleColors.RESET}"
        )
        print(f"{ConsoleColors.CYAN}{'=' * 80}{ConsoleColors.RESET}\n")

        # Información general
        print(f"{ConsoleColors.BOLD}Archivo:{ConsoleColors.RESET} {problem['file_name']}")
        print(f"{ConsoleColors.BOLD}Ruta original:{ConsoleColors.RESET} {problem['file_path']}")
        print(f"{ConsoleColors.BOLD}Fecha/Hora:{ConsoleColors.RESET} {problem['timestamp'][:19]}")
        print(f"{ConsoleColors.BOLD}Tipo:{ConsoleColors.RESET} {problem['problem_type'] or 'N/A'}")

        print(f"\n{ConsoleColors.BOLD}Dimensiones:{ConsoleColors.RESET}")
        print(f"  Variables: {problem['num_variables'] or 0}")
        print(f"  Restricciones: {problem['num_constraints'] or 0}")

        print(f"\n{ConsoleColors.BOLD}Resultado:{ConsoleColors.RESET}")
        print(f"  Estado: {problem['status'] or 'N/A'}")
        if problem["optimal_value"] is not None:
            print(
                f"  Valor óptimo: {ConsoleColors.GREEN}{problem['optimal_value']:.6f}{ConsoleColors.RESET}"
            )
        print(f"  Iteraciones: {problem['iterations'] or 0}")
        if problem["execution_time_ms"] is not None:
            print(f"  Tiempo de ejecución: {problem['execution_time_ms']:.2f} ms")

        # Solución de variables si existe
        if problem["solution_variables"]:
            try:
                solution = json.loads(problem["solution_variables"])
                print(f"\n{ConsoleColors.BOLD}Variables de solución:{ConsoleColors.RESET}")
                for var, value in solution.items():
                    print(f"  {var} = {ConsoleColors.GREEN}{value:.6f}{ConsoleColors.RESET}")
            except (json.JSONDecodeError, KeyError, TypeError, ValueError) as e:
                logger.warning(f"No se pudo parsear la solución guardada: {e}")
                pass

        # Contenido del archivo
        print(f"\n{ConsoleColors.BOLD}Contenido del archivo:{ConsoleColors.RESET}")
        print(f"{ConsoleColors.CYAN}{'-' * 80}{ConsoleColors.RESET}")
        print(problem["file_content"])
        print(f"{ConsoleColors.CYAN}{'-' * 80}{ConsoleColors.RESET}\n")

    def create_temp_file_from_history(self, problem_id: int) -> Optional[str]:
        """
        Crea un archivo temporal con el contenido de un problema del historial.

        Args:
            problem_id: ID del problema

        Returns:
            Ruta del archivo temporal creado o None si hay error
        """
        problem = self.get_problem_by_id(problem_id)
        if not problem:
            return None

        try:
            # Crear archivo temporal
            suffix = os.path.splitext(problem["file_name"])[1] or ".txt"
            temp_file = tempfile.NamedTemporaryFile(
                mode="w",
                suffix=suffix,
                prefix=f"simplex_history_{problem_id}_",
                delete=False,
                encoding="utf-8",
            )

            temp_file.write(problem["file_content"])
            temp_file.close()

            return temp_file.name
        except Exception as e:
            print(f"{ConsoleColors.RED}Error creando archivo temporal: {e}{ConsoleColors.RESET}")
            return None

    def get_statistics(self) -> Dict[str, Any]:
        """Obtiene estadísticas del historial."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            stats = {}

            # Total de problemas
            cursor.execute("SELECT COUNT(*) FROM problem_history")
            stats["total_problems"] = cursor.fetchone()[0]

            # Problemas por tipo
            cursor.execute(
                """
                SELECT problem_type, COUNT(*) 
                FROM problem_history 
                GROUP BY problem_type
            """
            )
            stats["by_type"] = dict(cursor.fetchall())

            # Problemas por estado
            cursor.execute(
                """
                SELECT status, COUNT(*) 
                FROM problem_history 
                GROUP BY status
            """
            )
            stats["by_status"] = dict(cursor.fetchall())

            # Promedio de iteraciones
            cursor.execute(
                """
                SELECT AVG(iterations) 
                FROM problem_history 
                WHERE iterations IS NOT NULL
            """
            )
            result = cursor.fetchone()[0]
            stats["avg_iterations"] = result if result else 0

            # Promedio de tiempo de ejecución
            cursor.execute(
                """
                SELECT AVG(execution_time_ms) 
                FROM problem_history 
                WHERE execution_time_ms IS NOT NULL
            """
            )
            result = cursor.fetchone()[0]
            stats["avg_execution_time"] = result if result else 0

            return stats
        finally:
            conn.close()


def show_history_menu():
    """Muestra un menú interactivo para gestionar el historial."""
    history = ProblemHistory()

    while True:
        print(f"\n{ConsoleColors.CYAN}{'=' * 80}{ConsoleColors.RESET}")
        print(
            f"{ConsoleColors.BOLD}{ConsoleColors.GREEN}HISTORIAL DE PROBLEMAS{ConsoleColors.RESET}"
        )
        print(f"{ConsoleColors.CYAN}{'=' * 80}{ConsoleColors.RESET}\n")
        print(f"{ConsoleColors.BOLD}1.{ConsoleColors.RESET} Ver todos los problemas")
        print(f"{ConsoleColors.BOLD}2.{ConsoleColors.RESET} Buscar problema por nombre")
        print(f"{ConsoleColors.BOLD}3.{ConsoleColors.RESET} Ver detalles de un problema")
        print(f"{ConsoleColors.BOLD}4.{ConsoleColors.RESET} Re-resolver un problema del historial")
        print(f"{ConsoleColors.BOLD}5.{ConsoleColors.RESET} Ver estadísticas")
        print(f"{ConsoleColors.BOLD}6.{ConsoleColors.RESET} Volver al menú principal")
        print()

        choice = input(
            f"{ConsoleColors.YELLOW}Selecciona una opción: {ConsoleColors.RESET}"
        ).strip()

        if choice == "1":
            problems = history.get_all_problems()
            history.display_problems_table(problems)
            if problems:
                input(
                    f"\n{ConsoleColors.YELLOW}Presiona Enter para continuar...{ConsoleColors.RESET}"
                )

        elif choice == "2":
            keyword = input(
                f"\n{ConsoleColors.YELLOW}Ingresa palabra clave: {ConsoleColors.RESET}"
            ).strip()
            if keyword:
                problems = history.search_problems(keyword)
                history.display_problems_table(problems)
                if problems:
                    input(
                        f"\n{ConsoleColors.YELLOW}Presiona Enter para continuar...{ConsoleColors.RESET}"
                    )

        elif choice == "3":
            try:
                problem_id = int(
                    input(
                        f"\n{ConsoleColors.YELLOW}Ingresa el ID del problema: {ConsoleColors.RESET}"
                    ).strip()
                )
                problem = history.get_problem_by_id(problem_id)
                if problem:
                    history.display_problem_detail(problem)
                else:
                    print(f"\n{ConsoleColors.RED}Problema no encontrado.{ConsoleColors.RESET}")
                input(
                    f"\n{ConsoleColors.YELLOW}Presiona Enter para continuar...{ConsoleColors.RESET}"
                )
            except ValueError:
                print(f"\n{ConsoleColors.RED}ID inválido.{ConsoleColors.RESET}")

        elif choice == "4":
            try:
                problem_id = int(
                    input(
                        f"\n{ConsoleColors.YELLOW}Ingresa el ID del problema a re-resolver: {ConsoleColors.RESET}"
                    ).strip()
                )
                temp_file = history.create_temp_file_from_history(problem_id)
                if temp_file:
                    print(
                        f"\n{ConsoleColors.GREEN}✓ Archivo temporal creado: {temp_file}{ConsoleColors.RESET}"
                    )
                    return temp_file  # Retorna la ruta para que main.py lo use
                else:
                    print(
                        f"\n{ConsoleColors.RED}No se pudo crear el archivo temporal.{ConsoleColors.RESET}"
                    )
                    input(
                        f"\n{ConsoleColors.YELLOW}Presiona Enter para continuar...{ConsoleColors.RESET}"
                    )
            except ValueError:
                print(f"\n{ConsoleColors.RED}ID inválido.{ConsoleColors.RESET}")

        elif choice == "5":
            stats = history.get_statistics()
            print(f"\n{ConsoleColors.CYAN}{'=' * 80}{ConsoleColors.RESET}")
            print(
                f"{ConsoleColors.BOLD}{ConsoleColors.GREEN}ESTADÍSTICAS DEL HISTORIAL{ConsoleColors.RESET}"
            )
            print(f"{ConsoleColors.CYAN}{'=' * 80}{ConsoleColors.RESET}\n")
            print(
                f"{ConsoleColors.BOLD}Total de problemas resueltos:{ConsoleColors.RESET} {stats['total_problems']}"
            )

            if stats["by_type"]:
                print(f"\n{ConsoleColors.BOLD}Por tipo:{ConsoleColors.RESET}")
                for ptype, count in stats["by_type"].items():
                    print(f"  {ptype or 'N/A'}: {count}")

            if stats["by_status"]:
                print(f"\n{ConsoleColors.BOLD}Por estado:{ConsoleColors.RESET}")
                for status, count in stats["by_status"].items():
                    print(f"  {status or 'N/A'}: {count}")

            print(
                f"\n{ConsoleColors.BOLD}Promedio de iteraciones:{ConsoleColors.RESET} {stats['avg_iterations']:.2f}"
            )
            print(
                f"{ConsoleColors.BOLD}Promedio de tiempo de ejecución:{ConsoleColors.RESET} {stats['avg_execution_time']:.2f} ms"
            )

            input(f"\n{ConsoleColors.YELLOW}Presiona Enter para continuar...{ConsoleColors.RESET}")

        elif choice == "6":
            return None

        else:
            print(f"\n{ConsoleColors.RED}Opción no válida.{ConsoleColors.RESET}")


if __name__ == "__main__":
    show_history_menu()
