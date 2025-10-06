"""
Tests unitarios para el sistema NLP de optimización.
"""

import sys
from pathlib import Path
import unittest
from unittest.mock import Mock, patch

# Agregar src al path para importar módulos
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from nlp import (
    OptimizationProblem,
    NLPResult,
    MockNLPProcessor,
    SimplexModelGenerator,
    ModelValidator,
    SimplexSolverAdapter,
    NLPConnectorFactory,
    SolverType,
)


class TestOptimizationProblem(unittest.TestCase):
    """Tests para la estructura OptimizationProblem."""

    def test_optimization_problem_creation(self):
        """Test creación básica de problema de optimización."""
        problem = OptimizationProblem(
            objective_type="maximize",
            objective_coefficients=[1.0, 2.0, 3.0],
            constraints=[
                {"coefficients": [1.0, 1.0, 0.0], "operator": "<=", "rhs": 10.0},
                {"coefficients": [0.0, 1.0, 1.0], "operator": "<=", "rhs": 15.0},
            ],
        )

        self.assertEqual(problem.objective_type, "maximize")
        self.assertEqual(len(problem.objective_coefficients), 3)
        self.assertEqual(len(problem.constraints), 2)
        self.assertEqual(problem.variable_names, ["x1", "x2", "x3"])

    def test_optimization_problem_with_custom_names(self):
        """Test con nombres personalizados de variables."""
        problem = OptimizationProblem(
            objective_type="minimize",
            objective_coefficients=[5.0, 3.0],
            constraints=[{"coefficients": [2.0, 1.0], "operator": ">=", "rhs": 8.0}],
            variable_names=["production", "inventory"],
        )

        self.assertEqual(problem.variable_names, ["production", "inventory"])


class TestMockNLPProcessor(unittest.TestCase):
    """Tests para el procesador NLP mock."""

    def setUp(self):
        self.processor = MockNLPProcessor()

    def test_is_available(self):
        """Test disponibilidad del procesador mock."""
        self.assertTrue(self.processor.is_available())

    def test_process_text_maximize(self):
        """Test procesamiento de texto con maximización."""
        text = "Maximizar la función objetivo sujeto a restricciones"
        result = self.processor.process_text(text)

        self.assertTrue(result.success)
        self.assertIsNotNone(result.problem)
        if result.problem:
            self.assertEqual(result.problem.objective_type, "maximize")
        if result.confidence_score:
            self.assertGreater(result.confidence_score, 0.5)

    def test_process_text_minimize(self):
        """Test procesamiento de texto con minimización."""
        text = "Minimizar los costos de producción"
        result = self.processor.process_text(text)

        self.assertTrue(result.success)
        self.assertIsNotNone(result.problem)
        if result.problem:
            self.assertEqual(result.problem.objective_type, "minimize")


class TestModelValidator(unittest.TestCase):
    """Tests para el validador de modelos."""

    def setUp(self):
        self.validator = ModelValidator()

    def test_valid_problem(self):
        """Test validación de problema válido."""
        problem = OptimizationProblem(
            objective_type="maximize",
            objective_coefficients=[1.0, 2.0],
            constraints=[{"coefficients": [1.0, 1.0], "operator": "<=", "rhs": 10.0}],
        )

        self.assertTrue(self.validator.validate(problem))
        self.assertEqual(len(self.validator.get_validation_errors(problem)), 0)

    def test_invalid_objective_type(self):
        """Test validación con tipo de objetivo inválido."""
        problem = OptimizationProblem(
            objective_type="invalid",
            objective_coefficients=[1.0, 2.0],
            constraints=[{"coefficients": [1.0, 1.0], "operator": "<=", "rhs": 10.0}],
        )

        self.assertFalse(self.validator.validate(problem))
        errors = self.validator.get_validation_errors(problem)
        self.assertTrue(any("Invalid objective type" in error for error in errors))

    def test_dimension_mismatch(self):
        """Test validación con dimensiones inconsistentes."""
        problem = OptimizationProblem(
            objective_type="maximize",
            objective_coefficients=[1.0, 2.0],  # 2 variables
            constraints=[
                {
                    "coefficients": [1.0, 1.0, 1.0],
                    "operator": "<=",
                    "rhs": 10.0,
                }  # 3 coeficientes
            ],
        )

        self.assertFalse(self.validator.validate(problem))
        errors = self.validator.get_validation_errors(problem)
        self.assertTrue(any("Dimension mismatch" in error for error in errors))

    def test_empty_constraints(self):
        """Test validación sin restricciones."""
        problem = OptimizationProblem(
            objective_type="maximize", objective_coefficients=[1.0, 2.0], constraints=[]
        )

        self.assertFalse(self.validator.validate(problem))
        errors = self.validator.get_validation_errors(problem)
        self.assertTrue(any("No constraints found" in error for error in errors))


