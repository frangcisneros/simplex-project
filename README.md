x1 (mesas) = 25.0 unidades

# Simplex Solver con Inteligencia Artificial

Sistema de optimización lineal que combina el algoritmo Simplex con modelos de lenguaje (Ollama) para resolver problemas de programación lineal descritos en español.

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## Características

- **IA Integrada**: Usa modelos de lenguaje (Llama 3.1, Mistral) para entender problemas en español
- **Lenguaje Natural**: Describe problemas con texto normal, sin necesidad de fórmulas matemáticas
- **Procesamiento Local**: Funciona completamente en tu computadora usando Ollama
- **Múltiples Tipos de Problemas**: Producción, transporte, dieta, mezclas, asignación de recursos

---

## Instalación

### 1. Clonar el repositorio

```bash
git clone https://github.com/frangcisneros/simplex-project
cd simplex-project
pip install -r requirements.txt
```

### 2. Instalar Ollama

Descargar desde: https://ollama.ai/download

Después de instalar:

```bash
ollama pull llama3.1:8b
```

### 3. Probar el sistema

```bash
cd tests
python test_nlp_system.py
```

---

## Ejemplo de Uso

**Entrada:**

```
Una carpintería fabrica mesas y sillas.
Cada mesa da $80 de ganancia, cada silla $50.
Hay 200 horas de trabajo disponibles.
Cada mesa requiere 4 horas, cada silla 2 horas.
¿Cuántas hacer para maximizar ganancia?
```

**Proceso:**

1. La IA identifica 2 variables (mesas, sillas)
2. Extrae la función objetivo (maximizar ganancia)
3. Detecta las restricciones (200 horas disponibles)
4. Resuelve el problema con el algoritmo Simplex

**Salida:**

```
Solución óptima encontrada
Valor óptimo: $4,000.00

Variables:
  mesas = 50.00
  sillas = 0.00
```

---

## Estructura del Proyecto

```
simplex-project/
├── README.md
├── requirements.txt
│
├── tests/
│   └── test_nlp_system.py           # Suite completa de tests
│
├── src/
│   ├── solver.py                    # Algoritmo Simplex
│   └── nlp/                         # Sistema NLP
│       ├── config.py                # Configuración
│       ├── connector.py             # Orquestador principal
│       ├── ollama_processor.py      # Procesador con Ollama
│       ├── model_generator.py       # Generador de modelos
│       ├── interfaces.py            # Interfaces
│       ├── problem_structure_detector.py  # Detector de estructura
│       └── complexity_analyzer.py   # Análisis de complejidad
│
└── ejemplos/nlp/                    # Ejemplos de problemas
```

---

## Documentación

- **ARQUITECTURA.md**: Diseño técnico del sistema
- **GUIA_IA.md**: Guía detallada de instalación y uso
- **ESTRUCTURA.md**: Organización de archivos
- **LIMPIEZA.md**: Cambios recientes

---

## Uso

### Desde Python

```python
from src.nlp import NLPConnectorFactory, NLPModelType

# Crear conector
connector = NLPConnectorFactory.create_connector(
    nlp_model_type=NLPModelType.LLAMA3_1_8B
)

# Resolver problema
resultado = connector.process_and_solve("""
    Una empresa fabrica productos A y B.
    A da $50 de ganancia, B da $40.
    Cada A requiere 2 horas, cada B 1 hora.
    Hay 100 horas disponibles.
    Maximizar ganancia.
""")

# Mostrar resultado
if resultado["success"]:
    print(f"Valor óptimo: ${resultado['solution']['optimal_value']:.2f}")
```

### Tests Incluidos

```bash
# Ejecutar suite completa de tests
cd tests
python test_nlp_system.py
```

---

## Modelos Soportados

| Modelo      | Tamaño | Precisión | Recomendado Para                  |
| ----------- | ------ | --------- | --------------------------------- |
| llama3.1:8b | 4.9 GB | Alta      | Problemas complejos (recomendado) |
| llama3.2:3b | 2.0 GB | Media     | Problemas simples                 |
| mistral:7b  | 4.0 GB | Alta      | Uso general                       |
| qwen2.5:14b | 8.0 GB | Muy Alta  | Problemas muy complejos           |

**Instalación:**

```bash
ollama pull llama3.1:8b    # Modelo por defecto
```

---

## Tipos de Problemas Soportados

- **Producción**: Maximizar ganancias con recursos limitados
- **Transporte**: Minimizar costos de distribución
- **Dieta**: Optimizar nutrición con presupuesto
- **Mezclas**: Combinar materias primas óptimamente
- **Asignación**: Distribuir recursos eficientemente

Ver ejemplos en carpeta `ejemplos/nlp/`

---

## Configuración

### Cambiar Modelo

Editar `src/nlp/config.py`:

```python
class DefaultSettings:
    DEFAULT_MODEL = NLPModelType.LLAMA3_1_8B  # Cambiar aquí
```

### Ajustar Parámetros

```python
ModelConfig.DEFAULT_CONFIGS[NLPModelType.LLAMA3_1_8B] = {
    "temperature": 0.1,  # Precisión (0-1)
    "max_tokens": 2048,
    "top_p": 0.9
}
```

---

## Solución de Problemas

### Ollama no responde

```bash
# Verificar que está corriendo
ollama list

# Instalar modelo si falta
ollama pull llama3.1:8b
```

### Modelo lento

Primera vez es normal (30-60s para cargar). Si siempre es lento, usar un modelo más pequeño:

```bash
ollama pull llama3.2:3b
```

### Error de dependencias

```bash
pip install -r requirements.txt
```

Ver GUIA_IA.md para más ayuda.

---

## Testing

```bash
# Suite completa de tests del sistema NLP
cd tests
python test_nlp_system.py
```

Los tests incluyen:

- Tests unitarios de cada componente
- Tests de integración del pipeline completo
- Tests de extremo a extremo con problemas reales
- Validación de modelos y estructuras

---

## Autor

- Francisco - [@frangcisneros](https://github.com/frangcisneros)
- Emiliana
- Marcelo
- Guillermo
- Lucia

---

## Soporte

- Documentación: ARQUITECTURA.md | GUIA_IA.md
- Issues: [GitHub Issues](https://github.com/frangcisneros/simplex-project/issues)

---

_Versión 3.0 - Octubre 2025_
