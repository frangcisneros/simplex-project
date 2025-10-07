# 📖 Guía Completa: Sistema NLP para Simplex

> **Resuelve problemas de optimización lineal escribiendo en español**

---

## 🎯 ¿Qué es este sistema?

Este sistema te permite resolver problemas de **programación lineal** escribiéndolos en **lenguaje natural** (español). En vez de escribir matrices y vectores manualmente, describes tu problema en palabras normales y el sistema automáticamente:

1. ✅ Entiende qué quieres maximizar o minimizar
2. ✅ Identifica las restricciones y límites
3. ✅ Extrae los coeficientes numéricos
4. ✅ Construye el modelo matemático
5. ✅ Lo resuelve con el algoritmo Simplex

---

## 🚀 Instalación Rápida

### 1. Instalar Ollama (recomendado)

**Ollama** es una herramienta gratuita que ejecuta modelos de lenguaje localmente.

```bash
# Descargar e instalar desde: https://ollama.ai
# Luego instalar un modelo (recomendado: Llama 3.1)
ollama pull llama3.1:8b
```

### 2. Instalar dependencias Python

```bash
pip install -r requirements.txt
```

**Dependencias principales:**

- `requests` - Para comunicarse con Ollama
- `numpy` - Para cálculos numéricos
- `scipy` (opcional) - Solvers adicionales

---

## 📝 Uso Básico

El script ahora **detecta automáticamente** el formato del archivo, por lo que no necesitas especificar `--nlp` o `--classic`.

### Opción 1: Desde archivo (detección automática)

```bash
# El sistema detecta automáticamente si es lenguaje natural o formato clásico
python nlp_simplex.py ejemplos/nlp/problema_complejo.txt
python nlp_simplex.py ejemplos/maximizar_basico.txt
```

### Opción 2: Texto directo en línea de comando

```bash
python nlp_simplex.py --text "Maximizar 3x + 2y sujeto a x + y <= 4"
```

### Opción 3: Modo NLP explícito

```bash
# Forzar modo NLP (útil si el archivo no se detecta automáticamente)
python nlp_simplex.py --nlp --file mi_problema.txt
```

### Opción 4: Modo clásico explícito

```bash
# Forzar modo clásico (formato MAXIMIZE/MINIMIZE)
python nlp_simplex.py --classic archivo.txt
```

**¿Cómo detecta el formato?**

- ✅ Si la primera línea es `MAXIMIZE` o `MINIMIZE` → Formato clásico
- ✅ Si el archivo está en carpeta `nlp/` → Lenguaje natural
- ✅ Si la primera línea es larga (>50 caracteres) → Lenguaje natural
- ✅ Por defecto → Lenguaje natural

---

## 💡 Ejemplos de Problemas

### Ejemplo 1: Problema Simple

**Entrada:**

```
Una empresa fabrica mesas y sillas. Cada mesa genera $50 de ganancia
y cada silla $30. Hay 100 horas de carpintería disponibles.
Cada mesa requiere 4 horas y cada silla 2 horas.
Maximizar la ganancia.
```

**El sistema extrae automáticamente:**

- Variables: x1 (mesas), x2 (sillas)
- Función objetivo: Maximizar 50x1 + 30x2
- Restricción: 4x1 + 2x2 ≤ 100

**Solución:**

```
x1 = 25.0 (mesas)
x2 = 0.0 (sillas)
Ganancia máxima = $1,250
```

### Ejemplo 2: Problema Multi-Instalación

**Entrada:**

```
Una empresa tiene 2 plantas. Planta 1 puede producir max 500 unidades,
Planta 2 max 700 unidades. Producen 3 productos: A, B, C con ganancias
de $10, $15, $20 por unidad respectivamente (igual en ambas plantas).
Hay demanda máxima: producto A 300 unidades, B 400 unidades, C 600 unidades.
Maximizar ganancia.
```

**El sistema identifica:**

- Variables: x11, x12, x13 (planta 1), x21, x22, x23 (planta 2)
- Restricciones de capacidad por planta
- Restricciones de demanda por producto

### Ejemplo 3: Problema de Mezclas

**Entrada:**

```
Una refinería tiene 1000 barriles de petróleo tipo 1 y 1500 de tipo 2.
Puede venderlos directamente a $40 y $35 por barril, o mezclarlos en
gasolina premium (70% tipo1 + 30% tipo2) que se vende a $50 por barril.
Maximizar ingresos.
```

**El sistema reconoce:**

- Variables: x1 (venta tipo1), x2 (venta tipo2), x3 (mezcla)
- Restricciones de disponibilidad con proporciones

---

## 🧠 Cómo Funciona: Arquitectura

### Componentes Principales

