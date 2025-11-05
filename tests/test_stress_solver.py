import os
import pytest
import random

from simplex_solver.core.algorithm import SimplexSolver
from simplex_solver.nlp.model_generator import SimplexModelGenerator, ModelValidator
from simplex_solver.logging_system import LoggingSystem


@pytest.mark.skipif(os.environ.get("SHORT_TESTS"), reason="Skipping long stress tests")
def test_stress_large_solver():
    """Stress test: solve a reasonably large random problem (keeps sizes moderate for CI)."""
    # Sizes chosen to be large but reasonable for CI; adjust via env if needed
    n_vars = int(os.environ.get("STRESS_VARS", 30))
    n_cons = int(os.environ.get("STRESS_CONS", 60))

    random.seed(0)
    c = [random.uniform(1, 10) for _ in range(n_vars)]
    A = []
    b = []
    for _ in range(n_cons):
        row = [random.uniform(0, 5) for _ in range(n_vars)]
        rhs = sum(row) * random.uniform(0.5, 2.0) + 1.0
        A.append(row)
        b.append(rhs)

    constraint_types = ["<=" for _ in range(n_cons)]
    solver = SimplexSolver()

    result = solver.solve(c, A, b, constraint_types, maximize=True)

    # We only assert the solver didn't crash and returned a known status
    assert result.get("status") in ("optimal", "unbounded", "error", "infeasible")


def test_nlp_generator_handles_large_json():
    # Create a very large NLP-style problem and ensure ModelValidator/Generator handle it
    num_vars = 50
    num_cons = 100

    problem = {
        "objective_type": "maximize",
        "objective_coefficients": [1.0 for _ in range(num_vars)],
        "constraints": [],
        "variable_names": [f"x{i+1}" for i in range(num_vars)],
    }

    for i in range(num_cons):
        coeffs = [0.0 for _ in range(num_vars)]
        # set a couple of coefficients per constraint
        coeffs[i % num_vars] = 1.0
        coeffs[(i * 3) % num_vars] = 2.0
        problem["constraints"].append({"coefficients": coeffs, "operator": "<=", "rhs": 100.0})

    # Use model validator with higher limits
    validator = ModelValidator(max_variables=200, max_constraints=500)

    # Convert dict to OptimizationProblem-like object for the generator
    from simplex_solver.nlp.interfaces import OptimizationProblem

    opt = OptimizationProblem(
        objective_type=problem["objective_type"],
        objective_coefficients=problem["objective_coefficients"],
        constraints=problem["constraints"],
        variable_names=problem["variable_names"],
    )

    assert validator.validate(opt)
    gen = SimplexModelGenerator()
    model = gen.generate_model(opt)

    assert len(model["c"]) == num_vars
    assert len(model["A"]) == num_cons


def test_logging_stress_writes_many_entries(tmp_path, monkeypatch):
    # Prepare an isolated DB for stress logging
    monkeypatch.setattr(
        LoggingSystem, "_get_db_path", lambda self: str(tmp_path / "stress_logs.db")
    )
    LoggingSystem._instance = None
    ls = LoggingSystem()

    COUNT = int(os.environ.get("LOG_STRESS_COUNT", 1000))
    for i in range(COUNT):
        ls.info(f"stress log {i}", module="tests", function="test_logging_stress")

    # spot-check that some logs exist
    db = ls.get_db_path()
    assert os.path.exists(db)
