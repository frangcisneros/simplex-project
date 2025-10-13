"""
Configuración de los modelos de lenguaje y constantes del sistema NLP.

Define qué modelos podemos usar, cómo configurarlos, los prompts para extraer
información, y los mensajes de error estándar.
"""

from enum import Enum
from typing import Dict, Any


class NLPModelType(Enum):
    """
    Modelos disponibles para procesamiento de problemas de optimización.

    Diferentes modelos pueden tener distintas capacidades para analizar
    problemas matemáticos complejos y generar estructuras JSON correctas.
    """

    MISTRAL_7B = "mistral:7b"  # Modelo predeterminado
    LLAMA3_1_8B = "llama3.1:8b"  # Mejor razonamiento matemático
    QWEN2_5_14B = "qwen2.5:14b"  # Especializado en matemáticas
    LLAMA3_2_3B = "llama3.2:3b"  # Ligero pero capaz


class ModelConfig:
    """
    Configuración optimizada para Mistral 7B.

    Parámetros ajustados específicamente para generar JSON estructurado
    de problemas de optimización lineal de forma determinística.
    """

    DEFAULT_CONFIGS: Dict[NLPModelType, Dict[str, Any]] = {
        NLPModelType.MISTRAL_7B: {
            "temperature": 0.0,  # Determinístico para JSON
            "max_tokens": 1024,
            "top_p": 0.8,
        },
        NLPModelType.LLAMA3_1_8B: {
            "temperature": 0.1,  # Ligeramente creativo para problemas complejos
            "max_tokens": 2048,  # Más espacio para análisis completo
            "top_p": 0.95,
        },
        NLPModelType.QWEN2_5_14B: {
            "temperature": 0.0,  # Determinístico para JSON
            "max_tokens": 2048,  # Máximo espacio para análisis complejo
            "top_p": 0.9,
        },
        NLPModelType.LLAMA3_2_3B: {
            "temperature": 0.0,  # Determinístico para JSON
            "max_tokens": 1024,
            "top_p": 0.8,
        },
    }


