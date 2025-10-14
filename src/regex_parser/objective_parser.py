"""
Parser de función objetivo usando expresiones regulares.

Extrae y parsea la función objetivo de problemas de optimización:
- Tipo (maximizar/minimizar)
- Coeficientes de cada variable
- Términos constantes

Soporta formatos como:
- "Maximizar Z = 3x + 2y"
- "min: 5x1 - 2x2 + x3"
- "Maximizar beneficio = 100*producto_A + 80*producto_B"
"""

import re
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import logging


@dataclass
class ObjectiveFunction:
    """Representa una función objetivo parseada."""

    objective_type: str  # "maximize" o "minimize"
    coefficients: Dict[str, float]  # {variable_name: coefficient}
    constant_term: float = 0.0
    original_expression: str = ""


class ObjectiveParser:
    """
    Parsea funciones objetivo de problemas de optimización.

    Usa regex para identificar el tipo de optimización y extraer
    los coeficientes de cada variable.
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)

        # Patrones para detectar tipo de objetivo
        self.maximize_pattern = re.compile(
            r"\b(maximizar|maximice|maximiza|max|maximize)\b", re.IGNORECASE
        )
        self.minimize_pattern = re.compile(
            r"\b(minimizar|minimice|minimiza|min|minimize)\b", re.IGNORECASE
        )

        # Patrón para la expresión completa del objetivo
        # Captura: "Maximizar Z = 3x + 2y - 5"
        self.full_objective_pattern = re.compile(
            r"(maximizar|minimizar|max|min)\s*:?\s*(?:[A-Za-z]\s*=\s*)?(.*?)(?=sujeto|tal que|s\.t\.|restricciones|constraints|subject\s+to|$)",
            re.IGNORECASE | re.DOTALL,
        )

        # Patrón para términos individuales: "3x", "-2.5y", "x" (coef=1)
        self.term_pattern = re.compile(
            r"([-+]?\s*\d*\.?\d*)\s*\*?\s*([a-zA-Z][a-zA-Z0-9_]*)"
        )

    def parse_objective(
        self, text: str, variable_names: Optional[List[str]] = None
    ) -> Optional[ObjectiveFunction]:
        """
        Extrae y parsea la función objetivo del texto.

        Args:
            text: Texto del problema
            variable_names: Lista opcional de nombres de variables conocidos

        Returns:
            ObjectiveFunction o None si no se encuentra función objetivo
        """
        # 1. Determinar tipo de optimización
        objective_type = self._detect_objective_type(text)

        if not objective_type:
            self.logger.warning("No se detectó tipo de optimización (max/min)")
            return None

        # 2. Extraer la expresión de la función objetivo
        expression = self._extract_objective_expression(text)

        if not expression:
            self.logger.warning("No se pudo extraer expresión de función objetivo")
            return None

        self.logger.info(f"Expresión objetivo encontrada: {expression}")

        # 3. Parsear coeficientes
        coefficients = self._parse_coefficients(expression, variable_names)

        if not coefficients:
            self.logger.warning(
                "No se pudieron extraer coeficientes de la función objetivo"
            )
            return None

        # 4. Buscar término constante
        constant = self._extract_constant_term(expression, coefficients)

        objective = ObjectiveFunction(
            objective_type=objective_type,
            coefficients=coefficients,
            constant_term=constant,
            original_expression=expression,
        )

        self.logger.info(
            f"Objetivo parseado: {objective_type} con {len(coefficients)} variables"
        )

        return objective

    def _detect_objective_type(self, text: str) -> Optional[str]:
        """Detecta si es maximización o minimización."""
        if self.maximize_pattern.search(text):
            return "maximize"
        elif self.minimize_pattern.search(text):
            return "minimize"
        return None

    def _extract_objective_expression(self, text: str) -> Optional[str]:
        """
        Extrae la expresión matemática de la función objetivo.

        Busca texto entre "maximizar/minimizar" y "sujeto a/restricciones".
        """
        match = self.full_objective_pattern.search(text)

        if match:
            expression = match.group(2).strip()
            # Limpiar posible nombre de función objetivo (Z =, f =, etc.)
            expression = re.sub(r"^[A-Za-z]\s*=\s*", "", expression)
            return expression

        return None

    def _parse_coefficients(
        self, expression: str, variable_names: Optional[List[str]] = None
    ) -> Dict[str, float]:
        """
        Extrae coeficientes de cada variable en la expresión.

        Maneja casos como:
        - "3x" -> {"x": 3.0}
        - "-2.5y" -> {"y": -2.5}
        - "x" -> {"x": 1.0}
        - "- x" -> {"x": -1.0}
        """
        coefficients = {}

        # Normalizar espacios alrededor de operadores
        expression = re.sub(r"\s*([+-])\s*", r" \1 ", expression)

        for match in self.term_pattern.finditer(expression):
            coef_str = match.group(1).strip()
            var_name = match.group(2)

            # Si se proporcionaron nombres de variables, validar
            if variable_names and var_name not in variable_names:
                continue

            # Parsear coeficiente
            if not coef_str or coef_str == "+":
                coef = 1.0
            elif coef_str == "-":
                coef = -1.0
            else:
                try:
                    coef = float(coef_str.replace(" ", ""))
                except ValueError:
                    self.logger.warning(f"No se pudo parsear coeficiente: {coef_str}")
                    continue

            coefficients[var_name] = coef
            self.logger.debug(f"Coeficiente parseado: {var_name} = {coef}")

        return coefficients

    def _extract_constant_term(
        self, expression: str, coefficients: Dict[str, float]
    ) -> float:
        """
        Extrae término constante de la expresión.

        Por ejemplo, en "3x + 2y - 5", el término constante es -5.
        """
        # Remover todos los términos con variables
        temp_expr = expression
        for var in coefficients.keys():
            temp_expr = re.sub(
                rf"[-+]?\s*\d*\.?\d*\s*\*?\s*{re.escape(var)}\b", "", temp_expr
            )

        # Buscar números que quedaron
        numbers = re.findall(r"[-+]?\d+\.?\d*", temp_expr)

        if numbers:
            try:
                return float(numbers[0])
            except ValueError:
                pass

        return 0.0

    def format_objective_for_display(self, objective: ObjectiveFunction) -> str:
        """
        Formatea la función objetivo para mostrarla de forma legible.

        Returns:
            String como "Maximizar: 3x1 + 2x2 - 5"
        """
        terms = []

        for var, coef in sorted(objective.coefficients.items()):
            if coef > 0 and terms:  # No poner + al inicio
                sign = "+"
            elif coef < 0:
                sign = "-"
                coef = abs(coef)
            else:
                sign = ""

            if coef == 1.0:
                terms.append(f"{sign}{var}".strip())
            else:
                terms.append(f"{sign}{coef}{var}".strip())

        result = " ".join(terms)

        if objective.constant_term != 0:
            if objective.constant_term > 0:
                result += f" + {objective.constant_term}"
            else:
                result += f" - {abs(objective.constant_term)}"

        obj_type = (
            "Maximizar" if objective.objective_type == "maximize" else "Minimizar"
        )

        return f"{obj_type}: {result}"

    def validate_objective_with_variables(
        self, objective: ObjectiveFunction, variable_names: List[str]
    ) -> Tuple[bool, List[str]]:
        """
        Valida que la función objetivo use solo variables declaradas.

        Returns:
            (is_valid, list_of_errors)
        """
        errors = []

        for var in objective.coefficients.keys():
            if var not in variable_names:
                errors.append(f"Variable '{var}' en función objetivo no está declarada")

        return len(errors) == 0, errors
