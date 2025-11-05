from simplex_solver.nlp.connector import NLPOptimizationConnector
from simplex_solver.nlp.model_generator import SimplexModelGenerator
from simplex_solver.nlp.connector import SimplexSolverAdapter
from simplex_solver.nlp.model_generator import ModelValidator
from simplex_solver.nlp.interfaces import OptimizationProblem, NLPResult


def test_nlp_pipeline_with_mocked_processor():
    # Create a fake processor that returns a known problem (carpinteria)
    class FakeProcessor:
        def is_available(self):
            return True

        def process_text(self, text):
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

    processor = FakeProcessor()
    generator = SimplexModelGenerator()
    solver = SimplexSolverAdapter()
    validator = ModelValidator()

    connector = NLPOptimizationConnector(
        nlp_processor=processor, model_generator=generator, solver=solver, validator=validator
    )

    result = connector.process_and_solve("Una carpintería ...")

    assert result["success"] is True
    assert "solution" in result
    assert result["solution"]["status"] == "optimal"
    assert "optimal_value" in result["solution"] or "optimal_value" in result
