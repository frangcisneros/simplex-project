# Guía del Desarrollador - Simplex Solver

## Descripción General

Esta guía proporciona información técnica sobre la arquitectura, sistemas internos y procedimientos de desarrollo del proyecto Simplex Solver. Está dirigida a desarrolladores que deseen entender, modificar o contribuir al proyecto.

## Arquitectura del Sistema

### Estructura del Proyecto

```
simplex-project/
├── simplex.py                       # Script principal
├── installer.py                     # Instalador interactivo
├── pyproject.toml                   # Configuración del proyecto
├── requirements*.txt                # Dependencias
│
├── simplex_solver/                  # Paquete principal
│   ├── __init__.py
│   ├── main.py                      # Punto de entrada principal
│   ├── solver.py                    # Wrapper de compatibilidad
│   ├── file_parser.py               # Parser de archivos de entrada
│   ├── user_interface.py            # Interfaz de usuario interactiva
│   ├── input_validator.py           # Validación de entrada
│   ├── reporting_pdf.py             # Generación de reportes
│   ├── export.py                    # Exportación a PDF
│   ├── logging_system.py            # Sistema de logging
│   ├── problem_history.py           # Historial de problemas
│   ├── log_viewer.py                # Visor de logs
│   ├── debug.py                     # Utilidades de depuración
│   ├── system_analyzer.py           # Análisis de capacidades del sistema
│   │
│   ├── core/                        # Algoritmo Simplex
│   │   ├── __init__.py
│   │   └── algorithm.py             # Implementación del algoritmo
│   │
│   ├── utils/                       # Utilidades
│   │   ├── __init__.py
│   │   └── tableau.py               # Gestión de tableaus
│   │
│   ├── nlp/                         # Sistema de procesamiento de lenguaje natural
│   │   ├── __init__.py
│   │   ├── connector.py             # Orquestador principal
│   │   ├── interfaces.py            # Interfaces base
│   │   ├── config.py                # Configuración de modelos
│   │   ├── processor.py             # Procesador mock
│   │   ├── ollama_processor.py      # Procesador Ollama
│   │   ├── model_generator.py       # Generador de modelos matemáticos
│   │   ├── problem_structure_detector.py  # Detector de estructura
│   │   └── complexity_analyzer.py   # Análisis de complejidad
│   │
│   ├── io/                          # Entrada/Salida (reservado)
│   └── ui/                          # Interfaz de usuario (reservado)
│
├── context_menu/                    # Integración con Windows
│   ├── solve_from_context.py
│   ├── solve_from_context_ai.py
│   ├── install.bat
│   ├── uninstall.bat
│   └── reinstall.bat
│
├── ejemplos/                        # Archivos de ejemplo
├── tests/                           # Suite de tests
├── tools/                           # Herramientas de desarrollo
└── logs/                           # Base de datos de logging
```

### Módulos Principales

#### core/algorithm.py - SimplexSolver

Implementación del algoritmo Simplex con soporte para:

- Problemas de maximización y minimización
- Restricciones de tipo `<=`, `>=` y `=`
- Detección de problemas no acotados e infactibles
- Método de dos fases para restricciones de igualdad y `>=`
- Modo verbose con tres niveles de detalle

#### nlp/connector.py - NLPConnector

Orquestador del pipeline de procesamiento de lenguaje natural:

- Detección de estructura del problema
- Análisis de complejidad
- Validación de modelos matemáticos
- Generación de modelos
- Integración con el solver

#### logging_system.py - LoggingSystem

Sistema de logging persistente basado en SQLite:

