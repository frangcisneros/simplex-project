#!/usr/bin/env python3
"""
Tests básicos para el sistema simplex.
"""

import unittest
import numpy as np
from src.solver import SimplexSolver
from src.file_parser import FileParser
from src.user_interface import UserInterface


class TestSimplexSolver(unittest.TestCase):
    """Tests para el solver simplex."""
    
    def test_maximization_problem(self):
        """Test de un problema de maximización simple."""
        solver = SimplexSolver()
        
        # Problema: Maximizar 3x1 + 2x2
        # Sujeto a:
        # 2x1 + x2 <= 100
        # x1 + x2 <= 80
        # x1 <= 40
        # x1, x2 >= 0
        c = [3, 2]
        A = [
            [2, 1],
            [1, 1],
            [1, 0]
        ]
        b = [100, 80, 40]
        
        result = solver.solve(c, A, b, maximize=True)
        
        self.assertEqual(result["status"], "optimal")
        self.assertAlmostEqual(result["optimal_value"], 180.0, places=2)
        self.assertIn("x1", result["solution"])
        self.assertIn("x2", result["solution"])
    
    def test_minimization_problem(self):
        """Test de un problema de minimización simple."""
        solver = SimplexSolver()
        
        # Problema de minimización simple
        c = [1, 1]
        A = [
            [2, 1],
            [1, 2]
        ]
        b = [4, 3]
        
        result = solver.solve(c, A, b, maximize=False)
        
        self.assertEqual(result["status"], "optimal")
        self.assertGreaterEqual(result["optimal_value"], 0)
    
    def test_file_parser(self):
        """Test del parser de archivos."""
        # Este test requeriría un archivo de ejemplo
        # Se puede crear un archivo temporal para testing
        pass
    
    def test_unbounded_problem(self):
        """Test de problema no acotado."""
        solver = SimplexSolver()
        
        # Problema no acotado
        c = [1, 1]
        A = [
            [1, -1]
        ]
        b = [1]
        
        result = solver.solve(c, A, b, maximize=True)
        
        self.assertEqual(result["status"], "unbounded")


class TestTableau(unittest.TestCase):
    """Tests para las operaciones del tableau."""
    
    def test_tableau_construction(self):
        """Test de construcción del tableau."""
        from src.tableau import Tableau
        
        tableau = Tableau()
        c = [3, 2]
        A = [[2, 1], [1, 1]]
        b = [100, 80]
        
        tableau.build_initial_tableau(c, A, b, maximize=True)
        
        self.assertIsNotNone(tableau.tableau)
        self.assertEqual(tableau.tableau.shape, (3, 5))  # 2 restricciones + 1 fila objetivo
        self.assertEqual(len(tableau.basic_vars), 2)


if __name__ == "__main__":
    # Ejecutar tests
    unittest.main(verbosity=2)