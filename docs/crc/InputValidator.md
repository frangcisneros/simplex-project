# Tarjeta CRC: InputValidator

### Clase: InputValidator

**Responsabilidades:**

- Validar problemas de programación lineal completos
- Verificar que la función objetivo tenga al menos un coeficiente
- Validar que no todos los coeficientes objetivo sean cero
- Comprobar que haya al menos una restricción
- Validar consistencia dimensional (restricciones vs variables)
- Verificar que los coeficientes de restricciones sean numéricos
- Validar operadores de restricciones (<=, >=, =)
- Detectar restricciones con todos los coeficientes en cero
- Validar lado derecho de restricciones
- Proporcionar mensajes de error descriptivos

**Colaboradores:**

- `FileParser` - Valida problemas parseados de archivos
- `UserInterface` - Valida entrada interactiva del usuario

**Ubicación:** `simplex_solver/input_validator.py`

**Tipo:** Validador (Validator)
