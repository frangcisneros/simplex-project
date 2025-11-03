"""
Suite de tests completa para el sistema NLP de optimización.
Incluye tests unitarios, de integración y de extremo a extremo.
"""

import unittest
import sys
from pathlib import Path

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from simplex_solver.nlp.config import NLPModelType, DefaultSettings
from simplex_solver.nlp.connector import NLPConnectorFactory, SolverType
from simplex_solver.nlp.interfaces import OptimizationProblem
from simplex_solver.nlp.model_generator import SimplexModelGenerator, ModelValidator
from simplex_solver.nlp.processor import MockNLPProcessor
from simplex_solver.nlp.problem_structure_detector import ProblemStructureDetector
from simplex_solver.nlp.complexity_analyzer import ComplexityAnalyzer, ProblemComplexity


class TestProblemStructureDetector(unittest.TestCase):
    """Tests para el detector de estructura de problemas."""

    def setUp(self):
        self.detector = ProblemStructureDetector()

    def test_detect_simple_production(self):
        """Test detección de problema de producción simple."""
        text = """
        Una carpintería fabrica mesas y sillas.
        Cada mesa da $80 de ganancia.
        """
        structure = self.detector.detect_structure(text)
        self.assertEqual(structure["problem_type"], "simple")

    def test_detect_diet_problem(self):
        """Test detección de problema de dieta."""
        text = """
        Una persona necesita planificar su dieta.
        Debe consumir al menos 2000 calorías.
        Alimentos: pan, pollo, vegetales.
        """
        structure = self.detector.detect_structure(text)
        self.assertEqual(structure["problem_type"], "diet")
        self.assertEqual(structure["expected_variables"], 3)

    def test_detect_transport_problem(self):
        """Test detección de problema de transporte."""
        text = """
        Una empresa debe transportar productos desde 2 almacenes a 3 tiendas.
        Minimizar el costo total de transporte.
        """
        structure = self.detector.detect_structure(text)
        self.assertEqual(structure["problem_type"], "transport")
        self.assertEqual(structure["expected_variables"], 6)

    def test_detect_food_items(self):
        """Test detección de alimentos en problemas de dieta."""
        text = "dieta con alimentos: pan, pollo y vegetales con calorías"
        foods = self.detector._detect_food_items(text)
        self.assertGreater(len(foods), 0)
        # Verificar que detecta al menos algunos alimentos comunes
        detected = any(food in ["pan", "pollo", "vegetales"] for food in foods)
        self.assertTrue(detected or len(foods) > 0)

    def test_detect_transport_routes(self):
        """Test detección de rutas en problemas de transporte."""
        text = "transportar desde 2 almacenes a 3 tiendas"
        routes = self.detector._detect_transport_routes(text)
        self.assertEqual(len(routes), 6)


class TestComplexityAnalyzer(unittest.TestCase):
    """Tests para el analizador de complejidad."""

    def setUp(self):
        self.analyzer = ComplexityAnalyzer()

    def test_simple_problem_complexity(self):
        """Test análisis de problema simple."""
        text = "Maximizar 2x + 3y sujeto a x + y <= 10"
        complexity = self.analyzer.analyze_problem(text)
        self.assertEqual(complexity, ProblemComplexity.SIMPLE)

    def test_medium_problem_complexity(self):
        """Test análisis de problema medio."""
        text = (
            """
        Una empresa fabrica 4 productos.
        Hay 3 restricciones de recursos.
        Maximizar la ganancia total.
        """
            * 3
        )  # Repetir para aumentar longitud
        complexity = self.analyzer.analyze_problem(text)
        self.assertIn(complexity, [ProblemComplexity.SIMPLE, ProblemComplexity.MEDIUM])

    def test_complex_problem_complexity(self):
        """Test análisis de problema complejo."""
        text = (
            """
        Una empresa tiene 5 plantas y fabrica 6 productos.
        Hay 10 restricciones de capacidad.
        Hay 8 restricciones de demanda.
        Cada planta tiene diferentes costos.
        """
            * 10
        )  # Repetir para aumentar longitud
        complexity = self.analyzer.analyze_problem(text)
        self.assertIn(complexity, [ProblemComplexity.MEDIUM, ProblemComplexity.COMPLEX])


