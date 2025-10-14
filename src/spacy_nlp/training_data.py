"""
Datos de entrenamiento para el modelo spaCy especializado.

Incluye ejemplos anotados de problemas de optimización, desde simples hasta muy complejos.
Las anotaciones identifican:
- VARIABLE: nombres de variables de decisión
- COEFFICIENT: coeficientes numéricos
- OBJECTIVE_TYPE: maximizar/minimizar
- CONSTRAINT_OP: operadores de restricción
- VALUE: valores numéricos
- UNIT: unidades de medida
- PRODUCT_TYPE: tipos de productos/recursos
"""

from typing import List, Dict, Tuple, Any
import json


class TrainingDataGenerator:
    """
    Genera y gestiona datos de entrenamiento anotados para spaCy.

    Los datos están en formato spaCy: (texto, {"entities": [(start, end, label)]})
    """

    def __init__(self):
        self.training_examples = []
        self._generate_all_examples()

    def _generate_all_examples(self):
        """Genera todos los ejemplos de entrenamiento."""
        # Ejemplos simples
        self.training_examples.extend(self._simple_examples())

        # Ejemplos de producción
        self.training_examples.extend(self._production_examples())

        # Ejemplos de transporte
        self.training_examples.extend(self._transportation_examples())

        # Ejemplos de mezcla
        self.training_examples.extend(self._blending_examples())

        # Ejemplos complejos multi-planta
        self.training_examples.extend(self._complex_multiplant_examples())

        # Ejemplos de refinería (como tu problema complejo 2)
        self.training_examples.extend(self._refinery_examples())

    def _simple_examples(self) -> List[Tuple[str, Dict]]:
        """Ejemplos simples para empezar."""
        return [
            (
                "Maximizar Z = 3x + 2y",
                {
                    "entities": [
                        (0, 9, "OBJECTIVE_TYPE"),  # Maximizar
                        (10, 11, "OBJ_VAR"),  # Z
                        (14, 15, "COEFFICIENT"),  # 3
                        (15, 16, "VARIABLE"),  # x
                        (19, 20, "COEFFICIENT"),  # 2
                        (20, 21, "VARIABLE"),  # y
                    ]
                },
            ),
            (
                "Minimizar costo = 5x1 + 3x2 + 4x3",
                {
                    "entities": [
                        (0, 9, "OBJECTIVE_TYPE"),  # Minimizar
                        (10, 15, "OBJ_VAR"),  # costo
                        (18, 19, "COEFFICIENT"),  # 5
                        (19, 21, "VARIABLE"),  # x1
                        (24, 25, "COEFFICIENT"),  # 3
                        (25, 27, "VARIABLE"),  # x2
                        (30, 31, "COEFFICIENT"),  # 4
                        (31, 33, "VARIABLE"),  # x3
                    ]
                },
            ),
            (
                "sujeto a 2x + 3y <= 100",
                {
                    "entities": [
                        (0, 8, "CONSTRAINT_INTRO"),  # sujeto a
                        (9, 10, "COEFFICIENT"),  # 2
                        (10, 11, "VARIABLE"),  # x
                        (14, 15, "COEFFICIENT"),  # 3
                        (15, 16, "VARIABLE"),  # y
                        (17, 19, "CONSTRAINT_OP"),  # <=
                        (20, 23, "VALUE"),  # 100
                    ]
                },
            ),
            (
                "x + 2y >= 50",
                {
                    "entities": [
                        (0, 1, "VARIABLE"),  # x
                        (4, 5, "COEFFICIENT"),  # 2
                        (5, 6, "VARIABLE"),  # y
                        (7, 9, "CONSTRAINT_OP"),  # >=
                        (10, 12, "VALUE"),  # 50
                    ]
                },
            ),
        ]

    def _production_examples(self) -> List[Tuple[str, Dict]]:
        """Ejemplos de problemas de producción."""
        return [
            (
                "Una empresa fabrica sillas y mesas. Cada silla genera 50 dólares de ganancia y cada mesa 40 dólares.",
                {
                    "entities": [
                        (22, 28, "VARIABLE"),  # sillas
                        (31, 36, "VARIABLE"),  # mesas
                        (43, 48, "VARIABLE"),  # silla
                        (57, 59, "COEFFICIENT"),  # 50
                        (60, 67, "UNIT"),  # dólares
                        (71, 79, "OBJECTIVE_CONCEPT"),  # ganancia
                        (89, 93, "VARIABLE"),  # mesa
                        (94, 96, "COEFFICIENT"),  # 40
                        (97, 104, "UNIT"),  # dólares
                    ]
                },
            ),
            (
                "La producción de sillas requiere 3 horas de mano de obra y 2 unidades de madera",
                {
                    "entities": [
                        (17, 23, "VARIABLE"),  # sillas
                        (33, 34, "COEFFICIENT"),  # 3
                        (35, 40, "UNIT"),  # horas
                        (44, 56, "RESOURCE"),  # mano de obra
                        (59, 60, "COEFFICIENT"),  # 2
                        (61, 69, "UNIT"),  # unidades
                        (73, 79, "RESOURCE"),  # madera
                    ]
                },
            ),
            (
                "Disponemos de 150 horas de trabajo y 100 unidades de material",
                {
                    "entities": [
                        (15, 18, "VALUE"),  # 150
                        (19, 24, "UNIT"),  # horas
                        (28, 35, "RESOURCE"),  # trabajo
                        (38, 41, "VALUE"),  # 100
                        (42, 50, "UNIT"),  # unidades
                        (54, 62, "RESOURCE"),  # material
                    ]
                },
            ),
        ]

    def _transportation_examples(self) -> List[Tuple[str, Dict]]:
        """Ejemplos de problemas de transporte."""
        return [
            (
                "Enviar mercancía desde la planta A a los almacenes 1, 2 y 3",
                {
                    "entities": [
                        (7, 16, "PRODUCT_TYPE"),  # mercancía
                        (29, 36, "LOCATION"),  # planta A
                        (43, 54, "LOCATION"),  # almacenes
                        (55, 56, "LOCATION_ID"),  # 1
                        (58, 59, "LOCATION_ID"),  # 2
                        (62, 63, "LOCATION_ID"),  # 3
                    ]
                },
            ),
            (
                "El costo de envío desde A a B es 10 dólares por unidad",
                {
                    "entities": [
                        (3, 8, "OBJECTIVE_CONCEPT"),  # costo
                        (12, 17, "ACTION"),  # envío
                        (24, 25, "LOCATION"),  # A
                        (28, 29, "LOCATION"),  # B
                        (33, 35, "COEFFICIENT"),  # 10
                        (36, 43, "UNIT"),  # dólares
                        (48, 55, "UNIT"),  # unidad
                    ]
                },
            ),
        ]

    def _blending_examples(self) -> List[Tuple[str, Dict]]:
        """Ejemplos de problemas de mezcla."""
        return [
            (
                "Mezclar gasolina tipo A con número de performance 107 y presión de vapor 5",
                {
                    "entities": [
                        (8, 16, "PRODUCT_TYPE"),  # gasolina
                        (22, 23, "PRODUCT_ID"),  # A
                        (29, 51, "PROPERTY"),  # número de performance
                        (52, 55, "VALUE"),  # 107
                        (58, 75, "PROPERTY"),  # presión de vapor
                        (76, 77, "VALUE"),  # 5
                    ]
                },
            ),
            (
                "La mezcla debe tener al menos 100 de NP y no más de 7 de PV",
                {
                    "entities": [
                        (3, 9, "PRODUCT_TYPE"),  # mezcla
                        (20, 28, "CONSTRAINT_TYPE"),  # al menos
                        (29, 32, "VALUE"),  # 100
                        (36, 38, "PROPERTY"),  # NP
                        (41, 49, "CONSTRAINT_TYPE"),  # no más de
                        (50, 51, "VALUE"),  # 7
                        (55, 57, "PROPERTY"),  # PV
                    ]
                },
            ),
        ]

    def _complex_multiplant_examples(self) -> List[Tuple[str, Dict]]:
        """Ejemplos complejos multi-planta (basados en tu problema complejo 1)."""
        return [
            (
                "La planta 1 tiene capacidad para producir 750 unidades diarias",
                {
                    "entities": [
                        (3, 11, "LOCATION"),  # planta 1
                        (12, 13, "LOCATION_ID"),  # 1
                        (20, 29, "RESOURCE"),  # capacidad
                        (39, 42, "VALUE"),  # 750
                        (43, 51, "UNIT"),  # unidades
                        (52, 59, "TIME_UNIT"),  # diarias
                    ]
                },
            ),
            (
                "El producto grande da una ganancia de 420 dólares",
                {
                    "entities": [
                        (3, 11, "PRODUCT_TYPE"),  # producto
                        (12, 18, "SIZE"),  # grande
                        (26, 34, "OBJECTIVE_CONCEPT"),  # ganancia
                        (38, 41, "COEFFICIENT"),  # 420
                        (42, 49, "UNIT"),  # dólares
                    ]
                },
            ),
            (
                "Los tamaños grande, mediano y chico dan ganancias de 420, 360 y 300 respectivamente",
                {
                    "entities": [
                        (12, 18, "SIZE"),  # grande
                        (20, 27, "SIZE"),  # mediano
                        (30, 35, "SIZE"),  # chico
                        (40, 49, "OBJECTIVE_CONCEPT"),  # ganancias
                        (53, 56, "COEFFICIENT"),  # 420
                        (58, 61, "COEFFICIENT"),  # 360
                        (64, 67, "COEFFICIENT"),  # 300
                    ]
                },
            ),
            (
                "Cada unidad grande requiere 20 pies cuadrados de espacio",
                {
                    "entities": [
                        (5, 11, "UNIT"),  # unidad
                        (12, 18, "SIZE"),  # grande
                        (19, 27, "ACTION"),  # requiere
                        (28, 30, "COEFFICIENT"),  # 20
                        (31, 45, "UNIT"),  # pies cuadrados
                        (49, 56, "RESOURCE"),  # espacio
                    ]
                },
            ),
            (
                "Se pueden vender 900 unidades del tamaño grande",
                {
                    "entities": [
                        (16, 19, "VALUE"),  # 900
                        (20, 28, "UNIT"),  # unidades
                        (33, 39, "SIZE"),  # tamaño
                        (40, 46, "SIZE"),  # grande
                    ]
                },
            ),
        ]

    def _refinery_examples(self) -> List[Tuple[str, Dict]]:
        """Ejemplos de refinería (basados en tu problema complejo 2)."""
        return [
            (
                "La refinería produce gas 1 con NP de 107 y PV de 5",
                {
                    "entities": [
                        (3, 12, "FACILITY"),  # refinería
                        (21, 26, "PRODUCT_TYPE"),  # gas 1
                        (27, 28, "PRODUCT_ID"),  # 1
                        (33, 35, "PROPERTY"),  # NP
                        (39, 42, "VALUE"),  # 107
                        (45, 47, "PROPERTY"),  # PV
                        (51, 52, "VALUE"),  # 5
                    ]
                },
            ),
            (
                "Se producen 3814 barriles diarios de gas 1",
                {
                    "entities": [
                        (12, 16, "VALUE"),  # 3814
                        (17, 25, "UNIT"),  # barriles
                        (26, 33, "TIME_UNIT"),  # diarios
                        (37, 42, "PRODUCT_TYPE"),  # gas 1
                        (43, 44, "PRODUCT_ID"),  # 1
                    ]
                },
            ),
            (
                "El costo de producción es de 3.5 dólares por barril",
                {
                    "entities": [
                        (3, 8, "OBJECTIVE_CONCEPT"),  # costo
                        (12, 22, "ACTION"),  # producción
                        (29, 32, "COEFFICIENT"),  # 3.5
                        (33, 40, "UNIT"),  # dólares
                        (45, 51, "UNIT"),  # barril
                    ]
                },
            ),
            (
                "El precio de venta es de 24.83 dólares por barril",
                {
                    "entities": [
                        (3, 9, "OBJECTIVE_CONCEPT"),  # precio
                        (13, 18, "ACTION"),  # venta
                        (25, 30, "COEFFICIENT"),  # 24.83
                        (31, 38, "UNIT"),  # dólares
                        (43, 49, "UNIT"),  # barril
                    ]
                },
            ),
            (
                "La avgas A requiere al menos 100 de NP y no más de 7 de PV",
                {
                    "entities": [
                        (3, 10, "PRODUCT_TYPE"),  # avgas A
                        (11, 12, "PRODUCT_ID"),  # A
                        (13, 21, "ACTION"),  # requiere
                        (22, 30, "CONSTRAINT_TYPE"),  # al menos
                        (31, 34, "VALUE"),  # 100
                        (38, 40, "PROPERTY"),  # NP
                        (43, 51, "CONSTRAINT_TYPE"),  # no más de
                        (52, 53, "VALUE"),  # 7
                        (57, 59, "PROPERTY"),  # PV
                    ]
                },
            ),
            (
                "El NP de la mezcla es un promedio de los NP individuales",
                {
                    "entities": [
                        (3, 5, "PROPERTY"),  # NP
                        (12, 18, "PRODUCT_TYPE"),  # mezcla
                        (25, 33, "RELATION"),  # promedio
                        (41, 43, "PROPERTY"),  # NP
                    ]
                },
            ),
        ]

    def get_training_data(self) -> List[Tuple[str, Dict]]:
        """Retorna todos los ejemplos de entrenamiento."""
        return self.training_examples

    def get_labels(self) -> List[str]:
        """Retorna todas las etiquetas únicas usadas."""
        labels = set()
        for _, annotations in self.training_examples:
            for _, _, label in annotations["entities"]:
                labels.add(label)
        return sorted(list(labels))

    def save_to_json(self, filepath: str):
        """Guarda los datos de entrenamiento en formato JSON."""
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(self.training_examples, f, indent=2, ensure_ascii=False)

    def load_from_json(self, filepath: str):
        """Carga datos de entrenamiento desde JSON."""
        with open(filepath, "r", encoding="utf-8") as f:
            self.training_examples = json.load(f)