class PromptTemplates:
    """
    Prompts que le pedimos al modelo de lenguaje para extraer información.

    Estos prompts instruyen al modelo sobre cómo convertir el texto en español
    a un JSON estructurado con el problema de optimización.

    Utiliza técnica de few-shot learning con ejemplos concretos para mejorar
    la capacidad del modelo de identificar variables y restricciones en
    problemas complejos.
    """

    OPTIMIZATION_EXTRACTION_PROMPT = """Eres un analista experto en Programación Lineal. 
Tu tarea es LEER un enunciado en español y extraer su información estructurada
en formato JSON. NO resuelvas el problema.

🚨 REGLA CRÍTICA ABSOLUTA 🚨
SI EL PROBLEMA MENCIONA "N PLANTAS" Y "M PRODUCTOS/TAMAÑOS":
→ DEBES crear EXACTAMENTE N × M variables con nombres xij
→ Donde i = número de planta (1, 2, 3...)
→ Y j = número de producto/tamaño (1, 2, 3...)
→ EJEMPLO: 3 plantas × 3 tamaños = 9 variables OBLIGATORIAS
   ["x11", "x12", "x13", "x21", "x22", "x23", "x31", "x32", "x33"]

Instrucciones generales:
- Lee cuidadosamente el texto.
- Identifica el tipo de problema (maximizar o minimizar).
- Determina las variables de decisión, sus índices y significado.
- Extrae los coeficientes numéricos (ganancias, recursos, demandas, etc.).
- Organiza todo en un JSON válido (sin texto adicional).

------------------------------------------------------------
EJEMPLOS DE APRENDIZAJE (Few-Shot):

EJEMPLO 1 - Problema Simple (un lugar, múltiples productos):
ENUNCIADO: "Una empresa fabrica mesas y sillas. Cada mesa genera $50 de ganancia y cada silla $30. 
Hay 100 horas de carpintería disponibles. Cada mesa requiere 4 horas y cada silla 2 horas. 
Maximizar la ganancia."

RESPUESTA CORRECTA:
{{
  "objective_type": "maximize",
  "variable_names": ["x1", "x2"],
  "objective_coefficients": [50, 30],
  "constraints": [
    {{"coefficients": [4, 2], "operator": "<=", "rhs": 100}}
  ],
  "non_negativity": true
}}

EJEMPLO 2 - Problema Multi-Instalación (2 plantas, 3 productos):
ENUNCIADO: "Una empresa tiene 2 plantas. Planta 1 puede producir max 500 unidades, Planta 2 max 700 unidades. 
Producen 3 productos: A, B, C con ganancias de $10, $15, $20 por unidad respectivamente (igual en ambas plantas). 
Hay demanda máxima: producto A 300 unidades, B 400 unidades, C 600 unidades. Maximizar ganancia."

ANÁLISIS: 2 plantas × 3 productos = 6 variables
- xij donde i=producto (1=A,2=B,3=C), j=planta (1 o 2)
- La ganancia es IGUAL para cada producto sin importar la planta
- Por tanto: [10,15,20] se REPITE para cada planta → [10,15,20, 10,15,20]

RESPUESTA CORRECTA:
{{
  "objective_type": "maximize",
  "variable_names": ["x11", "x12", "x13", "x21", "x22", "x23"],
  "objective_coefficients": [10, 15, 20, 10, 15, 20],
  "constraints": [
    {{"coefficients": [1, 1, 1, 0, 0, 0], "operator": "<=", "rhs": 500}},
    {{"coefficients": [0, 0, 0, 1, 1, 1], "operator": "<=", "rhs": 700}},
    {{"coefficients": [1, 0, 0, 1, 0, 0], "operator": "<=", "rhs": 300}},
    {{"coefficients": [0, 1, 0, 0, 1, 0], "operator": "<=", "rhs": 400}},
    {{"coefficients": [0, 0, 1, 0, 0, 1], "operator": "<=", "rhs": 600}}
  ],
  "non_negativity": true
}}

EJEMPLO 2B - Problema Multi-Instalación (3 plantas, 2 productos):
ENUNCIADO: "Una fábrica tiene 3 plantas que producen productos tipo X e Y. 
La ganancia por X es $80 y por Y es $60 (igual en todas las plantas).
Capacidades: Planta 1 max 400 unidades, Planta 2 max 600 unidades, Planta 3 max 300 unidades.
Demandas: producto X max 800, producto Y max 500. Maximizar ganancia."

ANÁLISIS: 3 plantas × 2 productos = 6 variables
- xij donde i=planta (1,2,3), j=producto (1=X, 2=Y)
- Ganancia [80,60] se REPITE para cada planta → [80,60, 80,60, 80,60]

RESPUESTA CORRECTA:
{{
  "objective_type": "maximize",
  "variable_names": ["x11", "x12", "x21", "x22", "x31", "x32"],
  "objective_coefficients": [80, 60, 80, 60, 80, 60],
  "constraints": [
    {{"coefficients": [1, 1, 0, 0, 0, 0], "operator": "<=", "rhs": 400}},
    {{"coefficients": [0, 0, 1, 1, 0, 0], "operator": "<=", "rhs": 600}},
    {{"coefficients": [0, 0, 0, 0, 1, 1], "operator": "<=", "rhs": 300}},
    {{"coefficients": [1, 0, 1, 0, 1, 0], "operator": "<=", "rhs": 800}},
    {{"coefficients": [0, 1, 0, 1, 0, 1], "operator": "<=", "rhs": 500}}
  ],
  "non_negativity": true
}}

EJEMPLO 2C - Problema Multi-Instalación (3 plantas, 3 productos):
ENUNCIADO: "Una compañía tiene 3 plantas que fabrican 3 tamaños: grande, mediano, chico con ganancias de $420, $360, $300.
Capacidades: Planta 1 max 750 unidades, Planta 2 max 900 unidades, Planta 3 max 450 unidades (sin importar tamaño).
Demandas: grande max 900, mediano max 1200, chico max 750 unidades totales. Maximizar ganancia."

ANÁLISIS: 3 plantas × 3 productos = 9 variables
- xij donde i=planta (1,2,3), j=tamaño (1=grande, 2=mediano, 3=chico)
- Ganancia [420,360,300] se REPITE para cada planta → [420,360,300, 420,360,300, 420,360,300]

🚨 IMPORTANTE: TODAS las restricciones tienen 9 coeficientes (uno por cada variable)
- Capacidad planta 1: [1,1,1, 0,0,0, 0,0,0] ← suma x11+x12+x13
- Capacidad planta 2: [0,0,0, 1,1,1, 0,0,0] ← suma x21+x22+x23
- Capacidad planta 3: [0,0,0, 0,0,0, 1,1,1] ← suma x31+x32+x33
- Demanda grande: [1,0,0, 1,0,0, 1,0,0] ← suma x11+x21+x31
- Demanda mediano: [0,1,0, 0,1,0, 0,1,0] ← suma x12+x22+x32
- Demanda chico: [0,0,1, 0,0,1, 0,0,1] ← suma x13+x23+x33

RESPUESTA CORRECTA:
{{
  "objective_type": "maximize",
  "variable_names": ["x11", "x12", "x13", "x21", "x22", "x23", "x31", "x32", "x33"],
  "objective_coefficients": [420, 360, 300, 420, 360, 300, 420, 360, 300],
  "constraints": [
    {{"coefficients": [1, 1, 1, 0, 0, 0, 0, 0, 0], "operator": "<=", "rhs": 750}},
    {{"coefficients": [0, 0, 0, 1, 1, 1, 0, 0, 0], "operator": "<=", "rhs": 900}},
    {{"coefficients": [0, 0, 0, 0, 0, 0, 1, 1, 1], "operator": "<=", "rhs": 450}},
    {{"coefficients": [1, 0, 0, 1, 0, 0, 1, 0, 0], "operator": "<=", "rhs": 900}},
    {{"coefficients": [0, 1, 0, 0, 1, 0, 0, 1, 0], "operator": "<=", "rhs": 1200}},
    {{"coefficients": [0, 0, 1, 0, 0, 1, 0, 0, 1], "operator": "<=", "rhs": 750}}
  ],
  "non_negativity": true
}}

EJEMPLO 3 - Problema de Mezclas Simple (materiales que se venden o mezclan):
ENUNCIADO: "Una refinería tiene 1000 barriles de petróleo crudo tipo 1 y 1500 de tipo 2. 
Puede venderlos directamente a $40 y $35 por barril respectivamente, o mezclarlos en gasolina premium 
(70% tipo1 + 30% tipo2) que se vende a $50 por barril. Maximizar ingresos."

ANÁLISIS: Decisiones simples - venta directa o en mezcla
- x1: barriles de tipo1 vendidos directamente
- x2: barriles de tipo2 vendidos directamente
- x3: barriles de mezcla premium producidos

RESPUESTA CORRECTA:
{{
  "objective_type": "maximize",
  "variable_names": ["x1", "x2", "x3"],
  "objective_coefficients": [40, 35, 50],
  "constraints": [
    {{"coefficients": [1, 0, 0.7], "operator": "<=", "rhs": 1000}},
    {{"coefficients": [0, 1, 0.3], "operator": "<=", "rhs": 1500}}
  ],
  "non_negativity": true
}}

EJEMPLO 4 - Problema de Mezclas Complejo (4 materias primas, 2 mezclas finales):
ENUNCIADO: "Una refinería tiene 4 gasolinas base (G1, G2, G3, G4) con producciones de 100, 150, 200, 120 barriles.
Puede venderlas directamente a $20, $22, $18, $25 por barril respectivamente.
También puede mezclarlas para crear 2 productos premium:
- Premium A (utilidad $30/barril): puede contener G1, G2, G3, G4 en cualquier proporción
- Premium B (utilidad $28/barril): puede contener G1, G2, G3, G4 en cualquier proporción
Maximizar retornos."

ANÁLISIS: Problema complejo de mezclas con 4 materiales y 2 mezclas
- 4 variables para venta directa: x1, x2, x3, x4 (cuánto vender de cada gasolina)
- 2 variables para totales de mezclas: xA, xB (cuánto producir de Premium A y Premium B)
- 8 variables para componentes: xG1A, xG2A, xG3A, xG4A (gases en Premium A), xG1B, xG2B, xG3B, xG4B (gases en Premium B)
- Total: 4 + 2 + 8 = 14 variables

RESPUESTA CORRECTA:
{{
  "objective_type": "maximize",
  "variable_names": ["x1", "x2", "x3", "x4", "xA", "xB", "xG1A", "xG2A", "xG3A", "xG4A", "xG1B", "xG2B", "xG3B", "xG4B"],
  "objective_coefficients": [20, 22, 18, 25, 30, 28, 0, 0, 0, 0, 0, 0, 0, 0],
  "constraints": [
    {{"coefficients": [0, 0, 0, 0, 1, 0, -1, -1, -1, -1, 0, 0, 0, 0], "operator": "=", "rhs": 0}},
    {{"coefficients": [0, 0, 0, 0, 0, 1, 0, 0, 0, 0, -1, -1, -1, -1], "operator": "=", "rhs": 0}},
    {{"coefficients": [1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0], "operator": "<=", "rhs": 100}},
    {{"coefficients": [0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0], "operator": "<=", "rhs": 150}},
    {{"coefficients": [0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0], "operator": "<=", "rhs": 200}},
    {{"coefficients": [0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1], "operator": "<=", "rhs": 120}}
  ],
  "non_negativity": true
}}

------------------------------------------------------------
AHORA ANALIZA EL SIGUIENTE PROBLEMA:

ENUNCIADO:
{problem_text}
------------------------------------------------------------

PASOS DE ANÁLISIS:

1. DETERMINA EL TIPO DE PROBLEMA:
   - Si menciona "maximizar", "ganancia", "beneficio" → "maximize"
   - Si menciona "minimizar", "costo", "gasto" → "minimize"
   
   REFERENCIA: Todos los ejemplos anteriores son de maximización.

2. DEFINE LAS VARIABLES - IDENTIFICA QUÉ OPTIMIZAR:
   
   DETECCIÓN DE ESTRUCTURA (ver ejemplos above):
   
   A) PROBLEMA SIMPLE - Un solo lugar, varios productos:
     → Variables simples: ["x1", "x2", "x3"]
     → VER EJEMPLO 1: 2 productos = 2 variables ["x1", "x2"]
   
   B) PROBLEMA MULTI-INSTALACIÓN - Varias plantas, múltiples productos:
     → Usa xij donde i=planta, j=producto/tamaño
     → FÓRMULA: N_plantas × M_productos = Total de variables
     → VER EJEMPLO 2: 2 plantas × 3 productos = 6 variables ["x11","x12","x13","x21","x22","x23"]
     → VER EJEMPLO 2B: 3 plantas × 2 productos = 6 variables ["x11","x12","x21","x22","x31","x32"]
     → VER EJEMPLO 2C: 3 plantas × 3 productos = 9 variables 
       ["x11","x12","x13","x21","x22","x23","x31","x32","x33"]
   
   C) PROBLEMA DE MEZCLAS SIMPLES - Materias primas que se venden O mezclan:
     → VER EJEMPLO 3: 2 materias + 1 mezcla = 3 variables ["x1","x2","x3"]
   
   D) PROBLEMA DE MEZCLAS COMPLEJAS - Múltiples materias, múltiples mezclas:
     → ESTRUCTURA: ventas directas + totales de mezclas + componentes de cada mezcla
     → VER EJEMPLO 4: 4 materias (gasolinas), 2 mezclas (premium A y B)
       • 4 variables de venta directa (x1, x2, x3, x4)
       • 2 variables de totales de mezclas (xA, xB)
       • 8 variables de componentes (xG1A-xG4A para Premium A, xG1B-xG4B para Premium B)
       • Total: 4 + 2 + 8 = 14 variables
     → REGLA: N_materias + N_mezclas + (N_materias × N_mezclas) variables
     → EJEMPLO: 4 materias + 2 mezclas + (4×2) = 4 + 2 + 8 = 14 vars
   
   REGLA CRÍTICA: Identifica el TIPO de problema primero, luego cuenta variables según su estructura.

3. FUNCIÓN OBJETIVO - EXTRAE LOS COEFICIENTES:
   - Busca valores EXACTOS de ganancia/utilidad (para maximizar) o costo (para minimizar)
   - USA SOLO números que aparecen explícitamente en el problema
   - NO hagas operaciones matemáticas (NO escribas 24.83*3814)
   
   REGLA CRÍTICA PARA MULTI-INSTALACIÓN:
   - Si la ganancia/costo es IGUAL para todas las plantas:
     → REPITE el valor para CADA planta
   - La cantidad de coeficientes DEBE ser IGUAL a la cantidad de variables
   
   REFERENCIA EJEMPLOS:
   - Ejemplo 1: mesas $50, sillas $30 → [50, 30] (2 coeficientes, 2 variables)
   - Ejemplo 2: productos A,B,C = $10,$15,$20 en AMBAS plantas 
     → [10,15,20, 10,15,20] (6 coeficientes, 6 variables)
   - Ejemplo 2B: productos X,Y = $80,$60 en TRES plantas
     → [80,60, 80,60, 80,60] (6 coeficientes, 6 variables)
   - Ejemplo 2C: grande/mediano/chico = $420,$360,$300 en TRES plantas
     → [420,360,300, 420,360,300, 420,360,300] (9 coeficientes, 9 variables)
   - Ejemplo 3: venta directa $40,$35 + mezcla $50 
     → [40,35,50] (3 coeficientes, 3 variables)
   - Ejemplo 4: 4 gasolinas vendidas directamente ($20,$22,$18,$25) + 2 premiums ($30,$28) + componentes (0s)
     → [20,22,18,25, 30,28, 0,0,0,0,0,0,0,0] (14 coeficientes, 14 variables)
   
   VERIFICACIÓN: len(objective_coefficients) == len(variable_names)

4. RESTRICCIONES - IDENTIFICA LOS LÍMITES:

   APRENDE DE LOS EJEMPLOS:
   
   EJEMPLO 1 - Recurso compartido simple:
   - Carpintería: 4h × mesas + 2h × sillas ≤ 100h
   - Coeficientes: [4, 2] ≤ 100
   
   EJEMPLO 2 - Capacidad + Demanda en multi-instalación:
   - Capacidad planta 1: x11+x12+x13 ≤ 500 → [1,1,1,0,0,0] ≤ 500
   - Capacidad planta 2: x21+x22+x23 ≤ 700 → [0,0,0,1,1,1] ≤ 700
   - Demanda producto A: x11+x21 ≤ 300 → [1,0,0,1,0,0] ≤ 300
   
   EJEMPLO 3 - Disponibilidad de materiales con mezclas:
   - Tipo 1: venta_directa + 70% mezcla ≤ 1000 → [1,0,0.7] ≤ 1000
   - Tipo 2: venta_directa + 30% mezcla ≤ 1500 → [0,1,0.3] ≤ 1500
   
   PATRONES COMUNES A IDENTIFICAR:
   
   A) CAPACIDAD POR INSTALACIÓN:
   - Si planta 1 puede hacer max 750 unidades: [1,1,1,0,0,0] <= 750
   - Si planta 2 puede hacer max 900 unidades: [0,0,0,1,1,1] <= 900
   
   B) RECURSOS POR TIPO:
   - Si producto grande usa 20 unidades de recurso: [20,0,0,20,0,0] <= total_recurso
   - Si producto mediano usa 15 unidades: [0,15,0,0,15,0] <= total_recurso
   
   C) DEMANDA MÁXIMA:
   - Si demanda de producto 1 es 500: [1,0,0,1,0,0] <= 500 (suma todas plantas)
   
   D) DISPONIBILIDAD DE MATERIALES:
   - Si hay 3814 barriles de gas1 disponibles: [1,0,0,0,coef_mezcla1,coef_mezcla2] <= 3814
   
   IDENTIFICA estos patrones en TU problema específico comparando con los ejemplos.

5. REGLAS CRÍTICAS:
   - CADA array "coefficients" DEBE tener EXACTAMENTE el mismo número de elementos que "variable_names"
   - Si una variable no participa en una restricción, usa 0 en esa posición
   - Ejemplo: 6 variables → cada coefficients debe tener [a,b,c,d,e,f] (6 números)
   - VERIFICA que cada restricción tenga la longitud correcta antes de incluirla
   - NO agregues explicaciones, solo el JSON final.
   - COMPARA tu análisis con los ejemplos few-shot antes de generar el JSON.

------------------------------------------------------------
FORMATO DE SALIDA (solo JSON, nada más):

{{
  "objective_type": "maximize",
  "variable_names": ["x1", "x2", "x3"],
  "objective_coefficients": [coef1, coef2, coef3],
  "constraints": [
    {{"coefficients": [a1, b1, c1], "operator": "<=", "rhs": limite1}},
    {{"coefficients": [a2, b2, c2], "operator": ">=", "rhs": limite2}}
  ],
  "non_negativity": true
}}

NOTA: Si tienes N variables, cada coefficients debe tener exactamente N números.
------------------------------------------------------------

🚨 VALIDACIÓN FINAL ANTES DE GENERAR JSON:

1. Cuenta tus variables: N = len(variable_names)

2. Verifica función objetivo:
   ✓ len(objective_coefficients) == N

3. Verifica CADA restricción:
   ✓ Para cada constraint: len(coefficients) == N
   ✓ Si una variable no participa, pon 0 en su posición
   
4. Ejemplo de validación:
   - Si tienes 9 variables: ["x11","x12","x13","x21","x22","x23","x31","x32","x33"]
   - objective_coefficients debe tener 9 números: [420,360,300,420,360,300,420,360,300]
   - CADA constraint debe tener 9 coeficientes: [1,1,1,0,0,0,0,0,0] o [1,0,0,1,0,0,1,0,0]
   
5. Si no pasas esta validación, RECONTRUYE tu JSON

------------------------------------------------------------

CRÍTICO - REGLAS DE SALIDA:
- SOLO devuelve el JSON, SIN explicaciones, SIN texto adicional
- NO uses comas en números: usa 13000, NO 13,000
- NO hagas cálculos, usa valores exactos del problema
- NO agregues comentarios ni markdown (```json)
- La primera línea debe ser {{ y la última }}

JSON (SOLO ESTO):"""

    VALIDATION_PROMPT = """
Valida si el siguiente problema de optimización está bien formado y es resolvible:

{problem_json}

Responde "VALID" si es válido o lista los errores encontrados.
"""


