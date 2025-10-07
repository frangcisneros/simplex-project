"""
Sistema NLP para resolver problemas de optimización descritos en lenguaje natural.

Este paquete permite escribir problemas de programación lineal en español
(o cualquier lenguaje natural) y resolverlos automáticamente. El sistema
usa modelos de lenguaje para extraer la información matemática del texto,
la valida, genera el modelo, y lo resuelve con algoritmos de optimización.

Componentes principales:
- Procesadores NLP: Convierten texto a problemas estructurados
- Generadores de modelos: Transforman a formatos de solver específicos
- Solvers: Resuelven el problema de optimización
- Conectores: Orquestan todo el pipeline

Uso básico:
    from nlp import NLPConnectorFactory, NLPModelType, SolverType

    connector = NLPConnectorFactory.create_connector(
        nlp_model_type=NLPModelType.FLAN_T5_SMALL,
        solver_type=SolverType.SIMPLEX
    )

    result = connector.process_and_solve("Maximizar 3x + 2y sujeto a x + y <= 10")
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

from .complexity_analyzer import (
    ModelSelector,
    ComplexityAnalyzer,
    SystemAnalyzer,
    ProblemComplexity,
    SystemCapability,
)

from .ollama_processor import OllamaNLPProcessor
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
    # Complexity analysis
    "ModelSelector",
    "ComplexityAnalyzer",
    "SystemAnalyzer",
    "ProblemComplexity",
    "SystemCapability",
    # Processors
    "OllamaNLPProcessor",
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