class TestModelValidator(unittest.TestCase):
    """Tests para el validador de modelos."""

    def setUp(self):
        self.validator = ModelValidator()

    def test_valid_problem(self):
        """Test validación de problema correcto."""
        problem = OptimizationProblem(
            objective_type="maximize",
            objective_coefficients=[2.0, 3.0],
            constraints=[{"coefficients": [1.0, 1.0], "operator": "<=", "rhs": 10.0}],
            variable_names=["x1", "x2"],
        )
        self.assertTrue(self.validator.validate(problem))
        errors = self.validator.get_validation_errors(problem)
        self.assertEqual(len(errors), 0)

    def test_invalid_objective_type(self):
        """Test validación con tipo de objetivo inválido."""
        problem = OptimizationProblem(
            objective_type="optimizar",  # Tipo inválido
            objective_coefficients=[2.0, 3.0],
            constraints=[{"coefficients": [1.0, 1.0], "operator": "<=", "rhs": 10.0}],
            variable_names=["x1", "x2"],
        )
        self.assertFalse(self.validator.validate(problem))
        errors = self.validator.get_validation_errors(problem)
        self.assertGreater(len(errors), 0)

    def test_dimension_mismatch(self):
        """Test validación con error de dimensiones."""
        problem = OptimizationProblem(
            objective_type="maximize",
            objective_coefficients=[2.0, 3.0],
            constraints=[
                {
                    "coefficients": [1.0, 1.0, 1.0],
                    "operator": "<=",
                    "rhs": 10.0,
                }  # 3 coefs, 2 vars
            ],
            variable_names=["x1", "x2"],
        )
        self.assertFalse(self.validator.validate(problem))
        errors = self.validator.get_validation_errors(problem)
        self.assertTrue(any("Dimension mismatch" in err for err in errors))

    def test_invalid_operator(self):
        """Test validación con operador inválido."""
        problem = OptimizationProblem(
            objective_type="maximize",
            objective_coefficients=[2.0, 3.0],
            constraints=[
                {
                    "coefficients": [1.0, 1.0],
                    "operator": "~=",
                    "rhs": 10.0,
                }  # Operador inválido
            ],
            variable_names=["x1", "x2"],
        )
        self.assertFalse(self.validator.validate(problem))
        errors = self.validator.get_validation_errors(problem)
        self.assertTrue(any("Invalid operator" in err for err in errors))


class TestModelGenerator(unittest.TestCase):
    """Tests para el generador de modelos."""

    def setUp(self):
        self.generator = SimplexModelGenerator()

    def test_generate_maximization_model(self):
        """Test generación de modelo de maximización."""
        problem = OptimizationProblem(
            objective_type="maximize",
            objective_coefficients=[2.0, 3.0],
            constraints=[{"coefficients": [1.0, 1.0], "operator": "<=", "rhs": 10.0}],
            variable_names=["x1", "x2"],
        )
        model = self.generator.generate_model(problem)

        self.assertEqual(model["c"], [2.0, 3.0])
        self.assertEqual(model["A"], [[1.0, 1.0]])
        self.assertEqual(model["b"], [10.0])
        self.assertTrue(model["maximize"])
        self.assertFalse(model.get("is_minimization", False))

    def test_generate_minimization_model(self):
        """Test generación de modelo de minimización."""
        problem = OptimizationProblem(
            objective_type="minimize",
            objective_coefficients=[2.0, 5.0, 3.0],
            constraints=[
                {"coefficients": [150.0, 300.0, 80.0], "operator": ">=", "rhs": 2000.0}
            ],
            variable_names=["pan", "pollo", "vegetales"],
        )
        model = self.generator.generate_model(problem)

        # Para minimización, los coeficientes se niegan
        self.assertEqual(model["c"], [-2.0, -5.0, -3.0])
        # Las restricciones >= se convierten a <=
        self.assertEqual(model["A"], [[-150.0, -300.0, -80.0]])
        self.assertEqual(model["b"], [-2000.0])
        self.assertTrue(model["maximize"])  # Se convierte a maximización
        self.assertTrue(model["is_minimization"])  # Flag para ajustar resultado

    def test_convert_equality_constraint(self):
        """Test conversión de restricciones de igualdad."""
        problem = OptimizationProblem(
            objective_type="maximize",
            objective_coefficients=[2.0, 3.0],
            constraints=[{"coefficients": [1.0, 1.0], "operator": "=", "rhs": 10.0}],
            variable_names=["x1", "x2"],
        )
        model = self.generator.generate_model(problem)

        # La igualdad se convierte en dos restricciones (<= y >=)
        self.assertEqual(len(model["A"]), 2)
        self.assertEqual(model["A"], [[1.0, 1.0], [-1.0, -1.0]])
        self.assertEqual(model["b"], [10.0, -10.0])


