"""
Interfaces y abstracciones para el sistema NLP de programación lineal.
Siguiendo principios SOLID para mantener bajo acoplamiento y alta cohesión.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from dataclasses import dataclass


@dataclass
class OptimizationProblem:
    """Estructura de datos para representar un problema de optimización."""

    objective_type: str  # "maximize" o "minimize"
    objective_coefficients: List[float]
    constraints: List[
        Dict[str, Any]
    ]  # {"coefficients": [...], "operator": "<=", "rhs": float}
    variable_names: Optional[List[str]] = None

    def __post_init__(self):
        if self.variable_names is None:
            num_vars = len(self.objective_coefficients)
            self.variable_names = [f"x{i+1}" for i in range(num_vars)]


@dataclass
class NLPResult:
    """Resultado del procesamiento de lenguaje natural."""

    success: bool
    problem: Optional[OptimizationProblem] = None
    error_message: Optional[str] = None
    confidence_score: Optional[float] = None


class INLPProcessor(ABC):
    """
    Interfaz para procesadores de lenguaje natural.

    Principio de Responsabilidad Única: Solo se encarga del procesamiento NLP.
    Principio Abierto/Cerrado: Abierto para extensión con nuevos modelos.
    """

    @abstractmethod
    def process_text(self, natural_language_text: str) -> NLPResult:
        """
        Procesa texto en lenguaje natural y extrae información de optimización.

        Args:
            natural_language_text: Descripción del problema en lenguaje natural

        Returns:
            NLPResult con el problema extraído o error
        """
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Verifica si el procesador está disponible y configurado correctamente."""
        pass


class IModelGenerator(ABC):
    """
    Interfaz para generadores de modelos de optimización.

    Principio de Inversión de Dependencia: Depende de abstracciones, no de concreciones.
    """

    @abstractmethod
    def generate_model(self, problem: OptimizationProblem) -> Dict[str, Any]:
        """
        Genera un modelo de optimización a partir de la estructura del problema.

        Args:
            problem: Problema de optimización estructurado

        Returns:
            Diccionario con el modelo generado (formato depende de la implementación)
        """
        pass


class IOptimizationSolver(ABC):
    """
    Interfaz para solvers de optimización.

    Principio de Sustitución de Liskov: Cualquier implementación debe ser intercambiable.
    """

    @abstractmethod
    def solve(self, model: Dict[str, Any]) -> Dict[str, Any]:
        """
        Resuelve el modelo de optimización.

        Args:
            model: Modelo de optimización

        Returns:
            Diccionario con la solución
        """
        pass


class INLPConnector(ABC):
    """
    Interfaz para conectores que integran NLP con solvers existentes.

    Principio de Segregación de Interfaces: Interface específica para la integración.
    """

    @abstractmethod
    def process_and_solve(self, natural_language_text: str) -> Dict[str, Any]:
        """
        Pipeline completo: texto natural -> NLP -> modelo -> solución.

        Args:
            natural_language_text: Descripción del problema

        Returns:
            Resultado de la optimización
        """
        pass


class IModelValidator(ABC):
    """Interfaz para validadores de modelos generados por NLP."""

    @abstractmethod
    def validate(self, problem: OptimizationProblem) -> bool:
        """
        Valida que el problema extraído sea coherente y resolvible.

        Args:
            problem: Problema de optimización a validar

        Returns:
            True si es válido, False en caso contrario
        """
        pass

    @abstractmethod
    def get_validation_errors(self, problem: OptimizationProblem) -> List[str]:
        """Retorna lista de errores de validación si los hay."""
        pass
