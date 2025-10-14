# Sistema NLP Especializado con spaCy

Sistema avanzado de procesamiento de lenguaje natural usando **spaCy**, específicamente entrenado para problemas de optimización lineal. Combina Named Entity Recognition (NER), Pattern Matching y análisis lingüístico.

## 🎯 Características

- **🧠 NER Personalizado**: Modelo entrenado para reconocer entidades específicas
- **📐 Pattern Matching**: Reglas lingüísticas para patrones comunes
- **⚡ Rápido**: 10-100x más rápido que LLMs (segundos vs minutos)
- **🎯 Preciso**: Entiende contexto y relaciones semánticas
- **📚 Aprendizaje**: Mejora con ejemplos anotados
- **🔄 Integrable**: Compatible con el sistema existente

## 📦 Componentes

### 1. `training_data.py`

Ejemplos anotados para entrenamiento:

- Problemas simples (maximizar, minimizar)
- Problemas de producción
- Problemas de transporte
- Problemas de mezcla (blending)
- Problemas multi-planta complejos
- Problemas de refinería

**40+ ejemplos anotados** con entidades como:

- `VARIABLE`: nombres de variables
- `COEFFICIENT`: coeficientes numéricos
- `OBJECTIVE_TYPE`: maximizar/minimizar
- `CONSTRAINT_OP`: operadores (<=, >=, =)
- `VALUE`: valores numéricos
- `RESOURCE`: recursos (tiempo, material, etc.)
- `PRODUCT_TYPE`: tipos de productos
- Y más...

### 2. `model_trainer.py`

Entrenador del modelo spaCy:

- Crea modelo en blanco o usa base español
- Entrena con ejemplos anotados
- Guarda modelo entrenado
- Evalúa precisión
- Visualiza entidades

### 3. `entity_recognizer.py`

Reconocedor de entidades:

- Carga modelo entrenado
- Extrae entidades por tipo
- Detecta variables, coeficientes, restricciones
- Post-procesa y valida

### 4. `pattern_matcher.py`

Matcher de patrones:

- Patrones lingüísticos con Matcher
- Frases clave con PhraseMatcher
- Expresiones regulares
- Extracción de restricciones completas
- Identificación de secciones del problema

### 5. `spacy_processor.py`

Procesador principal:

- Combina NER + Pattern Matching
- Extrae problema estructurado
- Implementa `INLPProcessor`
- Integración con solver

## 🚀 Instalación

```bash
# Instalar spaCy
pip install spacy

# Descargar modelo base español
python -m spacy download es_core_news_sm

# O modelo más completo
python -m spacy download es_core_news_md
```

## 📚 Entrenamiento

### Opción 1: Entrenamiento Rápido

```bash
cd src/spacy_nlp
python train_model.py
```

Esto:

1. Genera ejemplos de entrenamiento
2. Entrena modelo NER (30 iteraciones)
3. Guarda modelo en `models/optimization_ner`
4. Prueba con ejemplos

### Opción 2: Entrenamiento Personalizado

```python
from spacy_nlp.training_data import TrainingDataGenerator
from spacy_nlp.model_trainer import SpacyModelTrainer

# Generar datos
generator = TrainingDataGenerator()
training_data = generator.get_training_data()
labels = generator.get_labels()

# Crear y entrenar
trainer = SpacyModelTrainer()
trainer.create_blank_model(labels)
trainer.train(training_data, n_iter=50)  # Más iteraciones = mejor

# Guardar
trainer.save_model("my_custom_model")
```

### Agregar Ejemplos Propios

```python
from spacy_nlp.training_data import ProblemAnnotator

annotator = ProblemAnnotator()

# Anotar texto
text = "Maximizar Z = 5x + 3y"
entities = [
    (0, 9, "OBJECTIVE_TYPE"),   # Maximizar
    (10, 11, "OBJ_VAR"),         # Z
    (14, 15, "COEFFICIENT"),     # 5
    (15, 16, "VARIABLE"),        # x
    (19, 20, "COEFFICIENT"),     # 3
    (20, 21, "VARIABLE"),        # y
]

annotation = annotator.annotate_text(text, entities)
annotator.display_annotated_text(text, entities)
```

## 🧪 Testing

### Test Completo

```bash
cd src/spacy_nlp
python test_spacy.py
```

