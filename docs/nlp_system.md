# Sistema NLP para Programación Lineal

## Descripción

Este sistema integra capacidades de Procesamiento de Lenguaje Natural (NLP) con el solver Simplex existente, permitiendo resolver problemas de optimización descritos en lenguaje natural.

## Arquitectura

El sistema sigue los principios SOLID y utiliza patrones de diseño para mantener bajo acoplamiento:

### Estructura del Proyecto

El sistema NLP está completamente organizado en `src/nlp/`:

```
src/
├── nlp/                    # 🆕 Carpeta dedicada al sistema NLP
│   ├── __init__.py        # Exporta todas las clases públicas
│   ├── interfaces.py      # Interfaces y abstracciones SOLID
│   ├── config.py          # Configuración de modelos y constantes
│   ├── processor.py       # Procesadores NLP (Transformer, Mock)
│   ├── model_generator.py # Generadores de modelos (Simplex, PuLP, OR-Tools)
│   └── connector.py       # Conectores y orchestradores
├── solver.py              # Solver Simplex original (sin modificar)
└── ...
```

### Componentes Principales

1. **INLPProcessor** (`nlp/interfaces.py`): Interfaz para procesadores de lenguaje natural

   - `TransformerNLPProcessor` (`nlp/processor.py`): FLAN-T5, Mistral, etc.
   - `MockNLPProcessor` (`nlp/processor.py`): Implementación mock para testing

2. **IModelGenerator** (`nlp/interfaces.py`): Interfaz para generadores de modelos

   - `SimplexModelGenerator` (`nlp/model_generator.py`): Formato SimplexSolver
   - `PuLPModelGenerator` (`nlp/model_generator.py`): Formato PuLP (opcional)
   - `ORToolsModelGenerator` (`nlp/model_generator.py`): Formato OR-Tools (opcional)

3. **IOptimizationSolver** (`nlp/interfaces.py`): Interfaz para solvers

   - `SimplexSolverAdapter` (`nlp/connector.py`): Adapta el SimplexSolver existente

4. **INLPConnector** (`nlp/interfaces.py`): Interfaz para conectores del pipeline completo

   - `NLPOptimizationConnector` (`nlp/connector.py`): Orquesta todo el proceso

5. **IModelValidator** (`nlp/interfaces.py`): Valida problemas extraídos por NLP
   - `ModelValidator` (`nlp/model_generator.py`): Validación de problemas

### Principios SOLID Aplicados

- **SRP**: Cada clase tiene una única responsabilidad
- **OCP**: Extensible sin modificar código existente
- **LSP**: Implementaciones intercambiables mediante interfaces
- **ISP**: Interfaces específicas y cohesivas
- **DIP**: Dependencia de abstracciones, no concreciones

## Instalación

1. Instalar dependencias:

```bash
pip install -r requirements.txt
```

2. Para usar modelos locales, asegurar que tenga suficiente RAM y espacio en disco:
   - FLAN-T5-small: ~1GB RAM
   - FLAN-T5-base: ~3GB RAM
   - Mistral-7B: ~14GB RAM (con quantización 4-bit: ~4GB)

## Uso

### Modo NLP con texto directo

```bash
python nlp_simplex.py --nlp --text "Maximizar 3x + 2y sujeto a x + y <= 4 y 2x + y <= 6"
```

### Modo NLP con archivo

```bash
python nlp_simplex.py --nlp --file ejemplos/nlp/problema_produccion_simple.txt
```

### Modo NLP interactivo

```bash
python nlp_simplex.py --nlp
```

### Usar modelo específico

```bash
python nlp_simplex.py --nlp --model t5-base --text "..."
```

### Modo de prueba (mock NLP)

```bash
python nlp_simplex.py --nlp --mock --text "cualquier texto"
```

### Modo tradicional (sin cambios)

```bash
python nlp_simplex.py ejemplos/maximizar_basico.txt
```

## Ejemplos de Problemas NLP

### Problema de Producción

```
Una empresa produce dos productos A y B.
A genera 3 unidades de ganancia, B genera 2 unidades.
Maximizar ganancias sujeto a:
- A + B <= 4 (capacidad)
- 2A + B <= 6 (recursos)
```

### Problema de Transporte