- Múltiples niveles de log (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- Almacenamiento de sesiones
- Eventos del solver
- Operaciones de archivos
- Retención automática de 180 días

#### problem_history.py - ProblemHistory

Sistema de historial de problemas resueltos:

- Almacenamiento automático de problemas óptimos
- Búsqueda y consulta
- Re-resolución desde historial
- Estadísticas

## Sistema de Inteligencia Artificial

### Arquitectura NLP

El sistema NLP utiliza una arquitectura modular basada en interfaces:

```
NLPConnector (Orquestador)
    │
    ├── ProblemStructureDetector  → Analiza el texto del problema
    ├── ComplexityAnalyzer         → Evalúa la complejidad
    ├── INLPProcessor              → Procesa con IA (Ollama o Mock)
    ├── ModelValidator             → Valida el modelo generado
    └── ModelGenerator             → Genera modelo matemático
```

### Procesadores NLP

#### MockNLPProcessor

Procesador de prueba que no requiere IA real:

- Detecta problemas predefinidos por palabras clave
- Útil para desarrollo y testing
- No requiere Ollama instalado

#### OllamaProcessor

Procesador que utiliza modelos de lenguaje local:

- Se conecta a Ollama vía HTTP API
- Utiliza prompts estructurados
- Parsea respuestas JSON
- Manejo de errores y reintentos

### Configuración de Modelos

En `simplex_solver/nlp/config.py`:

```python
class NLPModelType(Enum):
    LLAMA3_1_8B = "llama3.1:8b"
    LLAMA3_2_3B = "llama3.2:3b"
    MISTRAL_7B = "mistral:7b"
    PHI3_MINI = "phi3:mini"
    GEMMA2_9B = "gemma2:9b"
    QWEN2_5_14B = "qwen2.5:14b"
    LLAMA3_1_70B = "llama3.1:70b"
    MOCK = "mock"
```

Cada modelo tiene configuración específica:

```python
ModelConfig.DEFAULT_CONFIGS = {
    NLPModelType.LLAMA3_1_8B: {
        "temperature": 0.1,      # Precisión vs creatividad
        "max_tokens": 2048,      # Longitud máxima de respuesta
        "top_p": 0.9,           # Nucleus sampling
        "timeout": 120          # Timeout en segundos
    }
}
```

### Prompts del Sistema

Los prompts están optimizados para extracción estructurada:

```python
OPTIMIZATION_EXTRACTION_PROMPT = """
Eres un experto en programación lineal. Analiza el siguiente problema
y extrae la información en formato JSON exacto.

Formato requerido:
{
    "objective": {
        "type": "maximize" o "minimize",
        "coefficients": [lista de coeficientes],
        "variables": [nombres de variables]
    },
    "constraints": [
        {
            "coefficients": [coeficientes],
            "operator": "<=", ">=" o "=",
            "rhs": valor del lado derecho
        }
    ]
}
"""
```

### Tiempos de Ejecución Esperados

- **MockNLPProcessor**: < 1 segundo
- **Ollama (primera vez)**: 30-120 segundos (carga del modelo)
- **Ollama (modelo cargado)**: 10-30 segundos
- **Problemas complejos**: hasta 2 minutos

### Verificación de Ollama

```python
import requests

def verificar_ollama():
    try:
        response = requests.get("http://localhost:11434/api/tags")
        if response.status_code == 200:
            modelos = response.json().get("models", [])
            return [m["name"] for m in modelos]
    except:
        return None
```

## Sistema de Logging

### Arquitectura del Sistema de Logging

El sistema utiliza SQLite para almacenamiento persistente y estructurado de logs.

#### Características Principales

- **Base de datos SQLite**: Liviana, sin instalación adicional, portable
- **Thread-safe**: Manejo seguro de concurrencia
- **Niveles de log**: DEBUG, INFO, WARNING, ERROR, CRITICAL
- **Retención automática**: 180 días por defecto

#### Estructura de la Base de Datos

**Tabla: logs**

```sql
CREATE TABLE logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    session_id TEXT NOT NULL,
    level TEXT NOT NULL,
    module TEXT,
    function TEXT,
    line_number INTEGER,
    message TEXT NOT NULL,
    exception_type TEXT,
    exception_message TEXT,
    stack_trace TEXT,
    user_data TEXT,
    system_info TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Tabla: sessions**

```sql
CREATE TABLE sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT UNIQUE NOT NULL,
    start_time TEXT NOT NULL,
    end_time TEXT,
    python_version TEXT,
    os_system TEXT,
    os_version TEXT,
    machine TEXT,
    processor TEXT,
    app_version TEXT,
    execution_mode TEXT,
    command_line_args TEXT
);
```

**Tabla: solver_events**

```sql
CREATE TABLE solver_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    event_type TEXT NOT NULL,
    problem_type TEXT,
    num_variables INTEGER,
    num_constraints INTEGER,
    iterations INTEGER,
    execution_time_ms REAL,
    status TEXT,
    optimal_value REAL,
    additional_data TEXT
);
```

**Tabla: file_operations**

```sql
CREATE TABLE file_operations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    operation_type TEXT NOT NULL,
    file_path TEXT,
    file_size INTEGER,
    success INTEGER,
    error_message TEXT
);
```

### Uso del Sistema de Logging

```python
from simplex_solver.logging_system import logger

