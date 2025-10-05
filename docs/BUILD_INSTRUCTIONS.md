# Simplex Solver - Generación de Ejecutable

Este documento describe cómo generar un archivo .exe del Simplex Solver.

## Método Automático (Recomendado)

Usa el script automatizado `build_exe.py`:

```bash
python build_exe.py
```

Este script:

1. Instala PyInstaller automáticamente si es necesario
2. Limpia compilaciones anteriores
3. Crea un archivo .spec optimizado
4. Genera el ejecutable
5. Verifica que funcione correctamente

## Método Manual

Si prefieres hacerlo paso a paso:

### 1. Instalar PyInstaller

```bash
pip install -r requirements-build.txt
```

### 2. Generar el ejecutable

```bash
pyinstaller --onefile --name SimplexSolver --exclude-module test --exclude-module tests --exclude-module unittest --exclude-module doctest --exclude-module tkinter --console simplex.py
```

### 3. Opciones adicionales de PyInstaller

- `--onefile`: Crea un solo archivo ejecutable
- `--name SimplexSolver`: Nombre del ejecutable
- `--exclude-module`: Excluye módulos innecesarios
- `--console`: Mantiene la ventana de consola (necesario para input interactivo)
- `--noconsole`: Oculta la consola (solo si no necesitas input del usuario)
- `--icon=icon.ico`: Agrega un icono personalizado

## Archivos Incluidos en el .exe

El ejecutable incluye solo:

- `simplex.py` (punto de entrada)
- `src/solver.py` (lógica principal)
- Dependencias necesarias (numpy)

**Excluye automáticamente:**

- Archivos de documentación (`docs/`)
- Archivos de ejemplo (`ejemplos/`)
- Tests
- Módulos innecesarios del sistema

## Uso del Ejecutable

Una vez generado, puedes usar el ejecutable de estas formas:

```bash
# Modo interactivo
SimplexSolver.exe --interactive

# Desde archivo
SimplexSolver.exe ejemplos/maximizar_basico.txt

# Ver ayuda
SimplexSolver.exe --help
```

## Tamaño del Ejecutable

El ejecutable típicamente tiene un tamaño de:

- **30-50 MB**: Incluye Python runtime y numpy
- Para reducir el tamaño, considera usar `--exclude-module` con más módulos

## Troubleshooting

### Error: "No module named numpy"

- Asegúrate de que numpy esté instalado: `pip install numpy`

### Ejecutable muy grande

- Usa más exclusiones: `--exclude-module matplotlib --exclude-module scipy`

### Error de permisos

- Ejecuta como administrador o desde un directorio con permisos de escritura

### Antivirus detecta como amenaza

- Es común con ejecutables de PyInstaller
- Agrega excepción en tu antivirus
- Considera firmar el ejecutable digitalmente para distribución
