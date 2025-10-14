"""
Reconocedor de entidades para problemas de optimización.

Usa el modelo spaCy entrenado para identificar y extraer entidades
específicas como variables, coeficientes, restricciones, etc.
"""

import spacy
from typing import List, Dict, Tuple, Optional, Any
from dataclasses import dataclass
import logging


@dataclass
class OptimizationEntity:
    """Representa una entidad extraída del texto."""

    text: str
    label: str
    start: int
    end: int
    confidence: float = 1.0


class OptimizationEntityRecognizer:
    """
    Reconoce y extrae entidades de problemas de optimización.

    Usa un modelo spaCy entrenado y aplica post-procesamiento
    para mejorar la precisión.
    """

    def __init__(self, model_path: Optional[str] = None):
        """
        Args:
            model_path: Ruta al modelo entrenado. Si es None, usa modelo base.
        """
        self.logger = logging.getLogger(__name__)
        self.model_path = model_path
        self.nlp = None
        self._load_model()

    def _load_model(self):
        """Carga el modelo spaCy."""
        if self.model_path:
            try:
                self.nlp = spacy.load(self.model_path)
                self.logger.info(f"Modelo cargado desde {self.model_path}")
            except Exception as e:
                self.logger.warning(f"No se pudo cargar modelo: {e}")
                self.nlp = None
        else:
            try:
                self.nlp = spacy.load("es_core_news_sm")
                self.logger.info("Usando modelo base español")
            except Exception as e:
                self.logger.warning(f"No se pudo cargar modelo base: {e}")
                self.nlp = None

    def is_available(self) -> bool:
        """Verifica si el modelo está disponible."""
        return self.nlp is not None

    def extract_entities(self, text: str) -> List[OptimizationEntity]:
        """
        Extrae todas las entidades del texto.

        Args:
            text: Texto a analizar

        Returns:
            Lista de entidades encontradas
        """
        if not self.is_available():
            self.logger.error("Modelo no disponible")
            return []

        doc = self.nlp(text)

        entities = []
        for ent in doc.ents:
            entity = OptimizationEntity(
                text=ent.text,
                label=ent.label_,
                start=ent.start_char,
                end=ent.end_char,
            )
            entities.append(entity)

        return entities

    def extract_by_type(self, text: str, entity_type: str) -> List[OptimizationEntity]:
        """
        Extrae solo entidades de un tipo específico.

        Args:
            text: Texto a analizar
            entity_type: Tipo de entidad (VARIABLE, COEFFICIENT, etc.)

        Returns:
            Lista de entidades del tipo especificado
        """
        all_entities = self.extract_entities(text)
        return [e for e in all_entities if e.label == entity_type]

    def extract_variables(self, text: str) -> List[str]:
        """
        Extrae nombres de variables.

        Returns:
            Lista de nombres de variables
        """
        entities = self.extract_by_type(text, "VARIABLE")
        return [e.text for e in entities]

    def extract_coefficients(self, text: str) -> List[Tuple[float, str]]:
        """
        Extrae coeficientes con sus variables asociadas.

        Returns:
            Lista de (coeficiente, variable)
        """
        entities = self.extract_entities(text)

        coefficients = []
        for i, ent in enumerate(entities):
            if ent.label == "COEFFICIENT":
                # Buscar variable siguiente
                if i + 1 < len(entities) and entities[i + 1].label == "VARIABLE":
                    try:
                        coef = float(ent.text)
                        var = entities[i + 1].text
                        coefficients.append((coef, var))
                    except ValueError:
                        continue

        return coefficients

    def detect_objective_type(self, text: str) -> Optional[str]:
        """
        Detecta si es maximización o minimización.

        Returns:
            "maximize" o "minimize", o None si no se detecta
        """
        entities = self.extract_by_type(text, "OBJECTIVE_TYPE")

        if not entities:
            return None

        text_lower = entities[0].text.lower()
        if any(word in text_lower for word in ["maximizar", "maximice", "max"]):
            return "maximize"
        elif any(word in text_lower for word in ["minimizar", "minimice", "min"]):
            return "minimize"

        return None

    def extract_constraint_info(self, text: str) -> List[Dict[str, Any]]:
        """
        Extrae información de restricciones.

        Returns:
            Lista de dicts con información de cada restricción
        """
        doc = self.nlp(text)

        constraints = []
        current_constraint = {}

        for ent in doc.ents:
            if ent.label_ == "CONSTRAINT_INTRO":
                # Nueva restricción
                if current_constraint:
                    constraints.append(current_constraint)
                current_constraint = {"text": ent.text}

            elif ent.label_ == "CONSTRAINT_OP":
                current_constraint["operator"] = ent.text

            elif ent.label_ == "VALUE" and "operator" in current_constraint:
                try:
                    current_constraint["rhs"] = float(ent.text)
                except ValueError:
                    pass

        if current_constraint:
            constraints.append(current_constraint)

        return constraints

    def extract_structured_problem(self, text: str) -> Dict[str, Any]:
        """
        Extrae problema completo de forma estructurada.

        Returns:
            Dict con todas las componentes del problema
        """
        entities = self.extract_entities(text)

        # Organizar entidades por tipo
        by_type = {}
        for ent in entities:
            if ent.label not in by_type:
                by_type[ent.label] = []
            by_type[ent.label].append(ent.text)

        return {
            "objective_type": self.detect_objective_type(text),
            "variables": by_type.get("VARIABLE", []),
            "coefficients": by_type.get("COEFFICIENT", []),
            "values": by_type.get("VALUE", []),
            "resources": by_type.get("RESOURCE", []),
            "locations": by_type.get("LOCATION", []),
            "products": by_type.get("PRODUCT_TYPE", []),
            "units": by_type.get("UNIT", []),
            "constraints": self.extract_constraint_info(text),
            "all_entities": [(e.text, e.label) for e in entities],
        }

    def display_entities(self, text: str):
        """
        Muestra las entidades extraídas de forma visual.

        Args:
            text: Texto a analizar
        """
        entities = self.extract_entities(text)

        print(f"\n{'='*70}")
        print("ENTIDADES EXTRAÍDAS")
        print("=" * 70)
        print(f"\nTexto: {text}\n")

        # Agrupar por tipo
        by_type = {}
        for ent in entities:
            if ent.label not in by_type:
                by_type[ent.label] = []
            by_type[ent.label].append(ent.text)

        # Mostrar por tipo
        for label in sorted(by_type.keys()):
            print(f"\n{label}:")
            for text in by_type[label]:
                print(f"  - {text}")

    def get_entity_statistics(self, text: str) -> Dict[str, int]:
        """
        Obtiene estadísticas de las entidades extraídas.

        Returns:
            Dict con conteo por tipo de entidad
        """
        entities = self.extract_entities(text)

        stats = {}
        for ent in entities:
            stats[ent.label] = stats.get(ent.label, 0) + 1

        return stats
