from simplex_solver.nlp.connector import NLPOptimizationConnector
from simplex_solver.nlp.model_generator import SimplexModelGenerator
from simplex_solver.nlp.connector import SimplexSolverAdapter
from simplex_solver.nlp.model_generator import ModelValidator
from simplex_solver.nlp.interfaces import OptimizationProblem, NLPResult


def test_nlp_pipeline_with_mocked_processor():
    """
    Verifica el flujo completo de la canalización NLP utilizando un procesador simulado.

    Este test utiliza un procesador falso que devuelve un problema conocido (carpintería)
    para validar la integración entre el procesador NLP, el generador de modelos,
    el solver y el validador.
    """

    # Crear un procesador falso que simula el procesamiento de texto
    class FakeProcessor:
        def is_available(self):
            """
            Simula la disponibilidad del procesador NLP.

            Retorna:
                True, indicando que el procesador está disponible.
            """
            return True

        def process_text(self, text):
            """
            Simula el procesamiento de texto y devuelve un problema de optimización.

            Parámetros:
                text: Texto de entrada a procesar.

            Retorna:
                Un objeto NLPResult con un problema de optimización simulado.
            """
            problem = OptimizationProblem(
                objective_type="maximize",
                objective_coefficients=[80.0, 50.0],
                constraints=[
                    {"coefficients": [4.0, 2.0], "operator": "<=", "rhs": 200.0},
                    {"coefficients": [1.0, 1.0], "operator": "<=", "rhs": 60.0},
                ],
                variable_names=["mesas", "sillas"],
            )
            return NLPResult(success=True, problem=problem, confidence_score=0.9)

    # Instanciar los componentes necesarios para la canalización
    processor = FakeProcessor()
    generator = SimplexModelGenerator()
    solver = SimplexSolverAdapter()
    validator = ModelValidator()

    # Crear el conector NLP con los componentes simulados
    connector = NLPOptimizationConnector(
        nlp_processor=processor, model_generator=generator, solver=solver, validator=validator
    )

    # Procesar y resolver el problema simulado
    result = connector.process_and_solve("Una carpintería ...")

    # Verificar que el resultado sea exitoso
    assert result["success"] is True, "El procesamiento debe ser exitoso"
    assert "solution" in result, "El resultado debe contener una solución"
    assert result["solution"]["status"] == "optimal", "El estado de la solución debe ser óptimo"
    assert (
        "optimal_value" in result["solution"] or "optimal_value" in result
    ), "Debe incluir el valor óptimo"
