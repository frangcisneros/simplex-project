"""
Script de testing para el sistema de parsing con regex.

Prueba la extracción de variables, función objetivo y restricciones
en problemas de optimización sin usar modelos de lenguaje.
"""

import sys
from pathlib import Path

# Agregar paths necesarios
sys.path.insert(0, str(Path(__file__).parent.parent))

import logging
from regex_parser import (
    RegexOptimizationProcessor,
    VariableDetector,
    ObjectiveParser,
    ConstraintParser,
    PatternLibrary,
    RegexExtractor,
)

# Configurar logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


def test_simple_problem():
    """Prueba con un problema simple."""
    print("\n" + "=" * 60)
    print("TEST 1: Problema Simple")
    print("=" * 60)

    problem_text = """
    Maximizar Z = 3x + 2y
    Sujeto a:
    2x + y <= 100
    x + 2y <= 80
    x, y >= 0
    """

    processor = RegexOptimizationProcessor()
    result = processor.process_text(problem_text)

    print(f"\nÉxito: {result.success}")
    print(f"Confianza: {result.confidence_score}")

    if result.success and result.problem:
        print(f"\nTipo: {result.problem.objective_type}")
        print(f"Variables: {result.problem.variable_names}")
        print(f"Coeficientes objetivo: {result.problem.objective_coefficients}")
        print(f"Número de restricciones: {len(result.problem.constraints)}")

        for i, constraint in enumerate(result.problem.constraints, 1):
            print(f"\nRestricción {i}:")
            print(f"  Coeficientes: {constraint['coefficients']}")
            print(f"  Operador: {constraint['operator']}")
            print(f"  RHS: {constraint['rhs']}")


def test_production_problem():
    """Prueba con problema de producción."""
    print("\n" + "=" * 60)
    print("TEST 2: Problema de Producción")
    print("=" * 60)

    problem_text = """
    Una empresa fabrica dos productos A y B.
    Maximizar beneficio = 100*producto_A + 80*producto_B
    
    Restricciones:
    2*producto_A + 3*producto_B <= 120  (horas de producción)
    4*producto_A + 2*producto_B <= 160  (material)
    producto_A >= 10  (demanda mínima)
    producto_B >= 15
    """

    processor = RegexOptimizationProcessor()
    result = processor.process_text(problem_text)

    print(f"\nÉxito: {result.success}")
    print(f"Confianza: {result.confidence_score}")

    if result.success and result.problem:
        print(f"\nVariables: {result.problem.variable_names}")
        print(f"Coeficientes: {result.problem.objective_coefficients}")
        print(f"Restricciones: {len(result.problem.constraints)}")


def test_subscript_variables():
    """Prueba con variables con subíndices."""
    print("\n" + "=" * 60)
    print("TEST 3: Variables con Subíndices")
    print("=" * 60)

    problem_text = """
    Minimizar costo = 5x1 + 3x2 + 4x3
    
    Sujeto a:
    x1 + 2x2 + x3 >= 20
    2x1 + x2 + 3x3 >= 30
    x1, x2, x3 >= 0
    """

    processor = RegexOptimizationProcessor()
    result = processor.process_text(problem_text)

    print(f"\nÉxito: {result.success}")

    if result.success and result.problem:
        print(f"Variables detectadas: {result.problem.variable_names}")
        print(f"Tipo de objetivo: {result.problem.objective_type}")


def test_component_by_component():
    """Prueba cada componente por separado."""
    print("\n" + "=" * 60)
    print("TEST 4: Componentes Individuales")
    print("=" * 60)

    problem_text = """
    Maximizar Z = 4x1 + 3x2 - 2x3 + 5
    Sujeto a:
    2x1 + x2 <= 10
    x2 + 3x3 >= 5
    x1 = 2
    """

    # Test 1: Detector de variables
    print("\n--- Variable Detector ---")
    detector = VariableDetector()
    variables = detector.detect_variables(problem_text)
    print(f"Variables encontradas: {[v.name for v in variables]}")

    # Test 2: Parser de objetivo
    print("\n--- Objective Parser ---")
    obj_parser = ObjectiveParser()
    objective = obj_parser.parse_objective(problem_text)
    if objective:
        print(f"Tipo: {objective.objective_type}")
        print(f"Coeficientes: {objective.coefficients}")
        print(f"Término constante: {objective.constant_term}")

    # Test 3: Parser de restricciones
    print("\n--- Constraint Parser ---")
    const_parser = ConstraintParser()
    constraints = const_parser.parse_constraints(problem_text)
    print(f"Restricciones encontradas: {len(constraints)}")
    for i, c in enumerate(constraints, 1):
        print(f"  {i}. {const_parser.format_constraint_for_display(c)}")


def test_extractor_formatting():
    """Prueba el formato de salida del extractor."""
    print("\n" + "=" * 60)
    print("TEST 5: Formato de Salida")
    print("=" * 60)

    problem_text = """
    Maximizar 3x + 4y
    Sujeto a:
    x + y <= 10
    2x + y <= 15
    """

    extractor = RegexExtractor()
    formatted = extractor.extract_and_format(problem_text)

    print("\nResultado formateado:")
    import json

    print(json.dumps(formatted, indent=2, ensure_ascii=False))


def test_pattern_library():
    """Prueba la biblioteca de patrones."""
    print("\n" + "=" * 60)
    print("TEST 6: Pattern Library")
    print("=" * 60)

    library = PatternLibrary()

    # Test detección de tipo
    text1 = "Una fábrica produce 100 unidades por día"
    text2 = "Transportar mercancía de A a B minimizando costo"

    print(f"\nTipo problema 1: {library.detect_problem_type(text1)}")
    print(f"Tipo problema 2: {library.detect_problem_type(text2)}")

    # Test limpieza de texto
    dirty_text = "  3x   +   2y  ≤  100  "
    clean = library.clean_text(dirty_text)
    print(f"\nTexto sucio: '{dirty_text}'")
    print(f"Texto limpio: '{clean}'")


def main():
    """Ejecuta todos los tests."""
    print("\n" + "=" * 60)
    print("TESTS DEL SISTEMA DE REGEX PARSER")
    print("=" * 60)

    try:
        test_simple_problem()
        test_production_problem()
        test_subscript_variables()
        test_component_by_component()
        test_extractor_formatting()
        test_pattern_library()

        print("\n" + "=" * 60)
        print("TODOS LOS TESTS COMPLETADOS")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
