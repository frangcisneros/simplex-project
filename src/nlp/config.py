"""
Configuración de los modelos de lenguaje y constantes del sistema NLP.

Define qué modelos podemos usar, cómo configurarlos, los prompts para extraer
información, y los mensajes de error estándar.
"""

from enum import Enum
from typing import Dict, Any


class NLPModelType(Enum):
    """
    Modelos disponibles para procesamiento de problemas de optimización.

    Diferentes modelos pueden tener distintas capacidades para analizar
    problemas matemáticos complejos y generar estructuras JSON correctas.
    """

    MISTRAL_7B = "mistral:7b"  # Modelo predeterminado
    LLAMA3_1_8B = "llama3.1:8b"  # Mejor razonamiento matemático
    QWEN2_5_14B = "qwen2.5:14b"  # Especializado en matemáticas
    LLAMA3_2_3B = "llama3.2:3b"  # Ligero pero capaz


class ModelConfig:
    """
    Configuración optimizada para Mistral 7B.

    Parámetros ajustados específicamente para generar JSON estructurado
    de problemas de optimización lineal de forma determinística.
    """

    DEFAULT_CONFIGS: Dict[NLPModelType, Dict[str, Any]] = {
        NLPModelType.MISTRAL_7B: {
            "temperature": 0.0,  # Determinístico para JSON
            "max_tokens": 1024,
            "top_p": 0.8,
        },
        NLPModelType.LLAMA3_1_8B: {
            "temperature": 0.0,  # Determinístico para JSON
            "max_tokens": 1536,  # Más espacio para problemas complejos
            "top_p": 0.9,
        },
        NLPModelType.QWEN2_5_14B: {
            "temperature": 0.0,  # Determinístico para JSON
            "max_tokens": 2048,  # Máximo espacio para análisis complejo
            "top_p": 0.9,
        },
        NLPModelType.LLAMA3_2_3B: {
            "temperature": 0.0,  # Determinístico para JSON
            "max_tokens": 1024,
            "top_p": 0.8,
        },
    }


