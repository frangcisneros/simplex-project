"""
Detector de estructura de problemas de optimización.

Analiza el texto del problema para identificar:
- Número de plantas/instalaciones
- Número de productos/tamaños/tipos
- Tipo de problema (simple, multi-instalación, mezclas)
- Validación de variables extraídas vs esperadas
"""

import re
from typing import Dict, List, Tuple, Optional
import logging


class ProblemStructureDetector:
    """
    Detecta automáticamente la estructura de un problema de optimización
    basándose en el análisis del texto.
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def detect_structure(self, problem_text: str) -> Dict:
        """
        Analiza el texto y detecta la estructura del problema.

        Returns:
            Dict con:
            - problem_type: 'simple', 'multi_facility', 'blending_simple', 'blending_complex'
            - num_facilities: número de plantas/instalaciones
            - num_products: número de productos/tamaños
            - expected_variables: número esperado de variables
            - facility_names: lista de nombres de plantas detectadas
            - product_names: lista de nombres de productos detectados
        """
        text = problem_text.lower()

        # Detectar plantas/instalaciones
        facilities = self._detect_facilities(text)
        num_facilities = len(facilities) if facilities else 1

        # Detectar productos/tamaños
        products = self._detect_products(text)
        num_products = len(products) if products else 1

        # Detectar si hay mezclas
        has_blending = self._detect_blending(text)

        # Determinar tipo de problema
        # PRIORIDAD: Multi-instalación antes que mezclas
        if num_facilities > 1 and num_products > 1:
            # Problema multi-instalación claramente definido
            problem_type = "multi_facility"
            expected_variables = num_facilities * num_products
        elif has_blending:
            # Detectar materias primas y mezclas finales
            raw_materials = self._detect_raw_materials(text)
            final_blends = self._detect_final_blends(text)

            if raw_materials and final_blends:
                problem_type = "blending_complex"
                # Variables: ventas directas + totales mezclas + componentes
                expected_variables = (
                    len(raw_materials)
                    + len(final_blends)
                    + (len(raw_materials) * len(final_blends))
                )
            else:
                problem_type = "blending_simple"
                expected_variables = num_products + 1  # productos + mezcla
        elif num_facilities > 1 or "planta" in text:
            problem_type = "multi_facility"
            expected_variables = num_facilities * num_products
        else:
            problem_type = "simple"
            expected_variables = num_products

        return {
            "problem_type": problem_type,
            "num_facilities": num_facilities,
            "num_products": num_products,
            "expected_variables": expected_variables,
            "facility_names": facilities,
            "product_names": products,
            "has_blending": has_blending,
        }

    def _detect_facilities(self, text: str) -> List[str]:
        """Detecta plantas/instalaciones mencionadas en el texto."""
        facilities = []

        # Buscar "tres plantas", "dos plantas", etc. PRIMERO (más confiable)
        num_pattern = r"(tres|dos|cuatro|cinco|2|3|4|5)\s+plantas"
        match = re.search(num_pattern, text)
        if match:
            num_word = match.group(1)
            num_map = {
                "dos": 2,
                "2": 2,
                "tres": 3,
                "3": 3,
                "cuatro": 4,
                "4": 4,
                "cinco": 5,
                "5": 5,
            }
            num = num_map.get(num_word, 1)
            facilities = [f"planta_{i+1}" for i in range(num)]
            return facilities

        # Buscar patrones como "planta 1", "planta 2" o "plantas 1 2 y 3"
        # Primero buscar todos los números cerca de "planta"
        planta_pattern = r"planta[s]?\s*[\d\s,y]+"
        match = re.search(planta_pattern, text)
        if match:
            # Extraer todos los números de esa sección
            numbers = re.findall(r"\d+", match.group())
            if numbers:
                facilities = [f"planta_{n}" for n in sorted(set(numbers))]

        return facilities

    def _detect_products(self, text: str) -> List[str]:
        """Detecta productos/tamaños mencionados en el texto."""
        products = []

        # PRIMERO: Buscar "tres tamaños", "dos productos", etc. (más confiable)
        num_pattern = r"(tres|dos|cuatro|2|3|4)\s+(producto|tamaño|tipo)"
        match = re.search(num_pattern, text)
        if match:
            num_word = match.group(1)
            num_map = {"dos": 2, "2": 2, "tres": 3, "3": 3, "cuatro": 4, "4": 4}
            num = num_map.get(num_word, 1)
            products = [f"producto_{i+1}" for i in range(num)]
            return products

        # Buscar tamaños explícitos
        size_patterns = [
            r"(grande|mediano|chico)",
            r"(small|medium|large)",
        ]

        for pattern in size_patterns:
            matches = re.findall(pattern, text)
            if matches:
                # Eliminar duplicados inmediatamente
                products.extend(list(set(matches)))

        # Si encontramos productos específicos, devolverlos sin duplicados
        if products:
            return list(set(products))[:10]

        # Buscar productos específicos (A, B, C, etc.)
        product_pattern = r"producto[s]?\s*[:\-]?\s*([A-Z][,\s]*[A-Z]*[,\s]*[A-Z]*)"
        matches = re.findall(product_pattern, text)
        if matches:
            for match in matches:
                prods = re.findall(r"[A-Z]", match)
                products.extend(prods)

        return list(set(products))[:10]  # Limitar a 10 productos max

    def _detect_blending(self, text: str) -> bool:
        """Detecta si el problema involucra mezclas."""
        # Palabras clave fuertes que indican mezclas
        strong_blending_keywords = [
            "avgas",
            "gasolina de aviación",
            "refinería",
            "promedio de",
            "proporción",
            "porcentaje",
        ]

        # Solo considerar mezclas si hay palabras clave FUERTES
        # y NO es un problema multi-instalación típico
        has_strong_keywords = any(
            keyword in text for keyword in strong_blending_keywords
        )

        # Palabras que indican multi-instalación (no mezclas)
        facility_indicators = [
            "plantas",
            "fábrica",
            "instalación",
            "capacidad de producción",
        ]

        has_facilities = any(indicator in text for indicator in facility_indicators)

        # Si tiene plantas claramente definidas, probablemente NO es mezclas
        if has_facilities and not has_strong_keywords:
            return False

        return has_strong_keywords

    def _detect_raw_materials(self, text: str) -> List[str]:
        """Detecta materias primas en problemas de mezclas."""
        materials = []

        # Buscar "gas 1", "gas 2", etc.
        gas_pattern = r"gas\s*(\d+)"
        matches = re.findall(gas_pattern, text)
        if matches:
            materials = [f"gas_{n}" for n in sorted(set(matches))]

        # Buscar "tipo 1", "tipo 2", etc.
        if not materials:
            type_pattern = r"tipo\s*(\d+)"
            matches = re.findall(type_pattern, text)
            if matches:
                materials = [f"tipo_{n}" for n in sorted(set(matches))]

        return materials

    def _detect_final_blends(self, text: str) -> List[str]:
        """Detecta mezclas finales en problemas de mezclas."""
        blends = []

        # Buscar "avgas A", "avgas B", etc. (text ya está en minúsculas)
        avgas_pattern = r"avgas\s*([a-z])"
        matches = re.findall(avgas_pattern, text)
        if matches:
            blends = [f"avgas_{m.upper()}" for m in sorted(set(matches))]

        # Buscar "mezcla A", "mezcla B", etc.
        if not blends:
            mix_pattern = r"mezcla\s*([a-z])"
            matches = re.findall(mix_pattern, text)
            if matches:
                blends = [f"mezcla_{m.upper()}" for m in sorted(set(matches))]

        return blends

    def validate_extracted_variables(
        self, extracted_problem: Dict, structure: Dict
    ) -> Tuple[bool, List[str]]:
        """
        Valida si las variables extraídas coinciden con la estructura esperada.

        Returns:
            Tuple[bool, List[str]]: (es_válido, lista_de_advertencias)
        """
        warnings = []
        is_valid = True

        num_extracted = len(extracted_problem.get("variable_names", []))
        expected = structure["expected_variables"]

        if num_extracted != expected:
            is_valid = False
            warnings.append(
                f"Número de variables: extraídas={num_extracted}, esperadas={expected}"
            )

            # Dar sugerencias específicas
            if structure["problem_type"] == "multi_facility":
                warnings.append(
                    f"Problema multi-instalación: {structure['num_facilities']} plantas × "
                    f"{structure['num_products']} productos = {expected} variables"
                )
                if num_extracted < expected:
                    warnings.append(
                        "⚠️ FALTAN VARIABLES - El modelo no extrajo todas las combinaciones planta×producto"
                    )

        # Validar coeficientes objetivo
        num_coeffs = len(extracted_problem.get("objective_coefficients", []))
        if num_coeffs != num_extracted:
            is_valid = False
            warnings.append(
                f"Coeficientes objetivo: {num_coeffs}, pero variables: {num_extracted}"
            )

        return is_valid, warnings
