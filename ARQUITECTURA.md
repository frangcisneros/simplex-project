# Arquitectura del Sistema - Simplex Project

## 📋 Índice

1. [Estructura General](#estructura-general)
2. [Módulos Principales](#módulos-principales)
3. [Principios de Diseño](#principios-de-diseño)
4. [Flujo de Datos](#flujo-de-datos)
5. [Guía de Uso](#guía-de-uso)

---

## 🏗️ Estructura General

```
simplex-project/
├── src/
│   ├── nlp/                    # Sistema de procesamiento NLP (Principal)
│   │   ├── interfaces.py       # Contratos e interfaces (SOLID - I)
│   │   ├── config.py          # Configuración centralizada (DRY)
│   │   ├── processor.py       # Procesadores NLP base
│   │   ├── ollama_processor.py # Procesador con Ollama
│   │   ├── connector.py       # Orquestador principal (SOLID - S)
│   │   ├── model_generator.py # Generación de modelos matemáticos
│   │   ├── complexity_analyzer.py # Análisis y selección de modelos
│   │   └── problem_structure_detector.py # Detección de estructura
│   │
│   ├── regex_parser/          # Parser alternativo (regex)
│   ├── spacy_nlp/            # Parser alternativo (spaCy)
│   └── solver.py             # Algoritmo Simplex core
│
├── test_ejercicios_naturales.py # Tests con lenguaje natural
├── test_ia_simple.py            # Test rápido de IA
├── test_ia.py                   # Suite completa de tests
└── ejemplos/                    # Problemas de ejemplo

```

---

## 🎯 Módulos Principales

### 1. **Interfaces (`src/nlp/interfaces.py`)**

**Propósito:** Define contratos para todos los componentes (SOLID - Interface Segregation)

**Interfaces principales:**

- `INLPProcessor`: Procesa texto natural → problema estructurado
- `IModelGenerator`: Genera modelo matemático para el solver
- `IOptimizationSolver`: Resuelve el problema de optimización
- `INLPConnector`: Orquesta el pipeline completo
- `IModelValidator`: Valida problemas antes de resolver

**Ventajas:**

- ✅ Fácil agregar nuevos procesadores sin modificar código existente (Open/Closed)
- ✅ Testing simplificado con mocks
- ✅ Bajo acoplamiento entre componentes

---

### 2. **Configuración (`src/nlp/config.py`)**

**Propósito:** Centraliza configuración y elimina valores hardcoded (DRY)

**Contiene:**

- `NLPModelType`: Enum con modelos disponibles
- `ModelConfig`: Configuración de cada modelo (temperatura, tokens, etc.)
- `PromptTemplates`: Prompts para el LLM (centralizados)
- `ErrorMessages`: Mensajes de error estándar
- `DefaultSettings`: Valores por defecto del sistema

**Ventajas:**

- ✅ Un solo lugar para cambiar configuración
- ✅ Fácil agregar nuevos modelos
- ✅ Prompts versionados y documentados

---

### 3. **Procesadores NLP (`src/nlp/processor.py`, `ollama_processor.py`)**

#### `MockNLPProcessor` (Testing)

**Propósito:** Procesador simple para tests sin dependencias externas (KISS)

**Uso:**

```python
processor = MockNLPProcessor()
result = processor.process_text("Maximizar 2x + 3y...")
```

#### `OllamaNLPProcessor` (Producción)

**Propósito:** Procesador que usa Ollama para análisis real de problemas

**Características:**

- ✅ Conexión HTTP a Ollama (sin librerías pesadas)
- ✅ Detección automática de estructura del problema
- ✅ Validación robusta de JSON generado
- ✅ Manejo de errores completo

**Flujo:**

1. Detectar estructura del problema (hint para el modelo)
2. Generar prompt especializado
3. Llamar API de Ollama
4. Extraer y validar JSON
5. Calcular score de confianza

---

### 4. **Conector (`src/nlp/connector.py`)**

**Propósito:** Orquesta el pipeline completo (SOLID - Single Responsibility)

#### `NLPOptimizationConnector`

**Responsabilidad:** Coordinar el flujo: Texto → NLP → Validación → Modelo → Solución

**Pipeline:**

```
Texto Natural
    ↓
[INLPProcessor] → Extrae problema
    ↓
[IModelValidator] → Valida estructura
    ↓
[IModelGenerator] → Genera modelo matemático
    ↓
[IOptimizationSolver] → Resuelve
    ↓
Solución + Metadata
```

**Ventajas:**

- ✅ Un solo punto de entrada
- ✅ Manejo de errores en cada etapa
- ✅ Metadata completa (tiempo, confianza, warnings)

#### `NLPConnectorFactory`

**Responsabilidad:** Crear conectores configurados (Factory Pattern)

```python
# Crear conector con Ollama
connector = NLPConnectorFactory.create_connector(
    nlp_model_type=NLPModelType.LLAMA3_1_8B,
    solver_type=SolverType.SIMPLEX
)

# Usar
result = connector.process_and_solve(problema_texto)
```

#### `SimplexSolverAdapter`

**Responsabilidad:** Adaptar SimplexSolver al sistema NLP (Adapter Pattern)

**Ventajas:**

- ✅ No modifica el solver original (Open/Closed)
- ✅ Agrega funcionalidad (nombres de variables)
- ✅ Compatible con otros solvers futuros

---

### 5. **Generador de Modelos (`src/nlp/model_generator.py`)**

#### `SimplexModelGenerator`

**Responsabilidad:** Convertir problema estructurado → formato Simplex

**Transformación:**

```python
# Entrada (del NLP):
{
  "objective_type": "maximize",
  "objective_coefficients": [50, 40],
  "constraints": [
    {"coefficients": [2, 1], "operator": "<=", "rhs": 100}
  ]
}

# Salida (para Simplex):
{
  "c": [50, 40],
  "A": [[2, 1]],
  "b": [100],
  "maximize": True
}
```

#### `ModelValidator`

**Responsabilidad:** Validar problemas antes de resolver

**Validaciones:**

- ✅ Coeficientes son numéricos
- ✅ Dimensiones consistentes
- ✅ Restricciones bien formadas
- ✅ No hay valores infinitos/NaN

---

### 6. **Analizadores de Complejidad**

#### `ProblemStructureDetector` (`problem_structure_detector.py`)

**Responsabilidad:** Analizar texto y detectar estructura esperada

**Detecta:**

- Tipo de problema (simple, transporte, producción, multi-planta)
- Número esperado de variables
- Patrones comunes

**Uso:** Genera hints para el LLM para mejorar extracción

#### `ModelSelector` (`complexity_analyzer.py`)

**Responsabilidad:** Seleccionar modelo óptimo según problema y recursos

**Considera:**

- Complejidad del texto
- RAM disponible
- GPU disponible
- Modelos instalados

---

## 🎨 Principios de Diseño Aplicados

### ✅ SOLID

#### **S - Single Responsibility**

- Cada clase tiene una responsabilidad única
- `OllamaNLPProcessor`: solo procesar texto
- `ModelGenerator`: solo generar modelos
- `Connector`: solo orquestar

#### **O - Open/Closed**

- Abierto a extensión, cerrado a modificación
- Agregar nuevo procesador: implementar `INLPProcessor`
- Agregar nuevo solver: implementar `IOptimizationSolver`
- No modificar código existente

#### **L - Liskov Substitution**

- Todos los procesadores NLP son intercambiables
- `MockNLPProcessor` y `OllamaNLPProcessor` tienen misma interfaz
- Tests funcionan con cualquier implementación

#### **I - Interface Segregation**

- Interfaces pequeñas y específicas
- `INLPProcessor`: solo `process_text()` e `is_available()`
- `IModelValidator`: solo `validate()` y `get_validation_errors()`

#### **D - Dependency Inversion**

- Depende de abstracciones, no implementaciones concretas
- `Connector` depende de `INLPProcessor`, no de `OllamaNLPProcessor`
- Fácil inyectar dependencias para testing

### ✅ DRY (Don't Repeat Yourself)

- **Configuración centralizada** en `config.py`
- **Prompts reutilizables** en `PromptTemplates`
- **Validación común** en `ModelValidator`
- **Extracción de JSON** centralizada (método reutilizable)

### ✅ KISS (Keep It Simple, Stupid)

- **Interfaz simple**: `process_and_solve(texto)` → resultado
- **MockProcessor** para tests sin complejidad
- **Factory** para creación simple: `create_connector()`
- **Logging claro** en cada paso

---

## 🔄 Flujo de Datos

### Flujo Normal (Exitoso)

```
Usuario ingresa texto
    ↓
NLPConnectorFactory.create_connector()
    ├── Crea OllamaNLPProcessor
    ├── Crea SimplexModelGenerator
    ├── Crea SimplexSolverAdapter
    └── Crea ModelValidator
    ↓
connector.process_and_solve(texto)
    ↓
[1] ProblemStructureDetector.detect_structure()
    └── Analiza texto → hint de estructura
    ↓
[2] OllamaNLPProcessor.process_text()
    ├── Verifica Ollama disponible
    ├── Genera prompt con hint
    ├── Llama API Ollama
    ├── Extrae JSON de respuesta
    └── Calcula confianza → NLPResult
    ↓
[3] ModelValidator.validate(problem)
    └── Valida dimensiones y estructura
    ↓
[4] SimplexModelGenerator.generate_model()
    └── Convierte a formato {c, A, b, maximize}
    ↓
[5] SimplexSolverAdapter.solve(model)
    ├── Llama SimplexSolver.solve()
    └── Enriquece con variable_names
    ↓
Retorna resultado completo:
{
  "success": true,
  "solution": {...},
  "extracted_problem": {...},
  "nlp_confidence": 0.85,
  "processing_time": 12.5,
  "structure_analysis": {...}
}
```

### Manejo de Errores

Cada etapa puede fallar independientemente:

```
Error en paso X
    ↓
Return {
  "success": false,
  "error": "mensaje descriptivo",
  "step_failed": "nombre_del_paso"
}
```

**Puntos de fallo:**

1. `nlp_availability`: Ollama no disponible
2. `nlp_processing`: Error generando respuesta
3. `problem_extraction`: JSON inválido
4. `validation`: Problema mal formado
5. `model_generation`: Error en conversión
6. `solving`: Error en algoritmo Simplex

---

## 📖 Guía de Uso

### Uso Básico

```python
from src.nlp import NLPConnectorFactory, NLPModelType

# 1. Crear conector
connector = NLPConnectorFactory.create_connector(
    nlp_model_type=NLPModelType.LLAMA3_1_8B
)

# 2. Resolver problema
resultado = connector.process_and_solve("""
    Una empresa fabrica productos A y B.
    A da $50 de ganancia, B da $40.
    Cada A requiere 2 horas, cada B 1 hora.
    Hay 100 horas disponibles.
    Maximizar ganancia.
""")

# 3. Usar resultado
if resultado["success"]:
    print(f"Valor óptimo: {resultado['solution']['optimal_value']}")
    print(f"Variables: {resultado['solution']['solution']}")
```

### Testing

```python
# Con Mock (rápido, sin IA)
connector = NLPConnectorFactory.create_connector(use_mock_nlp=True)
resultado = connector.process_and_solve(problema)

# Con IA real
connector = NLPConnectorFactory.create_connector(use_mock_nlp=False)
resultado = connector.process_and_solve(problema)
```

### Agregar Nuevo Procesador

```python
from src.nlp.interfaces import INLPProcessor, NLPResult

class MiNuevoProcessador(INLPProcessor):
    def is_available(self) -> bool:
        # Verificar si está disponible
        return True

    def process_text(self, text: str) -> NLPResult:
        # Procesar texto
        problem = self._extraer_problema(text)
        return NLPResult(success=True, problem=problem)
```

### Agregar Nuevo Solver

```python
from src.nlp.interfaces import IOptimizationSolver

class MiSolverAdapter(IOptimizationSolver):
    def solve(self, model: Dict[str, Any]) -> Dict[str, Any]:
        # Resolver con tu algoritmo
        resultado = mi_algoritmo(model)
        return {
            "status": "optimal",
            "solution": resultado,
            "optimal_value": valor
        }
```

---

## 📊 Comparación de Componentes

| Componente                      | Responsabilidad | Complejidad | Testing      |
| ------------------------------- | --------------- | ----------- | ------------ |
| `interfaces.py`                 | Contratos       | Baja        | Fácil        |
| `config.py`                     | Configuración   | Baja        | Trivial      |
| `processor.py`                  | Base NLP        | Media       | Fácil (Mock) |
| `ollama_processor.py`           | IA Real         | Alta        | Media        |
| `connector.py`                  | Orquestación    | Media       | Media        |
| `model_generator.py`            | Transformación  | Baja        | Fácil        |
| `complexity_analyzer.py`        | Selección       | Media       | Media        |
| `problem_structure_detector.py` | Detección       | Media       | Media        |

---

## 🔧 Mantenimiento

### Agregar Nuevo Modelo LLM

1. Agregar a `NLPModelType` en `config.py`
2. Agregar configuración en `ModelConfig.DEFAULT_CONFIGS`
3. Opcional: Ajustar prompt si es necesario

### Modificar Prompt

1. Editar `PromptTemplates.OPTIMIZATION_EXTRACTION_PROMPT` en `config.py`
2. Mantener estructura JSON esperada
3. Probar con `test_ejercicios_naturales.py`

### Optimizar Performance

1. Reducir `max_tokens` en config
2. Usar modelo más pequeño (`llama3.2:3b`)
3. Ajustar `temperature` a 0.0 para más determinismo

---

## 📚 Referencias

- **Patrones de Diseño:** Factory, Adapter, Strategy
- **Principios:** SOLID, DRY, KISS
- **Testing:** Mock objects, Integration tests
- **Documentación:** Docstrings en cada función/clase

---

## 🚀 Próximas Mejoras

1. ✅ Sistema base funcional
2. ✅ Ollama integrado
3. ⏳ Cache de problemas similares
4. ⏳ API REST
5. ⏳ Interfaz web
6. ⏳ Soporte para más tipos de restricciones (>=, =)
7. ⏳ Visualización de soluciones
8. ⏳ Exportar a formato estándar (MPS, LP)
