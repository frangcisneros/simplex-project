#!/usr/bin/env python3
"""
Tests para el sistema de validación de entrada del simplex solver.
"""

import sys
import os

# Agregar el directorio padre al path para importar los módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from simplex_solver.input_validator import InputValidator


def run_validation_tests():
    """Ejecuta todos los tests de validación."""
    print("🧪 EJECUTANDO TESTS DE VALIDACIÓN")
    print("=" * 70)
    
    test_functions = [
        test_valid_problem,
        test_empty_objective,
        test_invalid_coefficients,
        test_inconsistent_constraints,
        test_all_zero_coefficients,
        test_contradictory_constraints,
        test_infeasible_problem,
        test_mismatched_variables,
        test_infinite_values,
        test_nan_values,
        test_negative_equality,
        test_solution_validation
    ]
    
    passed = 0
    failed = 0
    
    for test_func in test_functions:
        try:
            test_func()
            print(f"✅ {test_func.__name__}: PASÓ")
            passed += 1
        except AssertionError as e:
            print(f"❌ {test_func.__name__}: FALLÓ - {e}")
            failed += 1
        except Exception as e:
            print(f"⚠️ {test_func.__name__}: ERROR - {e}")
            failed += 1
    
    print("\n" + "=" * 70)
    print(f"RESUMEN: {passed} pasados, {failed} fallados")
    
    if failed == 0:
        print("🎉 ¡Todas las validaciones funcionan correctamente!")
    else:
        print("💡 Algunas validaciones necesitan atención.")
    
    return failed == 0


def test_valid_problem():
    """Test 1: Problema válido debería pasar todas las validaciones."""
    print("\n--- Test 1: Problema válido ---")
    c = [3, 2, 4]
    A = [
        [2, 1, 1],
        [1, 3, 2],
        [1, 1, 0]
    ]
    b = [8, 12, 4]
    constraint_types = ['>=', '>=', '>=']
    maximize = False
    
    is_valid, message = InputValidator.validate_problem(c, A, b, constraint_types, maximize)
    assert is_valid == True, f"Problema válido fue rechazado: {message}"
    print(f"   Mensaje: {message}")


def test_empty_objective():
    """Test 2: Función objetivo vacía debería ser rechazada."""
    print("\n--- Test 2: Función objetivo vacía ---")
    c = []
    A = [[1, 2]]
    b = [5]
    constraint_types = ['<=']
    maximize = True
    
    is_valid, message = InputValidator.validate_problem(c, A, b, constraint_types, maximize)
    assert is_valid == False, "Función objetivo vacía fue aceptada"
    assert "objetivo" in message.lower()
    print(f"   Mensaje esperado: {message}")


def test_invalid_coefficients():
    """Test 3: Coeficientes no numéricos deberían ser rechazados."""
    print("\n--- Test 3: Coeficientes inválidos ---")
    
    # Test con string en coeficientes
    c = [3, "invalid", 2]  # Esto causará TypeError, pero probemos con NaN
    A = [[1, 2, 3]]
    b = [5]
    constraint_types = ['<=']
    maximize = True
    
    # En lugar de string, probemos con NaN (que es float pero inválido)
    import math
    c = [3, float('nan'), 2]
    
    is_valid, message = InputValidator.validate_problem(c, A, b, constraint_types, maximize)
    assert is_valid == False, "Coeficiente NaN fue aceptado"
    assert "número finito" in message.lower()
    print(f"   Mensaje: {message}")


def test_inconsistent_constraints():
    """Test 4: Número inconsistente de restricciones debería ser rechazado."""
    print("\n--- Test 4: Restricciones inconsistentes ---")
    c = [3, 2]
    A = [[1, 2], [2, 1]]  # 2 restricciones
    b = [5]               # 1 término independiente
    constraint_types = ['<=', '<=']  # 2 tipos
    maximize = True
    
    is_valid, message = InputValidator.validate_problem(c, A, b, constraint_types, maximize)
    assert is_valid == False, "Inconsistencia en restricciones fue aceptada"
    assert "inconsistente" in message.lower()
    print(f"   Mensaje: {message}")