class TestSimplexModelGenerator(unittest.TestCase):
    """Tests para el generador de modelos Simplex."""

    def setUp(self):
        self.generator = SimplexModelGenerator()

    def test_generate_maximize_model(self):
        """Test generación de modelo de maximización."""
        problem = OptimizationProblem(
            objective_type="maximize",
            objective_coefficients=[3.0, 2.0],
            constraints=[
                {"coefficients": [1.0, 1.0], "operator": "<=", "rhs": 4.0},
                {"coefficients": [2.0, 1.0], "operator": "<=", "rhs": 6.0},
            ],
        )

        model = self.generator.generate_model(problem)

        self.assertEqual(model["c"], [3.0, 2.0])
        self.assertEqual(model["A"], [[1.0, 1.0], [2.0, 1.0]])
        self.assertEqual(model["b"], [4.0, 6.0])
        self.assertTrue(model["maximize"])

    def test_generate_minimize_model(self):
        """Test generación de modelo de minimización."""
        problem = OptimizationProblem(
            objective_type="minimize",
            objective_coefficients=[1.0, 2.0],
            constraints=[{"coefficients": [1.0, 1.0], "operator": ">=", "rhs": 3.0}],
        )

        model = self.generator.generate_model(problem)

        self.assertEqual(model["c"], [1.0, 2.0])
        # Restricción >= se convierte a <= multiplicando por -1
        self.assertEqual(model["A"], [[-1.0, -1.0]])
        self.assertEqual(model["b"], [-3.0])
        self.assertFalse(model["maximize"])

    def test_generate_equality_constraint(self):
        """Test generación con restricción de igualdad."""
        problem = OptimizationProblem(
            objective_type="maximize",
            objective_coefficients=[1.0, 1.0],
            constraints=[{"coefficients": [1.0, 2.0], "operator": "=", "rhs": 5.0}],
        )

        model = self.generator.generate_model(problem)

        # Restricción de igualdad se convierte en dos restricciones
        self.assertEqual(len(model["A"]), 2)
        self.assertEqual(model["A"][0], [1.0, 2.0])
        self.assertEqual(model["A"][1], [-1.0, -2.0])
        self.assertEqual(model["b"], [5.0, -5.0])


class TestSimplexSolverAdapter(unittest.TestCase):
    """Tests para el adaptador de SimplexSolver."""

    def setUp(self):
        self.adapter = SimplexSolverAdapter()

    def test_solve_simple_problem(self):
        """Test resolución de problema simple."""
        model = {
            "c": [3.0, 2.0],
            "A": [[1.0, 1.0], [2.0, 1.0]],
            "b": [4.0, 6.0],
            "maximize": True,
        }

        result = self.adapter.solve(model)

        # Verificar que se obtuvo una solución
        self.assertIn("status", result)
        if result["status"] == "optimal":
            self.assertIn("solution", result)
            self.assertIn("optimal_value", result)

    def test_solve_with_variable_names(self):
        """Test resolución con nombres de variables personalizados."""
        model = {
            "c": [1.0, 2.0],
            "A": [[1.0, 1.0]],
            "b": [10.0],
            "maximize": True,
            "variable_names": ["producto_a", "producto_b"],
        }

        result = self.adapter.solve(model)

        if result["status"] == "optimal":
            self.assertIn("named_solution", result)
            named_sol = result["named_solution"]
            self.assertIn("producto_a", named_sol)
            self.assertIn("producto_b", named_sol)


class TestNLPConnectorIntegration(unittest.TestCase):
    """Tests de integración para el conector NLP."""

    def test_create_connector_with_mock(self):
        """Test creación de conector con NLP mock."""
        connector = NLPConnectorFactory.create_connector(
            solver_type=SolverType.SIMPLEX, use_mock_nlp=True
        )

        self.assertIsNotNone(connector)

        # Verificar health check
        health = connector.health_check()
        self.assertIn("overall_status", health)
        self.assertIn("components", health)

    def test_process_and_solve_with_mock(self):
        """Test pipeline completo con procesador mock."""
        connector = NLPConnectorFactory.create_connector(
            solver_type=SolverType.SIMPLEX, use_mock_nlp=True
        )

        text = "Maximizar 2x + 3y sujeto a x + y <= 10"
        result = connector.process_and_solve(text)

        self.assertIn("success", result)
        if result["success"]:
            self.assertIn("solution", result)
            self.assertIn("extracted_problem", result)
            self.assertIn("processing_time", result)
        else:
            self.assertIn("error", result)
            self.assertIn("step_failed", result)


class TestErrorHandling(unittest.TestCase):
    """Tests para manejo de errores."""

    def test_invalid_model_keys(self):
        """Test manejo de modelo con claves faltantes."""
        adapter = SimplexSolverAdapter()
        incomplete_model = {
            "c": [1.0, 2.0],
            # Falta 'A', 'b', 'maximize'
        }

        result = adapter.solve(incomplete_model)

        self.assertEqual(result["status"], "error")
        self.assertIn("message", result)

    def test_nlp_result_without_problem(self):
        """Test manejo de resultado NLP sin problema extraído."""
        # Mock NLP processor que retorna resultado sin problema
        mock_processor = Mock()
        mock_processor.is_available.return_value = True
        mock_processor.process_text.return_value = NLPResult(
            success=True, problem=None, error_message=None  # Sin problema extraído
        )

        from nlp import NLPOptimizationConnector

        connector = NLPOptimizationConnector(
            nlp_processor=mock_processor,
            model_generator=SimplexModelGenerator(),
            solver=SimplexSolverAdapter(),
            validator=ModelValidator(),
        )

        result = connector.process_and_solve("test text")

        self.assertFalse(result["success"])
        self.assertEqual(result["step_failed"], "problem_extraction")


if __name__ == "__main__":
    # Configurar logging para tests
    import logging

    logging.basicConfig(level=logging.WARNING)

    unittest.main(verbosity=2)
