# CRC Card: SensitivityAnalyzer

## Información de la Clase

- **Nombre**: `SensitivityAnalyzer`
- **Módulo**: `simplex_solver.core.sensitivity`
- **Tipo**: Clase de análisis
- **Propósito**: Calcular análisis de sensibilidad sobre soluciones óptimas del método Simplex

## Responsabilidades

### Responsabilidades Principales

1. **Calcular Precios Sombra (Shadow Prices)**

   - Extraer valores duales del tableau óptimo
   - Interpretar el valor marginal de cada restricción
   - Proporcionar información sobre recursos escasos

2. **Calcular Rangos de Optimalidad**

   - Determinar rangos de coeficientes de la función objetivo
   - Identificar variaciones que no cambian la base óptima
   - Analizar sensibilidad de las variables de decisión

3. **Calcular Rangos de Factibilidad**

   - Determinar rangos de valores RHS (lado derecho)
   - Identificar variaciones de recursos que mantienen la base
   - Proporcionar límites de disponibilidad de recursos

4. **Coordinar Análisis Completo**
   - Ejecutar todos los cálculos de sensibilidad
   - Integrar resultados en una estructura coherente
   - Validar precondiciones (solución óptima requerida)

## Colaboradores

### Clases con las que Colabora

1. **SimplexSolver** (`simplex_solver.core.algorithm`)

   - **Relación**: Cliente
   - **Uso**: Recibe el tableau óptimo y variables básicas
   - **Dirección**: SimplexSolver → SensitivityAnalyzer

2. **Tableau** (`simplex_solver.utils.tableau`)

   - **Relación**: Proveedor de datos
   - **Uso**: Proporciona estructura del tableau óptimo
   - **Dirección**: SensitivityAnalyzer lee de Tableau

3. **LoggingSystem** (`simplex_solver.logging_system`)
   - **Relación**: Servicio de logging
   - **Uso**: Registra eventos y resultados del análisis
   - **Dirección**: SensitivityAnalyzer → LoggingSystem

## Atributos

| Atributo          | Tipo         | Descripción                                |
| ----------------- | ------------ | ------------------------------------------ |
| `tableau`         | `np.ndarray` | Tableau óptimo del método Simplex          |
| `basic_vars`      | `list`       | Lista de índices de variables básicas      |
| `num_vars`        | `int`        | Número de variables de decisión originales |
| `num_constraints` | `int`        | Número de restricciones del problema       |

## Métodos Públicos

### `__init__(tableau, basic_vars, num_vars, num_constraints)`

- **Propósito**: Inicializar el analizador con el estado óptimo
- **Parámetros**:
  - `tableau`: Tableau óptimo
  - `basic_vars`: Variables en la base óptima
  - `num_vars`: Número de variables originales
  - `num_constraints`: Número de restricciones
- **Retorna**: Instancia de SensitivityAnalyzer

### `calculate_shadow_prices()`

- **Propósito**: Calcular precios sombra de las restricciones
- **Retorna**: `Dict[str, float]` - Mapeo restricción → precio sombra
- **Algoritmo**:
  - Extrae fila objetivo del tableau
  - Obtiene coeficientes de variables de holgura
  - Calcula negativo de estos coeficientes

### `calculate_optimality_ranges(original_c)`

- **Propósito**: Calcular rangos de optimalidad para coeficientes de F.O.
- **Parámetros**: `original_c` - Coeficientes originales
- **Retorna**: `Dict[str, Tuple[float, float]]` - Mapeo variable → (min, max)
- **Algoritmo**:
  - Para cada variable básica: calcula ratios de costos reducidos
  - Para cada variable no básica: usa costo reducido directamente

### `calculate_feasibility_ranges(original_b)`

- **Propósito**: Calcular rangos de factibilidad para valores RHS
- **Parámetros**: `original_b` - Valores RHS originales
- **Retorna**: `Dict[str, Tuple[float, float]]` - Mapeo restricción → (min, max)
- **Algoritmo**:
  - Para cada restricción: calcula ratios de valores básicos
  - Determina límites inferior y superior

