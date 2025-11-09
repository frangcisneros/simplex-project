# Tarjeta CRC: SimplexSolverAdapter

### Clase: SimplexSolverAdapter

**Responsabilidades:**

- Adaptar el SimplexSolver existente al nuevo sistema NLP
- Traducir entre formato del modelo generator (Dict) y SimplexSolver (c, A, b)
- Validar que el modelo tenga las claves necesarias (c, A, b, maximize)
- Invocar el SimplexSolver con los parámetros correctos
- Enriquecer resultados con información adicional del modelo
- Mapear solución de variables genéricas (x1, x2, x3) a nombres personalizados
- Generar solución nombrada (named_solution) cuando hay variable_names
- Manejar errores y convertirlos a formato estándar del sistema
- Proporcionar logging de debug del modelo generado

**Colaboradores:**

- `IOptimizationSolver` - Interfaz base que implementa
- `SimplexSolver` - Algoritmo simplex original
- `LoggingSystem` - Registro de operaciones

**Ubicación:** `simplex_solver/nlp/connector.py`

**Tipo:** Adaptador (Adapter Pattern)
