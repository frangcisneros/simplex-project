# Tarjeta CRC: NLPOptimizationConnector

### Clase: NLPOptimizationConnector

**Responsabilidades:**

- Orquestar el flujo completo desde texto natural hasta solución óptima
- Coordinar el procesamiento NLP del texto de entrada
- Validar que el problema extraído sea matemáticamente correcto
- Generar el modelo de optimización a partir del problema validado
- Resolver el problema usando el solver configurado
- Manejar errores en cada paso del pipeline y proporcionar información detallada
- Realizar análisis post-mortem de estructura del problema (opcional)
- Ajustar valores óptimos para problemas de minimización
- Proporcionar resultados completos con metadata (tiempo, confianza, problema extraído)

**Colaboradores:**

- `INLPProcessor` - Procesa texto natural y extrae el problema de optimización
- `IModelGenerator` - Genera modelo matemático en el formato del solver
- `IOptimizationSolver` - Resuelve el problema de optimización
- `IModelValidator` - Valida consistencia matemática del problema
- `ProblemStructureDetector` - Detecta y valida la estructura del problema
- `NLPResult` - Resultado del procesamiento NLP
- `OptimizationProblem` - Representación estructurada del problema

**Ubicación:** `simplex_solver/nlp/connector.py`

**Tipo:** Clase orquestadora (Facade/Coordinator)
