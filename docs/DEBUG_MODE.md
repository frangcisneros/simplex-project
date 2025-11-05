# Guía del Modo Verbose del Simplex Solver

## Propósito del modo verbose

El modo verbose permite visualizar, paso a paso, el funcionamiento interno del algoritmo Simplex a través del sistema de logging integrado. Su objetivo es facilitar la comprensión, depuración y validación del comportamiento del solver durante el proceso iterativo.

El solver soporta diferentes niveles de verbosidad:

- **verbose_level=0** (por defecto): Modo silencioso. Solo registra el resultado final.
- **verbose_level=1**: Modo básico. Registra información general de las fases y condición de optimalidad.
- **verbose_level=2**: Modo detallado. Registra cada iteración con las variables entrantes/salientes y las soluciones básicas intermedias.

Cuando `verbose_level > 0`, el programa registra en el sistema de logging información detallada sobre:

- Las fases del algoritmo (Fase 1, Fase 2).
- La condición de optimalidad alcanzada.
- Las variables entrantes y salientes (solo en nivel 2).
- La solución básica después de cada pivoteo (solo en nivel 2).
- El valor de la función objetivo en cada iteración (solo en nivel 2).

---

## Cómo activar el modo verbose

El modo verbose se controla mediante el parámetro `verbose_level` en el método `solve` del `SimplexSolver`.

### Ejemplo básico (verbose_level=0, modo silencioso):

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

# Modo silencioso (por defecto)
result = solver.solve(c, A, b, constraint_types, maximize=True)
print(f"Solución óptima: {result['optimal_value']}")
```

### Ejemplo con verbose_level=1 (información básica):

```python
# Muestra información de las fases y condición de optimalidad
result = solver.solve(c, A, b, constraint_types, maximize=True, verbose_level=1)
```

### Ejemplo con verbose_level=2 (detalle completo):

```python
# Muestra cada iteración con variables entrantes/salientes y soluciones intermedias
result = solver.solve(c, A, b, constraint_types, maximize=True, verbose_level=2)
```

---

## Integración con el sistema de logging

La información del modo verbose se integra con el `logging_system.py` existente, lo que permite:

- **Filtrar logs por nivel**: DEBUG, INFO, WARNING, ERROR
- **Persistencia**: Los logs se guardan en la base de datos de logging
- **Consulta histórica**: Revisar logs de ejecuciones anteriores
- **Formato consistente**: Mensajes con timestamp, nivel y contexto

Los mensajes del modo verbose se registran principalmente con nivel `INFO` (cuando verbose_level > 0) o `DEBUG` (cuando verbose_level = 0).

---

## Niveles de Verbosidad Detallados

### Nivel 0 (Silencioso)

```
[INFO] Starting solver - Variables: 2, Constraints: 3, Type: MAX
[INFO] Optimal solution found - Value: 30.000000, Total iterations: 2
```

### Nivel 1 (Básico)

```
[INFO] Starting solver - Variables: 2, Constraints: 3, Type: MAX
[INFO] Solving in single phase (no artificial variables)
[INFO] Optimality condition reached: no coefficients in objective row improve the function
[INFO] Optimal solution found - Value: 30.000000, Total iterations: 2
```

### Nivel 2 (Detallado)

```
[INFO] Starting solver - Variables: 2, Constraints: 3, Type: MAX
[INFO] Solving in single phase (no artificial variables)
[INFO] Entering variable: column 2
[INFO] Leaving variable: row 2, pivot: 2.0000
[INFO] Iteration 1 - Basic solution: x1=0.0000, x2=6.0000, Current value: 30.0000
[INFO] Optimality condition reached: no coefficients in objective row improve the function
[INFO] Final solution of phase: x1=0.0000, x2=6.0000, Optimal value: 30.0000
[INFO] Optimal solution found - Value: 30.000000, Total iterations: 1
```

---

## Uso en Testing

Los tests pueden verificar el comportamiento del modo verbose:

```python
def test_solver_verbose_mode():
    solver = SimplexSolver()
    c = [3, 5]
    A = [[1, 0], [0, 2], [3, 2]]
    b = [4, 12, 18]
    constraint_types = ["<=", "<=", "<="]

    # Ejecutar con verbose_level=2
    result = solver.solve(c, A, b, constraint_types, maximize=True, verbose_level=2)

    assert result["status"] == "optimal"
    # Los logs se pueden verificar mediante el sistema de logging
```

---

## Notas Adicionales

- El modo verbose **no afecta el rendimiento** del algoritmo, solo agrega registros de logging.
- Para problemas grandes, usar `verbose_level=0` para evitar generar demasiados logs.
- Los logs detallados son útiles para depuración y aprendizaje del algoritmo Simplex.
- La información se registra tanto en consola como en la base de datos de logging (según la configuración del `logging_system`).
