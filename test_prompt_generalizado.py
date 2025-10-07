"""
Test del prompt generalizado con diferentes problemas
"""

import requests
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))
from nlp.config import PromptTemplates


def test_problem(problem_file, problem_name):
    """Prueba un problema específico"""

    # Leer el problema
    with open(problem_file, "r", encoding="utf-8") as f:
        problem_text = f.read()

    # Crear el prompt
    prompt = PromptTemplates.OPTIMIZATION_EXTRACTION_PROMPT.format(
        problem_text=problem_text
    )

    print(f"\n{'='*80}")
    print(f"🧠 PROBANDO: {problem_name}")
    print(f"{'='*80}")

    try:
        print(f"⏳ Generando respuesta con llama3.1:8b...")

        data = {"model": "llama3.1:8b", "prompt": prompt, "stream": False}

        response = requests.post(
            "http://localhost:11434/api/generate", json=data, timeout=60
        )

        if response.status_code == 200:
            result = response.json()
            response_text = result.get("response", "")

            print("📄 RESPUESTA:")
            print("-" * 40)

            # Intentar parsear JSON
            try:
                # Buscar el JSON en la respuesta
                start = response_text.find("{")
                end = response_text.rfind("}") + 1

                if start >= 0 and end > start:
                    json_str = response_text[start:end]
                    parsed_json = json.loads(json_str)

                    print(json.dumps(parsed_json, indent=2))

                    # Análisis básico
                    variables = parsed_json.get("variable_names", [])
                    objective_coeffs = parsed_json.get("objective_coefficients", [])
                    constraints = parsed_json.get("constraints", [])

                    print(f"\n📊 ANÁLISIS:")
                    print(f"Variables: {len(variables)}")
                    print(f"Coeficientes objetivo: {len(objective_coeffs)}")
                    print(f"Restricciones: {len(constraints)}")

                    # Verificar consistencia
                    if len(variables) == len(objective_coeffs):
                        print("✅ Variables y coeficientes consistentes")
                    else:
                        print(
                            f"⚠️ Inconsistencia: {len(variables)} vars vs {len(objective_coeffs)} coefs"
                        )

                    # Verificar restricciones
                    valid_constraints = 0
                    for i, constraint in enumerate(constraints):
                        coeffs = constraint.get("coefficients", [])
                        if len(coeffs) == len(variables):
                            valid_constraints += 1
                        else:
                            print(
                                f"⚠️ R{i+1}: {len(coeffs)} coefs, esperado {len(variables)}"
                            )

                    if valid_constraints == len(constraints):
                        print(f"✅ Todas las {len(constraints)} restricciones válidas")
                    else:
                        print(
                            f"⚠️ Solo {valid_constraints}/{len(constraints)} restricciones válidas"
                        )

                else:
                    print("❌ No se encontró JSON válido en la respuesta")
                    print(
                        response_text[:500] + "..."
                        if len(response_text) > 500
                        else response_text
                    )

            except json.JSONDecodeError as e:
                print(f"❌ Error parseando JSON: {e}")
                print("Respuesta recibida:")
                print(
                    response_text[:500] + "..."
                    if len(response_text) > 500
                    else response_text
                )
        else:
            print(f"❌ Error en la API: {response.status_code}")

    except Exception as e:
        print(f"❌ Error: {e}")


def main():
    """Prueba diferentes problemas"""

    print("🚀 PROBANDO PROMPT GENERALIZADO CON DIFERENTES PROBLEMAS")

    problems = [
        ("ejemplos/nlp/problema_complejo.txt", "PROBLEMA PLANTAS Y PRODUCTOS"),
        ("ejemplos/nlp/problema_compolejo2.txt", "PROBLEMA GASOLINAS Y MEZCLAS"),
    ]

    for problem_file, problem_name in problems:
        if os.path.exists(problem_file):
            test_problem(problem_file, problem_name)
        else:
            print(f"❌ No encontrado: {problem_file}")

    print(f"\n{'='*80}")
    print(
        "🎯 CONCLUSIÓN: ¿El prompt generalizado funciona para diferentes tipos de problemas?"
    )
    print(f"{'='*80}")


if __name__ == "__main__":
    main()
