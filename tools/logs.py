#!/usr/bin/env python3
"""
Herramienta Unificada de Gestión de Logs para el Solver Simplex
===============================================================

Esta herramienta consolida la visualización y verificación de logs.
Proporciona tanto estadísticas rápidas como una funcionalidad detallada de visualización de logs.

Uso:
    python tools/logs.py                # Lanzar visor interactivo (por defecto)
    python tools/logs.py --stats        # Mostrar estadísticas rápidas
    python tools/logs.py --verify       # Verificar la integridad del sistema de logs

Autor: Francisco Cisneros
"""

import sys
import os
import argparse
from pathlib import Path

# Agregar el directorio padre al path para las importaciones
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from simplex_solver.log_viewer import LogViewer


def get_db_path() -> Path:
    """Obtener la ruta a la base de datos de logs."""
    return Path.home() / "AppData" / "Roaming" / "SimplexSolver" / "logs" / "simplex_logs.db"


def verify_logs() -> int:
    """Verificar la integridad del sistema de logs y mostrar estadísticas."""
    import sqlite3

    db_path = get_db_path()

    print("=" * 70)
    print("VERIFICACIÓN DEL SISTEMA DE LOGS")
    print("=" * 70)
    print(f"\nRuta de la base de datos: {db_path}")
    print(f"Existe: {'[SÍ]' if db_path.exists() else '[NO]'}")

    if not db_path.exists():
        print("\n[ADVERTENCIA] La base de datos aún no existe.")
        print("Ejecute el programa al menos una vez para generar logs.")
        return 1

    # Tamaño de la base de datos
    size = db_path.stat().st_size
    print(f"Tamaño: {size:,} bytes ({size/1024:.2f} KB)")

    # Conectar a la base de datos
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        print("\n" + "=" * 70)
        print("ESTADÍSTICAS")
        print("=" * 70)

        # Total de logs
        cursor.execute("SELECT COUNT(*) FROM logs")
        total_logs = cursor.fetchone()[0]
        print(f"\n[ESTADÍSTICAS] Total de logs: {total_logs}")

        # Logs por nivel
        cursor.execute(
            """
            SELECT level, COUNT(*) as count 
            FROM logs 
            GROUP BY level 
            ORDER BY count DESC
        """
        )
        print("\n[ESTADÍSTICAS] Logs por nivel:")
        for level, count in cursor.fetchall():
            print(f"   {level:10} : {count:4} logs")

        # Sesiones
        cursor.execute("SELECT COUNT(*) FROM sessions")
        total_sessions = cursor.fetchone()[0]
        print(f"\n[ESTADÍSTICAS] Total de sesiones: {total_sessions}")

        # Eventos del solver
        cursor.execute('SELECT COUNT(*) FROM solver_events WHERE event_type="solve_complete"')
        problems_solved = cursor.fetchone()[0]
        print(f"[ESTADÍSTICAS] Problemas resueltos: {problems_solved}")

        # Última sesión
        cursor.execute(
            """
            SELECT session_id, start_time, end_time 
            FROM sessions 
            ORDER BY start_time DESC 
            LIMIT 1
        """
        )
        last_session = cursor.fetchone()
        if last_session:
            print(f"\n[INFO] Última sesión:")
            print(f"   ID: {last_session[0]}")
            print(f"   Inicio: {last_session[1][:19]}")
            print(f"   Fin: {last_session[2][:19] if last_session[2] else 'En progreso'}")

        # Últimos 5 logs
        print("\n" + "=" * 70)
        print("ÚLTIMOS 5 LOGS")
        print("=" * 70)
        cursor.execute(
            """
            SELECT timestamp, level, module, message 
            FROM logs 
            ORDER BY timestamp DESC 
            LIMIT 5
        """
        )

        for row in cursor.fetchall():
            timestamp = row[0][:19]
            level = row[1]
            module = row[2][:20]
            message = row[3][:60]
            print(f"\n[{timestamp}] [{level}] {module}")
            print(f"  → {message}")

        # Último problema resuelto
        print("\n" + "=" * 70)
        print("ÚLTIMO PROBLEMA RESUELTO")
        print("=" * 70)
        cursor.execute(
            """
            SELECT timestamp, problem_type, num_variables, num_constraints, 
                   iterations, execution_time_ms, status, optimal_value
            FROM solver_events 
            WHERE event_type = 'solve_complete'
            ORDER BY timestamp DESC 
            LIMIT 1
        """
        )

        result = cursor.fetchone()
        if result:
            print(f"\n⏰ Timestamp: {result[0][:19]}")
            print(f"📝 Tipo: {result[1]}")
            print(f"🔢 Variables: {result[2]}, Restricciones: {result[3]}")
            print(f"🔄 Iteraciones: {result[4]}")
            print(f"⚡ Tiempo: {result[5]:.2f} ms")
            print(f"✅ Estado: {result[6]}")
            if result[7]:
                print(f"🎯 Valor óptimo: {result[7]:.6f}")
        else:
            print("\n⚠️  No se han resuelto problemas aún.")

        conn.close()

        print("\n" + "=" * 70)
        print("✓ VERIFICACIÓN COMPLETA")
        print("=" * 70)
        print("\n¡El sistema de logs está funcionando correctamente!")
        print("\nPara una vista detallada, ejecute: python tools/logs.py")

        return 0

    except Exception as e:
        print(f"\n✗ Error al acceder a la base de datos: {e}")
        return 1


