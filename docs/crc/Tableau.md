# Tableau

**Clase:** Tableau (Tabla Simplex)

**Responsabilidades:**
- Construir tableau inicial con **variables de holgura, exceso y artificiales**
- Configurar **Fase 1**: Objetivo para minimizar suma de artificiales (w = Σ ai)
- Configurar **Fase 2**: Preparar tableau con función objetivo original
- Gestionar matriz de coeficientes, solución básica y función objetivo
- Ejecutar operaciones de pivoteo (transformaciones elementales)
- Identificar variable de entrada (regla de Bland)
- Identificar variable de salida (prueba de razón mínima)
- Calcular solución actual y valor de la función objetivo
- Validar factibilidad (todas las variables básicas >= 0)

**Atributos Principales:**
- `matrix`: Matriz del tableau (m  n) con restricciones y función objetivo
- `basis`: Índices de variables básicas en cada fila
- `num_constraints`: Número de restricciones (m)
- `num_original_vars`: Número de variables originales
- `num_slack_vars`: Número de variables de holgura ()
- `num_surplus_vars`: Número de variables de exceso ()
- `num_artificial_vars`: Número de variables artificiales (, =)
- `phase1_complete`: Flag indicando si Fase 1 ha terminado

**Métodos Principales:**

**Construcción del Tableau:**
- `build_initial_tableau()`: Construye tableau inicial con todas las variables auxiliares
- `_setup_phase1_objective()`: Configura objetivo de Fase 1 (minimizar Σ ai)
- `_setup_original_objective()`: Almacena coeficientes de función objetivo original

**Método de Dos Fases:**
- `setup_phase2()`: Transición de Fase 1 a Fase 2
  - Elimina columnas de variables artificiales del tableau
  - Reconstruye fila de función objetivo usando coeficientes originales c
  - Actualiza variables básicas si necesario
  - Marca `phase1_complete = True`

**Operaciones del Simplex:**
- `pivot()`: Ejecuta operación de pivoteo (transformación elemental)
- `get_entering_variable()`: Identifica variable de entrada (regla de Bland)
- `get_leaving_variable()`: Identifica variable de salida (prueba de razón)
- `get_solution()`: Calcula solución actual (variables básicas)
- `get_objective_value()`: Retorna valor actual de función objetivo

**Validaciones:**
- `is_optimal()`: Verifica si se alcanzó óptimo (todos costos reducidos >= 0)
- `is_unbounded()`: Detecta problema no acotado
- `is_feasible()`: Verifica factibilidad (solución básica >= 0)

**Colaboradores:**
- **SimplexSolver**: Coordina el uso del Tableau en Fase 1 y Fase 2
- **AlgorithmConfig**: Proporciona tolerancia numérica para comparaciones
- **numpy**: Operaciones matriciales eficientes

**Notas:**
- **Método de Dos Fases** implementado para manejar restricciones >=, ==, <=
- Variables artificiales solo existen en Fase 1; se eliminan en `setup_phase2()`
- Tolerancia numérica (1e-10) para todas las comparaciones
- Ver documentación técnica detallada en: `docs/METODO_DOS_FASES.md`
- Logging con verbosity 2 muestra detalles de construcción y transición de fases
