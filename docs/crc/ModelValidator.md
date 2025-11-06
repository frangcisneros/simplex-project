# Tarjeta CRC: ModelValidator

### Clase: ModelValidator

**Responsabilidades:**

- Validar que los problemas extraídos sean matemáticamente correctos
- Verificar que el tipo de objetivo sea 'maximize' o 'minimize'
- Validar que todos los coeficientes sean numéricos
- Comprobar consistencia dimensional entre restricciones y variables
- Verificar que los operadores de restricciones sean válidos (<=, >=, =)
- Validar que los problemas no excedan límites configurables
- Generar lista detallada de errores de validación
- Verificar que los nombres de variables no tengan duplicados
- Detectar restricciones con todos los coeficientes en cero
- Validar formato y estructura de cada restricción

**Colaboradores:**

- `IModelValidator` - Interfaz base que implementa
- `OptimizationProblem` - Problema a validar

**Ubicación:** `simplex_solver/nlp/model_generator.py`

**Tipo:** Validador (Validator)
