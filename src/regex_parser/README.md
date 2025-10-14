# Sistema de Parsing con Expresiones Regulares

Sistema completo de parsing para problemas de optimización lineal usando **solo expresiones regulares**, sin necesidad de modelos de lenguaje.

## 🎯 Características

- **⚡ Instantáneo**: Sin latencia de modelos LLM
- **🎯 Determinista**: Resultados predecibles y consistentes
- **💪 Robusto**: No requiere GPU, servidor externo o modelos grandes
- **🔧 Flexible**: Soporta múltiples formatos y convenciones
- **🔄 Integrable**: Compatible con la interfaz INLPProcessor

## 📦 Componentes

### 1. `pattern_library.py`

Biblioteca centralizada de patrones regex:

- Variables (simples, con subíndices, descriptivas)
- Números (enteros, decimales, fracciones)
- Operadores matemáticos
- Palabras clave de contexto

### 2. `variable_detector.py`

Detecta y normaliza variables:

- `x1, x2, x_3` (con subíndices)
- `producto_A, tiempo_max` (descriptivas)
- `x, y, z` (simples)
- Infiere rangos automáticamente

### 3. `objective_parser.py`

Extrae función objetivo:

- Tipo (maximizar/minimizar)
- Coeficientes de cada variable
- Términos constantes

### 4. `constraint_parser.py`

Parsea restricciones:

- Coeficientes por variable
- Operadores (`<=`, `>=`, `=`)
- Valores RHS
- Conversión a forma estándar

### 5. `regex_extractor.py`

Coordina toda la extracción:

- Orquesta todos los parsers
- Valida coherencia
- Calcula confianza

### 6. `regex_processor.py`

Procesador principal:

- **RegexOptimizationProcessor**: Solo regex
- **HybridProcessor**: Regex + LLM fallback

## 🚀 Uso Rápido

### Opción 1: Procesador Standalone

```python
from regex_parser import RegexOptimizationProcessor

processor = RegexOptimizationProcessor()

problem_text = """
Maximizar Z = 3x + 2y
Sujeto a:
2x + y <= 100
x + 2y <= 80
x, y >= 0
"""

result = processor.process_text(problem_text)

if result.success:
    print(f"Variables: {result.problem.variable_names}")
    print(f"Coeficientes: {result.problem.objective_coefficients}")
    print(f"Restricciones: {len(result.problem.constraints)}")
```

### Opción 2: Integrado con el Sistema NLP

```python
from nlp import NLPConnectorFactory, SolverType
from regex_parser import RegexOptimizationProcessor

# Crear conector usando regex en vez de LLM
connector = NLPConnectorFactory.create_connector(
    solver_type=SolverType.SIMPLEX,
    use_mock_nlp=False  # Puedes modificar el factory para aceptar regex_processor
)

# O usar directamente
from nlp.connector import NLPOptimizationConnector
from nlp.model_generator import SimplexModelGenerator, ModelValidator
from solver import SimplexSolver

processor = RegexOptimizationProcessor()
connector = NLPOptimizationConnector(
    nlp_processor=processor,
    model_generator=SimplexModelGenerator(),
    solver=SimplexSolver(),
    validator=ModelValidator()
)

result = connector.process_and_solve(problem_text)
```

### Opción 3: Procesador Híbrido (Regex + LLM)

```python
from regex_parser import HybridProcessor
from nlp.ollama_processor import OllamaNLPProcessor
from nlp.config import NLPModelType

# Regex primero, LLM como fallback
llm_processor = OllamaNLPProcessor(NLPModelType.LLAMA3_1_8B)
hybrid = HybridProcessor(llm_processor, confidence_threshold=0.8)

result = hybrid.process_text(problem_text)
# Usa regex si confianza >= 0.8, sino usa LLM
```

## 📝 Formatos Soportados

### Variables

```
x, y, z                          # Simples
x1, x2, x_3, y12                 # Con subíndices
producto_A, tiempo_max           # Descriptivas
```

