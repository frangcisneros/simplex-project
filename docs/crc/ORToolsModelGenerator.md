# Tarjeta CRC: ORToolsModelGenerator

### Clase: ORToolsModelGenerator

**Responsabilidades:**

- Generar modelos para Google OR-Tools
- Verificar disponibilidad de la librería OR-Tools
- Crear solver GLOP para programación lineal
- Definir variables NumVar no negativas con nombres personalizados
- Configurar función objetivo con coeficientes
- Establecer sentido de optimización (SetMaximization/SetMinimization)
- Crear restricciones con límites superior/inferior según el operador
- Configurar bounds de restricciones (<=: SetUB, >=: SetLB, =: SetBounds)
- Retornar estructura con solver, variables y restricciones
- Manejar errores si no se puede crear el solver

**Colaboradores:**

- `IModelGenerator` - Interfaz base que implementa
- `OptimizationProblem` - Problema de entrada estructurado
- `ortools.linear_solver` - Librería de optimización de Google
- `LoggingSystem` - Registro de operaciones

**Ubicación:** `simplex_solver/nlp/model_generator.py`

**Tipo:** Generador de modelos (Model Generator)
