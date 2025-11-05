# Test Suite Documentation

Esta carpeta contiene la suite de pruebas completa para el proyecto Simplex Solver. Las pruebas están organizadas usando **pytest** como framework principal.

## 📋 Tabla de Contenidos

- [Estructura de Tests](#estructura-de-tests)
- [Cómo Ejecutar las Pruebas](#cómo-ejecutar-las-pruebas)
- [Tests de Estrés](#tests-de-estrés)
- [Fixtures Compartidos](#fixtures-compartidos)
- [Cobertura de Código](#cobertura-de-código)
- [Tests Existentes](#tests-existentes)

## 🗂️ Estructura de Tests

```
tests/
├── conftest.py                      # Fixtures compartidos para todos los tests
├── test_unit_solver_core.py         # Tests unitarios del algoritmo Simplex
├── test_unit_parser_ui.py           # Tests unitarios del parser y UI
├── test_unit_nlp_processor.py       # Tests unitarios de componentes NLP
├── test_unit_utils.py               # Tests unitarios de utilidades (logging, PDF)
├── test_e2e_solver.py               # Tests end-to-end del solver completo
├── test_e2e_nlp_pipeline.py         # Tests end-to-end del pipeline NLP
├── test_stress_solver.py            # Tests de estrés y rendimiento
├── test_nlp_system_pytest.py        # Tests completos del sistema NLP (pytest)
├── test_maximizacion_pytest.py      # Tests de problemas de maximización (pytest)
├── test_minimizacion_pytest.py      # Tests de problemas de minimización (pytest)
├── test_validation_pytest.py        # Tests de validación de entrada (pytest)
├── test_context_menu.py             # Tests del menú contextual
├── test_export_pdf.py               # Tests de exportación PDF
├── test_logging_system.py           # Tests del sistema de logging
├── test_nlp_system.py               # Tests NLP originales (unittest)
├── test_maximizacion.py             # Tests maximización originales (unittest)
├── test_minimizacion.py             # Tests minimización originales (unittest)
└── test_validation.py               # Tests validación originales (unittest)
```

## 🚀 Cómo Ejecutar las Pruebas

### Ejecutar Todos los Tests

```powershell
python -m pytest tests/
```

### Ejecutar con Verbose (recomendado)

```powershell
python -m pytest tests/ -v
```

### Ejecutar Tests Específicos

```powershell
# Un archivo específico
python -m pytest tests/test_unit_solver_core.py -v

# Una función específica
python -m pytest tests/test_unit_solver_core.py::test_simple_optimal_solution -v

# Todos los tests que contienen "nlp" en el nombre
python -m pytest tests/ -k "nlp" -v
```

### Ejecutar con Cobertura

```powershell
# Cobertura básica
python -m pytest tests/ --cov=simplex_solver

# Cobertura con reporte HTML
python -m pytest tests/ --cov=simplex_solver --cov-report=html

# Abrir reporte HTML (se genera en htmlcov/index.html)
start htmlcov/index.html
```

### Modo Quieto (menos output)

```powershell
python -m pytest tests/ -q
```

### Ver solo errores y traceback corto

```powershell
python -m pytest tests/ -v --tb=short
```

## ⚡ Tests de Estrés

Los tests de estrés (`test_stress_solver.py`) evalúan el rendimiento del sistema con problemas grandes. Por defecto, ejecutan versiones reducidas para no alargar demasiado las pruebas.

### Variables de Entorno para Tests de Estrés

Puedes controlar el tamaño de los tests de estrés con variables de entorno:

#### En PowerShell:

```powershell
# Configurar variables de entorno para una sesión
$env:STRESS_VARS = "100"           # Número de variables para tests de estrés
$env:STRESS_CONS = "50"            # Número de restricciones para tests de estrés
$env:LOG_STRESS_COUNT = "500"      # Número de entradas para test de logging
$env:SHORT_TESTS = "0"             # 0 = tests completos, 1 = tests cortos (default)

# Ejecutar tests de estrés con configuración personalizada
python -m pytest tests/test_stress_solver.py -v

# Restablecer a valores por defecto (tests cortos)
$env:SHORT_TESTS = "1"
```

#### En CMD:

```cmd
set STRESS_VARS=100
set STRESS_CONS=50
set LOG_STRESS_COUNT=500
set SHORT_TESTS=0
python -m pytest tests/test_stress_solver.py -v
```

### Valores por Defecto de Tests de Estrés

Si `SHORT_TESTS=1` (o no está configurado):

- Variables: 10
- Restricciones: 5
- Entradas de log: 20

Si `SHORT_TESTS=0`:

- Variables: Según `STRESS_VARS` (default: 50)
- Restricciones: Según `STRESS_CONS` (default: 30)
- Entradas de log: Según `LOG_STRESS_COUNT` (default: 100)

### Ejemplos de Uso

```powershell
# Tests de estrés rápidos (default)
python -m pytest tests/test_stress_solver.py -v

# Tests de estrés completos
$env:SHORT_TESTS = "0"
python -m pytest tests/test_stress_solver.py -v

# Tests de estrés con configuración personalizada
$env:SHORT_TESTS = "0"
$env:STRESS_VARS = "200"
$env:STRESS_CONS = "100"
python -m pytest tests/test_stress_solver.py -v

# Solo un test de estrés específico
python -m pytest tests/test_stress_solver.py::test_stress_large_solver -v
```

## 🔧 Fixtures Compartidos

El archivo `conftest.py` contiene fixtures reutilizables para todos los tests:

### Fixtures de Solver y UI

- `solver()` - Instancia de SimplexSolver
- `ui()` - Instancia de UserInterface

### Fixtures de Problemas de Ejemplo

#### Problemas de Maximización:

- `simple_max_problem()` - Problema simple de 2 variables con ≤
- `max_problem_with_ge()` - Problema con restricciones ≥ y ≤
- `max_problem_with_eq()` - Problema con restricciones de igualdad
- `max_3vars_problem()` - Problema de 3 variables
- `max_all_constraints()` - Problema con ≤, ≥ y =

#### Problemas de Minimización:

- `simple_min_problem()` - Problema simple de 2 variables con ≥
- `min_problem_with_le()` - Problema con restricciones ≤ y ≥
- `min_problem_with_eq()` - Problema con restricciones de igualdad
- `min_3vars_only_ge()` - Problema de 3 variables solo con ≥
- `min_all_constraints()` - Problema con ≤, ≥ y =
- `diet_problem()` - Problema de dieta (minimización)

### Fixtures Helper

- `assert_optimal_solution(result, expected_value, tolerance=1e-6)` - Verifica solución óptima
- `assert_solution_feasible(result, problem)` - Verifica factibilidad de solución

### Ejemplo de Uso de Fixtures

```python
def test_my_maximization(solver, simple_max_problem, assert_optimal_solution):
    """Test usando fixtures compartidos"""
    result = solver.solve(**simple_max_problem)
    assert_optimal_solution(result, 54.0)  # Verifica valor óptimo esperado
```

## 📊 Cobertura de Código

La suite de pruebas actual proporciona:

- **Cobertura Total**: ~52%
- **Módulos Core**: ~89% (algorithm.py)
- **Logging System**: ~90%
- **NLP Connector**: ~88%
- **Input Validator**: ~86%
- **Tableau**: ~86%

### Generar Reporte de Cobertura

```powershell
# Generar cobertura HTML
python -m pytest tests/ --cov=simplex_solver --cov-report=html

# Ver el reporte
start htmlcov/index.html
```

## 📝 Tests Existentes

### Tests Unitarios (Unit Tests)

**test_unit_solver_core.py** - Algoritmo Simplex:

- `test_simple_optimal_solution` - Solución óptima básica
- `test_unbounded_detected_via_mock` - Detección de problema no acotado
- `test_infeasible_detected_via_mock` - Detección de problema infactible

**test_unit_parser_ui.py** - Parser y UI:

- `test_parse_valid_example_file` - Parseo de archivo válido
- `test_parse_invalid_file` - Manejo de archivo inválido
- `test_interactive_input_monkeypatch` - Input interactivo simulado

**test_unit_nlp_processor.py** - Componentes NLP:

- `test_model_validator_and_generator_basic` - Validador y generador básicos
- `test_model_generator_equality_and_ge_conversion` - Conversión de restricciones
- `test_ollama_processor_success_and_failure` - Procesador Ollama con mocks
- `test_mock_nlp_processor_transports_and_diet` - MockNLPProcessor

**test_unit_utils.py** - Utilidades:

- `test_logging_system_write_and_db` - Sistema de logging con BD aislada
- `test_generate_pdf_delegates_to_export` - Delegación a export_to_pdf

### Tests End-to-End (E2E)

**test_e2e_solver.py**:

- `test_main_resolves_example_file` - Ejecución completa con archivo de ejemplo

**test_e2e_nlp_pipeline.py**:

- `test_nlp_pipeline_with_mocked_processor` - Pipeline NLP completo

### Tests de Estrés (Stress Tests)

**test_stress_solver.py**:

- `test_stress_large_solver` - Solver con problema grande
- `test_nlp_generator_handles_large_json` - Generador NLP con JSON grande
- `test_logging_stress_writes_many_entries` - Sistema de logging con muchas entradas

### Tests de Sistema NLP

**test_nlp_system_pytest.py** (26 tests):

- Detección de estructura de problemas
- Análisis de complejidad
- Validación de modelos
- Generación de modelos
- Procesadores NLP (Mock y Ollama)
- Connector y pipeline completo

### Tests de Problemas Específicos

**test_maximizacion_pytest.py** (9 tests):

- Problemas de 2 y 3 variables
- Diferentes tipos de restricciones
- Tests parametrizados

**test_minimizacion_pytest.py** (10 tests):

- Problemas de minimización
- Problema de dieta
- Tests parametrizados

**test_validation_pytest.py** (18 tests):

- Validación de entrada
- Casos edge (NaN, infinito, contradicciones)
- Tests parametrizados extensivos

### Tests Originales (unittest)

Los tests originales en formato unittest aún están disponibles:

- `test_nlp_system.py`
- `test_maximizacion.py`
- `test_minimizacion.py`
- `test_validation.py`

También disponibles:

- `test_context_menu.py` - Tests del menú contextual (19 tests)
- `test_export_pdf.py` - Tests de exportación PDF
- `test_logging_system.py` - Tests del sistema de logging

## 🔍 Estrategias de Testing

### Isolation con Monkeypatch

Los tests usan `monkeypatch` de pytest para aislar dependencias:

```python
def test_with_monkeypatch(monkeypatch, tmp_path):
    # Aislar base de datos de logging
    monkeypatch.setattr(LoggingSystem, "_get_db_path",
                       lambda self: str(tmp_path / "test.db"))

    # Simular entrada del usuario
    inputs = iter(["2", "3 5", ...])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
```

### Mocking de APIs Externas

Los tests mockean llamadas HTTP a Ollama:

```python
def test_ollama_api(monkeypatch):
    def mock_post(url, json, timeout):
        return type('obj', (), {
            'status_code': 200,
            'json': lambda: {"response": '{"objective": [...]}'}
        })

    monkeypatch.setattr("requests.post", mock_post)
```

### Tests Parametrizados

Uso de `@pytest.mark.parametrize` para evitar repetición:

```python
@pytest.mark.parametrize("c,A,b,constraint_types,description", [
    ([3, 5], [[1, 0], [0, 1]], [4, 6], ["<=", "<="], "Simple case"),
    ([2, 3], [[1, 1]], [5], ["<="], "Single constraint"),
])
def test_multiple_cases(c, A, b, constraint_types, description):
    # Test con diferentes parámetros
    pass
```

## 🎯 Mejores Prácticas

1. **Ejecutar tests antes de commit**:

   ```powershell
   python -m pytest tests/ -v
   ```

2. **Usar fixtures cuando sea posible** - Evita duplicación de código

3. **Tests de estrés en CI**: Configurar `SHORT_TESTS=0` en CI/CD

4. **Verificar cobertura** después de agregar features nuevas

5. **Aislar dependencias** con monkeypatch y tmp_path

6. **Nombrar tests descriptivamente**:
   - `test_<what>_<scenario>_<expected>`
   - Ejemplo: `test_solver_unbounded_detects_correctly`

## 📚 Recursos Adicionales

- [Documentación de pytest](https://docs.pytest.org/)
- [pytest-cov Documentation](https://pytest-cov.readthedocs.io/)
- [Documentación del proyecto](../docs/)

---

**Total de Tests**: 157 tests (156 passed, 1 skipped)  
**Cobertura**: ~52% del código  
**Tiempo de Ejecución**: ~34 segundos (todos los tests)
