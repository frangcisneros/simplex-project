#!/usr/bin/env python3
"""
Script de construcción del instalador ejecutable del Simplex Solver.
Genera UN SOLO ARCHIVO .EXE que es el instalador interactivo.
"""
import os
import sys
import subprocess
import shutil
from pathlib import Path


def install_pyinstaller():
    """Instala PyInstaller si no está disponible."""
    print("Verificando PyInstaller...")
    try:
        import PyInstaller

        print("✓ PyInstaller ya está instalado")
        return True
    except ImportError:
        print("PyInstaller no encontrado. Instalando...")
        try:
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", "pyinstaller"]
            )
            print("✓ PyInstaller instalado correctamente")
            return True
        except subprocess.CalledProcessError:
            print("✗ Error al instalar PyInstaller")
            return False


def clean_build_directories():
    """Limpia directorios de compilación anteriores."""
    dirs_to_clean = ["build", "dist", "__pycache__"]

    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            print(f"Limpiando directorio: {dir_name}")
            shutil.rmtree(dir_name)

    # Limpiar archivos .spec
    for spec_file in Path(".").glob("*.spec"):
        print(f"Eliminando archivo spec: {spec_file}")
        spec_file.unlink()


def create_installer_spec():
    """Crea el archivo .spec para el instalador con todas las dependencias."""
    spec_content = """# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

# Datos a incluir en el instalador
added_files = [
    ('requirements.txt', '.'),
    ('context_menu', 'context_menu'),
    ('ejemplos', 'ejemplos'),
    ('docs', 'docs'),
    ('README.md', '.'),
]

a = Analysis(
    ['installer.py'],
    pathex=[],
    binaries=[],
    datas=added_files,
    hiddenimports=[
        'numpy', 
        'numpy.core._methods', 
        'numpy.lib.format',
        'psutil',
        'psutil._psutil_windows',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'test', 
        'tests', 
        'unittest', 
        'doctest', 
        'pdb', 
        'pstats', 
        'tkinter',
        'matplotlib',
        'PIL',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='SimplexInstaller',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    cofile=None,
    icon=None,
)
"""

    with open("simplex_installer.spec", "w", encoding="utf-8") as f:
        f.write(spec_content)

    print("✓ Archivo .spec creado: simplex_installer.spec")


def create_solver_spec():
    """Crea el archivo .spec para el solver principal."""
    spec_content = """# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

# Incluir todos los archivos necesarios
added_files = [
    ('ejemplos', 'ejemplos'),
    ('docs', 'docs'),
    ('README.md', '.'),
]

a = Analysis(
    ['simplex.py'],
    pathex=[],
    binaries=[],
    datas=added_files,
    hiddenimports=[
        'numpy', 
        'numpy.core._methods', 
        'numpy.lib.format',
        'psutil',
        'tabulate',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'test', 
        'tests', 
        'unittest', 
        'doctest', 
        'pdb', 
        'pstats', 
        'tkinter',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='SimplexSolver',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    cofile=None,
    icon=None,
)
"""

    with open("simplex_solver.spec", "w", encoding="utf-8") as f:
        f.write(spec_content)

    print("✓ Archivo .spec creado: simplex_solver.spec")


