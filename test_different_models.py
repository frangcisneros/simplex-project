"""
Script para probar diferentes modelos de Ollama y ver cuál genera
mejores restricciones para el problema complejo.
"""

import requests
import json
import sys
import os

# Agregar src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from nlp.config import PromptTemplates, NLPModelType

# Modelos a probar
MODELS_TO_TEST = ["mistral:7b", "llama3.1:8b", "qwen2.5:14b", "llama3.2:3b"]

# Leer el problema complejo
with open("ejemplos/nlp/problema_complejo.txt", "r", encoding="utf-8") as f:
    problem_text = f.read()


def test_model(model_name):
    """Prueba un modelo específico y analiza su respuesta."""
    print(f"\n{'='*80}")
    print(f"PROBANDO MODELO: {model_name}")
    print(f"{'='*80}")

    # Generar el prompt
    prompt = PromptTemplates.OPTIMIZATION_EXTRACTION_PROMPT.format(
        problem_text=problem_text
    )

    # Configuración de la petición
    request_data = {
        "model": model_name,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.0,
            "top_p": 0.9,
            "num_predict": 2048,
        },
    }

    try:
        print(f"Enviando petición a {model_name}...")
        response = requests.post(
            "http://localhost:11434/api/generate", json=request_data, timeout=300
        )

        if response.status_code != 200:
            print(f"❌ Error en API: {response.status_code}")
            return None

        response_data = response.json()
        generated_text = response_data.get("response", "").strip()

        # Extraer JSON
        import re

        json_match = re.search(r"\{.*\}", generated_text, re.DOTALL)
        if not json_match:
            print("❌ No se encontró JSON en la respuesta")
            return None

        json_text = json_match.group()
        data = json.loads(json_text)

        # Analizar la estructura
        obj_coeffs = data.get("objective_coefficients", [])
        constraints = data.get("constraints", [])
        var_names = data.get("variable_names", [])

        print(f"\n📊 ANÁLISIS DEL MODELO {model_name}:")
        print(f"Variables objetivo: {len(obj_coeffs)}")
        print(f"Número de restricciones: {len(constraints)}")
        print(f"Nombres de variables: {len(var_names)}")

        # Verificar consistencia dimensional
        consistent = True
        if len(obj_coeffs) != len(var_names):
            print(
                f"❌ Inconsistencia: {len(obj_coeffs)} coef. obj vs {len(var_names)} nombres"
            )
            consistent = False

        for i, constraint in enumerate(constraints):
            coeffs = constraint.get("coefficients", [])
            if len(coeffs) != len(obj_coeffs):
                print(
                    f"❌ Restricción {i}: {len(coeffs)} coef vs {len(obj_coeffs)} esperados"
                )
                consistent = False

        if consistent:
            print("✅ Dimensiones consistentes")

        # Mostrar estructura de restricciones
        print(f"\nESTRUCTURA DE RESTRICCIONES:")
        for i, constraint in enumerate(constraints):
            coeffs = constraint.get("coefficients", [])
            rhs = constraint.get("rhs", 0)
            print(f"  {i+1}. {coeffs} ≤ {rhs}")

        # Verificar si parece correcto para el problema 3x3
        expected_vars = 9  # 3 plantas x 3 productos
        if len(obj_coeffs) == expected_vars and consistent:
            print("🎯 Este modelo parece generar la estructura correcta")
        else:
            print("⚠️  Este modelo no genera la estructura esperada")

        return data

    except requests.Timeout:
        print(f"❌ Timeout con {model_name}")
        return None
    except json.JSONDecodeError as e:
        print(f"❌ Error JSON en {model_name}: {e}")
        return None
    except Exception as e:
        print(f"❌ Error inesperado con {model_name}: {e}")
        return None


def main():
    print("🔬 TESTING DIFFERENT MODELS FOR COMPLEX OPTIMIZATION PROBLEM")
    print("=" * 80)

    # Verificar qué modelos están disponibles
    print("Verificando modelos disponibles en Ollama...")
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            available_models = [m["name"] for m in response.json().get("models", [])]
            print(f"Modelos disponibles: {available_models}")
        else:
            print("No se pudo obtener lista de modelos")
            return
    except:
        print("Error conectando a Ollama")
        return

    results = {}

    # Probar cada modelo
    for model_name in MODELS_TO_TEST:
        if any(model_name in avail for avail in available_models):
            results[model_name] = test_model(model_name)
        else:
            print(f"\n⚠️  {model_name} no está disponible - descargando...")
            # Intentar descargar el modelo
            try:
                download_response = requests.post(
                    "http://localhost:11434/api/pull",
                    json={"name": model_name},
                    timeout=1800,  # 30 minutos
                )
                if download_response.status_code == 200:
                    print(f"✅ {model_name} descargado, probando...")
                    results[model_name] = test_model(model_name)
                else:
                    print(f"❌ Error descargando {model_name}")
            except:
                print(f"❌ No se pudo descargar {model_name}")

    # Resumen final
    print(f"\n{'='*80}")
    print("📋 RESUMEN DE RESULTADOS")
    print(f"{'='*80}")

    for model_name, result in results.items():
        if result:
            obj_len = len(result.get("objective_coefficients", []))
            const_len = len(result.get("constraints", []))
            print(f"{model_name:15} → {obj_len} vars, {const_len} restricciones")
        else:
            print(f"{model_name:15} → ❌ Falló")

    print(
        f"\n💡 Recomendación: Prueba el modelo que genere 9 variables y más restricciones"
    )


if __name__ == "__main__":
    main()
