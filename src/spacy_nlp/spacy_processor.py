"""
Procesador principal que integra spaCy con el sistema de optimización.

Combina NER, Pattern Matching y post-procesamiento para extraer
problemas de optimización del texto en lenguaje natural.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import logging
from typing import Dict, Any, List, Optional
from nlp.interfaces import INLPProcessor, NLPResult, OptimizationProblem

from .entity_recognizer import OptimizationEntityRecognizer
from .pattern_matcher import OptimizationPatternMatcher


class SpacyNLPProcessor(INLPProcessor):
    """
    Procesador NLP usando spaCy para problemas de optimización.

    Combina:
    - Named Entity Recognition (entrenado)
    - Pattern Matching (reglas)
    - Post-procesamiento (validación y estructuración)

    Ventajas sobre regex:
    - Entiende contexto y semántica
    - Maneja variaciones lingüísticas
    - Aprende de ejemplos

    Ventajas sobre LLM:
    - 10-100x más rápido
    - Modelo más pequeño
    - Más predecible
    - No requiere GPU potente
    """

    def __init__(self, model_path: Optional[str] = None):
        """
        Args:
            model_path: Ruta al modelo entrenado. Si es None, usa modelo base + patterns.
        """
        self.logger = logging.getLogger(__name__)
        self.model_path = model_path

        # Inicializar componentes
        self.entity_recognizer = OptimizationEntityRecognizer(model_path)
        self.pattern_matcher = OptimizationPatternMatcher(
            self.entity_recognizer.nlp
            if self.entity_recognizer.is_available()
            else None
        )

        self.logger.info("SpacyNLPProcessor inicializado")

    def is_available(self) -> bool:
        """
        Verifica si el procesador está disponible.

        Returns:
            True si al menos pattern matcher está disponible
        """
        # Pattern matcher siempre está disponible
        # Entity recognizer es opcional (mejora precisión si está)
        return True

    def process_text(self, natural_language_text: str) -> NLPResult:
        """
        Procesa texto y extrae problema de optimización.

        Args:
            natural_language_text: Texto del problema

        Returns:
            NLPResult con problema extraído o error
        """
        self.logger.info("Procesando texto con spaCy")

        try:
            # 1. Extraer entidades si modelo está disponible
            entities = []
            if self.entity_recognizer.is_available():
                entities = self.entity_recognizer.extract_entities(
                    natural_language_text
                )
                self.logger.info(f"Extraídas {len(entities)} entidades")

            # 2. Buscar patrones
            patterns = self.pattern_matcher.find_patterns(natural_language_text)
            self.logger.info(f"Encontrados {len(patterns)} patrones")

            # 3. Extraer componentes estructurados
            problem_data = self._extract_structured_problem(
                natural_language_text, entities, patterns
            )

            # 4. Validar y construir OptimizationProblem
            if not self._validate_problem_data(problem_data):
                return NLPResult(
                    success=False,
                    problem=None,
                    error_message="No se pudo extraer problema válido",
                    confidence_score=0.0,
                )

            problem = self._build_optimization_problem(problem_data)

            # Calcular confianza
            confidence = self._calculate_confidence(problem_data, entities, patterns)

            self.logger.info(f"Problema extraído con confianza {confidence:.2f}")

            return NLPResult(
                success=True,
                problem=problem,
                confidence_score=confidence,
            )

        except Exception as e:
            self.logger.error(f"Error procesando texto: {e}", exc_info=True)
            return NLPResult(
                success=False,
                problem=None,
                error_message=f"Error en spaCy processor: {str(e)}",
                confidence_score=0.0,
            )

    def _extract_structured_problem(
        self, text: str, entities: List, patterns: List[Dict]
    ) -> Dict[str, Any]:
        """
        Combina información de entidades y patrones.

        Returns:
            Dict con componentes del problema
        """
        # Usar entity recognizer si está disponible
        if self.entity_recognizer.is_available():
            structured = self.entity_recognizer.extract_structured_problem(text)
        else:
            structured = {"variables": [], "coefficients": []}

        # Complementar con pattern matcher
        sections = self.pattern_matcher.identify_problem_sections(text)
        constraints = self.pattern_matcher.extract_constraint_expressions(text)
        terms = self.pattern_matcher.extract_term_with_coefficient(text)

        # Detectar tipo de objetivo
        objective_type = structured.get("objective_type")
        if not objective_type:
            # Intentar detectar con patterns
            if "maximizar" in text.lower() or "max" in text.lower():
                objective_type = "maximize"
            elif "minimizar" in text.lower() or "min" in text.lower():
                objective_type = "minimize"

        # Extraer variables únicas
        variables = set(structured.get("variables", []))
        for coef, var in terms:
            variables.add(var)

        # Construir coeficientes objetivo
        objective_coefficients = {}

        # Buscar coeficientes en la sección objetivo
        if sections.get("objective"):
            obj_terms = self.pattern_matcher.extract_term_with_coefficient(
                sections["objective"]
            )
            for coef, var in obj_terms:
                objective_coefficients[var] = coef

        return {
            "objective_type": objective_type,
            "variables": sorted(list(variables)),
            "objective_coefficients": objective_coefficients,
            "constraints": constraints,
            "sections": sections,
            "raw_terms": terms,
        }

    def _validate_problem_data(self, problem_data: Dict[str, Any]) -> bool:
        """
        Valida que el problema tenga los componentes mínimos.

        Returns:
            True si el problema es válido
        """
        # Debe tener tipo de objetivo
        if not problem_data.get("objective_type"):
            self.logger.warning("No se detectó tipo de objetivo")
            return False

        # Debe tener al menos una variable
        if not problem_data.get("variables"):
            self.logger.warning("No se detectaron variables")
            return False

        # Debe tener coeficientes objetivo
        if not problem_data.get("objective_coefficients"):
            self.logger.warning("No se detectaron coeficientes objetivo")
            return False

        return True

    def _build_optimization_problem(
        self, problem_data: Dict[str, Any]
    ) -> OptimizationProblem:
        """
        Construye OptimizationProblem desde los datos extraídos.

        Args:
            problem_data: Datos estructurados del problema

        Returns:
            OptimizationProblem
        """
        variables = problem_data["variables"]
        obj_coef_dict = problem_data["objective_coefficients"]

        # Construir lista de coeficientes en orden de variables
        objective_coefficients = []
        for var in variables:
            coef = obj_coef_dict.get(var, 0.0)
            objective_coefficients.append(coef)

        # Convertir restricciones
        constraints = []
        for const in problem_data["constraints"]:
            # Construir coeficientes en orden de variables
            coefficients = []
            terms_dict = {var: coef for coef, var in const["terms"]}

            for var in variables:
                coef = terms_dict.get(var, 0.0)
                coefficients.append(coef)

            constraints.append(
                {
                    "coefficients": coefficients,
                    "operator": const["operator"],
                    "rhs": const["rhs"],
                }
            )

        return OptimizationProblem(
            objective_type=problem_data["objective_type"],
            objective_coefficients=objective_coefficients,
            constraints=constraints,
            variable_names=variables,
        )

    def _calculate_confidence(
        self, problem_data: Dict, entities: List, patterns: List
    ) -> float:
        """
        Calcula score de confianza basado en lo extraído.

        Returns:
            Score entre 0 y 1
        """
        confidence = 0.5  # Base

        # Bonus por tener objetivo claro
        if problem_data.get("objective_type"):
            confidence += 0.2

        # Bonus por tener variables
        if len(problem_data.get("variables", [])) > 0:
            confidence += 0.1

        # Bonus por tener restricciones
        if len(problem_data.get("constraints", [])) > 0:
            confidence += 0.1

        # Bonus por entidades reconocidas
        if len(entities) > 5:
            confidence += 0.05

        # Bonus por patrones encontrados
        if len(patterns) > 3:
            confidence += 0.05

        return min(1.0, confidence)

    def analyze_text(self, text: str) -> Dict[str, Any]:
        """
        Analiza texto y retorna información detallada.

        Útil para debugging y visualización.

        Returns:
            Dict con análisis completo
        """
        entities = []
        if self.entity_recognizer.is_available():
            entities = self.entity_recognizer.extract_entities(text)

        patterns = self.pattern_matcher.find_patterns(text)
        sections = self.pattern_matcher.identify_problem_sections(text)
        constraints = self.pattern_matcher.extract_constraint_expressions(text)
        terms = self.pattern_matcher.extract_term_with_coefficient(text)

        return {
            "entities": [(e.text, e.label) for e in entities],
            "patterns": patterns,
            "sections": sections,
            "constraints": constraints,
            "terms": terms,
            "n_entities": len(entities),
            "n_patterns": len(patterns),
            "n_constraints": len(constraints),
        }

    def display_analysis(self, text: str):
        """
        Muestra análisis completo del texto de forma visual.

        Args:
            text: Texto a analizar
        """
        print(f"\n{'='*70}")
        print("ANÁLISIS COMPLETO CON SPACY")
        print("=" * 70)

        # Entidades
        if self.entity_recognizer.is_available():
            self.entity_recognizer.display_entities(text)

        # Patrones
        self.pattern_matcher.display_matches(text)

        # Análisis completo
        analysis = self.analyze_text(text)

        print(f"\n{'='*70}")
        print("RESUMEN")
        print("=" * 70)
        print(f"Entidades encontradas: {analysis['n_entities']}")
        print(f"Patrones encontrados: {analysis['n_patterns']}")
        print(f"Restricciones extraídas: {analysis['n_constraints']}")
        print(f"Términos con coeficientes: {len(analysis['terms'])}")