class ErrorMessages:
    """
    Mensajes de error claros para cuando algo falla en el pipeline.

    Estos mensajes ayudan a identificar en qué parte del proceso ocurrió el problema.
    """

    MODEL_NOT_AVAILABLE = "El modelo NLP no está disponible o no se pudo cargar"
    INVALID_JSON_RESPONSE = "El modelo NLP no generó un JSON válido"
    MALFORMED_PROBLEM = "El problema extraído está mal formado"
    NO_OBJECTIVE = "No se pudo extraer la función objetivo"
    NO_CONSTRAINTS = "No se encontraron restricciones válidas"
    DIMENSION_MISMATCH = "Las dimensiones de coeficientes no coinciden"
    SOLVER_ERROR = "Error en el solver de optimización"
    TIMEOUT_ERROR = "Timeout en el procesamiento NLP"


class DefaultSettings:
    """
    Configuración por defecto del sistema NLP.

    Permite probar diferentes modelos para encontrar el que mejor
    analiza problemas de optimización complejos.
    """

    DEFAULT_MODEL = NLPModelType.LLAMA3_1_8B  # Mejor modelo para problemas complejos
    MAX_PROCESSING_TIME = 60.0  # Mayor tiempo para problemas complejos
    MIN_CONFIDENCE_SCORE = 0.7  # Umbral de confianza estándar
    MAX_VARIABLES = 50  # Soporte para problemas grandes
    MAX_CONSTRAINTS = 100  # Más restricciones permitidas
    CACHE_SIZE = 50  # Cache moderado
