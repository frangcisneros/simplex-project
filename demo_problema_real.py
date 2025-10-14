"""
demo_problema_real.py - Demo con tu problema real de multi-planta

Este script demuestra cómo usar el sistema spaCy NER con uno de
tus problemas complejos reales del proyecto.
"""

import sys
from pathlib import Path

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from spacy_nlp import SpacyNLPProcessor
import time


def print_header(text):
    print("\n" + "=" * 70)
    print(text)
    print("=" * 70 + "\n")


def main():
    print_header("🏭 DEMO: Problema Real Multi-Planta")

    # Versión simplificada de tu problema real
    # (El texto original es muy largo y narrativo, aquí usamos versión estructurada)
    problema_estructurado = """
Una compañía tiene tres plantas que fabrican productos en tres tamaños: 
grande, mediano y chico.

Las ganancias son 420, 360 y 300 dólares respectivamente.

Las plantas 1, 2 y 3 tienen capacidad para producir 750, 900 y 450 unidades 
diarias respectivamente.

Cada unidad grande, mediana y chica requiere 20, 15 y 12 pies cuadrados 
respectivamente.

Se dispone de 13000, 12000 y 5000 pies cuadrados en las plantas 1, 2 y 3.

Se pueden vender 900, 1200 y 750 unidades diarias de los tamaños grande, 
mediano y chico.

Maximizar la ganancia total.
"""

    print("📄 PROBLEMA:")
    print(problema_estructurado)

    # Inicializar procesador spaCy con modelo entrenado
    print_header("🤖 Procesando con spaCy NER...")

    model_path = (
        Path(__file__).parent / "src" / "spacy_nlp" / "models" / "optimization_ner"
    )

    if not model_path.exists():
        print("❌ Modelo no encontrado. Entrena primero con:")
        print("   cd src/spacy_nlp && python train_model.py")
        return

    processor = SpacyNLPProcessor(model_path=str(model_path))

    # Procesar
    start = time.time()
    result = processor.process_text(problema_estructurado)
    elapsed = time.time() - start

    print(f"⏱️  Tiempo de procesamiento: {elapsed:.2f} segundos")
    print(f"✓ Éxito: {result.success}")
    print(f"✓ Confianza: {result.confidence_score:.2%}")

    # Mostrar resultados
    if result.success and result.problem:
        print_header("📊 PROBLEMA EXTRAÍDO")

        prob = result.problem

        print(f"🎯 Tipo de optimización: {prob.objective_type.upper()}")
        print(f"📝 Variables detectadas: {len(prob.variable_names)}")
        print(f"   {prob.variable_names}")

        print(f"\n💰 Función objetivo:")
        for i, (var, coef) in enumerate(
            zip(prob.variable_names, prob.objective_coefficients)
        ):
            sign = "+" if i > 0 and coef >= 0 else ""
            print(f"   {sign}{coef} * {var}")

        print(f"\n⚖️ Restricciones: {len(prob.constraints)}")
        for i, constraint in enumerate(prob.constraints, 1):
            print(f"\n   Restricción {i}:")
            print(f"      Operador: {constraint['operator']}")
            print(f"      RHS: {constraint['rhs']}")
            print(f"      Coeficientes: {constraint['coefficients']}")

        print_header("🔍 ANÁLISIS DEL PROBLEMA")

        # Análisis automático
        num_plantas = 3
        num_tamanos = 3
        expected_vars = num_plantas * num_tamanos  # 9 variables (3 plantas x 3 tamaños)

        print(f"📌 Problema tipo: Multi-planta, multi-producto")
        print(f"📌 Plantas: {num_plantas}")
        print(f"📌 Tamaños de producto: {num_tamanos}")
        print(f"📌 Variables esperadas: {expected_vars} (planta x tamaño)")
        print(f"📌 Variables detectadas: {len(prob.variable_names)}")

        # Información de ganancias
        ganancias = [420, 360, 300]
        print(f"\n💵 Ganancias por tamaño:")
        print(f"   Grande: ${ganancias[0]}")
        print(f"   Mediano: ${ganancias[1]}")
        print(f"   Chico: ${ganancias[2]}")

        # Capacidades de planta
        capacidades = [750, 900, 450]
        print(f"\n🏭 Capacidades de producción (unidades/día):")
        for i, cap in enumerate(capacidades, 1):
            print(f"   Planta {i}: {cap} unidades")

        # Espacio disponible
        espacios = [13000, 12000, 5000]
        print(f"\n📦 Espacio disponible (pies cuadrados):")
        for i, esp in enumerate(espacios, 1):
            print(f"   Planta {i}: {esp:,} pies²")

        # Requerimientos de espacio
        espacio_req = [20, 15, 12]
        print(f"\n📏 Requerimientos de espacio por unidad:")
        print(f"   Grande: {espacio_req[0]} pies²")
        print(f"   Mediano: {espacio_req[1]} pies²")
        print(f"   Chico: {espacio_req[2]} pies²")

        # Demanda
        demanda = [900, 1200, 750]
        print(f"\n📈 Demanda máxima (unidades/día):")
        print(f"   Grande: {demanda[0]} unidades")
        print(f"   Mediano: {demanda[1]} unidades")
        print(f"   Chico: {demanda[2]} unidades")

        print_header("🎯 OBJETIVO")
        print("Maximizar la ganancia total produciendo la combinación óptima")
        print("de productos en cada planta, respetando:")
        print("  • Capacidad de producción de cada planta")
        print("  • Espacio disponible en cada planta")
        print("  • Demanda máxima del mercado")

        print_header("✅ PRÓXIMOS PASOS")
        print("1. Resolver con SimplexSolver")
        print("2. Interpretar solución óptima")
        print("3. Generar plan de producción")

        print("\n💡 Comando para resolver:")
        print("   python src/test_solver.py")

    else:
        print("❌ Error procesando problema:")
        print(f"   {result.error_message}")

    print("\n" + "=" * 70 + "\n")


if __name__ == "__main__":
    main()
