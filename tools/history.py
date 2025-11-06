#!/usr/bin/env python3
"""
Herramienta Unificada de Gestión de Historial para el Solver Simplex
===================================================================

Esta herramienta consolida la visualización y prueba del historial.
Proporciona tanto un menú interactivo como capacidades de diagnóstico.

Uso:
    python tools/history.py             # Lanzar menú interactivo (por defecto)
    python tools/history.py --test      # Probar el sistema de historial
    python tools/history.py --stats     # Mostrar estadísticas rápidas

Autor: Francisco Cisneros
"""

import sys
import os
import argparse
from pathlib import Path

# Agregar el directorio padre al path para las importaciones
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from simplex_solver.problem_history import ProblemHistory, show_history_menu


def test_history() -> int:
    """Probar la funcionalidad del sistema de historial."""
    print("=" * 80)
    print("PRUEBA DEL SISTEMA DE HISTORIAL")
    print("=" * 80)

    try:
        history = ProblemHistory()

        # Prueba 1: Obtener todos los problemas
        print("\n1. Recuperando todos los problemas...")
        problems = history.get_all_problems()
        print(f"   [OK] Encontrados: {len(problems)} problema(s)")

        if not problems:
            print("\n[ADVERTENCIA] No hay problemas en el historial aún.")
            print("   Resuelve un problema primero para llenar el historial.")
            return 0

        # Prueba 2: Mostrar tabla de problemas
        print("\n2. Mostrando tabla de problemas...")
        history.display_problems_table(problems)

        # Prueba 3: Obtener detalles del primer problema
        print("\n3. Recuperando detalles del primer problema...")
        first_id = problems[0]["id"]
        problem = history.get_problem_by_id(first_id)
        if problem:
            print(f"   [OK] Problema #{first_id} encontrado")
            history.display_problem_detail(problem)
        else:
            print(f"   [ERROR] Problema #{first_id} no encontrado")
            return 1

        # Prueba 4: Crear archivo temporal
        print("\n4. Creando archivo temporal desde el problema...")
        temp_file = history.create_temp_file_from_history(first_id)
        if temp_file:
            print(f"   [OK] Archivo temporal creado: {temp_file}")
            print(f"   [OK] Existe: {os.path.exists(temp_file)}")

            # Limpiar
            try:
                os.remove(temp_file)
                print(f"   [OK] Archivo temporal eliminado")
            except Exception as e:
                print(f"   [ADVERTENCIA] No se pudo eliminar el archivo temporal: {e}")
        else:
            print(f"   [ERROR] Falló la creación del archivo temporal")
            return 1

        # Prueba 5: Estadísticas
        print("\n5. Calculando estadísticas...")
        total = len(problems)
        optimal = sum(1 for p in problems if p.get("status") == "optimal")
        infeasible = sum(1 for p in problems if p.get("status") == "infeasible")
        unbounded = sum(1 for p in problems if p.get("status") == "unbounded")

        print(f"   Problemas totales: {total}")
        print(f"   Óptimos: {optimal}")
        print(f"   Infactibles: {infeasible}")
        print(f"   No acotados: {unbounded}")

        print("\n" + "=" * 80)
        print("[OK] TODAS LAS PRUEBAS PASARON")
        print("=" * 80)

        return 0

    except Exception as e:
        print(f"\n[ERROR] Prueba fallida: {e}")
        import traceback

        traceback.print_exc()
        return 1


def show_stats() -> int:
    """Mostrar estadísticas rápidas sobre el historial de problemas."""
    try:
        history = ProblemHistory()
        problems = history.get_all_problems()

        if not problems:
            print("[ADVERTENCIA] No hay problemas en el historial aún.")
            return 0

        # Calcular estadísticas
        total = len(problems)
        optimal = sum(1 for p in problems if p.get("status") == "optimal")
        max_vars = max((p.get("num_variables", 0) for p in problems), default=0)
        max_constraints = max((p.get("num_constraints", 0) for p in problems), default=0)

        # Problemas recientes
        recent = problems[:5]  # Primeros 5 (asumiendo que están ordenados por fecha DESC)

        print("\n[ESTADÍSTICAS] Estadísticas del Historial:")
        print(f"   Problemas totales: {total}")
        print(f"   Soluciones óptimas: {optimal} ({optimal/total*100:.1f}%)")
        print(f"   Máx. variables: {max_vars}")
        print(f"   Máx. restricciones: {max_constraints}")

        if recent:
            print("\n[INFO] Problemas recientes:")
            for p in recent:
                date = p.get("solved_at", "Desconocido")[:10]  # Solo la fecha
                status = p.get("status", "Desconocido")
                vars_count = p.get("num_variables", 0)
                print(f"   [{date}] {status} - {vars_count} variables")

        return 0

    except Exception as e:
        print(f"[ERROR] {e}")
        return 1


def launch_interactive_menu() -> int:
    """Lanzar el menú interactivo del historial."""
    try:
        temp_file = show_history_menu()

        if temp_file:
            # El usuario desea resolver nuevamente un problema
            print("\n¿Deseas ejecutar el Simplex Solver con este problema? (s/n)")
            choice = input().strip().lower()

            if choice == "s":
                print(f"\nEjecutando: python simplex.py {temp_file}")
                os.system(f'python simplex.py "{temp_file}"')
            else:
                print(f"\nPuedes ejecutarlo manualmente con:")
                print(f'python simplex.py "{temp_file}"')

        return 0

    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback

        traceback.print_exc()
        return 1


def main() -> int:
    """Punto de entrada principal."""
    parser = argparse.ArgumentParser(
        description="Herramienta unificada de gestión de historial para el Solver Simplex",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  python tools/history.py           # Lanzar menú interactivo
  python tools/history.py --test    # Probar el sistema de historial
  python tools/history.py --stats   # Mostrar estadísticas rápidas
        """,
    )

    parser.add_argument(
        "--test", action="store_true", help="Probar la funcionalidad del sistema de historial"
    )
    parser.add_argument("--stats", action="store_true", help="Mostrar estadísticas rápidas")

    args = parser.parse_args()

    if args.test:
        return test_history()
    elif args.stats:
        return show_stats()
    else:
        # Por defecto: lanzar menú interactivo
        return launch_interactive_menu()


if __name__ == "__main__":
    sys.exit(main())
