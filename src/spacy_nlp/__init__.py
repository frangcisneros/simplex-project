"""
Sistema NLP especializado con spaCy para problemas de optimización.

Este módulo implementa procesamiento avanzado de lenguaje natural usando spaCy,
específicamente entrenado y configurado para entender problemas de programación lineal
y optimización. Incluye:

- Named Entity Recognition (NER) personalizado para detectar variables, coeficientes, restricciones
- Pattern Matching con reglas lingüísticas
- Dependency Parsing para entender relaciones
- Sistema de entrenamiento con ejemplos anotados
- Extracción de información estructurada

Ventajas sobre regex:
- Entiende lenguaje natural más libre
- Maneja sinónimos y variaciones
- Detecta contexto y relaciones semánticas
- Aprende de ejemplos

Ventajas sobre LLM:
- Mucho más rápido (segundos vs minutos)
- No requiere GPU potente
- Modelo más pequeño (~500MB vs 8GB+)
- Más predecible y controlable
"""

from .spacy_processor import SpacyNLPProcessor
from .entity_recognizer import OptimizationEntityRecognizer
from .pattern_matcher import OptimizationPatternMatcher
from .training_data import TrainingDataGenerator, ProblemAnnotator
from .model_trainer import SpacyModelTrainer

__all__ = [
    "SpacyNLPProcessor",
    "OptimizationEntityRecognizer",
    "OptimizationPatternMatcher",
    "TrainingDataGenerator",
    "ProblemAnnotator",
    "SpacyModelTrainer",
]
