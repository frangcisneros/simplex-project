"""
Configuración de los modelos de lenguaje y constantes del sistema NLP.

Define qué modelos podemos usar, cómo configurarlos, los prompts para extraer
información, y los mensajes de error estándar.
"""

from enum import Enum
from typing import Dict, Any


class NLPModelType(Enum):
    """
    Enumeración de los modelos disponibles para el procesamiento de problemas de optimización.

    Cada modelo tiene capacidades específicas para analizar problemas matemáticos
    complejos y generar estructuras JSON correctas.
    """

    MISTRAL_7B = "mistral:7b"  # Modelo predeterminado, balance entre eficiencia y precisión
    LLAMA3_1_8B = "llama3.1:8b"  # Modelo avanzado para razonamiento matemático
    QWEN2_5_14B = "qwen2.5:14b"  # Especializado en problemas matemáticos complejos
    LLAMA3_2_3B = "llama3.2:3b"  # Modelo ligero para problemas simples


class ModelConfig:
    """
    Configuración optimizada para cada modelo de lenguaje.

    Define parámetros como temperatura, número máximo de tokens y top-p,
    ajustados para generar JSON estructurado de manera eficiente y precisa.
    """

    DEFAULT_CONFIGS: Dict[NLPModelType, Dict[str, Any]] = {
        NLPModelType.MISTRAL_7B: {
            "temperature": 0.0,  # Determinístico para generar JSON consistente
            "max_tokens": 1024,
            "top_p": 0.8,
        },
        NLPModelType.LLAMA3_1_8B: {
            "temperature": 0.1,  # Ligeramente creativo para problemas complejos
            "max_tokens": 2048,  # Más espacio para análisis detallado
            "top_p": 0.95,
        },
        NLPModelType.QWEN2_5_14B: {
            "temperature": 0.0,  # Determinístico para JSON
            "max_tokens": 2048,  # Máximo espacio para problemas complejos
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
    Plantillas de prompts para interactuar con los modelos de lenguaje.

    Estas plantillas instruyen al modelo sobre cómo convertir texto en español
    a un JSON estructurado que represente un problema de optimización.
    """

    OPTIMIZATION_EXTRACTION_PROMPT = """Eres un analista experto en Programación Lineal. Tu tarea es leer un problema en español y convertirlo a un formato JSON estructurado.

**Instrucciones Clave:**
1.  **Analiza el problema paso a paso** para identificar el objetivo, las variables y las restricciones. Presta especial atención a problemas con múltiples plantas o productos, ya que requieren variables compuestas (ej. xij).
2.  **Genera SOLAMENTE un objeto JSON válido** como respuesta final. No incluyas explicaciones, texto introductorio, ni markdown como ```json.

**Ejemplos de Referencia:**

---
**EJEMPLO 1: Problema Simple**
* **ENUNCIADO:** "Una empresa fabrica mesas y sillas. Cada mesa genera $50 de ganancia y cada silla $30. Hay 100 horas de carpintería disponibles. Cada mesa requiere 4 horas y cada silla 2 horas. Maximizar la ganancia."
* **JSON:**
    {{
      "objective_type": "maximize",
      "variable_names": ["mesas", "sillas"],
      "objective_coefficients": [50, 30],
      "constraints": [
        {{"coefficients": [4, 2], "operator": "<=", "rhs": 100, "name": "carpinteria"}}
      ]
    }}

---
**EJEMPLO 2: Problema Multi-Instalación (3 plantas, 2 productos)**
* **ENUNCIADO:** "Una fábrica tiene 3 plantas que producen productos tipo X e Y. La ganancia por X es $80 y por Y es $60. Capacidades: Planta 1 max 400, Planta 2 max 600, Planta 3 max 300. Demandas: producto X max 800, producto Y max 500. Maximizar ganancia."
* **ANÁLISIS INTERNO (Chain of Thought):** 3 plantas x 2 productos = 6 variables (x1_X, x1_Y, x2_X, x2_Y, x3_X, x3_Y). La función objetivo es [80, 60, 80, 60, 80, 60]. Hay 3 restricciones de capacidad (una por planta) y 2 de demanda (una por producto).
* **JSON:**
    {{
      "objective_type": "maximize",
      "variable_names": ["x1_X", "x1_Y", "x2_X", "x2_Y", "x3_X", "x3_Y"],
      "objective_coefficients": [80, 60, 80, 60, 80, 60],
      "constraints": [
        {{"coefficients": [1, 1, 0, 0, 0, 0], "operator": "<=", "rhs": 400, "name": "capacidad_planta1"}},
        {{"coefficients": [0, 0, 1, 1, 0, 0], "operator": "<=", "rhs": 600, "name": "capacidad_planta2"}},
        {{"coefficients": [0, 0, 0, 0, 1, 1], "operator": "<=", "rhs": 300, "name": "capacidad_planta3"}},
        {{"coefficients": [1, 0, 1, 0, 1, 0], "operator": "<=", "rhs": 800, "name": "demanda_X"}},
        {{"coefficients": [0, 1, 0, 1, 0, 1], "operator": "<=", "rhs": 500, "name": "demanda_Y"}}
      ]
    }}

---
**EJEMPLO 3: Problema de Mezclas**
* **ENUNCIADO:** "Una refinería tiene 1000 barriles de crudo tipo 1 y 1500 de tipo 2. Puede venderlos directamente a $40 y $35 por barril, o mezclarlos en gasolina premium (70% tipo1 + 30% tipo2) que se vende a $50 por barril. Maximizar ingresos."
* **JSON:**
    {{
      "objective_type": "maximize",
      "variable_names": ["venta_crudo1", "venta_crudo2", "produccion_premium"],
      "objective_coefficients": [40, 35, 50],
      "constraints": [
        {{"coefficients": [1, 0, 0.7], "operator": "<=", "rhs": 1000, "name": "disponibilidad_crudo1"}},
        {{"coefficients": [0, 1, 0.3], "operator": "<=", "rhs": 1500, "name": "disponibilidad_crudo2"}}
      ]
    }}

---
**Análisis Preliminar de Estructura (Pista):**
{structure_analysis}
---

**Ahora, analiza el siguiente problema y genera únicamente el JSON correspondiente.**

**ENUNCIADO:**
{problem_text}

**JSON de Salida:**
"""

    VALIDATION_PROMPT = """
Valida si el siguiente problema de optimización está bien formado y es resolvible:

{problem_json}

Responde "VALID" si es válido o lista los errores encontrados.
"""


class ErrorMessages:
    """
    Mensajes de error estándar para identificar problemas en el pipeline.

    Estos mensajes ayudan a depurar errores en diferentes etapas del proceso.
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

    Define parámetros globales como el modelo predeterminado, tiempos máximos
    de procesamiento y límites de variables y restricciones.
    """

    DEFAULT_MODEL = NLPModelType.LLAMA3_1_8B  # Fallback si no se detecta el sistema
    MAX_PROCESSING_TIME = 60.0  # Tiempo máximo permitido para procesar un problema
    MIN_CONFIDENCE_SCORE = 0.7  # Umbral mínimo de confianza para aceptar resultados
    MAX_VARIABLES = 50  # Límite de variables soportadas
    MAX_CONSTRAINTS = 100  # Límite de restricciones soportadas
    CACHE_SIZE = 50  # Tamaño máximo del caché

    @staticmethod
    def get_optimal_model() -> NLPModelType:
        """
        Detecta automáticamente el mejor modelo de IA según las capacidades del sistema.

        Returns:
            NLPModelType: El modelo más potente que puede ejecutar el sistema.
        """
        try:
            # Importar aquí para evitar dependencias circulares
            import sys
            from pathlib import Path

            # Agregar tools al path si no está
            tools_path = Path(__file__).parent.parent.parent / "tools"
            if str(tools_path) not in sys.path:
                sys.path.insert(0, str(tools_path))

            from system_analyzer import SystemAnalyzer

            analyzer = SystemAnalyzer()
            best_model_name = analyzer.get_best_available_model()

            # Mapear nombre de modelo a enum
            model_mapping = {
                "mistral:7b": NLPModelType.MISTRAL_7B,
                "llama3.1:8b": NLPModelType.LLAMA3_1_8B,
                "qwen2.5:14b": NLPModelType.QWEN2_5_14B,
                "llama3.2:3b": NLPModelType.LLAMA3_2_3B,
                "llama3.2:1b": NLPModelType.LLAMA3_2_3B,  # Fallback al 3b
                "phi3:mini": NLPModelType.LLAMA3_2_3B,  # Fallback al 3b
                "gemma2:9b": NLPModelType.QWEN2_5_14B,  # Similar al 14b
                "llama3.1:70b": NLPModelType.QWEN2_5_14B,  # Muy grande, pero si lo detecta, usar 14b
            }

            detected_model = model_mapping.get(best_model_name, DefaultSettings.DEFAULT_MODEL)

            return detected_model

        except Exception:
            # Si falla la detección, usar el modelo por defecto
            return DefaultSettings.DEFAULT_MODEL