def build_executable(spec_file: str, name: str):
    """Construye un ejecutable usando PyInstaller."""
    print(f"\nConstruyendo {name}...")

    try:
        cmd = [sys.executable, "-m", "PyInstaller", spec_file, "--clean"]

        print(f"Ejecutando: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            print(f"✓ {name} creado exitosamente")
            return True
        else:
            print(f"✗ Error durante la construcción de {name}:")
            print(result.stderr)
            return False

    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def verify_executable(exe_path: Path, name: str):
    """Verifica que el ejecutable se haya creado correctamente."""
    if exe_path.exists():
        size_mb = exe_path.stat().st_size / (1024 * 1024)
        print(f"✓ {name} creado: {exe_path}")
        print(f"  Tamaño: {size_mb:.1f} MB")
        return True
    else:
        print(f"✗ No se encontró {name} en {exe_path}")
        return False


def create_distribution_package():
    """Crea un paquete de distribución completo."""
    print("\nCreando paquete de distribución...")

    dist_dir = Path("dist")
    package_dir = dist_dir / "SimplexSolver"

    if package_dir.exists():
        shutil.rmtree(package_dir)

    package_dir.mkdir(parents=True, exist_ok=True)

    # Copiar ejecutables
    installer_exe = dist_dir / "SimplexInstaller.exe"
    solver_exe = dist_dir / "SimplexSolver.exe"

    if installer_exe.exists():
        shutil.copy2(installer_exe, package_dir / "SimplexInstaller.exe")
        print(f"  ✓ Copiado: SimplexInstaller.exe")

    if solver_exe.exists():
        shutil.copy2(solver_exe, package_dir / "SimplexSolver.exe")
        print(f"  ✓ Copiado: SimplexSolver.exe")

    # Copiar archivos necesarios
    files_to_copy = [
        ("README.md", "README.md"),
        ("requirements.txt", "requirements.txt"),
        ("ejemplos", "ejemplos"),
        ("docs", "docs"),
    ]

    for src, dst in files_to_copy:
        src_path = Path(src)
        dst_path = package_dir / dst

        if src_path.exists():
            if src_path.is_file():
                shutil.copy2(src_path, dst_path)
            else:
                shutil.copytree(src_path, dst_path, dirs_exist_ok=True)
            print(f"  ✓ Copiado: {src}")

    # Crear archivo de instrucciones
    instructions = """SIMPLEX SOLVER - INSTRUCCIONES DE INSTALACIÓN
==============================================

INSTALACIÓN:
-----------
1. Ejecuta SimplexInstaller.exe
2. Sigue las instrucciones en pantalla
3. El instalador detectará automáticamente las capacidades de tu sistema
4. Elige los componentes que deseas instalar:
   - Ollama (motor de IA local)
   - Modelos de IA (recomendados según tu sistema)
   - Menú contextual de Windows

USO:
----
Después de la instalación:

1. Modo Interactivo:
   SimplexSolver.exe --interactive

2. Resolver un archivo:
   SimplexSolver.exe ejemplos\\ejemplo_maximizacion.txt

3. Modo IA (requiere Ollama instalado):
   SimplexSolver.exe --ai "tu problema en lenguaje natural"

4. Desde el explorador de Windows (si instalaste el menú contextual):
   Click derecho en un archivo .txt > Resolver con Simplex

DOCUMENTACIÓN:
--------------
- README.md: Guía completa del proyecto
- docs\\GUIA_IA.md: Guía del sistema de IA
- docs\\CONTEXT_MENU_GUIDE.md: Guía del menú contextual
- ejemplos\\: Problemas de ejemplo

SOPORTE:
--------
Para reportar problemas o sugerencias:
https://github.com/frangcisneros/simplex-project

"""

    instructions_file = package_dir / "INSTALACION.txt"
    instructions_file.write_text(instructions, encoding="utf-8")
    print(f"  ✓ Creado: INSTALACION.txt")

    print(f"\n✓ Paquete de distribución creado en: {package_dir}")
    return package_dir


def main():
    """Función principal del script de construcción."""
    print("=" * 70)
    print(" " * 15 + "SIMPLEX SOLVER - BUILD SYSTEM")
    print("=" * 70)

    # Verificar que estamos en el directorio correcto
    if not os.path.exists("simplex.py"):
        print("✗ Error: No se encontró simplex.py en el directorio actual")
        print(
            "  Asegúrate de ejecutar este script desde el directorio raíz del proyecto"
        )
        sys.exit(1)

    if not os.path.exists("installer.py"):
        print("✗ Error: No se encontró installer.py en el directorio actual")
        sys.exit(1)

    # Paso 1: Instalar PyInstaller
    if not install_pyinstaller():
        sys.exit(1)

    # Paso 2: Limpiar directorios anteriores
    clean_build_directories()

    # Paso 3: Crear archivos .spec
    print("\n--- Creando archivos de configuración ---")
    create_installer_spec()
    create_solver_spec()

    # Paso 4: Construir ejecutables
    print("\n--- Construyendo ejecutables ---")

    success = True

    # Construir instalador
    if not build_executable("simplex_installer.spec", "SimplexInstaller"):
        success = False
    else:
        verify_executable(Path("dist/SimplexInstaller.exe"), "SimplexInstaller")

    # Construir solver
    if not build_executable("simplex_solver.spec", "SimplexSolver"):
        success = False
    else:
        verify_executable(Path("dist/SimplexSolver.exe"), "SimplexSolver")

    if not success:
        print("\n✗ Algunas compilaciones fallaron")
        sys.exit(1)

    # Paso 5: Crear paquete de distribución
    package_dir = create_distribution_package()

    # Resumen final
    print("\n" + "=" * 70)
    print("✓ PROCESO COMPLETADO EXITOSAMENTE")
    print("=" * 70)
    print(f"\nPaquete de distribución: {package_dir}")
    print("\nArchivos generados:")
    print(f"  • SimplexInstaller.exe - Instalador interactivo")
    print(f"  • SimplexSolver.exe - Aplicación principal")
    print(f"  • INSTALACION.txt - Instrucciones")
    print(f"  • Ejemplos y documentación incluidos")

    print("\nPróximos pasos:")
    print("  1. Prueba el instalador: .\\dist\\SimplexSolver\\SimplexInstaller.exe")
    print("  2. Distribuye la carpeta completa: dist\\SimplexSolver\\")
    print("  3. O crea un archivo ZIP para distribuir más fácilmente")


if __name__ == "__main__":
    main()
