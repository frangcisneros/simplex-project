"""
Script de testing para el sistema spaCy NLP.

Prueba el procesador con ejemplos simples y complejos,
incluyendo los problemas reales del proyecto.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import logging
import json
from spacy_nlp import SpacyNLPProcessor
from nlp.connector import NLPOptimizationConnector
from nlp.model_generator import SimplexModelGenerator, ModelValidator
from nlp.connector import SimplexSolverAdapter

# Configurar logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


def test_simple_problem():
    """Test 1: Problema simple."""
    print("\n" + "=" * 70)
    print("TEST 1: Problema Simple")
    print("=" * 70)

    problema = """
    Maximizar Z = 3x + 2y
    Sujeto a:
    2x + y <= 100
    x + 2y <= 80
    x, y >= 0
    """

    print(f"\nProblema:\n{problema}")

    processor = SpacyNLPProcessor()

    # Análisis detallado
    print("\n📊 ANÁLISIS DETALLADO:")
    processor.display_analysis(problema)

    # Procesar
    result = processor.process_text(problema)

    print(f"\n{'='*70}")
    print("RESULTADO:")
    print("=" * 70)
    print(f"Éxito: {result.success}")
    print(f"Confianza: {result.confidence_score}")

    if result.success and result.problem:
        print(f"\nTipo: {result.problem.objective_type}")
        print(f"Variables: {result.problem.variable_names}")
        print(f"Coeficientes: {result.problem.objective_coefficients}")
        print(f"Restricciones: {len(result.problem.constraints)}")


def test_production_problem():
    """Test 2: Problema de producción."""
    print("\n" + "=" * 70)
    print("TEST 2: Problema de Producción")
    print("=" * 70)

    problema = """
    Una empresa fabrica sillas y mesas.
    Maximizar ganancia = 50*silla + 40*mesa
    
    Restricciones:
    3*silla + 5*mesa <= 150 (horas de trabajo)
    2*silla + 4*mesa <= 100 (material)
    silla >= 0
    mesa >= 0
    """

    print(f"\nProblema:\n{problema}")

    processor = SpacyNLPProcessor()
    result = processor.process_text(problema)

    print(f"\n{'='*70}")
    print("RESULTADO:")
    print("=" * 70)
    print(f"Éxito: {result.success}")
    print(f"Confianza: {result.confidence_score:.2f}")

    if result.success:
        print(f"Variables: {result.problem.variable_names}")


def test_complex_multiplant():
    """Test 3: Problema complejo multi-planta."""
    print("\n" + "=" * 70)
    print("TEST 3: Problema Complejo Multi-Planta")
    print("=" * 70)

    # Versión simplificada del problema complejo 1
    problema = """
    Una compañía tiene tres plantas que fabrican productos en tres tamaños: grande, mediano y chico.
    Las ganancias son 420, 360 y 300 dólares respectivamente.
    
    Las plantas 1, 2 y 3 tienen capacidad para producir 750, 900 y 450 unidades diarias respectivamente.
    
    Cada unidad grande, mediana y chica requiere 20, 15 y 12 pies cuadrados respectivamente.
    Se dispone de 13000, 12000 y 5000 pies cuadrados en las plantas 1, 2 y 3.
    
    Se pueden vender 900, 1200 y 750 unidades diarias de los tamaños grande, mediano y chico.
    
    Maximizar la ganancia total.
    """

    print(f"\nProblema:\n{problema}")

    processor = SpacyNLPProcessor()

    # Análisis completo
    analysis = processor.analyze_text(problema)

    print(f"\n{'='*70}")
    print("ANÁLISIS:")
    print("=" * 70)
    print(f"Entidades: {analysis['n_entities']}")
    print(f"Patrones: {analysis['n_patterns']}")
    print(f"Restricciones: {analysis['n_constraints']}")
    print(f"Términos: {len(analysis['terms'])}")

    # Mostrar algunas entidades
    print("\n📌 Primeras entidades:")
    for text, label in analysis["entities"][:10]:
        print(f"  {text:20s} -> {label}")


def test_refinery_problem():
    """Test 4: Problema de refinería."""
    print("\n" + "=" * 70)
    print("TEST 4: Problema de Refinería (Complejo)")
    print("=" * 70)

    # Versión simplificada del problema complejo 2
    problema = """
    Una refinería produce 4 tipos de gasolina: gas1, gas2, gas3 y gas4.
    
    El gas1 tiene NP de 107 y PV de 5.
    El gas2 tiene NP de 93 y PV de 8.
    
    Se producen 3814 barriles de gas1 y 2666 barriles de gas2 diarios.
    
    El precio de venta es 24.83 dólares por barril.
    El costo de producción es 3.5 dólares por barril de gas1 y 2.3 dólares de gas2.
    
    Estas gasolinas pueden mezclarse para obtener avgas A y avgas B.
    La avgas A requiere al menos NP de 100 y no más de 7 de PV.
    
    Maximizar los retornos.
    """

    print(f"\nProblema:\n{problema}")

    processor = SpacyNLPProcessor()

    # Análisis
    processor.display_analysis(problema)


def test_with_solver():
    """Test 5: Integración completa con solver."""
    print("\n" + "=" * 70)
    print("TEST 5: Integración con Solver")
    print("=" * 70)

    problema = """
    Maximizar Z = 4x + 3y
    Sujeto a:
    x + y <= 10
    2x + y <= 15
    x >= 0
    y >= 0
    """

    print(f"\nProblema:\n{problema}")

    # Crear sistema completo
    processor = SpacyNLPProcessor()
    connector = NLPOptimizationConnector(
        nlp_processor=processor,
        model_generator=SimplexModelGenerator(),
        solver=SimplexSolverAdapter(),
        validator=ModelValidator(),
    )

    # Resolver
    resultado = connector.process_and_solve(problema)

    print(f"\n{'='*70}")
    print("RESULTADO COMPLETO:")
    print("=" * 70)
    print(json.dumps(resultado, indent=2, ensure_ascii=False))


def test_pattern_matcher_only():
    """Test 6: Solo pattern matcher (sin modelo entrenado)."""
    print("\n" + "=" * 70)
    print("TEST 6: Pattern Matcher Sin Modelo Entrenado")
    print("=" * 70)

    problema = """
    Minimizar costo = 5x1 + 3x2 + 4x3
    Tal que:
    x1 + 2x2 + x3 >= 20
    2x1 + x2 + 3x3 >= 30
    """

    print(f"\nProblema:\n{problema}")

    # Usar sin modelo entrenado (solo patterns)
    processor = SpacyNLPProcessor(model_path=None)

    analysis = processor.analyze_text(problema)

    print(f"\n{'='*70}")
    print("ANÁLISIS (solo patterns):")
    print("=" * 70)
    print(f"Patrones encontrados: {analysis['n_patterns']}")
    print(f"Restricciones: {analysis['n_constraints']}")
    print(f"Términos: {len(analysis['terms'])}")

    print("\nTérminos extraídos:")
    for coef, var in analysis["terms"]:
        print(f"  {coef}{var}")


def main():
    """Ejecuta todos los tests."""
    print("\n" + "=" * 70)
    print("TESTS DEL SISTEMA SPACY NLP")
    print("=" * 70)

    try:
        test_simple_problem()
        test_production_problem()
        test_complex_multiplant()
        test_refinery_problem()
        test_with_solver()
        test_pattern_matcher_only()

        print("\n" + "=" * 70)
        print("✅ TODOS LOS TESTS COMPLETADOS")
        print("=" * 70)

        print("\n💡 Notas:")
        print("   - Pattern Matcher funciona sin modelo entrenado")
        print("   - NER mejora precisión pero requiere entrenamiento")
        print("   - Para entrenar: python train_model.py")

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
