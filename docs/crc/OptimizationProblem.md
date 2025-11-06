# Tarjeta CRC: OptimizationProblem

### Clase: OptimizationProblem

**Responsabilidades:**

- Representar un problema de optimización de forma estructurada
- Almacenar tipo de objetivo (maximize/minimize)
- Mantener coeficientes de la función objetivo
- Almacenar lista de restricciones con sus propiedades
- Cada restricción contiene: coefficients, operator, rhs
- Mantener nombres personalizados de variables (opcional)
- Servir como formato estándar entre procesadores NLP y generadores de modelos
- Proporcionar estructura de datos inmutable para el problema
- Facilitar validación y transformación del problema

**Colaboradores:**

- `INLPProcessor` - Genera instancias de OptimizationProblem
- `IModelGenerator` - Consume OptimizationProblem para generar modelos
- `IModelValidator` - Valida instancias de OptimizationProblem
- `NLPResult` - Contiene OptimizationProblem como resultado

**Ubicación:** `simplex_solver/nlp/interfaces.py`

**Tipo:** Clase de datos (Data Class)
