# Simplex Solver - Build Instructions

Este documento describe cómo generar los ejecutables del Simplex Solver.

## 🚀 Método Recomendado: Script Unificado

Usa el nuevo script consolidado `tools/build.py` que sigue principios SOLID:

```bash
# Generar el instalador
python tools/build.py --installer

# Generar el solver
python tools/build.py --solver

# Generar ambos
python tools/build.py --all

# Limpiar archivos de compilación
python tools/build.py --clean
```

## 📦 Scripts Generados

El sistema de build genera:

1. **SimplexInstaller.exe** - Instalador interactivo con:

   - Detección automática de capacidades del sistema
   - Instalación opcional de Ollama y modelos de IA
   - Configuración del menú contextual de Windows
   - ~40-50 MB

2. **SimplexSolver.exe** - Solver standalone con:
   - Modo interactivo
   - Resolución desde archivos
   - Generación de reportes PDF
   - ~30-40 MB

## ⚙️ Método Manual (Para desarrollo avanzado)

Si prefieres hacerlo paso a paso:

### 1. Instalar PyInstaller

```bash
pip install -r requirements-build.txt
```

### 2. Generar archivos .spec personalizados

El sistema de build ahora genera automáticamente archivos `.spec` optimizados.
Puedes encontrar ejemplos en el código de `tools/build.py`.

### 3. Compilar con PyInstaller

```bash
pyinstaller SimplexInstaller.spec --clean
# o
pyinstaller SimplexSolver.spec --clean
```

## 📋 Archivos Incluidos/Excluidos

### Instalador (SimplexInstaller.exe)

**Incluye:**

- `installer.py` (punto de entrada)
- `simplex_solver/` (todo el paquete)
- `context_menu/` (scripts del menú contextual)
- `docs/` (documentación)
- `requirements.txt`
- `README.md`

**Excluye:**

- Tests
- `tkinter`, `matplotlib`, `PIL`
- Módulos de desarrollo

### Solver (SimplexSolver.exe)

**Incluye:**

- `simplex.py` (punto de entrada)
- `simplex_solver/` (paquete completo)
- Documentación básica

**Excluye:**

- Context menu (solo en instalador)
- Tests y herramientas de desarrollo

## 🎯 Uso de los Ejecutables

### SimplexInstaller.exe

```bash
# Ejecutar instalador interactivo
.\SimplexInstaller.exe

# El instalador guiará el proceso:
# 1. Detecta capacidades del sistema
# 2. Ofrece instalar Ollama (opcional)
# 3. Permite elegir modelos de IA
# 4. Configura menú contextual de Windows
```

### SimplexSolver.exe

```bash
# Modo interactivo
.\SimplexSolver.exe --interactive

# Desde archivo
.\SimplexSolver.exe ejemplos/ejemplo_maximizacion.txt

# Ver historial
.\SimplexSolver.exe --history

# Ver ayuda
.\SimplexSolver.exe --help
```

## 📊 Tamaño de los Ejecutables

El tamaño típico de los ejecutables:

- **SimplexInstaller.exe**: ~40-50 MB

  - Incluye Python runtime
  - Sistema completo de instalación
  - Todas las dependencias (numpy, psutil, tabulate)

- **SimplexSolver.exe**: ~30-40 MB
  - Incluye Python runtime
  - Solver completo
  - Sistema de logs e historial

### Para reducir el tamaño:

- Usa más exclusiones en el archivo `.spec`
- Considera UPX compression (ya habilitado por defecto)
- Excluye módulos opcionales no utilizados

## 🔧 Troubleshooting

### Error: "PyInstaller not found"

El sistema lo instala automáticamente, pero si falla:

```bash
pip install pyinstaller
```

### Error: "No module named numpy"

Instala las dependencias:

```bash
pip install -r requirements.txt
```

### Ejecutable muy grande

1. Verifica las exclusiones en `tools/build.py`
2. Considera agregar más módulos a la lista de exclusión
3. UPX está habilitado por defecto para comprimir

### Error de permisos

- Ejecuta desde un directorio con permisos de escritura
- Para el instalador, se recomienda ejecutar como administrador

### Antivirus bloquea el ejecutable

- Común con ejecutables de PyInstaller (falsos positivos)
- Agrega una excepción en tu antivirus
- Firma el ejecutable con un certificado digital (producción)

### Build falla en Windows

1. Verifica que Python esté en el PATH
2. Asegúrate de tener permisos de escritura en `dist/` y `build/`
3. Cierra el ejecutable si está corriendo
4. Ejecuta `python tools/build.py --clean` primero

## 📝 Scripts Legacy (Deprecated)

Los siguientes scripts están **obsoletos** y se mantienen solo para compatibilidad:

- ❌ `build_exe.py` → Usar `tools/build.py --solver`
- ❌ `tools/build_installer.py` → Usar `tools/build.py --installer`

El nuevo sistema unificado `tools/build.py` combina toda la funcionalidad
y es más fácil de mantener siguiendo principios SOLID.

## 🚀 Workflow Recomendado

```bash
# 1. Limpiar builds anteriores
python tools/build.py --clean

# 2. Generar ambos ejecutables
python tools/build.py --all

# 3. Los ejecutables estarán en dist/
#    - dist/SimplexInstaller.exe
#    - dist/SimplexSolver.exe

# 4. Probar el instalador
cd dist
.\SimplexInstaller.exe

# 5. Probar el solver
.\SimplexSolver.exe --interactive
```

## 📚 Referencias

- [PyInstaller Documentation](https://pyinstaller.org/)
- [Tools README](../tools/README.md) - Documentación de herramientas
- [Installer Guide](INSTALLER_README.md) - Guía del instalador
- [Project README](../README.md) - Documentación principal
- Considera firmar el ejecutable digitalmente para distribución
