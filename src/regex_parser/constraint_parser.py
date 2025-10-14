"""
Parser de restricciones usando expresiones regulares.

Extrae y parsea restricciones de problemas de optimización:
- Coeficientes de variables
- Operador (<=, >=, =)
- Lado derecho (RHS)

Soporta formatos como:
- "2x + 3y <= 100"
- "x1 + 2*x2 - x3 = 50"
- "5producto_A + 3producto_B >= 20"
"""

import re
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
import logging


@dataclass
class Constraint:
    """Representa una restricción parseada."""

    coefficients: Dict[str, float]  # {variable_name: coefficient}
    operator: str  # "<=", ">=", o "="
    rhs: float  # Right-hand side value
    original_text: str = ""


class ConstraintParser:
    """
    Parsea restricciones de problemas de optimización.

    Identifica la sección de restricciones y extrae cada una,
    parseando coeficientes, operadores y valores RHS.
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)

        # Patrones para detectar inicio de restricciones
        self.constraint_section_patterns = [
            re.compile(r"\bsujeto\s+a\b", re.IGNORECASE),
            re.compile(r"\btal\s+que\b", re.IGNORECASE),
            re.compile(r"\bs\.t\.\b", re.IGNORECASE),
            re.compile(r"\brestricciones\b", re.IGNORECASE),
            re.compile(r"\bconstraints\b", re.IGNORECASE),
            re.compile(r"\bsubject\s+to\b", re.IGNORECASE),
        ]

        # Patrón para restricción completa: "2x + 3y <= 100"
        self.constraint_pattern = re.compile(
            r"(.*?)\s*(<=|>=|=|≤|≥)\s*([-+]?\d*\.?\d+)"
        )

        # Patrón para términos: "3x", "-2.5y"
        self.term_pattern = re.compile(
            r"([-+]?\s*\d*\.?\d*)\s*\*?\s*([a-zA-Z][a-zA-Z0-9_]*)"
        )

        # Normalizar operadores unicode
        self.operator_normalization = {"≤": "<=", "≥": ">="}

    def parse_constraints(
        self, text: str, variable_names: Optional[List[str]] = None
    ) -> List[Constraint]:
        """
        Extrae y parsea todas las restricciones del texto.

        Args:
            text: Texto del problema
            variable_names: Lista opcional de variables conocidas

        Returns:
            Lista de objetos Constraint
        """
        # 1. Encontrar sección de restricciones
        constraint_text = self._extract_constraint_section(text)

        if not constraint_text:
            self.logger.warning("No se encontró sección de restricciones")
            return []

        self.logger.info(
            f"Sección de restricciones encontrada: {len(constraint_text)} caracteres"
        )

        # 2. Dividir en restricciones individuales
        constraint_lines = self._split_into_individual_constraints(constraint_text)

        # 3. Parsear cada restricción
        constraints = []
        for i, line in enumerate(constraint_lines, 1):
            constraint = self._parse_single_constraint(line, variable_names)
            if constraint:
                constraints.append(constraint)
                self.logger.debug(
                    f"Restricción {i} parseada: {len(constraint.coefficients)} variables"
                )

        self.logger.info(f"Total de {len(constraints)} restricciones parseadas")

        return constraints

    def _extract_constraint_section(self, text: str) -> Optional[str]:
        """
        Extrae la sección de restricciones del texto.

        Busca desde el marcador (sujeto a, restricciones, etc.) hasta el final
        o hasta encontrar otra sección.
        """
        # Buscar dónde empieza la sección de restricciones
        start_pos = None
        for pattern in self.constraint_section_patterns:
            match = pattern.search(text)
            if match:
                start_pos = match.end()
                break

        if start_pos is None:
            # Intentar detectar restricciones sin marcador explícito
            # (buscar líneas con operadores de comparación)
            return self._extract_constraints_without_marker(text)

        # Extraer desde el marcador hasta el final
        constraint_text = text[start_pos:].strip()

        return constraint_text

    def _extract_constraints_without_marker(self, text: str) -> Optional[str]:
        """
        Intenta extraer restricciones cuando no hay marcador explícito.

        Busca líneas que contengan operadores de comparación.
        """
        lines = text.split("\n")
        constraint_lines = []

        for line in lines:
            if re.search(r"(<=|>=|=|≤|≥)", line):
                # Verificar que no sea la función objetivo
                if not re.search(
                    r"\b(maximizar|minimizar|max|min)\b", line, re.IGNORECASE
                ):
                    constraint_lines.append(line)

        if constraint_lines:
            return "\n".join(constraint_lines)

        return None

    def _split_into_individual_constraints(self, text: str) -> List[str]:
        """
        Divide el texto en restricciones individuales.

        Usa saltos de línea, comas, y palabras clave como delimitadores.
        """
        # Reemplazar comas y punto y coma por saltos de línea
        text = text.replace(",", "\n").replace(";", "\n")

        # Dividir por saltos de línea
        lines = [line.strip() for line in text.split("\n") if line.strip()]

        # Filtrar líneas que parecen restricciones (tienen operadores)
        constraint_lines = []
        for line in lines:
            if re.search(r"(<=|>=|=|≤|≥)", line):
                constraint_lines.append(line)

        return constraint_lines

    def _parse_single_constraint(
        self, text: str, variable_names: Optional[List[str]] = None
    ) -> Optional[Constraint]:
        """
        Parsea una restricción individual.

        Args:
            text: Texto de la restricción (ej: "2x + 3y <= 100")
            variable_names: Variables conocidas para validación

        Returns:
            Objeto Constraint o None si falla el parsing
        """
        # Buscar el patrón de restricción
        match = self.constraint_pattern.search(text)

        if not match:
            self.logger.warning(f"No se pudo parsear restricción: {text}")
            return None

        lhs_text = match.group(1).strip()  # Lado izquierdo
        operator = match.group(2)  # Operador
        rhs_value = float(match.group(3))  # Lado derecho

        # Normalizar operador
        operator = self.operator_normalization.get(operator, operator)

        # Parsear coeficientes del lado izquierdo
        coefficients = self._parse_lhs_coefficients(lhs_text, variable_names)

        if not coefficients:
            self.logger.warning(f"No se encontraron variables en: {lhs_text}")
            return None

        constraint = Constraint(
            coefficients=coefficients,
            operator=operator,
            rhs=rhs_value,
            original_text=text,
        )

        return constraint

    def _parse_lhs_coefficients(
        self, lhs_text: str, variable_names: Optional[List[str]] = None
    ) -> Dict[str, float]:
        """
        Parsea coeficientes del lado izquierdo de una restricción.

        Similar al parsing de función objetivo.
        """
        coefficients = {}

        # Normalizar espacios alrededor de operadores
        lhs_text = re.sub(r"\s*([+-])\s*", r" \1 ", lhs_text)

        for match in self.term_pattern.finditer(lhs_text):
            coef_str = match.group(1).strip()
            var_name = match.group(2)

            # Validar variable si se proporcionó lista
            if variable_names and var_name not in variable_names:
                self.logger.debug(f"Variable '{var_name}' no está en lista conocida")
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

        return coefficients

    def format_constraint_for_display(self, constraint: Constraint) -> str:
        """
        Formatea una restricción para mostrarla legiblemente.

        Returns:
            String como "2x1 + 3x2 <= 100"
        """
        terms = []

        for var, coef in sorted(constraint.coefficients.items()):
            if coef > 0 and terms:
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

        lhs = " ".join(terms)

        return f"{lhs} {constraint.operator} {constraint.rhs}"

    def validate_constraints_with_variables(
        self, constraints: List[Constraint], variable_names: List[str]
    ) -> Tuple[bool, List[str]]:
        """
        Valida que las restricciones usen solo variables declaradas.

        Returns:
            (is_valid, list_of_errors)
        """
        errors = []

        for i, constraint in enumerate(constraints, 1):
            for var in constraint.coefficients.keys():
                if var not in variable_names:
                    errors.append(
                        f"Restricción {i}: Variable '{var}' no está declarada"
                    )

        return len(errors) == 0, errors

    def convert_to_standard_form(
        self, constraints: List[Constraint]
    ) -> List[Constraint]:
        """
        Convierte restricciones a forma estándar (todas con <=).

        Multiplica por -1 las restricciones con >= para convertirlas.
        """
        standard_constraints = []

        for constraint in constraints:
            if constraint.operator == ">=":
                # Multiplicar por -1 para convertir a <=
                new_coefficients = {
                    var: -coef for var, coef in constraint.coefficients.items()
                }
                new_constraint = Constraint(
                    coefficients=new_coefficients,
                    operator="<=",
                    rhs=-constraint.rhs,
                    original_text=constraint.original_text,
                )
                standard_constraints.append(new_constraint)
            else:
                standard_constraints.append(constraint)

        return standard_constraints
