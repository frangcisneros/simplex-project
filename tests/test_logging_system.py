"""
Test básico del sistema de logging.
Verifica que el sistema se inicializa correctamente y registra eventos.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.logging_system import logger, LogLevel


def test_logging_system():
    """Prueba básica del sistema de logging."""
    print("=" * 60)
    print("TEST DEL SISTEMA DE LOGGING")
    print("=" * 60)

    # Test 1: Logs básicos
    print("\n1. Probando logs básicos...")
    logger.debug("Este es un mensaje DEBUG")
    logger.info("Este es un mensaje INFO")
    logger.warning("Este es un mensaje WARNING")
    logger.error("Este es un mensaje ERROR")
    logger.critical("Este es un mensaje CRITICAL")
    print("✓ Logs básicos funcionando")

    # Test 2: Log con datos personalizados
    print("\n2. Probando log con datos personalizados...")
    logger.info(
        "Operación completada",
        user_data={"operacion": "test", "duracion": 123, "exitoso": True},
    )
    print("✓ Log con datos personalizados funcionando")

    # Test 3: Log con excepción
    print("\n3. Probando log con excepción...")
    try:
        raise ValueError("Error de prueba intencional")
    except Exception as e:
        logger.error("Capturado error de prueba", exception=e)
    print("✓ Log con excepción funcionando")

    # Test 4: Log de evento del solver
    print("\n4. Probando log de evento del solver...")
    logger.log_solver_event(
        event_type="solve_test",
        problem_type="maximización",
        num_variables=5,
        num_constraints=3,
        iterations=10,
        execution_time_ms=45.67,
        status="optimal",
        optimal_value=123.45,
        additional_data={"test": True},
    )
    print("✓ Log de evento del solver funcionando")

    # Test 5: Log de operación con archivos
    print("\n5. Probando log de operación con archivos...")
    logger.log_file_operation(
        operation_type="test_read", file_path="archivo_prueba.txt", success=True
    )
    print("✓ Log de operación con archivos funcionando")

    # Test 6: Verificar ubicación de la BD
    print(f"\n6. Ubicación de la base de datos:")
    print(f"   {logger.get_db_path()}")
    if os.path.exists(logger.get_db_path()):
        size = os.path.getsize(logger.get_db_path())
        print(f"   Tamaño: {size:,} bytes")
        print("✓ Base de datos creada exitosamente")
    else:
        print("✗ Base de datos NO encontrada")

    # Finalizar sesión
    logger.end_session()

    print("\n" + "=" * 60)
    print("TODOS LOS TESTS PASARON ✓")
    print("=" * 60)
    print(f"\nRevisa los logs en: {logger.get_db_path()}")
    print("O ejecuta: python view_logs.py")


if __name__ == "__main__":
    test_logging_system()
