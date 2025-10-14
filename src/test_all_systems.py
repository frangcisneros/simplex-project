"""
test_all_systems.py - Compara los 3 sistemas de parsing NLP

Este script prueba y compara:
1. Regex Parser (instantáneo)
2. spaCy NER (1-2 segundos)
3. LLM/Ollama (5+ minutos) - opcional

Ejecutar:
    python test_all_systems.py
"""

import time
import sys
from pathlib import Path

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent))


# Colores para terminal
class Colors:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"


def print_header(text):
    print(f"\n{Colors.HEADER}{'=' * 60}{Colors.ENDC}")
    print(f"{Colors.BOLD}{text}{Colors.ENDC}")
    print(f"{Colors.HEADER}{'=' * 60}{Colors.ENDC}\n")


def print_success(text):
    print(f"{Colors.OKGREEN}✓ {text}{Colors.ENDC}")


def print_error(text):
    print(f"{Colors.FAIL}✗ {text}{Colors.ENDC}")


def print_info(text):
    print(f"{Colors.OKCYAN}ℹ {text}{Colors.ENDC}")


def format_time(seconds):
    """Formatea tiempo de manera legible"""
    if seconds < 0.001:
        return f"{seconds * 1000000:.0f} µs"
    elif seconds < 1:
        return f"{seconds * 1000:.2f} ms"
    else:
        return f"{seconds:.2f} s"


def test_regex(problema):
    """Test del sistema Regex"""
    print_header("TEST 1: REGEX PARSER")

    try:
        from regex_parser import RegexNLPProcessor

        processor = RegexNLPProcessor()

        start = time.time()
        result = processor.process_text(problema)
        elapsed = time.time() - start

        print(f"⏱️  Tiempo: {format_time(elapsed)}")

        if result.get("success"):
            print_success("Procesamiento exitoso")
            print(f"   Variables: {result.get('variable_names', [])}")
            print(
                f"   Coeficientes objetivo: {result.get('objective_coefficients', [])}"
            )
            print(f"   Tipo: {result.get('objective_type', 'N/A')}")
            print(f"   Restricciones: {len(result.get('constraints', []))}")
            print(f"   Confianza: {result.get('confidence', 0):.2%}")
        else:
            print_error(f"Fallo: {result.get('error', 'Error desconocido')}")

        return result, elapsed

    except ImportError:
        print_error("Regex parser no disponible")
        return None, 0
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return None, 0


def test_spacy(problema):
    """Test del sistema spaCy"""
    print_header("TEST 2: SPACY NER")

    try:
        from spacy_nlp import SpacyNLPProcessor

        # Intentar con modelo entrenado primero
        model_path = Path(__file__).parent / "spacy_nlp" / "models" / "optimization_ner"

        if model_path.exists():
            print_info(f"Usando modelo entrenado: {model_path}")
            processor = SpacyNLPProcessor(model_path=str(model_path))
        else:
            print_info("Usando pattern matching (sin modelo entrenado)")
            processor = SpacyNLPProcessor()

        start = time.time()
        result = processor.process_text(problema)
        elapsed = time.time() - start

        print(f"⏱️  Tiempo: {format_time(elapsed)}")

        if result.get("success"):
            print_success("Procesamiento exitoso")
            print(f"   Variables: {result.get('variable_names', [])}")
            print(
                f"   Coeficientes objetivo: {result.get('objective_coefficients', [])}"
            )
            print(f"   Tipo: {result.get('objective_type', 'N/A')}")
            print(f"   Restricciones: {len(result.get('constraints', []))}")
            print(f"   Confianza: {result.get('confidence', 0):.2%}")

            # Info adicional de spaCy
            entities = result.get("entities", [])
            patterns = result.get("patterns", [])
            print(f"   Entidades detectadas: {len(entities)}")
            print(f"   Patrones encontrados: {len(patterns)}")
        else:
            print_error(f"Fallo: {result.get('error', 'Error desconocido')}")

        return result, elapsed

    except ImportError:
        print_error("spaCy no disponible. Instalar con: pip install spacy")
        return None, 0
    except Exception as e:
        print_error(f"Error: {str(e)}")
        import traceback

        traceback.print_exc()
        return None, 0