class PromptTemplates:
    """
    Prompts que le pedimos al modelo de lenguaje para extraer información.

    Estos prompts instruyen al modelo sobre cómo convertir el texto en español
    a un JSON estructurado con el problema de optimización.

    Utiliza técnica de few-shot learning con ejemplos concretos para mejorar
    la capacidad del modelo de identificar variables y restricciones en
    problemas complejos.
    """

    OPTIMIZATION_EXTRACTION_PROMPT = """Eres un analista experto en Programación Lineal. 
Tu tarea es LEER un enunciado en español y extraer su información estructurada
en formato JSON. NO resuelvas el problema.

Instrucciones generales:
- Lee cuidadosamente el texto.
- Identifica el tipo de problema (maximizar o minimizar).
- Determina las variables de decisión, sus índices y significado.
- Extrae los coeficientes numéricos (ganancias, recursos, demandas, etc.).
- Organiza todo en un JSON válido (sin texto adicional).

------------------------------------------------------------
EJEMPLOS DE APRENDIZAJE (Few-Shot):

EJEMPLO 1 - Problema Simple (un lugar, múltiples productos):
ENUNCIADO: "Una empresa fabrica mesas y sillas. Cada mesa genera $50 de ganancia y cada silla $30. 
Hay 100 horas de carpintería disponibles. Cada mesa requiere 4 horas y cada silla 2 horas. 
Maximizar la ganancia."

RESPUESTA CORRECTA:
{{
  "objective_type": "maximize",
  "variable_names": ["x1", "x2"],
  "objective_coefficients": [50, 30],
  "constraints": [
    {{"coefficients": [4, 2], "operator": "<=", "rhs": 100}}
  ],
  "non_negativity": true
}}

EJEMPLO 2 - Problema Multi-Instalación (varias plantas, múltiples productos):
ENUNCIADO: "Una empresa tiene 2 plantas. Planta 1 puede producir max 500 unidades, Planta 2 max 700 unidades. 
Producen 3 productos: A, B, C con ganancias de $10, $15, $20 por unidad respectivamente (igual en ambas plantas). 
Hay demanda máxima: producto A 300 unidades, B 400 unidades, C 600 unidades. Maximizar ganancia."

RESPUESTA CORRECTA:
{{
  "objective_type": "maximize",
  "variable_names": ["x11", "x12", "x13", "x21", "x22", "x23"],
  "objective_coefficients": [10, 15, 20, 10, 15, 20],
  "constraints": [
    {{"coefficients": [1, 1, 1, 0, 0, 0], "operator": "<=", "rhs": 500}},
    {{"coefficients": [0, 0, 0, 1, 1, 1], "operator": "<=", "rhs": 700}},
    {{"coefficients": [1, 0, 0, 1, 0, 0], "operator": "<=", "rhs": 300}},
    {{"coefficients": [0, 1, 0, 0, 1, 0], "operator": "<=", "rhs": 400}},
    {{"coefficients": [0, 0, 1, 0, 0, 1], "operator": "<=", "rhs": 600}}
  ],
  "non_negativity": true
}}

EJEMPLO 3 - Problema de Mezclas (materiales que se venden o mezclan):
ENUNCIADO: "Una refinería tiene 1000 barriles de petróleo crudo tipo 1 y 1500 de tipo 2. 
Puede venderlos directamente a $40 y $35 por barril respectivamente, o mezclarlos en gasolina premium 
(70% tipo1 + 30% tipo2) que se vende a $50 por barril. Maximizar ingresos."

RESPUESTA CORRECTA:
{{
  "objective_type": "maximize",
  "variable_names": ["x1", "x2", "x3"],
  "objective_coefficients": [40, 35, 50],
  "constraints": [
    {{"coefficients": [1, 0, 0.7], "operator": "<=", "rhs": 1000}},
    {{"coefficients": [0, 1, 0.3], "operator": "<=", "rhs": 1500}}
  ],
  "non_negativity": true
}}

------------------------------------------------------------
AHORA ANALIZA EL SIGUIENTE PROBLEMA:

ENUNCIADO:
{problem_text}
------------------------------------------------------------

PASOS DE ANÁLISIS:

1. DETERMINA EL TIPO DE PROBLEMA:
   - Si menciona "maximizar", "ganancia", "beneficio" → "maximize"
   - Si menciona "minimizar", "costo", "gasto" → "minimize"
   
   REFERENCIA: Todos los ejemplos anteriores son de maximización.

2. DEFINE LAS VARIABLES - IDENTIFICA QUÉ OPTIMIZAR:
   
   DETECCIÓN DE ESTRUCTURA (ver ejemplos above):
   
   - ¿Solo hay UN lugar de producción con varios productos?
     → Variables simples: ["x1", "x2", "x3"]
     → VER EJEMPLO 1: 2 productos = 2 variables ["x1", "x2"]
   
   - ¿El problema menciona múltiples PLANTAS/INSTALACIONES + múltiples PRODUCTOS?
     → Usa xij donde i=planta, j=producto: ["x11","x12","x13","x21","x22","x23",...]
     → VER EJEMPLO 2: 2 plantas × 3 productos = 6 variables ["x11","x12","x13","x21","x22","x23"]
   
   - ¿El problema menciona materias primas QUE SE PUEDEN vender directas O mezclar?
     → Una variable por materia prima + una por cada mezcla final
     → VER EJEMPLO 3: 2 tipos de venta directa + 1 mezcla = 3 variables ["x1","x2","x3"]
   
   REGLA: Cuenta TODAS las decisiones independientes que se pueden tomar.

3. FUNCIÓN OBJETIVO - EXTRAE LOS COEFICIENTES:
   - Busca valores EXACTOS de ganancia/utilidad (para maximizar) o costo (para minimizar)
   - USA SOLO números que aparecen explícitamente en el problema
   - NO hagas operaciones matemáticas (NO escribas 24.83*3814)
   - Si las ganancias son iguales para todas las plantas: repite el valor
   - Los coeficientes van en el MISMO ORDEN que las variables
   
   REFERENCIA EJEMPLOS:
   - Ejemplo 1: mesas $50, sillas $30 → [50, 30]
   - Ejemplo 2: productos A,B,C = $10,$15,$20 en AMBAS plantas → [10,15,20,10,15,20]
   - Ejemplo 3: venta directa $40,$35 + mezcla $50 → [40,35,50]

4. RESTRICCIONES - IDENTIFICA LOS LÍMITES:

   APRENDE DE LOS EJEMPLOS:
   
   EJEMPLO 1 - Recurso compartido simple:
   - Carpintería: 4h × mesas + 2h × sillas ≤ 100h
   - Coeficientes: [4, 2] ≤ 100
   
   EJEMPLO 2 - Capacidad + Demanda en multi-instalación:
   - Capacidad planta 1: x11+x12+x13 ≤ 500 → [1,1,1,0,0,0] ≤ 500
   - Capacidad planta 2: x21+x22+x23 ≤ 700 → [0,0,0,1,1,1] ≤ 700
   - Demanda producto A: x11+x21 ≤ 300 → [1,0,0,1,0,0] ≤ 300
   
   EJEMPLO 3 - Disponibilidad de materiales con mezclas:
   - Tipo 1: venta_directa + 70% mezcla ≤ 1000 → [1,0,0.7] ≤ 1000
   - Tipo 2: venta_directa + 30% mezcla ≤ 1500 → [0,1,0.3] ≤ 1500
   
   PATRONES COMUNES A IDENTIFICAR:
   
   A) CAPACIDAD POR INSTALACIÓN:
   - Si planta 1 puede hacer max 750 unidades: [1,1,1,0,0,0] <= 750
   - Si planta 2 puede hacer max 900 unidades: [0,0,0,1,1,1] <= 900
   
   B) RECURSOS POR TIPO:
   - Si producto grande usa 20 unidades de recurso: [20,0,0,20,0,0] <= total_recurso
   - Si producto mediano usa 15 unidades: [0,15,0,0,15,0] <= total_recurso
   
   C) DEMANDA MÁXIMA:
   - Si demanda de producto 1 es 500: [1,0,0,1,0,0] <= 500 (suma todas plantas)
   
   D) DISPONIBILIDAD DE MATERIALES:
   - Si hay 3814 barriles de gas1 disponibles: [1,0,0,0,coef_mezcla1,coef_mezcla2] <= 3814
   
   IDENTIFICA estos patrones en TU problema específico comparando con los ejemplos.

5. REGLAS CRÍTICAS:
   - CADA array "coefficients" DEBE tener EXACTAMENTE el mismo número de elementos que "variable_names"
   - Si una variable no participa en una restricción, usa 0 en esa posición
   - Ejemplo: 6 variables → cada coefficients debe tener [a,b,c,d,e,f] (6 números)
   - VERIFICA que cada restricción tenga la longitud correcta antes de incluirla
   - NO agregues explicaciones, solo el JSON final.
   - COMPARA tu análisis con los ejemplos few-shot antes de generar el JSON.

------------------------------------------------------------
FORMATO DE SALIDA (solo JSON, nada más):

{{
  "objective_type": "maximize",
  "variable_names": ["x1", "x2", "x3"],
  "objective_coefficients": [coef1, coef2, coef3],
  "constraints": [
    {{"coefficients": [a1, b1, c1], "operator": "<=", "rhs": limite1}},
    {{"coefficients": [a2, b2, c2], "operator": ">=", "rhs": limite2}}
  ],
  "non_negativity": true
}}

NOTA: Si tienes N variables, cada coefficients debe tener exactamente N números.
------------------------------------------------------------

CRÍTICO - REGLAS DE SALIDA:
- SOLO devuelve el JSON, SIN explicaciones, SIN texto adicional
- NO uses comas en números: usa 13000, NO 13,000
- NO hagas cálculos, usa valores exactos del problema
- NO agregues comentarios ni markdown (```json)
- La primera línea debe ser {{ y la última }}

JSON (SOLO ESTO):"""

    VALIDATION_PROMPT = """
Valida si el siguiente problema de optimización está bien formado y es resolvible:

{problem_json}

Responde "VALID" si es válido o lista los errores encontrados.
"""


