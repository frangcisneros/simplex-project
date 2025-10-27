# Guía de Instalación del Menú Contextual

Esta guía te ayudará a instalar el Simplex Solver en el menú contextual de Windows para resolver problemas directamente haciendo clic derecho en archivos `.txt`.

## 📋 Requisitos Previos

- **Windows** (probado en Windows 10/11)
- **Python 3.8+** instalado en tu sistema
- **Permisos de Administrador** para modificar el registro de Windows
- Todas las dependencias de Simplex Solver instaladas (`pip install -r requirements.txt`)

## 🚀 Instalación

### Método 1: Instalación Automática (Recomendado)

1. **Navega a la carpeta** `context_menu/` del proyecto
2. **Localiza el archivo** `install.bat`
3. **Haz clic derecho** sobre `install.bat`
4. **Selecciona** "Ejecutar como administrador"
5. **Sigue las instrucciones** en pantalla

El instalador:

- ✅ Detectará automáticamente tu instalación de Python
- ✅ Verificará que el script de Python existe
- ✅ Agregará la entrada al registro de Windows
- ✅ Configurará el comando correcto

### Método 2: Instalación Manual

Si prefieres hacerlo manualmente o el script automático no funciona:

1. **Abre el Editor del Registro** (Win+R, escribe `regedit`, Enter)
2. **Navega a:** `HKEY_CLASSES_ROOT\txtfile\shell`
3. **Crea una nueva clave** llamada `SimplexSolver`
4. En la clave `SimplexSolver`:
   - Modifica el valor `(Predeterminado)` a: `Resolver con Simplex Solver`
5. **Crea una subclave** dentro de `SimplexSolver` llamada `command`
6. En la clave `command`:
   - Modifica el valor `(Predeterminado)` a:
   ```
   "C:\ruta\a\python.exe" "C:\ruta\al\proyecto\context_menu\solve_from_context.py" "%1"
   ```
   _(Reemplaza las rutas con tus rutas reales)_

## 🎯 Uso

Una vez instalado:

1. **Crea o abre** un archivo `.txt` con un problema de Simplex (ver carpeta [`ejemplos/`](../ejemplos/))
2. **Haz clic derecho** sobre el archivo
3. **Selecciona** "Resolver con Simplex Solver" del menú contextual
4. **Se abrirá** una ventana de consola mostrando:
   - El problema parseado
   - El proceso de resolución
   - Los resultados
   - Opción para generar un PDF

**💡 Consejo**: Usa los archivos de ejemplo en la carpeta `ejemplos/` para probar la funcionalidad.

## 📝 Formato del Archivo de Entrada

Tu archivo `.txt` debe seguir este formato:

```
MAXIMIZE
3 2
SUBJECT TO
2 1 <= 18
2 3 <= 42
3 1 <= 24
```

O para minimización:

```
MINIMIZE
-3 -2
SUBJECT TO
2 1 >= 18
2 3 >= 42
3 1 = 24
```

**Estructura:**

1. Primera línea: `MAXIMIZE` o `MINIMIZE`
2. Segunda línea: Coeficientes de la función objetivo (separados por espacios)
3. Tercera línea: `SUBJECT TO`
4. Siguientes líneas: Restricciones en formato `a1 a2 ... an <= b` (o `>=` o `=`)

## 🗑️ Desinstalación

Para eliminar el menú contextual:

1. **Navega a la carpeta** `context_menu/`
2. **Localiza** `uninstall.bat`
3. **Haz clic derecho** y selecciona "Ejecutar como administrador"
4. **Confirma** la desinstalación

Alternativamente, elimina manualmente la clave del registro:

- `HKEY_CLASSES_ROOT\txtfile\shell\SimplexSolver`

## 🐛 Solución de Problemas

### "No se pudo encontrar Python"

- Verifica que Python esté instalado: `python --version` en cmd
- Asegúrate de que Python esté en el PATH del sistema
- Edita `install_context_menu.bat` y agrega la ruta correcta de Python

### "No se encontró el archivo solve_from_context.py"

- Asegúrate de ejecutar el instalador desde la carpeta `context_menu/`
- Verifica que `solve_from_context.py` existe en la carpeta `context_menu/`

### "El menú no aparece al hacer clic derecho"

- Verifica que ejecutaste el instalador como administrador
- Reinicia el explorador de archivos (Ctrl+Shift+Esc → Buscar "Windows Explorer" → Reiniciar)
- Verifica que la entrada existe en el registro

### "Error al resolver el problema"

- Verifica que el formato del archivo `.txt` sea correcto
- Comprueba que todas las dependencias estén instaladas
- Revisa que no haya errores de sintaxis en el archivo

### "Ventana se cierra inmediatamente"

- Esto es normal, la ventana permanece abierta hasta que presiones Enter
- Si se cierra antes, puede haber un error en el archivo de entrada

## 🎨 Personalización

### Cambiar el nombre del menú

Edita la línea en `context_menu/install.bat`:

```batch
reg add "HKEY_CLASSES_ROOT\txtfile\shell\SimplexSolver" /ve /d "Tu Nombre Personalizado" /f
```

### Agregar un icono personalizado

1. Coloca un archivo `.ico` en la carpeta `context_menu/` llamado `simplex_icon.ico`
2. El instalador lo detectará automáticamente

### Agregar a otros tipos de archivo

Modifica el instalador para incluir otros tipos:

- `.dat`: `HKEY_CLASSES_ROOT\.dat`
- `.lp`: Crea una extensión personalizada

## 📚 Recursos Adicionales

- [Documentación del Proyecto](../README.md)
- [Ejemplos de Archivos .txt](../ejemplos/)
- [Arquitectura del Sistema](../ARQUITECTURA.md)
- [Guía de IA](../GUIA_IA.md)

## 🤝 Contribuciones

Si encuentras problemas o tienes sugerencias para mejorar la integración con Windows:

1. Abre un issue en GitHub
2. Describe el problema o mejora
3. Incluye tu versión de Windows y Python

## ⚖️ Licencia

Este componente está sujeto a la misma licencia que el proyecto principal Simplex Solver.

---

**Nota de Seguridad:** La modificación del registro de Windows requiere permisos de administrador. Siempre revisa los scripts antes de ejecutarlos con privilegios elevados.