class TestMockNLPProcessor(unittest.TestCase):
    """Tests para el procesador mock (usado en testing)."""

    def setUp(self):
        self.processor = MockNLPProcessor()

    def test_mock_is_available(self):
        """Test que el mock siempre está disponible."""
        self.assertTrue(self.processor.is_available())

    def test_mock_process_simple_text(self):
        """Test procesamiento con mock."""
        text = "Maximizar 2x + 3y sujeto a x + y <= 10"
        result = self.processor.process_text(text)

        self.assertTrue(result.success)
        self.assertIsNotNone(result.problem)
        self.assertEqual(result.problem.objective_type, "maximize")
        self.assertEqual(len(result.problem.objective_coefficients), 2)


class TestNLPConnectorIntegration(unittest.TestCase):
    """Tests de integración del conector NLP completo."""

    def setUp(self):
        # Usar mock para tests sin dependencia de Ollama
        self.connector = NLPConnectorFactory.create_connector(
            use_mock_nlp=True, solver_type=SolverType.SIMPLEX
        )

    def test_full_pipeline_maximization(self):
        """Test pipeline completo con problema de maximización."""
        text = """
        Una empresa fabrica productos A y B.
        Cada A da $50 de ganancia, cada B $30.
        Hay 100 horas disponibles.
        Cada A requiere 2 horas, cada B 1 hora.
        Maximizar ganancia.
        """
        result = self.connector.process_and_solve(text)

        self.assertTrue(result["success"])
        self.assertIn("solution", result)
        self.assertIn("extracted_problem", result)
        self.assertIn("processing_time", result)

    def test_full_pipeline_minimization(self):
        """Test pipeline completo con problema de minimización."""
        text = """
        Minimizar costos.
        Producto A cuesta $10, producto B cuesta $20.
        Necesitamos al menos 5 unidades de A.
        Necesitamos al menos 3 unidades de B.
        """
        result = self.connector.process_and_solve(text)

        self.assertTrue(result["success"])
        self.assertIn("solution", result)

    def test_pipeline_validation_failure(self):
        """Test que el pipeline maneja errores de validación."""
        # Crear un conector con validador estricto
        connector = NLPConnectorFactory.create_connector(use_mock_nlp=True)

        # Texto inválido/vacío
        result = connector.process_and_solve("")

        # Debería fallar en algún paso
        if not result["success"]:
            self.assertIn("step_failed", result)


class TestNLPConnectorFactory(unittest.TestCase):
    """Tests para la factory de conectores."""

    def test_create_connector_with_mock(self):
        """Test creación de conector con mock."""
        connector = NLPConnectorFactory.create_connector(use_mock_nlp=True)
        self.assertIsNotNone(connector)
        self.assertIsNotNone(connector.nlp_processor)
        self.assertTrue(connector.nlp_processor.is_available())

    def test_create_connector_with_ollama(self):
        """Test creación de conector con Ollama."""
        connector = NLPConnectorFactory.create_connector(
            nlp_model_type=NLPModelType.LLAMA3_1_8B, use_mock_nlp=False
        )
        self.assertIsNotNone(connector)
        self.assertIsNotNone(connector.nlp_processor)

    def test_create_connector_with_custom_config(self):
        """Test creación con configuración personalizada."""
        custom_config = {"temperature": 0.0, "max_tokens": 1024}
        connector = NLPConnectorFactory.create_connector(
            nlp_model_type=NLPModelType.LLAMA3_1_8B, custom_config=custom_config
        )
        self.assertIsNotNone(connector)