### Función Objetivo

```
Maximizar Z = 3x + 2y
max: 5x1 - 2x2 + x3
Minimizar costo = 100*A + 80*B
min 4x + 3y - 5
```

### Restricciones

```
2x + 3y <= 100
x1 + 2x2 >= 50
3x = 45
x, y >= 0
```

### Secciones de Restricciones

```
Sujeto a:
Tal que:
s.t.
Restricciones:
Constraints:
Subject to:
```

## 🧪 Testing

Ejecutar todos los tests:

```bash
cd src/regex_parser
python test_regex_parser.py
```

Tests incluidos:

1. ✅ Problema simple
2. ✅ Problema de producción
3. ✅ Variables con subíndices
4. ✅ Componentes individuales
5. ✅ Formato de salida
6. ✅ Biblioteca de patrones

## 📊 Comparación: Regex vs LLM

| Característica | Regex                   | LLM                       |
| -------------- | ----------------------- | ------------------------- |
| Velocidad      | ⚡ Instantáneo (<1ms)   | 🐌 Lento (5-30s)          |
| Recursos       | 💚 Mínimos              | 🔴 GPU/RAM alta           |
| Flexibilidad   | 🟡 Formato estructurado | 🟢 Lenguaje natural libre |
| Ambigüedad     | 🔴 No maneja            | 🟢 Maneja bien            |
| Confiabilidad  | 🟢 Determinista         | 🟡 Probabilística         |
| Setup          | 🟢 Ninguno              | 🔴 Ollama/modelo          |

## 🎯 Cuándo Usar Cada Uno

### Usar Regex cuando:

- ✅ Problema tiene formato estándar
- ✅ Velocidad es crítica
- ✅ Recursos limitados
- ✅ Testing rápido
- ✅ Producción con alta carga

### Usar LLM cuando:

- ✅ Texto muy informal
- ✅ Ambigüedad en el problema
- ✅ Lenguaje natural complejo
- ✅ Variables no explícitas
- ✅ Formato no estándar

### Usar Híbrido cuando:

- ✅ Mezcla de ambos casos
- ✅ Optimización automática
- ✅ No sabes qué esperar

## 🔧 Extensión

### Agregar nuevos patrones:

```python
# En pattern_library.py
self.CUSTOM_PATTERNS = {
    "mi_patron": re.compile(r"..."),
}
```

### Crear parser personalizado:

```python
from regex_parser import ConstraintParser

class MyCustomParser(ConstraintParser):
    def parse_special_constraint(self, text):
        # Tu lógica aquí
        pass
```

## 📈 Ejemplos de Casos de Uso

### 1. Sistema de Producción

```python
problem = """
Maximizar beneficio = 50*silla + 40*mesa
Restricciones:
3*silla + 5*mesa <= 150  (horas)
2*silla + 4*mesa <= 100  (material)
silla, mesa >= 0
"""
```

### 2. Transporte

```python
problem = """
Minimizar costo = 10*ruta1 + 15*ruta2 + 12*ruta3
s.t.
ruta1 + ruta2 >= 100
ruta2 + ruta3 >= 80
"""
```

### 3. Asignación

```python
problem = """
Maximizar Z = x1 + 2x2 + 3x3
Tal que:
x1 + x2 + x3 = 1
x1, x2, x3 >= 0
"""
```

## 🐛 Debugging

Activar logging detallado:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

Ver componentes extraídos:

```python
from regex_parser import RegexExtractor

extractor = RegexExtractor()
formatted = extractor.extract_and_format(problem_text)
print(formatted)
```

## 📄 Licencia

MIT - Usa libremente en tus proyectos

## 🤝 Contribuciones

Para agregar nuevas funcionalidades:

1. Agregar patrones en `pattern_library.py`
2. Crear parser específico si es necesario
3. Actualizar `regex_extractor.py` para usar nuevo parser
4. Agregar tests en `test_regex_parser.py`
