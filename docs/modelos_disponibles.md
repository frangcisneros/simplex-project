# Modelos NLP Disponibles

## ¿Por qué no funciona con problemas complejos?

Los modelos **FLAN-T5** (small/base) son muy ligeros y rápidos, pero tienen **precisión limitada** para problemas complejos con muchas variables y restricciones. Son buenos para problemas simples (2-3 variables, pocas restricciones).

Para el **problema de las 3 plantas** (9 variables, 9 restricciones) necesitas modelos más potentes.

---

## Modelos Disponibles

### 1. Modelos T5 (Ligeros - Baja/Media Precisión)

| Modelo            | Tamaño | RAM | GPU | Velocidad     | Precisión         | Uso Recomendado       |
| ----------------- | ------ | --- | --- | ------------- | ----------------- | --------------------- |
| **FLAN-T5-small** | 80MB   | 2GB | No  | ⚡ Muy rápido | ⭐⭐ Baja         | Problemas muy simples |
| **FLAN-T5-base**  | 250MB  | 4GB | No  | ⚡ Rápido     | ⭐⭐⭐ Media-baja | Problemas simples     |
| **FLAN-T5-large** | 780MB  | 6GB | No  | 🐌 Lento      | ⭐⭐⭐ Media      | Problemas medios      |

**✅ Ventajas:** Rápidos, funcionan en CPU, no requieren GPU  
**❌ Desventajas:** Baja precisión en problemas complejos  
**Resultado con problema_complejo.txt:** ❌ No funciona

---

### 2. Modelos Pequeños Potentes (Nueva Generación)

| Modelo         | Tamaño | RAM  | GPU      | Velocidad | Precisión           | Uso Recomendado                       |
| -------------- | ------ | ---- | -------- | --------- | ------------------- | ------------------------------------- |
| **Phi-3-mini** | 3.8GB  | 6GB  | Opcional | ⚡ Rápido | ⭐⭐⭐⭐ Alta       | **¡RECOMENDADO!** Problemas complejos |
| **Gemma-2B**   | 2GB    | 4GB  | Opcional | ⚡ Rápido | ⭐⭐⭐⭐ Alta       | Problemas medios-complejos            |
| **Gemma-7B**   | 7GB    | 10GB | Sí       | 🐌 Medio  | ⭐⭐⭐⭐⭐ Muy alta | Problemas muy complejos               |

**✅ Ventajas:** Excelente balance tamaño/precisión, funcionan en CPU (más lento)  
**❌ Desventajas:** Más lentos que T5, requieren más RAM  
**Resultado con problema_complejo.txt:** ✅ Probablemente funcione bien (especialmente Phi-3)

**🎯 MEJOR OPCIÓN PARA TI:** **Phi-3-mini**

- Tu sistema: 11.9GB RAM, sin GPU → Capacidad MEDIUM
- Phi-3 es pequeño (3.8GB) pero muy preciso
- Funciona en CPU (será lento pero funcionará)
- Es de Microsoft, muy bien optimizado

---

### 3. Modelos Grandes (Máxima Precisión)

| Modelo         | Tamaño | RAM  | GPU      | Velocidad | Precisión           | Uso Recomendado         |
| -------------- | ------ | ---- | -------- | --------- | ------------------- | ----------------------- |
| **Mistral-7B** | 7GB    | 16GB | Sí (8GB) | 🐌 Lento  | ⭐⭐⭐⭐⭐ Muy alta | Problemas muy complejos |
| **Llama-3-8B** | 8GB    | 16GB | Sí (8GB) | 🐌 Lento  | ⭐⭐⭐⭐⭐ Muy alta | Problemas muy complejos |

**✅ Ventajas:** Máxima precisión, pueden resolver cualquier problema  
**❌ Desventajas:** Requieren GPU potente, lentos, ocupan mucho espacio  
**Resultado con problema_complejo.txt:** ✅✅ Funcionarían perfectamente  
**⚠️ Para tu sistema:** No recomendados (requieren GPU, tú no tienes)

---

### 4. APIs (Alternativa Sin Descargar)

