"""
Gestor de Historial de Problemas Resueltos.
Permite ver y re-resolver problemas anteriores.
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


# Colores ANSI para terminal
class Colors:
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    MAGENTA = "\033[95m"
    BLUE = "\033[94m"
    BOLD = "\033[1m"
    RESET = "\033[0m"


class ProblemHistory:
    """Gestor del historial de problemas resueltos."""

    def __init__(self):
        """Inicializa el gestor de historial."""
        self.db_path = self._get_db_path()

    def _get_db_path(self) -> str:
        """Obtiene la ruta de la base de datos."""
        if getattr(sys, "frozen", False):
            app_data = os.getenv("APPDATA") or os.path.expanduser("~")
            log_dir = os.path.join(app_data, "SimplexSolver", "logs")
        else:
            log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")

        return os.path.join(log_dir, "simplex_logs.db")

    def get_all_problems(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Obtiene todos los problemas del historial.

        Args:
            limit: Número máximo de problemas a retornar

        Returns:
            Lista de diccionarios con información de cada problema
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
        Obtiene un problema específico por su ID, incluyendo el contenido del archivo.

        Args:
            problem_id: ID del problema

        Returns:
            Diccionario con toda la información del problema o None si no existe
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
        Busca problemas por nombre de archivo.

        Args:
            keyword: Palabra clave para buscar

        Returns:
            Lista de problemas que coinciden
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
        """Muestra una tabla formateada de problemas."""
        if not problems:
            print(f"\n{Colors.YELLOW}No se encontraron problemas en el historial.{Colors.RESET}\n")
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
            f"{Colors.BOLD}ID{Colors.RESET}",
            f"{Colors.BOLD}Fecha/Hora{Colors.RESET}",
            f"{Colors.BOLD}Archivo{Colors.RESET}",
            f"{Colors.BOLD}Tipo{Colors.RESET}",
            f"{Colors.BOLD}Var/Rest{Colors.RESET}",
            f"{Colors.BOLD}Iter{Colors.RESET}",
            f"{Colors.BOLD}Valor Ópt.{Colors.RESET}",
            f"{Colors.BOLD}Tiempo{Colors.RESET}",
            f"{Colors.BOLD}Estado{Colors.RESET}",
        ]

        print(f"\n{Colors.CYAN}{'=' * 120}{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.GREEN}HISTORIAL DE PROBLEMAS RESUELTOS{Colors.RESET}")
        print(f"{Colors.CYAN}{'=' * 120}{Colors.RESET}\n")
        print(tabulate(table_data, headers=headers, tablefmt="grid"))
        print(f"\n{Colors.CYAN}Total: {len(problems)} problema(s){Colors.RESET}\n")

    def display_problem_detail(self, problem: Dict[str, Any]):
        """Muestra detalles completos de un problema."""
        print(f"\n{Colors.CYAN}{'=' * 80}{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.GREEN}DETALLES DEL PROBLEMA #{problem['id']}{Colors.RESET}")
        print(f"{Colors.CYAN}{'=' * 80}{Colors.RESET}\n")

        # Información general
        print(f"{Colors.BOLD}Archivo:{Colors.RESET} {problem['file_name']}")
        print(f"{Colors.BOLD}Ruta original:{Colors.RESET} {problem['file_path']}")
        print(f"{Colors.BOLD}Fecha/Hora:{Colors.RESET} {problem['timestamp'][:19]}")
        print(f"{Colors.BOLD}Tipo:{Colors.RESET} {problem['problem_type'] or 'N/A'}")

        print(f"\n{Colors.BOLD}Dimensiones:{Colors.RESET}")
        print(f"  Variables: {problem['num_variables'] or 0}")
        print(f"  Restricciones: {problem['num_constraints'] or 0}")

        print(f"\n{Colors.BOLD}Resultado:{Colors.RESET}")
        print(f"  Estado: {problem['status'] or 'N/A'}")
        if problem["optimal_value"] is not None:
            print(f"  Valor óptimo: {Colors.GREEN}{problem['optimal_value']:.6f}{Colors.RESET}")
        print(f"  Iteraciones: {problem['iterations'] or 0}")
        if problem["execution_time_ms"] is not None:
            print(f"  Tiempo de ejecución: {problem['execution_time_ms']:.2f} ms")

        # Solución de variables si existe
        if problem["solution_variables"]:
            try:
                solution = json.loads(problem["solution_variables"])
                print(f"\n{Colors.BOLD}Variables de solución:{Colors.RESET}")
                for var, value in solution.items():
                    print(f"  {var} = {Colors.GREEN}{value:.6f}{Colors.RESET}")
            except (json.JSONDecodeError, KeyError, TypeError, ValueError) as e:
                logger.warning(f"No se pudo parsear la solución guardada: {e}")
                pass

        # Contenido del archivo
        print(f"\n{Colors.BOLD}Contenido del archivo:{Colors.RESET}")
        print(f"{Colors.CYAN}{'-' * 80}{Colors.RESET}")
        print(problem["file_content"])
        print(f"{Colors.CYAN}{'-' * 80}{Colors.RESET}\n")

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
            print(f"{Colors.RED}Error creando archivo temporal: {e}{Colors.RESET}")
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
        print(f"\n{Colors.CYAN}{'=' * 80}{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.GREEN}HISTORIAL DE PROBLEMAS{Colors.RESET}")
        print(f"{Colors.CYAN}{'=' * 80}{Colors.RESET}\n")
        print(f"{Colors.BOLD}1.{Colors.RESET} Ver todos los problemas")
        print(f"{Colors.BOLD}2.{Colors.RESET} Buscar problema por nombre")
        print(f"{Colors.BOLD}3.{Colors.RESET} Ver detalles de un problema")
        print(f"{Colors.BOLD}4.{Colors.RESET} Re-resolver un problema del historial")
        print(f"{Colors.BOLD}5.{Colors.RESET} Ver estadísticas")
        print(f"{Colors.BOLD}6.{Colors.RESET} Volver al menú principal")
        print()

        choice = input(f"{Colors.YELLOW}Selecciona una opción: {Colors.RESET}").strip()

        if choice == "1":
            problems = history.get_all_problems()
            history.display_problems_table(problems)
            if problems:
                input(f"\n{Colors.YELLOW}Presiona Enter para continuar...{Colors.RESET}")

        elif choice == "2":
            keyword = input(f"\n{Colors.YELLOW}Ingresa palabra clave: {Colors.RESET}").strip()
            if keyword:
                problems = history.search_problems(keyword)
                history.display_problems_table(problems)
                if problems:
                    input(f"\n{Colors.YELLOW}Presiona Enter para continuar...{Colors.RESET}")

        elif choice == "3":
            try:
                problem_id = int(
                    input(f"\n{Colors.YELLOW}Ingresa el ID del problema: {Colors.RESET}").strip()
                )
                problem = history.get_problem_by_id(problem_id)
                if problem:
                    history.display_problem_detail(problem)
                else:
                    print(f"\n{Colors.RED}Problema no encontrado.{Colors.RESET}")
                input(f"\n{Colors.YELLOW}Presiona Enter para continuar...{Colors.RESET}")
            except ValueError:
                print(f"\n{Colors.RED}ID inválido.{Colors.RESET}")

        elif choice == "4":
            try:
                problem_id = int(
                    input(
                        f"\n{Colors.YELLOW}Ingresa el ID del problema a re-resolver: {Colors.RESET}"
                    ).strip()
                )
                temp_file = history.create_temp_file_from_history(problem_id)
                if temp_file:
                    print(f"\n{Colors.GREEN}✓ Archivo temporal creado: {temp_file}{Colors.RESET}")
                    return temp_file  # Retorna la ruta para que main.py lo use
                else:
                    print(f"\n{Colors.RED}No se pudo crear el archivo temporal.{Colors.RESET}")
                    input(f"\n{Colors.YELLOW}Presiona Enter para continuar...{Colors.RESET}")
            except ValueError:
                print(f"\n{Colors.RED}ID inválido.{Colors.RESET}")

        elif choice == "5":
            stats = history.get_statistics()
            print(f"\n{Colors.CYAN}{'=' * 80}{Colors.RESET}")
            print(f"{Colors.BOLD}{Colors.GREEN}ESTADÍSTICAS DEL HISTORIAL{Colors.RESET}")
            print(f"{Colors.CYAN}{'=' * 80}{Colors.RESET}\n")
            print(
                f"{Colors.BOLD}Total de problemas resueltos:{Colors.RESET} {stats['total_problems']}"
            )

            if stats["by_type"]:
                print(f"\n{Colors.BOLD}Por tipo:{Colors.RESET}")
                for ptype, count in stats["by_type"].items():
                    print(f"  {ptype or 'N/A'}: {count}")

            if stats["by_status"]:
                print(f"\n{Colors.BOLD}Por estado:{Colors.RESET}")
                for status, count in stats["by_status"].items():
                    print(f"  {status or 'N/A'}: {count}")

            print(
                f"\n{Colors.BOLD}Promedio de iteraciones:{Colors.RESET} {stats['avg_iterations']:.2f}"
            )
            print(
                f"{Colors.BOLD}Promedio de tiempo de ejecución:{Colors.RESET} {stats['avg_execution_time']:.2f} ms"
            )

            input(f"\n{Colors.YELLOW}Presiona Enter para continuar...{Colors.RESET}")

        elif choice == "6":
            return None

        else:
            print(f"\n{Colors.RED}Opción no válida.{Colors.RESET}")


if __name__ == "__main__":
    show_history_menu()
