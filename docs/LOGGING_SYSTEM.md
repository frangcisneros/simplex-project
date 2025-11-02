# Sistema de Logging - Simplex Solver

## Descripción General

El sistema de logging del Simplex Solver utiliza **SQLite** como base de datos para almacenar todos los eventos del sistema de manera persistente y eficiente. SQLite viene incluido con Python, por lo que no requiere instalación adicional.

## Características

### 📊 **Base de Datos SQLite**

- **Liviana**: SQLite es la base de datos más liviana disponible
- **Sin instalación**: Incluida con Python por defecto
- **Portable**: Un solo archivo `.db` contiene todo
- **Thread-safe**: Manejo seguro de concurrencia

### 📝 **Niveles de Log**

- **DEBUG**: Información detallada para diagnóstico
- **INFO**: Eventos generales del sistema
- **WARNING**: Advertencias que no detienen la ejecución
- **ERROR**: Errores que afectan funcionalidad
- **CRITICAL**: Errores graves que detienen el sistema

### 💾 **Información Capturada**

#### Logs Generales

- Timestamp con microsegundos
- Nivel del log (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- Módulo y función que genera el log
- Número de línea
- Mensaje descriptivo
- Información de excepciones (tipo, mensaje, stack trace)
- Datos personalizados del usuario

#### Sesiones

- ID único de sesión
- Timestamp de inicio y fin
- Versión de Python
- Sistema operativo y versión
- Arquitectura de máquina
- Modo de ejecución (development/executable)
- Argumentos de línea de comandos

#### Eventos del Solver

- Tipo de evento
- Tipo de problema (maximización/minimización)
- Número de variables y restricciones
- Iteraciones realizadas
- Tiempo de ejecución en milisegundos
- Estado final (optimal/unbounded/infeasible)
- Valor óptimo
- Datos adicionales personalizados

#### Operaciones con Archivos

- Tipo de operación (read/write/export)
- Ruta del archivo
- Tamaño del archivo
- Éxito/fallo de la operación
- Mensaje de error si aplica

### 🗄️ **Ubicación de la Base de Datos**

#### En Desarrollo

```
<proyecto>/logs/simplex_logs.db
```

#### En Producción (Ejecutable)

```
Windows: %APPDATA%\SimplexSolver\logs\simplex_logs.db
Linux/Mac: ~/.SimplexSolver/logs/simplex_logs.db
```

### ⏰ **Retención de Datos**

- **Período**: 6 meses (180 días)
- **Limpieza automática**: Se ejecuta al iniciar el sistema
- **Limpieza manual**: Disponible en el visor de logs

## Uso

### En el Código

```python
from logging_system import logger

# Logs básicos
logger.debug("Mensaje de depuración")
logger.info("Información general")
logger.warning("Advertencia")
logger.error("Error")
logger.critical("Error crítico")

# Log con excepción
try:
    # código que puede fallar
    resultado = operacion_riesgosa()
except Exception as e:
    logger.error("Falló la operación", exception=e)

# Log con datos personalizados
logger.info("Usuario realizó acción", user_data={
    "action": "solve",
    "variables": 5,
    "constraints": 3
})

# Log de eventos del solver
logger.log_solver_event(
    event_type="solve_complete",
    problem_type="maximización",
    num_variables=5,
    num_constraints=3,
    iterations=12,
    execution_time_ms=45.23,
    status="optimal",
    optimal_value=150.5
)

# Log de operaciones con archivos
logger.log_file_operation(
    operation_type="read",
    file_path="problema.txt",
    success=True
)
```

### Visor de Logs en Consola

#### Ejecutar el Visor

```bash
# En desarrollo
python view_logs.py

# O desde src
python src/log_viewer.py
```

#### Menú Principal

```
SIMPLEX SOLVER - VISOR DE LOGS
═══════════════════════════════════════════════════════════
1. Ver logs recientes
2. Ver logs por nivel
3. Ver logs por sesión
4. Ver estadísticas
5. Ver eventos del solver
6. Ver operaciones de archivos
7. Buscar en logs
8. Ver sesiones
9. Exportar logs
10. Limpiar logs antiguos
0. Salir
═══════════════════════════════════════════════════════════
```

### Integración con el .exe

El sistema de logs está completamente integrado y se incluye automáticamente al compilar el ejecutable:

1. **SQLite**: Ya viene con Python
2. **Tabulate**: Se agrega a `requirements.txt`
3. **Logging System**: Módulos en `src/`

No se requiere configuración adicional. El sistema:

- Se inicializa automáticamente
- Crea la BD en la primera ejecución
- Limpia logs antiguos automáticamente
- Funciona tanto en desarrollo como en el .exe

## Consultas SQL Útiles

### Conectar a la BD

```python
import sqlite3
conn = sqlite3.connect('path/to/simplex_logs.db')
cursor = conn.cursor()
```

### Ver todos los logs de hoy

```sql
SELECT timestamp, level, module, message
FROM logs
WHERE date(timestamp) = date('now')
ORDER BY timestamp DESC;
```

### Contar errores por módulo

```sql
SELECT module, COUNT(*) as error_count
FROM logs
WHERE level = 'ERROR'
GROUP BY module
ORDER BY error_count DESC;
```

### Ver sesiones activas

```sql
SELECT session_id, start_time, execution_mode
FROM sessions
WHERE end_time IS NULL;
```

### Estadísticas del solver

```sql
SELECT
    COUNT(*) as total_solves,
    AVG(iterations) as avg_iterations,
    AVG(execution_time_ms) as avg_time_ms,
    status,
    COUNT(*) as count_by_status
FROM solver_events
WHERE event_type = 'solve_complete'
GROUP BY status;
```

### Archivos más problemáticos

```sql
SELECT file_path, COUNT(*) as fail_count
FROM file_operations
WHERE success = 0
GROUP BY file_path
ORDER BY fail_count DESC
LIMIT 10;
```

## Estructura de Tablas

### Tabla: `logs`

- `id`: ID autoincremental
- `timestamp`: Fecha y hora del log
- `session_id`: ID de la sesión
- `level`: Nivel del log
- `module`: Nombre del módulo
- `function`: Nombre de la función
- `line_number`: Número de línea
- `message`: Mensaje del log
- `exception_type`: Tipo de excepción (si aplica)
- `exception_message`: Mensaje de excepción (si aplica)
- `stack_trace`: Stack trace completo (si aplica)
- `user_data`: Datos personalizados (JSON string)
- `system_info`: Información del sistema
- `created_at`: Timestamp de creación

### Tabla: `sessions`

- `id`: ID autoincremental
- `session_id`: ID único de sesión
- `start_time`: Inicio de la sesión
- `end_time`: Fin de la sesión
- `python_version`: Versión de Python
- `os_system`: Sistema operativo
- `os_version`: Versión del SO
- `machine`: Arquitectura de máquina
- `processor`: Información del procesador
- `app_version`: Versión de la aplicación
- `execution_mode`: Modo (development/executable)
- `command_line_args`: Argumentos de CLI

### Tabla: `solver_events`

- `id`: ID autoincremental
- `session_id`: ID de la sesión
- `timestamp`: Fecha y hora del evento
- `event_type`: Tipo de evento
- `problem_type`: Tipo de problema
- `num_variables`: Número de variables
- `num_constraints`: Número de restricciones
- `iterations`: Iteraciones realizadas
- `execution_time_ms`: Tiempo de ejecución en ms
- `status`: Estado final
- `optimal_value`: Valor óptimo
- `additional_data`: Datos adicionales (JSON string)

### Tabla: `file_operations`

- `id`: ID autoincremental
- `session_id`: ID de la sesión
- `timestamp`: Fecha y hora de la operación
- `operation_type`: Tipo de operación
- `file_path`: Ruta del archivo
- `file_size`: Tamaño del archivo
- `success`: Éxito (1) o fallo (0)
- `error_message`: Mensaje de error (si aplica)

## Rendimiento

- **Tamaño promedio**: ~1-2 MB por mes de uso normal
- **Velocidad de escritura**: < 1ms por log
- **Velocidad de consulta**: < 10ms para la mayoría de consultas
- **Índices**: Optimizados para búsquedas frecuentes por timestamp, nivel y sesión

## Mantenimiento

### Limpieza Automática

- Se ejecuta al iniciar cada sesión
- Elimina logs mayores a 6 meses
- Ejecuta VACUUM para liberar espacio

### Limpieza Manual

```python
from logging_system import logger
logger._cleanup_old_logs()
```

O desde el visor de logs: Opción 10

### Backup

```bash
# Copiar la base de datos
cp logs/simplex_logs.db logs/simplex_logs_backup.db

# O desde Python
import shutil
shutil.copy('logs/simplex_logs.db', 'logs/backup.db')
```

## Troubleshooting

### La BD no se crea

- Verificar permisos de escritura en la carpeta
- Verificar que SQLite está disponible: `python -c "import sqlite3; print(sqlite3.version)"`

### La BD crece mucho

- Ejecutar limpieza manual de logs antiguos
- Reducir el nivel de log (menos DEBUG, más INFO)
- Ejecutar VACUUM: `sqlite3 simplex_logs.db "VACUUM;"`

### Errores al importar tabulate

```bash
pip install tabulate
```

### Ver la BD con herramientas externas

- **DB Browser for SQLite**: https://sqlitebrowser.org/
- **SQLite Viewer (VS Code)**: Extensión disponible
- **CLI**: `sqlite3 path/to/simplex_logs.db`

## Ejemplo de Integración Completa

```python
from logging_system import logger
import time

def resolver_problema(c, A, b):
    """Ejemplo de función con logging completo."""
    logger.info("Iniciando resolución del problema")
    start_time = time.time()

    try:
        # Validación
        logger.debug(f"Validando problema con {len(c)} variables")
        if not validar_entrada(c, A, b):
            logger.warning("Problema no válido")
            return None

        # Resolución
        logger.info("Ejecutando algoritmo simplex")
        resultado = simplex_solver(c, A, b)

        # Log del evento
        exec_time = (time.time() - start_time) * 1000
        logger.log_solver_event(
            event_type="solve_complete",
            problem_type="maximización",
            num_variables=len(c),
            num_constraints=len(A),
            iterations=resultado['iterations'],
            execution_time_ms=exec_time,
            status=resultado['status'],
            optimal_value=resultado.get('optimal_value')
        )

        logger.info(f"Resolución completada en {exec_time:.2f}ms")
        return resultado

    except Exception as e:
        logger.error(f"Error al resolver problema: {str(e)}", exception=e)
        raise
    finally:
        logger.end_session()
```

## Próximos Pasos

Posibles mejoras futuras:

- Dashboard web para visualización
- Alertas por email/SMS en errores críticos
- Exportación a formato JSON/CSV
- Integración con sistemas de monitoreo externos
- Métricas de rendimiento en tiempo real
- Análisis de tendencias y patrones