### `analyze(original_c, original_b)`

- **Propósito**: Realizar análisis completo de sensibilidad
- **Parámetros**:
  - `original_c`: Coeficientes de la función objetivo
  - `original_b`: Valores RHS
- **Retorna**: `Dict[str, Any]` - Análisis completo
- **Estructura de retorno**:
  ```python
  {
      "shadow_prices": Dict[str, float],
      "optimality_ranges": Dict[str, Tuple[float, float]],
      "feasibility_ranges": Dict[str, Tuple[float, float]]
  }
  ```

## Métodos Privados

### `_calculate_basic_var_range(var_index)`

- **Propósito**: Calcular rango para variable básica
- **Parámetros**: `var_index` - Índice de la variable
- **Retorna**: `Tuple[float, float]` - (min_delta, max_delta)

### `_calculate_nonbasic_var_range(var_index)`

- **Propósito**: Calcular rango para variable no básica
- **Parámetros**: `var_index` - Índice de la variable
- **Retorna**: `Tuple[float, float]` - (min_delta, max_delta)

### `_calculate_rhs_range(constraint_index)`

- **Propósito**: Calcular rango para un RHS específico
- **Parámetros**: `constraint_index` - Índice de la restricción
- **Retorna**: `Tuple[float, float]` - (min_delta, max_delta)

## Notas de Diseño

### Principios SOLID Aplicados

1. **Single Responsibility**: Responsable únicamente del análisis de sensibilidad
2. **Open/Closed**: Extendible para nuevos tipos de análisis sin modificar código existente
3. **Dependency Inversion**: Depende de abstracciones (np.ndarray) no de implementaciones concretas

### Patrones de Diseño

- **Strategy Pattern**: Diferentes estrategias para variables básicas vs no básicas
- **Template Method**: `analyze()` coordina los pasos del análisis

### Consideraciones Numéricas

- Usa tolerancia de `1e-10` para comparaciones de punto flotante
- Maneja infinitos para rangos no acotados
- Previene división por cero

### Casos de Uso Principales

1. **Análisis Post-Optimización**

   - Usuario resuelve problema
   - Solicita análisis de sensibilidad
   - Sistema calcula y presenta resultados

2. **Planificación de Recursos**

   - Identificar recursos escasos (precios sombra altos)
   - Determinar márgenes de cambio seguros
   - Evaluar impacto de variaciones

3. **Validación de Robustez**
   - Verificar estabilidad de la solución
   - Identificar variables sensibles
   - Evaluar riesgos de cambios paramétricos

## Ejemplo de Uso

```python
from simplex_solver.core.algorithm import SimplexSolver
from simplex_solver.core.sensitivity import SensitivityAnalyzer
import numpy as np

# Resolver problema
solver = SimplexSolver()
result = solver.solve(c, A, b, constraint_types, maximize=True)

# Realizar análisis de sensibilidad
if result["status"] == "optimal":
    analyzer = SensitivityAnalyzer(
        tableau=solver.tableau.tableau,
        basic_vars=solver.tableau.basic_vars,
        num_vars=len(c),
        num_constraints=len(A)
    )

    analysis = analyzer.analyze(np.array(c), np.array(b))

    # Interpretar resultados
    print("Precios Sombra:", analysis["shadow_prices"])
    print("Rangos de Optimalidad:", analysis["optimality_ranges"])
    print("Rangos de Factibilidad:", analysis["feasibility_ranges"])
```

## Historial de Cambios

- **v1.0** (2025-11-05): Implementación inicial con TDD
  - Cálculo de precios sombra
  - Cálculo de rangos de optimalidad
  - Cálculo de rangos de factibilidad
  - Integración con SimplexSolver

## Referencias

- Libro: "Introduction to Linear Optimization" (Bertsimas & Tsitsiklis)
- Capítulo 5: Sensitivity Analysis
- Wikipedia: [Sensitivity Analysis (Linear Programming)](https://en.wikipedia.org/wiki/Sensitivity_analysis)