class ErrorMessages:
    """
    Mensajes de error claros para cuando algo falla en el pipeline.

    Estos mensajes ayudan a identificar en qué parte del proceso ocurrió el problema.
    """

    MODEL_NOT_AVAILABLE = "El modelo NLP no está disponible o no se pudo cargar"
    INVALID_JSON_RESPONSE = "El modelo NLP no generó un JSON válido"
    MALFORMED_PROBLEM = "El problema extraído está mal formado"
    NO_OBJECTIVE = "No se pudo extraer la función objetivo"
    NO_CONSTRAINTS = "No se encontraron restricciones válidas"
    DIMENSION_MISMATCH = "Las dimensiones de coeficientes no coinciden"
    SOLVER_ERROR = "Error en el solver de optimización"
    TIMEOUT_ERROR = "Timeout en el procesamiento NLP"


class DefaultSettings:
    """
    Configuración por defecto del sistema NLP.

    Permite probar diferentes modelos para encontrar el que mejor
    analiza problemas de optimización complejos.
    """

    DEFAULT_MODEL = NLPModelType.LLAMA3_1_8B  # Mejor modelo para problemas complejos
    MAX_PROCESSING_TIME = 60.0  # Mayor tiempo para problemas complejos
    MIN_CONFIDENCE_SCORE = 0.7  # Umbral de confianza estándar
    MAX_VARIABLES = 50  # Soporte para problemas grandes
    MAX_CONSTRAINTS = 100  # Más restricciones permitidas
    CACHE_SIZE = 50  # Cache moderado
