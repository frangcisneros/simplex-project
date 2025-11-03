# Guía Rápida de Construcción del Instalador

## 🎯 Objetivo

Crear ejecutables distribuibles del Simplex Solver con un instalador interactivo.

## 📋 Pre-requisitos

1. Python 3.8 o superior
2. Todas las dependencias instaladas:
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-build.txt
   ```

## 🚀 Pasos de Construcción

### 1. Probar el Instalador Interactivo

Antes de compilar, prueba el instalador en modo Python:

```bash
python test_installer.py
```

Esto mostrará:

- Capacidades de tu sistema
- Modelos recomendados
- Verificación de componentes

Si todo está OK, ejecuta el instalador en modo de prueba:

```bash
python installer.py
```

### 2. Construir los Ejecutables

Ejecuta el script de construcción:

```bash
python build_installer.py
```

Este script:

1. ✓ Verifica PyInstaller
2. ✓ Limpia builds anteriores
3. ✓ Crea archivos .spec para ambos ejecutables
4. ✓ Compila SimplexInstaller.exe
5. ✓ Compila SimplexSolver.exe
6. ✓ Crea paquete de distribución completo

### 3. Resultado

Después de la compilación, encontrarás:

```
dist/
└── SimplexSolver/
    ├── SimplexInstaller.exe  (Instalador interactivo)
    ├── SimplexSolver.exe     (Solver principal)
    ├── INSTALACION.txt       (Instrucciones)
    ├── README.md
    ├── requirements.txt
    ├── ejemplos/
    │   └── ... (archivos de ejemplo)
    └── docs/
        └── ... (documentación)
```

## 🧪 Probar los Ejecutables

### Probar el Instalador

```bash
cd dist\SimplexSolver
.\SimplexInstaller.exe
```

Verifica que:

- ✓ Se muestre la interfaz correctamente
- ✓ Analice el sistema
- ✓ Muestre recomendaciones apropiadas
- ✓ Permita seleccionar componentes

### Probar el Solver

```bash
cd dist\SimplexSolver
.\SimplexSolver.exe --help
.\SimplexSolver.exe --interactive
.\SimplexSolver.exe ejemplos\ejemplo_maximizacion.txt
```

## 📦 Distribuir

### Opción 1: Carpeta Completa

Comparte la carpeta `dist/SimplexSolver/` completa.

Usuarios deben:

1. Descomprimir
2. Ejecutar `SimplexInstaller.exe`
3. Seguir instrucciones

### Opción 2: Crear ZIP

```bash
# PowerShell
Compress-Archive -Path "dist\SimplexSolver" -DestinationPath "SimplexSolver-v1.0.zip"
```

### Opción 3: Crear Instalador MSI (Avanzado)

Para crear un instalador MSI profesional, puedes usar WiX Toolset:

```bash
# Instalar WiX (requiere descarga separada)
# Crear archivo .wxs para configuración
# Compilar MSI
```

## 🐛 Solución de Problemas

### Error: "PyInstaller no encontrado"

```bash
pip install pyinstaller
```

### Error: "No module named 'numpy'"

```bash
pip install -r requirements.txt
```

### Ejecutable muy grande

El tamaño normal es 30-50 MB. Si es mucho mayor:

- Verifica que no se incluyan librerías innecesarias
- Revisa los `excludes` en los archivos .spec
- Usa UPX (ya habilitado por defecto)

### Error al ejecutar el .exe

1. Prueba desde cmd/PowerShell (no doble-click)
2. Verifica que no haya antivirus bloqueando
3. Revisa los logs en la consola

### El instalador no detecta capacidades

Asegúrate de que `psutil` esté correctamente instalado:

```bash
python -c "import psutil; print(psutil.virtual_memory())"
```

## 📊 Tamaños Esperados

| Archivo                | Tamaño Aprox. |
| ---------------------- | ------------- |
| SimplexInstaller.exe   | 15-25 MB      |
| SimplexSolver.exe      | 20-35 MB      |
| Paquete completo (ZIP) | 40-70 MB      |

## 🔄 Actualizar el Build

Si modificas el código:

1. Limpia builds anteriores:

   ```bash
   rmdir /s dist
   rmdir /s build
   del *.spec
   ```

2. Vuelve a compilar:
   ```bash
   python build_installer.py
   ```

## 📝 Personalización

### Cambiar el ícono del ejecutable

1. Crea o consigue un archivo .ico
2. En `build_installer.py`, modifica las líneas:
   ```python
   icon=None,
   ```
   Por:
   ```python
   icon='path/to/icon.ico',
   ```

### Agregar más archivos al paquete

En `build_installer.py`, modifica:

```python
files_to_copy = [
    ("README.md", "README.md"),
    ("tu_archivo.txt", "tu_archivo.txt"),  # ← Agregar aquí
]
```

### Cambiar configuración de PyInstaller

Edita los archivos `.spec` generados o modifica las funciones:

- `create_installer_spec()` para el instalador
- `create_solver_spec()` para el solver

## ✅ Checklist Final

Antes de distribuir:

- [ ] Probado el instalador en modo Python
- [ ] Compilados ambos ejecutables sin errores
- [ ] Probado SimplexInstaller.exe
- [ ] Probado SimplexSolver.exe
- [ ] Verificadas las recomendaciones de modelos
- [ ] Probado en un sistema limpio (sin Python)
- [ ] Creado paquete ZIP
- [ ] Documentación actualizada
- [ ] README con instrucciones claras

## 🎓 Recursos Adicionales

- [Documentación PyInstaller](https://pyinstaller.readthedocs.io/)
- [Guía del Instalador](docs/INSTALLER_README.md)
- [Sistema de IA](docs/GUIA_IA.md)
- [Menú Contextual](docs/CONTEXT_MENU_GUIDE.md)

## 📞 Soporte

Si tienes problemas durante la compilación:

1. Revisa los errores en la consola
2. Verifica que todas las dependencias estén instaladas
3. Consulta la documentación de PyInstaller
4. Abre un issue en GitHub con:
   - Versión de Python
   - Sistema operativo
   - Mensaje de error completo
   - Salida de `pip list`
