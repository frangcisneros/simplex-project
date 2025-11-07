# Herramientas de Desarrollo - Simplex Solver

Este directorio contiene herramientas de desarrollo consolidadas que siguen los principios SOLID. Cada herramienta está diseñada para un propósito único y bien definido.

## Descripción General

Todas las herramientas en este directorio son scripts independientes de Python que pueden ejecutarse desde la raíz del proyecto. Proporcionan interfaces unificadas para tareas comunes de desarrollo.

## Herramientas Disponibles

### build.py - Sistema de Construcción Unificado

Consolida toda la funcionalidad de construcción para crear ejecutables de Windows utilizando PyInstaller.

**Uso:**

```powershell
# Construir todo en el orden correcto (RECOMENDADO)
python tools/build.py --all

# Construir solo el solver
python tools/build.py --solver

# Construir solo el instalador (requiere que el solver ya esté compilado)
python tools/build.py --installer

# Limpiar artefactos de construcción (dist/, build/, *.spec)
python tools/build.py --clean

# Limpiar y reconstruir todo
python tools/build.py --clean --all
```

**Importante - Orden de Construcción:**

El instalador (`SimplexInstaller.exe`) incluye el solver (`SimplexSolver.exe`) empaquetado dentro. Por lo tanto, **debes construir el solver ANTES de construir el instalador**.

- Correcto: `python tools/build.py --all` (construye en orden automáticamente)
- Correcto: Primero `--solver`, luego `--installer`
- Incorrecto: Solo `--installer` sin haber compilado el solver primero

**Características:**

- Instalación automática de PyInstaller si no está presente
- Configuraciones separadas para instalador y solver
- Genera archivos .spec dinámicamente
- Verifica la salida y muestra tamaños de archivo
- Separación clara de responsabilidades utilizando principios SOLID

**Salida:**

- `dist/SimplexSolver.exe` - Solver independiente (~25-35 MB)
- `dist/SimplexInstaller.exe` - Instalador interactivo que incluye el solver (~45-55 MB)

**Orden de Construcción:**

Cuando usas `--all`, el sistema automáticamente:

1. Construye `SimplexSolver.exe` primero
2. Verifica que existe
3. Construye `SimplexInstaller.exe` incluyendo el solver

Si intentas construir solo el instalador sin tener el solver, recibirás un error claro con instrucciones.

**Configuraciones de Construcción:**

- **Installer**: Incluye manifiesto de administrador UAC, documentación completa, scripts de menú contextual
- **Solver**: Paquete mínimo con funcionalidad principal únicamente

**Arquitectura:**

- `BuildCleaner` - Elimina artefactos de construcción
- `PyInstallerManager` - Asegura la disponibilidad de PyInstaller
- `SpecFileGenerator` - Genera archivos .spec
- `ExecutableBuilder` - Compila ejecutables
- `BuildOrchestrator` - Coordina todo el proceso de construcción

### logs.py - Herramienta de Gestión de Logs

Proporciona acceso al sistema de registro basado en SQLite con múltiples modos de visualización y análisis.

**Uso:**

```powershell
# Iniciar visor de logs interactivo (predeterminado)
python tools/logs.py

# Mostrar estadísticas rápidas
python tools/logs.py --stats

# Verificar integridad del sistema de logs
python tools/logs.py --verify
```

**Características:**

**Modo Interactivo:**

