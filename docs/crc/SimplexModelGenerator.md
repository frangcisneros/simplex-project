# Tarjeta CRC: SimplexModelGenerator

### Clase: SimplexModelGenerator

**Responsabilidades:**

- Convertir problemas de optimización a formato de matrices para Simplex
- Extraer coeficientes de la función objetivo
- Construir matriz A con coeficientes de restricciones
- Convertir todas las restricciones a forma estándar (<=)
- Manejar restricciones >= (multiplicando por -1)
- Dividir restricciones de igualdad en dos restricciones (≤ y ≥)
- Convertir problemas de minimización a maximización (negando coeficientes)
- Validar dimensiones del modelo (variables vs restricciones)
- Generar estructura compatible con SimplexSolver (c, A, b, constraint_types)
- Preservar información de nombres de variables

**Colaboradores:**

- `IModelGenerator` - Interfaz base que implementa
- `OptimizationProblem` - Problema de entrada estructurado
- `LoggingSystem` - Registro de operaciones y errores

**Ubicación:** `simplex_solver/nlp/model_generator.py`

**Tipo:** Generador de modelos (Model Generator)
