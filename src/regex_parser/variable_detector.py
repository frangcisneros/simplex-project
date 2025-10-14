"""
Detector de variables usando expresiones regulares.

Identifica y normaliza variables en problemas de optimización:
- Variables con subíndices (x1, x2, x_3)
- Variables descriptivas (producto_A, tiempo_B)
- Variables simples (x, y, z)

También infiere rangos de variables basándose en patrones (x1...x10).
"""

import re
from typing import List, Set, Dict, Tuple
from dataclasses import dataclass
import logging


@dataclass
class Variable:
    """Representa una variable detectada."""

    name: str
    original_form: str  # Como apareció en el texto
    base_name: str  # Parte base sin subíndice (x de x1)
    subscript: int = None  # Subíndice numérico si existe
    is_descriptive: bool = False  # True para nombres como producto_A


class VariableDetector:
    """
    Detecta y normaliza variables en texto de problemas de optimización.

    Usa múltiples estrategias de regex para identificar variables
    y manejar diferentes convenciones de nomenclatura.
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)

        # Patrones para detectar variables
        self.patterns = {
            # x1, x2, x_3, y12
            "subscript": re.compile(r"\b([a-zA-Z]+)_?(\d+)\b"),
            # producto_A, tiempo_max, costo_envio
            "descriptive": re.compile(r"\b([a-zA-Z][a-zA-Z_]{2,})\b"),
            # x, y, z (solo en contextos matemáticos)
            "simple": re.compile(r"\b([a-zA-Z])\b"),
        }

        # Palabras que NO son variables aunque coincidan con patrones
        self.stopwords = {
            "maximizar",
            "minimizar",
            "sujeto",
            "tal",
            "que",
            "donde",
            "con",
            "para",
            "por",
            "cada",
            "todo",
            "son",
            "sea",
            "sean",
            "max",
            "min",
            "s",
            "t",
            "a",
            "e",
            "i",
            "o",
            "u",
            "y",
            "o",
            "de",
            "la",
            "el",
            "en",
        }

    def detect_variables(self, text: str) -> List[Variable]:
        """
        Detecta todas las variables en el texto.

        Primero busca variables con subíndices (más específicas),
        luego descriptivas, y finalmente simples.

        Args:
            text: Texto del problema de optimización

        Returns:
            Lista de objetos Variable detectados
        """
        variables = []
        seen_names = set()

        text_lower = text.lower()

        # 1. Detectar variables con subíndices primero (más específicas)
        for match in self.patterns["subscript"].finditer(text):
            base = match.group(1)
            subscript = int(match.group(2))
            full_name = f"{base}{subscript}"

            if full_name not in seen_names and base.lower() not in self.stopwords:
                var = Variable(
                    name=full_name,
                    original_form=match.group(0),
                    base_name=base,
                    subscript=subscript,
                    is_descriptive=False,
                )
                variables.append(var)
                seen_names.add(full_name)

        # 2. Detectar variables descriptivas
        for match in self.patterns["descriptive"].finditer(text):
            name = match.group(1)

            if (
                name not in seen_names
                and name.lower() not in self.stopwords
                and not self._is_part_of_subscript_var(name, text, match.start())
            ):
                var = Variable(
                    name=name,
                    original_form=name,
                    base_name=name,
                    is_descriptive=True,
                )
                variables.append(var)
                seen_names.add(name)

        # 3. Detectar variables simples solo si aparecen en contexto matemático
        if not variables:  # Solo si no encontramos variables más específicas
            for match in self.patterns["simple"].finditer(text):
                name = match.group(1)

                if (
                    name not in seen_names
                    and name.lower() not in self.stopwords
                    and self._is_mathematical_context(text, match.start())
                ):
                    var = Variable(
                        name=name,
                        original_form=name,
                        base_name=name,
                        is_descriptive=False,
                    )
                    variables.append(var)
                    seen_names.add(name)

        self.logger.info(
            f"Detected {len(variables)} variables: {[v.name for v in variables]}"
        )
        return variables

    def infer_variable_range(self, variables: List[Variable]) -> List[Variable]:
        """
        Infiere variables faltantes basándose en rangos detectados.

        Por ejemplo, si encuentra x1 y x5, infiere x2, x3, x4.

        Args:
            variables: Lista de variables detectadas

        Returns:
            Lista expandida con variables inferidas
        """
        # Agrupar por base_name
        by_base: Dict[str, List[Variable]] = {}
        for var in variables:
            if var.subscript is not None:
                if var.base_name not in by_base:
                    by_base[var.base_name] = []
                by_base[var.base_name].append(var)

        expanded_variables = list(variables)

        # Para cada base con subíndices, completar el rango
        for base_name, base_vars in by_base.items():
            if len(base_vars) < 2:
                continue

            subscripts = sorted([v.subscript for v in base_vars])
            min_sub = subscripts[0]
            max_sub = subscripts[-1]

            # Si hay un gap significativo (diferencia > 1), inferir intermedios
            if max_sub - min_sub > len(subscripts):
                for i in range(min_sub, max_sub + 1):
                    full_name = f"{base_name}{i}"
                    if not any(v.name == full_name for v in expanded_variables):
                        inferred_var = Variable(
                            name=full_name,
                            original_form=full_name,
                            base_name=base_name,
                            subscript=i,
                            is_descriptive=False,
                        )
                        expanded_variables.append(inferred_var)
                        self.logger.info(f"Inferred variable: {full_name}")

        return sorted(expanded_variables, key=lambda v: (v.base_name, v.subscript or 0))

    def normalize_variable_names(self, variables: List[Variable]) -> Dict[str, str]:
        """
        Crea un mapeo de nombres originales a nombres normalizados.

        Útil para estandarizar variables antes de pasar al solver.

        Returns:
            Dict mapping original name -> normalized name (x1, x2, x3, ...)
        """
        mapping = {}
        for i, var in enumerate(variables, 1):
            mapping[var.name] = f"x{i}"

        return mapping

    def _is_mathematical_context(self, text: str, position: int) -> bool:
        """
        Verifica si una posición está en un contexto matemático.

        Busca operadores cerca (+, -, *, /, =, <=, >=) para confirmar.
        """
        # Buscar en una ventana de ±20 caracteres
        start = max(0, position - 20)
        end = min(len(text), position + 20)
        context = text[start:end]

        math_operators = ["+", "-", "*", "/", "=", "<=", ">=", "<", ">"]
        return any(op in context for op in math_operators)

    def _is_part_of_subscript_var(self, name: str, text: str, position: int) -> bool:
        """
        Verifica si este nombre es parte de una variable con subíndice.

        Por ejemplo, no queremos detectar "producto" si aparece "producto_1".
        """
        # Mirar si después viene un underscore o número
        if position + len(name) < len(text):
            next_char = text[position + len(name)]
            if next_char in ["_", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]:
                return True

        return False

    def extract_variable_bounds(
        self, text: str, variables: List[Variable]
    ) -> Dict[str, Tuple[float, float]]:
        """
        Detecta cotas explícitas para variables.

        Busca patrones como:
        - "0 <= x <= 100"
        - "x >= 0"
        - "x entre 0 y 10"

        Returns:
            Dict con {variable_name: (lower_bound, upper_bound)}
        """
        bounds = {}

        # Patrón: 0 <= x <= 100
        double_bound_pattern = re.compile(
            r"([-+]?\d*\.?\d+)\s*<=\s*([a-zA-Z][a-zA-Z0-9_]*)\s*<=\s*([-+]?\d*\.?\d+)"
        )

        for match in double_bound_pattern.finditer(text):
            var_name = match.group(2)
            lower = float(match.group(1))
            upper = float(match.group(3))

            if any(v.name == var_name for v in variables):
                bounds[var_name] = (lower, upper)
                self.logger.info(f"Detected bounds for {var_name}: [{lower}, {upper}]")

        return bounds