```
Minimizar costos de envío en 3 rutas.
Ruta 1 cuesta 5 por unidad, ruta 2 cuesta 3, ruta 3 cuesta 4.
Restricciones:
- Enviar al menos 10 unidades total
- Ruta 1 máximo 8 unidades
- Ruta 2 máximo 6 unidades
```

## API Programática

### Uso Básico

```python
# 🆕 Importación simplificada desde el paquete nlp
from nlp import NLPConnectorFactory, SolverType, NLPModelType

# Crear conector
connector = NLPConnectorFactory.create_connector(
    nlp_model_type=NLPModelType.FLAN_T5_SMALL,
    solver_type=SolverType.SIMPLEX,
    use_mock_nlp=False  # True para testing
)

# Procesar problema
result = connector.process_and_solve(
    "Maximizar 2x + 3y sujeto a x + y <= 10"
)

if result['success']:
    print("Solución:", result['solution'])
else:
    print("Error:", result['error'])
```

### Uso Avanzado con Configuración

```python
# 🆕 Importación simplificada
from nlp import ConfigurableNLPConnector, NLPModelType, SolverType

connector = ConfigurableNLPConnector()

# Configurar conector
success = connector.configure(
    nlp_model_type=NLPModelType.MISTRAL_7B,
    solver_type=SolverType.SIMPLEX,
    use_mock_nlp=False,
    custom_config={
        'temperature': 0.5,
        'max_length': 1024
    }
)

if success:
    result = connector.process_and_solve(problem_text)
```

## Testing

Ejecutar tests:

```bash
python -m pytest tests/ -v
```

O ejecutar directamente:

```bash
python tests/test_nlp_system.py
```

## Arquitectura de Microservicio

El sistema está diseñado como si fuera un microservicio:

1. **Bajo Acoplamiento**: Componentes intercambiables vía interfaces
2. **Alta Cohesión**: Cada componente tiene responsabilidad específica
3. **Conector Adaptable**: Fácil cambio de lógica principal o NLP
4. **Configuración Flexible**: Múltiples modelos y configuraciones
5. **Monitoreo**: Health checks y logging detallado

### Cambiar Componentes

Para cambiar el procesador NLP:

```python
# Implementar nueva clase
class CustomNLPProcessor(INLPProcessor):
    def process_text(self, text: str) -> NLPResult:
        # Lógica personalizada
        pass

# Usar en conector
connector = NLPOptimizationConnector(
    nlp_processor=CustomNLPProcessor(),
    model_generator=SimplexModelGenerator(),
    solver=SimplexSolverAdapter(),
    validator=ModelValidator()
)
```

Para cambiar el solver:

```python
class CustomSolver(IOptimizationSolver):
    def solve(self, model: Dict[str, Any]) -> Dict[str, Any]:
        # Lógica de solver personalizada
        pass
```

## Modelos NLP Soportados

### FLAN-T5 (Recomendado para empezar)

- **t5-small**: Rápido, menor precisión, ~1GB RAM
- **t5-base**: Balance velocidad/precisión, ~3GB RAM

### Mistral 7B (Mayor calidad)

- Mejor comprensión de lenguaje natural
- Requiere ~4GB RAM con quantización
- Más lento pero más preciso

### Extensiones Futuras

- Support para LLaMA 2
- Modelos fine-tuneados específicos para optimización
- Cache de resultados NLP
- Procesamiento batch

## Troubleshooting

### Error: "transformers library not available"

```bash
pip install torch transformers accelerate
```

### Error: "CUDA not available"

- Normal si no tiene GPU NVIDIA
- El sistema automáticamente usa CPU
- Para GPU: instalar `torch` con soporte CUDA

### Error: "Model not loading"

- Verificar memoria disponible
- Usar modelo más pequeño (t5-small)
- Activar modo mock: `--mock-nlp`

### Error de memoria con modelos grandes

```python
# Usar quantización
custom_config = {
    'load_in_4bit': True,  # Reduce memoria
    'device_map': 'auto'
}
```

## Logging

El sistema incluye logging detallado:

```bash
# Modo verboso
python nlp_simplex.py --nlp --verbose --text "..."

# En código
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Contribución

Para agregar nuevos componentes:

1. Implementar interfaces correspondientes
2. Agregar tests unitarios
3. Documentar configuración
4. Actualizar factory si necesario

El diseño modular facilita extensiones sin modificar código existente.
