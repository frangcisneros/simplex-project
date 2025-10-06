"""
Configuración y constantes para el sistema NLP.
"""

from enum import Enum
from typing import Dict, Any


class NLPModelType(Enum):
    """Tipos de modelos NLP soportados."""

    FLAN_T5_SMALL = "google/flan-t5-small"
    FLAN_T5_BASE = "google/flan-t5-base"
    MISTRAL_7B = "mistralai/Mistral-7B-Instruct-v0.1"
    LLAMA2_7B = "meta-llama/Llama-2-7b-chat-hf"


class ModelConfig:
    """Configuración para modelos NLP."""

    # Configuraciones por defecto para cada modelo
    DEFAULT_CONFIGS: Dict[NLPModelType, Dict[str, Any]] = {
        NLPModelType.FLAN_T5_SMALL: {
            "max_length": 512,
            "temperature": 0.7,
            "do_sample": True,
            "num_beams": 4,
            "load_in_8bit": False,
            "device_map": "auto",
        },
        NLPModelType.FLAN_T5_BASE: {
            "max_length": 512,
            "temperature": 0.7,
            "do_sample": True,
            "num_beams": 4,
            "load_in_8bit": True,
            "device_map": "auto",
        },
        NLPModelType.MISTRAL_7B: {
            "max_length": 1024,
            "temperature": 0.7,
            "do_sample": True,
            "top_p": 0.95,
            "load_in_4bit": True,
            "device_map": "auto",
        },
        NLPModelType.LLAMA2_7B: {
            "max_length": 1024,
            "temperature": 0.7,
            "do_sample": True,
            "top_p": 0.95,
            "load_in_4bit": True,
            "device_map": "auto",
        },
    }


class PromptTemplates:
    """Templates para prompts de los modelos NLP."""

    OPTIMIZATION_EXTRACTION_PROMPT = """
Analiza el siguiente problema de optimización en español y extrae SOLO un JSON válido.

FORMATO REQUERIDO (solo devuelve este JSON, nada más):
{
    "objective_type": "maximize",
    "objective_coefficients": [420, 360, 300, 420, 360, 300, 420, 360, 300],
    "constraints": [
        {"coefficients": [1, 1, 1, 0, 0, 0, 0, 0, 0], "operator": "<=", "rhs": 750}
    ],
    "variable_names": ["x11", "x12", "x13", "x21", "x22", "x23", "x31", "x32", "x33"]
}

REGLAS:
- Identifica todas las variables de decisión (ej: cantidad a producir de cada tamaño en cada planta)
- Extrae coeficientes de ganancia/costo de la función objetivo
- Identifica restricciones de capacidad, recursos, demanda
- Usa "maximize" para maximizar ganancias, "minimize" para minimizar costos
- Operadores: "<=" menor igual, ">=" mayor igual, "=" igual

PROBLEMA: {problem_text}

JSON:"""

    VALIDATION_PROMPT = """
Valida si el siguiente problema de optimización está bien formado y es resolvible:

{problem_json}

Responde "VALID" si es válido o lista los errores encontrados.
"""


class ErrorMessages:
    """Mensajes de error estandardizados."""

    MODEL_NOT_AVAILABLE = "El modelo NLP no está disponible o no se pudo cargar"
    INVALID_JSON_RESPONSE = "El modelo NLP no generó un JSON válido"
    MALFORMED_PROBLEM = "El problema extraído está mal formado"
    NO_OBJECTIVE = "No se pudo extraer la función objetivo"
    NO_CONSTRAINTS = "No se encontraron restricciones válidas"
    DIMENSION_MISMATCH = "Las dimensiones de coeficientes no coinciden"
    SOLVER_ERROR = "Error en el solver de optimización"
    TIMEOUT_ERROR = "Timeout en el procesamiento NLP"


class DefaultSettings:
    """Configuraciones por defecto del sistema."""

    DEFAULT_MODEL = NLPModelType.FLAN_T5_SMALL
    MAX_PROCESSING_TIME = 30.0  # segundos
    MIN_CONFIDENCE_SCORE = 0.7
    MAX_VARIABLES = 20
    MAX_CONSTRAINTS = 50
    CACHE_SIZE = 100
