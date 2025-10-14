"""
Procesador principal que integra regex parsing con el sistema de optimización.

Implementa la interfaz INLPProcessor usando solo expresiones regulares,
proporcionando una alternativa rápida y ligera al procesamiento con LLM.
"""

import logging
from typing import Dict, Any
import sys
from pathlib import Path

# Importar interfaces del sistema NLP
sys.path.insert(0, str(Path(__file__).parent.parent))
from nlp.interfaces import INLPProcessor, NLPResult, OptimizationProblem

from .regex_extractor import RegexExtractor
from .variable_detector import VariableDetector
from .objective_parser import ObjectiveParser
from .constraint_parser import ConstraintParser


class RegexOptimizationProcessor(INLPProcessor):
    """
    Procesador de problemas de optimización usando solo regex.

    Implementa INLPProcessor para integrarse con el sistema existente,
    pero usa expresiones regulares en lugar de modelos de lenguaje.

    Ventajas:
    - Instantáneo (sin latencia)
    - No requiere modelos ni GPU
    - Determinista y predecible
    - Bajo uso de recursos

    Ideal para:
    - Testing rápido
    - Problemas con formato estándar
    - Sistemas con recursos limitados
    - Producción donde velocidad es crítica
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.extractor = RegexExtractor()
        self.logger.info("RegexOptimizationProcessor inicializado")

    def is_available(self) -> bool:
        """
        Regex siempre está disponible (no depende de servicios externos).

        Returns:
            True siempre
        """
        return True

    def process_text(self, text: str) -> NLPResult:
        """
        Procesa texto usando regex y retorna un NLPResult.

        Args:
            text: Texto del problema de optimización

        Returns:
            NLPResult con el problema extraído o error
        """
        self.logger.info("Procesando texto con regex parser")

        try:
            # Extraer problema completo
            extracted = self.extractor.extract_problem(text)

            if not extracted:
                return NLPResult(
                    success=False,
                    problem=None,
                    error_message="No se pudo extraer el problema con regex",
                    confidence_score=0.0,
                )

            # Convertir a OptimizationProblem
            problem = self._convert_to_optimization_problem(extracted)

            return NLPResult(
                success=True,
                problem=problem,
                confidence_score=extracted.confidence_score,
            )

        except Exception as e:
            self.logger.error(f"Error procesando con regex: {e}", exc_info=True)
            return NLPResult(
                success=False,
                problem=None,
                error_message=f"Error en regex parser: {str(e)}",
                confidence_score=0.0,
            )

    def _convert_to_optimization_problem(self, extracted) -> OptimizationProblem:
        """
        Convierte ExtractedProblem a OptimizationProblem.

        Args:
            extracted: Resultado del RegexExtractor

        Returns:
            OptimizationProblem compatible con el sistema
        """
        # Extraer nombres de variables en orden
        variable_names = [v.name for v in extracted.variables]

        # Construir coeficientes de la función objetivo
        # Asegurar que estén en el orden correcto de las variables
        objective_coefficients = []
        for var_name in variable_names:
            coef = extracted.objective.coefficients.get(var_name, 0.0)
            objective_coefficients.append(coef)

        # Convertir restricciones a formato de matrices
        constraints = []
        for constraint in extracted.constraints:
            # Construir coeficientes en orden de variables
            coefficients = []
            for var_name in variable_names:
                coef = constraint.coefficients.get(var_name, 0.0)
                coefficients.append(coef)

            constraints.append(
                {
                    "coefficients": coefficients,
                    "operator": constraint.operator,
                    "rhs": constraint.rhs,
                }
            )

        # Crear OptimizationProblem
        problem = OptimizationProblem(
            objective_type=extracted.objective.objective_type,
            objective_coefficients=objective_coefficients,
            constraints=constraints,
            variable_names=variable_names,
        )

        return problem

    def get_model_info(self) -> Dict[str, Any]:
        """
        Retorna información sobre el 'modelo' (en este caso, regex).

        Returns:
            Dict con metadata del procesador
        """
        return {
            "processor_type": "regex",
            "model_name": "Regular Expressions",
            "version": "1.0",
            "requires_external_service": False,
            "is_deterministic": True,
            "average_latency_ms": 1,  # Casi instantáneo
            "capabilities": [
                "variable_detection",
                "objective_parsing",
                "constraint_parsing",
                "standard_format_problems",
            ],
            "limitations": [
                "requires_structured_input",
                "limited_natural_language_flexibility",
                "no_ambiguity_resolution",
            ],
        }


class HybridProcessor(INLPProcessor):
    """
    Procesador híbrido que usa regex primero, y LLM como fallback.

    Estrategia:
    1. Intenta con regex (rápido)
    2. Si falla o confianza es baja, usa LLM
    3. Retorna mejor resultado

    Beneficios:
    - Velocidad de regex para casos simples
    - Robustez de LLM para casos complejos
    - Optimización automática de recursos
    """

    def __init__(self, llm_processor: INLPProcessor, confidence_threshold: float = 0.8):
        """
        Args:
            llm_processor: Procesador basado en LLM para fallback
            confidence_threshold: Umbral mínimo de confianza para aceptar resultado regex
        """
        self.logger = logging.getLogger(__name__)
        self.regex_processor = RegexOptimizationProcessor()
        self.llm_processor = llm_processor
        self.confidence_threshold = confidence_threshold

    def is_available(self) -> bool:
        """Disponible si regex está OK (LLM es opcional)."""
        return self.regex_processor.is_available()

    def process_text(self, text: str) -> NLPResult:
        """
        Procesa con estrategia híbrida.

        Returns:
            Mejor resultado entre regex y LLM
        """
        self.logger.info("Procesando con estrategia híbrida (regex + LLM)")

        # 1. Intentar con regex primero
        regex_result = self.regex_processor.process_text(text)

        # Si regex funciona bien, usarlo
        confidence = regex_result.confidence_score or 0.0
        if regex_result.success and confidence >= self.confidence_threshold:
            self.logger.info(
                f"Regex exitoso con confianza {confidence:.2f}, no se necesita LLM"
            )
            return regex_result

        # 2. Si regex falla o tiene baja confianza, usar LLM
        self.logger.info(
            f"Regex tuvo confianza baja ({confidence:.2f}), usando LLM como fallback"
        )

        if not self.llm_processor.is_available():
            self.logger.warning("LLM no disponible, retornando resultado regex")
            return regex_result

        llm_result = self.llm_processor.process_text(text)

        # 3. Retornar mejor resultado
        if llm_result.success:
            self.logger.info("LLM procesó exitosamente")
            return llm_result
        else:
            self.logger.warning("LLM falló, retornando resultado regex")
            return regex_result

    def get_model_info(self) -> Dict[str, Any]:
        """Retorna info del procesador híbrido."""
        llm_info = {}
        if hasattr(self.llm_processor, "get_model_info"):
            llm_info = self.llm_processor.get_model_info()
        else:
            llm_info = {"type": "llm_processor"}

        return {
            "processor_type": "hybrid",
            "primary": self.regex_processor.get_model_info(),
            "fallback": llm_info,
            "confidence_threshold": self.confidence_threshold,
        }
