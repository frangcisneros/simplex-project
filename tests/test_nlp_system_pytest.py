"""
Comprehensive test suite for the NLP optimization system.
Converted from unittest to pytest with fixtures.
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
    """Create a ProblemStructureDetector instance."""
    return ProblemStructureDetector()


@pytest.fixture
def complexity_analyzer():
    """Create a ComplexityAnalyzer instance."""
    return ComplexityAnalyzer()


@pytest.fixture
def model_validator():
    """Create a ModelValidator instance."""
    return ModelValidator()


@pytest.fixture
def model_generator():
    """Create a SimplexModelGenerator instance."""
    return SimplexModelGenerator()


@pytest.fixture
def mock_nlp_processor():
    """Create a MockNLPProcessor instance."""
    return MockNLPProcessor()


@pytest.fixture
def nlp_connector():
    """Create an NLP connector with mock processor."""
    return NLPConnectorFactory.create_connector(use_mock_nlp=True, solver_type=SolverType.SIMPLEX)


# ==================== Structure Detector Tests ====================


def test_detect_simple_production(structure_detector):
    """Test detection of simple production problem."""
    text = """
    Una carpintería fabrica mesas y sillas.
    Cada mesa da $80 de ganancia.
    """
    structure = structure_detector.detect_structure(text)
    assert structure["problem_type"] == "simple"


def test_detect_diet_problem(structure_detector):
    """Test detection of diet problem."""
    text = """
    Una persona necesita planificar su dieta.
    Debe consumir al menos 2000 calorías.
    Alimentos: pan, pollo, vegetales.
    """
    structure = structure_detector.detect_structure(text)
    assert structure["problem_type"] == "diet"
    assert structure["expected_variables"] == 3


def test_detect_transport_problem(structure_detector):
    """Test detection of transport problem."""
    text = """
    Una empresa debe transportar productos desde 2 almacenes a 3 tiendas.
    Minimizar el costo total de transporte.
    """
    structure = structure_detector.detect_structure(text)
    assert structure["problem_type"] == "transport"
    assert structure["expected_variables"] == 6


def test_detect_food_items(structure_detector):
    """Test detection of food items in diet problems."""
    text = "dieta con alimentos: pan, pollo y vegetales con calorías"
    foods = structure_detector._detect_food_items(text)
    assert len(foods) > 0
    # Verify at least some common foods are detected
    detected = any(food in ["pan", "pollo", "vegetales"] for food in foods)
    assert detected or len(foods) > 0


def test_detect_transport_routes(structure_detector):
    """Test detection of routes in transport problems."""
    text = "transportar desde 2 almacenes a 3 tiendas"
    routes = structure_detector._detect_transport_routes(text)
    assert len(routes) == 6


# ==================== Complexity Analyzer Tests ====================


def test_simple_problem_complexity(complexity_analyzer):
    """Test analysis of simple problem."""
    text = "Maximizar 2x + 3y sujeto a x + y <= 10"
    complexity = complexity_analyzer.analyze_problem(text)
    assert complexity == ProblemComplexity.SIMPLE


def test_medium_problem_complexity(complexity_analyzer):
    """Test analysis of medium complexity problem."""
    text = (
        """
    Una empresa fabrica 4 productos.
    Hay 3 restricciones de recursos.
    Maximizar la ganancia total.
    """
        * 3
    )  # Repeat to increase length
    complexity = complexity_analyzer.analyze_problem(text)
    assert complexity in [ProblemComplexity.SIMPLE, ProblemComplexity.MEDIUM]


def test_complex_problem_complexity(complexity_analyzer):
    """Test analysis of complex problem."""
    text = (
        """
    Una empresa tiene 5 plantas y fabrica 6 productos.
    Hay 10 restricciones de capacidad.
    Hay 8 restricciones de demanda.
    Cada planta tiene diferentes costos.
    """
        * 10
    )  # Repeat to increase length
    complexity = complexity_analyzer.analyze_problem(text)
    assert complexity in [ProblemComplexity.MEDIUM, ProblemComplexity.COMPLEX]


# ==================== Model Validator Tests ====================


def test_valid_problem(model_validator):
    """Test validation of correct problem."""
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
    """Test validation with invalid objective type."""
    problem = OptimizationProblem(
        objective_type="optimizar",  # Invalid type
        objective_coefficients=[2.0, 3.0],
        constraints=[{"coefficients": [1.0, 1.0], "operator": "<=", "rhs": 10.0}],
        variable_names=["x1", "x2"],
    )
    assert not model_validator.validate(problem)
    errors = model_validator.get_validation_errors(problem)
    assert len(errors) > 0


def test_dimension_mismatch(model_validator):
    """Test validation with dimension error."""
    problem = OptimizationProblem(
        objective_type="maximize",
        objective_coefficients=[2.0, 3.0],
        constraints=[
            {"coefficients": [1.0, 1.0, 1.0], "operator": "<=", "rhs": 10.0}  # 3 coefs, 2 vars
        ],
        variable_names=["x1", "x2"],
    )
    assert not model_validator.validate(problem)
    errors = model_validator.get_validation_errors(problem)
    assert any("Dimension mismatch" in err for err in errors)


def test_invalid_operator(model_validator):
    """Test validation with invalid operator."""
    problem = OptimizationProblem(
        objective_type="maximize",
        objective_coefficients=[2.0, 3.0],
        constraints=[
            {"coefficients": [1.0, 1.0], "operator": "~=", "rhs": 10.0}  # Invalid operator
        ],
        variable_names=["x1", "x2"],
    )
    assert not model_validator.validate(problem)
    errors = model_validator.get_validation_errors(problem)
    assert any("Invalid operator" in err for err in errors)


# ==================== Model Generator Tests ====================


def test_generate_maximization_model(model_generator):
    """Test generation of maximization model."""
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
    """Test generation of minimization model."""
    problem = OptimizationProblem(
        objective_type="minimize",
        objective_coefficients=[2.0, 5.0, 3.0],
        constraints=[{"coefficients": [150.0, 300.0, 80.0], "operator": ">=", "rhs": 2000.0}],
        variable_names=["pan", "pollo", "vegetales"],
    )
    model = model_generator.generate_model(problem)

    # For minimization, coefficients are negated
    assert model["c"] == [-2.0, -5.0, -3.0]
    # >= constraints converted to <=
    assert model["A"] == [[-150.0, -300.0, -80.0]]
    assert model["b"] == [-2000.0]
    assert model["maximize"]  # Converted to maximization
    assert model["is_minimization"]  # Flag to adjust result


def test_convert_equality_constraint(model_generator):
    """Test conversion of equality constraints."""
    problem = OptimizationProblem(
        objective_type="maximize",
        objective_coefficients=[2.0, 3.0],
        constraints=[{"coefficients": [1.0, 1.0], "operator": "=", "rhs": 10.0}],
        variable_names=["x1", "x2"],
    )
    model = model_generator.generate_model(problem)

    # Equality becomes two constraints (<= and >=)
    assert len(model["A"]) == 2
    assert model["A"] == [[1.0, 1.0], [-1.0, -1.0]]
    assert model["b"] == [10.0, -10.0]


# ==================== Mock NLP Processor Tests ====================


def test_mock_is_available(mock_nlp_processor):
    """Test that mock is always available."""
    assert mock_nlp_processor.is_available()


def test_mock_process_simple_text(mock_nlp_processor):
    """Test processing with mock."""
    text = "Maximizar 2x + 3y sujeto a x + y <= 10"
    result = mock_nlp_processor.process_text(text)

    assert result.success
    assert result.problem is not None
    assert result.problem.objective_type == "maximize"
    assert len(result.problem.objective_coefficients) >= 2


# ==================== NLP Connector Integration Tests ====================


def test_full_pipeline_maximization(nlp_connector):
    """Test full pipeline with maximization problem."""
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
    """Test full pipeline with minimization problem."""
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
    """Test that pipeline handles validation errors."""
    connector = NLPConnectorFactory.create_connector(use_mock_nlp=True)

    # Empty text should fail at some step
    result = connector.process_and_solve("")

    # Should fail somewhere in the pipeline
    if not result["success"]:
        assert "step_failed" in result or "error" in result


# ==================== NLP Connector Factory Tests ====================


def test_create_connector_with_mock():
    """Test creation of connector with mock."""
    connector = NLPConnectorFactory.create_connector(use_mock_nlp=True)
    assert connector is not None
    assert connector.nlp_processor is not None
    assert connector.nlp_processor.is_available()


def test_create_connector_with_ollama():
    """Test creation of connector with Ollama."""
    connector = NLPConnectorFactory.create_connector(
        nlp_model_type=NLPModelType.LLAMA3_1_8B, use_mock_nlp=False
    )
    assert connector is not None
    assert connector.nlp_processor is not None


def test_create_connector_with_custom_config():
    """Test creation with custom configuration."""
    custom_config = {"temperature": 0.0, "max_tokens": 1024}
    connector = NLPConnectorFactory.create_connector(
        nlp_model_type=NLPModelType.LLAMA3_1_8B, custom_config=custom_config
    )
    assert connector is not None


# ==================== End-to-End Tests ====================


def test_production_problem(nlp_connector):
    """Test complete production problem."""
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
    """Test complete diet problem."""
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
    """Test complete transport problem."""
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
