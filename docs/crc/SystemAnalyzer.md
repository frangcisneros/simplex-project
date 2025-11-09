# Tarjeta CRC: SystemAnalyzer

### Clase: SystemAnalyzer

**Responsabilidades:**

- Analizar capacidades del sistema (CPU, RAM, Ollama)
- Detectar disponibilidad de Ollama y modelos instalados
- Obtener información de hardware (cores, memoria)
- Proporcionar recomendaciones de modelo según capacidades del sistema
- Clasificar complejidad del problema (simple, medium, complex)
- Sugerir modelos apropiados según complejidad y recursos
- Verificar requisitos mínimos para ejecutar modelos NLP
- Generar reporte de capacidades del sistema

**Colaboradores:**

- `SystemCapabilities` - Clase de datos para capacidades
- `ModelRecommendation` - Clase de datos para recomendaciones
- `psutil` - Información del sistema
- `requests` - Comunicación con Ollama

**Ubicación:** `simplex_solver/system_analyzer.py`

**Tipo:** Analizador de sistema (System Analyzer)
