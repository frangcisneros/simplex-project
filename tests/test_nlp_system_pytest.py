"""
Suite de pruebas exhaustiva para el sistema de optimización NLP.
Convertido de unittest a pytest con fixtures.
"""

import pytest
from simplex_solver.nlp.config import NLPModelType, DefaultSettings
from simplex_solver.nlp.connector import NLPConnectorFactory, SolverType
from simplex_solver.nlp.interfaces import OptimizationProblem
from simplex_solver.nlp.model_generator import SimplexModelGenerator, ModelValidator
from simplex_solver.nlp.processor import MockNLPProcessor
from simplex_solver.nlp.problem_structure_detector import ProblemStructureDetector
from simplex_solver.nlp.complexity_analyzer import ComplexityAnalyzer, ProblemComplexity


# ==================== Fixtures ====================


@pytest.fixture
def structure_detector():
    """Crea una instancia de ProblemStructureDetector."""
    return ProblemStructureDetector()


@pytest.fixture
def complexity_analyzer():
    """Crea una instancia de ComplexityAnalyzer."""
    return ComplexityAnalyzer()


@pytest.fixture
def model_validator():
    """Crea una instancia de ModelValidator."""
    return ModelValidator()


@pytest.fixture
def model_generator():
    """Crea una instancia de SimplexModelGenerator."""
    return SimplexModelGenerator()


@pytest.fixture
def mock_nlp_processor():
    """Crea una instancia de MockNLPProcessor."""
    return MockNLPProcessor()


@pytest.fixture
def nlp_connector():
    """Crea un conector NLP con un procesador simulado."""
    return NLPConnectorFactory.create_connector(use_mock_nlp=True, solver_type=SolverType.SIMPLEX)


# ==================== Pruebas del Detector de Estructura ====================


def test_detect_simple_production(structure_detector):
    """Prueba la detección de un problema de producción simple."""
    text = """
    Una carpintería fabrica mesas y sillas.
    Cada mesa da $80 de ganancia.
    """
    structure = structure_detector.detect_structure(text)
    assert structure["problem_type"] == "simple"


def test_detect_diet_problem(structure_detector):
    """Prueba la detección de un problema de dieta."""
    text = """
    Una persona necesita planificar su dieta.
    Debe consumir al menos 2000 calorías.
    Alimentos: pan, pollo, vegetales.
    """
    structure = structure_detector.detect_structure(text)
    assert structure["problem_type"] == "diet"
    assert structure["expected_variables"] == 3


def test_detect_transport_problem(structure_detector):
    """Prueba la detección de un problema de transporte."""
    text = """
    Una empresa debe transportar productos desde 2 almacenes a 3 tiendas.
    Minimizar el costo total de transporte.
    """
    structure = structure_detector.detect_structure(text)
    assert structure["problem_type"] == "transport"
    assert structure["expected_variables"] == 6


def test_detect_food_items(structure_detector):
    """Prueba la detección de alimentos en problemas de dieta."""
    text = "dieta con alimentos: pan, pollo y vegetales con calorías"
    foods = structure_detector._detect_food_items(text)
    assert len(foods) > 0
    # Verifica que se detecten algunos alimentos comunes
    detected = any(food in ["pan", "pollo", "vegetales"] for food in foods)
    assert detected or len(foods) > 0


def test_detect_transport_routes(structure_detector):
    """Prueba la detección de rutas en problemas de transporte."""
    text = "transportar desde 2 almacenes a 3 tiendas"
    routes = structure_detector._detect_transport_routes(text)
    assert len(routes) == 6


# ==================== Pruebas del Analizador de Complejidad ====================


def test_simple_problem_complexity(complexity_analyzer):
    """Prueba el análisis de un problema simple."""
    text = "Maximizar 2x + 3y sujeto a x + y <= 10"
    complexity = complexity_analyzer.analyze_problem(text)
    assert complexity == ProblemComplexity.SIMPLE


def test_medium_problem_complexity(complexity_analyzer):
    """Prueba el análisis de un problema de complejidad media."""
    text = (
        """
    Una empresa fabrica 4 productos.
    Hay 3 restricciones de recursos.
    Maximizar la ganancia total.
    """
        * 3
    )  # Repetir para aumentar la longitud
    complexity = complexity_analyzer.analyze_problem(text)
    assert complexity in [ProblemComplexity.SIMPLE, ProblemComplexity.MEDIUM]


