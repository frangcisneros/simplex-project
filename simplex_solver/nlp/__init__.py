"""
Sistema NLP para resolver problemas de optimización descritos en lenguaje natural.

Este paquete permite escribir problemas de programación lineal en español
(o cualquier lenguaje natural) y resolverlos automáticamente. El sistema
usa modelos de lenguaje para extraer la información matemática del texto,
la valida, genera el modelo, y lo resuelve con algoritmos de optimización.

Componentes principales:
- Procesadores NLP: Convierten texto a problemas estructurados.
- Generadores de modelos: Transforman los problemas a formatos específicos para solvers.
- Solvers: Resuelven el problema de optimización.
- Conectores: Orquestan todo el pipeline de procesamiento.

Uso básico:
    from nlp import NLPConnectorFactory, NLPModelType, SolverType

    # Crear un conector para procesar y resolver problemas
    connector = NLPConnectorFactory.create_connector(
        nlp_model_type=NLPModelType.FLAN_T5_SMALL,
        solver_type=SolverType.SIMPLEX
    )

    # Resolver un problema de optimización descrito en lenguaje natural
    result = connector.process_and_solve("Maximizar 3x + 2y sujeto a x + y <= 10")
"""

# Importación de interfaces principales del sistema NLP
from .interfaces import (
    OptimizationProblem,
    NLPResult,
    INLPProcessor,
    IModelGenerator,
    IOptimizationSolver,
    INLPConnector,
    IModelValidator,
)

# Configuración y constantes del sistema NLP
from .config import (
    NLPModelType,
    ModelConfig,
    PromptTemplates,
    ErrorMessages,
    DefaultSettings,
)

# Herramientas para análisis de complejidad y selección de modelos
from .complexity_analyzer import (
    ModelSelector,
    ComplexityAnalyzer,
    SystemAnalyzer,
    ProblemComplexity,
    SystemCapability,
)

# Procesadores NLP específicos
from .ollama_processor import OllamaNLPProcessor
from .processor import TransformerNLPProcessor, MockNLPProcessor

# Generadores de modelos para diferentes solvers
from .model_generator import (
    SimplexModelGenerator,
    PuLPModelGenerator,
    ORToolsModelGenerator,
    ModelValidator,
)

# Conectores para integrar procesamiento NLP y resolución de problemas
from .connector import (
    SimplexSolverAdapter,
    NLPConnectorFactory,
    NLPOptimizationConnector,
    SolverType,
)

# Definición de los elementos públicos del paquete
__all__ = [
    # Interfaces principales
    "OptimizationProblem",
    "NLPResult",
    "INLPProcessor",
    "IModelGenerator",
    "IOptimizationSolver",
    "INLPConnector",
    "IModelValidator",
    # Configuración
    "NLPModelType",
    "ModelConfig",
    "PromptTemplates",
    "ErrorMessages",
    "DefaultSettings",
    # Análisis de complejidad
    "ModelSelector",
    "ComplexityAnalyzer",
    "SystemAnalyzer",
    "ProblemComplexity",
    "SystemCapability",
    # Procesadores NLP
    "OllamaNLPProcessor",
    "TransformerNLPProcessor",
    "MockNLPProcessor",
    # Generadores de modelos
    "SimplexModelGenerator",
    "PuLPModelGenerator",
    "ORToolsModelGenerator",
    "ModelValidator",
    # Conectores
    "SimplexSolverAdapter",
    "NLPConnectorFactory",
    "NLPOptimizationConnector",
    "SolverType",
]
