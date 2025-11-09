"""
Visor de Logs para Simplex Solver.
Interfaz en consola para visualizar y analizar logs almacenados en una base de datos SQLite.
"""

import sqlite3
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from tabulate import tabulate


class LogViewer:
    """
    Clase para gestionar y visualizar logs generados por el sistema.
    Proporciona una interfaz de consola para realizar consultas y análisis.
    """

    def __init__(self, db_path: str):
        """
        Inicializa el visor de logs y verifica la existencia de la base de datos.

        Args:
            db_path: Ruta al archivo de la base de datos de logs.
        """
        self.db_path = db_path
        if not os.path.exists(db_path):
            raise FileNotFoundError(f"Base de datos no encontrada: {db_path}")

    def show_menu(self):
        """
        Muestra el menú principal del visor de logs y gestiona la interacción con el usuario.
        """
        while True:
            print("\n" + "=" * 60)
            print("SIMPLEX SOLVER - VISOR DE LOGS")
            print("=" * 60)
            print("1. Ver logs recientes")
            print("2. Ver logs por nivel")
            print("3. Ver logs por sesión")
            print("4. Ver estadísticas")
            print("5. Ver eventos del solver")
            print("6. Ver operaciones de archivos")
            print("7. Buscar en logs")
            print("8. Ver sesiones")
            print("9. Exportar logs")
            print("10. Limpiar logs antiguos")
            print("0. Salir")
            print("=" * 60)

            try:
                choice = input("\nSeleccione una opción: ").strip()

                if choice == "0":
                    break
                elif choice == "1":
                    self.view_recent_logs()
                elif choice == "2":
                    self.view_logs_by_level()
                elif choice == "3":
                    self.view_logs_by_session()
                elif choice == "4":
                    self.view_statistics()
                elif choice == "5":
                    self.view_solver_events()
                elif choice == "6":
                    self.view_file_operations()
                elif choice == "7":
                    self.search_logs()
                elif choice == "8":
                    self.view_sessions()
                elif choice == "9":
                    self.export_logs()
                elif choice == "10":
                    self.cleanup_old_logs()
                else:
                    print("Opción inválida. Intente nuevamente.")

            except KeyboardInterrupt:
                print("\n\nSaliendo del visor de logs...")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")
                input("Presione Enter para continuar...")

    def view_recent_logs(self):
        """
        Muestra los logs más recientes almacenados en la base de datos.
        Permite al usuario especificar la cantidad de registros a visualizar.
        """
        limit = int(input("Cantidad de logs a mostrar (default: 50): ") or "50")

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT timestamp, level, module, function, message
            FROM logs
            ORDER BY timestamp DESC
            LIMIT ?
        """,
            (limit,),
        )

        logs = cursor.fetchall()
        conn.close()

        if logs:
            print(f"\n📋 Últimos {len(logs)} logs:")
            print("-" * 120)
            headers = ["Timestamp", "Nivel", "Módulo", "Función", "Mensaje"]
            # Truncar mensajes largos para mejorar la legibilidad
            formatted_logs = [
                (
                    log[0][:19],
                    log[1],
                    log[2][:20],
                    log[3][:20] if log[3] else "",
                    (log[4][:60] + "...") if len(log[4]) > 60 else log[4],
                )
                for log in logs
            ]
            print(tabulate(formatted_logs, headers=headers, tablefmt="grid"))
        else:
            print("\n⚠️  No hay logs disponibles.")

        input("\nPresione Enter para continuar...")

    def view_logs_by_level(self):
        """
        Filtra y muestra los logs según el nivel de severidad especificado por el usuario.
        """
        print("\nNiveles disponibles:")
        print("1. DEBUG")
        print("2. INFO")
        print("3. WARNING")
        print("4. ERROR")
        print("5. CRITICAL")

        choice = input("Seleccione un nivel: ").strip()
        levels = {
            "1": "DEBUG",
            "2": "INFO",
            "3": "WARNING",
            "4": "ERROR",
            "5": "CRITICAL",
        }

        level = levels.get(choice)
        if not level:
            print("Nivel inválido.")
            return

        limit = int(input("Cantidad de logs a mostrar (default: 50): ") or "50")

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT timestamp, module, function, message, exception_message
            FROM logs
            WHERE level = ?
            ORDER BY timestamp DESC
            LIMIT ?
        """,
            (level, limit),
        )

        logs = cursor.fetchall()
        conn.close()

        if logs:
            print(f"\n📋 Logs nivel {level}:")
            print("-" * 120)
            headers = ["Timestamp", "Módulo", "Función", "Mensaje", "Excepción"]
            formatted_logs = [
                (
                    log[0][:19],
                    log[1][:20],
                    log[2][:20] if log[2] else "",
                    (log[3][:50] + "...") if len(log[3]) > 50 else log[3],
                    ((log[4][:30] + "...") if log[4] and len(log[4]) > 30 else (log[4] or "")),
                )
                for log in logs
            ]
            print(tabulate(formatted_logs, headers=headers, tablefmt="grid"))
        else:
            print(f"\n⚠️  No hay logs de nivel {level}.")

        input("\nPresione Enter para continuar...")

    def view_logs_by_session(self):
        """
        Permite al usuario seleccionar una sesión específica y muestra los logs asociados a ella.
        """
        # Primero mostrar sesiones disponibles
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT session_id, start_time, end_time, execution_mode
            FROM sessions
            ORDER BY start_time DESC
            LIMIT 10
        """
        )

        sessions = cursor.fetchall()

        if not sessions:
            print("\n⚠️  No hay sesiones disponibles.")
            conn.close()
            return

        print("\n📋 Últimas 10 sesiones:")
        for i, session in enumerate(sessions, 1):
            end = session[2] if session[2] else "En curso"
            print(
                f"{i}. {session[0]} | Inicio: {session[1][:19]} | Fin: {end} | Modo: {session[3]}"
            )

        try:
            choice = int(input("\nSeleccione una sesión (número): "))
            if 1 <= choice <= len(sessions):
                session_id = sessions[choice - 1][0]

                cursor.execute(
                    """
                    SELECT timestamp, level, module, function, message
                    FROM logs
                    WHERE session_id = ?
                    ORDER BY timestamp DESC
                """,
                    (session_id,),
                )

                logs = cursor.fetchall()

                if logs:
                    print(f"\n📋 Logs de la sesión {session_id}:")
                    print("-" * 120)
                    headers = ["Timestamp", "Nivel", "Módulo", "Función", "Mensaje"]
                    formatted_logs = [
                        (
                            log[0][:19],
                            log[1],
                            log[2][:20],
                            log[3][:20] if log[3] else "",
                            (log[4][:60] + "...") if len(log[4]) > 60 else log[4],
                        )
                        for log in logs
                    ]
                    print(tabulate(formatted_logs, headers=headers, tablefmt="grid"))
                else:
                    print("\n⚠️  No hay logs para esta sesión.")
            else:
                print("Selección inválida.")
        except ValueError:
            print("Entrada inválida.")
        finally:
            conn.close()

        input("\nPresione Enter para continuar...")

    def view_statistics(self):
        """Muestra estadísticas generales del sistema."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        print("\n" + "=" * 60)
        print("ESTADÍSTICAS DEL SISTEMA")
        print("=" * 60)

        # Total de logs por nivel
        cursor.execute(
            """
            SELECT level, COUNT(*) as count
            FROM logs
            GROUP BY level
            ORDER BY count DESC
        """
        )
        log_counts = cursor.fetchall()

        if log_counts:
            print("\n📊 Logs por nivel:")
            print(tabulate(log_counts, headers=["Nivel", "Cantidad"], tablefmt="grid"))

        # Módulos más activos
        cursor.execute(
            """
            SELECT module, COUNT(*) as count
            FROM logs
            GROUP BY module
            ORDER BY count DESC
            LIMIT 10
        """
        )
        module_counts = cursor.fetchall()

        if module_counts:
            print("\n📊 Top 10 módulos más activos:")
            print(tabulate(module_counts, headers=["Módulo", "Logs"], tablefmt="grid"))

        # Estadísticas de sesiones
        cursor.execute(
            """
            SELECT 
                COUNT(*) as total_sessions,
                COUNT(CASE WHEN end_time IS NOT NULL THEN 1 END) as completed_sessions,
                COUNT(CASE WHEN end_time IS NULL THEN 1 END) as active_sessions
            FROM sessions
        """
        )
        session_stats = cursor.fetchone()

        print("\n📊 Estadísticas de sesiones:")
        print(f"  Total de sesiones: {session_stats[0]}")
        print(f"  Sesiones completadas: {session_stats[1]}")
        print(f"  Sesiones activas: {session_stats[2]}")

        # Estadísticas del solver
        cursor.execute(
            """
            SELECT 
                COUNT(*) as total_problems,
                AVG(iterations) as avg_iterations,
                AVG(execution_time_ms) as avg_time,
                COUNT(CASE WHEN status = 'optimal' THEN 1 END) as optimal_count
            FROM solver_events
            WHERE event_type = 'solve_complete'
        """
        )
        solver_stats = cursor.fetchone()

        if solver_stats and solver_stats[0] > 0:
            print("\n📊 Estadísticas del Solver:")
            print(f"  Problemas resueltos: {solver_stats[0]}")
            print(f"  Iteraciones promedio: {solver_stats[1]:.2f if solver_stats[1] else 0}")
            print(f"  Tiempo promedio: {solver_stats[2]:.2f if solver_stats[2] else 0} ms")
            print(f"  Soluciones óptimas: {solver_stats[3]}")

        # Tamaño de la BD
        db_size = os.path.getsize(self.db_path) / (1024 * 1024)  # MB
        print(f"\n💾 Tamaño de la base de datos: {db_size:.2f} MB")

        conn.close()
        input("\nPresione Enter para continuar...")

    def view_solver_events(self):
        """Muestra eventos específicos del solver."""
        limit = int(input("Cantidad de eventos a mostrar (default: 20): ") or "20")

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT timestamp, event_type, problem_type, num_variables, 
                   num_constraints, iterations, status, optimal_value
            FROM solver_events
            ORDER BY timestamp DESC
            LIMIT ?
        """,
            (limit,),
        )

        events = cursor.fetchall()
        conn.close()

        if events:
            print(f"\n📋 Últimos {len(events)} eventos del solver:")
            print("-" * 120)
            headers = [
                "Timestamp",
                "Evento",
                "Tipo",
                "Vars",
                "Rest",
                "Iter",
                "Estado",
                "Valor",
            ]
            formatted_events = [
                (
                    event[0][:19],
                    event[1][:20],
                    event[2] or "",
                    event[3] or "",
                    event[4] or "",
                    event[5] or "",
                    event[6] or "",
                    f"{event[7]:.4f}" if event[7] else "",
                )
                for event in events
            ]
            print(tabulate(formatted_events, headers=headers, tablefmt="grid"))
        else:
            print("\n⚠️  No hay eventos del solver disponibles.")

        input("\nPresione Enter para continuar...")

    def view_file_operations(self):
        """Muestra operaciones con archivos."""
        limit = int(input("Cantidad de operaciones a mostrar (default: 20): ") or "20")

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT timestamp, operation_type, file_path, file_size, success, error_message
            FROM file_operations
            ORDER BY timestamp DESC
            LIMIT ?
        """,
            (limit,),
        )

        operations = cursor.fetchall()
        conn.close()

        if operations:
            print(f"\n📋 Últimas {len(operations)} operaciones con archivos:")
            print("-" * 120)
            headers = ["Timestamp", "Operación", "Archivo", "Tamaño", "Éxito", "Error"]
            formatted_ops = [
                (
                    op[0][:19],
                    op[1],
                    os.path.basename(op[2])[:30],
                    f"{op[3]} bytes" if op[3] else "",
                    "✓" if op[4] else "✗",
                    ((op[5][:30] + "...") if op[5] and len(op[5]) > 30 else (op[5] or "")),
                )
                for op in operations
            ]
            print(tabulate(formatted_ops, headers=headers, tablefmt="grid"))
        else:
            print("\n⚠️  No hay operaciones con archivos disponibles.")

        input("\nPresione Enter para continuar...")

    def search_logs(self):
        """Busca en los logs por texto."""
        search_term = input("Ingrese el término de búsqueda: ").strip()
        if not search_term:
            print("Término de búsqueda vacío.")
            return

        limit = int(input("Cantidad máxima de resultados (default: 50): ") or "50")

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT timestamp, level, module, function, message
            FROM logs
            WHERE message LIKE ? OR exception_message LIKE ?
            ORDER BY timestamp DESC
            LIMIT ?
        """,
            (f"%{search_term}%", f"%{search_term}%", limit),
        )

        results = cursor.fetchall()
        conn.close()

        if results:
            print(f"\n🔍 Resultados de búsqueda para '{search_term}':")
            print("-" * 120)
            headers = ["Timestamp", "Nivel", "Módulo", "Función", "Mensaje"]
            formatted_results = [
                (
                    result[0][:19],
                    result[1],
                    result[2][:20],
                    result[3][:20] if result[3] else "",
                    (result[4][:60] + "...") if len(result[4]) > 60 else result[4],
                )
                for result in results
            ]
            print(tabulate(formatted_results, headers=headers, tablefmt="grid"))
        else:
            print(f"\n⚠️  No se encontraron resultados para '{search_term}'.")

        input("\nPresione Enter para continuar...")

    def view_sessions(self):
        """Muestra información detallada de las sesiones."""
        limit = int(input("Cantidad de sesiones a mostrar (default: 10): ") or "10")

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT session_id, start_time, end_time, execution_mode, 
                   os_system, python_version
            FROM sessions
            ORDER BY start_time DESC
            LIMIT ?
        """,
            (limit,),
        )

        sessions = cursor.fetchall()
        conn.close()

        if sessions:
            print(f"\n📋 Últimas {len(sessions)} sesiones:")
            print("-" * 120)
            headers = ["Session ID", "Inicio", "Fin", "Modo", "OS", "Python"]
            formatted_sessions = [
                (
                    session[0][:20],
                    session[1][:19],
                    session[2][:19] if session[2] else "En curso",
                    session[3],
                    session[4],
                    session[5][:20],
                )
                for session in sessions
            ]
            print(tabulate(formatted_sessions, headers=headers, tablefmt="grid"))
        else:
            print("\n⚠️  No hay sesiones disponibles.")

        input("\nPresione Enter para continuar...")

    def export_logs(self):
        """Exporta logs a un archivo de texto."""
        filename = (
            input("Nombre del archivo de salida (default: logs_export.txt): ").strip()
            or "logs_export.txt"
        )

        days = int(input("Días de logs a exportar (default: 7): ") or "7")
        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT timestamp, level, module, function, message, exception_message, stack_trace
            FROM logs
            WHERE timestamp >= ?
            ORDER BY timestamp DESC
        """,
            (cutoff_date,),
        )

        logs = cursor.fetchall()
        conn.close()

        if logs:
            try:
                with open(filename, "w", encoding="utf-8") as f:
                    f.write("=" * 80 + "\n")
                    f.write("SIMPLEX SOLVER - EXPORTACIÓN DE LOGS\n")
                    f.write(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"Período: Últimos {days} días\n")
                    f.write(f"Total de logs: {len(logs)}\n")
                    f.write("=" * 80 + "\n\n")

                    for log in logs:
                        f.write(f"Timestamp: {log[0]}\n")
                        f.write(f"Nivel: {log[1]}\n")
                        f.write(f"Módulo: {log[2]}\n")
                        f.write(f"Función: {log[3]}\n")
                        f.write(f"Mensaje: {log[4]}\n")
                        if log[5]:
                            f.write(f"Excepción: {log[5]}\n")
                        if log[6]:
                            f.write(f"Stack Trace:\n{log[6]}\n")
                        f.write("-" * 80 + "\n\n")

                print(f"\n✓ Logs exportados exitosamente a: {filename}")
            except Exception as e:
                print(f"\n❌ Error al exportar logs: {e}")
        else:
            print(f"\n⚠️  No hay logs de los últimos {days} días.")

        input("\nPresione Enter para continuar...")

    def cleanup_old_logs(self):
        """Limpia logs antiguos manualmente."""
        days = int(input("Eliminar logs más antiguos que (días, default: 180): ") or "180")

        confirm = input(
            f"¿Está seguro de eliminar logs más antiguos que {days} días? (s/n): "
        ).lower()
        if confirm != "s":
            print("Operación cancelada.")
            return

        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("DELETE FROM logs WHERE timestamp < ?", (cutoff_date,))
            logs_deleted = cursor.rowcount

            cursor.execute("DELETE FROM solver_events WHERE timestamp < ?", (cutoff_date,))
            events_deleted = cursor.rowcount

            cursor.execute("DELETE FROM file_operations WHERE timestamp < ?", (cutoff_date,))
            files_deleted = cursor.rowcount

            cursor.execute("DELETE FROM sessions WHERE start_time < ?", (cutoff_date,))
            sessions_deleted = cursor.rowcount

            conn.commit()

            print(f"\n✓ Limpieza completada:")
            print(f"  - Logs eliminados: {logs_deleted}")
            print(f"  - Eventos eliminados: {events_deleted}")
            print(f"  - Operaciones de archivos eliminadas: {files_deleted}")
            print(f"  - Sesiones eliminadas: {sessions_deleted}")

            # VACUUM para liberar espacio
            cursor.execute("VACUUM")
            print("  - Base de datos compactada")

        except Exception as e:
            print(f"\n❌ Error durante la limpieza: {e}")
        finally:
            conn.close()

        input("\nPresione Enter para continuar...")


def main():
    """
    Punto de entrada principal para iniciar el visor de logs.
    Verifica la existencia de la base de datos y lanza el menú principal.
    """
    # Intentar obtener la ruta de la BD
    import sys
    from pathlib import Path

    if getattr(sys, "frozen", False):
        app_data = os.getenv("APPDATA") or os.path.expanduser("~")
        db_path = os.path.join(app_data, "SimplexSolver", "logs", "simplex_logs.db")
    else:
        db_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "logs", "simplex_logs.db"
        )

    if not os.path.exists(db_path):
        print(f"❌ No se encontró la base de datos de logs en: {db_path}")
        print("Asegúrese de haber ejecutado el programa al menos una vez.")
        return

    try:
        viewer = LogViewer(db_path)
        viewer.show_menu()
    except Exception as e:
        print(f"❌ Error al iniciar el visor de logs: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