def test_all_zero_coefficients():
    """Test 5: Todos los coeficientes cero deberían ser rechazados."""
    print("\n--- Test 5: Coeficientes todos cero ---")
    c = [0, 0, 0]  # Todos cero
    A = [[1, 2, 3]]
    b = [5]
    constraint_types = ['<=']
    maximize = True
    
    is_valid, message = InputValidator.validate_problem(c, A, b, constraint_types, maximize)
    assert is_valid == False, "Coeficientes todos cero fueron aceptados"
    assert "cero" in message.lower()
    print(f"   Mensaje: {message}")


def test_contradictory_constraints():
    """Test 6: Restricciones contradictorias deberían ser detectadas."""
    print("\n--- Test 6: Restricciones contradictorias ---")
    c = [3, 2]
    A = [
        [1, 1],
        [1, 1]
    ]
    b = [5, 10]
    constraint_types = ['<=', '>=']  # Contradictorias: x1+x2 <=5 y x1+x2 >=10
    maximize = True
    
    is_valid, message = InputValidator.validate_problem(c, A, b, constraint_types, maximize)
    assert is_valid == False, "Restricciones contradictorias fueron aceptadas"
    assert "contradictorias" in message.lower()
    print(f"   Mensaje: {message}")


def test_infeasible_problem():
    """Test 7: Problema obviamente infactible debería ser detectado."""
    print("\n--- Test 7: Problema infactible ---")
    c = [1, 1]
    A = [
        [-1, -1],
        [-2, -1]
    ]
    b = [5, 8]
    constraint_types = ['>=', '>=']  # -x1-x2 >=5 y -2x1-x2 >=8 con x1,x2>=0 es imposible
    maximize = False
    
    is_valid, message = InputValidator.validate_problem(c, A, b, constraint_types, maximize)
    assert is_valid == False, "Problema infactible fue aceptado"
    assert "infactible" in message.lower()
    print(f"   Mensaje: {message}")


def test_mismatched_variables():
    """Test 8: Número de variables inconsistente debería ser rechazado."""
    print("\n--- Test 8: Variables inconsistentes ---")
    c = [3, 2]    # 2 variables
    A = [[1]]     # 1 coeficiente (deberían ser 2)
    b = [5]
    constraint_types = ['<=']
    maximize = True
    
    is_valid, message = InputValidator.validate_problem(c, A, b, constraint_types, maximize)
    assert is_valid == False, "Número de variables inconsistente fue aceptado"
    assert "coincide" in message.lower()
    print(f"   Mensaje: {message}")


def test_infinite_values():
    """Test 9: Valores infinitos deberían ser rechazados."""
    print("\n--- Test 9: Valores infinitos ---")
    import math
    c = [3, float('inf')]
    A = [[1, 2]]
    b = [5]
    constraint_types = ['<=']
    maximize = True
    
    is_valid, message = InputValidator.validate_problem(c, A, b, constraint_types, maximize)
    assert is_valid == False, "Valor infinito fue aceptado"
    assert "finito" in message.lower()
    print(f"   Mensaje: {message}")


def test_nan_values():
    """Test 10: Valores NaN deberían ser rechazados."""
    print("\n--- Test 10: Valores NaN ---")
    import math
    c = [3, float('nan')]
    A = [[1, 2]]
    b = [5]
    constraint_types = ['<=']
    maximize = True
    
    is_valid, message = InputValidator.validate_problem(c, A, b, constraint_types, maximize)
    assert is_valid == False, "Valor NaN fue aceptado"
    assert "finito" in message.lower()
    print(f"   Mensaje: {message}")


