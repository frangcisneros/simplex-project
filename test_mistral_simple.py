"""
Test rápido solo con Mistral para verificar que el prompt funciona.
"""

import sys
from pathlib import Path

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from nlp import OllamaNLPProcessor, NLPModelType


def test_mistral_only():
    print("🧪 Probando solo Mistral con prompt mejorado...")

    # Cargar problema
    problem_file = Path("ejemplos/nlp/problema_complejo.txt")
    if not problem_file.exists():
        print("❌ No se encontró el archivo del problema")
        return

    problem_text = problem_file.read_text(encoding="utf-8")
    print(f"📄 Problema: {len(problem_text)} caracteres")

    # Crear procesador
    processor = OllamaNLPProcessor(model_type=NLPModelType.MISTRAL_7B)

    # Verificar disponibilidad
    if not processor.is_available():
        print("❌ Mistral no está disponible")
        return

    print("✅ Mistral está disponible")
    print("🔄 Generando respuesta...")

    # Procesar
    result = processor.process_text(problem_text)

    if result.success:
        print("🎉 ¡ÉXITO!")
        print(f"📊 Confianza: {result.confidence_score:.2%}")
        if result.problem:
            print(f"🎯 Objetivo: {result.problem.objective_type}")
            print(f"📈 Variables: {len(result.problem.objective_coefficients)}")
            print(f"📋 Restricciones: {len(result.problem.constraints)}")
            print(f"🏷️  Nombres: {result.problem.variable_names}")
    else:
        print("❌ Falló:")
        print(f"   {result.error_message}")


if __name__ == "__main__":
    test_mistral_only()