Incluye tests de:

- Problema simple
- Problema de producción
- Problema multi-planta complejo
- Problema de refinería
- Integración con solver
- Pattern matcher solo

### Uso Programático

```python
from spacy_nlp import SpacyNLPProcessor

# Con modelo entrenado
processor = SpacyNLPProcessor(model_path="models/optimization_ner")

# O sin modelo (solo patterns)
processor = SpacyNLPProcessor()

# Procesar texto
problema = """
Maximizar Z = 3x + 2y
Sujeto a:
2x + y <= 100
x + 2y <= 80
"""

result = processor.process_text(problema)

if result.success:
    print(f"Variables: {result.problem.variable_names}")
    print(f"Coeficientes: {result.problem.objective_coefficients}")
```

### Análisis Detallado

```python
# Ver análisis completo
processor.display_analysis(problema)

# O programáticamente
analysis = processor.analyze_text(problema)
print(f"Entidades: {analysis['n_entities']}")
print(f"Patrones: {analysis['n_patterns']}")
print(f"Restricciones: {analysis['n_constraints']}")
```

## 🔄 Integración con Sistema Existente

### Con Solver

```python
from spacy_nlp import SpacyNLPProcessor
from nlp.connector import NLPOptimizationConnector
from nlp.model_generator import SimplexModelGenerator, ModelValidator
from nlp.connector import SimplexSolverAdapter

# Crear procesador spaCy
processor = SpacyNLPProcessor(model_path="models/optimization_ner")

# Integrar con sistema completo
connector = NLPOptimizationConnector(
    nlp_processor=processor,
    model_generator=SimplexModelGenerator(),
    solver=SimplexSolverAdapter(),
    validator=ModelValidator()
)

# Resolver
resultado = connector.process_and_solve(problema)
```

### En test_solver.py

```python
# Modificar test_solver.py para usar spaCy
from spacy_nlp import SpacyNLPProcessor

# En vez de OllamaNLPProcessor
conector = NLPConnectorFactory.create_connector(
    nlp_model_type=NLPModelType.LLAMA3_1_8B,  # Se ignora
    use_mock_nlp=False
)

# Reemplazar processor manualmente
from spacy_nlp import SpacyNLPProcessor
conector.nlp_processor = SpacyNLPProcessor()
```

## 📊 Comparación

| Aspecto           | spaCy NER       | Pattern Matching | Regex      | LLM             |
| ----------------- | --------------- | ---------------- | ---------- | --------------- |
| **Velocidad**     | ⚡⚡ 1-2s       | ⚡⚡⚡ <1s       | ⚡⚡⚡ <1s | 🐌 300s+        |
| **Flexibilidad**  | 🟢🟢🟢 Alta     | 🟡🟡 Media       | 🟡 Baja    | 🟢🟢🟢 Muy Alta |
| **Contexto**      | 🟢🟢🟢 Entiende | 🟢🟢 Parcial     | 🔴 No      | 🟢🟢🟢 Entiende |
| **Entrenamiento** | ⚠️ Requiere     | ✅ No            | ✅ No      | ⚠️ Complejo     |
| **Recursos**      | 💚 Bajo         | 💚 Mínimo        | 💚 Mínimo  | 🔴 Alto (GPU)   |
| **Tamaño Modelo** | 💚 ~500MB       | -                | -          | 🔴 8GB+         |

## 💡 Cuándo Usar Cada Sistema

### spaCy NER (Recomendado)

- ✅ Problemas con variaciones lingüísticas
- ✅ Texto semi-estructurado
- ✅ Necesitas entender contexto
- ✅ Puedes entrenar con ejemplos
- ✅ Balance velocidad/precisión

### Pattern Matching (Fallback)

- ✅ Sin modelo entrenado disponible
- ✅ Patrones muy específicos
- ✅ Máxima velocidad
- ✅ Complemento a NER

### Regex

- ✅ Formato muy estándar
- ✅ Testing rápido
- ✅ No necesitas NLP

### LLM

- ✅ Lenguaje muy natural/informal
- ✅ Ambigüedad compleja
- ✅ No puedes entrenar spaCy

## 📈 Ejemplos de Entrenamiento

### Problema Simple

