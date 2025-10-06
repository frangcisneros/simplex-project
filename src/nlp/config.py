"""
Configuración de los modelos de lenguaje y constantes del sistema NLP.

Define qué modelos podemos usar, cómo configurarlos, los prompts para extraer
información, y los mensajes de error estándar.
"""

from enum import Enum
from typing import Dict, Any


class NLPModelType(Enum):
    """
    Modelos de lenguaje soportados para procesar texto en español.

    Cada modelo tiene un balance diferente entre velocidad, precisión y uso de recursos.

    Modelos locales (requieren descarga y RAM/GPU):
    - FLAN-T5: Rápido pero limitado en precisión
    - Mistral: Muy preciso pero requiere GPU
    - Phi-3: Modelo pequeño pero potente de Microsoft
    - Gemma: Modelo abierto de Google

    APIs (requieren conexión a internet y API key):
    - OpenAI GPT: Muy preciso, requiere pago
    - Ollama: Modelos locales con API sencilla (gratuito)
    """

    # Modelos T5 (ligeros, rápidos, precisión limitada)
    FLAN_T5_SMALL = "google/flan-t5-small"  # ~80MB, CPU ok, precisión baja
    FLAN_T5_BASE = "google/flan-t5-base"  # ~250MB, CPU ok, precisión media-baja
    FLAN_T5_LARGE = "google/flan-t5-large"  # ~780MB, CPU lento, precisión media

    # Modelos pequeños pero potentes (nueva generación)
    PHI_3_MINI = "microsoft/Phi-3-mini-4k-instruct"  # ~3.8GB, CPU ok, precisión alta
    GEMMA_2B = "google/gemma-2b-it"  # ~2GB, CPU ok, precisión media-alta
    GEMMA_7B = "google/gemma-7b-it"  # ~7GB, GPU recomendada, precisión muy alta

    # Modelos grandes (requieren GPU, máxima precisión)
    MISTRAL_7B = "mistralai/Mistral-7B-Instruct-v0.3"  # ~7GB GPU, precisión muy alta
    LLAMA3_8B = "meta-llama/Meta-Llama-3-8B-Instruct"  # ~8GB GPU, precisión muy alta

    # APIs (requieren internet y configuración)
    OPENAI_GPT4 = "openai:gpt-4"  # API, máxima precisión
    OPENAI_GPT35 = "openai:gpt-3.5-turbo"  # API, precisión alta, más barato
    OLLAMA_LLAMA3 = "ollama:llama3"  # API local, gratuito
    OLLAMA_MISTRAL = "ollama:mistral"  # API local, gratuito


class ModelConfig:
    """
    Configuraciones predefinidas para cada modelo de lenguaje.

    Cada modelo tiene parámetros óptimos para:
    - max_length: cuánto texto puede generar
    - temperature: qué tan creativo es (0 = determinista, 1 = aleatorio)
    - quantización: comprimir el modelo para usar menos memoria
    """

    DEFAULT_CONFIGS: Dict[NLPModelType, Dict[str, Any]] = {
        # Modelos T5
        NLPModelType.FLAN_T5_SMALL: {
            "max_length": 1024,
            "max_new_tokens": 512,
            "temperature": 0.3,
            "do_sample": False,
            "num_beams": 1,
            "load_in_8bit": False,
            "device_map": "auto",
        },
        NLPModelType.FLAN_T5_BASE: {
            "max_length": 1024,
            "max_new_tokens": 512,
            "temperature": 0.3,
            "do_sample": False,
            "num_beams": 1,
            "load_in_8bit": False,
            "device_map": "auto",
        },
        NLPModelType.FLAN_T5_LARGE: {
            "max_length": 1024,
            "max_new_tokens": 512,
            "temperature": 0.3,
            "do_sample": False,
            "num_beams": 1,
            "load_in_8bit": True,
            "device_map": "auto",
        },
        # Modelos pequeños pero potentes
        NLPModelType.PHI_3_MINI: {
            "max_length": 4096,
            "max_new_tokens": 1024,
            "temperature": 0.1,
            "do_sample": True,
            "top_p": 0.95,
            "load_in_4bit": True,
            "device_map": "auto",
        },
        NLPModelType.GEMMA_2B: {
            "max_length": 8192,
            "max_new_tokens": 1024,
            "temperature": 0.1,
            "do_sample": True,
            "top_p": 0.95,
            "load_in_8bit": True,
            "device_map": "auto",
        },
        NLPModelType.GEMMA_7B: {
            "max_length": 8192,
            "max_new_tokens": 1024,
            "temperature": 0.1,
            "do_sample": True,
            "top_p": 0.95,
            "load_in_4bit": True,
            "device_map": "auto",
        },
        # Modelos grandes
        NLPModelType.MISTRAL_7B: {
            "max_length": 8192,
            "max_new_tokens": 2048,
            "temperature": 0.1,
            "do_sample": True,
            "top_p": 0.95,
            "load_in_4bit": True,
            "device_map": "auto",
        },
        NLPModelType.LLAMA3_8B: {
            "max_length": 8192,
            "max_new_tokens": 2048,
            "temperature": 0.1,
            "do_sample": True,
            "top_p": 0.95,
            "load_in_4bit": True,
            "device_map": "auto",
        },
        # APIs - configuración básica (se manejan diferente)
        NLPModelType.OPENAI_GPT4: {
            "max_tokens": 2048,
            "temperature": 0.1,
        },
        NLPModelType.OPENAI_GPT35: {
            "max_tokens": 2048,
            "temperature": 0.1,
        },
        NLPModelType.OLLAMA_LLAMA3: {
            "temperature": 0.1,
        },
        NLPModelType.OLLAMA_MISTRAL: {
            "temperature": 0.1,
        },
    }


class PromptTemplates:
    """
    Prompts que le pedimos al modelo de lenguaje para extraer información.

    Estos prompts instruyen al modelo sobre cómo convertir el texto en español
    a un JSON estructurado con el problema de optimización.
    """

    OPTIMIZATION_EXTRACTION_PROMPT = """Task: Extract optimization problem as JSON.

Problem: {problem_text}

Return ONLY valid JSON in this exact format:
{{"objective_type": "maximize", "objective_coefficients": [1, 2], "constraints": [{{"coefficients": [1, 1], "operator": "<=", "rhs": 10}}], "variable_names": ["x1", "x2"]}}"""

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

    Define límites razonables para evitar problemas de memoria o rendimiento,
    y establece umbrales de calidad para aceptar resultados del modelo.
    """

    DEFAULT_MODEL = NLPModelType.FLAN_T5_SMALL  # El más rápido para empezar
    MAX_PROCESSING_TIME = 30.0  # Tiempo máximo en segundos para procesar un problema
    MIN_CONFIDENCE_SCORE = 0.7  # Qué tan seguro debe estar el modelo (0-1)
    MAX_VARIABLES = 20  # Límite de variables para problemas manejables
    MAX_CONSTRAINTS = 50  # Límite de restricciones para evitar problemas muy complejos
    CACHE_SIZE = 100  # Cuántos resultados guardar en caché
