# Tarjeta CRC: OllamaNLPProcessor

### Clase: OllamaNLPProcessor

**Responsabilidades:**

- Comunicarse con la API HTTP de Ollama para procesamiento NLP
- Verificar disponibilidad del servidor Ollama y del modelo configurado
- Procesar texto en lenguaje natural y extraer problemas de optimización
- Generar prompts contextuales usando detección de estructura del problema
- Gestionar configuración del modelo (temperatura, tokens, top_p)
- Extraer y parsear respuestas JSON del modelo de lenguaje
- Limpiar errores comunes en JSON generado (comas finales, etc.)
- Calcular score de confianza basado en la calidad de la respuesta
- Manejar timeouts y errores de comunicación con Ollama
- Validar estructura mínima del problema extraído

**Colaboradores:**

- `INLPProcessor` - Interfaz base que implementa
- `ProblemStructureDetector` - Analiza estructura del problema para generar hints
- `OptimizationProblem` - Objeto de resultado estructurado
- `NLPResult` - Encapsula resultado del procesamiento
- `ModelConfig` - Configuración del modelo NLP
- `PromptTemplates` - Plantillas de prompts predefinidas
- `requests` - Comunicación HTTP con Ollama

**Ubicación:** `simplex_solver/nlp/ollama_processor.py`

**Tipo:** Procesador de integración externa (External Integration Processor)
