# 📚 Sistema de Historial de Problemas

## Descripción

El sistema de historial permite **guardar automáticamente** todos los problemas resueltos y **re-resolverlos** en cualquier momento sin necesidad de buscar el archivo original.

## 🎯 Características

### ✅ Guardado Automático

- Cada problema resuelto con **estado óptimo** se guarda automáticamente en el historial
- Se almacena:
  - Contenido completo del archivo
  - Tipo de problema (maximización/minimización)
  - Número de variables y restricciones
  - Iteraciones y tiempo de ejecución
  - Valor óptimo y variables de solución
  - Fecha y hora de resolución

### 📊 Visualización

- Ver **tabla completa** de todos los problemas resueltos
- **Buscar** problemas por nombre de archivo
- Ver **detalles completos** de cualquier problema
- Ver **estadísticas** del historial

### 🔄 Re-resolver Problemas

- Seleccionar cualquier problema del historial
- Se crea automáticamente un archivo temporal con el contenido original
- Se ejecuta el solver sin necesidad de buscar el archivo original

## 🚀 Uso

### Opción 1: Desde el menú del .exe

```batch
# Ejecutar SimplexSolver_Menu.bat
# Seleccionar opción 2: "Ver historial de problemas resueltos"
```

### Opción 2: Desde línea de comandos

```bash
# Ver historial y opcionalmente re-resolver
python simplex.py --history

# O usar el script dedicado
python view_history.py
```

### Opción 3: Programáticamente

```python
from problem_history import ProblemHistory

# Crear instancia
history = ProblemHistory()

# Obtener todos los problemas
problems = history.get_all_problems(limit=50)

# Buscar por nombre
results = history.search_problems("test")

# Obtener detalles completos
problem = history.get_problem_by_id(1)

# Crear archivo temporal para re-resolver
temp_file = history.create_temp_file_from_history(1)

# Obtener estadísticas
stats = history.get_statistics()
```

## 📋 Menú Interactivo

El visor de historial ofrece las siguientes opciones:

1. **Ver todos los problemas** - Tabla con todos los problemas resueltos
2. **Buscar problema por nombre** - Búsqueda por palabra clave
3. **Ver detalles de un problema** - Información completa incluyendo contenido
4. **Re-resolver un problema** - Crear archivo temporal y ejecutar solver
5. **Ver estadísticas** - Resumen del historial
6. **Volver al menú principal** - Salir

## 🗄️ Almacenamiento

### Ubicación de la Base de Datos

**En desarrollo:**

```
<proyecto>/logs/simplex_logs.db
```

**En producción (.exe):**

```
%APPDATA%\SimplexSolver\logs\simplex_logs.db
```

### Tabla: problem_history

| Campo              | Tipo    | Descripción                     |
| ------------------ | ------- | ------------------------------- |
| id                 | INTEGER | ID único del problema           |
| session_id         | TEXT    | ID de la sesión que lo resolvió |
| timestamp          | TEXT    | Fecha y hora de resolución      |
| file_path          | TEXT    | Ruta original del archivo       |
| file_name          | TEXT    | Nombre del archivo              |
| file_content       | TEXT    | Contenido completo del archivo  |
| problem_type       | TEXT    | "maximización" o "minimización" |
| num_variables      | INTEGER | Número de variables             |
| num_constraints    | INTEGER | Número de restricciones         |
| iterations         | INTEGER | Iteraciones necesarias          |
| execution_time_ms  | REAL    | Tiempo de ejecución en ms       |
| status             | TEXT    | Estado final ("optimal", etc.)  |
| optimal_value      | REAL    | Valor óptimo encontrado         |
| solution_variables | TEXT    | JSON con variables de solución  |

## 🔧 Retención de Datos

- **Período de retención:** 180 días (6 meses)
- **Limpieza automática:** Se ejecuta al iniciar el sistema
- Los problemas más antiguos se eliminan automáticamente

## 📊 Estadísticas Disponibles

El sistema proporciona:

- Total de problemas resueltos
- Problemas por tipo (maximización/minimización)
- Problemas por estado (optimal, infeasible, etc.)
- Promedio de iteraciones
- Promedio de tiempo de ejecución

## 💡 Ejemplos de Uso

### Ejemplo 1: Ver historial completo

```bash
$ python view_history.py

HISTORIAL DE PROBLEMAS
1. Ver todos los problemas

[Muestra tabla con todos los problemas]
```

### Ejemplo 2: Re-resolver un problema

```bash
$ python simplex.py --history

[Menú interactivo]
Opción: 4
ID del problema: 1

✓ Archivo temporal creado
Ejecutando solver...
[Solución del problema]
```

### Ejemplo 3: Buscar problema específico

```bash
$ python view_history.py

Opción: 2
Palabra clave: produccion

[Muestra problemas que contienen "produccion"]
```

## 🔍 Consultas SQL Útiles

Si necesitas acceder directamente a la base de datos:

```sql
-- Ver últimos 10 problemas
SELECT id, timestamp, file_name, problem_type, optimal_value
FROM problem_history
ORDER BY timestamp DESC
LIMIT 10;

-- Buscar por nombre
SELECT * FROM problem_history
WHERE file_name LIKE '%test%';

-- Estadísticas por tipo
SELECT problem_type, COUNT(*), AVG(iterations), AVG(execution_time_ms)
FROM problem_history
GROUP BY problem_type;
```

## ⚠️ Notas Importantes

1. **Solo problemas óptimos**: Solo se guardan en el historial los problemas con solución óptima
2. **Archivos temporales**: Los archivos creados para re-resolver son temporales y se eliminan automáticamente
3. **Modo interactivo**: Los problemas ingresados interactivamente también se guardan si se resuelven exitosamente
4. **Backup**: Considera hacer backup periódico de `simplex_logs.db` si el historial es importante

## 🆘 Solución de Problemas

### No se muestra el historial

- Verifica que hayas resuelto al menos un problema exitosamente
- Confirma que la base de datos existe en la ubicación correcta

### Error al re-resolver

- El archivo temporal puede haber sido eliminado
- Verifica permisos de escritura en la carpeta temporal

### Historial vacío después de reinstalar

- El historial se guarda en `%APPDATA%`, no se pierde al reinstalar
- Si reinstalaste Windows, el historial se habrá perdido

## 📞 Soporte

Para más información sobre el sistema de historial, consulta:

- `src/problem_history.py` - Código fuente
- `LOGGING_SYSTEM.md` - Documentación del sistema de logs
- `test_history.py` - Ejemplos de uso programático
