"""
Script de prueba para el sistema de historial.
Verifica que todo funciona correctamente.
"""

import sys
import os

# Agregar src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from problem_history import ProblemHistory


def test_history():
    """Prueba las funcionalidades del historial."""
    history = ProblemHistory()

    print("=" * 80)
    print("TEST DEL SISTEMA DE HISTORIAL")
    print("=" * 80)

    # Test 1: Obtener todos los problemas
    print("\n1. Obteniendo todos los problemas...")
    problems = history.get_all_problems()
    print(f"   ✓ Encontrados: {len(problems)} problema(s)")

    if problems:
        print("\n2. Mostrando tabla de problemas...")
        history.display_problems_table(problems)

        print("\n3. Obteniendo detalles del primer problema...")
        first_id = problems[0]["id"]
        problem = history.get_problem_by_id(first_id)
        if problem:
            print(f"   ✓ Problema #{first_id} encontrado")
            history.display_problem_detail(problem)

        print("\n4. Creando archivo temporal del problema...")
        temp_file = history.create_temp_file_from_history(first_id)
        if temp_file:
            print(f"   ✓ Archivo temporal creado: {temp_file}")
            print(f"   ✓ Existe: {os.path.exists(temp_file)}")

            # Limpiar archivo temporal
            try:
                os.remove(temp_file)
                print(f"   ✓ Archivo temporal eliminado")
            except:
                pass
    else:
        print("\n⚠️  No hay problemas en el historial.")
        print("   Ejecuta el programa al menos una vez para crear historial.")

    # Test 5: Estadísticas
    print("\n5. Obteniendo estadísticas...")
    stats = history.get_statistics()
    print(f"   ✓ Total de problemas: {stats['total_problems']}")
    print(f"   ✓ Promedio de iteraciones: {stats['avg_iterations']:.2f}")
    print(f"   ✓ Promedio de tiempo: {stats['avg_execution_time']:.2f} ms")

    print("\n" + "=" * 80)
    print("✓ TODOS LOS TESTS COMPLETADOS")
    print("=" * 80)


if __name__ == "__main__":
    test_history()
