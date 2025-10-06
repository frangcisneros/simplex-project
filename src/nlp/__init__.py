"""
Paquete NLP para el sistema de programación lineal.
"""

from .interfaces import (
    OptimizationProblem,
    NLPResult,
    INLPProcessor,
    IModelGenerator,
    IOptimizationSolver,
    INLPConnector,
    IModelValidator,
)

from .config import (
    NLPModelType,
    ModelConfig,
    PromptTemplates,
    ErrorMessages,
    DefaultSettings,
)

from .processor import TransformerNLPProcessor, MockNLPProcessor

from .model_generator import (
    SimplexModelGenerator,
    PuLPModelGenerator,
    ORToolsModelGenerator,
    ModelValidator,
)

from .connector import (
    SimplexSolverAdapter,
    NLPConnectorFactory,
    NLPOptimizationConnector,
    ConfigurableNLPConnector,
    SolverType,
)

__all__ = [
    # Core interfaces
    "OptimizationProblem",
    "NLPResult",
    "INLPProcessor",
    "IModelGenerator",
    "IOptimizationSolver",
    "INLPConnector",
    "IModelValidator",
    # Configuration
    "NLPModelType",
    "ModelConfig",
    "PromptTemplates",
    "ErrorMessages",
    "DefaultSettings",
    # Processors
    "TransformerNLPProcessor",
    "MockNLPProcessor",
    # Model generators
    "SimplexModelGenerator",
    "PuLPModelGenerator",
    "ORToolsModelGenerator",
    "ModelValidator",
    # Connectors
    "SimplexSolverAdapter",
    "NLPConnectorFactory",
    "NLPOptimizationConnector",
    "ConfigurableNLPConnector",
    "SolverType",
]
