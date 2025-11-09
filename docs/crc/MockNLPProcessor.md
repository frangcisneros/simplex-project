# Tarjeta CRC: MockNLPProcessor

### Clase: MockNLPProcessor

**Responsabilidades:**

- Proporcionar procesador NLP simulado para testing
- Retornar siempre disponibilidad positiva
- Generar problemas de optimización pre-configurados
- Crear respuestas de prueba sin llamar a modelos reales
- Facilitar pruebas unitarias y de integración
- Proporcionar problemas de ejemplo con estructura conocida
- Simular procesamiento exitoso para validación de pipeline
- Evitar dependencias de modelos NLP en tests

**Colaboradores:**

- `INLPProcessor` - Interfaz base que implementa
- `OptimizationProblem` - Genera problemas simulados
- `NLPResult` - Retorna resultados de prueba
- `NLPConnectorFactory` - Usa MockNLPProcessor en modo testing

**Ubicación:** `simplex_solver/nlp/processor.py`

**Tipo:** Mock para testing (Test Mock)
