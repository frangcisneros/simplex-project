# Arquitectura del Sistema - Vista CRC

## Diagrama de Capas

```
┌─────────────────────────────────────────────────────────────────────┐
│                        CAPA DE USUARIO                              │
│                                                                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐            │
│  │ UserInterface│  │  FileParser  │  │ ProblemHistory│            │
│  └──────────────┘  └──────────────┘  └──────────────┘            │
└─────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│                    CAPA DE VALIDACIÓN                               │
│                                                                     │
│  ┌──────────────────┐                                              │
│  │ InputValidator   │                                              │
│  └──────────────────┘                                              │
└─────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│                    CAPA DE ORQUESTACIÓN NLP                         │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │          NLPOptimizationConnector (Facade)                  │  │
│  │                                                             │  │
│  │  ┌──────────────┐   ┌──────────────┐   ┌──────────────┐   │  │
│  │  │ NLPConnector │◄──┤   Factory    │──►│ System       │   │  │
│  │  │   Factory    │   │              │   │  Analyzer    │   │  │
│  │  └──────────────┘   └──────────────┘   └──────────────┘   │  │
│  └─────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│                  CAPA DE PROCESAMIENTO NLP                          │
│                                                                     │
│  ┌────────────────────────────────────────────────────────────┐   │
│  │              INLPProcessor (Interface)                     │   │
│  │                                                            │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │   │
│  │  │   Ollama     │  │ Transformer  │  │    Mock      │    │   │
│  │  │ NLPProcessor │  │ NLPProcessor │  │ NLPProcessor │    │   │
│  │  └──────────────┘  └──────────────┘  └──────────────┘    │   │
│  │         ↓                  ↓                  ↓           │   │
│  │  ┌─────────────────────────────────────────────────┐     │   │
│  │  │    ProblemStructureDetector                     │     │   │
│  │  └─────────────────────────────────────────────────┘     │   │
│  └────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│               CAPA DE VALIDACIÓN DE MODELOS                         │
│                                                                     │
│  ┌────────────────────────────────────────────────────────────┐   │
│  │           IModelValidator (Interface)                      │   │
│  │                      ↓                                     │   │
│  │              ModelValidator                                │   │
│  └────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│               CAPA DE GENERACIÓN DE MODELOS                         │
│                                                                     │
│  ┌────────────────────────────────────────────────────────────┐   │
│  │           IModelGenerator (Interface)                      │   │
│  │                                                            │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │   │
│  │  │   Simplex    │  │     PuLP     │  │   OR-Tools   │    │   │
│  │  │Model Generator│ │Model Generator│ │Model Generator│   │   │
│  │  └──────────────┘  └──────────────┘  └──────────────┘    │   │
│  └────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│                  CAPA DE ADAPTACIÓN                                 │
│                                                                     │
│  ┌────────────────────────────────────────────────────────────┐   │
│  │      IOptimizationSolver (Interface)                       │   │
│  │                      ↓                                     │   │
│  │          SimplexSolverAdapter                              │   │
│  └────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│                    CAPA DE ALGORITMO CORE                           │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │                    SimplexSolver                            │  │
│  │                         ↓                                   │  │
│  │                     Tableau                                 │  │
│  └─────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│                  CAPA DE EXPORTACIÓN                                │
│                                                                     │
│  ┌──────────────┐                                                  │
│  │ export_to_pdf│                                                  │
│  └──────────────┘                                                  │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                  CAPA DE INFRAESTRUCTURA                            │
│              (Transversal a todas las capas)                        │
│                                                                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐            │
│  │LoggingSystem │  │  LogViewer   │  │ ProblemHistory│            │
│  │  (Singleton) │  │              │  │               │            │
│  └──────────────┘  └──────────────┘  └──────────────┘            │
└─────────────────────────────────────────────────────────────────────┘
```

## Flujo de Datos - Pipeline NLP

