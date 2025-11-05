# Guía del Usuario - Simplex Solver

## Descripción General

Simplex Solver es un sistema de optimización lineal que implementa el algoritmo Simplex con capacidades de procesamiento de lenguaje natural. El sistema permite resolver problemas de programación lineal tanto en formato matemático como descritos en español usando modelos de lenguaje local mediante Ollama.

## Instalación

### Instalación mediante Instalador Interactivo (Recomendado)

El instalador interactivo facilita la configuración completa del sistema, incluyendo componentes opcionales como Ollama y modelos de inteligencia artificial.

#### Requisitos del Sistema

**Requisitos Mínimos (solver básico):**

- Windows 10 o superior
- 2 GB RAM
- 500 MB espacio en disco
- Python 3.8+ (si se usa desde código fuente)

**Requisitos Recomendados (con IA):**

- Windows 10 o superior
- 8 GB RAM
- 20 GB espacio en disco (para Ollama y modelos)
- GPU NVIDIA (opcional, mejora rendimiento)

#### Procedimiento de Instalación

1. Descargue el paquete de distribución
2. Ejecute `SimplexInstaller.exe` como administrador
3. El instalador analizará automáticamente las capacidades de su sistema
4. Siga las instrucciones en pantalla para seleccionar los componentes deseados

**Nota sobre permisos de administrador:** El instalador requiere permisos de administrador para:

- Instalar el menú contextual de Windows (modifica el registro)
- Instalar paquetes de Python globalmente
- Garantizar que Ollama se configure correctamente

#### Componentes Instalables

**1. Dependencias Base** (obligatorio)

- Bibliotecas necesarias para el solver: NumPy, psutil, tabulate

**2. Ollama** (opcional)

- Motor de IA local para procesamiento de lenguaje natural
- Permite resolver problemas descritos en español
- Funciona completamente offline

**3. Modelos de IA** (opcional)

El instalador recomienda modelos según las capacidades de su sistema:

| Modelo       | RAM Requerida | Descripción                                         |
| ------------ | ------------- | --------------------------------------------------- |
| llama3.2:1b  | 2 GB          | Modelo ligero para sistemas con recursos limitados  |
| llama3.2:3b  | 4 GB          | Modelo balanceado para uso general                  |
| phi3:mini    | 4 GB          | Modelo optimizado por Microsoft                     |
| llama3.1:8b  | 8 GB          | Calidad media, recomendado para problemas complejos |
| mistral:7b   | 8 GB          | Rendimiento excelente para uso general              |
| gemma2:9b    | 10 GB         | Alta capacidad de procesamiento                     |
| llama3.1:70b | 48 GB         | Máxima calidad para sistemas de alto rendimiento    |

**4. Menú Contextual de Windows** (opcional)

- Integración con el explorador de archivos
- Opción de clic derecho en archivos .txt
- Acceso rápido a "Resolver con Simplex Solver"
- Opción adicional "Resolver con IA"

#### Análisis Automático del Sistema

El instalador detecta automáticamente:

- RAM total y disponible
- Núcleos de CPU y frecuencia
- GPU NVIDIA (si está disponible)
- Sistema operativo y arquitectura

Esta información se utiliza para recomendar los modelos más adecuados para su hardware.

### Instalación Manual desde Código Fuente

Para desarrolladores o usuarios avanzados:

```bash
# Clonar el repositorio
git clone https://github.com/frangcisneros/simplex-project
cd simplex-project

# Instalar dependencias
pip install -r requirements.txt

# Instalar Ollama (opcional, para IA)
# Descargar desde: https://ollama.ai/download

# Descargar modelo de IA (opcional)
ollama pull llama3.1:8b
```

## Menú Contextual de Windows

El menú contextual permite resolver problemas de Simplex directamente desde el Explorador de Windows.

### Instalación del Menú Contextual

#### Instalación Automática (Recomendado)

1. Navegue a la carpeta `context_menu/` del proyecto
2. Localice el archivo `install.bat`
3. Haga clic derecho sobre `install.bat`
4. Seleccione "Ejecutar como administrador"
5. Siga las instrucciones en pantalla

El instalador detectará automáticamente su instalación de Python, verificará que el script existe y configurará la entrada en el registro de Windows.

