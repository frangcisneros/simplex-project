# Tarjeta CRC: PuLPModelGenerator

### Clase: PuLPModelGenerator

**Responsabilidades:**

- Generar modelos de optimización usando la librería PuLP
- Verificar disponibilidad de la librería PuLP
- Crear problema PuLP con sentido de optimización (maximize/minimize)
- Crear variables de decisión LpVariable con límites no negativos
- Definir función objetivo usando lpSum
- Agregar restricciones con operadores correctos (<=, >=, =)
- Construir lado izquierdo de restricciones con lpSum
- Asociar nombres personalizados a variables cuando estén disponibles
- Retornar estructura con problema PuLP y diccionario de variables

**Colaboradores:**

- `IModelGenerator` - Interfaz base que implementa
- `OptimizationProblem` - Problema de entrada estructurado
- `pulp` - Librería de modelado de optimización
- `LoggingSystem` - Registro de operaciones

**Ubicación:** `simplex_solver/nlp/model_generator.py`

**Tipo:** Generador de modelos (Model Generator)