def test_llm(problema, skip=True):
    """Test del sistema LLM (opcional, muy lento)"""
    print_header("TEST 3: LLM (OLLAMA)")

    if skip:
        print_info("Test de LLM omitido (tarda 5+ minutos)")
        print_info("Para ejecutarlo, pasar skip=False")
        return None, 0

    try:
        from nlp import NLPConnector

        print_info("Iniciando procesamiento con LLM...")
        print_info("⚠️  Esto puede tardar varios minutos...")

        connector = NLPConnector(model_name="mistral", timeout=300)  # o "llama3.1:8b"

        start = time.time()
        result = connector.process_and_solve(problema)
        elapsed = time.time() - start

        print(f"⏱️  Tiempo: {format_time(elapsed)}")

        if result.get("success"):
            print_success("Procesamiento exitoso")
            extracted = result.get("extracted_problem", {})
            print(f"   Variables: {extracted.get('variable_names', [])}")
            print(
                f"   Coeficientes objetivo: {extracted.get('objective_coefficients', [])}"
            )
            print(f"   Tipo: {extracted.get('objective_type', 'N/A')}")
            print(f"   Restricciones: {len(extracted.get('constraints', []))}")
            print(f"   Confianza: {result.get('nlp_confidence', 0):.2%}")
        else:
            print_error(f"Fallo: {result.get('error', 'Error desconocido')}")

        return result, elapsed

    except ImportError:
        print_error("NLP connector no disponible")
        return None, 0
    except Exception as e:
        print_error(f"Error: {str(e)}")
        import traceback

        traceback.print_exc()
        return None, 0


def test_hybrid(problema):
    """Test del sistema híbrido (usa el mejor disponible)"""
    print_header("TEST 4: SISTEMA HÍBRIDO")

    results = []
    total_time = 0

    # 1. Probar Regex primero
    print("📍 Paso 1: Probando Regex...")
    result_regex, time_regex = test_regex_silent(problema)
    results.append(("Regex", result_regex, time_regex))
    total_time += time_regex

    if (
        result_regex
        and result_regex.get("success")
        and result_regex.get("confidence", 0) > 0.85
    ):
        print_success(
            f"Regex exitoso con confianza {result_regex.get('confidence', 0):.2%}"
        )
        print(f"⏱️  Tiempo total: {format_time(total_time)}")
        return result_regex, total_time, "Regex"
    else:
        print_info("Regex insuficiente, probando spaCy...")

    # 2. Probar spaCy
    print("\n📍 Paso 2: Probando spaCy...")
    result_spacy, time_spacy = test_spacy_silent(problema)
    results.append(("spaCy", result_spacy, time_spacy))
    total_time += time_spacy

    if (
        result_spacy
        and result_spacy.get("success")
        and result_spacy.get("confidence", 0) > 0.75
    ):
        print_success(
            f"spaCy exitoso con confianza {result_spacy.get('confidence', 0):.2%}"
        )
        print(f"⏱️  Tiempo total: {format_time(total_time)}")
        return result_spacy, total_time, "spaCy"
    else:
        print_info("spaCy insuficiente, se necesitaría LLM...")

    # 3. LLM sería el siguiente paso (pero no lo ejecutamos por el tiempo)
    print("\n📍 Paso 3: LLM disponible pero no ejecutado (demasiado lento)")
    print_info("En producción, aquí se usaría el LLM como último recurso")

    # Retornar el mejor resultado disponible
    best_result = None
    best_system = None

    for system, result, _ in results:
        if result and result.get("success"):
            best_result = result
            best_system = system
            break

    print(f"\n⏱️  Tiempo total: {format_time(total_time)}")

    if best_result:
        print_success(f"Mejor resultado: {best_system}")
        return best_result, total_time, best_system
    else:
        print_error("Ningún sistema pudo procesar el problema")
        return None, total_time, None


def test_regex_silent(problema):
    """Versión silenciosa del test de regex"""
    try:
        from regex_parser import RegexNLPProcessor

        processor = RegexNLPProcessor()
        start = time.time()
        result = processor.process(problema)
        elapsed = time.time() - start
        return result, elapsed
    except:
        return None, 0