```
┌─────────────────────────────────────────────────────────┐
│  1. PROCESADOR NLP (OllamaNLPProcessor)                 │
│     • Lee el texto en español                           │
│     • Usa modelo de lenguaje (Llama, Mistral, etc.)     │
│     • Extrae variables, restricciones y coeficientes    │
│     • Genera JSON estructurado                          │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│  2. GENERADOR DE MODELO (SimplexModelGenerator)         │
│     • Valida el JSON extraído                           │
│     • Convierte a formato matemático (c, A, b)          │
│     • Verifica consistencia de dimensiones              │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│  3. SOLVER (SimplexSolver)                              │
│     • Resuelve el problema de optimización              │
│     • Aplica el algoritmo Simplex                       │
│     • Devuelve solución óptima                          │
└─────────────────────────────────────────────────────────┘
```

### Estructura del Código

```
src/
├── nlp/                          # Sistema NLP
│   ├── __init__.py              # Exporta clases públicas
│   ├── interfaces.py            # Contratos de componentes
│   ├── config.py                # ⭐ Configuración y prompts
│   ├── ollama_processor.py     # Procesador con Ollama
│   ├── processor.py             # Procesador con Transformers
│   ├── model_generator.py       # Generadores de modelos
│   ├── connector.py             # Orquestador del sistema
│   └── complexity_analyzer.py   # Selección automática de modelos
├── solver.py                     # Algoritmo Simplex
└── ...
```

---

## 🎨 Mejora: Few-Shot Learning

### ¿Qué es Few-Shot Learning?

En lugar de entrenar el modelo desde cero, el sistema incluye **3 ejemplos concretos** en el prompt que enseñan al modelo cómo extraer información de diferentes tipos de problemas.

### Ejemplos Incluidos en el Prompt

El sistema muestra al modelo estos ejemplos antes de procesar tu problema:

1. **Ejemplo Simple** - Problema básico con 1 instalación
2. **Ejemplo Multi-Instalación** - Problema complejo con múltiples plantas
3. **Ejemplo de Mezclas** - Problema con materias primas que se combinan

### Beneficios

- ✅ **No requiere re-entrenar** el modelo
- ✅ **Mejor precisión** en problemas complejos
- ✅ **Funciona con cualquier modelo** (Mistral, Llama, Qwen)
- ✅ **Fácil de extender** - solo agregar más ejemplos

### Ubicación del Código

Los ejemplos están en: `src/nlp/config.py` → `PromptTemplates.OPTIMIZATION_EXTRACTION_PROMPT`

---

## 🤖 Modelos Disponibles

### Configuración Actual

Los modelos están configurados en `src/nlp/config.py`:

```python
class NLPModelType(Enum):
    MISTRAL_7B = "mistral:7b"      # Modelo versátil
    LLAMA3_1_8B = "llama3.1:8b"    # ⭐ RECOMENDADO - Mejor razonamiento
    QWEN2_5_14B = "qwen2.5:14b"    # Especializado en matemáticas
    LLAMA3_2_3B = "llama3.2:3b"    # Ligero pero capaz
```

### Modelo Predeterminado

```python
DEFAULT_MODEL = NLPModelType.LLAMA3_1_8B  # El mejor para problemas complejos
```

### Comparación de Modelos

| Modelo              | Tamaño | Precisión  | Velocidad  | Uso Recomendado         |
| ------------------- | ------ | ---------- | ---------- | ----------------------- |
| **Llama 3.1 8B** ⭐ | 4.7GB  | ⭐⭐⭐⭐⭐ | Media      | **Problemas complejos** |
| Mistral 7B          | 4.1GB  | ⭐⭐⭐⭐   | Rápida     | Problemas generales     |
| Qwen 2.5 14B        | 9GB    | ⭐⭐⭐⭐⭐ | Lenta      | Matemáticas avanzadas   |
| Llama 3.2 3B        | 2GB    | ⭐⭐⭐     | Muy rápida | Problemas simples       |

### Instalar Modelos en Ollama

```bash
# Modelo recomendado
ollama pull llama3.1:8b

# Otros modelos
ollama pull mistral:7b
ollama pull qwen2.5:14b
ollama pull llama3.2:3b
```

### Cambiar de Modelo

Edita `src/nlp/config.py`:

```python
DEFAULT_MODEL = NLPModelType.MISTRAL_7B  # Cambiar aquí
```

---

## 🔧 Configuración Avanzada

### Parámetros del Modelo

Ubicación: `src/nlp/config.py` → `ModelConfig.DEFAULT_CONFIGS`

```python
DEFAULT_CONFIGS = {
    NLPModelType.LLAMA3_1_8B: {
        "temperature": 0.0,      # Determinístico (0.0) vs Creativo (1.0)
        "max_tokens": 1536,      # Longitud máxima de respuesta
        "top_p": 0.9,            # Nucleus sampling
    }
}
```

**Parámetros Explicados:**

