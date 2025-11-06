# Tarjeta CRC: NLPConnectorFactory

### Clase: NLPConnectorFactory

**Responsabilidades:**

- Crear conectores NLP completamente configurados
- Instanciar procesador NLP (real o mock) según configuración
- Seleccionar modelo de lenguaje apropiado (FLAN-T5, Mistral, etc.)
- Crear generador de modelos según tipo de solver (Simplex, PuLP, OR-Tools)
- Instanciar solver adapter correspondiente
- Crear validador de modelos
- Conectar todos los componentes en un NLPOptimizationConnector
- Simplificar la creación del sistema completo
- Manejar configuración personalizada del modelo NLP
- Soportar modo mock para testing

**Colaboradores:**

- `NLPOptimizationConnector` - Producto final que construye
- `OllamaNLPProcessor` - Procesador NLP real
- `MockNLPProcessor` - Procesador NLP para testing
- `SimplexModelGenerator` - Generador de modelos Simplex
- `SimplexSolverAdapter` - Adaptador del solver
- `ModelValidator` - Validador de modelos
- `NLPModelType` - Enumeración de modelos disponibles
- `SolverType` - Enumeración de solvers soportados

**Ubicación:** `simplex_solver/nlp/connector.py`

**Tipo:** Factory (Factory Pattern)