def test_negative_equality():
    """Test 11: Restricciones de igualdad con RHS negativo deberían ser rechazadas."""
    print("\n--- Test 11: Igualdad con RHS negativo ---")
    c = [3, 2]
    A = [[1, 1]]
    b = [-5]  # RHS negativo en igualdad
    constraint_types = ['=']
    maximize = True
    
    is_valid, message = InputValidator.validate_problem(c, A, b, constraint_types, maximize)
    assert is_valid == False, "Igualdad con RHS negativo fue aceptada"
    assert "negativo" in message.lower()
    print(f"   Mensaje: {message}")


def test_solution_validation():
    """Test 12: Validación de solución factible e infactible."""
    print("\n--- Test 12: Validación de solución ---")
    
    # Datos del problema
    A = [[2, 1], [1, 2]]
    b = [8, 8]
    constraint_types = ['<=', '<=']
    
    # Solución factible
    solution_feasible = {'x1': 2.0, 'x2': 3.0}
    is_feasible, errors = InputValidator.validate_solution_feasibility(
        solution_feasible, A, b, constraint_types
    )
    assert is_feasible == True, f"Solución factible fue rechazada: {errors}"
    print(f"   ✅ Solución factible validada correctamente")
    
    # Solución infactible (viola restricciones)
    solution_infeasible = {'x1': 10.0, 'x2': 10.0}
    is_feasible, errors = InputValidator.validate_solution_feasibility(
        solution_infeasible, A, b, constraint_types
    )
    assert is_feasible == False, "Solución infactible fue aceptada"
    assert len(errors) > 0, "No se detectaron errores en solución infactible"
    print(f"   ✅ Solución infactible detectada correctamente")
    print(f"   Errores detectados: {errors}")


def test_interactive_examples():
    """Ejemplos para probar manualmente en modo interactivo."""
    print("\n" + "=" * 70)
    print("📝 EJEMPLOS PARA PROBAR EN MODO INTERACTIVO")
    print("=" * 70)
    
    examples = [
        {
            "name": "✅ Ejemplo válido (debería funcionar)",
            "c": [5, 3, 4],
            "A": [[2, 1, 1], [1, 3, 2], [1, 1, 0]],
            "b": [8, 12, 4],
            "types": ['>=', '>=', '>='],
            "maximize": False
        },
        {
            "name": "❌ Coeficiente infinito",
            "c": [1, float('inf')],
            "A": [[1, 1]],
            "b": [5],
            "types": ['<='],
            "maximize": True
        },
        {
            "name": "❌ Restricciones contradictorias", 
            "c": [3, 2],
            "A": [[1, 1], [1, 1]],
            "b": [5, 10],
            "types": ['<=', '>='],
            "maximize": True
        },
        {
            "name": "❌ Variables inconsistentes",
            "c": [1, 2, 3],
            "A": [[1, 2]],  # Solo 2 coeficientes, deberían ser 3
            "b": [5],
            "types": ['<='],
            "maximize": True
        },
        {
            "name": "❌ Todos coeficientes cero",
            "c": [0, 0, 0],
            "A": [[1, 2, 3]],
            "b": [5],
            "types": ['<='],
            "maximize": True
        }
    ]
    
    for example in examples:
        print(f"\n{example['name']}:")
        print(f"   c = {example['c']}")
        print(f"   A = {example['A']}")
        print(f"   b = {example['b']}")
        print(f"   tipos = {example['types']}")
        
        is_valid, message = InputValidator.validate_problem(
            example['c'], example['A'], example['b'], 
            example['types'], example['maximize']
        )
        
        status = "✅ VÁLIDO" if is_valid else "❌ INVÁLIDO"
        print(f"   Resultado: {status}")
        print(f"   Mensaje: {message}")


if __name__ == "__main__":
    # Ejecutar tests automáticos
    success = run_validation_tests()
    
    # Mostrar ejemplos para probar manualmente
    test_interactive_examples()
