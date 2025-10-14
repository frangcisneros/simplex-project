"""
Extractor principal que coordina todos los parsers regex.

Usa VariableDetector, ObjectiveParser y ConstraintParser
para extraer todos los componentes de un problema.
"""

import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass

from .variable_detector import VariableDetector, Variable
from .objective_parser import ObjectiveParser, ObjectiveFunction
from .constraint_parser import ConstraintParser, Constraint
from .pattern_library import PatternLibrary


@dataclass
class ExtractedProblem:
    """Representa un problema completo extraído."""

    variables: list[Variable]
    objective: ObjectiveFunction
    constraints: list[Constraint]
    problem_type: str  # Tipo detectado (production, transportation, etc.)
    raw_text: str
    confidence_score: float = 1.0  # Regex siempre tiene confianza alta


class RegexExtractor:
    """
    Coordina la extracción completa de un problema usando regex.

    Orquesta el uso de todos los parsers especializados y
    proporciona el resultado en un formato unificado.
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.pattern_library = PatternLibrary()
        self.variable_detector = VariableDetector()
        self.objective_parser = ObjectiveParser()
        self.constraint_parser = ConstraintParser()

    def extract_problem(self, text: str) -> Optional[ExtractedProblem]:
        """
        Extrae todos los componentes del problema del texto.

        Proceso:
        1. Limpiar y preprocesar texto
        2. Detectar tipo de problema
        3. Detectar variables
        4. Extraer función objetivo
        5. Extraer restricciones
        6. Validar coherencia

        Args:
            text: Texto del problema en lenguaje natural

        Returns:
            ExtractedProblem con todos los componentes o None si falla
        """
        self.logger.info("Iniciando extracción con regex")

        try:
            # 1. Limpiar texto
            cleaned_text = self.pattern_library.clean_text(text)

            # 2. Detectar tipo de problema (contexto)
            problem_type = self.pattern_library.detect_problem_type(cleaned_text)
            self.logger.info(f"Tipo de problema detectado: {problem_type}")

            # 3. Detectar variables
            variables = self.variable_detector.detect_variables(cleaned_text)

            if not variables:
                self.logger.error("No se detectaron variables")
                return None

            # Inferir variables faltantes en rangos
            variables = self.variable_detector.infer_variable_range(variables)

            variable_names = [v.name for v in variables]
            self.logger.info(f"Variables detectadas: {variable_names}")

            # 4. Extraer función objetivo
            objective = self.objective_parser.parse_objective(
                cleaned_text, variable_names
            )

            if not objective:
                self.logger.error("No se pudo extraer función objetivo")
                return None

            # 5. Extraer restricciones
            constraints = self.constraint_parser.parse_constraints(
                cleaned_text, variable_names
            )

            if not constraints:
                self.logger.warning("No se encontraron restricciones explícitas")

            # 6. Validar coherencia
            validation_errors = self._validate_problem(
                variables, objective, constraints
            )

            if validation_errors:
                self.logger.warning(f"Errores de validación: {validation_errors}")
                # No retornar None, pero registrar los warnings

            # Construir resultado
            problem = ExtractedProblem(
                variables=variables,
                objective=objective,
                constraints=constraints,
                problem_type=problem_type,
                raw_text=text,
                confidence_score=self._calculate_confidence(
                    variables, objective, constraints, validation_errors
                ),
            )

            self.logger.info("Extracción completada exitosamente")
            return problem

        except Exception as e:
            self.logger.error(f"Error durante extracción: {e}", exc_info=True)
            return None

    def _validate_problem(
        self,
        variables: list[Variable],
        objective: ObjectiveFunction,
        constraints: list[Constraint],
    ) -> list[str]:
        """
        Valida que el problema extraído sea coherente.

        Verifica:
        - Variables en objetivo están declaradas
        - Variables en restricciones están declaradas
        - Hay al menos una restricción
        """
        errors = []

        variable_names = [v.name for v in variables]

        # Validar función objetivo
        _, obj_errors = self.objective_parser.validate_objective_with_variables(
            objective, variable_names
        )
        errors.extend(obj_errors)

        # Validar restricciones
        _, const_errors = self.constraint_parser.validate_constraints_with_variables(
            constraints, variable_names
        )
        errors.extend(const_errors)

        # Verificar que haya restricciones
        if not constraints:
            errors.append("No se encontraron restricciones")

        return errors

    def _calculate_confidence(
        self,
        variables: list[Variable],
        objective: ObjectiveFunction,
        constraints: list[Constraint],
        validation_errors: list[str],
    ) -> float:
        """
        Calcula un score de confianza basado en lo extraído.

        Regex es determinista, pero podemos dar menor confianza
        si hay problemas de validación.
        """
        base_confidence = 1.0

        # Reducir confianza por errores de validación
        confidence = base_confidence - (len(validation_errors) * 0.1)

        # Bonificar si todo está bien estructurado
        if (
            len(variables) > 0
            and len(objective.coefficients) > 0
            and len(constraints) > 0
        ):
            confidence = min(1.0, confidence + 0.1)

        return max(0.0, confidence)

    def extract_and_format(self, text: str) -> Dict[str, Any]:
        """
        Extrae el problema y lo formatea para logging/display.

        Returns:
            Dict con información formateada del problema
        """
        problem = self.extract_problem(text)

        if not problem:
            return {
                "success": False,
                "error": "No se pudo extraer el problema",
            }

        return {
            "success": True,
            "problem_type": problem.problem_type,
            "variables": [v.name for v in problem.variables],
            "objective": self.objective_parser.format_objective_for_display(
                problem.objective
            ),
            "constraints": [
                self.constraint_parser.format_constraint_for_display(c)
                for c in problem.constraints
            ],
            "confidence": problem.confidence_score,
        }
