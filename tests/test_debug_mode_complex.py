import io
import sys
from simplex_solver.core.algorithm import SimplexSolver

def test_debug_complex_case_minimization():
    solver = SimplexSolver()

    # Problema de minimización (más complejo)
    # Min Z = 2x1 + 3x2 + x3
    # Sujeto a:
    #   x1 + x2 + x3 >= 4
    #   2x1 + x2 + 3x3 >= 6
    #   x1, x2, x3 >= 0
    c = [2, 3, 1]
    A = [
        [1, 1, 1],
        [2, 1, 3],
    ]
    b = [4, 6]
    constraint_types = [">=", ">="]

    # Capturar salida del modo debug
    captured_output = io.StringIO()
    sys.stdout = captured_output

    result = solver.solve(c, A, b, constraint_types, maximize=False)

    # Restaurar stdout
    sys.stdout = sys.__stdout__
    output = captured_output.getvalue()

    # Verificaciones
    assert result["status"] in ["optimal", "feasible"], "El solver no devolvió una solución válida"
    assert all(var.startswith("x") for var in result["solution"].keys()), "Las variables deben tener formato x1, x2..."
    
    # Verificamos que el modo debug haya mostrado los pasos importantes
    assert "Tableau inicial" in output or "tableau inicial" in output
    assert "Variable entrante" in output
    assert "Variable saliente" in output
    assert "Actualización del tableau" in output
    assert "Solución básica actual" in output
    assert "Condición de optimalidad" in output or "Valor óptimo" in output

    # Si el modo debug está correctamente implementado, debe mostrar los pasos intermedios
    assert len(output.strip()) > 0, "No se imprimió nada en modo debug"