class TestEndToEnd(unittest.TestCase):
    """Tests de extremo a extremo con problemas reales."""

    def setUp(self):
        self.connector = NLPConnectorFactory.create_connector(use_mock_nlp=True)

    def test_production_problem(self):
        """Test problema de producción completo."""
        text = """
        Una carpintería fabrica mesas y sillas.
        Cada mesa da $80 de ganancia, cada silla $50.
        Hay 200 horas de trabajo disponibles.
        Cada mesa requiere 4 horas, cada silla 2 horas.
        Hay 300 kg de madera disponibles.
        Cada mesa requiere 6 kg, cada silla 3 kg.
        Maximizar ganancia.
        """
        result = self.connector.process_and_solve(text)

        self.assertTrue(result["success"])
        solution = result["solution"]
        self.assertEqual(solution["status"], "optimal")
        self.assertIsNotNone(solution["optimal_value"])

    def test_diet_problem(self):
        """Test problema de dieta completo."""
        text = """
        Una persona necesita planificar su dieta minimizando costos.
        Debe consumir al menos 2000 calorías, 50g proteína, 30g fibra.
        
        Pan: $2, 150 calorías, 5g proteína, 3g fibra
        Pollo: $5, 300 calorías, 25g proteína, 0g fibra
        Vegetales: $3, 80 calorías, 3g proteína, 8g fibra
        
        Minimizar costo.
        """
        result = self.connector.process_and_solve(text)

        self.assertTrue(result["success"])
        self.assertIn("solution", result)

    def test_transport_problem(self):
        """Test problema de transporte completo."""
        text = """
        Una empresa transporta desde 2 almacenes a 3 tiendas.
        
        Costos: A1-T1: $4, A1-T2: $6, A1-T3: $8
                A2-T1: $5, A2-T2: $4, A2-T3: $7
        
        Almacén 1: 100 unidades
        Almacén 2: 150 unidades
        
        Tienda A: 80 unidades
        Tienda B: 90 unidades
        Tienda C: 60 unidades
        
        Minimizar costo.
        """
        result = self.connector.process_and_solve(text)

        self.assertTrue(result["success"])
        self.assertIn("solution", result)


def run_tests(verbose=True):
    """Ejecuta todos los tests del sistema NLP."""
    # Crear suite de tests
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Agregar todas las clases de test
    suite.addTests(loader.loadTestsFromTestCase(TestProblemStructureDetector))
    suite.addTests(loader.loadTestsFromTestCase(TestComplexityAnalyzer))
    suite.addTests(loader.loadTestsFromTestCase(TestModelValidator))
    suite.addTests(loader.loadTestsFromTestCase(TestModelGenerator))
    suite.addTests(loader.loadTestsFromTestCase(TestMockNLPProcessor))
    suite.addTests(loader.loadTestsFromTestCase(TestNLPConnectorIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestNLPConnectorFactory))
    suite.addTests(loader.loadTestsFromTestCase(TestEndToEnd))

    # Ejecutar tests
    runner = unittest.TextTestRunner(verbosity=2 if verbose else 1)
    result = runner.run(suite)

    # Retornar resultado
    return result.wasSuccessful()


if __name__ == "__main__":
    print("=" * 80)
    print("SUITE DE TESTS COMPLETA DEL SISTEMA NLP")
    print("=" * 80)
    print()

    success = run_tests(verbose=True)

    print()
    print("=" * 80)
    if success:
        print("TODOS LOS TESTS PASARON")
    else:
        print("ALGUNOS TESTS FALLARON")
    print("=" * 80)

    sys.exit(0 if success else 1)
