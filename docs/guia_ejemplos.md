# Guía de Ejemplos del Simplex Solver

## Ejemplo 1: Problema de maximización simple

**Archivo: ejemplos/maximizar_basico.txt**

```
MAXIMIZE
3 5
SUBJECT TO
1 0 <= 4
0 2 <= 12
3 2 <= 18
```

**Problema:** Maximizar 3x₁ + 5x₂ sujeto a:

- x₁ ≤ 4
- 2x₂ ≤ 12
- 3x₁ + 2x₂ ≤ 18
- x₁, x₂ ≥ 0

**Solución:** x₁ = 2, x₂ = 6, valor óptimo = 36

## Ejemplo 2: Problema de minimización simple

**Archivo: ejemplos/minimizar_simple.txt**

```
MINIMIZE
1 2
SUBJECT TO
1 1 <= 3
2 1 <= 4
```

**Problema:** Minimizar x₁ + 2x₂ sujeto a:

- x₁ + x₂ ≤ 3
- 2x₁ + x₂ ≤ 4
- x₁, x₂ ≥ 0

**Solución:** x₁ = 0, x₂ = 3, valor óptimo = 6

## Ejemplo 3: Problema de minimización con 3 variables

**Archivo: ejemplos/minimizar_3variables.txt**

```
MINIMIZE
2 3 4
SUBJECT TO
1 1 1 <= 10
2 1 0 <= 15
0 1 2 <= 20
```

**Problema:** Minimizar 2x₁ + 3x₂ + 4x₃ sujeto a:

- x₁ + x₂ + x₃ ≤ 10
- 2x₁ + x₂ ≤ 15
- x₂ + 2x₃ ≤ 20
- x₁, x₂, x₃ ≥ 0

## Ejemplo 4: Problema de producción

**Problema:** Una fábrica produce dos productos A y B.

- Producto A da una ganancia de $40 por unidad
- Producto B da una ganancia de $30 por unidad
- Restricciones de recursos:
  - Tiempo de máquina: 2A + 1B ≤ 100 horas
  - Materia prima: 1A + 1B ≤ 80 kg
  - Mano de obra: 1A + 2B ≤ 120 horas

**Archivo: ejemplos/problema_produccion.txt**

```
MAXIMIZE
40 30
SUBJECT TO
2 1 <= 100
1 1 <= 80
1 2 <= 120
```

## Uso en modo interactivo

Para usar el modo interactivo, ejecuta:

```bash
python simplex_solver.py --interactive
```

El programa te guiará paso a paso para ingresar:

1. Si quieres maximizar o minimizar
2. Los coeficientes de la función objetivo
3. Las restricciones una por una
4. Escribir 'fin' cuando termines

## Interpretación de resultados

El programa muestra:

- **Tableau inicial:** La tabla simplex al comenzar
- **Iteraciones:** Cada paso del algoritmo simplex
- **Variable que entra/sale:** Las variables que entran y salen de la base
- **Elemento pivote:** El elemento usado para las operaciones de pivoteo
- **Solución óptima:** Los valores de las variables y el valor objetivo óptimo

## Limitaciones actuales

- Solo soporta restricciones del tipo ≤ (menor o igual)
- Las variables deben ser no negativas (xi ≥ 0)
- No maneja casos degenerados o múltiples soluciones óptimas

## Próximas mejoras

- Soporte para restricciones de igualdad (=) y mayor o igual (≥)
- Método de dos fases para problemas sin solución factible inicial
- Detección de soluciones múltiples
- Análisis de sensibilidad
- Integración con IA para procesar enunciados en lenguaje natural
