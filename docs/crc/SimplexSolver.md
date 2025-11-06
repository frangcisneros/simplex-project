# Tarjeta CRC: SimplexSolver

### Clase: SimplexSolver

**Responsabilidades:**

- Implementar el algoritmo Simplex para resolver problemas de programación lineal
- Gestionar el proceso de resolución en dos fases (Fase 1 y Fase 2)
- Verificar condiciones de optimalidad en cada iteración
- Identificar variables que entran y salen de la base
- Detectar problemas no acotados (unbounded)
- Realizar operaciones de pivoteo en el tableau
- Mantener historial de pasos para generación de reportes
- Calcular la solución básica y valor óptimo
- Manejar problemas con variables artificiales
- Soportar diferentes niveles de verbosidad en logging

**Colaboradores:**

- `Tableau` - Maneja la estructura y operaciones del tableau simplex
- `LoggingSystem` - Registra eventos, iteraciones y errores del proceso
- `numpy` - Operaciones matriciales y numéricas

**Ubicación:** `simplex_solver/core/algorithm.py`

**Tipo:** Algoritmo núcleo (Core Algorithm)
