"""
Entrenador del modelo spaCy personalizado para optimización.

Entrena un modelo NER (Named Entity Recognition) usando los ejemplos
anotados para reconocer entidades específicas de problemas de optimización.
"""

import spacy
from spacy.training import Example
from spacy.util import minibatch, compounding
import random
from pathlib import Path
from typing import List, Tuple, Dict, Any
import logging


class SpacyModelTrainer:
    """
    Entrena y guarda modelos spaCy personalizados.

    Usa los ejemplos anotados para entrenar un modelo que reconozca
    entidades específicas de problemas de optimización.
    """

    def __init__(self, base_model: str = "es_core_news_sm"):
        """
        Args:
            base_model: Modelo base de spaCy (español)
        """
        self.logger = logging.getLogger(__name__)
        self.base_model = base_model
        self.nlp = None

    def create_blank_model(self, labels: List[str]) -> spacy.Language:
        """
        Crea un modelo en blanco con las etiquetas especificadas.

        Args:
            labels: Lista de etiquetas NER a reconocer

        Returns:
            Modelo spaCy configurado
        """
        # Crear modelo en blanco para español
        self.nlp = spacy.blank("es")

        # Crear el componente NER
        if "ner" not in self.nlp.pipe_names:
            ner = self.nlp.add_pipe("ner")
        else:
            ner = self.nlp.get_pipe("ner")

        # Agregar las etiquetas
        for label in labels:
            ner.add_label(label)

        self.logger.info(f"Modelo creado con {len(labels)} etiquetas")
        return self.nlp

    def load_base_model(self) -> spacy.Language:
        """Carga el modelo base de spaCy."""
        try:
            self.nlp = spacy.load(self.base_model)
            self.logger.info(f"Modelo base '{self.base_model}' cargado")
        except OSError:
            self.logger.warning(
                f"No se pudo cargar '{self.base_model}', creando modelo en blanco"
            )
            self.nlp = spacy.blank("es")

        # Asegurar que tiene NER
        if "ner" not in self.nlp.pipe_names:
            ner = self.nlp.add_pipe("ner", last=True)

        return self.nlp

    def train(
        self,
        training_data: List[Tuple[str, Dict]],
        n_iter: int = 30,
        drop_rate: float = 0.5,
        batch_size: int = 8,
    ) -> Dict[str, Any]:
        """
        Entrena el modelo con los datos proporcionados.

        Args:
            training_data: Lista de (texto, {"entities": [(start, end, label)]})
            n_iter: Número de iteraciones de entrenamiento
            drop_rate: Tasa de dropout para regularización
            batch_size: Tamaño de batch inicial

        Returns:
            Dict con métricas de entrenamiento
        """
        if self.nlp is None:
            raise ValueError("Debe crear o cargar un modelo primero")

        self.logger.info(f"Iniciando entrenamiento con {len(training_data)} ejemplos")

        # Obtener el componente NER
        ner = self.nlp.get_pipe("ner")

        # Agregar etiquetas de los datos de entrenamiento
        for _, annotations in training_data:
            for _, _, label in annotations.get("entities", []):
                ner.add_label(label)

        # Deshabilitar otros pipes durante entrenamiento
        other_pipes = [pipe for pipe in self.nlp.pipe_names if pipe != "ner"]

        losses_history = []

        with self.nlp.disable_pipes(*other_pipes):
            # Obtener nombres de los componentes a entrenar
            optimizer = self.nlp.begin_training()

            for iteration in range(n_iter):
                random.shuffle(training_data)
                losses = {}

                # Crear batches con tamaño variable
                batches = minibatch(
                    training_data, size=compounding(4.0, batch_size, 1.001)
                )

                for batch in batches:
                    examples = []
                    for text, annotations in batch:
                        doc = self.nlp.make_doc(text)
                        example = Example.from_dict(doc, annotations)
                        examples.append(example)

                    # Actualizar el modelo
                    self.nlp.update(
                        examples,
                        drop=drop_rate,
                        losses=losses,
                    )

                losses_history.append(losses.get("ner", 0))

                if (iteration + 1) % 5 == 0:
                    self.logger.info(
                        f"Iteración {iteration + 1}/{n_iter} - Loss: {losses.get('ner', 0):.4f}"
                    )

        self.logger.info("Entrenamiento completado")

        return {
            "n_iterations": n_iter,
            "final_loss": losses_history[-1] if losses_history else 0,
            "loss_history": losses_history,
            "n_examples": len(training_data),
        }

    def evaluate(self, test_data: List[Tuple[str, Dict]]) -> Dict[str, float]:
        """
        Evalúa el modelo con datos de prueba.

        Args:
            test_data: Datos de prueba en formato spaCy

        Returns:
            Dict con métricas de evaluación
        """
        if self.nlp is None:
            raise ValueError("No hay modelo cargado")

        examples = []
        for text, annotations in test_data:
            doc = self.nlp.make_doc(text)
            example = Example.from_dict(doc, annotations)
            examples.append(example)

        scores = self.nlp.evaluate(examples)

        self.logger.info(f"Evaluación completada - Precisión: {scores['ents_p']:.2%}")

        return {
            "precision": scores.get("ents_p", 0),
            "recall": scores.get("ents_r", 0),
            "f1_score": scores.get("ents_f", 0),
        }

    def save_model(self, output_dir: str):
        """
        Guarda el modelo entrenado.

        Args:
            output_dir: Directorio donde guardar el modelo
        """
        if self.nlp is None:
            raise ValueError("No hay modelo para guardar")

        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        self.nlp.to_disk(output_path)
        self.logger.info(f"Modelo guardado en {output_path}")

    def load_model(self, model_dir: str):
        """
        Carga un modelo previamente entrenado.

        Args:
            model_dir: Directorio del modelo
        """
        model_path = Path(model_dir)
        if not model_path.exists():
            raise ValueError(f"No existe el directorio {model_path}")

        self.nlp = spacy.load(model_path)
        self.logger.info(f"Modelo cargado desde {model_path}")

    def test_model(self, text: str) -> List[Tuple[str, str]]:
        """
        Prueba el modelo con un texto.

        Args:
            text: Texto a analizar

        Returns:
            Lista de (texto_entidad, etiqueta)
        """
        if self.nlp is None:
            raise ValueError("No hay modelo cargado")

        doc = self.nlp(text)
        return [(ent.text, ent.label_) for ent in doc.ents]

    def visualize_entities(self, text: str):
        """
        Visualiza las entidades detectadas en un texto.

        Args:
            text: Texto a analizar
        """
        if self.nlp is None:
            raise ValueError("No hay modelo cargado")

        doc = self.nlp(text)

        print(f"\nTexto: {text}\n")
        print("Entidades detectadas:")
        for ent in doc.ents:
            print(f"  {ent.text:30s} -> {ent.label_}")


def quick_train_model(
    training_data: List[Tuple[str, Dict]],
    output_dir: str = "models/optimization_ner",
    n_iter: int = 30,
) -> SpacyModelTrainer:
    """
    Función auxiliar para entrenar rápidamente un modelo.

    Args:
        training_data: Datos de entrenamiento
        output_dir: Dónde guardar el modelo
        n_iter: Iteraciones de entrenamiento

    Returns:
        Trainer con modelo entrenado
    """
    # Extraer etiquetas únicas
    labels = set()
    for _, annotations in training_data:
        for _, _, label in annotations["entities"]:
            labels.add(label)

    # Crear y entrenar
    trainer = SpacyModelTrainer()
    trainer.create_blank_model(list(labels))

    # Entrenar
    metrics = trainer.train(training_data, n_iter=n_iter)

    # Guardar
    trainer.save_model(output_dir)

    print(f"\n✅ Modelo entrenado y guardado en {output_dir}")
    print(f"Loss final: {metrics['final_loss']:.4f}")

    return trainer