- `temperature`: 0.0 = respuestas determinísticas (ideal para JSON)
- `max_tokens`: Espacio para problemas complejos (más = mejor)
- `top_p`: Control de creatividad (0.9 = balance)

### Ajustar el Prompt

El prompt está en `src/nlp/config.py` → `PromptTemplates.OPTIMIZATION_EXTRACTION_PROMPT`

**Para agregar un nuevo ejemplo:**

1. Abre `src/nlp/config.py`
2. Busca la sección "EJEMPLOS DE APRENDIZAJE (Few-Shot)"
3. Agrega un nuevo ejemplo siguiendo el formato:

```python
EJEMPLO 4 - Tu Nuevo Tipo de Problema:
ENUNCIADO: "Descripción del problema..."

RESPUESTA CORRECTA:
{{
  "objective_type": "maximize",
  "variable_names": ["x1", "x2"],
  "objective_coefficients": [10, 20],
  "constraints": [
    {{"coefficients": [1, 2], "operator": "<=", "rhs": 100}}
  ],
  "non_negativity": true
}}
```

---

## 📂 Archivos de Ejemplo

### Ubicación: `ejemplos/nlp/`

```
ejemplos/nlp/
├── problema_simple.txt         # Problema básico de 2 variables
├── problema_complejo.txt       # Problema de 3 plantas (9 variables)
└── problema_compolejo2.txt     # Otro problema complejo
```

### Crear Tu Propio Ejemplo

1. Crea un archivo `.txt` en `ejemplos/nlp/`
2. Escribe tu problema en español natural
3. Ejecuta: `python nlp_simplex.py ejemplos/nlp/tu_archivo.txt`

**Consejos para escribir problemas:**

✅ **Sé específico con los números**

- Bueno: "Cada mesa requiere 4 horas"
- Malo: "Cada mesa requiere varias horas"

✅ **Menciona claramente el objetivo**

- Bueno: "Maximizar la ganancia total"
- Malo: "Queremos ganar más"

✅ **Define todas las restricciones**

- Incluye capacidades, demandas, disponibilidad
- Usa palabras como: "máximo", "límite", "disponible"

---

## 🐛 Solución de Problemas

### Problema: "No se pudo conectar con Ollama"

**Solución:**

```bash
# 1. Verificar que Ollama está corriendo
ollama list

# 2. Si no está corriendo, iniciarlo
ollama serve

# 3. Verificar que el modelo está instalado
ollama pull llama3.1:8b
```

### Problema: "El modelo no genera JSON válido"

**Causas comunes:**

- Temperature muy alta (debe ser 0.0)
- Problema ambiguo o mal descrito
- Modelo no adecuado para el problema

**Solución:**

```bash
# 1. Verificar configuración en src/nlp/config.py
temperature = 0.0

# 2. Probar con modelo más potente
ollama pull qwen2.5:14b

# 3. Hacer el problema más explícito
```

### Problema: "Dimensiones inconsistentes"

**Causa:** El modelo identificó mal el número de variables

**Solución:**

- Sé más explícito en la descripción
- Enumera claramente todas las variables
- Revisa los ejemplos few-shot en el prompt

### Problema: "Tiempo de espera agotado"

**Causa:** El modelo es muy lento o el problema muy complejo

**Solución:**

```python
# En src/nlp/config.py
MAX_PROCESSING_TIME = 120.0  # Aumentar tiempo (default: 60)
```

---

## 📊 Formato de Salida

### JSON Intermedio (Debug)

El sistema genera un JSON estructurado antes de resolver:

```json
{
	"objective_type": "maximize",
	"variable_names": ["x1", "x2", "x3"],
	"objective_coefficients": [420, 360, 300],
	"constraints": [
		{
			"coefficients": [1, 1, 1],
			"operator": "<=",
			"rhs": 750
		}
	],
	"non_negativity": true
}
```

### Solución Final

```
=== SOLUCIÓN ÓPTIMA ===
x1 = 250.0
x2 = 300.0
x3 = 200.0

Valor óptimo: 242,000.0
```

---

## 🎓 Casos de Uso

### 1. Problemas de Producción

```
Una fábrica produce widgets y gadgets...
```

**El sistema identifica:**

- Variables de producción por producto
- Restricciones de recursos (materias primas, tiempo, etc.)
- Función objetivo de maximización de ganancia

### 2. Problemas de Distribución

```
Una empresa tiene 3 almacenes y 5 tiendas...
```

**El sistema reconoce:**

- Variables indexadas (almacén × tienda)
- Restricciones de capacidad y demanda
- Minimización de costos de transporte

### 3. Problemas de Mezclas

```
Una planta química mezcla materias primas...
```

**El sistema entiende:**

- Variables de venta directa vs mezcla
- Proporciones en las mezclas (70%, 30%, etc.)
- Restricciones de disponibilidad

