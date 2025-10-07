# Simplex Solver con NLP

> **Resuelve problemas de optimización lineal escribiéndolos en español**

Este programa resuelve problemas de programación lineal usando el método Simplex. Incluye un sistema avanzado de **Procesamiento de Lenguaje Natural (NLP)** que te permite escribir problemas en español y obtener soluciones automáticamente.

---

## 🚀 Inicio Rápido

### 1. Instalar Ollama (recomendado para NLP)

```bash
# Descargar desde: https://ollama.ai
# Luego instalar un modelo
ollama pull llama3.1:8b
```

### 2. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 3. Resolver un problema

**El sistema detecta automáticamente el formato:**

```bash
# Lenguaje natural (detectado automáticamente)
python nlp_simplex.py ejemplos/nlp/problema_complejo.txt

# Formato clásico MAXIMIZE/MINIMIZE (detectado automáticamente)
python nlp_simplex.py ejemplos/maximizar_basico.txt

# O con texto directo
python nlp_simplex.py --text "Maximizar 3x + 2y sujeto a x + y <= 4"
```

---

## 📖 Documentación Completa

**Lee la guía completa para aprender todo sobre el sistema NLP:**

👉 **[GUIA_NLP.md](GUIA_NLP.md)** - Guía completa del sistema NLP

La guía incluye:

- ✅ Instalación paso a paso
- ✅ Ejemplos de uso
- ✅ Configuración de modelos
- ✅ Casos de uso complejos
- ✅ Solución de problemas
- ✅ Arquitectura del sistema

---

## 💡 Ejemplo Rápido

**Escribe en español:**

```
Una empresa fabrica mesas y sillas. Cada mesa genera $50 de ganancia
y cada silla $30. Hay 100 horas de carpintería disponibles.
Cada mesa requiere 4 horas y cada silla 2 horas.
Maximizar la ganancia.
```

**El sistema automáticamente:**

1. Identifica las variables (mesas, sillas)
2. Extrae la función objetivo (maximizar ganancia)
3. Encuentra las restricciones (horas disponibles)
4. Resuelve el problema con Simplex
5. Te muestra la solución óptima

**Resultado:**

```
x1 = 25.0 (mesas)
x2 = 0.0 (sillas)
Ganancia máxima = $1,250
```

---

## 🎯 Características Principales

- 🧠 **Inteligencia Artificial** - Usa modelos de lenguaje (Llama, Mistral, Qwen)
- 🎨 **Few-Shot Learning** - Aprende de ejemplos sin re-entrenar
- 📝 **Lenguaje Natural** - Escribe problemas en español
- 🔧 **Configurable** - Múltiples modelos disponibles
- 📈 **Escalable** - Hasta 50 variables y 100 restricciones
- 💰 **Gratis** - Usa Ollama localmente sin costo
- 🔒 **Privado** - Todo se ejecuta en tu computadora

---

## 📂 Estructura del Proyecto

```
simplex-project/
├── nlp_simplex.py              # Script principal para NLP
├── simplex.py                  # Solver clásico
├── GUIA_NLP.md                 # 📖 GUÍA COMPLETA ⭐
├── README.md                   # Este archivo
├── requirements.txt            # Dependencias
├── src/
│   ├── solver.py              # Algoritmo Simplex
│   └── nlp/                   # Sistema NLP
│       ├── config.py          # Configuración y prompts
│       ├── ollama_processor.py # Procesador con Ollama
│       ├── processor.py       # Procesador con Transformers
│       ├── model_generator.py # Generadores de modelos
│       └── connector.py       # Orquestador
└── ejemplos/
    ├── nlp/                   # Ejemplos en lenguaje natural
    │   ├── problema_simple.txt
    │   └── problema_complejo.txt
    └── *.txt                  # Ejemplos formato clásico
```

---

## 🤖 Modelos Soportados

| Modelo              | Tamaño | Precisión  | Recomendado Para        |
| ------------------- | ------ | ---------- | ----------------------- |
| **Llama 3.1 8B** ⭐ | 4.7GB  | ⭐⭐⭐⭐⭐ | **Problemas complejos** |
| Mistral 7B          | 4.1GB  | ⭐⭐⭐⭐   | Problemas generales     |
| Qwen 2.5 14B        | 9GB    | ⭐⭐⭐⭐⭐ | Matemáticas avanzadas   |
| Llama 3.2 3B        | 2GB    | ⭐⭐⭐     | Problemas simples       |

---

## 📋 Ejemplos de Uso

### Detección automática de formato

```bash
# El sistema detecta automáticamente si es lenguaje natural o formato clásico
python nlp_simplex.py ejemplos/nlp/problema_complejo.txt
python nlp_simplex.py ejemplos/maximizar_basico.txt
```

### Texto directo

```bash
python nlp_simplex.py --text "Maximizar 3x + 2y sujeto a x + y <= 4"
```

### Modo verbose (más información)

```bash
python nlp_simplex.py --verbose ejemplos/nlp/problema_complejo.txt
```

### Forzar formato específico

```bash
# Forzar NLP
python nlp_simplex.py --nlp --file mi_problema.txt

# Forzar clásico
python nlp_simplex.py --classic archivo.txt
```

---

## 🔧 Configuración

El sistema usa **Llama 3.1 8B** por defecto (mejor para problemas complejos).

Para cambiar de modelo, edita `src/nlp/config.py`:

```python
DEFAULT_MODEL = NLPModelType.MISTRAL_7B  # Cambiar aquí
```

---

## 🐛 Solución de Problemas

### "No se pudo conectar con Ollama"

```bash
# Verificar que Ollama está corriendo
ollama list

# Instalar el modelo
ollama pull llama3.1:8b
```

### Más ayuda

Consulta la **[Guía Completa](GUIA_NLP.md)** para:

- Configuración avanzada
- Solución de problemas detallada
- Ejemplos complejos
- Optimización de rendimiento

---

## 📚 Recursos

- **Guía Completa**: [GUIA_NLP.md](GUIA_NLP.md)
- **Ollama**: https://ollama.ai
- **Ejemplos**: Carpeta `ejemplos/nlp/`

---

## ⭐ Características Avanzadas

### Few-Shot Learning

El sistema incluye ejemplos integrados en el prompt que enseñan al modelo cómo extraer información de diferentes tipos de problemas:

1. Problemas simples (1 instalación, múltiples productos)
2. Problemas multi-instalación (varias plantas, varios productos)
3. Problemas de mezclas (materias primas que se combinan)

**Beneficio:** Mejor precisión sin necesidad de re-entrenar el modelo.

### Selección Automática de Modelos

El sistema puede analizar la complejidad del problema y seleccionar automáticamente el modelo más adecuado.

### Validación Automática

Verifica que el problema extraído sea matemáticamente correcto antes de intentar resolverlo.

---

## 🎓 Casos de Uso

- ✅ Problemas de producción (maximizar ganancias)
- ✅ Problemas de distribución (minimizar costos)
- ✅ Problemas de mezclas (optimizar combinaciones)
- ✅ Problemas de asignación (recursos limitados)

---

## 📞 Ayuda

Para aprender a usar el sistema completo, ver ejemplos detallados, configurar modelos, y solucionar problemas, consulta:

### 👉 [GUIA_NLP.md](GUIA_NLP.md)

---

**Última actualización:** Octubre 7, 2025  
**Versión:** 2.0 con Few-Shot Learning y NLP
