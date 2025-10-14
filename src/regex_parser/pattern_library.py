"""
Biblioteca de patrones regex para diferentes elementos de problemas de optimización.

Contiene patrones compilados y organizados para detectar:
- Variables (x, y, x1, x2, producto_A, etc.)
- Operadores matemáticos (+, -, <=, >=, =)
- Números (enteros, decimales, negativos)
- Funciones objetivo (maximizar, minimizar)
- Restricciones (sujeto a, tal que, constraints)
"""

import re
from typing import Dict, List, Pattern
from dataclasses import dataclass


@dataclass
class RegexPattern:
    """Encapsula un patrón regex con metadata."""

    name: str
    pattern: Pattern
    description: str
    priority: int = 0  # Mayor prioridad = se evalúa primero


class PatternLibrary:
    """
    Biblioteca centralizada de todos los patrones regex del sistema.

    Organiza los patrones por categoría y proporciona métodos
    para acceder a ellos de forma estructurada.
    """

    def __init__(self):
        self._compile_all_patterns()

    def _compile_all_patterns(self):
        """Compila todos los patrones regex al inicializar."""

        # ==================== VARIABLES ====================
        self.VARIABLE_PATTERNS = {
            # Variables con subíndices: x1, x2, y_3, z12
            "subscript": RegexPattern(
                name="subscript_variable",
                pattern=re.compile(r"\b([a-zA-Z]+)_?(\d+)\b"),
                description="Variables con subíndices como x1, x_2",
                priority=10,
            ),
            # Variables con nombres descriptivos: producto_A, tiempo_fabricacion
            "descriptive": RegexPattern(
                name="descriptive_variable",
                pattern=re.compile(r"\b([a-zA-Z][a-zA-Z_]*[a-zA-Z])\b"),
                description="Variables descriptivas como producto_A, tiempo_max",
                priority=5,
            ),
            # Variables simples: x, y, z
            "simple": RegexPattern(
                name="simple_variable",
                pattern=re.compile(r"\b([a-zA-Z])\b"),
                description="Variables de una letra como x, y, z",
                priority=1,
            ),
        }

        # ==================== NÚMEROS ====================
        self.NUMBER_PATTERNS = {
            # Números decimales con signo opcional
            "decimal": re.compile(r"[-+]?\d*\.?\d+"),
            # Números enteros
            "integer": re.compile(r"[-+]?\d+"),
            # Fracciones (1/2, 3/4)
            "fraction": re.compile(r"(\d+)/(\d+)"),
        }

        # ==================== FUNCIÓN OBJETIVO ====================
        self.OBJECTIVE_PATTERNS = {
            # Maximizar/Maximice/Max
            "maximize": re.compile(
                r"\b(maximizar|maximice|maximiza|max|maximize)\b", re.IGNORECASE
            ),
            # Minimizar/Minimice/Min
            "minimize": re.compile(
                r"\b(minimizar|minimice|minimiza|min|minimize)\b", re.IGNORECASE
            ),
            # Expresión completa: "Maximizar Z = 3x + 2y"
            "full_objective": re.compile(
                r"(maximizar|minimizar|max|min)\s*:?\s*([A-Za-z])\s*=\s*(.*?)(?=sujeto|tal que|s\.t\.|restricciones|$)",
                re.IGNORECASE | re.DOTALL,
            ),
        }

        # ==================== RESTRICCIONES ====================
        self.CONSTRAINT_PATTERNS = {
            # Detecta inicio de sección de restricciones
            "section_start": re.compile(
                r"\b(sujeto\s+a|tal\s+que|s\.t\.|restricciones|constraints|subject\s+to)\b",
                re.IGNORECASE,
            ),
            # Restricción completa: "2x + 3y <= 100"
            "full_constraint": re.compile(r"(.*?)\s*(<=|>=|=|≤|≥)\s*([-+]?\d*\.?\d+)"),
            # Operadores de comparación
            "operators": re.compile(r"(<=|>=|=|≤|≥|<|>)"),
        }

        # ==================== TÉRMINOS MATEMÁTICOS ====================
        self.TERM_PATTERNS = {
            # Término con coeficiente: "3x", "-2.5y", "x" (coef implícito 1)
            "coefficient_variable": re.compile(
                r"([-+]?\s*\d*\.?\d*)\s*\*?\s*([a-zA-Z][a-zA-Z0-9_]*)"
            ),
            # Detecta suma/resta
            "operators": re.compile(r"([+-])"),
        }

        # ==================== NO-NEGATIVIDAD ====================
        self.NON_NEGATIVITY_PATTERNS = {
            # "x >= 0", "x, y >= 0"
            "explicit": re.compile(
                r"([a-zA-Z][a-zA-Z0-9_,\s]*)\s*>=\s*0", re.IGNORECASE
            ),
            # "x, y, z no negativos" o "variables no negativas"
            "text": re.compile(
                r"(.*?)\s*(no\s+negativ[oa]s?|non-negative)", re.IGNORECASE
            ),
        }

        # ==================== PALABRAS CLAVE DE CONTEXTO ====================
        self.CONTEXT_KEYWORDS = {
            "production": [
                "producir",
                "fabricar",
                "manufactura",
                "producción",
                "unidades",
            ],
            "transportation": ["enviar", "transportar", "distribuir", "ruta", "costo"],
            "assignment": ["asignar", "trabajador", "tarea", "empleado", "proyecto"],
            "resource": ["recurso", "tiempo", "mano de obra", "material", "capacidad"],
            "financial": ["inversión", "costo", "ganancia", "beneficio", "presupuesto"],
        }

    def get_all_variable_patterns(self) -> List[RegexPattern]:
        """Retorna todos los patrones de variables ordenados por prioridad."""
        patterns = list(self.VARIABLE_PATTERNS.values())
        return sorted(patterns, key=lambda p: p.priority, reverse=True)

    def detect_problem_type(self, text: str) -> str:
        """
        Detecta el tipo de problema basado en palabras clave.

        Returns:
            Tipo de problema: 'production', 'transportation', 'assignment', etc.
        """
        text_lower = text.lower()

        max_matches = 0
        detected_type = "general"

        for prob_type, keywords in self.CONTEXT_KEYWORDS.items():
            matches = sum(1 for keyword in keywords if keyword in text_lower)
            if matches > max_matches:
                max_matches = matches
                detected_type = prob_type

        return detected_type

    def is_constraint_operator(self, text: str) -> bool:
        """Verifica si el texto contiene un operador de restricción."""
        return bool(self.CONSTRAINT_PATTERNS["operators"].search(text))

    def extract_numbers(self, text: str) -> List[float]:
        """Extrae todos los números de un texto."""
        numbers = []
        for match in self.NUMBER_PATTERNS["decimal"].finditer(text):
            try:
                numbers.append(float(match.group()))
            except ValueError:
                continue
        return numbers

    def clean_text(self, text: str) -> str:
        """
        Limpia el texto para facilitar el parsing.

        - Normaliza espacios
        - Convierte símbolos unicode a ASCII
        - Elimina caracteres especiales innecesarios
        """
        # Normalizar símbolos unicode
        replacements = {"≤": "<=", "≥": ">=", "×": "*", "·": "*", "−": "-"}

        for old, new in replacements.items():
            text = text.replace(old, new)

        # Normalizar espacios múltiples
        text = re.sub(r"\s+", " ", text)

        # Limpiar espacios alrededor de operadores
        text = re.sub(r"\s*([+\-*/<>=])\s*", r" \1 ", text)

        return text.strip()

    def split_into_lines(self, text: str) -> List[str]:
        """
        Divide el texto en líneas lógicas.

        Considera puntos, saltos de línea, y palabras clave como delimitadores.
        """
        # Reemplazar marcadores de sección por saltos de línea
        text = re.sub(
            r"(sujeto\s+a|tal\s+que|restricciones)", r"\n\1", text, flags=re.IGNORECASE
        )

        # Dividir por saltos de línea y punto y coma
        lines = [line.strip() for line in re.split(r"[\n;]", text) if line.strip()]

        return lines
