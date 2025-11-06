# Tarjetas CRC - Simplex Solver

## ¿Qué son las Tarjetas CRC?

Las tarjetas CRC (Clase-Responsabilidad-Colaborador) son una técnica de diseño orientado a objetos que ayuda a:

- **Comprender** la arquitectura del sistema
- **Documentar** las responsabilidades de cada clase
- **Identificar** las relaciones entre componentes
- **Facilitar** la comunicación entre desarrolladores

## Estructura de las Tarjetas

Cada tarjeta CRC documenta:

### 1. **Clase**

El nombre de la clase o componente principal.

### 2. **Responsabilidades**

Lista de todas las tareas que la clase debe realizar. Cada responsabilidad debe ser específica y clara.

### 3. **Colaboradores**

Otras clases con las que esta clase interactúa para cumplir sus responsabilidades.

### 4. **Ubicación**

Ruta del archivo en el proyecto donde se encuentra la implementación.

### 5. **Tipo**

Clasificación del componente según su rol arquitectónico.

---

## Índice de Componentes

### Componentes Principales (Core)

- **[SimplexSolver](./SimplexSolver.md)** - Algoritmo Simplex para resolver problemas de programación lineal
- **[Tableau](./Tableau.md)** - Estructura de datos del tableau simplex

### Sistema NLP (Procesamiento de Lenguaje Natural)

- **[NLPOptimizationConnector](./NLPOptimizationConnector.md)** - Orquestador del flujo completo NLP → Solución
- **[OllamaNLPProcessor](./OllamaNLPProcessor.md)** - Procesador NLP usando Ollama
- **[TransformerNLPProcessor](./TransformerNLPProcessor.md)** - Procesador NLP usando modelos Transformer locales
- **[MockNLPProcessor](./MockNLPProcessor.md)** - Procesador simulado para testing
- **[ProblemStructureDetector](./ProblemStructureDetector.md)** - Detector de estructura de problemas

### Generadores de Modelos

- **[SimplexModelGenerator](./SimplexModelGenerator.md)** - Genera modelos para SimplexSolver
- **[PuLPModelGenerator](./PuLPModelGenerator.md)** - Genera modelos para PuLP
- **[ORToolsModelGenerator](./ORToolsModelGenerator.md)** - Genera modelos para OR-Tools

### Validación

- **[ModelValidator](./ModelValidator.md)** - Valida problemas de optimización extraídos por NLP
- **[InputValidator](./InputValidator.md)** - Valida entrada de usuario y archivos

### Adaptadores y Factories

- **[SimplexSolverAdapter](./SimplexSolverAdapter.md)** - Adapta SimplexSolver al sistema NLP
- **[NLPConnectorFactory](./NLPConnectorFactory.md)** - Factory para crear conectores NLP configurados

### Entrada/Salida

- **[UserInterface](./UserInterface.md)** - Interfaz de usuario en modo consola
- **[FileParser](./FileParser.md)** - Parser de archivos de problemas
- **[PDFExporter](./PDFExporter.md)** - Generador de reportes PDF

### Logging e Historial

- **[LoggingSystem](./LoggingSystem.md)** - Sistema centralizado de logging con SQLite
- **[LogViewer](./LogViewer.md)** - Visor de logs
- **[ProblemHistory](./ProblemHistory.md)** - Gestor de historial de problemas

### Sistema

- **[SystemAnalyzer](./SystemAnalyzer.md)** - Analizador de capacidades del sistema

### Clases de Datos

- **[OptimizationProblem](./OptimizationProblem.md)** - Representación estructurada de un problema de optimización
- **[NLPResult](./NLPResult.md)** - Resultado del procesamiento NLP

---

## Flujo de Componentes

### Pipeline NLP Completo

