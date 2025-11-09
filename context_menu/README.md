# Menú Contextual de Windows para Simplex Solver

Este directorio contiene los scripts necesarios para integrar Simplex Solver con el menú contextual de Windows Explorer, permitiendo resolver problemas de programación lineal con un simple clic derecho.

## Contenido del Directorio

- **install.bat** - Instalador del menú contextual (requiere permisos de administrador)
- **uninstall.bat** - Desinstalador del menú contextual
- **reinstall.bat** - Reinstalador (desinstala y vuelve a instalar)
- **solve_from_context.py** - Script que se ejecuta al seleccionar "Resolver con Simplex Solver"
- **solve_from_context_ai.py** - Script que se ejecuta al seleccionar "Resolver con IA"
- **run_solver.bat** - Script auxiliar para ejecutar el solver tradicional
- **run_solver_ai.bat** - Script auxiliar para ejecutar el solver con IA

## Instalación

### Instalación Automática (Recomendado)

1. Navegue a esta carpeta en el Explorador de Windows
2. Haga clic derecho en `install.bat`
3. Seleccione **"Ejecutar como administrador"**
4. Siga las instrucciones en pantalla

El instalador:

- Detecta automáticamente su instalación de Python
- Verifica que los scripts existen en la ubicación correcta
- Crea las entradas necesarias en el registro de Windows
- Configura dos opciones en el menú contextual:
  - "Resolver con Simplex Solver" (modo tradicional)
  - "Resolver con IA" (requiere Ollama)

### Verificación de la Instalación

Para verificar que la instalación fue exitosa:

1. Navegue a la carpeta `ejemplos/` del proyecto
2. Haga clic derecho en cualquier archivo `.txt`
3. Debe aparecer la opción **"Resolver con Simplex Solver"** en el menú contextual

Si instaló Ollama, también verá **"Resolver con IA"**.

## Uso

### Modo Tradicional

Para resolver un problema usando el formato matemático estándar:

1. Cree un archivo `.txt` con su problema en el formato especificado (ver ejemplos)
2. Haga clic derecho sobre el archivo
3. Seleccione **"Resolver con Simplex Solver"**
4. Se abrirá una ventana de consola mostrando:
   - El problema parseado
   - El proceso de resolución
   - La solución óptima
   - Opción para generar un reporte PDF

### Modo IA (Lenguaje Natural)

Si tiene Ollama instalado, puede resolver problemas descritos en español:

1. Cree un archivo `.txt` con su problema en lenguaje natural
2. Haga clic derecho sobre el archivo
3. Seleccione **"Resolver con IA"**
4. El sistema procesará el texto, identificará variables y restricciones automáticamente

**Ejemplo de problema en lenguaje natural:**

```
Una fábrica produce dos tipos de productos.
El producto A genera $50 de ganancia y requiere 2 horas.
El producto B genera $40 de ganancia y requiere 1 hora.
Hay 100 horas disponibles.
Maximizar la ganancia.
```

## Formato de Archivos de Entrada

### Formato Tradicional

```
MAXIMIZE                    # O MINIMIZE
c1 c2 c3 ...               # Coeficientes de función objetivo
SUBJECT TO
a11 a12 ... <= b1          # Restricciones
a21 a22 ... >= b2
a31 a32 ... = b3
```

**Ejemplo completo:**

```
MAXIMIZE
3 2
SUBJECT TO
2 1 <= 18
2 3 <= 42
3 1 <= 24
```

Esto representa:

- **Función Objetivo:** Maximizar Z = 3x₁ + 2x₂
- **Restricción 1:** 2x₁ + x₂ ≤ 18
- **Restricción 2:** 2x₁ + 3x₂ ≤ 42
- **Restricción 3:** 3x₁ + x₂ ≤ 24

### Tipos de Restricción Soportados

- `<=` - Menor o igual que
- `>=` - Mayor o igual que
- `=` - Igual a

## Desinstalación

Para eliminar el menú contextual:

1. Navegue a esta carpeta en el Explorador de Windows
2. Haga clic derecho en `uninstall.bat`
3. Seleccione **"Ejecutar como administrador"**
4. Confirme la desinstalación cuando se le solicite

El script eliminará todas las entradas del registro de Windows asociadas.

## Reinstalación

Si necesita reinstalar (por ejemplo, después de mover el proyecto a otra ubicación):

1. Haga clic derecho en `reinstall.bat`
2. Seleccione **"Ejecutar como administrador"**

Este script desinstala la configuración anterior y vuelve a instalar con las rutas actualizadas.

## Solución de Problemas

### "No se pudo encontrar Python"

**Problema:** El instalador no puede detectar Python en su sistema.

**Solución:**

1. Verifique que Python está instalado: `python --version` en cmd
2. Asegúrese de que Python está en el PATH del sistema
3. Si es necesario, edite `install.bat` y especifique la ruta completa de Python

### "No se encontró el archivo solve_from_context.py"

**Problema:** Los scripts de resolución no se encuentran en la ubicación esperada.

**Solución:**

1. Asegúrese de ejecutar el instalador desde la carpeta `context_menu/`
2. Verifique que todos los archivos `.py` existen en esta carpeta
3. No mueva el proyecto después de la instalación