- Ver logs recientes
- Filtrar por nivel (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- Ver logs por sesión
- Ver eventos del solver y operaciones de archivo
- Funcionalidad de búsqueda
- Exportar logs
- Limpiar logs antiguos

**Modo Estadísticas:**

- Conteo total de logs
- Conteo de sesiones
- Problemas resueltos
- Actividad en las últimas 24 horas

**Modo Verificar:**

- Verificación de integridad de la base de datos
- Estadísticas detalladas
- Últimos 5 registros
- Detalles del último problema resuelto
- Verificación de salud del sistema

**Ubicación de la Base de Datos de Logs:**

- **Desarrollo**: `logs/simplex_logs.db`
- **Producción**: `%APPDATA%\SimplexSolver\logs\simplex_logs.db`

### history.py - Gestión del Historial de Problemas

Gestiona el historial de problemas resueltos con menú interactivo y diagnósticos.

**Uso:**

```powershell
# Iniciar menú interactivo de historial (predeterminado)
python tools/history.py

# Probar funcionalidad del sistema de historial
python tools/history.py --test

# Mostrar estadísticas rápidas
python tools/history.py --stats
```

**Características:**

**Menú Interactivo:**

- Ver todos los problemas resueltos
- Buscar por nombre de problema
- Ver información detallada del problema
- Resolver problemas desde el historial
- Mostrar estadísticas de problemas

**Modo Prueba:**

- Recupera todos los problemas
- Muestra tabla de problemas
- Prueba la recuperación de detalles de problemas
- Crea y verifica archivos temporales
- Calcula estadísticas completas

**Modo Estadísticas:**

- Conteo total de problemas
- Tasa de éxito
- Máximo de variables/restricciones
- Lista de problemas recientes

**Datos del Historial:**

Almacenados en la misma base de datos SQLite que los logs, incluyen:

- Contenido del archivo
- Parámetros del problema
- Detalles de la solución
- Metadatos de ejecución

### system_analyzer.py - Analizador de Capacidades del Sistema

Analiza el hardware del sistema y proporciona recomendaciones para la selección de modelos Ollama.
**Actualizado con detección mejorada de RAM y selección automática de modelo óptimo.**

**Uso:**

```python
from tools.system_analyzer import SystemAnalyzer

analyzer = SystemAnalyzer()

# Obtener información básica del sistema
info = analyzer.get_system_info()
print(f"RAM Total: {info['RAM Total']}")
print(f"RAM Disponible: {info['RAM Disponible']}")

# Obtener el mejor modelo disponible automáticamente
best_model = analyzer.get_best_available_model()
print(f"Modelo recomendado: {best_model}")

# Obtener todas las recomendaciones de modelos
recommendations = analyzer.get_model_recommendations()
for rec in recommendations:
    if rec.recommended:
        print(f"✓ {rec.name} - {rec.reason}")
```

**Características:**

- **Detección Mejorada de RAM**: Usa el 80% de la RAM total como referencia (más realista que RAM "disponible")
- **Selección Automática de Modelo**: Identifica el modelo de IA más potente que puede ejecutar tu sistema
- **Recomendaciones Inteligentes**: Considera un margen de seguridad del 30% sobre los requisitos mínimos
- **Detección de GPU**: Identifica GPUs NVIDIA para aceleración
- **Análisis de CPU**: Detecta núcleos y frecuencia

**Modelos Soportados:**

| Modelo       | RAM Requerida | Tamaño | Descripción                     |
| ------------ | ------------- | ------ | ------------------------------- |
| llama3.2:1b  | 2 GB          | 1.3 GB | Modelo pequeño y rápido         |
| llama3.2:3b  | 4 GB          | 2.0 GB | Balance velocidad/calidad       |
| phi3:mini    | 4 GB          | 2.3 GB | Optimizado de Microsoft         |
| llama3.1:8b  | 8 GB          | 4.7 GB | Modelo por defecto              |
| mistral:7b   | 8 GB          | 4.1 GB | Excelente para tareas generales |
| gemma2:9b    | 10 GB         | 5.5 GB | Modelo de Google                |
| llama3.1:70b | 48 GB         | 40 GB  | Solo para sistemas potentes     |

**Integración con el Sistema de IA:**

El sistema ahora detecta automáticamente el mejor modelo al crear el conector NLP:

```python
from simplex_solver.nlp import NLPConnectorFactory

# Auto-detecta el mejor modelo según tu sistema
connector = NLPConnectorFactory.create_connector()

# O especifica uno manualmente
connector = NLPConnectorFactory.create_connector(nlp_model_type=NLPModelType.LLAMA3_1_8B)
```

**Usado por:**

- `installer.py` para recomendaciones automáticas de modelos

### test_installer.py - Pruebas del Instalador

Suite de pruebas para la funcionalidad del instalador interactivo.

**Uso:**

```powershell
python -m pytest tools/test_installer.py -v
```

**Pruebas:**

- Detección de capacidades del sistema
- Recomendaciones de modelos
- Flujos de trabajo de instalación

## Requisitos

Todas las herramientas requieren las dependencias base del proyecto:

```powershell
pip install -r requirements.txt
```

Para construir ejecutables:

```powershell
pip install -r requirements-build.txt
```

## Principios de Arquitectura

Todas las herramientas siguen los principios SOLID:

- **Responsabilidad Única**: Cada clase/función tiene un propósito claro
- **Abierto/Cerrado**: Extensible sin modificar el código existente
- **Sustitución de Liskov**: Las interfaces están correctamente abstraídas
- **Segregación de Interfaces**: No hay dependencias forzadas en métodos no utilizados
- **Inversión de Dependencias**: Dependencia en abstracciones, no en concreciones

## Ejemplos

### Construcción para Liberación

```powershell
# Limpiar construcciones previas
python tools/build.py --clean

# Construir ambos ejecutables
python tools/build.py --all

# Verificar salidas
ls dist/
```

### Verificación de Logs Después de un Error

```powershell
# Verificación rápida
python tools/logs.py --stats

# Verificación completa
python tools/logs.py --verify

# Visualización interactiva
python tools/logs.py
```

### Revisión del Historial de Problemas

```powershell
# Estadísticas rápidas
python tools/history.py --stats

# Encontrar y resolver un problema
python tools/history.py
# Luego seleccionar opción para ver/solucionar
```

## Formato de Salida

Todas las herramientas utilizan un formato de salida consistente:

- `[OK]` - Operación exitosa
- `[ERROR]` - Ocurrió un error
- `[WARNING]` - Mensaje de advertencia
- `[INFO]` - Mensaje informativo
- `[STATS]` - Información estadística
- `[BUILD]` - Mensaje relacionado con construcción
- `[CLEAN]` - Operación de limpieza

## Manejo de Errores

Todas las herramientas implementan un manejo de errores completo:

- Mensajes de error claros
- Impresión de traceback para depuración
- Fallo controlado con códigos de salida apropiados
- Verificaciones de existencia de archivos/bases de datos

## Pruebas

Las herramientas pueden probarse individualmente:

```powershell
# Probar sistema de construcción (ejecución simulada con --help)
python tools/build.py --help

# Probar sistema de logs
python tools/logs.py --verify

# Probar sistema de historial
python tools/history.py --test
```

## Integración con CI/CD

Estas herramientas están diseñadas para integración con CI/CD:

```yaml
# Ejemplo de flujo de trabajo en GitHub Actions
- name: Build executables
  run: python tools/build.py --all

- name: Verify logs
  run: python tools/logs.py --verify
```

## Mantenimiento

### Agregar Nuevos Objetivos de Construcción

Editar `build.py` y agregar un nuevo `BuildConfig` a `BuildOrchestrator.CONFIGS`:

```python
CONFIGS = {
    "new_target": BuildConfig(
        name="New Target",
        script="new_script.py",
        output_name="NewExecutable",
        add_data=[...],
        hidden_imports=[...],
        excludes=[...],
    )
}
```

### Extender el Visor de Logs

Subclasificar `LogViewer` en `simplex_solver/log_viewer.py` para agregar nuevas características.

### Agregar Funcionalidades al Historial

Extender la clase `ProblemHistory` en `simplex_solver/problem_history.py`.

## Resolución de Problemas

### Fallos en la Construcción

```powershell
# Asegurarse de que PyInstaller esté instalado
pip install pyinstaller

# Verificar errores de importación
python -c "import simplex_solver"

# Verificar todas las dependencias
pip install -r requirements.txt
```

### Errores en el Visor de Logs

```powershell
# Verificar que la base de datos exista
python tools/logs.py --verify

# Si falta, ejecutar el solver una vez para crearla
python simplex.py --interactive
```

### Historial Vacío

El historial solo almacena problemas con soluciones óptimas. Resolver al menos un problema válido primero.

## Rendimiento

- **Tiempo de construcción**: ~30-60 segundos por ejecutable
- **Visor de logs**: Maneja eficientemente más de 10,000 entradas de log
- **Historial**: La base de datos SQLite escala a miles de problemas

## Seguridad

- Todas las herramientas se ejecutan localmente, sin llamadas externas a la red
- Las bases de datos SQLite utilizan permisos de archivo apropiados
- Los artefactos de construcción están ignorados en git

## Contribuir

Al agregar nuevas herramientas:

1. Seguir los principios SOLID
2. Agregar docstrings completos
3. Implementar la bandera `--help`
4. Usar un manejo de errores consistente
5. Actualizar este README
6. Agregar pruebas si corresponde

## Referencias

- **Documentación Principal**: `GUIA_DESARROLLADOR.md`
- **Guía del Usuario**: `GUIA_USUARIO.md`
- **Configuración de Construcción**: `pyproject.toml`

---

**Última Actualización**: Noviembre 2025
**Versión**: 3.1
