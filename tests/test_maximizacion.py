"""
Tests para problemas de MAXIMIZACIÓN del método simplex.
Contiene ejercicios con 2 y 3 variables con diferentes tipos de restricciones.
"""

import unittest
import sys
import os

# Agregar el directorio padre al path para importar los módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from simplex_solver.solver import SimplexSolver
from simplex_solver.user_interface import UserInterface


class TestMaximizationProblems(unittest.TestCase):
    """Tests para problemas de maximización."""
    
    def setUp(self):
        """Configura el solver antes de cada test."""
        self.solver = SimplexSolver()
        self.ui = UserInterface()
    
    def test_max_2vars_only_less_equal(self):
        """Maximización con 2 variables y solo restricciones <=."""
        print("\n" + "="*70)
        print("TEST 1: Maximización 2 variables (solo <=)")
        print("="*70)
        
        # Problema: Maximizar z = 3x1 + 2x2
        # Sujeto a:
        # 2x1 + x2 ≤ 100
        # x1 + x2 ≤ 80
        # x1 ≤ 40
        # x1, x2 ≥ 0
        c = [3, 2]
        A = [
            [2, 1],
            [1, 1], 
            [1, 0]
        ]
        b = [100, 80, 40]
        constraint_types = ['<=', '<=', '<=']
        maximize = True
        
        # 1. Mostrar el problema
        print("\n1. PROBLEMA INGRESADO:")
        self.ui.display_problem(c, A, b, constraint_types, maximize)
        
        # 2. Resolver el problema
        print("\n2. PROCESANDO SOLUCIÓN...")
        result = self.solver.solve(c, A, b, constraint_types, maximize)
        
        # 3. Mostrar resultados
        print("\n3. RESULTADO OBTENIDO:")
        self.ui.display_result(result)
    
    def test_max_2vars_with_greater_equal(self):
        """Maximización con 2 variables y restricciones >=."""
        print("\n" + "="*70)
        print("TEST 2: Maximización 2 variables (con >=)")
        print("="*70)
        
        # Problema: Maximizar z = 4x1 + 3x2
        # Sujeto a:
        # 2x1 + x2 ≥ 10
        # x1 + 2x2 ≥ 8
        # x1 ≤ 6
        # x2 ≤ 5
        # x1, x2 ≥ 0
        c = [4, 3]
        A = [
            [2, 1],
            [1, 2],
            [1, 0],
            [0, 1]
        ]
        b = [10, 8, 6, 5]
        constraint_types = ['>=', '>=', '<=', '<=']
        maximize = True
        
        # 1. Mostrar el problema
        print("\n1. PROBLEMA INGRESADO:")
        self.ui.display_problem(c, A, b, constraint_types, maximize)
        
        # 2. Resolver el problema
        print("\n2. PROCESANDO SOLUCIÓN...")
        result = self.solver.solve(c, A, b, constraint_types, maximize)
        
        # 3. Mostrar resultados
        print("\n3. RESULTADO OBTENIDO:")
        self.ui.display_result(result)

    def test_max_2vars_with_equal(self):
        """Maximización con 2 variables y restricción =."""
        print("\n" + "="*70)
        print("TEST 3: Maximización 2 variables (con =)")
        print("="*70)
        
        # Problema: Maximizar z = 2x1 + 5x2
        # Sujeto a:
        # x1 + x2 = 8
        # 2x1 + x2 ≤ 12
        # x1 ≤ 6
        # x1, x2 ≥ 0
        c = [2, 5]
        A = [
            [1, 1],
            [2, 1],
            [1, 0]
        ]
        b = [8, 12, 6]
        constraint_types = ['=', '<=', '<=']
        maximize = True
        
        # 1. Mostrar el problema
        print("\n1. PROBLEMA INGRESADO:")
        self.ui.display_problem(c, A, b, constraint_types, maximize)
        
        # 2. Resolver el problema
        print("\n2. PROCESANDO SOLUCIÓN...")
        result = self.solver.solve(c, A, b, constraint_types, maximize)
        
        # 3. Mostrar resultados
        print("\n3. RESULTADO OBTENIDO:")
        self.ui.display_result(result)
    
    def test_max_3vars_mixed_constraints(self):
        """Maximización con 3 variables y mezcla de restricciones."""
        print("\n" + "="*70)
        print("TEST 4: Maximización 3 variables (restricciones mixtas)")
        print("="*70)
        
        # Problema: Maximizar z = 3x1 + 2x2 + 4x3
        # Sujeto a:
        # x1 + x2 + x3 ≤ 10
        # 2x1 + x2 + 3x3 ≥ 6
        # x1 + 2x2 + x3 = 8
        # x1, x2, x3 ≥ 0
        c = [3, 2, 4]
        A = [
            [1, 1, 1],
            [2, 1, 3],
            [1, 2, 1]
        ]
        b = [10, 6, 8]
        constraint_types = ['<=', '>=', '=']
        maximize = True
        
        # 1. Mostrar el problema
        print("\n1. PROBLEMA INGRESADO:")
        self.ui.display_problem(c, A, b, constraint_types, maximize)
        
        # 2. Resolver el problema
        print("\n2. PROCESANDO SOLUCIÓN...")
        result = self.solver.solve(c, A, b, constraint_types, maximize)
        
        # 3. Mostrar resultados
        print("\n3. RESULTADO OBTENIDO:")
        self.ui.display_result(result)
    
    def test_max_3vars_only_less_equal(self):
        """Maximización con 3 variables y solo restricciones <=."""
        print("\n" + "="*70)
        print("TEST 5: Maximización 3 variables (solo <=)")
        print("="*70)
        
        # Problema: Maximizar z = 5x1 + 4x2 + 3x3
        # Sujeto a:
        # 2x1 + 3x2 + x3 ≤ 5
        # 4x1 + x2 + 2x3 ≤ 11
        # 3x1 + 4x2 + 2x3 ≤ 8
        # x1, x2, x3 ≥ 0
        c = [5, 4, 3]
        A = [
            [2, 3, 1],
            [4, 1, 2],
            [3, 4, 2]
        ]
        b = [5, 11, 8]
        constraint_types = ['<=', '<=', '<=']
        maximize = True
        
        # 1. Mostrar el problema
        print("\n1. PROBLEMA INGRESADO:")
        self.ui.display_problem(c, A, b, constraint_types, maximize)
        
        # 2. Resolver el problema
        print("\n2. PROCESANDO SOLUCIÓN...")
        result = self.solver.solve(c, A, b, constraint_types, maximize)
        
        # 3. Mostrar resultados
        print("\n3. RESULTADO OBTENIDO:")
        self.ui.display_result(result)
    
    def test_max_2vars_all_constraint_types(self):
        """Maximización con 2 variables usando todos los tipos de restricciones."""
        print("\n" + "="*70)
        print("TEST 6: Maximización 2 variables (todos los tipos)")
        print("="*70)
        
        # Problema: Maximizar z = 6x1 + 8x2
        # Sujeto a:
        # x1 + x2 ≤ 10
        # 2x1 + x2 ≥ 4  
        # x1 = 2
        # x2 ≤ 8
        # x1, x2 ≥ 0
        c = [6, 8]
        A = [
            [1, 1],
            [2, 1],
            [1, 0],
            [0, 1]
        ]
        b = [10, 4, 2, 8]
        constraint_types = ['<=', '>=', '=', '<=']
        maximize = True
        
        # 1. Mostrar el problema
        print("\n1. PROBLEMA INGRESADO:")
        self.ui.display_problem(c, A, b, constraint_types, maximize)
        
        # 2. Resolver el problema
        print("\n2. PROCESANDO SOLUCIÓN...")
        result = self.solver.solve(c, A, b, constraint_types, maximize)
        
        # 3. Mostrar resultados
        print("\n3. RESULTADO OBTENIDO:")
        self.ui.display_result(result)


def run_maximization_tests():
    """Función para ejecutar solo los tests de maximización."""
    print("EJECUTANDO TESTS DE MAXIMIZACIÓN")
    print("=" * 70)

    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestMaximizationProblems)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "="*70)
    print("RESUMEN TESTS MAXIMIZACIÓN")
    print("="*70)
    
    if result.wasSuccessful():
        print("✅ Todos los tests de maximización pasaron exitosamente")
    else:
        print("❌ Algunos tests de maximización fallaron")
    
    return result.wasSuccessful()

if __name__ == "__main__":
    run_maximization_tests()
