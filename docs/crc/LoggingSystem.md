# Tarjeta CRC: LoggingSystem

### Clase: LoggingSystem

**Responsabilidades:**

- Proporcionar sistema centralizado de logging con persistencia en SQLite
- Implementar patrón Singleton para instancia única
- Gestionar base de datos de logs con múltiples tablas (logs, sessions, solver_events, file_operations, problem_history)
- Registrar eventos del sistema con información detallada (timestamp, nivel, módulo, función, línea)
- Capturar y almacenar excepciones con stack traces completos
- Registrar información del sistema al inicio de cada sesión
- Mantener historial de problemas resueltos para re-resolución
- Registrar eventos específicos del solver (iteraciones, tiempo, valor óptimo)
- Registrar operaciones con archivos (lectura, escritura, exportación)
- Implementar limpieza automática de logs antiguos (retention policy)
- Formatear y mostrar logs en consola con colores ANSI
- Indexar logs para mejorar rendimiento de consultas
- Proporcionar métodos de conveniencia (debug, info, warning, error, critical)

**Colaboradores:**

- `sqlite3` - Almacenamiento persistente de logs
- Componentes del sistema que generan logs

**Ubicación:** `simplex_solver/logging_system.py`

**Tipo:** Singleton, Sistema de infraestructura (Infrastructure Service)