def test_spacy_silent(problema):
    """Versión silenciosa del test de spacy"""
    try:
        from spacy_nlp import SpacyNLPProcessor

        model_path = Path(__file__).parent / "spacy_nlp" / "models" / "optimization_ner"
        if model_path.exists():
            processor = SpacyNLPProcessor(model_path=str(model_path))
        else:
            processor = SpacyNLPProcessor()
        start = time.time()
        result = processor.process(problema)
        elapsed = time.time() - start
        return result, elapsed
    except:
        return None, 0


def print_comparison(times):
    """Imprime comparación de tiempos"""
    print_header("COMPARACIÓN DE RENDIMIENTO")

    if not times:
        print_info("No hay datos para comparar")
        return

    # Encontrar el más rápido
    fastest = min(times.values())

    for system, time_val in times.items():
        if time_val > 0:
            speedup = time_val / fastest if fastest > 0 else 1
            print(f"{system:15s}: {format_time(time_val):>12s}  ({speedup:.0f}x)")
        else:
            print(f"{system:15s}: {'N/A':>12s}")


def main():
    """Función principal"""
    print(f"\n{Colors.BOLD}{'=' * 60}")
    print("  TEST COMPARATIVO DE SISTEMAS NLP")
    print(f"{'=' * 60}{Colors.ENDC}\n")

    # Problema de ejemplo
    problema_simple = """
    Maximizar Z = 3x + 2y
    sujeto a:
    2x + y <= 100
    x + 2y <= 80
    x, y >= 0
    """

    problema_complejo = """
    Una empresa fabrica sillas y mesas.
    Maximizar ganancia = 50*silla + 40*mesa
    
    Restricciones:
    3*silla + 5*mesa <= 150 (horas de trabajo)
    2*silla + 4*mesa <= 100 (material)
    silla >= 0
    mesa >= 0
    """

    # Permitir selección de problema
    print("Selecciona el problema a probar:")
    print("1. Problema simple (formato matemático)")
    print("2. Problema complejo (lenguaje natural)")
    print("3. Ambos")

    choice = input("\nOpción (1/2/3, default=1): ").strip() or "1"

    problemas = []
    if choice == "1":
        problemas = [("Simple", problema_simple)]
    elif choice == "2":
        problemas = [("Complejo", problema_complejo)]
    else:
        problemas = [("Simple", problema_simple), ("Complejo", problema_complejo)]

    for nombre, problema in problemas:
        print(f"\n{Colors.BOLD}{'#' * 60}")
        print(f"  PROBLEMA: {nombre}")
        print(f"{'#' * 60}{Colors.ENDC}\n")
        print(f"{Colors.OKCYAN}{problema.strip()}{Colors.ENDC}")

        times = {}

        # Test individual de cada sistema
        result_regex, time_regex = test_regex(problema)
        if time_regex > 0:
            times["Regex"] = time_regex

        result_spacy, time_spacy = test_spacy(problema)
        if time_spacy > 0:
            times["spaCy"] = time_spacy

        # LLM opcional
        test_llm_choice = (
            input("\n¿Probar LLM? (s/N, tarda 5+ minutos): ").strip().lower()
        )
        if test_llm_choice == "s":
            result_llm, time_llm = test_llm(problema, skip=False)
            if time_llm > 0:
                times["LLM"] = time_llm

        # Test híbrido
        result_hybrid, time_hybrid, system_used = test_hybrid(problema)
        if time_hybrid > 0:
            times["Híbrido"] = time_hybrid

        # Comparación
        print_comparison(times)

        # Recomendación
        print_header("RECOMENDACIÓN")
        if result_regex and result_regex.get("confidence", 0) > 0.85:
            print_success("Usar Regex - Mayor velocidad con buena precisión")
        elif result_spacy and result_spacy.get("confidence", 0) > 0.75:
            print_success("Usar spaCy - Balance óptimo velocidad/precisión")
        else:
            print_info("Usar LLM - Necesario para máxima precisión")

    print(f"\n{Colors.BOLD}{'=' * 60}")
    print("  TESTS COMPLETADOS")
    print(f"{'=' * 60}{Colors.ENDC}\n")

    print_info("Para más detalles, ver: COMPARACION_SISTEMAS.md")


if __name__ == "__main__":
    main()
