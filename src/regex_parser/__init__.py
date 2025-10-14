"""
Sistema de parsing basado en expresiones regulares para problemas de optimización.

Este módulo proporciona una alternativa ligera y rápida al procesamiento NLP
usando solo expresiones regulares. Es ideal para problemas con estructura
estándar y no requiere modelos de lenguaje.

Componentes:
- regex_extractor: Extrae componentes del problema usando regex
- variable_detector: Detecta y normaliza nombres de variables
- constraint_parser: Parsea restricciones matemáticas
- objective_parser: Extrae función objetivo
- regex_processor: Orquesta todo el pipeline

Ventajas sobre NLP:
- Instantáneo (sin latencia de modelo)
- No requiere GPU ni modelos grandes
- Determinista y predecible
- Ideal para formatos estándar

Limitaciones:
- Requiere sintaxis más estructurada
- Menos flexible con lenguaje natural libre
- No maneja ambigüedad tan bien como LLM
"""

from .regex_processor import RegexOptimizationProcessor
from .variable_detector import VariableDetector
from .constraint_parser import ConstraintParser
from .objective_parser import ObjectiveParser
from .regex_extractor import RegexExtractor
from .pattern_library import PatternLibrary

__all__ = [
    "RegexOptimizationProcessor",
    "VariableDetector",
    "ConstraintParser",
    "ObjectiveParser",
    "RegexExtractor",
    "PatternLibrary",
]