#### Instalación Manual

Si prefiere configurar manualmente la integración:

1. Abra el Editor del Registro (Win+R, escriba `regedit`, presione Enter)
2. Navegue a: `HKEY_CLASSES_ROOT\txtfile\shell`
3. Cree una nueva clave llamada `SimplexSolver`
4. En la clave `SimplexSolver`:
   - Modifique el valor `(Predeterminado)` a: `Resolver con Simplex Solver`
5. Cree una subclave dentro de `SimplexSolver` llamada `command`
6. En la clave `command`:
   - Modifique el valor `(Predeterminado)` a:
   ```
   "C:\ruta\a\python.exe" "C:\ruta\al\proyecto\context_menu\solve_from_context.py" "%1"
   ```
   (Reemplace las rutas con sus rutas reales)

### Uso del Menú Contextual

Una vez instalado:

1. Cree o abra un archivo `.txt` con un problema de Simplex
2. Haga clic derecho sobre el archivo
3. Seleccione "Resolver con Simplex Solver" del menú contextual
4. Se abrirá una ventana de consola mostrando:
   - El problema parseado
   - El proceso de resolución
   - Los resultados
   - Opción para generar un PDF

### Formato de Archivos de Entrada

Los archivos `.txt` deben seguir esta estructura:

```
MAXIMIZE
3 2
SUBJECT TO
2 1 <= 18
2 3 <= 42
3 1 <= 24
```

Para problemas de minimización:

```
MINIMIZE
-3 -2
SUBJECT TO
2 1 >= 18
2 3 >= 42
3 1 = 24
```

**Estructura del formato:**

1. Primera línea: `MAXIMIZE` o `MINIMIZE`
2. Segunda línea: Coeficientes de la función objetivo (separados por espacios)
3. Tercera línea: `SUBJECT TO`
4. Siguientes líneas: Restricciones en formato `a1 a2 ... an <= b` (también puede usar `>=` o `=`)

### Desinstalación del Menú Contextual

Para eliminar el menú contextual:

1. Navegue a la carpeta `context_menu/`
2. Localice `uninstall.bat`
3. Haga clic derecho y seleccione "Ejecutar como administrador"
4. Confirme la desinstalación

Alternativamente, elimine manualmente la clave del registro:

- `HKEY_CLASSES_ROOT\txtfile\shell\SimplexSolver`

### Solución de Problemas Comunes

**"No se pudo encontrar Python"**

- Verifique que Python esté instalado: `python --version` en cmd
- Asegúrese de que Python esté en el PATH del sistema
- Edite `install.bat` y agregue la ruta correcta de Python

**"No se encontró el archivo solve_from_context.py"**

- Asegúrese de ejecutar el instalador desde la carpeta `context_menu/`
- Verifique que `solve_from_context.py` existe en la carpeta `context_menu/`

**"El menú no aparece al hacer clic derecho"**

- Verifique que ejecutó el instalador como administrador
- Reinicie el explorador de archivos (Ctrl+Shift+Esc → Buscar "Windows Explorer" → Reiniciar)
- Verifique que la entrada existe en el registro

**"Error al resolver el problema"**

- Verifique que el formato del archivo `.txt` sea correcto
- Compruebe que todas las dependencias estén instaladas
- Revise que no haya errores de sintaxis en el archivo

**"Ventana se cierra inmediatamente"**

- La ventana permanece abierta hasta que presione Enter
- Si se cierra antes, puede haber un error en el archivo de entrada

## Uso de la Aplicación

### Modo Interactivo

Ejecute el solver sin argumentos para iniciar el modo interactivo:

```bash
# Desde Python
python simplex.py --interactive

# Desde el ejecutable
SimplexSolver.exe --interactive
```

El sistema solicitará:

1. Tipo de problema (maximización o minimización)
2. Número de variables
3. Coeficientes de la función objetivo
4. Número de restricciones
5. Coeficientes y tipo de cada restricción

### Resolución desde Archivo

```bash
# Desde Python
python simplex.py ejemplos/ejemplo_maximizacion.txt

# Desde el ejecutable
SimplexSolver.exe ejemplos/ejemplo_maximizacion.txt

# Con generación de PDF
python simplex.py ejemplos/ejemplo_carpinteria.txt --pdf resultado.pdf
```