### "El menú no aparece al hacer clic derecho"

**Problema:** No se ve la opción en el menú contextual.

**Solución:**

1. Verifique que ejecutó el instalador **como administrador**
2. Reinicie el Explorador de Windows:
   - Presione Ctrl+Shift+Esc
   - Busque "Windows Explorer"
   - Haga clic derecho → Reiniciar
3. Verifique las entradas del registro:
   - Ejecute `regedit`
   - Navegue a `HKEY_CLASSES_ROOT\txtfile\shell`
   - Debe existir una clave `SimplexSolver`

### "Error al resolver el problema"

**Problema:** El solver genera un error al procesar el archivo.

**Solución:**

1. Verifique que el formato del archivo `.txt` sea correcto
2. Compruebe que todas las dependencias están instaladas:
   ```bash
   pip list | findstr "numpy tabulate psutil reportlab"
   ```
3. Revise que no haya errores de sintaxis en el archivo
4. Consulte los ejemplos en la carpeta `ejemplos/`

### "Ventana se cierra inmediatamente"

**Problema:** La ventana de consola se cierra antes de poder ver el resultado.

**Solución:**

- Los scripts están configurados para esperar a que presione Enter antes de cerrar
- Si se cierra inmediatamente, hay un error en el archivo de entrada
- Ejecute el script manualmente desde cmd para ver el error completo:
  ```bash
  python solve_from_context.py ruta\al\archivo.txt
  ```

### "Resolver con IA no funciona"

**Problema:** La opción de IA no aparece o genera errores.

**Solución:**

1. Verifique que Ollama está instalado y corriendo:
   ```bash
   ollama list
   ```
2. Asegúrese de tener un modelo instalado:
   ```bash
   ollama pull llama3.1:8b
   ```
3. Verifique que el servicio de Ollama está activo:
   - El servicio debe estar escuchando en `http://localhost:11434`

## Requisitos

### Requisitos Mínimos

- **Sistema Operativo:** Windows 10 o superior
- **Python:** 3.8 o superior
- **Permisos:** Administrador (solo para instalación)
- **Dependencias Python:**
  - numpy >= 1.24.0
  - psutil >= 5.9.0
  - tabulate >= 0.9.0
  - requests >= 2.31.0
  - reportlab >= 4.0.0

### Requisitos Opcionales (para IA)

- **Ollama:** Descargable desde https://ollama.ai/download
- **Modelos de IA:** Al menos un modelo de lenguaje instalado (recomendado: llama3.1:8b)
- **RAM:** 8 GB mínimo para modelos de IA
- **Espacio en disco:** 5-10 GB para modelos

## Archivos del Registro de Windows

La instalación crea las siguientes entradas en el registro:

**Para el modo tradicional:**

```
HKEY_CLASSES_ROOT\txtfile\shell\SimplexSolver
HKEY_CLASSES_ROOT\txtfile\shell\SimplexSolver\command
```

**Para el modo IA:**

```
HKEY_CLASSES_ROOT\txtfile\shell\SimplexSolverAI
HKEY_CLASSES_ROOT\txtfile\shell\SimplexSolverAI\command
```

Estas entradas apuntan a los scripts `.bat` en esta carpeta, que a su vez ejecutan los scripts Python correspondientes.

## Personalización

### Cambiar el Texto del Menú

Para cambiar el texto que aparece en el menú contextual:

1. Abra `install.bat` con un editor de texto
2. Localice la línea:
   ```batch
   reg add "HKEY_CLASSES_ROOT\txtfile\shell\SimplexSolver" /ve /d "Resolver con Simplex Solver" /f
   ```
3. Modifique el texto entre comillas
4. Ejecute `reinstall.bat` como administrador

### Agregar Icono al Menú

Para agregar un icono personalizado:

1. Coloque un archivo `.ico` en esta carpeta
2. Edite `install.bat` y agregue después de crear la clave:
   ```batch
   reg add "HKEY_CLASSES_ROOT\txtfile\shell\SimplexSolver" /v Icon /d "%~dp0icono.ico" /f
   ```
3. Ejecute `reinstall.bat` como administrador

## Seguridad

**Nota importante sobre permisos de administrador:**

La instalación requiere permisos de administrador porque modifica el registro de Windows (específicamente `HKEY_CLASSES_ROOT`). Esta es una ubicación protegida del sistema que solo puede ser modificada con privilegios elevados.

**¿Por qué es seguro?**

- El instalador solo crea/elimina entradas en `txtfile\shell`
- No modifica archivos del sistema
- No instala servicios en segundo plano
- Los scripts `.bat` son de código abierto y verificables

## Referencias

- **Documentación completa:** Ver `GUIA_USUARIO.md` en la raíz del proyecto
- **Guía del desarrollador:** Ver `GUIA_DESARROLLADOR.md`
- **Ejemplos de problemas:** Ver carpeta `ejemplos/`
- **Reportar problemas:** https://github.com/frangcisneros/simplex-project/issues

---

**Última actualización:** Noviembre 2025  
**Versión:** 3.1