class ProblemAnnotator:
    """
    Herramienta para anotar nuevos problemas manualmente.

    Permite crear anotaciones interactivas para expandir el dataset.
    """

    def __init__(self):
        self.annotations = []

    def annotate_text(
        self, text: str, entities: List[Tuple[int, int, str]]
    ) -> Tuple[str, Dict]:
        """
        Anota un texto con entidades.

        Args:
            text: Texto del problema
            entities: Lista de (start, end, label)

        Returns:
            Tupla en formato spaCy
        """
        annotation = (text, {"entities": entities})
        self.annotations.append(annotation)
        return annotation

    def validate_annotations(self) -> bool:
        """Valida que las anotaciones no se solapen."""
        for text, annot in self.annotations:
            entities = sorted(annot["entities"], key=lambda x: x[0])
            for i in range(len(entities) - 1):
                if entities[i][1] > entities[i + 1][0]:
                    print(f"Warning: Overlapping entities in '{text}'")
                    print(f"  {entities[i]} overlaps with {entities[i+1]}")
                    return False
        return True

    def get_annotations(self) -> List[Tuple[str, Dict]]:
        """Retorna todas las anotaciones."""
        return self.annotations

    def display_annotated_text(self, text: str, entities: List[Tuple[int, int, str]]):
        """Muestra el texto con las anotaciones de forma visual."""
        print(f"\nTexto: {text}")
        print("\nEntidades:")
        for start, end, label in sorted(entities, key=lambda x: x[0]):
            entity_text = text[start:end]
            print(f"  [{start}:{end}] {label:20s} -> '{entity_text}'")