# Logs básicos
logger.debug("Mensaje de depuración")
logger.info("Información general")
logger.warning("Advertencia")
logger.error("Error")
logger.critical("Error crítico")

# Log con excepción
try:
    resultado = operacion_riesgosa()
except Exception as e:
    logger.error("Falló la operación", exception=e)

# Log con datos personalizados
logger.info("Usuario realizó acción", user_data={
    "action": "solve",
    "variables": 5,
    "constraints": 3
})

# Log de eventos del solver
logger.log_solver_event(
    event_type="solve_complete",
    problem_type="maximización",
    num_variables=5,
    num_constraints=3,
    iterations=12,
    execution_time_ms=45.23,
    status="optimal",
    optimal_value=150.5
)

# Log de operaciones con archivos
logger.log_file_operation(
    operation_type="read",
    file_path="problema.txt",
    success=True
)
```

### Visor de Logs

```bash
# Ejecutar visor interactivo
python tools/logs.py

# Ver estadísticas rápidas
python tools/logs.py --stats

# Verificar integridad
python tools/logs.py --verify
```

El visor proporciona:

1. Ver logs recientes
2. Filtrar por nivel
3. Ver logs por sesión
4. Ver estadísticas
5. Ver eventos del solver
6. Ver operaciones de archivos
7. Buscar en logs
8. Exportar logs
9. Limpiar logs antiguos

### Ubicación de la Base de Datos

- **Desarrollo**: `<proyecto>/logs/simplex_logs.db`
- **Producción (Windows)**: `%APPDATA%\SimplexSolver\logs\simplex_logs.db`
- **Producción (Linux/Mac)**: `~/.SimplexSolver/logs/simplex_logs.db`

### Consultas SQL Útiles

```sql
-- Ver últimos 10 logs
SELECT timestamp, level, module, message
FROM logs
ORDER BY timestamp DESC
LIMIT 10;

-- Contar errores por módulo
SELECT module, COUNT(*) as error_count
FROM logs
WHERE level = 'ERROR'
GROUP BY module
ORDER BY error_count DESC;

-- Estadísticas del solver
SELECT
    COUNT(*) as total_solves,
    AVG(iterations) as avg_iterations,
    AVG(execution_time_ms) as avg_time_ms,
    status
FROM solver_events
WHERE event_type = 'solve_complete'
GROUP BY status;
```

## Sistema de Historial de Problemas

### Arquitectura

El sistema de historial almacena automáticamente todos los problemas resueltos con estado óptimo en la misma base de datos de logging.

### Tabla: problem_history

```sql
CREATE TABLE problem_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    file_path TEXT,
    file_name TEXT,
    file_content TEXT NOT NULL,
    problem_type TEXT,
    num_variables INTEGER,
    num_constraints INTEGER,
    iterations INTEGER,
    execution_time_ms REAL,
    status TEXT,
    optimal_value REAL,
    solution_variables TEXT
);
```

### Uso Programático

```python
from simplex_solver.problem_history import ProblemHistory

# Crear instancia
history = ProblemHistory()

