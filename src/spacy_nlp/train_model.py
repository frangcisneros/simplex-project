"""
Script para entrenar el modelo spaCy con ejemplos de optimización.

Entrena un modelo NER personalizado usando los ejemplos anotados,
incluyendo problemas complejos multi-planta y de refinería.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import logging
from spacy_nlp.training_data import TrainingDataGenerator
from spacy_nlp.model_trainer import SpacyModelTrainer, quick_train_model

# Configurar logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


def main():
    """Entrena y guarda el modelo."""
    print("\n" + "=" * 70)
    print("ENTRENAMIENTO DEL MODELO SPACY PARA OPTIMIZACIÓN")
    print("=" * 70)

    # 1. Generar datos de entrenamiento
    print("\n📚 Generando datos de entrenamiento...")
    generator = TrainingDataGenerator()
    training_data = generator.get_training_data()
    labels = generator.get_labels()

    print(f"✅ Generados {len(training_data)} ejemplos de entrenamiento")
    print(f"✅ Etiquetas: {', '.join(labels)}")

    # Mostrar algunos ejemplos
    print("\n📋 Ejemplos de entrenamiento:")
    for i, (text, annot) in enumerate(training_data[:3], 1):
        print(f"\n{i}. {text[:80]}...")
        print(f"   Entidades: {len(annot['entities'])}")

    # Opcionalmente guardar datos
    output_file = "training_data_optimization.json"
    generator.save_to_json(output_file)
    print(f"\n💾 Datos guardados en {output_file}")

    # 2. Entrenar modelo
    print("\n🏋️ Entrenando modelo...")
    print("⏳ Esto puede tardar varios minutos...")

    model_dir = "models/optimization_ner"

    trainer = quick_train_model(
        training_data=training_data,
        output_dir=model_dir,
        n_iter=30,  # Puedes aumentar para mejor precisión
    )

    # 3. Probar modelo
    print("\n🧪 Probando modelo entrenado...")

    test_texts = [
        "Maximizar Z = 3x + 2y sujeto a 2x + y <= 100",
        "La planta 1 tiene capacidad para producir 750 unidades diarias",
        "El producto grande da una ganancia de 420 dólares",
        "La refinería produce gas 1 con NP de 107 y PV de 5",
    ]

    for text in test_texts:
        print(f"\n📝 Texto: {text}")
        entities = trainer.test_model(text)
        if entities:
            print("   Entidades detectadas:")
            for ent_text, label in entities:
                print(f"     - {ent_text:20s} -> {label}")
        else:
            print("   (No se detectaron entidades)")

    print("\n" + "=" * 70)
    print("✅ ENTRENAMIENTO COMPLETADO")
    print("=" * 70)
    print(f"\n💡 Modelo guardado en: {model_dir}")
    print("\n📌 Para usar el modelo:")
    print(f"   from spacy_nlp import SpacyNLPProcessor")
    print(f"   processor = SpacyNLPProcessor(model_path='{model_dir}')")


if __name__ == "__main__":
    main()
