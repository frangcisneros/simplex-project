"""
Script para debuggear el prompt y ver exactamente qué está generando Mistral.
"""

import requests
import json
import sys
import os

# Agregar src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from nlp.config import PromptTemplates

# Leer el problema complejo
with open("ejemplos/nlp/problema_complejo.txt", "r", encoding="utf-8") as f:
    problem_text = f.read()

# Generar el prompt
prompt = PromptTemplates.OPTIMIZATION_EXTRACTION_PROMPT.format(
    problem_text=problem_text
)

print("=" * 80)
print("PROMPT QUE SE ENVÍA A MISTRAL:")
print("=" * 80)
print(prompt)
print("=" * 80)

# Llamar a Ollama
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

print("Enviando petición a Ollama...")
response = requests.post("http://localhost:11434/api/generate", json=request_data)

if response.status_code == 200:
    response_data = response.json()
    generated_text = response_data.get("response", "").strip()

    print("\nRESPUESTA COMPLETA DE MISTRAL:")
    print("=" * 80)
    print(generated_text)
    print("=" * 80)

    # Intentar parsear JSON
    try:
        # Buscar JSON en la respuesta
        import re

        json_match = re.search(r"\{.*\}", generated_text, re.DOTALL)
        if json_match:
            json_text = json_match.group()
            data = json.loads(json_text)

            print("\nJSON PARSEADO:")
            print("=" * 80)
            print(json.dumps(data, indent=2, ensure_ascii=False))
            print("=" * 80)

            # Analizar dimensiones
            obj_coeffs = data.get("objective_coefficients", [])
            constraints = data.get("constraints", [])

            print(f"\nANÁLISIS DE DIMENSIONES:")
            print(f"Coeficientes objetivo: {len(obj_coeffs)} variables")
            print(f"Variables: {obj_coeffs}")

            for i, constraint in enumerate(constraints):
                coeffs = constraint.get("coefficients", [])
                print(f"Restricción {i}: {len(coeffs)} coeficientes -> {coeffs}")

        else:
            print("No se encontró JSON válido en la respuesta")

    except json.JSONDecodeError as e:
        print(f"Error parseando JSON: {e}")

else:
    print(f"Error en Ollama: {response.status_code}")
    print(response.text)
