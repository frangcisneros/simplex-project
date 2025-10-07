"""
Script directo para probar Llama 3.1:8b con el problema complejo
y verificar si puede generar todas las restricciones necesarias.
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

print("🧠 PROBANDO DIRECTAMENTE CON LLAMA 3.1:8B")
print("=" * 80)

# Configurar petición específicamente para Llama 3.1:8b
request_data = {
    "model": "llama3.1:8b",
    "prompt": prompt,
    "stream": False,
    "options": {
        "temperature": 0.0,  # Determinístico
        "top_p": 0.9,
        "num_predict": 2048,  # Más espacio para análisis complejo
    },
}

try:
    print("⏳ Generando respuesta con Llama 3.1:8b...")
    response = requests.post(
        "http://localhost:11434/api/generate", json=request_data, timeout=120
    )

    if response.status_code == 200:
        response_data = response.json()
        generated_text = response_data.get("response", "").strip()

        print("📄 RESPUESTA COMPLETA:")
        print("=" * 80)
        print(generated_text)
        print("=" * 80)

        # Parsear JSON
        import re

        json_match = re.search(r"\{.*\}", generated_text, re.DOTALL)
        if json_match:
            json_text = json_match.group()
            data = json.loads(json_text)

            print("\n📊 JSON PARSEADO:")
            print("=" * 80)
            print(json.dumps(data, indent=2, ensure_ascii=False))
            print("=" * 80)

            # Análisis detallado
            print("\n🔍 ANÁLISIS DETALLADO:")
            print("-" * 50)

            obj_coeffs = data.get("objective_coefficients", [])
            constraints = data.get("constraints", [])
            var_names = data.get("variable_names", [])

            print(f"Variables ({len(var_names)}): {var_names}")
            print(f"Función objetivo ({len(obj_coeffs)}): {obj_coeffs}")
            print(f"Restricciones ({len(constraints)}):")

            for i, constraint in enumerate(constraints):
                coeffs = constraint.get("coefficients", [])
                op = constraint.get("operator", "")
                rhs = constraint.get("rhs", 0)
                print(f"  R{i+1}: {coeffs} {op} {rhs}")

            # Verificar si es la solución esperada
            expected_obj = [420, 360, 300, 420, 360, 300, 420, 360, 300]
            if obj_coeffs == expected_obj:
                print("\n✅ ¡FUNCIÓN OBJETIVO PERFECTA!")
            else:
                print(f"\n⚠️ Función objetivo esperada: {expected_obj}")

            # Verificar restricciones necesarias
            print("\n📋 RESTRICCIONES NECESARIAS:")
            print("- 3 restricciones de capacidad de planta")
            print("- 3 restricciones de espacio por planta")
            print("- 3 restricciones de demanda por producto")
            print("- Total esperado: 9 restricciones")
            print(f"- Generadas: {len(constraints)} restricciones")

            if len(constraints) >= 9:
                print("✅ Número suficiente de restricciones")
            else:
                print("⚠️ Faltan restricciones")

        else:
            print("❌ No se encontró JSON válido en la respuesta")

    else:
        print(f"❌ Error HTTP: {response.status_code}")
        print(response.text)

except Exception as e:
    print(f"❌ Error: {e}")