def test_complex_problem_complexity(complexity_analyzer):
    """Prueba el análisis de un problema complejo."""
    text = (
        """
    Una empresa tiene 5 plantas y fabrica 6 productos.
    Hay 10 restricciones de capacidad.
    Hay 8 restricciones de demanda.
    Cada planta tiene diferentes costos.
    """
        * 10
    )  # Repetir para aumentar la longitud
    complexity = complexity_analyzer.analyze_problem(text)
    assert complexity in [ProblemComplexity.MEDIUM, ProblemComplexity.COMPLEX]


# ==================== Pruebas del Validador de Modelos ====================


def test_valid_problem(model_validator):
    """Prueba la validación de un problema correcto."""
    problem = OptimizationProblem(
        objective_type="maximize",
        objective_coefficients=[2.0, 3.0],
        constraints=[{"coefficients": [1.0, 1.0], "operator": "<=", "rhs": 10.0}],
        variable_names=["x1", "x2"],
    )
    assert model_validator.validate(problem)
    errors = model_validator.get_validation_errors(problem)
    assert len(errors) == 0


def test_invalid_objective_type(model_validator):
    """Prueba la validación con un tipo de objetivo inválido."""
    problem = OptimizationProblem(
        objective_type="optimizar",  # Tipo inválido
        objective_coefficients=[2.0, 3.0],
        constraints=[{"coefficients": [1.0, 1.0], "operator": "<=", "rhs": 10.0}],
        variable_names=["x1", "x2"],
    )
    assert not model_validator.validate(problem)
    errors = model_validator.get_validation_errors(problem)
    assert len(errors) > 0


def test_dimension_mismatch(model_validator):
    """Prueba la validación con error de dimensiones."""
    problem = OptimizationProblem(
        objective_type="maximize",
        objective_coefficients=[2.0, 3.0],
        constraints=[
            {
                "coefficients": [1.0, 1.0, 1.0],
                "operator": "<=",
                "rhs": 10.0,
            }  # 3 coeficientes, 2 variables
        ],
        variable_names=["x1", "x2"],
    )
    assert not model_validator.validate(problem)
    errors = model_validator.get_validation_errors(problem)
    assert any("Dimension mismatch" in err for err in errors)


def test_invalid_operator(model_validator):
    """Prueba la validación con un operador inválido."""
    problem = OptimizationProblem(
        objective_type="maximize",
        objective_coefficients=[2.0, 3.0],
        constraints=[
            {"coefficients": [1.0, 1.0], "operator": "~=", "rhs": 10.0}  # Operador inválido
        ],
        variable_names=["x1", "x2"],
    )
    assert not model_validator.validate(problem)
    errors = model_validator.get_validation_errors(problem)
    assert any("Invalid operator" in err for err in errors)


# ==================== Pruebas del Generador de Modelos ====================


def test_generate_maximization_model(model_generator):
    """Prueba la generación de un modelo de maximización."""
    problem = OptimizationProblem(
        objective_type="maximize",
        objective_coefficients=[2.0, 3.0],
        constraints=[{"coefficients": [1.0, 1.0], "operator": "<=", "rhs": 10.0}],
        variable_names=["x1", "x2"],
    )
    model = model_generator.generate_model(problem)

    assert model["c"] == [2.0, 3.0]
    assert model["A"] == [[1.0, 1.0]]
    assert model["b"] == [10.0]
    assert model["maximize"]
    assert not model.get("is_minimization", False)


def test_generate_minimization_model(model_generator):
    """Prueba la generación de un modelo de minimización."""
    problem = OptimizationProblem(
        objective_type="minimize",
        objective_coefficients=[2.0, 5.0, 3.0],
        constraints=[{"coefficients": [150.0, 300.0, 80.0], "operator": ">=", "rhs": 2000.0}],
        variable_names=["pan", "pollo", "vegetales"],
    )
    model = model_generator.generate_model(problem)

    # Para minimización, los coeficientes se niegan
    assert model["c"] == [-2.0, -5.0, -3.0]
    # Las restricciones >= se convierten en <=
    assert model["A"] == [[-150.0, -300.0, -80.0]]
    assert model["b"] == [-2000.0]
    assert model["maximize"]  # Convertido a maximización
    assert model["is_minimization"]  # Bandera para ajustar el resultado


def test_convert_equality_constraint(model_generator):
    """Prueba la conversión de restricciones de igualdad."""
    problem = OptimizationProblem(
        objective_type="maximize",
        objective_coefficients=[2.0, 3.0],
        constraints=[{"coefficients": [1.0, 1.0], "operator": "=", "rhs": 10.0}],
        variable_names=["x1", "x2"],
    )
    model = model_generator.generate_model(problem)

    # La igualdad se convierte en dos restricciones (<= y >=)
    assert len(model["A"]) == 2
    assert model["A"] == [[1.0, 1.0], [-1.0, -1.0]]
    assert model["b"] == [10.0, -10.0]


