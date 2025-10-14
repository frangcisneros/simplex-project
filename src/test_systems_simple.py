"""
test_systems_simple.py - Test simple de los sistemas NLP

Compara Regex y spaCy side-by-side.
"""

import sys
import time
from pathlib import Path

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent))


def test_regex(problem_text):
    """Test con Regex Parser"""
    print("\n" + "=" * 60)
    print("TEST 1: REGEX PARSER")
    print("=" * 60)

    try:
        from regex_parser import RegexOptimizationProcessor

        processor = RegexOptimizationProcessor()

        start = time.time()
        result = processor.process_text(problem_text)
        elapsed = time.time() - start

        print(f"⏱️  Tiempo: {elapsed * 1000:.2f} ms")
        print(f"✓ Success: {result.success}")

        if result.success and result.problem:
            prob = result.problem
            print(f"   Tipo: {prob.objective_type}")
            print(f"   Variables: {prob.variable_names}")
            print(f"   Coeficientes: {prob.objective_coefficients}")
            print(f"   Restricciones: {len(prob.constraints)}")
            print(f"   Confianza: {result.confidence_score:.2%}")
        elif result.error_message:
            print(f"✗ Error: {result.error_message}")

        return result, elapsed

    except ImportError as e:
        print(f"✗ Error de importación: {e}")
        return None, 0
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback

        traceback.print_exc()
        return None, 0


def test_spacy(problem_text):
    """Test con spaCy NER"""
    print("\n" + "=" * 60)
    print("TEST 2: SPACY NER")
    print("=" * 60)

    try:
        from spacy_nlp import SpacyNLPProcessor

        # Intentar con modelo entrenado
        model_path = Path(__file__).parent / "spacy_nlp" / "models" / "optimization_ner"

        if model_path.exists():
            print(f"ℹ️  Usando modelo entrenado")
            processor = SpacyNLPProcessor(model_path=str(model_path))
        else:
            print(f"ℹ️  Usando pattern matching (sin modelo entrenado)")
            processor = SpacyNLPProcessor()

        start = time.time()
        result = processor.process_text(problem_text)
        elapsed = time.time() - start

        print(f"⏱️  Tiempo: {elapsed:.2f} s")
        print(f"✓ Success: {result.success}")

        if result.success and result.problem:
            prob = result.problem
            print(f"   Tipo: {prob.objective_type}")
            print(f"   Variables: {prob.variable_names}")
            print(f"   Coeficientes: {prob.objective_coefficients}")
            print(f"   Restricciones: {len(prob.constraints)}")
            print(f"   Confianza: {result.confidence_score:.2%}")
        elif result.error_message:
            print(f"✗ Error: {result.error_message}")

        return result, elapsed

    except ImportError as e:
        print(f"✗ Error de importación: {e}")
        print("   Instalar con: pip install spacy")
        return None, 0
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback

        traceback.print_exc()
        return None, 0


def main():
    print("\n" + "=" * 60)
    print("  TEST COMPARATIVO: REGEX vs SPACY")
    print("=" * 60)

    # Problema simple
    problem_simple = """
Maximizar Z = 3x + 2y
sujeto a:
2x + y <= 100
x + 2y <= 80
x, y >= 0
"""

    # Problema complejo
    problem_complex = """
Una empresa fabrica sillas y mesas.
Maximizar ganancia = 50*silla + 40*mesa

Restricciones:
3*silla + 5*mesa <= 150 (horas de trabajo)
2*silla + 4*mesa <= 100 (material)
silla >= 0
mesa >= 0
"""

    # Test con problema simple
    print("\n" + "#" * 60)
    print("  PROBLEMA 1: SIMPLE (formato matemático)")
    print("#" * 60)
    print(problem_simple)

    result_regex_1, time_regex_1 = test_regex(problem_simple)
    result_spacy_1, time_spacy_1 = test_spacy(problem_simple)

    # Comparación
    print("\n" + "=" * 60)
    print("COMPARACIÓN")
    print("=" * 60)
    if time_regex_1 > 0 and time_spacy_1 > 0:
        speedup = time_spacy_1 / time_regex_1
        print(f"Regex:  {time_regex_1 * 1000:>8.2f} ms")
        print(f"spaCy:  {time_spacy_1:>8.2f} s  ({speedup:.0f}x más lento)")

        if result_regex_1 and result_regex_1.success:
            print("✓ Recomendación: Usar Regex (más rápido con buena precisión)")
        elif result_spacy_1 and result_spacy_1.success:
            print("✓ Recomendación: Usar spaCy (mejor comprensión)")

    # Test con problema complejo
    print("\n\n" + "#" * 60)
    print("  PROBLEMA 2: COMPLEJO (lenguaje natural)")
    print("#" * 60)
    print(problem_complex)

    result_regex_2, time_regex_2 = test_regex(problem_complex)
    result_spacy_2, time_spacy_2 = test_spacy(problem_complex)

    # Comparación
    print("\n" + "=" * 60)
    print("COMPARACIÓN")
    print("=" * 60)
    if time_regex_2 > 0 and time_spacy_2 > 0:
        speedup = time_spacy_2 / time_regex_2
        print(f"Regex:  {time_regex_2 * 1000:>8.2f} ms")
        print(f"spaCy:  {time_spacy_2:>8.2f} s  ({speedup:.0f}x más lento)")

        if result_regex_2 and result_regex_2.success:
            print("✓ Recomendación: Usar Regex")
        elif result_spacy_2 and result_spacy_2.success:
            print("✓ Recomendación: Usar spaCy (maneja lenguaje natural mejor)")

    # Resumen final
    print("\n" + "=" * 60)
    print("  RESUMEN")
    print("=" * 60)
    print("\n📊 RESULTADOS:")
    print(
        f"   Regex:  Simple={result_regex_1.success if result_regex_1 else False}, Complejo={result_regex_2.success if result_regex_2 else False}"
    )
    print(
        f"   spaCy:  Simple={result_spacy_1.success if result_spacy_1 else False}, Complejo={result_spacy_2.success if result_spacy_2 else False}"
    )

    print("\n💡 RECOMENDACIONES:")
    print("   • Desarrollo/Testing → Usar Regex (velocidad)")
    print("   • Producción → Usar spaCy (balance)")
    print("   • Lenguaje muy informal → Usar LLM (no probado aquí)")

    print("\n📖 Más info: COMPARACION_SISTEMAS.md")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
