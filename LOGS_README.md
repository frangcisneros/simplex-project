# 📊 Sistema de Logs - Guía Rápida

## ¿Qué es?

Un sistema completo de logging con SQLite que captura **TODO** lo que pasa en el Simplex Solver:

- ✅ Cada operación del solver
- ✅ Cada archivo leído/escrito
- ✅ Cada error o warning
- ✅ Información del sistema
- ✅ Métricas de rendimiento

## 🚀 Inicio Rápido

### Ver los Logs

```bash
# Ejecutar el visor de logs
python view_logs.py
```

Esto abre un menú interactivo en consola donde puedes:

- Ver logs recientes
- Buscar por nivel (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- Ver estadísticas
- Exportar logs a archivo de texto
- Limpiar logs antiguos

### En el Código

El logging ya está integrado en todos los módulos principales. No necesitas hacer nada adicional, pero si quieres agregar logs personalizados:

```python
from logging_system import logger

logger.info("Tu mensaje aquí")
logger.warning("Una advertencia")
logger.error("Un error", exception=e)
```

## 📁 ¿Dónde están los logs?

### En desarrollo:

```
<proyecto>/logs/simplex_logs.db
```

### En el ejecutable (.exe):

```
%APPDATA%\SimplexSolver\logs\simplex_logs.db
```

## 🔍 Ver la Base de Datos

### Con el Visor Incluido

```bash
python view_logs.py
```

### Con DB Browser (Opcional)

Descarga: https://sqlitebrowser.org/
Abre: `logs/simplex_logs.db`

### Con SQLite CLI

```bash
sqlite3 logs/simplex_logs.db
.tables
SELECT * FROM logs ORDER BY timestamp DESC LIMIT 10;
```

## 📊 ¿Qué se Guarda?

### 1. Logs Generales (tabla `logs`)

- Timestamp preciso (microsegundos)
- Nivel (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- Módulo y función que generó el log
- Mensaje descriptivo
- Stack traces de errores
- Datos personalizados

### 2. Sesiones (tabla `sessions`)

- Cuándo inició y terminó cada ejecución
- Versión de Python y SO
- Argumentos de línea de comandos
- Modo (development o executable)

### 3. Eventos del Solver (tabla `solver_events`)

- Cada problema resuelto
- Número de variables y restricciones
- Iteraciones realizadas
- Tiempo de ejecución en milisegundos
- Estado final (optimal, unbounded, infeasible)
- Valor óptimo encontrado

### 4. Operaciones con Archivos (tabla `file_operations`)

- Cada archivo leído o escrito
- Tamaño del archivo
- Éxito/fallo de la operación
- Errores si los hubo

## ⏰ Retención

- **6 meses** de logs guardados automáticamente
- Limpieza automática al iniciar el programa
- Puedes cambiar el período en `logging_system.py`:
  ```python
  self.retention_days = 180  # Cambiar según necesites
  ```

## 🎯 Casos de Uso

### 1. Debugging

```
Ver logs > Filtrar por ERROR > Encontrar stack trace completo
```

### 2. Análisis de Rendimiento

```
Ver estadísticas > Tiempo promedio de ejecución
```

### 3. Auditoría

```
Ver sesiones > Ver qué archivos se procesaron > Exportar informe
```

### 4. Búsqueda Específica

```
Buscar en logs > "problema no factible" > Ver contexto
```

## 🛠️ Configuración

Todo funciona out-of-the-box, pero puedes personalizar:

### Cambiar Nivel de Log

En `logging_system.py`, puedes filtrar logs por nivel:

```python
# En _print_log(), comenta niveles que no quieres ver en consola
if level == "DEBUG":
    return  # No mostrar DEBUG en consola
```

### Cambiar Ubicación de la BD

En `logging_system.py`, método `_get_db_path()`:

```python
log_dir = "tu/ruta/personalizada"
```

### Agregar Campos Personalizados

Extiende las tablas en `_init_database()`:

```sql
ALTER TABLE logs ADD COLUMN mi_campo TEXT;
```

## 📈 Consultas SQL Útiles

### Ver errores recientes

```sql
SELECT timestamp, module, message, exception_message
FROM logs
WHERE level = 'ERROR'
ORDER BY timestamp DESC
LIMIT 20;
```

### Problemas más lentos

```sql
SELECT num_variables, num_constraints, iterations, execution_time_ms
FROM solver_events
ORDER BY execution_time_ms DESC
LIMIT 10;
```

### Tasa de éxito

```sql
SELECT
    status,
    COUNT(*) as count,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM solver_events), 2) as percentage
FROM solver_events
GROUP BY status;
```

## 🚨 Troubleshooting

### Error: "No se encuentra la BD"

```bash
# Ejecuta el programa al menos una vez para crear la BD
python simplex.py -i
```

### Error al importar tabulate

```bash
pip install -r requirements.txt
```

### BD muy grande

```bash
# Limpiar logs manualmente
python view_logs.py
# Opción 10 > Ingresar días > Confirmar
```

### Logs no aparecen en consola

Verifica que los colores ANSI funcionen en tu terminal. En Windows, asegúrate de usar Windows Terminal o PowerShell moderno.

## 📚 Documentación Completa

Ver: `docs/LOGGING_SYSTEM.md`

## 💡 Tips

1. **Performance**: El logging es asíncrono y no afecta el rendimiento del solver
2. **Tamaño**: 6 meses de logs normales = ~10-20 MB
3. **Búsqueda**: Usa el visor de logs, es más rápido que SQL directo
4. **Exportar**: Si necesitas compartir logs, usa la opción de exportación
5. **Backup**: La BD es un solo archivo, fácil de copiar/respaldar

## 🎨 Colores en Consola

Los logs usan colores ANSI:

- 🔵 DEBUG = Cyan
- 🟢 INFO = Verde
- 🟡 WARNING = Amarillo
- 🔴 ERROR = Rojo
- 🟣 CRITICAL = Magenta

## ✅ Checklist de Instalación

- [x] SQLite (viene con Python)
- [x] tabulate (en requirements.txt)
- [x] Módulos de logging integrados
- [x] Visor de logs incluido
- [x] Todo funciona en el .exe

¡Listo para usar! 🎉