# Obtener todos los problemas
problems = history.get_all_problems(limit=50)

# Buscar por nombre
results = history.search_problems("produccion")

# Obtener detalles completos
problem = history.get_problem_by_id(1)

# Crear archivo temporal para re-resolver
temp_file = history.create_temp_file_from_history(1)

# Obtener estadísticas
stats = history.get_statistics()
```

### Visor de Historial

```bash
# Ejecutar visor interactivo
python tools/history.py

# Ver estadísticas
python tools/history.py --stats

# Ejecutar tests
python tools/history.py --test
```

## Modo Debug/Verbose

El solver soporta tres niveles de verbosidad para facilitar la depuración y el aprendizaje del algoritmo.

### Niveles de Verbosidad

- **verbose_level=0** (por defecto): Modo silencioso, solo registra el resultado final
- **verbose_level=1**: Modo básico, registra información general de fases y optimalidad
- **verbose_level=2**: Modo detallado, registra cada iteración con variables entrantes/salientes

### Uso

```python
from simplex_solver.core.algorithm import SimplexSolver

solver = SimplexSolver()

# Modo silencioso (por defecto)
result = solver.solve(c, A, b, constraint_types, maximize=True)

# Modo básico
result = solver.solve(c, A, b, constraint_types, maximize=True, verbose_level=1)

# Modo detallado
result = solver.solve(c, A, b, constraint_types, maximize=True, verbose_level=2)
```

### Ejemplo de Salida

**Nivel 0 (Silencioso):**

```
[INFO] Starting solver - Variables: 2, Constraints: 3, Type: MAX
[INFO] Optimal solution found - Value: 30.000000, Total iterations: 2
```

**Nivel 1 (Básico):**

```
[INFO] Starting solver - Variables: 2, Constraints: 3, Type: MAX
[INFO] Solving in single phase (no artificial variables)
[INFO] Optimality condition reached
[INFO] Optimal solution found - Value: 30.000000, Total iterations: 2
```

**Nivel 2 (Detallado):**

```
[INFO] Starting solver - Variables: 2, Constraints: 3, Type: MAX
[INFO] Solving in single phase (no artificial variables)
[INFO] Entering variable: column 2
[INFO] Leaving variable: row 2, pivot: 2.0000
[INFO] Iteration 1 - Basic solution: x1=0.0000, x2=6.0000, Current value: 30.0000
[INFO] Optimality condition reached
[INFO] Final solution: x1=0.0000, x2=6.0000, Optimal value: 30.0000
[INFO] Optimal solution found - Value: 30.000000, Total iterations: 1
```

## Compilación de Ejecutables

### Sistema Unificado de Build

El proyecto utiliza un sistema de build consolidado siguiendo principios SOLID:

```bash
# Generar el instalador
python tools/build.py --installer

# Generar el solver
python tools/build.py --solver

# Generar ambos
python tools/build.py --all

# Limpiar artifacts de compilación
python tools/build.py --clean
```

### Requisitos de Build

```bash
pip install -r requirements-build.txt
```

Esto instalará:

- PyInstaller
- Todas las dependencias necesarias

### Archivos Generados

**SimplexInstaller.exe** (~40-50 MB)

- Instalador interactivo completo
- Incluye análisis de sistema
- Gestión de componentes opcionales
- Configuración de menú contextual

**SimplexSolver.exe** (~30-40 MB)

- Solver standalone
- Modo interactivo
- Resolución desde archivos
- Generación de reportes PDF

### Ubicación de Salida

Los ejecutables se generan en:

```
dist/
├── SimplexInstaller.exe
└── SimplexSolver.exe
```

### Personalización del Build

El archivo `tools/build.py` contiene la configuración de PyInstaller. Para personalizar:

```python
class BuildConfig:
    # Directorios
    DIST_DIR = "dist"
    BUILD_DIR = "build"

    # Exclusiones (reducir tamaño)
    EXCLUDED_MODULES = [
        "tkinter", "matplotlib", "PIL", "PyQt5",
        "scipy", "pandas", "IPython", "jupyter"
    ]

    # Datos adicionales
    DATAS = [
        ("context_menu", "context_menu"),
        ("ejemplos", "ejemplos"),
        ("README.md", "."),
    ]
