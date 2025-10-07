"""
Test automático de modelos NLP para resolver el problema complejo.

Este script prueba diferentes modelos en orden de eficiencia hasta encontrar
uno que resuelva correctamente el problema de las 3 plantas.
"""

import sys
import logging
from pathlib import Path
import time

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from nlp import (
    OllamaNLPProcessor,
    NLPModelType,
    ModelSelector,
)


# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


def test_model(model_type: NLPModelType, problem_text: str, timeout: int = 600) -> bool:
    """
    Prueba un modelo específico con el problema.

    Returns:
        True si el modelo resolvió el problema correctamente, False si no.
    """
    logger.info("=" * 70)
    logger.info(f"🧪 Probando modelo: {model_type.value}")
    logger.info("=" * 70)

    try:
        start_time = time.time()

        # Crear procesador Ollama con el modelo específico
        processor = OllamaNLPProcessor(
            model_type=model_type,
        )

        # Procesar el problema
        logger.info("📝 Procesando problema...")
        result = processor.process_text(problem_text)

        elapsed_time = time.time() - start_time

        # Verificar resultado
        if result.success:
            logger.info(f"✅ ÉXITO! Modelo {model_type.value} resolvió el problema")
            logger.info(f"⏱️  Tiempo: {elapsed_time:.1f} segundos")
            logger.info(f"📊 Confianza: {result.confidence_score:.2%}")

            if result.problem:
                logger.info(
                    f"📈 Variables: {len(result.problem.objective_coefficients)}"
                )
                logger.info(f"📋 Restricciones: {len(result.problem.constraints)}")
                logger.info(f"🎯 Objetivo: {result.problem.objective_type}")

            return True
        else:
            logger.warning(f"❌ Falló: {result.error_message}")
            logger.info(f"⏱️  Tiempo hasta fallo: {elapsed_time:.1f} segundos")
            return False

    except KeyboardInterrupt:
        logger.warning("⚠️  Test interrumpido por el usuario")
        raise
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        return False


def main():
    """Ejecuta test con Mistral 7B."""

    print("\n" + "=" * 70)
    print("🔬 TEST DE MISTRAL 7B")
    print("=" * 70)

    # Detectar memoria RAM disponible
    import psutil
    total_ram_gb = psutil.virtual_memory().total / (1024**3)
    logger.info(f"🖥️  RAM detectada: {total_ram_gb:.1f} GB")

    # Verificar que hay suficiente RAM para Mistral 7B
    if total_ram_gb < 6:
        logger.warning("⚠️  RAM baja detectada. Mistral 7B requiere al menos 6GB.")
        print("� Considera usar un modelo más ligero con Ollama")
        return

    # Usar únicamente Mistral 7B
    models_to_test = [NLPModelType.MISTRAL_7B]
    logger.info("🎯 Usando modelo predeterminado: Mistral 7B")

    # Cargar problema
    problem_file = Path("ejemplos/nlp/problema_complejo.txt")
    if not problem_file.exists():
        logger.error(f"❌ No se encontró el archivo: {problem_file}")
        return

    problem_text = problem_file.read_text(encoding="utf-8")
    logger.info(f"\n📄 Problema cargado: {len(problem_text)} caracteres\n")

    # Mostrar análisis automático primero
    logger.info("🔍 Análisis automático del problema:")
    selector = ModelSelector()
    recommended_model = selector.select_model(problem_text)
    logger.info(f"   Modelo recomendado: {recommended_model.value}\n")

    print("\n📋 Modelos a probar (en orden):")
    for i, model in enumerate(models_to_test, 1):
        print(f"   {i}. {model.value}")
    print()

    # Probar cada modelo
    for i, model_type in enumerate(models_to_test, 1):
        logger.info(f"\n{'='*70}")
        logger.info(f"Test {i}/{len(models_to_test)}")
        logger.info(f"{'='*70}\n")

        try:
            success = test_model(model_type, problem_text)

            if success:
                print("\n" + "=" * 70)
                print("🎉 ¡PROBLEMA RESUELTO!")
                print("=" * 70)
                print(f"\n✅ Modelo exitoso: {model_type.value}")
                print("\n💡 Puedes usar este modelo en el futuro especificando:")
                print(
                    f"   python nlp_simplex.py --nlp --model {model_type.name.lower()} --file problema.txt"
                )
                print()
                return

        except KeyboardInterrupt:
            logger.warning("\n⚠️  Tests interrumpidos por el usuario")
            return
        except Exception as e:
            logger.error(f"Error inesperado: {e}")
            continue

        # Pausa entre tests
        if i < len(models_to_test):
            logger.info("\n⏳ Esperando 5 segundos antes del siguiente test...\n")
            time.sleep(5)

    # Si llegamos aquí, ningún modelo funcionó
    print("\n" + "=" * 70)
    print("� ANÁLISIS DE RESULTADOS")
    print("=" * 70)
    print("\n� Resumen:")
    print(f"   • RAM detectada: {total_ram_gb:.1f} GB")
    print(f"   • Modelos probados: {len(models_to_test)}")
    print(f"   • Problema: {len(problem_text)} caracteres")
    
    print("\n❌ Problemas encontrados:")
    print("   • Los modelos FLAN-T5 no generan JSON estructurado correctamente")
    print("   • Los modelos más potentes (Phi-3, Gemma) requieren dependencias complejas")
    print("   • El problema es complejo (9 variables, múltiples restricciones)")
    
    print("\n✅ Pasos siguientes:")
    print("   1. ✓ Ollama está instalado o instalándose")
    print("   2. 📥 Descargar modelo recomendado:")
    if total_ram_gb < 8:
        print("      ollama pull llama3.2:3b")
    elif total_ram_gb < 16:
        print("      ollama pull mistral:7b")
    else:
        print("      ollama pull llama3.1:8b")
    print("   3. 🔄 Ejecutar este script nuevamente")
    print("   4. 🧪 Probar con: python nlp_simplex.py --nlp --file problema.txt")
    
    print("\n💡 Comandos útiles de Ollama:")
    print("   • ollama list          # Ver modelos descargados")
    print("   • ollama serve         # Iniciar servidor (automático)")  
    print("   • ollama pull <model>  # Descargar modelo")
    print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Test cancelado por el usuario")
    except Exception as e:
        logger.error(f"\n❌ Error fatal: {e}")
        sys.exit(1)