```python
("Maximizar Z = 3x + 2y", {
    "entities": [
        (0, 9, "OBJECTIVE_TYPE"),
        (10, 11, "OBJ_VAR"),
        (14, 15, "COEFFICIENT"),
        (15, 16, "VARIABLE"),
        (19, 20, "COEFFICIENT"),
        (20, 21, "VARIABLE"),
    ]
})
```

### Problema Complejo

```python
("La planta 1 tiene capacidad para producir 750 unidades diarias", {
    "entities": [
        (3, 11, "LOCATION"),      # planta 1
        (20, 29, "RESOURCE"),     # capacidad
        (39, 42, "VALUE"),        # 750
        (43, 51, "UNIT"),         # unidades
        (52, 59, "TIME_UNIT"),    # diarias
    ]
})
```

## 🔧 Personalización

### Agregar Nueva Etiqueta

```python
# En training_data.py, agregar ejemplos con nueva etiqueta
("Texto con nueva entidad", {
    "entities": [(start, end, "NUEVA_ETIQUETA")]
})

# Re-entrenar modelo
python train_model.py
```

### Agregar Patrón Nuevo

```python
# En pattern_matcher.py
pattern_nuevo = [
    {"LOWER": "palabra"},
    {"IS_DIGIT": True},
    {"TEXT": "clave"},
]
self.matcher.add("NUEVO_PATRON", [pattern_nuevo])
```

## 📁 Estructura

```
src/spacy_nlp/
├── __init__.py                 # Exportaciones
├── training_data.py            # 40+ ejemplos anotados
├── model_trainer.py            # Entrenamiento
├── entity_recognizer.py        # NER
├── pattern_matcher.py          # Patterns
├── spacy_processor.py          # Procesador principal
├── train_model.py              # Script entrenamiento
├── test_spacy.py               # Tests completos
└── README.md                   # Esta documentación
```

## 🎓 Etiquetas NER

| Etiqueta            | Descripción           | Ejemplo                   |
| ------------------- | --------------------- | ------------------------- |
| `VARIABLE`          | Variables de decisión | x, y, x1, producto_A      |
| `COEFFICIENT`       | Coeficientes          | 3, 2.5, -4                |
| `OBJECTIVE_TYPE`    | Tipo de objetivo      | maximizar, minimizar      |
| `OBJECTIVE_CONCEPT` | Concepto objetivo     | ganancia, costo           |
| `CONSTRAINT_OP`     | Operador              | <=, >=, =                 |
| `CONSTRAINT_INTRO`  | Intro restricción     | sujeto a, tal que         |
| `VALUE`             | Valor numérico        | 100, 50.5                 |
| `UNIT`              | Unidad de medida      | dólares, horas, barriles  |
| `RESOURCE`          | Recurso               | tiempo, material, espacio |
| `LOCATION`          | Ubicación             | planta 1, almacén A       |
| `PRODUCT_TYPE`      | Tipo producto         | silla, mesa, gas1         |
| `SIZE`              | Tamaño                | grande, mediano, chico    |
| `PROPERTY`          | Propiedad             | NP, PV, capacidad         |

## 🐛 Troubleshooting

### Modelo no encontrado

```bash
python -m spacy download es_core_news_sm
```

### Error en entrenamiento

- Verificar que las anotaciones no se solapen
- Validar formato de datos

### Baja precisión

- Agregar más ejemplos de entrenamiento
- Aumentar iteraciones (n_iter)
- Usar modelo base más grande (es_core_news_md)

## 📚 Referencias

- [spaCy Documentation](https://spacy.io/)
- [Training Custom NER](https://spacy.io/usage/training)
- [Pattern Matching](https://spacy.io/usage/rule-based-matching)

## 🎉 Ventajas Clave

1. **⚡ Rápido**: 1-2 segundos vs 5+ minutos de LLM
2. **🎯 Preciso**: Entiende contexto lingüístico
3. **📚 Aprende**: Mejora con más ejemplos
4. **💚 Eficiente**: Sin GPU, ~500MB modelo
5. **🔄 Flexible**: Funciona sin modelo (patterns) o con modelo (NER)
6. **🛠️ Personalizable**: Fácil agregar etiquetas y patrones
7. **🧪 Testeable**: Sistema robusto y determinista

¡Empieza ahora mismo sin esperar descargas de LLMs! 🚀
