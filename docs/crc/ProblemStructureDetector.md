# Tarjeta CRC: ProblemStructureDetector

### Clase: ProblemStructureDetector

**Responsabilidades:**

- Analizar texto del problema para identificar su estructura
- Detectar tipo de problema (simple, multi-instalación, mezclas, dieta, transporte)
- Identificar número de plantas/instalaciones en el texto
- Identificar número de productos/tamaños/tipos
- Calcular número esperado de variables según el tipo de problema
- Extraer nombres de plantas y productos del texto
- Detectar alimentos en problemas de dieta
- Detectar rutas en problemas de transporte
- Detectar materias primas y mezclas finales en problemas de blending
- Validar variables extraídas vs estructura esperada
- Generar advertencias cuando hay discrepancias
- Proporcionar sugerencias específicas según tipo de problema

**Colaboradores:**

- `OllamaNLPProcessor` - Usa el detector para generar hints contextuales
- `NLPOptimizationConnector` - Realiza análisis post-mortem de estructura
- `re` - Expresiones regulares para parsing de texto

**Ubicación:** `simplex_solver/nlp/problem_structure_detector.py`

**Tipo:** Analizador de dominio (Domain Analyzer)
