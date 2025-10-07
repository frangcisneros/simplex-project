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
ENUNCIADO:
{problem_text}
------------------------------------------------------------

PASOS DE ANÁLISIS:

1. DETERMINA EL TIPO DE PROBLEMA:
   - Si menciona "maximizar", "ganancia", "beneficio" → "maximize"
   - Si menciona "minimizar", "costo", "gasto" → "minimize"

2. DEFINE LAS VARIABLES - IDENTIFICA QUÉ OPTIMIZAR:
   
   DETECCIÓN DE ESTRUCTURA:
   - ¿El problema menciona múltiples PLANTAS/INSTALACIONES + múltiples PRODUCTOS?
     → Usa xij donde i=planta, j=producto: ["x11","x12","x13","x21","x22","x23",...]
   
   - ¿El problema menciona materias primas QUE SE PUEDEN vender directas O mezclar?
     → Una variable por materia prima + una por cada mezcla final
   
   - ¿Solo hay UN lugar de producción con varios productos?
     → Variables simples: ["x1", "x2", "x3"]
   
   REGLA: Cuenta TODAS las decisiones independientes que se pueden tomar.

3. FUNCIÓN OBJETIVO - EXTRAE LOS COEFICIENTES:
   - Busca valores EXACTOS de ganancia/utilidad (para maximizar) o costo (para minimizar)
   - USA SOLO números que aparecen explícitamente en el problema
   - NO hagas operaciones matemáticas (NO escribas 24.83*3814)
   - Si las ganancias son iguales para todas las plantas: repite el valor
   - Los coeficientes van en el MISMO ORDEN que las variables

4. RESTRICCIONES - IDENTIFICA LOS LÍMITES:

   EJEMPLOS DE PATRONES COMUNES:
   
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
   
   IDENTIFICA estos patrones en TU problema específico.

5. REGLAS CRÍTICAS:
   - CADA array "coefficients" DEBE tener EXACTAMENTE el mismo número de elementos que "variable_names"
   - Si una variable no participa en una restricción, usa 0 en esa posición
   - Ejemplo: 6 variables → cada coefficients debe tener [a,b,c,d,e,f] (6 números)
   - VERIFICA que cada restricción tenga la longitud correcta antes de incluirla
   - NO agregues explicaciones, solo el JSON final.

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
