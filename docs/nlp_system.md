# Sistema NLP para Programación Lineal

## Descripción

Este sistema permite resolver problemas de optimización escribiéndolos en lenguaje natural (español). En vez de escribir matrices y vectores manualmente, puedes describir tu problema en palabras normales y el sistema automáticamente:

1. Entiende qué quieres maximizar o minimizar
2. Identifica las restricciones y límites
3. Extrae los coeficientes numéricos
4. Construye el modelo matemático
5. Lo resuelve con el algoritmo Simplex

El sistema integra modelos de lenguaje avanzados (como FLAN-T5 y Mistral) con el solver Simplex ya existente en el proyecto.

## Arquitectura

El sistema está organizado de forma modular para que cada componente haga una cosa bien:

### Estructura del Proyecto

El sistema NLP está organizado en la carpeta `src/nlp/`:

```
src/
├── nlp/                    # Sistema de procesamiento de lenguaje natural
│   ├── __init__.py        # Exporta todas las clases públicas del paquete
│   ├── interfaces.py      # Define los contratos que deben cumplir los componentes
│   ├── config.py          # Configuración de modelos y constantes
│   ├── processor.py       # Procesadores que extraen problemas del texto
│   ├── model_generator.py # Generadores que convierten a formatos de solver
│   └── connector.py       # Conectores que orquestan todo el proceso
├── solver.py              # Solver Simplex original (no modificado)
└── ...
```

### Componentes Principales

1. **Procesadores de Lenguaje Natural** (`nlp/processor.py`)

   - `TransformerNLPProcessor`: Usa modelos como FLAN-T5 o Mistral para leer texto en español y extraer problemas de optimización
   - `MockNLPProcessor`: Versión simple para pruebas que no requiere descargar modelos grandes

2. **Generadores de Modelos** (`nlp/model_generator.py`)

   - `SimplexModelGenerator`: Convierte el problema a matrices (c, A, b) que entiende el Simplex
   - `PuLPModelGenerator`: Genera modelos para PuLP (opcional)
   - `ORToolsModelGenerator`: Genera modelos para OR-Tools de Google (opcional)

3. **Adaptadores de Solver** (`nlp/connector.py`)

   - `SimplexSolverAdapter`: Conecta el SimplexSolver original con el nuevo sistema sin modificarlo

4. **Orquestadores** (`nlp/connector.py`)

   - `NLPOptimizationConnector`: Coordina todo el proceso de principio a fin
   - `NLPConnectorFactory`: Crea fácilmente configuraciones completas del sistema

5. **Validadores** (`nlp/model_generator.py`)
   - `ModelValidator`: Verifica que el problema extraído sea matemáticamente correcto antes de intentar resolverlo

### Ventajas del Diseño

El sistema está diseñado para ser:

- **Modular**: Cada componente hace una cosa específica y se puede cambiar sin afectar a los demás
- **Extensible**: Agregar soporte para nuevos modelos NLP o solvers es simple
- **Testeable**: El MockNLPProcessor permite probar sin descargar modelos de GB
- **Flexible**: Puedes usar diferentes modelos según tus necesidades (velocidad vs precisión)
- **Robusto**: Validación en cada paso evita errores crip ticos más adelante

## Instalación

1. Instalar dependencias:

```bash
pip install -r requirements.txt
```

Las dependencias principales son:

- `torch`: Motor de deep learning para los modelos
- `transformers`: Librería de Hugging Face con los modelos de lenguaje
- `accelerate`: Para manejar modelos grandes eficientemente

2. Requisitos de memoria según el modelo:
   - **FLAN-T5 small**: ~1GB RAM (funciona en cualquier PC moderna)
   - **FLAN-T5 base**: ~3GB RAM (recomendado 8GB total en el sistema)
   - **Mistral 7B**: ~4GB RAM con quantización 4-bit (recomendado 16GB total + GPU)

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
from nlp import NLPConnectorFactory, SolverType, NLPModelType

# Crear conector con configuración por defecto
connector = NLPConnectorFactory.create_connector(
    nlp_model_type=NLPModelType.FLAN_T5_SMALL,
    solver_type=SolverType.SIMPLEX,
    use_mock_nlp=False  # True para testing sin descargar modelos
)

# Procesar y resolver un problema
result = connector.process_and_solve(
    "Maximizar 2x + 3y sujeto a x + y <= 10"
)

# Revisar resultados
if result['success']:
    print("Solución encontrada:")
    print(f"  Variables: {result['solution']}")
    print(f"  Valor objetivo: {result['solution']['objective_value']}")
    print(f"  Problema extraído: {result['extracted_problem']}")
    print(f"  Confianza del NLP: {result['nlp_confidence']}")
    print(f"  Tiempo de procesamiento: {result['processing_time']:.2f}s")
else:
    print(f"Error: {result['error']}")
    print(f"Falló en: {result['step_failed']}")
```

### Uso Avanzado con Configuración Personalizada

```python
from nlp import ConfigurableNLPConnector, NLPModelType, SolverType

connector = ConfigurableNLPConnector()