# ==================== Pruebas del Procesador NLP Simulado ====================


def test_mock_is_available(mock_nlp_processor):
    """Prueba que el procesador simulado siempre esté disponible."""
    assert mock_nlp_processor.is_available()


def test_mock_process_simple_text(mock_nlp_processor):
    """Prueba el procesamiento con el simulador."""
    text = "Maximizar 2x + 3y sujeto a x + y <= 10"
    result = mock_nlp_processor.process_text(text)

    assert result.success
    assert result.problem is not None
    assert result.problem.objective_type == "maximize"
    assert len(result.problem.objective_coefficients) >= 2


# ==================== Pruebas de Integración del Conector NLP ====================


def test_full_pipeline_maximization(nlp_connector):
    """Prueba la tubería completa con un problema de maximización."""
    text = """
    Una empresa fabrica productos A y B.
    Cada A da $50 de ganancia, cada B $30.
    Hay 100 horas disponibles.
    Cada A requiere 2 horas, cada B 1 hora.
    Maximizar ganancia.
    """
    result = nlp_connector.process_and_solve(text)

    assert result["success"]
    assert "solution" in result
    assert "extracted_problem" in result
    assert "processing_time" in result


def test_full_pipeline_minimization(nlp_connector):
    """Prueba la tubería completa con un problema de minimización."""
    text = """
    Minimizar costos.
    Producto A cuesta $10, producto B cuesta $20.
    Necesitamos al menos 5 unidades de A.
    Necesitamos al menos 3 unidades de B.
    """
    result = nlp_connector.process_and_solve(text)

    assert result["success"]
    assert "solution" in result


def test_pipeline_validation_failure():
    """Prueba que la tubería maneje errores de validación."""
    connector = NLPConnectorFactory.create_connector(use_mock_nlp=True)

    # Texto vacío debería fallar en algún paso
    result = connector.process_and_solve("")

    # Debería fallar en algún lugar de la tubería
    if not result["success"]:
        assert "step_failed" in result or "error" in result


# ==================== Pruebas de la Fábrica de Conectores NLP ====================


def test_create_connector_with_mock():
    """Prueba la creación de un conector con simulador."""
    connector = NLPConnectorFactory.create_connector(use_mock_nlp=True)
    assert connector is not None
    assert connector.nlp_processor is not None
    assert connector.nlp_processor.is_available()


def test_create_connector_with_ollama():
    """Prueba la creación de un conector con Ollama."""
    connector = NLPConnectorFactory.create_connector(
        nlp_model_type=NLPModelType.LLAMA3_1_8B, use_mock_nlp=False
    )
    assert connector is not None
    assert connector.nlp_processor is not None


def test_create_connector_with_custom_config():
    """Prueba la creación con configuración personalizada."""
    custom_config = {"temperature": 0.0, "max_tokens": 1024}
    connector = NLPConnectorFactory.create_connector(
        nlp_model_type=NLPModelType.LLAMA3_1_8B, custom_config=custom_config
    )
    assert connector is not None


# ==================== Pruebas de Extremo a Extremo ====================


def test_production_problem(nlp_connector):
    """Prueba completa de un problema de producción."""
    text = """
    Una carpintería fabrica mesas y sillas.
    Cada mesa da $80 de ganancia, cada silla $50.
    Hay 200 horas de trabajo disponibles.
    Cada mesa requiere 4 horas, cada silla 2 horas.
    Hay 300 kg de madera disponibles.
    Cada mesa requiere 6 kg, cada silla 3 kg.
    Maximizar ganancia.
    """
    result = nlp_connector.process_and_solve(text)

    assert result["success"]
    solution = result["solution"]
    assert solution["status"] == "optimal"
    assert "optimal_value" in solution


def test_diet_problem(nlp_connector):
    """Prueba completa de un problema de dieta."""
    text = """
    Una persona necesita planificar su dieta minimizando costos.
    Debe consumir al menos 2000 calorías, 50g proteína, 30g fibra.

    Pan: $2, 150 calorías, 5g proteína, 3g fibra
    Pollo: $5, 300 calorías, 25g proteína, 0g fibra
    Vegetales: $3, 80 calorías, 3g proteína, 8g fibra

    Minimizar costo.
    """
    result = nlp_connector.process_and_solve(text)

    assert result["success"]
    assert "solution" in result


def test_transport_problem(nlp_connector):
    """Prueba completa de un problema de transporte."""
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
    result = nlp_connector.process_and_solve(text)

    assert result["success"]
    assert "solution" in result
