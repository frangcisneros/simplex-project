# Tarjeta CRC: TransformerNLPProcessor

### Clase: TransformerNLPProcessor

**Responsabilidades:**

- Procesar texto usando modelos Transformer locales
- Cargar modelos de HuggingFace (FLAN-T5, T5, etc.)
- Verificar disponibilidad del modelo y recursos del sistema
- Generar respuestas usando pipeline de texto a texto
- Extraer problemas de optimización de respuestas JSON
- Parsear JSON con manejo de errores robusto
- Calcular score de confianza basado en calidad de respuesta
- Gestionar configuración de temperatura y tokens
- Manejar errores de carga y generación del modelo
- Validar estructura mínima del problema extraído

**Colaboradores:**

- `INLPProcessor` - Interfaz base que implementa
- `OptimizationProblem` - Objeto de resultado estructurado
- `NLPResult` - Encapsula resultado del procesamiento
- `ModelConfig` - Configuración del modelo
- `transformers` - Librería de HuggingFace

**Ubicación:** `simplex_solver/nlp/processor.py`

**Tipo:** Procesador de modelos locales (Local Model Processor)
