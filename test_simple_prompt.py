"""
Test simple del prompt mejorado sin importar todo el sistema NLP
"""

import requests
import json

# Leer el problema complejo
with open("ejemplos/nlp/problema_complejo.txt", "r", encoding="utf-8") as f:
    problem_text = f.read()

# Prompt mejorado (copiado desde config.py)
PROMPT = f"""Eres un experto en programación lineal. Analiza este problema y extrae ÚNICAMENTE un JSON válido con la estructura de optimización.

PROBLEMA:
{problem_text}

INSTRUCCIONES:

1. VARIABLES:
   - Usa nomenclatura xij donde i=planta (1,2,3) y j=tamaño (1=grande,2=mediano,3=chico)
   - Orden: [x11,x12,x13,x21,x22,x23,x31,x32,x33]

2. TIPO DE PROBLEMA:
   - "maximize" para maximizar ganancias
   - "minimize" para minimizar costos

3. FUNCIÓN OBJETIVO:
   - Lista de 9 coeficientes (uno por variable)
   - Orden debe coincidir con variable_names
   - Ejemplo: [420,360,300,420,360,300,420,360,300]

4. RESTRICCIONES (EXACTAMENTE 9 - NO MENOS):
   
   CAPACIDAD (3 restricciones obligatorias):
   R1: [1,1,1,0,0,0,0,0,0] <= capacidad_planta1
   R2: [0,0,0,1,1,1,0,0,0] <= capacidad_planta2  
   R3: [0,0,0,0,0,0,1,1,1] <= capacidad_planta3
   
   ESPACIO (3 restricciones obligatorias):
   R4: [20,15,12,0,0,0,0,0,0] <= espacio_planta1
   R5: [0,0,0,20,15,12,0,0,0] <= espacio_planta2
   R6: [0,0,0,0,0,0,20,15,12] <= espacio_planta3
   
   DEMANDA (3 restricciones obligatorias):
   R7: [1,0,0,1,0,0,1,0,0] <= demanda_grande
   R8: [0,1,0,0,1,0,0,1,0] <= demanda_mediana  
   R9: [0,0,1,0,0,1,0,0,1] <= demanda_chica

   DEBES GENERAR EXACTAMENTE ESTAS 9 RESTRICCIONES CON ESTOS COEFICIENTES.

5. REGLAS:
   - TODAS las listas de coeficientes deben tener exactamente 9 elementos.
   - GENERA las 9 restricciones completas, no solo algunas.
   - Usa coeficientes [1,1,1,0,0,0,0,0,0] para capacidad de planta 1.
   - Usa coeficientes [0,0,0,1,1,1,0,0,0] para capacidad de planta 2.
   - NO agregues explicaciones, solo el JSON final.

------------------------------------------------------------
FORMATO DE SALIDA (solo JSON, nada más):

{{
  "objective_type": "maximize",
  "variable_names": ["x11","x12","x13","x21","x22","x23","x31","x32","x33"],
  "objective_coefficients": [420,360,300,420,360,300,420,360,300],
  "constraints": [
    {{"coefficients": [1,1,1,0,0,0,0,0,0], "operator": "<=", "rhs": 750}},
    {{"coefficients": [20,15,12,0,0,0,0,0,0], "operator": "<=", "rhs": 13000}}
  ],
  "non_negativity": true
}}
------------------------------------------------------------

IMPORTANTE:
- La salida debe ser un JSON válido.
- No incluyas comentarios, texto ni explicaciones antes o después del JSON.
- No resuelvas el problema ni calcules valores óptimos.
- Mantén coherencia en el orden de las variables y sus coeficientes.

JSON:"""


def test_ollama_model(model_name):
    """Prueba el modelo con el prompt mejorado"""
    print(f"🧠 PROBANDO DIRECTAMENTE CON {model_name.upper()}")
    print("=" * 80)

    try:
        print(f"⏳ Generando respuesta con {model_name}...")

        data = {"model": model_name, "prompt": PROMPT, "stream": False}

        response = requests.post(
            "http://localhost:11434/api/generate", json=data, timeout=60
        )

        if response.status_code == 200:
            result = response.json()
            response_text = result.get("response", "")

            print("📄 RESPUESTA COMPLETA:")
            print("=" * 80)
            print(response_text)
            print("=" * 80)

            # Intentar parsear JSON
            try:
                # Buscar el JSON en la respuesta
                start = response_text.find("{")
                end = response_text.rfind("}") + 1

                if start >= 0 and end > start:
                    json_str = response_text[start:end]
                    parsed_json = json.loads(json_str)

                    print("\n📊 JSON PARSEADO:")
                    print("=" * 80)
                    print(json.dumps(parsed_json, indent=2))
                    print("=" * 80)

                    # Análisis de restricciones
                    constraints = parsed_json.get("constraints", [])
                    print(f"\n🔍 ANÁLISIS:")
                    print(f"Variables: {len(parsed_json.get('variable_names', []))}")
                    print(
                        f"Coeficientes objetivo: {len(parsed_json.get('objective_coefficients', []))}"
                    )
                    print(f"Restricciones generadas: {len(constraints)}")

                    for i, constraint in enumerate(constraints):
                        coeffs = constraint.get("coefficients", [])
                        operator = constraint.get("operator", "")
                        rhs = constraint.get("rhs", "")
                        print(f"  R{i+1}: {len(coeffs)} coefs, {operator} {rhs}")

                    if len(constraints) == 9:
                        print(
                            "✅ ¡PERFECTO! Se generaron las 9 restricciones necesarias"
                        )
                    else:
                        print(
                            f"⚠️ Faltan restricciones. Esperado: 9, Generado: {len(constraints)}"
                        )

            except json.JSONDecodeError as e:
                print(f"❌ Error parseando JSON: {e}")
        else:
            print(f"❌ Error en la API: {response.status_code}")

    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    test_ollama_model("llama3.1:8b")