# Configurar con parámetros personalizados
success = connector.configure(
    nlp_model_type=NLPModelType.MISTRAL_7B,
    solver_type=SolverType.SIMPLEX,
    use_mock_nlp=False,
    custom_config={
        'temperature': 0.5,      # Menos aleatorio, más determinista
        'max_length': 1024,      # Respuestas más largas
        'load_in_4bit': True     # Comprimir modelo para ahorrar RAM
    }
)

if success:
    result = connector.process_and_solve(problem_text)
    print(result)
```

### Verificar Estado del Sistema

```python
# Health check de todos los componentes
health = connector.health_check()
print(f"Estado general: {health['overall_status']}")
print(f"Componentes: {health['components']}")

# Ver configuración actual
status = connector.get_status()
if status['configured']:
    print(f"Sistema listo: {status['status']}")
else:
    print("Sistema no configurado aún")
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

## Cómo Funciona Internamente

El sistema sigue un pipeline de 5 pasos:

### Paso 1: Procesamiento NLP

El texto en español se envía al modelo de lenguaje con un prompt especializado que le pide extraer:

- Tipo de objetivo (maximizar/minimizar)
- Coeficientes de la función objetivo
- Restricciones con sus coeficientes y operadores
- Nombres de variables

El modelo devuelve un JSON estructurado.

### Paso 2: Validación

El ModelValidator revisa que:

- Todos los coeficientes sean números
- Las dimensiones coincidan (misma cantidad de variables en objetivo y restricciones)
- Los operadores sean válidos (<=, >=, =)
- No haya inconsistencias lógicas

### Paso 3: Generación del Modelo

El generador convierte el problema a formato matricial:

- Vector c: coeficientes de la función objetivo
- Matriz A: coeficientes de las restricciones
- Vector b: lados derechos de las restricciones

También maneja conversiones (restricciones >= a <=, restricciones = a dos restricciones)

### Paso 4: Resolución

El SimplexSolver ejecuta el algoritmo y encuentra la solución óptima.

### Paso 5: Enriquecimiento de Resultados

Si había nombres personalizados para las variables (x11, x12 en vez de x1, x2), se mapean en la solución final.

## Extensibilidad

### Agregar un Nuevo Modelo NLP

Simplemente agrégalo a `NLPModelType` en `config.py` y define su configuración:

```python
class NLPModelType(Enum):
    MI_MODELO = "org/mi-modelo"

ModelConfig.DEFAULT_CONFIGS[NLPModelType.MI_MODELO] = {
    "max_length": 512,
    "temperature": 0.7,
    # ... otros parámetros
}
```

### Agregar un Nuevo Solver

1. Crea un generador que implemente `IModelGenerator`
2. Crea un adaptador que implemente `IOptimizationSolver`
3. Agrégalos a la factory:

```python
if solver_type == SolverType.MI_SOLVER:
    model_generator = MiSolverGenerator()
    solver = MiSolverAdapter()
```

### Crear un Procesador Personalizado

Implementa la interfaz `INLPProcessor`:

```python
class MiProcesador(INLPProcessor):
    def process_text(self, text: str) -> NLPResult:
        # Tu lógica personalizada
        pass

    def is_available(self) -> bool:
        return True
```

## Mejoras Futuras

- Soporte para modelos LLaMA 2 y otros
- Caché de problemas ya procesados (evitar reprocesar el mismo texto)
- Procesamiento batch (múltiples problemas a la vez)
- Fine-tuning de modelos específicamente para optimización
- Soporte para más idiomas además del español
- API REST para usar como servicio web
- Interfaz gráfica para usuarios no técnicos

## Contribución

Para contribuir al sistema:

1. Los componentes están organizados por responsabilidad en archivos separados
2. Cada clase tiene interfaces bien definidas
3. Agrega tests para nuevas funcionalidades
4. Documenta los nuevos componentes con docstrings claros
5. Si agregas un modelo NLP, documenta sus requerimientos de recursos

6. **Bajo Acoplamiento**: Componentes intercambiables vía interfaces
7. **Alta Cohesión**: Cada componente tiene responsabilidad específica
8. **Conector Adaptable**: Fácil cambio de lógica principal o NLP
9. **Configuración Flexible**: Múltiples modelos y configuraciones
10. **Monitoreo**: Health checks y logging detallado

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

**t5-small**: Rápido y liviano

- Usa ~1GB de RAM
- Bueno para problemas simples
- Se carga en segundos
- Ideal para probar el sistema

**t5-base**: Balance entre velocidad y calidad

- Usa ~3GB de RAM
- Mejor comprensión de problemas complejos
- Tarda un poco más en cargar

### Mistral 7B (Para máxima precisión)

- Modelo más grande y preciso
- Mejor comprensión de lenguaje natural
- Requiere ~4GB RAM con quantización 4-bit
- Más lento pero maneja problemas muy complejos
- Recomendado si tienes GPU

### Cuál elegir?

- **Empezando o probando**: FLAN-T5 small
- **Uso general**: FLAN-T5 base
- **Máxima calidad y tienes recursos**: Mistral 7B
- **Testing sin modelos**: MockNLPProcessor

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
