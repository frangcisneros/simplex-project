# Tarjeta CRC: LogViewer

### Clase: LogViewer

**Responsabilidades:**

- Proporcionar interfaz para visualizar logs del sistema
- Consultar base de datos SQLite de logs
- Filtrar logs por nivel (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- Filtrar logs por sesión
- Mostrar logs recientes (últimas 24h, última semana, etc.)
- Formatear y mostrar logs en consola con colores
- Permitir búsqueda de logs por texto
- Mostrar estadísticas de logs
- Exportar logs a archivo de texto
- Proporcionar resumen de errores y advertencias

**Colaboradores:**

- `LoggingSystem` - Accede a base de datos de logs
- `sqlite3` - Consultas a base de datos

**Ubicación:** `simplex_solver/log_viewer.py`

**Tipo:** Visor de logs (Log Viewer)
