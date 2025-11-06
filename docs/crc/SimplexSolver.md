# SimplexSolver

**Clase:** SimplexSolver (Solucionador Simplex)

**Responsabilidades:**
- Gestionar el proceso de resolución con **Método de Dos Fases**:
  - **Fase 1**: Minimizar suma de variables artificiales para encontrar SBF
  - **Fase 2**: Resolver problema original con función objetivo dada
- Detectar problemas infactibles (cuando Fase 1 da w* > 0)
- Coordinar transición entre Fase 1 y Fase 2
- Ejecutar iteraciones del método simplex
- Detectar soluciones óptimas, no acotadas e infactibles
- Registrar pasos del algoritmo (logging)
- Validar consistencia del problema
- Gestionar la configuración del algoritmo

**Métodos Principales:**
- solve(): Punto de entrada principal (coordina Fase 1 y Fase 2)
- _solve_phase1(): Minimiza suma de variables artificiales
- _solve_phase2(): Resuelve problema original si Fase 1 fue exitosa
- _simplex_iteration(): Ejecuta una iteración del algoritmo simplex
- _get_solution(): Extrae la solución óptima del tableau final

**Colaboradores:**
- **Tableau**: Gestiona la tabla simplex y transformaciones (Fase 1 y Fase 2)
- **AlgorithmConfig**: Proporciona configuración (max_iterations, tolerancias)
- **SimplexResult**: Almacena resultados de la resolución

**Notas:**
- Implementa el **Método de Dos Fases** completo para manejar restricciones >=, ==, <=
- Ver documentación técnica en: docs/METODO_DOS_FASES.md
- Verbosity 2 muestra detalles de Fase 1 y transición a Fase 2
- Detecta infactibilidad cuando w* > tolerancia después de Fase 1
