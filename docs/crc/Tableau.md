# Tarjeta CRC: Tableau

### Clase: Tableau

**Responsabilidades:**

- Manejar la estructura de datos del tableau simplex
- Construir el tableau inicial a partir de c, A, b y tipos de restricciones
- Normalizar restricciones con lado derecho negativo
- Gestionar variables de holgura, exceso y artificiales
- Configurar función objetivo para Fase 1 (minimizar artificiales)
- Configurar función objetivo para Fase 2 (objetivo original)
- Determinar si la solución actual es óptima
- Identificar la variable que entra a la base (ratio test)
- Identificar la variable que sale de la base
- Detectar problemas no acotados
- Ejecutar operaciones de pivoteo
- Extraer la solución básica actual
- Calcular el valor óptimo usando c^T x
- Limpiar columnas de variables artificiales en Fase 2
- Verificar presencia de variables artificiales en la base

**Colaboradores:**

- `SimplexSolver` - Consume las operaciones del tableau
- `numpy` - Operaciones matriciales

**Ubicación:** `simplex_solver/utils/tableau.py`

**Tipo:** Estructura de datos especializada (Data Structure)
