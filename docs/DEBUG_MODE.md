# Guía del modo Debug del Simplex Solver

## Propósito del modo debug
El modo debug permite visualizar, paso a paso, el funcionamiento interno del algoritmo Simplex. 
Su objetivo es facilitar la comprensión, depuración y validación del comportamiento del solver durante el proceso iterativo.

Cuando el modo debug está activado, el programa imprime en consola información detallada sobre:
- El tableau inicial.
- La selección de variables entrantes y salientes.
- La actualización del tableau después de cada pivoteo.
- La nueva solución básica tras cada iteración.
- La condición de optimalidad o finalización del algoritmo.

---

## Cómo activar el modo debug
El modo debug puede activarse pasando el parámetro `debug=True` al método `solve` del `SimplexSolver`.

# Ejecutar tests:
pytest -v

### Ejemplo:
```python
from simplex_solver.core.algorithm import SimplexSolver

solver = SimplexSolver()

c = [3, 5]
A = [
    [1, 0],
    [0, 2],
    [3, 2],
]
b = [4, 12, 18]
constraint_types = ["<=", "<=", "<="]

solver.solve(c, A, b, constraint_types, maximize=True, debug=True)