### Historial de Problemas

El sistema mantiene un historial de todos los problemas resueltos:

```bash
# Ver historial
python simplex.py --history

# Desde el ejecutable
SimplexSolver.exe --history
```

El visor de historial ofrece:

1. Ver todos los problemas resueltos
2. Buscar problema por nombre
3. Ver detalles de un problema específico
4. Re-resolver un problema del historial
5. Ver estadísticas del historial

El historial se almacena en una base de datos SQLite y conserva:

- Contenido completo del archivo
- Tipo de problema y parámetros
- Iteraciones y tiempo de ejecución
- Valor óptimo y variables de solución
- Fecha y hora de resolución

**Ubicación de la base de datos:**

- En desarrollo: `<proyecto>/logs/simplex_logs.db`
- En producción: `%APPDATA%\SimplexSolver\logs\simplex_logs.db` (Windows)

**Retención de datos:** Los problemas se conservan durante 180 días (6 meses) antes de ser eliminados automáticamente.

### Resolución con Inteligencia Artificial

Para resolver problemas descritos en lenguaje natural:

```bash
python simplex.py --nlp "Una empresa fabrica dos productos..."

# O usando el menú contextual con opción "Resolver con IA"
```

Ejemplo de descripción en lenguaje natural:

```
Una carpintería fabrica mesas y sillas.
Cada mesa genera $80 de ganancia.
Cada silla genera $50 de ganancia.
Hay 200 horas de trabajo disponibles.
Cada mesa requiere 4 horas, cada silla 2 horas.
Máximo 60 unidades en total.
¿Cuántas unidades se deben producir para maximizar la ganancia?
```

El sistema procesará la descripción, identificará variables y restricciones, y resolverá el problema automáticamente.

## Ejemplos de Problemas

La carpeta `ejemplos/` contiene varios archivos de ejemplo:

### ejemplo_maximizacion.txt

Problema básico de maximización con restricciones de tipo `<=`.

### ejemplo_minimizacion.txt

Problema de minimización con restricciones de tipo `>=`.

### ejemplo_carpinteria.txt

Problema realista de producción en una carpintería.

### max_4tablas.txt

Problema complejo con múltiples restricciones.

### Crear Problemas Personalizados

1. Cree un nuevo archivo `.txt`
2. Siga el formato especificado en la sección "Formato de Archivos de Entrada"
3. Guárdelo en cualquier ubicación
4. Resuélvalo usando el menú contextual o línea de comandos

## Exportación de Resultados

### Generación de PDF

```bash
python simplex.py problema.txt --pdf reporte.pdf
```

El PDF incluye:

- Problema original
- Proceso de solución
- Resultado final
- Valor óptimo
- Valores de las variables

### Formato de Salida en Consola

La salida muestra:

- Tipo de problema (maximización/minimización)
- Función objetivo
- Restricciones
- Número de iteraciones
- Tiempo de ejecución
- Estado de la solución (óptima/no acotada/infactible)
- Valor óptimo
- Valores de las variables

## Configuración Avanzada

### Modelos de IA

Para cambiar el modelo de IA utilizado, edite `simplex_solver/nlp/config.py`:

```python
class DefaultSettings:
    DEFAULT_MODEL = NLPModelType.LLAMA3_1_8B  # Cambiar según preferencia
```

### Parámetros del Modelo

Ajuste los parámetros de generación en `simplex_solver/nlp/config.py`:

```python
ModelConfig.DEFAULT_CONFIGS[NLPModelType.LLAMA3_1_8B] = {
    "temperature": 0.1,  # Precisión (0-1, menor = más preciso)
    "max_tokens": 2048,
    "top_p": 0.9
}
```

## Verificación de la Instalación

### Verificar Ollama

```bash
ollama list
```

Debería mostrar los modelos instalados.

### Verificar Dependencias de Python

```bash
pip list | findstr "numpy tabulate psutil"
```

### Ejecutar Tests de Sistema

```bash
cd tests
python test_nlp_system.py
```

## Soporte y Documentación Adicional

Para más información técnica, consulte GUIA_DESARROLLADOR.md en la raíz del proyecto.

Para reportar problemas o solicitar características, visite el repositorio del proyecto en GitHub.
