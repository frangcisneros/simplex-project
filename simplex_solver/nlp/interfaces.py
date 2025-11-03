"""
Define las estructuras base y contratos que deben cumplir todos los componentes
del sistema NLP para programación lineal.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from dataclasses import dataclass


@dataclass
class OptimizationProblem:
    """
    Representa un problema de optimización lineal extraído del lenguaje natural.

    Contiene toda la información necesaria: función objetivo (qué maximizar/minimizar),
    restricciones (límites y condiciones), y los nombres de las variables.
    """

    objective_type: str  # "maximize" o "minimize"
    objective_coefficients: List[float]
    constraints: List[
        Dict[str, Any]
    ]  # {"coefficients": [...], "operator": "<=", "rhs": float}
    variable_names: Optional[List[str]] = None

    def __post_init__(self):
        """
        Si no se especifican nombres para las variables, genera nombres por defecto
        del tipo x1, x2, x3, etc.
        """
        if self.variable_names is None:
            num_vars = len(self.objective_coefficients)
            self.variable_names = [f"x{i+1}" for i in range(num_vars)]


@dataclass
class NLPResult:
    """
    Encapsula el resultado del procesamiento de un texto en lenguaje natural.

    Incluye el problema extraído si tuvo éxito, o un mensaje de error si falló.
    También incluye un score de confianza que indica qué tan seguro está el modelo
    de la extracción realizada.
    """

    success: bool
    problem: Optional[OptimizationProblem] = None
    error_message: Optional[str] = None
    confidence_score: Optional[float] = None


class INLPProcessor(ABC):
    """
    Define el contrato para cualquier procesador de lenguaje natural.

    Un procesador toma texto en español y lo convierte en un problema de
    optimización estructurado que podemos resolver matemáticamente.
    """

    @abstractmethod
    def process_text(self, natural_language_text: str) -> NLPResult:
        """
        Toma una descripción en lenguaje natural y extrae el problema de optimización.

        Por ejemplo, convierte "Maximizar 3x + 2y sujeto a x + y <= 4" en una
        estructura OptimizationProblem con coeficientes y restricciones.

        Args:
            natural_language_text: Descripción del problema en lenguaje natural

        Returns:
            NLPResult con el problema extraído o un mensaje de error
        """
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """
        Verifica si el procesador está listo para usar.

        Chequea que el modelo NLP esté cargado, que las dependencias estén instaladas,
        y que haya suficiente memoria disponible.
        """
        pass


class IModelGenerator(ABC):
    """
    Define cómo convertir un problema de optimización a un formato específico de solver.

    Cada solver (Simplex, PuLP, OR-Tools) tiene su propio formato de entrada.
    Los generadores toman nuestro OptimizationProblem estándar y lo convierten
    al formato que necesita cada solver.
    """

    @abstractmethod
    def generate_model(self, problem: OptimizationProblem) -> Dict[str, Any]:
        """
        Convierte el problema a un formato listo para resolver.

        Por ejemplo, para Simplex necesitamos matrices y vectores (c, A, b).
        Para PuLP necesitamos objetos LpProblem. Esta función hace esa conversión.

        Args:
            problem: Problema de optimización estructurado

        Returns:
            Diccionario con el modelo en el formato del solver correspondiente
        """
        pass


class IOptimizationSolver(ABC):
    """
    Define cómo debe comportarse cualquier solver de optimización.

    Toma un modelo de optimización y encuentra la mejor solución posible,
    respetando todas las restricciones del problema.
    """

    @abstractmethod
    def solve(self, model: Dict[str, Any]) -> Dict[str, Any]:
        """
        Resuelve el problema de optimización y devuelve la solución.

        Ejecuta el algoritmo (Simplex, Branch & Bound, etc.) y encuentra
        los valores óptimos de las variables, junto con el valor de la
        función objetivo.

        Args:
            model: Modelo de optimización en el formato del solver

        Returns:
            Diccionario con la solución, el estado (óptimo, no factible, etc.)
            y valores de las variables
        """
        pass


class INLPConnector(ABC):
    """
    Orquesta el proceso completo: desde texto natural hasta la solución óptima.

    Conecta todos los pasos del pipeline: procesar el texto con NLP, generar el modelo
    matemático, y resolverlo con el solver. Es la pieza que une todo el sistema.
    """

    @abstractmethod
    def process_and_solve(self, natural_language_text: str) -> Dict[str, Any]:
        """
        Ejecuta el pipeline completo de optimización desde texto hasta solución.

        Toma una descripción en español, la procesa con NLP para extraer el problema,
        valida que esté bien formado, genera el modelo matemático, y lo resuelve.

        Args:
            natural_language_text: Descripción del problema en lenguaje natural

        Returns:
            Diccionario con la solución, el problema extraído, y detalles del proceso
        """
        pass


class IModelValidator(ABC):
    """
    Valida que los problemas extraídos por NLP sean matemáticamente correctos.

    Revisa que las dimensiones coincidan, que los operadores sean válidos,
    que los coeficientes sean numéricos, etc. Esto evita errores más adelante
    cuando intentemos resolver el problema.
    """

    @abstractmethod
    def validate(self, problem: OptimizationProblem) -> bool:
        """
        Chequea si el problema está bien formado y se puede resolver.

        Verifica dimensiones de matrices, tipos de datos, operadores válidos,
        y que no haya inconsistencias lógicas en las restricciones.

        Args:
            problem: Problema de optimización a validar

        Returns:
            True si pasa todas las validaciones, False si encuentra errores
        """
        pass

    @abstractmethod
    def get_validation_errors(self, problem: OptimizationProblem) -> List[str]:
        """
        Lista todos los problemas encontrados en la validación.

        Returns:
            Lista de mensajes de error describiendo cada problema encontrado
        """
        pass