```
Usuario (texto natural)
    ↓
[NLPOptimizationConnector]
    ↓
┌─────────────────────────┐
│ 1. Procesamiento NLP    │
│   [OllamaNLPProcessor]  │ → usa → [ProblemStructureDetector]
│   ↓                     │
│   [NLPResult]           │
└─────────────────────────┘
    ↓
┌─────────────────────────┐
│ 2. Validación           │
│   [ModelValidator]      │
└─────────────────────────┘
    ↓
┌─────────────────────────┐
│ 3. Generación Modelo    │
│   [SimplexModelGenerator]
└─────────────────────────┘
    ↓
┌─────────────────────────┐
│ 4. Resolución           │
│   [SimplexSolverAdapter]│
│   ↓                     │
│   [SimplexSolver]       │
│   ↓                     │
│   [Tableau]             │
└─────────────────────────┘
    ↓
Solución + Metadata
```

### Pipeline Tradicional (Archivo o Interactivo)

```
Archivo .txt / Usuario interactivo
    ↓
[FileParser] / [UserInterface]
    ↓
[InputValidator]
    ↓
[SimplexSolver]
    ↓
[Tableau]
    ↓
Solución
    ↓
[PDFExporter] (opcional)
```

---

## Patrones de Diseño Utilizados

### Factory Pattern

- `NLPConnectorFactory` - Crea conectores NLP completos con todos sus componentes

### Adapter Pattern

- `SimplexSolverAdapter` - Adapta la interfaz de SimplexSolver al sistema NLP

### Strategy Pattern

- `INLPProcessor` - Diferentes estrategias de procesamiento NLP (Ollama, Transformer, Mock)
- `IModelGenerator` - Diferentes estrategias de generación de modelos (Simplex, PuLP, OR-Tools)

### Singleton Pattern

- `LoggingSystem` - Instancia única del sistema de logging

### Template Method Pattern

- `SimplexSolver._solve_phase()` - Template para Fase 1 y Fase 2

### Facade Pattern

- `NLPOptimizationConnector` - Fachada que simplifica el uso del sistema NLP completo

---

## Guía de Lectura

### Para nuevos desarrolladores:

1. Comienza con **[NLPOptimizationConnector](./NLPOptimizationConnector.md)** para entender el flujo general
2. Revisa **[SimplexSolver](./SimplexSolver.md)** para el algoritmo núcleo
3. Explora los procesadores NLP según tu interés

### Para entender el algoritmo Simplex:

1. **[SimplexSolver](./SimplexSolver.md)** - Lógica del algoritmo
2. **[Tableau](./Tableau.md)** - Estructura de datos y operaciones

### Para trabajar con NLP:

1. **[NLPOptimizationConnector](./NLPOptimizationConnector.md)** - Orquestador principal
2. **[OllamaNLPProcessor](./OllamaNLPProcessor.md)** - Procesamiento con Ollama
3. **[ProblemStructureDetector](./ProblemStructureDetector.md)** - Detección de estructura

### Para debugging:

1. **[LoggingSystem](./LoggingSystem.md)** - Sistema de logs
2. **[LogViewer](./LogViewer.md)** - Visualización de logs

---

## Convenciones

- **Negrita**: Nombres de clases y componentes clave
- `Código`: Referencias a código, métodos y archivos
- → : Relación de uso o flujo
- ↓ : Continuación de flujo
- [...] : Componente opcional

---

## Mantenimiento

Al agregar una nueva clase al sistema:

1. Crea un archivo `.md` con el nombre de la clase
2. Sigue el formato establecido (Clase, Responsabilidades, Colaboradores, Ubicación, Tipo)
3. Actualiza este README.md en la sección de Índice
4. Actualiza los diagramas de flujo si aplica
5. Revisa las tarjetas de clases colaboradoras y actualiza sus listas de colaboradores

---

## Referencias

- **Documentación general**: `GUIA_DESARROLLADOR.md` (raíz del proyecto)
- **Guía de usuario**: `GUIA_USUARIO.md` (raíz del proyecto)
- **Código fuente**: `simplex_solver/` (estructura modular)

---

_Última actualización: Noviembre 2025_
