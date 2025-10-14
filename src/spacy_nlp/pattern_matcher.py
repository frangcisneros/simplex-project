"""
Pattern Matcher para problemas de optimización.

Usa reglas basadas en patrones para complementar el NER y extraer
información estructurada que sigue patrones específicos.
"""

import spacy
from spacy.matcher import Matcher, PhraseMatcher
from spacy.tokens import Doc, Span
from typing import List, Dict, Tuple, Optional, Any
import re
import logging


class OptimizationPatternMatcher:
    """
    Encuentra patrones específicos en problemas de optimización.

    Complementa el NER con reglas basadas en patrones lingüísticos
    y expresiones regulares para mayor precisión.
    """

    def __init__(self, nlp: Optional[spacy.Language] = None):
        """
        Args:
            nlp: Modelo spaCy cargado. Si es None, carga modelo base.
        """
        self.logger = logging.getLogger(__name__)

        if nlp is None:
            try:
                self.nlp = spacy.load("es_core_news_sm")
            except:
                self.nlp = spacy.blank("es")
        else:
            self.nlp = nlp

        self.matcher = Matcher(self.nlp.vocab)
        self.phrase_matcher = PhraseMatcher(self.nlp.vocab)

        self._setup_patterns()

    def _setup_patterns(self):
        """Configura los patrones de matching."""

        # Patrón para objetivo: "Maximizar Z = ..."
        pattern_objective = [
            {"LOWER": {"IN": ["maximizar", "minimizar", "max", "min"]}},
            {"IS_ALPHA": True, "OP": "?"},  # Variable objetivo opcional
            {"TEXT": "=", "OP": "?"},
        ]
        self.matcher.add("OBJECTIVE_PATTERN", [pattern_objective])

        # Patrón para restricción: "x + y <= 100"
        pattern_constraint = [
            {"IS_ALPHA": True},  # Variable
            {"TEXT": {"IN": ["+", "-"]}},
            {"IS_DIGIT": True, "OP": "?"},  # Coeficiente opcional
            {"IS_ALPHA": True},  # Variable
            {"TEXT": {"IN": ["<=", ">=", "="]}},
            {"IS_DIGIT": True},  # RHS
        ]
        self.matcher.add("CONSTRAINT_PATTERN", [pattern_constraint])

        # Patrón para coeficiente + variable: "3x", "2.5y"
        pattern_coef_var = [
            {"LIKE_NUM": True},  # Coeficiente
            {"TEXT": "*", "OP": "?"},  # Multiplicación opcional
            {"IS_ALPHA": True},  # Variable
        ]
        self.matcher.add("COEF_VAR_PATTERN", [pattern_coef_var])

        # Patrón para capacidad/recursos: "X unidades de Y"
        pattern_capacity = [
            {"LIKE_NUM": True},  # Cantidad
            {"LOWER": {"IN": ["unidades", "horas", "metros", "litros", "barriles"]}},
            {"LOWER": {"IN": ["de", "del"]}, "OP": "?"},
            {"IS_ALPHA": True, "OP": "+"},  # Recurso
        ]
        self.matcher.add("CAPACITY_PATTERN", [pattern_capacity])

        # Frases clave para contexto
        objective_phrases = [
            "ganancia",
            "beneficio",
            "utilidad",
            "costo",
            "tiempo",
            "maximizar",
            "minimizar",
            "optimizar",
        ]

        constraint_phrases = [
            "sujeto a",
            "tal que",
            "restricciones",
            "limitaciones",
            "no más de",
            "al menos",
            "como máximo",
            "como mínimo",
        ]

        # Agregar frases al phrase matcher
        objective_patterns = [self.nlp.make_doc(text) for text in objective_phrases]
        constraint_patterns = [self.nlp.make_doc(text) for text in constraint_phrases]

        self.phrase_matcher.add("OBJECTIVE_PHRASES", objective_patterns)
        self.phrase_matcher.add("CONSTRAINT_PHRASES", constraint_patterns)

    def find_patterns(self, text: str) -> List[Dict[str, Any]]:
        """
        Encuentra todos los patrones en el texto.

        Returns:
            Lista de matches con información del patrón
        """
        doc = self.nlp(text)

        matches = self.matcher(doc)
        phrase_matches = self.phrase_matcher(doc)

        results = []

        # Procesar matches del Matcher
        for match_id, start, end in matches:
            span = doc[start:end]
            pattern_name = self.nlp.vocab.strings[match_id]

            results.append(
                {
                    "pattern": pattern_name,
                    "text": span.text,
                    "start": span.start_char,
                    "end": span.end_char,
                }
            )

        # Procesar matches del PhraseMatcher
        for match_id, start, end in phrase_matches:
            span = doc[start:end]
            pattern_name = self.nlp.vocab.strings[match_id]

            results.append(
                {
                    "pattern": pattern_name,
                    "text": span.text,
                    "start": span.start_char,
                    "end": span.end_char,
                }
            )

        return results

    def extract_term_with_coefficient(self, text: str) -> List[Tuple[float, str]]:
        """
        Extrae términos con coeficientes usando regex y patterns.

        Returns:
            Lista de (coeficiente, variable)
        """
        # Patrón regex para términos como "3x", "2.5y", "-4z"
        pattern = r"([-+]?\s*\d*\.?\d+)\s*\*?\s*([a-zA-Z][a-zA-Z0-9_]*)"

        matches = re.finditer(pattern, text)

        terms = []
        for match in matches:
            try:
                coef = float(match.group(1).replace(" ", ""))
                var = match.group(2)
                terms.append((coef, var))
            except ValueError:
                continue

        return terms

    def extract_constraint_expressions(self, text: str) -> List[Dict[str, Any]]:
        """
        Extrae expresiones de restricciones completas.

        Returns:
            Lista de restricciones con sus componentes
        """
        # Patrón para restricciones completas
        pattern = r"(.*?)\s*(<=|>=|=)\s*([-+]?\d+\.?\d*)"

        matches = re.finditer(pattern, text)

        constraints = []
        for match in matches:
            lhs = match.group(1).strip()
            operator = match.group(2)
            rhs = float(match.group(3))

            # Extraer términos del lado izquierdo
            terms = self.extract_term_with_coefficient(lhs)

            if terms:
                constraints.append(
                    {
                        "lhs": lhs,
                        "operator": operator,
                        "rhs": rhs,
                        "terms": terms,
                    }
                )

        return constraints

    def find_numeric_values(self, text: str) -> List[Tuple[float, str]]:
        """
        Encuentra valores numéricos con sus unidades.

        Returns:
            Lista de (valor, contexto/unidad)
        """
        doc = self.nlp(text)

        values = []
        for token in doc:
            if token.like_num:
                # Buscar contexto (siguiente token)
                context = ""
                if token.i + 1 < len(doc):
                    context = doc[token.i + 1].text

                try:
                    value = float(token.text)
                    values.append((value, context))
                except ValueError:
                    continue

        return values

    def identify_problem_sections(self, text: str) -> Dict[str, str]:
        """
        Identifica y separa las secciones del problema.

        Returns:
            Dict con {"objective": texto, "constraints": texto, "context": texto}
        """
        sections = {
            "objective": "",
            "constraints": "",
            "context": "",
        }

        # Patrones para identificar secciones
        objective_keywords = r"\b(maximizar|minimizar|max|min|optimizar)\b"
        constraint_keywords = r"\b(sujeto\s+a|tal\s+que|restricciones|limitaciones)\b"

        # Buscar función objetivo
        obj_match = re.search(objective_keywords, text, re.IGNORECASE)
        const_match = re.search(constraint_keywords, text, re.IGNORECASE)

        if obj_match and const_match:
            sections["objective"] = text[
                obj_match.start() : const_match.start()
            ].strip()
            sections["constraints"] = text[const_match.start() :].strip()
        elif obj_match:
            sections["objective"] = text[obj_match.start() :].strip()
        else:
            sections["context"] = text

        return sections

    def extract_variable_bounds(
        self, text: str
    ) -> Dict[str, Tuple[Optional[float], Optional[float]]]:
        """
        Extrae cotas de variables (ej: "0 <= x <= 100").

        Returns:
            Dict con {variable: (lower_bound, upper_bound)}
        """
        # Patrón para cotas dobles: "0 <= x <= 100"
        double_bound = r"([\d.]+)\s*<=\s*([a-zA-Z][a-zA-Z0-9_]*)\s*<=\s*([\d.]+)"

        # Patrón para cotas simples: "x >= 0"
        simple_bound = r"([a-zA-Z][a-zA-Z0-9_]*)\s*(>=|<=)\s*([\d.]+)"

        bounds = {}

        # Buscar cotas dobles
        for match in re.finditer(double_bound, text):
            var = match.group(2)
            lower = float(match.group(1))
            upper = float(match.group(3))
            bounds[var] = (lower, upper)

        # Buscar cotas simples
        for match in re.finditer(simple_bound, text):
            var = match.group(1)
            operator = match.group(2)
            value = float(match.group(3))

            if var not in bounds:
                if operator == ">=":
                    bounds[var] = (value, None)
                else:  # <=
                    bounds[var] = (None, value)

        return bounds

    def display_matches(self, text: str):
        """
        Muestra todos los patrones encontrados de forma visual.

        Args:
            text: Texto a analizar
        """
        patterns = self.find_patterns(text)

        print(f"\n{'='*70}")
        print("PATRONES ENCONTRADOS")
        print("=" * 70)
        print(f"\nTexto: {text}\n")

        # Agrupar por tipo de patrón
        by_pattern = {}
        for match in patterns:
            pattern_name = match["pattern"]
            if pattern_name not in by_pattern:
                by_pattern[pattern_name] = []
            by_pattern[pattern_name].append(match["text"])

        # Mostrar por patrón
        for pattern_name in sorted(by_pattern.keys()):
            print(f"\n{pattern_name}:")
            for text in by_pattern[pattern_name]:
                print(f"  - {text}")

        # Mostrar restricciones extraídas
        constraints = self.extract_constraint_expressions(text)
        if constraints:
            print(f"\nRESTRICCIONES COMPLETAS:")
            for const in constraints:
                print(f"  {const['lhs']} {const['operator']} {const['rhs']}")
                print(f"    Términos: {const['terms']}")