```

### Solución de Problemas de Build

**PyInstaller no encontrado:**

```bash
pip install pyinstaller
```

**Error de módulos faltantes:**

```bash
pip install -r requirements.txt
```

**Ejecutable muy grande:**

- Verifique las exclusiones en `tools/build.py`
- Agregue más módulos a `EXCLUDED_MODULES`
- UPX está habilitado por defecto para compresión

**Antivirus bloquea el ejecutable:**

- Común con ejecutables de PyInstaller (falsos positivos)
- Agregue una excepción en su antivirus
- Para distribución, firme el ejecutable con certificado digital

## Testing

### Estructura de Tests

```
tests/
├── conftest.py                      # Fixtures compartidos
├── test_unit_solver_core.py         # Tests unitarios del solver
├── test_unit_parser_ui.py           # Tests de parser y UI
├── test_unit_nlp_processor.py       # Tests de componentes NLP
├── test_unit_utils.py               # Tests de utilidades
├── test_e2e_solver.py               # Tests end-to-end del solver
├── test_e2e_nlp_pipeline.py         # Tests end-to-end NLP
└── test_stress_solver.py            # Tests de estrés
```

### Ejecutar Tests

```bash
# Todos los tests
python -m pytest tests/ -v

# Tests específicos
python -m pytest tests/test_unit_solver_core.py -v

# Con cobertura
python -m pytest tests/ --cov=simplex_solver --cov-report=html

# Solo tests que contienen "nlp"
python -m pytest tests/ -k "nlp" -v
```

### Fixtures Compartidos

El archivo `conftest.py` proporciona fixtures reutilizables:

```python
@pytest.fixture
def solver():
    """Instancia del solver"""
    return SimplexSolver()

@pytest.fixture
def simple_max_problem():
    """Problema de maximización simple"""
    return {
        "c": [3, 5],
        "A": [[1, 0], [0, 2], [3, 2]],
        "b": [4, 12, 18],
        "constraint_types": ["<=", "<=", "<="],
        "maximize": True
    }
```

### Tests de Estrés

Los tests de estrés evalúan el rendimiento con problemas grandes:

```bash
# Tests de estrés con configuración por defecto
python -m pytest tests/test_stress_solver.py -v

# Tests de estrés completos
$env:SHORT_TESTS = "0"
python -m pytest tests/test_stress_solver.py -v

# Configuración personalizada
$env:STRESS_VARS = "200"
$env:STRESS_CONS = "100"
python -m pytest tests/test_stress_solver.py -v
```

### Cobertura de Código

Cobertura actual:

- **Total**: ~53%
- **core/algorithm.py**: ~89%
- **logging_system.py**: ~90%
- **nlp/connector.py**: ~88%
- **input_validator.py**: ~86%

Para mejorar la cobertura:

1. Agregar tests para casos edge
2. Cubrir manejo de excepciones
3. Agregar tests de integración

### Estrategias de Testing

**Isolation con Monkeypatch:**

```python
def test_with_monkeypatch(monkeypatch, tmp_path):
    # Aislar base de datos
    monkeypatch.setattr(LoggingSystem, "_get_db_path",
                       lambda self: str(tmp_path / "test.db"))
```

**Mocking de APIs Externas:**

```python
def test_ollama_api(monkeypatch):
    def mock_post(url, json, timeout):
        return type('obj', (), {
            'status_code': 200,
            'json': lambda: {"response": '{"objective": [...]}'}
        })
    monkeypatch.setattr("requests.post", mock_post)
