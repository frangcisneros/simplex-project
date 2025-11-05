import io
import sys
from simplex_solver.core.algorithm import SimplexSolver

def test_debug_prints_solution_and_optimality(capsys):
    solver = SimplexSolver()
    c = [3, 5]
    A = [
        [1, 0],
        [0, 2],
        [3, 2],
    ]
    b = [4, 12, 18]
    constraint_types = ["<=", "<=", "<="]

    # Ejecutar y capturar salida de consola
    result = solver.solve(c, A, b, constraint_types, maximize=True)

    # Validar resultado y que la salida contenga las líneas esperadas
    assert result["status"] == "optimal"
    captured = capsys.readouterr().out

    assert "Solución básica actual" in captured or "Solución final" in captured
    assert "Condición de optimalidad alcanzada" in captured
    # comprobación de variables
    assert "x1" in captured and "x2" in captured
