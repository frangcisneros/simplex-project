"""
Debug script para ver exactamente qué JSON está generando Mistral.
"""

import sys
import json
from pathlib import Path

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from nlp import OllamaNLPProcessor, NLPModelType


def debug_mistral_output():
    print("🔍 Debug: Viendo exactamente qué genera Mistral...")

    # Cargar problema
    problem_file = Path("ejemplos/nlp/problema_complejo.txt")
    problem_text = problem_file.read_text(encoding="utf-8")

    # Crear procesador
    processor = OllamaNLPProcessor(model_type=NLPModelType.MISTRAL_7B)

    # Generar respuesta sin procesar
    from nlp.config import PromptTemplates
    import requests

    prompt = PromptTemplates.OPTIMIZATION_EXTRACTION_PROMPT.format(
        problem_text=problem_text
    )

    print("📝 Prompt enviado:")
    print("-" * 50)
    print(prompt[:200] + "...")
    print("-" * 50)

    request_data = {
        "model": "mistral:7b",
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.0,
            "top_p": 0.8,
            "num_predict": 1024,
        },
    }

    print("\n🔄 Generando respuesta...")
    response = requests.post(
        "http://localhost:11434/api/generate", json=request_data, timeout=60
    )

    if response.status_code == 200:
        data = response.json()
        generated_text = data.get("response", "").strip()

        print("\n📄 Respuesta completa:")
        print("-" * 50)
        print(generated_text)
        print("-" * 50)

        # Intentar parsear como JSON
        try:
            # Buscar JSON en la respuesta
            import re

            json_match = re.search(r"\{.*\}", generated_text, re.DOTALL)
            if json_match:
                json_text = json_match.group(0)
                parsed = json.loads(json_text)

                print("\n✅ JSON parseado exitosamente:")
                print(json.dumps(parsed, indent=2))

                print("\n🔍 Análisis de restricciones:")
                for i, constraint in enumerate(parsed.get("constraints", [])):
                    rhs = constraint.get("rhs")
                    print(f"  Restricción {i+1}: RHS = {rhs} (tipo: {type(rhs)})")

            else:
                print("\n❌ No se encontró JSON en la respuesta")

        except json.JSONDecodeError as e:
            print(f"\n❌ Error parseando JSON: {e}")
    else:
        print(f"❌ Error en API: {response.status_code}")


if __name__ == "__main__":
    debug_mistral_output()