```

**Tests Parametrizados:**

```python
@pytest.mark.parametrize("c,A,b,expected", [
    ([3, 5], [[1, 0]], [4], 20),
    ([2, 3], [[1, 1]], [5], 15),
])
def test_multiple_cases(c, A, b, expected):
    result = solver.solve(c, A, b, ["<="], maximize=True)
    assert abs(result["optimal_value"] - expected) < 1e-6
```

## Herramientas de Desarrollo

El directorio `tools/` contiene herramientas consolidadas:

### tools/build.py

Sistema unificado de compilación siguiendo principios SOLID.

### tools/logs.py

Gestión unificada de logs con interfaz interactiva.

### tools/history.py

Gestión del historial de problemas con interfaz interactiva.

Para más información, consulte `tools/README.md`.

## Contribución al Proyecto

### Flujo de Trabajo Recomendado

1. Fork del repositorio
2. Crear rama de feature: `git checkout -b feature/nueva-funcionalidad`
3. Implementar cambios siguiendo el estilo del proyecto
4. Agregar tests para nueva funcionalidad
5. Verificar que todos los tests pasen: `python -m pytest tests/ -v`
6. Verificar cobertura: `python -m pytest tests/ --cov=simplex_solver`
7. Commit con mensajes descriptivos
8. Push y crear Pull Request

### Estándares de Código

- Seguir PEP 8 para estilo de código Python
- Documentar funciones y clases con docstrings
- Mantener funciones pequeñas y enfocadas (principio SOLID)
- Agregar type hints cuando sea posible
- Escribir tests para nueva funcionalidad

### Documentación

Al agregar funcionalidad nueva:

1. Actualizar docstrings en el código
2. Actualizar esta guía si es necesario
3. Agregar ejemplos de uso
4. Documentar cambios en el formato de datos

## Integración Continua

El proyecto utiliza GitHub Actions para CI/CD (ver `.github/workflows/ci.yml`):

### Workflow de CI

- Se ejecuta en cada push y pull request a `main` y `quality/tests`
- Configura Python 3.10
- Instala todas las dependencias
- Ejecuta la suite completa de tests

### Workflow de CD

- Se activa al crear tags con patrón `v*.*.*`
- Compila los ejecutables
- Crea una Release en GitHub
- Adjunta ejecutables y documentación

Para crear una nueva release:

```bash
git tag v1.0.0
git push origin v1.0.0
```

## Análisis del Sistema

El módulo `system_analyzer.py` proporciona información sobre las capacidades del sistema:

```python
from simplex_solver.system_analyzer import SystemAnalyzer

analyzer = SystemAnalyzer()
capabilities = analyzer.analyze_system()

print(f"RAM: {capabilities.ram_gb} GB")
print(f"CPU: {capabilities.cpu_count} cores @ {capabilities.cpu_freq_ghz} GHz")
print(f"GPU: {capabilities.has_nvidia_gpu}")
print(f"Compatible con Ollama: {capabilities.can_run_ollama}")

# Obtener recomendaciones de modelos
recommendations = analyzer.get_model_recommendations()
for rec in recommendations:
    print(f"{rec.model_name}: {rec.recommendation_level}")
```

## Recursos Adicionales

### Documentación de Dependencias

- **NumPy**: https://numpy.org/doc/
- **Tabulate**: https://pypi.org/project/tabulate/
- **Psutil**: https://psutil.readthedocs.io/
- **PyInstaller**: https://pyinstaller.org/
- **Pytest**: https://docs.pytest.org/
- **Ollama**: https://ollama.ai/

### Referencias de Algoritmos

- Algoritmo Simplex: https://en.wikipedia.org/wiki/Simplex_algorithm
- Método de Dos Fases: https://en.wikipedia.org/wiki/Simplex_algorithm#Two-phase_simplex
- Programación Lineal: https://en.wikipedia.org/wiki/Linear_programming

## Contacto y Soporte

Para cuestiones técnicas o contribuciones:

- GitHub Issues: https://github.com/frangcisneros/simplex-project/issues
- Pull Requests: https://github.com/frangcisneros/simplex-project/pulls

Para usuarios finales, consulte GUIA_USUARIO.md.
