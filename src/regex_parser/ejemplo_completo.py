"""
Ejemplo completo de uso del sistema regex con el solver SimplexSolver.

Demuestra cómo usar RegexOptimizationProcessor integrado con
el sistema completo de optimización para resolver problemas
sin necesidad de LLMs.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import json
import logging
from regex_parser import RegexOptimizationProcessor
from nlp.connector import NLPOptimizationConnector
from nlp.model_generator import SimplexModelGenerator, ModelValidator
from nlp.connector import SimplexSolverAdapter

# Configurar logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


def ejemplo_basico():
    """Ejemplo 1: Problema simple con regex."""
    print("\n" + "=" * 70)
    print("EJEMPLO 1: Problema Básico (2 variables)")
    print("=" * 70)

    problema = """
    Maximizar Z = 3x + 2y
    Sujeto a:
    2x + y <= 100
    x + 2y <= 80
    x >= 0
    y >= 0
    """

    print(f"\nProblema:\n{problema}")

    # Crear el sistema completo con regex
    processor = RegexOptimizationProcessor()
    generator = SimplexModelGenerator()
    solver = SimplexSolverAdapter()
    validator = ModelValidator()

    connector = NLPOptimizationConnector(
        nlp_processor=processor,
        model_generator=generator,
        solver=solver,
        validator=validator,
    )

    # Resolver
    resultado = connector.process_and_solve(problema)

    print("\n" + "-" * 70)
    print("RESULTADO:")
    print("-" * 70)
    print(json.dumps(resultado, indent=2, ensure_ascii=False))


def ejemplo_produccion():
    """Ejemplo 2: Problema de producción con variables descriptivas."""
    print("\n" + "=" * 70)
    print("EJEMPLO 2: Problema de Producción")
    print("=" * 70)

    problema = """
    Maximizar beneficio = 50*silla + 40*mesa
    
    Restricciones:
    3*silla + 5*mesa <= 150
    2*silla + 4*mesa <= 100
    silla >= 0
    mesa >= 0
    """

    print(f"\nProblema:\n{problema}")

    # Crear y resolver
    processor = RegexOptimizationProcessor()
    generator = SimplexModelGenerator()
    solver = SimplexSolverAdapter()
    validator = ModelValidator()

    connector = NLPOptimizationConnector(
        nlp_processor=processor,
        model_generator=generator,
        solver=solver,
        validator=validator,
    )

    resultado = connector.process_and_solve(problema)

    print("\n" + "-" * 70)
    print("RESULTADO:")
    print("-" * 70)
    if resultado["success"]:
        print(f"✅ Éxito!")
        print(f"Valor objetivo: {resultado['solution'].get('objective_value')}")
        print(f"Solución: {resultado['solution'].get('solution')}")
        if "named_solution" in resultado["solution"]:
            print(f"Solución con nombres: {resultado['solution']['named_solution']}")
    else:
        print(f"❌ Error: {resultado['error']}")


def ejemplo_subscripts():
    """Ejemplo 3: Variables con subíndices."""
    print("\n" + "=" * 70)
    print("EJEMPLO 3: Variables con Subíndices")
    print("=" * 70)

    problema = """
    Minimizar costo = 5*x1 + 3*x2 + 4*x3
    
    Sujeto a:
    x1 + 2*x2 + x3 >= 20
    2*x1 + x2 + 3*x3 >= 30
    x1 >= 0
    x2 >= 0
    x3 >= 0
    """

    print(f"\nProblema:\n{problema}")

    processor = RegexOptimizationProcessor()
    generator = SimplexModelGenerator()
    solver = SimplexSolverAdapter()
    validator = ModelValidator()

    connector = NLPOptimizationConnector(
        nlp_processor=processor,
        model_generator=generator,
        solver=solver,
        validator=validator,
    )

    resultado = connector.process_and_solve(problema)

    print("\n" + "-" * 70)
    print("RESULTADO:")
    print("-" * 70)
    print(json.dumps(resultado, indent=2, ensure_ascii=False))


def comparacion_velocidad():
    """Ejemplo 4: Comparación de velocidad regex vs modelo."""
    print("\n" + "=" * 70)
    print("EJEMPLO 4: Comparación de Velocidad")
    print("=" * 70)

    import time

    problema = """
    Maximizar Z = 4*x + 3*y
    Sujeto a:
    x + y <= 10
    2*x + y <= 15
    x >= 0
    y >= 0
    """

    # Con regex
    print("\n🔵 Procesando con REGEX...")
    start = time.time()

    processor = RegexOptimizationProcessor()
    generator = SimplexModelGenerator()
    solver = SimplexSolverAdapter()
    validator = ModelValidator()

    connector = NLPOptimizationConnector(
        nlp_processor=processor,
        model_generator=generator,
        solver=solver,
        validator=validator,
    )

    resultado = connector.process_and_solve(problema)
    tiempo_regex = time.time() - start

    print(f"⏱️  Tiempo con regex: {tiempo_regex:.4f} segundos")
    print(f"✅ Éxito: {resultado['success']}")

    if resultado["success"]:
        print(f"Valor objetivo: {resultado['solution'].get('objective_value')}")


def solo_parsing_sin_solver():
    """Ejemplo 5: Solo parsing sin resolver."""
    print("\n" + "=" * 70)
    print("EJEMPLO 5: Solo Parsing (sin resolver)")
    print("=" * 70)

    problema = """
    Maximizar ganancia = 100*A + 80*B + 60*C
    
    Restricciones:
    2*A + 3*B + C <= 120
    4*A + 2*B + 5*C <= 200
    A + B + C <= 50
    """

    print(f"\nProblema:\n{problema}")

    # Solo parsear, no resolver
    processor = RegexOptimizationProcessor()
    result = processor.process_text(problema)

    print("\n" + "-" * 70)
    print("PROBLEMA EXTRAÍDO:")
    print("-" * 70)

    if result.success:
        prob = result.problem
        print(f"Tipo: {prob.objective_type}")
        print(f"Variables: {prob.variable_names}")
        print(f"Coeficientes objetivo: {prob.objective_coefficients}")
        print(f"Número de restricciones: {len(prob.constraints)}")
        print("\nRestricciones:")
        for i, const in enumerate(prob.constraints, 1):
            print(f"  {i}. {const['coefficients']} {const['operator']} {const['rhs']}")


def main():
    """Ejecuta todos los ejemplos."""
    print("\n" + "=" * 70)
    print("EJEMPLOS DE USO DEL SISTEMA REGEX + SOLVER")
    print("=" * 70)

    try:
        ejemplo_basico()
        ejemplo_produccion()
        ejemplo_subscripts()
        comparacion_velocidad()
        solo_parsing_sin_solver()

        print("\n" + "=" * 70)
        print("✅ TODOS LOS EJEMPLOS COMPLETADOS")
        print("=" * 70)
        print("\n💡 Ventajas del sistema regex:")
        print("   - ⚡ Instantáneo (< 1ms)")
        print("   - 💪 No requiere GPU ni modelos grandes")
        print("   - 🎯 Determinista y predecible")
        print("   - 🔄 Integración fácil con el sistema existente")

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
