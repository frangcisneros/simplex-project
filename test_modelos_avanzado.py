"""
Script para probar diferentes modelos de Ollama con el problema complejo.
Compara qué modelo genera mejor la estructura de restricciones.
"""

import requests
import json
import sys
import os
from time import time

# Agregar src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from nlp.config import PromptTemplates, NLPModelType

# Leer el problema complejo
with open("ejemplos/nlp/problema_complejo.txt", "r", encoding="utf-8") as f:
    problem_text = f.read()

# Modelos a probar
MODELS_TO_TEST = [
    NLPModelType.MISTRAL_7B,
    NLPModelType.LLAMA3_1_8B,
    NLPModelType.QWEN2_5_14B,
    NLPModelType.LLAMA3_2_3B,
]


def check_model_availability(model_name):
    """Verifica si un modelo está disponible en Ollama."""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get("models", [])
            return any(model_name in model.get("name", "") for model in models)
    except:
        return False
    return False


def test_model(model_type):
    """Prueba un modelo específico con el problema complejo."""
    model_name = model_type.value

    print(f"\n{'='*80}")
    print(f"🧠 PROBANDO MODELO: {model_name}")
    print(f"{'='*80}")

    # Verificar disponibilidad
    if not check_model_availability(model_name):
        print(
            f"❌ Modelo {model_name} no disponible. Ejecuta: ollama pull {model_name}"
        )
        return None

    # Generar el prompt
    prompt = PromptTemplates.OPTIMIZATION_EXTRACTION_PROMPT.format(
        problem_text=problem_text
    )

    # Configurar petición
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
        print("⏳ Generando respuesta...")
        start_time = time()

        response = requests.post(
            "http://localhost:11434/api/generate", json=request_data, timeout=120
        )

        elapsed_time = time() - start_time

        if response.status_code != 200:
            print(f"❌ Error HTTP: {response.status_code}")
            return None

        response_data = response.json()
        generated_text = response_data.get("response", "").strip()

        print(f"✅ Respuesta generada en {elapsed_time:.1f}s")

        # Intentar parsear JSON
        import re

        json_match = re.search(r"\{.*\}", generated_text, re.DOTALL)
        if not json_match:
            print("❌ No se encontró JSON válido")
            return None

        json_text = json_match.group()
        data = json.loads(json_text)

        # Analizar la respuesta
        print("\\n📊 ANÁLISIS DE LA RESPUESTA:")
        print("-" * 50)

        obj_coeffs = data.get("objective_coefficients", [])
        constraints = data.get("constraints", [])
        var_names = data.get("variable_names", [])
        objective_type = data.get("objective_type", "")

        print(f"Tipo objetivo: {objective_type}")
        print(f"Variables: {len(var_names)} -> {var_names}")
        print(f"Coef. objetivo: {len(obj_coeffs)} -> {obj_coeffs}")
        print(f"Restricciones: {len(constraints)}")

        # Verificar dimensiones
        dimension_ok = True
        expected_vars = len(obj_coeffs)

        for i, constraint in enumerate(constraints):
            coeffs = constraint.get("coefficients", [])
            op = constraint.get("operator", "")
            rhs = constraint.get("rhs", 0)
            print(f"  R{i+1}: {len(coeffs)} coef -> {coeffs} {op} {rhs}")

            if len(coeffs) != expected_vars:
                dimension_ok = False

        # Evaluar calidad
        print("\\n🔍 EVALUACIÓN:")
        print("-" * 30)

        score = 0
        issues = []

        # ¿Variables correctas?
        if len(var_names) == 9 and len(obj_coeffs) == 9:
            score += 3
            print("✅ Dimensiones correctas (9 variables)")
        else:
            issues.append(
                f"Dimensiones incorrectas: {len(var_names)} vars, {len(obj_coeffs)} coef"
            )

        # ¿Coeficientes objetivo correctos?
        expected_obj = [420, 360, 300, 420, 360, 300, 420, 360, 300]
        if obj_coeffs == expected_obj:
            score += 3
            print("✅ Función objetivo perfecta")
        elif len(obj_coeffs) == 9:
            score += 1
            print("⚠️ 9 coeficientes pero valores incorrectos")
        else:
            issues.append("Función objetivo incorrecta")

        # ¿Restricciones dimensionalmente correctas?
        if dimension_ok:
            score += 2
            print("✅ Restricciones dimensionalmente consistentes")
        else:
            issues.append("Restricciones con dimensiones incorrectas")

        # ¿Suficientes restricciones?
        if len(constraints) >= 6:  # Al menos capacidad + espacio para plantas
            score += 1
            print("✅ Número razonable de restricciones")
        else:
            issues.append("Muy pocas restricciones")

        # ¿Tipo objetivo correcto?
        if objective_type.lower() in ["maximize", "max"]:
            score += 1
            print("✅ Tipo objetivo correcto")
        else:
            issues.append(f"Tipo objetivo incorrecto: {objective_type}")

        print(f"\\n🏆 PUNTUACIÓN: {score}/10")

        if issues:
            print("⚠️ PROBLEMAS DETECTADOS:")
            for issue in issues:
                print(f"   • {issue}")

        return {
            "model": model_name,
            "score": score,
            "time": elapsed_time,
            "variables": len(var_names),
            "obj_coefficients": len(obj_coeffs),
            "constraints": len(constraints),
            "dimension_ok": dimension_ok,
            "data": data,
        }

    except json.JSONDecodeError as e:
        print(f"❌ Error parseando JSON: {e}")
        return None
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return None


def main():
    print("🚀 PRUEBA DE MODELOS PARA PROBLEMA COMPLEJO")
    print("=" * 80)
    print("Evaluando qué modelo analiza mejor el problema de 3 plantas × 3 tamaños")

    results = []

    for model in MODELS_TO_TEST:
        result = test_model(model)
        if result:
            results.append(result)

    # Mostrar resumen
    if results:
        print(f"\\n\\n📈 RESUMEN DE RESULTADOS")
        print("=" * 80)

        # Ordenar por puntuación
        results.sort(key=lambda x: x["score"], reverse=True)

        print(
            f"{'Modelo':<15} {'Puntos':<8} {'Tiempo':<8} {'Variables':<10} {'Coef.Obj':<10} {'Restricc.':<10}"
        )
        print("-" * 70)

        for r in results:
            print(
                f"{r['model']:<15} {r['score']}/10    {r['time']:.1f}s     "
                f"{r['variables']:<10} {r['obj_coefficients']:<10} {r['constraints']:<10}"
            )

        # Mejor modelo
        best = results[0]
        print(f"\\n🏆 MEJOR MODELO: {best['model']} con {best['score']}/10 puntos")

        if best["score"] >= 8:
            print("🎉 ¡Excelente! Este modelo resuelve bien el problema.")
        elif best["score"] >= 6:
            print("⚠️ Aceptable, pero necesita mejoras en el prompt.")
        else:
            print("❌ Todos los modelos necesitan mejores instrucciones.")
    else:
        print(
            "❌ No se pudo probar ningún modelo. Verifica que Ollama esté ejecutándose."
        )


if __name__ == "__main__":
    main()
