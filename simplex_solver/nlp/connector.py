"""
Conectores que integran el procesamiento NLP con los solvers de optimización.

Orquestan todo el flujo: procesar texto -> validar problema -> generar modelo -> resolver.
Incluye adaptadores para usar el SimplexSolver existente sin modificarlo, y factories
para crear fácilmente configuraciones completas del sistema.
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
from .processor import MockNLPProcessor
from .ollama_processor import OllamaNLPProcessor
from .model_generator import SimplexModelGenerator, ModelValidator
from .problem_structure_detector import ProblemStructureDetector
from simplex_solver.solver import SimplexSolver
from .config import NLPModelType, DefaultSettings, ErrorMessages


class SolverType(Enum):
    """
    Enumeración de los tipos de solvers soportados.
    """

    SIMPLEX = "simplex"
    PULP = "pulp"
    ORTOOLS = "ortools"


class SimplexSolverAdapter(IOptimizationSolver):
    """
    Adaptador para integrar el SimplexSolver con el sistema NLP.

    Este adaptador traduce el formato del modelo generado por el sistema NLP
    al formato esperado por el SimplexSolver, y enriquece los resultados con
    nombres personalizados de variables si están disponibles.
    """

    def __init__(self):
        self.simplex_solver = SimplexSolver()
        self.logger = logging.getLogger(__name__)

    def solve(self, model: Dict[str, Any]) -> Dict[str, Any]:
        """
        Resuelve un modelo de optimización utilizando el SimplexSolver.

        Args:
            model: Diccionario que contiene las claves 'c', 'A', 'b', 'maximize',
                   y opcionalmente 'variable_names'.

        Returns:
            Diccionario con el estado de la solución, valores óptimos y otros detalles.
        """
        try:
            required_keys = ["c", "A", "b", "maximize"]
            missing_keys = [k for k in required_keys if k not in model]
            if missing_keys:
                raise ValueError(f"Faltan claves requeridas en el modelo: {missing_keys}")

            # DEBUG: Imprimir detalles del modelo generado
            print("=== DEBUG: Modelo generado para Simplex ===")
            for k, v in model.items():
                if k != "A":
                    print(f"{k}: {v}")
                else:
                    print(f"A: [matriz {len(v)}x{len(v[0]) if v else 0}]")
            print("constraint_types:", model.get("constraint_types"))
            print("==========================================")

            result = self.simplex_solver.solve(
                c=model["c"],
                A=model["A"],
                b=model["b"],
                constraint_types=model["constraint_types"],
                maximize=model["maximize"],
            )

            # Enriquecer resultado con nombres personalizados de variables
            if "variable_names" in model and result.get("status") == "optimal":
                var_names = model["variable_names"]
                if var_names and len(var_names) == len(model["c"]):
                    named_solution = {}
                    for i, name in enumerate(var_names):
                        old_key = f"x{i+1}"
                        if old_key in result["solution"]:
                            named_solution[name] = result["solution"][old_key]
                    result["named_solution"] = named_solution

            return result

        except Exception as e:
            self.logger.error(f"Error al resolver con SimplexSolver: {e}")
            return {"status": "error", "message": str(e)}


class NLPConnectorFactory:
    """
    Factory para crear conectores NLP completamente configurados.

    Simplifica la creación de un sistema completo al instanciar automáticamente
    todos los componentes necesarios (procesador NLP, generador de modelos, solver y validador).
    """

    @staticmethod
    def create_connector(
        nlp_model_type: Optional[NLPModelType] = None,  # None = auto-detectar
        solver_type: SolverType = SolverType.SIMPLEX,
        use_mock_nlp: bool = False,
        custom_config: Optional[Dict[str, Any]] = None,
    ) -> "NLPOptimizationConnector":
        """
        Construye un conector NLP completo con todos sus componentes.

        Args:
            nlp_model_type: Modelo de lenguaje a usar. Si es None, detecta automáticamente
                          el mejor modelo según las capacidades del sistema.
            solver_type: Tipo de solver a utilizar (actualmente solo SIMPLEX).
            use_mock_nlp: Si es True, utiliza un procesador NLP simulado para pruebas.
            custom_config: Configuración personalizada para el modelo NLP.

        Returns:
            NLPOptimizationConnector configurado y listo para usar.
        """
        # Auto-detectar el mejor modelo si no se especifica
        if nlp_model_type is None:
            nlp_model_type = DefaultSettings.get_optimal_model()

        # Crear procesador NLP
        if use_mock_nlp:
            nlp_processor = MockNLPProcessor()
        else:
            nlp_processor = OllamaNLPProcessor(nlp_model_type, custom_config=custom_config)

        # Crear generador de modelo
        if solver_type == SolverType.SIMPLEX:
            model_generator = SimplexModelGenerator()
        else:
            raise NotImplementedError(f"Solver type {solver_type} no implementado aún")

        # Crear solver
        if solver_type == SolverType.SIMPLEX:
            solver = SimplexSolverAdapter()
        else:
            raise NotImplementedError(f"Solver type {solver_type} no implementado aún")

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
    Conector principal que orquesta el pipeline completo de optimización NLP.

    Coordina los pasos desde el procesamiento del texto en lenguaje natural
    hasta la obtención de la solución óptima del problema de optimización.
    """

    def __init__(
        self,
        nlp_processor: INLPProcessor,
        model_generator: IModelGenerator,
        solver: IOptimizationSolver,
        validator: IModelValidator,
    ):
        """
        Inicializa el conector con los componentes necesarios.

        Args:
            nlp_processor: Procesador NLP para extraer problemas del texto.
            model_generator: Generador de modelos matemáticos para el solver.
            solver: Solver para resolver el problema de optimización.
            validator: Validador para verificar la validez del problema extraído.
        """
        self.nlp_processor = nlp_processor
        self.model_generator = model_generator
        self.solver = solver
        self.validator = validator
        self.structure_detector = ProblemStructureDetector()
        self.logger = logging.getLogger(__name__)

    def process_and_solve(self, natural_language_text: str) -> Dict[str, Any]:
        """
        Ejecuta el pipeline completo desde texto hasta solución óptima.

        Args:
            natural_language_text: Descripción del problema en lenguaje natural.

        Returns:
            Diccionario con los resultados del proceso, incluyendo solución,
            problema extraído, tiempo de procesamiento y análisis de estructura.
        """
        start_time = time.time()

        try:
            self.logger.info("Iniciando pipeline de optimización NLP")

            # Paso 1: Verificar disponibilidad del procesador NLP
            if not self.nlp_processor.is_available():
                return {
                    "success": False,
                    "error": ErrorMessages.MODEL_NOT_AVAILABLE,
                    "step_failed": "nlp_availability",
                }

            # Paso 2: Procesar texto con NLP
            self.logger.info("Paso 1: Procesando texto con NLP")
            nlp_result = self.nlp_processor.process_text(natural_language_text)

            if not nlp_result.success:
                return {
                    "success": False,
                    "error": nlp_result.error_message,
                    "step_failed": "nlp_processing",
                }

            if nlp_result.problem is None:
                return {
                    "success": False,
                    "error": "No se extrajo ningún problema del resultado NLP",
                    "step_failed": "problem_extraction",
                }

            # Paso 3: Validar el problema extraído
            self.logger.info("Paso 2: Validando el problema extraído")
            if not self.validator.validate(nlp_result.problem):
                validation_errors = self.validator.get_validation_errors(nlp_result.problem)
                return {
                    "success": False,
                    "error": f"Validación fallida: {', '.join(validation_errors)}",
                    "step_failed": "validation",
                    "validation_errors": validation_errors,
                }

            # Paso 4: Generar modelo
            self.logger.info("Paso 3: Generando modelo de optimización")
            model = self.model_generator.generate_model(nlp_result.problem)

            # Guardar si era un problema de minimización (para ajustar resultado)
            was_minimization = model.get("is_minimization", False)

            # Paso 5: Resolver modelo
            self.logger.info("Paso 4: Resolviendo modelo de optimización")
            solution = self.solver.solve(model)

            # Si el problema original era de minimización, ajustar el valor óptimo
            if was_minimization and solution.get("status") == "optimal":
                if "optimal_value" in solution:
                    solution["optimal_value"] = -solution["optimal_value"]
                    self.logger.info("Valor óptimo ajustado para problema de minimización")

            processing_time = time.time() - start_time

            # (Opcional) Análisis de estructura post-mortem para logging o warnings
            expected_structure = self.structure_detector.detect_structure(natural_language_text)
            problem_dict = {
                "variable_names": nlp_result.problem.variable_names or [],
                "objective_coefficients": nlp_result.problem.objective_coefficients,
            }
            is_valid, warnings = self.structure_detector.validate_extracted_variables(
                problem_dict, expected_structure
            )
            if not is_valid:
                self.logger.warning(f"Desajuste de estructura detectado: {warnings}")

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
                "structure_analysis": {
                    "detected_type": expected_structure["problem_type"],
                    "expected_variables": expected_structure["expected_variables"],
                    "extracted_variables": len(nlp_result.problem.variable_names or []),
                    "warnings": warnings,
                },
            }

            self.logger.info(f"Pipeline completado exitosamente en {processing_time:.2f}s")
            return result

        except Exception as e:
            processing_time = time.time() - start_time
            self.logger.error(f"Pipeline fallido: {e}", exc_info=True)

            return {
                "success": False,
                "error": f"Error en el pipeline: {str(e)}",
                "step_failed": "unknown",
                "processing_time": processing_time,
            }
