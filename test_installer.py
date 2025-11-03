#!/usr/bin/env python3
"""
Script de prueba del sistema de análisis y del instalador.
Ejecuta sin instalar nada, solo muestra información.
"""
import sys
from pathlib import Path

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from system_analyzer import SystemAnalyzer


def test_system_analyzer():
    """Prueba el analizador de sistema."""
    print("=" * 70)
    print(" " * 20 + "TEST DEL ANALIZADOR DE SISTEMA")
    print("=" * 70)

    # Crear analizador
    analyzer = SystemAnalyzer()

    # Mostrar información del sistema
    print("\n--- INFORMACIÓN DEL SISTEMA ---")
    info = analyzer.get_system_info()
    for key, value in info.items():
        print(f"  {key:20}: {value}")

    # Verificar compatibilidad con Ollama
    print("\n--- COMPATIBILIDAD CON OLLAMA ---")
    can_run, reason = analyzer.can_run_ollama()
    if can_run:
        print(f"  ✓ Compatible: {reason}")
    else:
        print(f"  ✗ No compatible: {reason}")

    # Mostrar recomendaciones de modelos
    print("\n--- RECOMENDACIONES DE MODELOS ---")
    recommendations = analyzer.get_model_recommendations()

    print("\nTodos los modelos:")
    for rec in recommendations:
        status = "✓ RECOMENDADO" if rec.recommended else "⚠ REQUIERE MÁS RAM"
        print(f"\n  {rec.name}")
        print(f"    Tamaño: {rec.size}")
        print(f"    RAM requerida: {rec.ram_required_gb} GB")
        print(f"    Descripción: {rec.description}")
        print(f"    Estado: {status}")
        print(f"    Razón: {rec.reason}")

    # Mostrar solo los recomendados
    print("\n--- MODELOS RECOMENDADOS PARA TU SISTEMA ---")
    recommended = analyzer.get_recommended_models()
    if recommended:
        for model in recommended:
            print(f"  • {model}")
    else:
        print("  No hay modelos recomendados para las capacidades actuales.")
        print("  Considera aumentar RAM o usar modelos más pequeños.")

    print("\n" + "=" * 70)


def test_installer_import():
    """Verifica que el instalador se pueda importar."""
    print("\n--- VERIFICACIÓN DE COMPONENTES ---")

    try:
        # El instalador usa paths relativos, verificar archivos
        installer_path = Path(__file__).parent / "installer.py"

        if installer_path.exists():
            print("  ✓ installer.py encontrado")
        else:
            print("  ✗ installer.py no encontrado")

        # Verificar archivos necesarios
        required_files = [
            "simplex.py",
            "requirements.txt",
            "context_menu/install.bat",
            "ejemplos/ejemplo_maximizacion.txt",
        ]

        for file_path in required_files:
            full_path = Path(__file__).parent / file_path
            if full_path.exists():
                print(f"  ✓ {file_path} encontrado")
            else:
                print(f"  ⚠ {file_path} no encontrado")

    except Exception as e:
        print(f"  ✗ Error: {e}")


def main():
    """Función principal."""
    try:
        test_system_analyzer()
        test_installer_import()

        print("\n" + "=" * 70)
        print("TEST COMPLETADO")
        print("=" * 70)
        print("\nEl instalador está listo para usar.")
        print("Ejecuta: python installer.py")
        print("O genera el .exe con: python build_installer.py")

    except Exception as e:
        print(f"\n✗ Error durante las pruebas: {e}")
        import traceback

        traceback.print_exc()
        return False

    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
