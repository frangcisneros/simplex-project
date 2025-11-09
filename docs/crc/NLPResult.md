# Tarjeta CRC: NLPResult

### Clase: NLPResult

**Responsabilidades:**

- Encapsular resultado del procesamiento NLP
- Indicar éxito o fallo del procesamiento (success)
- Contener el problema de optimización extraído (problem)
- Almacenar score de confianza del resultado (confidence_score)
- Proporcionar mensaje de error en caso de fallo (error_message)
- Servir como contrato de comunicación entre procesador NLP y conector
- Permitir propagación de errores con información detallada

**Colaboradores:**

- `INLPProcessor` - Genera instancias de NLPResult
- `NLPOptimizationConnector` - Consume NLPResult del procesador
- `OptimizationProblem` - Contenido principal cuando success=True

**Ubicación:** `simplex_solver/nlp/interfaces.py`

**Tipo:** Clase de datos resultado (Result Data Class)
