"""
Conectores para integrar NLP con solvers de optimización.
Implementa el patrón Adapter y Factory para mantener bajo acoplamiento.
"""

import logging
import time
from typing import Dict, Any, Optional, Union
from enum import Enum

from .interfaces import (
    INLPConnector,
    INLPProcessor,
    IModelGenerator,
    IOptimizationSolver,
    IModelValidator,
)
from .processor import TransformerNLPProcessor, MockNLPProcessor
from .model_generator import SimplexModelGenerator, ModelValidator
import sys
from pathlib import Path

# Agregar la carpeta padre al path para importar solver
sys.path.insert(0, str(Path(__file__).parent.parent))
from solver import SimplexSolver
from .config import NLPModelType, DefaultSettings, ErrorMessages


class SolverType(Enum):
    """Tipos de solver soportados."""

    SIMPLEX = "simplex"
    PULP = "pulp"
    ORTOOLS = "ortools"


class SimplexSolverAdapter(IOptimizationSolver):
    """
    Adapter para integrar SimplexSolver existente con la nueva arquitectura.

    Principios SOLID:
    - SRP: Solo adapta SimplexSolver a la interfaz IOptimizationSolver
    - OCP: Permite usar SimplexSolver sin modificar su código
    - LSP: Implementa completamente IOptimizationSolver
    - ISP: Interface específica para solvers
    - DIP: Depende de abstracciones
    """

    def __init__(self):
        self.simplex_solver = SimplexSolver()
        self.logger = logging.getLogger(__name__)

    def solve(self, model: Dict[str, Any]) -> Dict[str, Any]:
        """
        Resuelve el modelo usando SimplexSolver.

        Args:
            model: Modelo con claves 'c', 'A', 'b', 'maximize'

        Returns:
            Resultado de la optimización
        """
        try:
            required_keys = ["c", "A", "b", "maximize"]
            missing_keys = [k for k in required_keys if k not in model]
            if missing_keys:
                raise ValueError(f"Missing required keys in model: {missing_keys}")

            result = self.simplex_solver.solve(
                c=model["c"], A=model["A"], b=model["b"], maximize=model["maximize"]
            )

            # Enriquecer resultado con información adicional
            if "variable_names" in model and result.get("status") == "optimal":
                var_names = model["variable_names"]
                if var_names and len(var_names) == len(model["c"]):
                    # Mapear variables con nombres personalizados
                    named_solution = {}
                    for i, name in enumerate(var_names):
                        old_key = f"x{i+1}"
                        if old_key in result["solution"]:
                            named_solution[name] = result["solution"][old_key]
                    result["named_solution"] = named_solution

            return result

        except Exception as e:
            self.logger.error(f"Error solving with SimplexSolver: {e}")
            return {"status": "error", "message": str(e)}


class NLPConnectorFactory:
    """
    Factory para crear conectores NLP según la configuración.

    Principio de responsabilidad única: Solo se encarga de crear conectores.
    Patrón Factory: Encapsula la lógica de creación de objetos complejos.
    """

    @staticmethod
    def create_connector(
        nlp_model_type: NLPModelType = DefaultSettings.DEFAULT_MODEL,
        solver_type: SolverType = SolverType.SIMPLEX,
        use_mock_nlp: bool = False,
        custom_config: Optional[Dict[str, Any]] = None,
    ) -> "NLPOptimizationConnector":
        """
        Crea un conector NLP configurado.

        Args:
            nlp_model_type: Tipo de modelo NLP
            solver_type: Tipo de solver a usar
            use_mock_nlp: Si usar mock NLP para testing
            custom_config: Configuración personalizada

        Returns:
            Conector NLP configurado
        """
        # Crear procesador NLP
        if use_mock_nlp:
            nlp_processor = MockNLPProcessor()
        else:
            nlp_processor = TransformerNLPProcessor(nlp_model_type, custom_config)

        # Crear generador de modelo
        if solver_type == SolverType.SIMPLEX:
            model_generator = SimplexModelGenerator()
        else:
            # Aquí se pueden agregar otros generadores
            raise NotImplementedError(f"Solver type {solver_type} not implemented yet")

        # Crear solver
        if solver_type == SolverType.SIMPLEX:
            solver = SimplexSolverAdapter()
        else:
            raise NotImplementedError(f"Solver type {solver_type} not implemented yet")

        # Crear validador
        validator = ModelValidator()

        return NLPOptimizationConnector(
            nlp_processor=nlp_processor,
            model_generator=model_generator,
            solver=solver,
            validator=validator,
        )


