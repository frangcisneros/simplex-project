"""
Tests para problemas de MINIMIZACIÓN del método simplex.
Contiene ejercicios con 2 y 3 variables con diferentes tipos de restricciones.
"""

import unittest
import sys
import os

# Agregar el directorio padre al path para importar los módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.solver import SimplexSolver
from src.user_interface import UserInterface


class TestMinimizationProblems(unittest.TestCase):
    """Tests para problemas de minimización."""
    
    def setUp(self):
        """Configura el solver antes de cada test."""
        self.solver = SimplexSolver()
        self.ui = UserInterface()
    
    def test_min_2vars_only_greater_equal(self):
        """Minimización con 2 variables y solo restricciones >=."""
        print("\n" + "="*70)
        print("TEST 1: Minimización 2 variables (solo >=)")
        print("="*70)
        
        # Problema: Minimizar z = 3x1 + 2x2
        # Sujeto a:
        # 2x1 + x2 ≥ 6
        # x1 + x2 ≥ 4
        # x1 ≥ 0, x2 ≥ 0
        c = [3, 2]
        A = [
            [2, 1],
            [1, 1]
        ]
        b = [6, 4]
        constraint_types = ['>=', '>=']
        maximize = False
        
        # 1. Mostrar el problema
        print("\n1. PROBLEMA INGRESADO:")
        self.ui.display_problem(c, A, b, constraint_types, maximize)
        
        # 2. Resolver el problema
        print("\n2. PROCESANDO SOLUCIÓN...")
        result = self.solver.solve(c, A, b, constraint_types, maximize)
        
        # 3. Mostrar resultados
        print("\n3. RESULTADO OBTENIDO:")
        self.ui.display_result(result)
        
        # 4. Verificaciones básicas      
        print("\n4. INFORMACIÓN DE LA SOLUCIÓN:")
        print(f"   - Estado: {result['status']}")
        print(f"   - Iteraciones: {result['iterations']}")
        if 'phase1_iterations' in result:
            print(f"   - Iteraciones Fase 1: {result['phase1_iterations']}")
        print(f"   - Valor óptimo: {result['optimal_value']:.4f}")
        
        # Mostrar solución dinámicamente
        print("   - Solución:")
        for var_name, value in result["solution"].items():
            print(f"     {var_name} = {value:.4f}")
        
        # Verificaciones de assert
        self.assertEqual(result["status"], "optimal")
        self.assertIn("x1", result["solution"])
        self.assertIn("x2", result["solution"])
    
    def test_min_2vars_with_less_equal(self):
        """Minimización con 2 variables y restricciones <=."""
        print("\n" + "="*70)
        print("TEST 2: Minimización 2 variables (con <=)")
        print("="*70)
        
        # Problema: Minimizar z = 2x1 + 5x2
        # Sujeto a:
        # x1 + 2x2 ≥ 4
        # 3x1 + x2 ≥ 3
        # x1 ≤ 5
        # x2 ≤ 4
        # x1, x2 ≥ 0
        c = [2, 5]
        A = [
            [1, 2],
            [3, 1],
            [1, 0],
            [0, 1]
        ]
        b = [4, 3, 5, 4]
        constraint_types = ['>=', '>=', '<=', '<=']
        maximize = False
        
        # 1. Mostrar el problema
        print("\n1. PROBLEMA INGRESADO:")
        self.ui.display_problem(c, A, b, constraint_types, maximize)
        
        # 2. Resolver el problema
        print("\n2. PROCESANDO SOLUCIÓN...")
        result = self.solver.solve(c, A, b, constraint_types, maximize)
        
        # 3. Mostrar resultados
        print("\n3. RESULTADO OBTENIDO:")
        self.ui.display_result(result)
        
        # 4. Verificaciones básicas      
        print("\n4. INFORMACIÓN DE LA SOLUCIÓN:")
        print(f"   - Estado: {result['status']}")
        print(f"   - Iteraciones: {result['iterations']}")
        if 'phase1_iterations' in result:
            print(f"   - Iteraciones Fase 1: {result['phase1_iterations']}")
        print(f"   - Valor óptimo: {result['optimal_value']:.4f}")
        
        # Mostrar solución dinámicamente
        print("   - Solución:")
        for var_name, value in result["solution"].items():
            print(f"     {var_name} = {value:.4f}")
        
        # Verificaciones de assert
        self.assertEqual(result["status"], "optimal")
        self.assertIn("x1", result["solution"])
        self.assertIn("x2", result["solution"])
    
    def test_min_2vars_with_equal(self):
        """Minimización con 2 variables y restricción =."""
        print("\n" + "="*70)
        print("TEST 3: Minimización 2 variables (con =)")
        print("="*70)
        
        # Problema: Minimizar z = 4x1 + 3x2
        # Sujeto a:
        # 2x1 + x2 = 10
        # x1 + x2 ≥ 6
        # x1 ≤ 8
        # x1, x2 ≥ 0
        c = [4, 3]
        A = [
            [2, 1],
            [1, 1],
            [1, 0]
        ]
        b = [10, 6, 8]
        constraint_types = ['=', '>=', '<=']
        maximize = False
        
        # 1. Mostrar el problema
        print("\n1. PROBLEMA INGRESADO:")
        self.ui.display_problem(c, A, b, constraint_types, maximize)
        
        # 2. Resolver el problema
        print("\n2. PROCESANDO SOLUCIÓN...")
        result = self.solver.solve(c, A, b, constraint_types, maximize)
        
        # 3. Mostrar resultados
        print("\n3. RESULTADO OBTENIDO:")
        self.ui.display_result(result)
        
        # 4. Verificaciones básicas      
        print("\n4. INFORMACIÓN DE LA SOLUCIÓN:")
        print(f"   - Estado: {result['status']}")
        print(f"   - Iteraciones: {result['iterations']}")
        if 'phase1_iterations' in result:
            print(f"   - Iteraciones Fase 1: {result['phase1_iterations']}")
        print(f"   - Valor óptimo: {result['optimal_value']:.4f}")
        
        # Mostrar solución dinámicamente
        print("   - Solución:")
        for var_name, value in result["solution"].items():
            print(f"     {var_name} = {value:.4f}")
        
        # Verificaciones de assert
        self.assertEqual(result["status"], "optimal")
        self.assertIn("x1", result["solution"])
        self.assertIn("x2", result["solution"])
    
    def test_min_3vars_mixed_constraints(self):
        """Minimización con 3 variables y mezcla de restricciones."""
        print("\n" + "="*70)
        print("TEST 4: Minimización 3 variables (restricciones mixtas)")
        print("="*70)
        
        # Problema: Minimizar z = x1 + 2x2 + 3x3
        # Sujeto a:
        # x1 + x2 + x3 ≥ 6
        # 2x1 + x2 + x3 ≤ 10
        # x1 + 2x2 + x3 = 8
        # x1, x2, x3 ≥ 0
        c = [1, 2, 3]
        A = [
            [1, 1, 1],
            [2, 1, 1],
            [1, 2, 1]
        ]
        b = [6, 10, 8]
        constraint_types = ['>=', '<=', '=']
        maximize = False
        
        # 1. Mostrar el problema
        print("\n1. PROBLEMA INGRESADO:")
        self.ui.display_problem(c, A, b, constraint_types, maximize)
        
        # 2. Resolver el problema
        print("\n2. PROCESANDO SOLUCIÓN...")
        result = self.solver.solve(c, A, b, constraint_types, maximize)
        
        # 3. Mostrar resultados
        print("\n3. RESULTADO OBTENIDO:")
        self.ui.display_result(result)
        
        # 4. Verificaciones básicas      
        print("\n4. INFORMACIÓN DE LA SOLUCIÓN:")
        print(f"   - Estado: {result['status']}")
        print(f"   - Iteraciones: {result['iterations']}")
        if 'phase1_iterations' in result:
            print(f"   - Iteraciones Fase 1: {result['phase1_iterations']}")
        print(f"   - Valor óptimo: {result['optimal_value']:.4f}")
        
        # Mostrar solución dinámicamente
        print("   - Solución:")
        for var_name, value in result["solution"].items():
            print(f"     {var_name} = {value:.4f}")
        
        # Verificaciones de assert
        self.assertEqual(result["status"], "optimal")
        self.assertIn("x1", result["solution"])
        self.assertIn("x2", result["solution"])
        self.assertIn("x3", result["solution"])
    
    def test_min_3vars_only_greater_equal(self):
        """Minimización con 3 variables y solo restricciones >=."""
        print("\n" + "="*70)
        print("TEST 5: Minimización 3 variables (solo >=)")
        print("="*70)
        
        # Problema: Minimizar z = 2x1 + x2 + 3x3
        # Sujeto a:
        # x1 + x2 + x3 ≥ 3
        # 2x1 + x2 + x3 ≥ 4
        # x1 + 2x2 + x3 ≥ 5
        # x1, x2, x3 ≥ 0
        c = [2, 1, 3]
        A = [
            [1, 1, 1],
            [2, 1, 1],
            [1, 2, 1]
        ]
        b = [3, 4, 5]
        constraint_types = ['>=', '>=', '>=']
        maximize = False
        
        # 1. Mostrar el problema
        print("\n1. PROBLEMA INGRESADO:")
        self.ui.display_problem(c, A, b, constraint_types, maximize)
        
        # 2. Resolver el problema
        print("\n2. PROCESANDO SOLUCIÓN...")
        result = self.solver.solve(c, A, b, constraint_types, maximize)
        
        # 3. Mostrar resultados
        print("\n3. RESULTADO OBTENIDO:")
        self.ui.display_result(result)
        
        # 4. Verificaciones básicas      
        print("\n4. INFORMACIÓN DE LA SOLUCIÓN:")
        print(f"   - Estado: {result['status']}")
        print(f"   - Iteraciones: {result['iterations']}")
        if 'phase1_iterations' in result:
            print(f"   - Iteraciones Fase 1: {result['phase1_iterations']}")
        print(f"   - Valor óptimo: {result['optimal_value']:.4f}")
        
        # Mostrar solución dinámicamente
        print("   - Solución:")
        for var_name, value in result["solution"].items():
            print(f"     {var_name} = {value:.4f}")
        
        # Verificaciones de assert
        self.assertEqual(result["status"], "optimal")
        self.assertIn("x1", result["solution"])
        self.assertIn("x2", result["solution"])
        self.assertIn("x3", result["solution"])
    
    def test_min_2vars_all_constraint_types(self):
        """Minimización con 2 variables usando todos los tipos de restricciones."""
        print("\n" + "="*70)
        print("TEST 6: Minimización 2 variables (todos los tipos)")
        print("="*70)
        
        # Problema: Minimizar z = 5x1 + 6x2
        # Sujeto a:
        # x1 + x2 ≥ 5
        # 2x1 + x2 ≤ 12
        # x1 = 3
        # x2 ≥ 2
        # x1, x2 ≥ 0
        c = [5, 6]
        A = [
            [1, 1],
            [2, 1],
            [1, 0],
            [0, 1]
        ]
        b = [5, 12, 3, 2]
        constraint_types = ['>=', '<=', '=', '>=']
        maximize = False
        
        # 1. Mostrar el problema
        print("\n1. PROBLEMA INGRESADO:")
        self.ui.display_problem(c, A, b, constraint_types, maximize)
        
        # 2. Resolver el problema
        print("\n2. PROCESANDO SOLUCIÓN...")
        result = self.solver.solve(c, A, b, constraint_types, maximize)
        
        # 3. Mostrar resultados
        print("\n3. RESULTADO OBTENIDO:")
        self.ui.display_result(result)
        
        # 4. Verificaciones básicas      
        print("\n4. INFORMACIÓN DE LA SOLUCIÓN:")
        print(f"   - Estado: {result['status']}")
        print(f"   - Iteraciones: {result['iterations']}")
        if 'phase1_iterations' in result:
            print(f"   - Iteraciones Fase 1: {result['phase1_iterations']}")
        print(f"   - Valor óptimo: {result['optimal_value']:.4f}")
        
        # Mostrar solución dinámicamente
        print("   - Solución:")
        for var_name, value in result["solution"].items():
            print(f"     {var_name} = {value:.4f}")
        
        # Verificaciones de assert
        self.assertEqual(result["status"], "optimal")
        self.assertIn("x1", result["solution"])
        self.assertIn("x2", result["solution"])
    
    def test_min_diet_problem(self):
        """Problema de la dieta - ejemplo clásico de minimización."""
        print("\n" + "="*70)
        print("TEST 7: Problema de la dieta (minimización clásica)")
        print("="*70)
        
        # Problema: Minimizar costo de la dieta
        # Alimento A: $2 por unidad, Alimento B: $3 por unidad
        # Requerimientos mínimos:
        # Nutriente X: al menos 4 unidades (2A + 1B ≥ 4)
        # Nutriente Y: al menos 5 unidades (1A + 2B ≥ 5)
        # Nutriente Z: exactamente 6 unidades (1A + 1B = 6)
        c = [2, 3]  # Costos de los alimentos
        A = [
            [2, 1],  # Nutriente X
            [1, 2],  # Nutriente Y
            [1, 1]   # Nutriente Z
        ]
        b = [4, 5, 6]
        constraint_types = ['>=', '>=', '=']
        maximize = False
        
        # 1. Mostrar el problema
        print("\n1. PROBLEMA INGRESADO:")
        self.ui.display_problem(c, A, b, constraint_types, maximize)
        
        # 2. Resolver el problema
        print("\n2. PROCESANDO SOLUCIÓN...")
        result = self.solver.solve(c, A, b, constraint_types, maximize)
        
        # 3. Mostrar resultados
        print("\n3. RESULTADO OBTENIDO:")
        self.ui.display_result(result)
        
        # 4. Verificaciones básicas      
        print("\n4. INFORMACIÓN DE LA SOLUCIÓN:")
        print(f"   - Estado: {result['status']}")
        print(f"   - Iteraciones: {result['iterations']}")
        if 'phase1_iterations' in result:
            print(f"   - Iteraciones Fase 1: {result['phase1_iterations']}")
        print(f"   - Valor óptimo: {result['optimal_value']:.4f}")
        
        # Mostrar solución dinámicamente
        print("   - Solución:")
        for var_name, value in result["solution"].items():
            print(f"     {var_name} = {value:.4f}")
        
        # Verificaciones de assert
        self.assertEqual(result["status"], "optimal")
        self.assertIn("x1", result["solution"])
        self.assertIn("x2", result["solution"])


def run_minimization_tests():
    """Función para ejecutar solo los tests de minimización."""
    print("EJECUTANDO TESTS DE MINIMIZACIÓN")
    print("=" * 70)
    
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestMinimizationProblems)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "="*70)
    print("RESUMEN TESTS MINIMIZACIÓN")
    print("="*70)
    
    if result.wasSuccessful():
        print("✅ Todos los tests de minimización pasaron exitosamente")
    else:
        print("❌ Algunos tests de minimización fallaron")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    run_minimization_tests()