| Servicio           | Costo     | Velocidad     | Precisión         | Configuración   |
| ------------------ | --------- | ------------- | ----------------- | --------------- |
| **OpenAI GPT-4**   | 💰 Pago   | ⚡ Rápido     | ⭐⭐⭐⭐⭐ Máxima | API key         |
| **OpenAI GPT-3.5** | 💰 Barato | ⚡ Muy rápido | ⭐⭐⭐⭐ Alta     | API key         |
| **Ollama (local)** | 💚 Gratis | 🐌 Variable   | ⭐⭐⭐⭐ Alta     | Instalar Ollama |

**✅ Ventajas:** No descargar modelos, siempre la última versión, muy precisos  
**❌ Desventajas:** Requieren internet, algunos son de pago  
**Resultado con problema_complejo.txt:** ✅✅ Funcionarían perfectamente

**Ollama es GRATIS y local:**

```bash
# Instalar Ollama (https://ollama.ai)
ollama pull llama3
ollama pull mistral

# Luego el sistema puede usarlo automáticamente
```

---

## ¿Qué Modelo Usar Para Tu Caso?

### Tu Sistema Actual:

- RAM: 11.9GB ✅
- GPU: No ❌
- Capacidad: MEDIUM

### Recomendaciones por Prioridad:

#### 🥇 **Opción 1: Phi-3-mini** (RECOMENDADO)

```bash
# No requiere configuración adicional
# El sistema lo descargará automáticamente
python nlp_simplex.py --nlp --file ejemplos/nlp/problema_complejo.txt
```

**Pros:** Mejor balance precisión/tamaño, funcionará en tu CPU  
**Cons:** Primera vez tardará en descargar (3.8GB), procesamiento ~2-5 minutos

#### 🥈 **Opción 2: Ollama + Llama3** (Gratis, muy preciso)

```bash
# 1. Instalar Ollama desde https://ollama.ai
# 2. Descargar modelo
ollama pull llama3

# 3. Configurar el sistema para usar Ollama
# (Necesitaremos agregar soporte para Ollama - próximo paso)
```

**Pros:** Muy preciso, gratis, actualizaciones automáticas  
**Cons:** Requiere instalar software adicional

#### 🥉 **Opción 3: OpenAI GPT-3.5** (Pago pero preciso)

```bash
# 1. Obtener API key de OpenAI
# 2. Configurar
export OPENAI_API_KEY="tu-key-aqui"

# 3. Usar
# (Necesitaremos agregar soporte para OpenAI - próximo paso)
```

**Pros:** Muy preciso, rápido, no usa tu computadora  
**Cons:** De pago (~$0.50 por 1000 solicitudes)

---

## Cómo Forzar un Modelo Específico

### Método 1: Por línea de comandos

```bash
# Próximamente agregaremos:
python nlp_simplex.py --nlp --model phi-3-mini --file problema.txt
```

### Método 2: En código Python

```python
from src.nlp import TransformerNLPProcessor, NLPModelType

# Forzar Phi-3
processor = TransformerNLPProcessor(
    model_type=NLPModelType.PHI_3_MINI,
    auto_select_model=False  # Desactivar selección automática
)

result = processor.process_text(problem_text)
```

---

## Comparación de Resultados Esperados

| Problema                  | T5-small | T5-base | Phi-3 | Mistral | GPT-4 |
| ------------------------- | -------- | ------- | ----- | ------- | ----- |
| Simple (2 vars)           | ✅       | ✅      | ✅    | ✅      | ✅    |
| Medio (4-6 vars)          | ⚠️       | ⚠️      | ✅    | ✅      | ✅    |
| Complejo (9+ vars)        | ❌       | ❌      | ✅    | ✅      | ✅    |
| **problema_complejo.txt** | ❌       | ❌      | ✅    | ✅      | ✅    |

---

## Próximos Pasos

Para resolver tu problema actualmente:

### Opción A: Usar Phi-3-mini (Recomendado)

Te voy a ayudar a configurar el sistema para que use Phi-3-mini por defecto para problemas complejos.

### Opción B: Integrar Ollama

Puedo agregar soporte para Ollama, que es gratis y muy preciso.

### Opción C: Integrar OpenAI API

Puedo agregar soporte para GPT-3.5/GPT-4 si tienes una API key.

### Opción D: Método de Respaldo basado en Reglas

Puedo implementar un sistema de extracción basado en patrones regex como fallback cuando los modelos fallan.

**¿Cuál prefieres que implemente primero?**