class NLPOptimizationConnector(INLPConnector):
    """
    Conector principal que orquesta el pipeline completo NLP -> Modelo -> Solución.

    Principios SOLID aplicados:
    - SRP: Solo se encarga de orquestar el pipeline
    - OCP: Extensible mediante inyección de dependencias
    - LSP: Implementa completamente INLPConnector
    - ISP: Interface específica para conectores
    - DIP: Depende solo de abstracciones (interfaces)

    Patrón de diseño: Facade - Proporciona interfaz simple para subsistema complejo.
    """

    def __init__(
        self,
        nlp_processor: INLPProcessor,
        model_generator: IModelGenerator,
        solver: IOptimizationSolver,
        validator: IModelValidator,
    ):
        """
        Inicializa el conector con todas las dependencias.

        Args:
            nlp_processor: Procesador de lenguaje natural
            model_generator: Generador de modelos
            solver: Solver de optimización
            validator: Validador de modelos
        """
        self.nlp_processor = nlp_processor
        self.model_generator = model_generator
        self.solver = solver
        self.validator = validator
        self.logger = logging.getLogger(__name__)

    def process_and_solve(self, natural_language_text: str) -> Dict[str, Any]:
        """
        Pipeline completo: texto -> NLP -> modelo -> solución.

        Args:
            natural_language_text: Descripción del problema en lenguaje natural

        Returns:
            Resultado completo del proceso
        """
        start_time = time.time()

        try:
            self.logger.info("Starting NLP optimization pipeline")

            # Paso 1: Verificar disponibilidad del procesador NLP
            if not self.nlp_processor.is_available():
                return {
                    "success": False,
                    "error": ErrorMessages.MODEL_NOT_AVAILABLE,
                    "step_failed": "nlp_availability",
                }

            # Paso 2: Procesar texto con NLP
            self.logger.info("Step 1: Processing text with NLP")
            nlp_result = self.nlp_processor.process_text(natural_language_text)

            if not nlp_result.success:
                return {
                    "success": False,
                    "error": nlp_result.error_message,
                    "step_failed": "nlp_processing",
                }

            # Paso 3: Validar problema extraído
            self.logger.info("Step 2: Validating extracted problem")
            if nlp_result.problem is None:
                return {
                    "success": False,
                    "error": "No problem extracted from NLP result",
                    "step_failed": "problem_extraction",
                }

            if not self.validator.validate(nlp_result.problem):
                validation_errors = self.validator.get_validation_errors(
                    nlp_result.problem
                )
                return {
                    "success": False,
                    "error": f"Validation failed: {', '.join(validation_errors)}",
                    "step_failed": "validation",
                    "validation_errors": validation_errors,
                }

            # Paso 4: Generar modelo
            self.logger.info("Step 3: Generating optimization model")
            model = self.model_generator.generate_model(nlp_result.problem)

            # Paso 5: Resolver modelo
            self.logger.info("Step 4: Solving optimization model")
            solution = self.solver.solve(model)

            processing_time = time.time() - start_time

            # Construir resultado completo
            result = {
                "success": True,
                "solution": solution,
                "extracted_problem": {
                    "objective_type": nlp_result.problem.objective_type,
                    "objective_coefficients": nlp_result.problem.objective_coefficients,
                    "constraints": nlp_result.problem.constraints,
                    "variable_names": nlp_result.problem.variable_names,
                },
                "nlp_confidence": nlp_result.confidence_score,
                "processing_time": processing_time,
                "pipeline_steps": {
                    "nlp_processing": "completed",
                    "validation": "completed",
                    "model_generation": "completed",
                    "optimization": "completed",
                },
            }

            self.logger.info(
                f"Pipeline completed successfully in {processing_time:.2f}s"
            )
            return result

        except Exception as e:
            processing_time = time.time() - start_time
            self.logger.error(f"Pipeline failed: {e}")

            return {
                "success": False,
                "error": f"Pipeline error: {str(e)}",
                "step_failed": "unknown",
                "processing_time": processing_time,
            }

    def health_check(self) -> Dict[str, Any]:
        """
        Verifica el estado de todos los componentes.

        Returns:
            Estado de salud del conector
        """
        health = {"overall_status": "healthy", "components": {}}

        try:
            # Verificar NLP processor
            health["components"]["nlp_processor"] = {
                "status": (
                    "healthy" if self.nlp_processor.is_available() else "unhealthy"
                ),
                "type": type(self.nlp_processor).__name__,
            }

            # Verificar otros componentes (por ahora asumimos que están bien si se instanciaron)
            health["components"]["model_generator"] = {
                "status": "healthy",
                "type": type(self.model_generator).__name__,
            }

            health["components"]["solver"] = {
                "status": "healthy",
                "type": type(self.solver).__name__,
            }

            health["components"]["validator"] = {
                "status": "healthy",
                "type": type(self.validator).__name__,
            }

            # Determinar estado general
            if any(
                comp["status"] == "unhealthy" for comp in health["components"].values()
            ):
                health["overall_status"] = "degraded"

        except Exception as e:
            health["overall_status"] = "unhealthy"
            health["error"] = str(e)

        return health


class ConfigurableNLPConnector:
    """
    Conector configurable que permite cambiar componentes dinámicamente.
    Útil para experimentación y testing.
    """

    def __init__(self):
        self.connector: Optional[NLPOptimizationConnector] = None
        self.logger = logging.getLogger(__name__)

    def configure(
        self,
        nlp_model_type: NLPModelType = DefaultSettings.DEFAULT_MODEL,
        solver_type: SolverType = SolverType.SIMPLEX,
        use_mock_nlp: bool = False,
        custom_config: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Configura el conector con los parámetros especificados.

        Returns:
            True si la configuración fue exitosa
        """
        try:
            self.connector = NLPConnectorFactory.create_connector(
                nlp_model_type=nlp_model_type,
                solver_type=solver_type,
                use_mock_nlp=use_mock_nlp,
                custom_config=custom_config,
            )

            # Verificar que todo esté funcionando
            health = self.connector.health_check()
            if health["overall_status"] in ["healthy", "degraded"]:
                self.logger.info("Connector configured successfully")
                return True
            else:
                self.logger.error(f"Connector unhealthy after configuration: {health}")
                return False

        except Exception as e:
            self.logger.error(f"Error configuring connector: {e}")
            return False

    def process_and_solve(self, natural_language_text: str) -> Dict[str, Any]:
        """Procesa texto si el conector está configurado."""
        if not self.connector:
            return {
                "success": False,
                "error": "Connector not configured. Call configure() first.",
                "step_failed": "configuration",
            }

        return self.connector.process_and_solve(natural_language_text)

    def get_status(self) -> Dict[str, Any]:
        """Obtiene el estado actual del conector."""
        if not self.connector:
            return {"configured": False, "status": "not_configured"}

        health = self.connector.health_check()
        return {
            "configured": True,
            "status": health["overall_status"],
            "components": health["components"],
        }