def show_stats() -> int:
    """Mostrar estadísticas rápidas sin lanzar el visor completo."""
    import sqlite3

    db_path = get_db_path()

    if not db_path.exists():
        print("[ADVERTENCIA] No se encontró la base de datos de logs. Ejecute el solver primero.")
        return 1

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Estadísticas rápidas
        cursor.execute("SELECT COUNT(*) FROM logs")
        total_logs = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM sessions")
        total_sessions = cursor.fetchone()[0]

        cursor.execute('SELECT COUNT(*) FROM solver_events WHERE event_type="solve_complete"')
        problems_solved = cursor.fetchone()[0]

        print("\n[ESTADÍSTICAS] Estadísticas rápidas:")
        print(f"   Logs: {total_logs}")
        print(f"   Sesiones: {total_sessions}")
        print(f"   Problemas resueltos: {problems_solved}")

        # Actividad reciente
        cursor.execute(
            """
            SELECT level, COUNT(*) 
            FROM logs 
            WHERE datetime(timestamp) > datetime('now', '-1 day')
            GROUP BY level
        """
        )
        recent = cursor.fetchall()

        if recent:
            print("\n[ESTADÍSTICAS] Últimas 24 horas:")
            for level, count in recent:
                print(f"   {level}: {count}")

        conn.close()
        return 0

    except Exception as e:
        print(f"[ERROR] {e}")
        return 1


def launch_viewer() -> int:
    """Lanzar el visor interactivo de logs."""
    try:
        db_path = get_db_path()
        if not db_path.exists():
            print(
                "[ADVERTENCIA] No se encontró la base de datos de logs. Ejecute el solver primero."
            )
            return 1

        viewer = LogViewer(str(db_path))
        viewer.show_menu()
        return 0
    except Exception as e:
        print(f"[ERROR] Error al lanzar el visor: {e}")
        import traceback

        traceback.print_exc()
        return 1


def main() -> int:
    """Punto de entrada principal."""
    parser = argparse.ArgumentParser(
        description="Herramienta unificada de gestión de logs para el Solver Simplex",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  python tools/logs.py              # Lanzar visor interactivo
  python tools/logs.py --stats      # Mostrar estadísticas rápidas
  python tools/logs.py --verify     # Verificar la integridad del sistema
        """,
    )

    parser.add_argument("--stats", action="store_true", help="Mostrar estadísticas rápidas")
    parser.add_argument(
        "--verify", action="store_true", help="Verificar la integridad del sistema de logs"
    )

    args = parser.parse_args()

    if args.verify:
        return verify_logs()
    elif args.stats:
        return show_stats()
    else:
        # Por defecto: lanzar visor interactivo
        return launch_viewer()


if __name__ == "__main__":
    sys.exit(main())
