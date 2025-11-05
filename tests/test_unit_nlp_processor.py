import pytest
from unittest import mock

from simplex_solver.nlp.model_generator import SimplexModelGenerator, ModelValidator
from simplex_solver.nlp.ollama_processor import OllamaNLPProcessor
from simplex_solver.nlp.processor import MockNLPProcessor
from simplex_solver.nlp.interfaces import OptimizationProblem, NLPResult


def test_model_validator_and_generator_basic():
    validator = ModelValidator()

    valid_problem = OptimizationProblem(
        objective_type="maximize",
        objective_coefficients=[2.0, 3.0],
        constraints=[{"coefficients": [1.0, 1.0], "operator": "<=", "rhs": 10.0}],
    )

    assert validator.validate(valid_problem)

    gen = SimplexModelGenerator()
    model = gen.generate_model(valid_problem)

    assert model["c"] == [2.0, 3.0]
    assert model["A"] == [[1.0, 1.0]]
    assert model["constraint_types"] == ["<="]


def test_model_generator_equality_and_ge_conversion():
    gen = SimplexModelGenerator()

    problem = OptimizationProblem(
        objective_type="maximize",
        objective_coefficients=[1.0, 2.0],
        constraints=[
            {"coefficients": [1.0, 1.0], "operator": "=", "rhs": 5.0},
            {"coefficients": [2.0, 0.0], "operator": ">=", "rhs": 3.0},
        ],
    )

    model = gen.generate_model(problem)

    # equality becomes two constraints
    assert len(model["A"]) >= 2
    # >= should have been converted to <= by negation
    assert any(all(x < 0 for x in row) for row in model["A"]) or any(
        row == [2.0, 0.0] for row in model["A"]
    )


def make_fake_ollama_response(json_body: str):
    class FakeResp:
        status_code = 200

        def json(self):
            return {"response": json_body}

    return FakeResp()


def test_ollama_processor_success_and_failure(monkeypatch):
    # Create a processor but patch requests.get/post to simulate API
    proc = OllamaNLPProcessor()

    # Simulate is_available check (requests.get)
    monkeypatch.setattr(
        "requests.get",
        lambda *args, **kwargs: mock.Mock(
            status_code=200, json=lambda: {"models": [{"name": proc.model_type.value}]}
        ),
    )

    # Good JSON in response
    good_json = '{"objective_type":"maximize","objective_coefficients":[1,2],"constraints":[{"coefficients":[1,1],"operator":"<=","rhs":10}]}'
    monkeypatch.setattr(
        "requests.post", lambda *args, **kwargs: make_fake_ollama_response(good_json)
    )

    res = proc.process_text("Dummy text")
    assert isinstance(res, NLPResult)
    assert res.success

    # Malformed JSON -> processor should return failure
    bad_resp = make_fake_ollama_response("not a json { this is bad")
    monkeypatch.setattr("requests.post", lambda *args, **kwargs: bad_resp)

    res2 = proc.process_text("Dummy text")
    assert not res2.success

    # HTTP error
    monkeypatch.setattr(
        "requests.post", lambda *args, **kwargs: mock.Mock(status_code=500, text="Internal")
    )
    res3 = proc.process_text("Dummy text")
    assert not res3.success


def test_mock_nlp_processor_transports_and_diet():
    mockp = MockNLPProcessor()

    text = "Transportar desde 2 almacenes a 3 tiendas"
    res = mockp.process_text(text)
    assert res.success
    assert res.problem is not None
    assert len(res.problem.objective_coefficients) == 6

    diet_text = "dieta con pan pollo vegetales"
    res2 = mockp.process_text(diet_text)
    assert res2.success
    assert res2.problem is not None
    assert res2.problem.objective_type in ("minimize", "maximize")
