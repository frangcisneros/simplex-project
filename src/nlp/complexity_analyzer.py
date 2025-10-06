"""
Analizador de complejidad de problemas y capacidades del sistema.

Detecta automáticamente:
- Complejidad del problema (simple, medio, complejo)
- Capacidades de hardware (RAM, GPU, CPU)
- Modelo óptimo a usar
"""

import re
import logging
import psutil
from typing import Dict, Any, Optional
from enum import Enum

try:
    import torch

    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False

from .config import NLPModelType


class ProblemComplexity(Enum):
    """Niveles de complejidad de un problema."""

    SIMPLE = "simple"
    MEDIUM = "medium"
    COMPLEX = "complex"


class SystemCapability(Enum):
    """Capacidades del sistema."""

    LOW = "low"  # < 4GB RAM, sin GPU
    MEDIUM = "medium"  # 4-8GB RAM, GPU opcional
    HIGH = "high"  # > 8GB RAM, GPU disponible


class ComplexityAnalyzer:
    """
    Analiza la complejidad de un problema de optimización.

    Examina el texto para estimar:
    - Número de variables
    - Número de restricciones
    - Longitud y complejidad del texto
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def analyze_problem(self, text: str) -> ProblemComplexity:
        """
        Determina la complejidad de un problema basándose en su descripción.

        Args:
            text: Descripción del problema en lenguaje natural

        Returns:
            Nivel de complejidad (SIMPLE, MEDIUM, COMPLEX)
        """
        # Calcular métricas del texto
        text_length = len(text)
        num_sentences = len(re.findall(r"[.!?]+", text))
        num_numbers = len(re.findall(r"\d+", text))

        # Estimar número de variables
        variable_indicators = [
            r"\bvariables?\b",
            r"\bproductos?\b",
            r"\btamaños?\b",
            r"\bplantas?\b",
            r"\bfábricas?\b",
            r"\bx\d+",
        ]
        estimated_vars = sum(
            len(re.findall(pattern, text, re.IGNORECASE))
            for pattern in variable_indicators
        )

        # Estimar número de restricciones
        constraint_indicators = [
            r"\bcapacidad\b",
            r"\brestricc",
            r"\blímite",
            r"\bmáximo",
            r"\bmínimo",
            r"\bdemanda\b",
            r"\bespacio\b",
            r"\brecursos?\b",
        ]
        estimated_constraints = sum(
            len(re.findall(pattern, text, re.IGNORECASE))
            for pattern in constraint_indicators
        )

        # Calcular score de complejidad
        complexity_score = 0

        # Longitud del texto
        if text_length > 2000:
            complexity_score += 3
        elif text_length > 800:
            complexity_score += 2
        elif text_length > 300:
            complexity_score += 1

        # Número de oraciones
        if num_sentences > 15:
            complexity_score += 2
        elif num_sentences > 8:
            complexity_score += 1

        # Variables estimadas
        if estimated_vars > 8:
            complexity_score += 3
        elif estimated_vars > 4:
            complexity_score += 2
        elif estimated_vars > 2:
            complexity_score += 1

        # Restricciones estimadas
        if estimated_constraints > 8:
            complexity_score += 3
        elif estimated_constraints > 4:
            complexity_score += 2
        elif estimated_constraints > 2:
            complexity_score += 1

        # Números en el texto (indica complejidad de cálculos)
        if num_numbers > 20:
            complexity_score += 2
        elif num_numbers > 10:
            complexity_score += 1

        # Determinar complejidad final
        if complexity_score <= 4:
            complexity = ProblemComplexity.SIMPLE
        elif complexity_score <= 9:
            complexity = ProblemComplexity.MEDIUM
        else:
            complexity = ProblemComplexity.COMPLEX

        self.logger.info(
            f"Problem complexity: {complexity.value} "
            f"(score: {complexity_score}, length: {text_length}, "
            f"sentences: {num_sentences}, vars: {estimated_vars}, "
            f"constraints: {estimated_constraints})"
        )

        return complexity


class SystemAnalyzer:
    """
    Analiza las capacidades del sistema actual.

    Detecta:
    - Memoria RAM disponible
    - Disponibilidad de GPU
    - Velocidad del CPU
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def analyze_system(self) -> SystemCapability:
        """
        Determina la capacidad del sistema actual.

        Returns:
            Nivel de capacidad (LOW, MEDIUM, HIGH)
        """
        # Obtener memoria RAM total en GB
        ram_gb = psutil.virtual_memory().total / (1024**3)

        # Detectar GPU
        has_gpu = TORCH_AVAILABLE and torch.cuda.is_available()
        if has_gpu:
            gpu_memory_gb = torch.cuda.get_device_properties(0).total_memory / (1024**3)
        else:
            gpu_memory_gb = 0

        # Número de núcleos de CPU
        cpu_cores = psutil.cpu_count(logical=False) or 1

        self.logger.info(
            f"System specs: RAM={ram_gb:.1f}GB, GPU={'Yes' if has_gpu else 'No'}"
            f"{f' ({gpu_memory_gb:.1f}GB)' if has_gpu else ''}, CPU_cores={cpu_cores}"
        )

        # Determinar capacidad
        if has_gpu and ram_gb >= 8:
            capability = SystemCapability.HIGH
        elif ram_gb >= 6 or (has_gpu and ram_gb >= 4):
            capability = SystemCapability.MEDIUM
        else:
            capability = SystemCapability.LOW

        self.logger.info(f"System capability: {capability.value}")
        return capability


