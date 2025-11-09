# Índice Rápido de Clases - Simplex Solver

## Tabla de Componentes

| Clase                        | Tipo                      | Ubicación                                          | Descripción Breve                                           |
| ---------------------------- | ------------------------- | -------------------------------------------------- | ----------------------------------------------------------- |
| **NLPOptimizationConnector** | Orquestador               | `simplex_solver/nlp/connector.py`                  | Orquesta el flujo completo: texto → NLP → modelo → solución |
| **SimplexSolver**            | Algoritmo                 | `simplex_solver/core/algorithm.py`                 | Implementa el algoritmo Simplex (Fase 1 y Fase 2)           |
| **OllamaNLPProcessor**       | Procesador NLP            | `simplex_solver/nlp/ollama_processor.py`           | Procesa texto usando API de Ollama                          |
| **TransformerNLPProcessor**  | Procesador NLP            | `simplex_solver/nlp/processor.py`                  | Procesa texto usando modelos Transformer locales            |
| **MockNLPProcessor**         | Mock                      | `simplex_solver/nlp/processor.py`                  | Procesador simulado para testing                            |
| **ModelValidator**           | Validador                 | `simplex_solver/nlp/model_generator.py`            | Valida problemas extraídos por NLP                          |
| **SimplexModelGenerator**    | Generador                 | `simplex_solver/nlp/model_generator.py`            | Genera modelos en formato Simplex (matrices)                |
| **PuLPModelGenerator**       | Generador                 | `simplex_solver/nlp/model_generator.py`            | Genera modelos para librería PuLP                           |
| **ORToolsModelGenerator**    | Generador                 | `simplex_solver/nlp/model_generator.py`            | Genera modelos para OR-Tools                                |
| **Tableau**                  | Estructura de Datos       | `simplex_solver/utils/tableau.py`                  | Maneja el tableau simplex y operaciones                     |
| **LoggingSystem**            | Singleton/Infraestructura | `simplex_solver/logging_system.py`                 | Sistema centralizado de logging con SQLite                  |
| **SimplexSolverAdapter**     | Adaptador                 | `simplex_solver/nlp/connector.py`                  | Adapta SimplexSolver al sistema NLP                         |
| **NLPConnectorFactory**      | Factory                   | `simplex_solver/nlp/connector.py`                  | Crea conectores NLP configurados                            |
| **ProblemStructureDetector** | Analizador                | `simplex_solver/nlp/problem_structure_detector.py` | Detecta estructura de problemas en texto                    |
| **UserInterface**            | UI                        | `simplex_solver/user_interface.py`                 | Interfaz de usuario en consola                              |
| **FileParser**               | Parser                    | `simplex_solver/file_parser.py`                    | Lee y parsea archivos de problemas                          |
| **export_to_pdf**            | Exportador                | `simplex_solver/export.py`                         | Genera reportes PDF detallados                              |
| **SystemAnalyzer**           | Analizador                | `simplex_solver/system_analyzer.py`                | Analiza capacidades del sistema                             |
| **ProblemHistory**           | Gestor                    | `simplex_solver/problem_history.py`                | Gestiona historial de problemas                             |
| **InputValidator**           | Validador                 | `simplex_solver/input_validator.py`                | Valida entrada de usuario/archivos                          |
| **LogViewer**                | Visor                     | `simplex_solver/log_viewer.py`                     | Visualiza logs del sistema                                  |
| **OptimizationProblem**      | Data Class                | `simplex_solver/nlp/interfaces.py`                 | Representación estructurada del problema                    |
| **NLPResult**                | Data Class                | `simplex_solver/nlp/interfaces.py`                 | Resultado del procesamiento NLP                             |

## Interfaces (Contratos)

| Interfaz                | Implementaciones                                                 | Propósito                               |
| ----------------------- | ---------------------------------------------------------------- | --------------------------------------- |
| **INLPProcessor**       | OllamaNLPProcessor, TransformerNLPProcessor, MockNLPProcessor    | Procesamiento de texto natural          |
| **IModelGenerator**     | SimplexModelGenerator, PuLPModelGenerator, ORToolsModelGenerator | Generación de modelos de optimización   |
| **IOptimizationSolver** | SimplexSolverAdapter                                             | Resolución de problemas de optimización |
| **IModelValidator**     | ModelValidator                                                   | Validación de problemas                 |
| **INLPConnector**       | NLPOptimizationConnector                                         | Conexión completa NLP-Solver            |

## Clasificación por Responsabilidad

### 🎯 Core (Algoritmo Principal)

- SimplexSolver
- Tableau

### 🤖 NLP (Procesamiento de Lenguaje Natural)

- NLPOptimizationConnector
- OllamaNLPProcessor
- TransformerNLPProcessor
- MockNLPProcessor
- ProblemStructureDetector

### 🏭 Generación y Transformación

- SimplexModelGenerator
- PuLPModelGenerator
- ORToolsModelGenerator

### ✅ Validación

- ModelValidator
- InputValidator

### 🔌 Integración

- SimplexSolverAdapter
- NLPConnectorFactory

### 📊 I/O (Entrada/Salida)

- UserInterface
- FileParser
- export_to_pdf

### 📝 Persistencia y Logging

- LoggingSystem
- LogViewer
- ProblemHistory

### 🔧 Sistema

- SystemAnalyzer

### 📦 Datos

- OptimizationProblem
- NLPResult

## Matriz de Dependencias Principales

| Clase                    | Depende de                                                                                     |
| ------------------------ | ---------------------------------------------------------------------------------------------- |
| NLPOptimizationConnector | INLPProcessor, IModelGenerator, IOptimizationSolver, IModelValidator, ProblemStructureDetector |
| SimplexSolver            | Tableau, LoggingSystem                                                                         |
| OllamaNLPProcessor       | ProblemStructureDetector, ModelConfig, PromptTemplates                                         |
| SimplexSolverAdapter     | SimplexSolver, LoggingSystem                                                                   |
| NLPConnectorFactory      | OllamaNLPProcessor, SimplexModelGenerator, SimplexSolverAdapter, ModelValidator                |
| FileParser               | InputValidator, LoggingSystem                                                                  |
| UserInterface            | InputValidator                                                                                 |
| export_to_pdf            | LoggingSystem (opcional)                                                                       |

## Leyenda de Tipos

- **Orquestador**: Coordina múltiples componentes para un flujo complejo
- **Algoritmo**: Implementa lógica algorítmica específica
- **Procesador**: Transforma datos de un formato a otro
- **Generador**: Crea estructuras de datos específicas
- **Validador**: Verifica correctitud de datos
- **Adaptador**: Traduce entre interfaces incompatibles
- **Factory**: Construye objetos complejos
- **Analizador**: Extrae información de datos
- **Parser**: Interpreta formato específico
- **Exportador**: Genera salida en formato específico
- **UI**: Interacción con usuario
- **Singleton**: Instancia única global
- **Data Class**: Contenedor de datos estructurados
- **Gestor**: Administra recursos o colecciones
- **Visor**: Presenta datos al usuario
- **Mock**: Simulación para testing

---

_Para más detalles sobre cada clase, consulta su tarjeta CRC individual._
