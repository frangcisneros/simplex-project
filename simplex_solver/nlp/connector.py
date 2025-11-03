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
    """Tipos de solver soportados."""

    SIMPLEX = "simplex"
    PULP = "pulp"
    ORTOOLS = "ortools"


class SimplexSolverAdapter(IOptimizationSolver):
    """
    Permite usar el SimplexSolver original con el nuevo sistema NLP.

    El SimplexSolver ya existía antes del sistema NLP y tiene su propia interfaz.
    Este adaptador traduce entre lo que espera SimplexSolver (c, A, b) y lo que
    devuelve el modelo generator. También enriquece los resultados con nombres
    de variables personalizados.
    """

    def __init__(self):
        self.simplex_solver = SimplexSolver()
        self.logger = logging.getLogger(__name__)

    def solve(self, model: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ejecuta el algoritmo Simplex y devuelve la solución.

        Valida que el modelo tenga las claves necesarias (c, A, b, maximize),
        llama al SimplexSolver, y si hay variable_names personalizado,
        mapea la solución de x1, x2, x3... a los nombres reales.

        Args:
            model: Modelo con claves 'c', 'A', 'b', 'maximize' y opcionalmente 'variable_names'

        Returns:
            Diccionario con 'status', 'solution', 'objective_value', etc.
        """
        try:
            required_keys = ["c", "A", "b", "maximize"]
            missing_keys = [k for k in required_keys if k not in model]
            if missing_keys:
                raise ValueError(f"Missing required keys in model: {missing_keys}")

            # DEBUG: Print model and constraint_types
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
    Crea conectores NLP configurados y listos para usar.

    En vez de instanciar manualmente cada componente (procesador, generador, solver, validador),
    esta factory lo hace automáticamente con la configuración adecuada. Simplifica
    la creación del sistema completo.
    """

    @staticmethod
    def create_connector(
        nlp_model_type: NLPModelType = DefaultSettings.DEFAULT_MODEL,
        solver_type: SolverType = SolverType.SIMPLEX,
        use_mock_nlp: bool = False,
        custom_config: Optional[Dict[str, Any]] = None,
    ) -> "NLPOptimizationConnector":
        """
        Construye un conector NLP completo con todos sus componentes.

        Instancia el procesador NLP (real o mock), el generador de modelos
        para el solver elegido, el solver mismo, y el validador. Devuelve
        todo conectado y listo para procesar problemas.

        Args:
            nlp_model_type: Modelo de lenguaje a usar (FLAN-T5, Mistral, etc.)
            solver_type: Qué solver usar (por ahora solo SIMPLEX está implementado)
            use_mock_nlp: Si True, usa un procesador simple para testing
            custom_config: Parámetros personalizados para el modelo NLP

        Returns:
            NLPOptimizationConnector configurado y listo para usar
        """
        # Crear procesador NLP
        if use_mock_nlp:
            nlp_processor = MockNLPProcessor()
        else:
            # Usar Ollama por defecto (más simple y confiable)
            nlp_processor = OllamaNLPProcessor(nlp_model_type, custom_config=custom_config)

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
    Orquesta el pipeline completo: texto -> NLP -> modelo -> solución.

    Este es el componente principal del sistema. Recibe texto en lenguaje natural
    y coordina todos los pasos:
    1. Procesar el texto con NLP para extraer el problema
    2. Validar que el problema esté bien formado
    3. Generar el modelo matemático
    4. Resolver con el solver
    5. Devolver resultados completos

    Maneja errores en cada paso y proporciona información detallada sobre
    qué salió mal si algo falla.
    """

    def __init__(
        self,
        nlp_processor: INLPProcessor,
        model_generator: IModelGenerator,
        solver: IOptimizationSolver,
        validator: IModelValidator,
    ):
        """
        Conecta todos los componentes del sistema.

        Recibe las instancias de cada componente ya configuradas. Esto permite
        flexibilidad: podemos usar cualquier implementación que cumpla las interfaces.

        Args:
            nlp_processor: Procesador para extraer problemas del texto
            model_generator: Generador para convertir a formato del solver
            solver: Algoritmo que resuelve el problema de optimización
            validator: Validador para chequear que el problema esté bien formado
        """
        self.nlp_processor = nlp_processor
        self.model_generator = model_generator
        self.solver = solver
        self.validator = validator
        self.structure_detector = ProblemStructureDetector()
        self.logger = logging.getLogger(__name__)

    def process_and_solve(self, natural_language_text: str) -> Dict[str, Any]:
        """
        Ejecuta el proceso completo desde texto hasta la solución óptima.

        Pasos:
        1. Verifica que el procesador NLP esté disponible
        2. Procesa el texto para extraer el problema
        3. Valida que el problema sea matemáticamente correcto
        4. Genera el modelo en el formato del solver
        5. Resuelve el problema de optimización
        6. Devuelve solución con metadata (tiempo, confianza, problema extraído)

        Si algo falla en cualquier paso, devuelve un dict con success=False
        y detalles del error.

        Args:
            natural_language_text: Descripción del problema en español

        Returns:
            Dict con 'success', 'solution', 'extracted_problem', 'processing_time', etc.
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

            if nlp_result.problem is None:
                return {
                    "success": False,
                    "error": "No problem extracted from NLP result",
                    "step_failed": "problem_extraction",
                }

            # Paso 3: Validar el problema extraído
            self.logger.info("Step 2: Validating extracted problem")
            if not self.validator.validate(nlp_result.problem):
                validation_errors = self.validator.get_validation_errors(nlp_result.problem)
                return {
                    "success": False,
                    "error": f"Validation failed: {', '.join(validation_errors)}",
                    "step_failed": "validation",
                    "validation_errors": validation_errors,
                }

            # Paso 4: Generar modelo
            self.logger.info("Step 3: Generating optimization model")
            model = self.model_generator.generate_model(nlp_result.problem)

            # Guardar si era un problema de minimización (para ajustar resultado)
            was_minimization = model.get("is_minimization", False)

            # Paso 5: Resolver modelo
            self.logger.info("Step 4: Solving optimization model")
            solution = self.solver.solve(model)

            # Si el problema original era de minimización, ajustar el valor óptimo
            if was_minimization and solution.get("status") == "optimal":
                if "optimal_value" in solution:
                    solution["optimal_value"] = -solution["optimal_value"]
                    self.logger.info(f"Adjusted optimal value for minimization problem")

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
                self.logger.warning(f"Structure mismatch detected: {warnings}")

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

            self.logger.info(f"Pipeline completed successfully in {processing_time:.2f}s")
            return result

        except Exception as e:
            processing_time = time.time() - start_time
            self.logger.error(f"Pipeline failed: {e}", exc_info=True)

            return {
                "success": False,
                "error": f"Pipeline error: {str(e)}",
                "step_failed": "unknown",
                "processing_time": processing_time,
            }