class ModelSelector:
    """
    Selecciona el modelo óptimo basándose en la complejidad del problema
    y las capacidades del sistema.

    Estrategia de selección:
    - Problemas SIMPLE: Modelos T5 ligeros
    - Problemas MEDIUM: Phi-3 o Gemma (pequeños pero potentes)
    - Problemas COMPLEX: Modelos grandes (Mistral, Llama3) o Phi-3 si no hay GPU
    """

    # Matriz de selección: [complejidad][capacidad] -> modelo
    MODEL_MATRIX = {
        ProblemComplexity.SIMPLE: {
            SystemCapability.LOW: NLPModelType.FLAN_T5_SMALL,
            SystemCapability.MEDIUM: NLPModelType.FLAN_T5_BASE,
            SystemCapability.HIGH: NLPModelType.PHI_3_MINI,  # Mejor precisión
        },
        ProblemComplexity.MEDIUM: {
            SystemCapability.LOW: NLPModelType.FLAN_T5_BASE,
            SystemCapability.MEDIUM: NLPModelType.PHI_3_MINI,  # Pequeño pero potente
            SystemCapability.HIGH: NLPModelType.GEMMA_7B,  # Muy preciso
        },
        ProblemComplexity.COMPLEX: {
            SystemCapability.LOW: NLPModelType.PHI_3_MINI,  # Mejor opción sin GPU
            SystemCapability.MEDIUM: NLPModelType.GEMMA_7B,  # Balance GPU/precisión
            SystemCapability.HIGH: NLPModelType.MISTRAL_7B,  # Máxima precisión
        },
    }

    # Cadena de fallback: si un modelo falla, intentar con estos en orden
    FALLBACK_CHAIN = {
        # T5 models
        NLPModelType.FLAN_T5_SMALL: [
            NLPModelType.FLAN_T5_BASE,
            NLPModelType.PHI_3_MINI,
        ],
        NLPModelType.FLAN_T5_BASE: [
            NLPModelType.FLAN_T5_LARGE,
            NLPModelType.PHI_3_MINI,
        ],
        NLPModelType.FLAN_T5_LARGE: [
            NLPModelType.PHI_3_MINI,
            NLPModelType.FLAN_T5_BASE,
        ],
        # Modelos pequeños pero potentes
        NLPModelType.PHI_3_MINI: [
            NLPModelType.GEMMA_2B,
            NLPModelType.FLAN_T5_LARGE,
        ],
        NLPModelType.GEMMA_2B: [
            NLPModelType.PHI_3_MINI,
            NLPModelType.GEMMA_7B,
        ],
        NLPModelType.GEMMA_7B: [
            NLPModelType.MISTRAL_7B,
            NLPModelType.PHI_3_MINI,
        ],
        # Modelos grandes
        NLPModelType.MISTRAL_7B: [
            NLPModelType.LLAMA3_8B,
            NLPModelType.GEMMA_7B,
            NLPModelType.PHI_3_MINI,
        ],
        NLPModelType.LLAMA3_8B: [
            NLPModelType.MISTRAL_7B,
            NLPModelType.GEMMA_7B,
        ],
    }

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.complexity_analyzer = ComplexityAnalyzer()
        self.system_analyzer = SystemAnalyzer()

        # Cachear capacidad del sistema (no cambia durante ejecución)
        self._system_capability: Optional[SystemCapability] = None

    def select_model(self, problem_text: str) -> NLPModelType:
        """
        Selecciona el modelo óptimo para un problema dado.

        Args:
            problem_text: Descripción del problema

        Returns:
            Modelo recomendado
        """
        # Analizar complejidad del problema
        problem_complexity = self.complexity_analyzer.analyze_problem(problem_text)

        # Obtener capacidad del sistema (con caché)
        if self._system_capability is None:
            self._system_capability = self.system_analyzer.analyze_system()

        # Seleccionar modelo
        model = self.MODEL_MATRIX[problem_complexity][self._system_capability]

        self.logger.info(
            f"Selected model: {model.value} "
            f"(problem: {problem_complexity.value}, system: {self._system_capability.value})"
        )

        return model

    def get_fallback_models(self, current_model: NLPModelType) -> list[NLPModelType]:
        """
        Obtiene la lista de modelos de respaldo si el actual falla.

        Args:
            current_model: Modelo que falló

        Returns:
            Lista de modelos alternativos a intentar
        """
        return self.FALLBACK_CHAIN.get(current_model, [])