# Ejemplos adicionales muy complejos
COMPLEX_EXAMPLES_EXTRA = [
    # Problema de asignación multi-objetivo
    (
        "Asignar 5 trabajadores a 4 proyectos minimizando tiempo total y costo, donde el trabajador 1 tarda 10 horas en proyecto A con costo 150, trabajador 2 tarda 8 horas en proyecto B con costo 120",
        {
            "entities": [
                (8, 9, "VALUE"),  # 5
                (10, 22, "RESOURCE"),  # trabajadores
                (25, 26, "VALUE"),  # 4
                (27, 36, "RESOURCE"),  # proyectos
                (37, 48, "OBJECTIVE_TYPE"),  # minimizando
                (49, 55, "OBJECTIVE_CONCEPT"),  # tiempo
                (56, 61, "OBJECTIVE_CONCEPT"),  # total
                (64, 69, "OBJECTIVE_CONCEPT"),  # costo
                (81, 92, "RESOURCE"),  # trabajador 1
                (93, 94, "VALUE"),  # 1
                (101, 103, "VALUE"),  # 10
                (104, 109, "UNIT"),  # horas
                (113, 121, "RESOURCE"),  # proyecto
                (122, 123, "LOCATION_ID"),  # A
                (128, 133, "OBJECTIVE_CONCEPT"),  # costo
                (134, 137, "VALUE"),  # 150
                (139, 150, "RESOURCE"),  # trabajador 2
                (151, 152, "VALUE"),  # 2
                (159, 160, "VALUE"),  # 8
                (161, 166, "UNIT"),  # horas
                (170, 178, "RESOURCE"),  # proyecto
                (179, 180, "LOCATION_ID"),  # B
                (185, 190, "OBJECTIVE_CONCEPT"),  # costo
                (191, 194, "VALUE"),  # 120
            ]
        },
    ),
]