### 4. Problemas de Asignación

```
Asignar empleados a tareas minimizando tiempo...
```

**El sistema extrae:**

- Matriz de asignación (empleado × tarea)
- Restricciones de capacidad por empleado
- Minimización de tiempo/costo total

---

## 📈 Rendimiento y Limitaciones

### Casos que Funciona Bien ✅

- Problemas con hasta 50 variables
- Hasta 100 restricciones
- Problemas con estructura clara
- Coeficientes numéricos explícitos

### Casos Difíciles ⚠️

- Números no explícitos ("varios", "muchos")
- Restricciones implícitas no mencionadas
- Problemas con lógica compleja (if-then-else)
- Objetivos múltiples (requiere reformulación)

### Tiempos Aproximados

| Modelo       | Problema Simple | Problema Complejo |
| ------------ | --------------- | ----------------- |
| Llama 3.2 3B | 5-10 seg        | 15-30 seg         |
| Llama 3.1 8B | 10-20 seg       | 30-60 seg         |
| Qwen 2.5 14B | 20-40 seg       | 60-120 seg        |

_En CPU sin GPU. Con GPU sería 3-5x más rápido._

---

## 🔄 Workflow Completo

```
1. ESCRIBES el problema en español
   ↓
2. OLLAMA procesa el texto con el modelo de lenguaje
   ↓
3. SISTEMA NLP extrae variables, restricciones, coeficientes
   ↓
4. VALIDADOR verifica que el JSON sea correcto
   ↓
5. GENERADOR convierte a formato matemático (c, A, b)
   ↓
6. SIMPLEX resuelve el problema de optimización
   ↓
7. OBTIENES la solución óptima
```

---

## 💻 Comandos Útiles

### Uso básico (detección automática)

```bash
# El sistema detecta el formato automáticamente
python nlp_simplex.py ejemplos/nlp/problema_complejo.txt
```

### Uso con texto directo

```bash
python nlp_simplex.py --text "Maximizar 3x + 2y sujeto a x + y <= 4"
```

### Ver modelos instalados en Ollama

```bash
ollama list
```

### Probar un modelo directamente

```bash
ollama run llama3.1:8b
```

### Ejecutar con modo verbose (más información)

```bash
python nlp_simplex.py --verbose ejemplos/nlp/problema_complejo.txt
```

### Forzar modo NLP o clásico

```bash
# Forzar modo NLP
python nlp_simplex.py --nlp --file mi_archivo.txt

# Forzar modo clásico
python nlp_simplex.py --classic archivo.txt
```

---

## 🤝 Contribuir

### Agregar soporte para un nuevo modelo

1. Agregar a `NLPModelType` en `src/nlp/config.py`
2. Agregar configuración en `ModelConfig.DEFAULT_CONFIGS`
3. Probar con varios problemas

### Mejorar el prompt

1. Editar `PromptTemplates.OPTIMIZATION_EXTRACTION_PROMPT`
2. Agregar más ejemplos few-shot
3. Mejorar instrucciones de análisis

### Reportar problemas

- Incluir el texto del problema
- Incluir el modelo usado
- Incluir el error completo

---

## 📚 Referencias

### Documentación Técnica

- **Ollama**: https://ollama.ai
- **Few-Shot Learning**: Técnica de aprendizaje con pocos ejemplos
- **Simplex**: Algoritmo de optimización lineal

### Archivos Clave

- `src/nlp/config.py` - Configuración, modelos, prompts
- `src/nlp/ollama_processor.py` - Procesador con Ollama
- `src/nlp/connector.py` - Orquestador del sistema
- `nlp_simplex.py` - Punto de entrada principal

---

## 🎯 Resumen de Uso Rápido

```bash
# 1. Instalar Ollama
# Descargar desde https://ollama.ai

# 2. Instalar modelo
ollama pull llama3.1:8b

# 3. Instalar dependencias Python
pip install -r requirements.txt

# 4. Ejecutar con tu problema
python nlp_simplex.py ejemplos/nlp/problema_complejo.txt

# 5. ¡Listo! Obtendrás la solución óptima
```

---

## ⭐ Características Destacadas

- 🧠 **Inteligencia Artificial** - Usa modelos de lenguaje avanzados
- 🎯 **Few-Shot Learning** - Aprende de ejemplos sin re-entrenar
- 🚀 **Fácil de usar** - Solo escribe en español
- 🔧 **Configurable** - Múltiples modelos disponibles
- 📈 **Escalable** - Hasta 50 variables y 100 restricciones
- 💰 **Gratis** - Usa Ollama localmente sin costo
- 🔒 **Privado** - Todo se ejecuta en tu computadora

---

**Última actualización:** Octubre 7, 2025  
**Versión:** 2.0 con Few-Shot Learning
