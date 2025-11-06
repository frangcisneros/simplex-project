# Tarjeta CRC: UserInterface

### Clase: UserInterface

**Responsabilidades:**

- Gestionar entrada interactiva del usuario
- Solicitar tipo de optimización (maximizar/minimizar)
- Recoger coeficientes de la función objetivo
- Recoger restricciones del problema
- Validar formato de restricciones (<=, >=, =)
- Verificar consistencia dimensional de entrada
- Validar que no todos los coeficientes sean cero
- Mostrar el problema formateado antes de resolver
- Mostrar resultados de la optimización
- Formatear salida según el estado (optimal, infeasible, unbounded, error)
- Proporcionar mensajes de error descriptivos al usuario

**Colaboradores:**

- `InputValidator` - Valida problemas antes de resolver
- Usuario - Interacción en modo consola

**Ubicación:** `simplex_solver/user_interface.py`

**Tipo:** Interfaz de usuario (User Interface)