```
┌──────────────────────────────────────────────────────────────────┐
│                        ENTRADA                                    │
│                                                                  │
│             Texto en Lenguaje Natural                            │
│  "Una carpintería fabrica mesas y sillas. Cada mesa..."         │
└──────────────────────────────────────────────────────────────────┘
                            ↓
┌──────────────────────────────────────────────────────────────────┐
│   PASO 1: Procesamiento NLP                                      │
│   ┌────────────────────────────────────────┐                    │
│   │ OllamaNLPProcessor                     │                    │
│   │  • Detecta estructura del problema     │                    │
│   │  • Genera prompt contextual            │                    │
│   │  • Llama API de Ollama                 │                    │
│   │  • Extrae JSON de respuesta            │                    │
│   └────────────────────────────────────────┘                    │
│                     ↓                                            │
│   ┌────────────────────────────────────────┐                    │
│   │ NLPResult                              │                    │
│   │  • success: True                       │                    │
│   │  • problem: OptimizationProblem        │                    │
│   │  • confidence_score: 0.85              │                    │
│   └────────────────────────────────────────┘                    │
└──────────────────────────────────────────────────────────────────┘
                            ↓
┌──────────────────────────────────────────────────────────────────┐
│   PASO 2: Validación                                             │
│   ┌────────────────────────────────────────┐                    │
│   │ ModelValidator                         │                    │
│   │  • Valida tipo objetivo                │                    │
│   │  • Verifica dimensiones                │                    │
│   │  • Comprueba operadores                │                    │
│   │  • Valida coeficientes numéricos       │                    │
│   └────────────────────────────────────────┘                    │
│                     ↓                                            │
│             [✓] Problema válido                                  │
└──────────────────────────────────────────────────────────────────┘
                            ↓
┌──────────────────────────────────────────────────────────────────┐
│   PASO 3: Generación de Modelo                                   │
│   ┌────────────────────────────────────────┐                    │
│   │ SimplexModelGenerator                  │                    │
│   │  • Extrae coeficientes c               │                    │
│   │  • Construye matriz A                  │                    │
│   │  • Convierte restricciones a forma ≤   │                    │
│   │  • Maneja minimización                 │                    │
│   └────────────────────────────────────────┘                    │
│                     ↓                                            │
│   Model = { c: [...], A: [...], b: [...],                       │
│             constraint_types: [...], maximize: True }            │
└──────────────────────────────────────────────────────────────────┘
                            ↓
┌──────────────────────────────────────────────────────────────────┐
│   PASO 4: Resolución                                             │
│   ┌────────────────────────────────────────┐                    │
│   │ SimplexSolverAdapter                   │                    │
│   │          ↓                             │                    │
│   │ SimplexSolver                          │                    │
│   │  • Construye tableau inicial           │                    │
│   │  • Ejecuta Fase 1 (si hay artificiales)│                    │
│   │  • Ejecuta Fase 2                      │                    │
│   │  • Pivotea hasta optimalidad           │                    │
│   │          ↓                             │                    │
│   │     Tableau                            │                    │
│   └────────────────────────────────────────┘                    │
│                     ↓                                            │
│   Solution = { status: 'optimal',                                │
│                solution: {x1: 20, x2: 60},                       │
│                optimal_value: 440 }                              │
└──────────────────────────────────────────────────────────────────┘
                            ↓
┌──────────────────────────────────────────────────────────────────┐
│   PASO 5: Resultados Enriquecidos                                │
│   ┌────────────────────────────────────────┐                    │
│   │ NLPOptimizationConnector               │                    │
│   │  • Ajusta valor si era minimización    │                    │
│   │  • Agrega problema extraído            │                    │
│   │  • Incluye análisis de estructura      │                    │
│   │  • Calcula tiempo total                │                    │
│   └────────────────────────────────────────┘                    │
│                     ↓                                            │
│   Result = { success: True,                                      │
│              solution: {...},                                    │
│              extracted_problem: {...},                           │
│              nlp_confidence: 0.85,                               │
│              processing_time: 2.34,                              │
│              structure_analysis: {...} }                         │
└──────────────────────────────────────────────────────────────────┘
                            ↓
┌──────────────────────────────────────────────────────────────────┐
│                        SALIDA                                     │
│                                                                  │
│  • Solución óptima: x1 = 20, x2 = 60                            │
│  • Valor óptimo: 440                                             │
│  • Metadata del proceso completo                                │
│  • (Opcional) Exportación a PDF                                 │
└──────────────────────────────────────────────────────────────────┘
```

## Responsabilidades por Capa

### Capa de Usuario

**Responsabilidad**: Interacción con el usuario

- Recoger entrada (archivo o interactiva)
- Mostrar resultados
- Gestionar historial

### Capa de Validación de Entrada

**Responsabilidad**: Verificar corrección básica de datos

- Validar formato de entrada
- Comprobar consistencia dimensional

### Capa de Orquestación NLP

**Responsabilidad**: Coordinar el flujo completo

- Gestionar el pipeline
- Manejar errores
- Proporcionar factory para configuración

### Capa de Procesamiento NLP

**Responsabilidad**: Extraer problema de texto natural

- Analizar estructura
- Comunicarse con modelos de lenguaje
- Parsear respuestas

### Capa de Validación de Modelos

**Responsabilidad**: Validar problema extraído

- Verificar consistencia matemática
- Validar dimensiones y tipos
- Generar mensajes de error descriptivos

### Capa de Generación de Modelos

**Responsabilidad**: Transformar a formato específico del solver

- Convertir a matrices (Simplex)
- Generar objetos PuLP
- Crear modelos OR-Tools

### Capa de Adaptación

**Responsabilidad**: Conectar sistemas heterogéneos

- Adaptar interfaz de SimplexSolver
- Enriquecer resultados
- Mapear nombres de variables

### Capa de Algoritmo Core

**Responsabilidad**: Resolver problema de optimización

- Ejecutar algoritmo Simplex
- Gestionar tableau
- Realizar pivoteos

### Capa de Exportación

**Responsabilidad**: Generar reportes

- Crear PDFs profesionales
- Incluir detalles de iteraciones
- Formatear resultados

### Capa de Infraestructura

**Responsabilidad**: Servicios transversales

- Logging centralizado
- Persistencia de historial
- Visualización de logs

---

## Principios de Diseño Aplicados

### Single Responsibility Principle (SRP)

Cada clase tiene una responsabilidad única y bien definida.

**Ejemplo**: `SimplexSolver` solo implementa el algoritmo, delegando I/O a `UserInterface` y logging a `LoggingSystem`.

### Open/Closed Principle (OCP)

El sistema está abierto a extensión pero cerrado a modificación.

**Ejemplo**: Se pueden agregar nuevos procesadores NLP implementando `INLPProcessor` sin modificar el código existente.

### Liskov Substitution Principle (LSP)

Las implementaciones de interfaces son intercambiables.

**Ejemplo**: `OllamaNLPProcessor`, `TransformerNLPProcessor` y `MockNLPProcessor` son intercambiables a través de `INLPProcessor`.

### Interface Segregation Principle (ISP)

Interfaces específicas en lugar de una interfaz general.

**Ejemplo**: `INLPProcessor`, `IModelGenerator`, `IModelValidator` son interfaces separadas y específicas.

### Dependency Inversion Principle (DIP)

Dependencias en abstracciones, no en implementaciones concretas.

**Ejemplo**: `NLPOptimizationConnector` depende de interfaces (`INLPProcessor`, `IModelGenerator`) no de clases concretas.

---

_Para detalles de implementación de cada componente, consulta las tarjetas CRC individuales._
