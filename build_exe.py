#!/usr/bin/env python3
import os
import sys
import subprocess
import shutil
from pathlib import Path


def install_pyinstaller():
    print("Verificando PyInstaller...")
    try:
        import PyInstaller

        print("PyInstaller ya está instalado")
        return True
    except ImportError:
        print("PyInstaller no encontrado. Instalando...")
        try:
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", "pyinstaller"]
            )
            print("PyInstaller instalado correctamente")
            return True
        except subprocess.CalledProcessError:
            print("Error al instalar PyInstaller")
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


def create_spec_file():
    """Crea el archivo .spec para PyInstaller con configuración personalizada."""
    spec_content = """# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['simplex.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=['numpy', 'numpy.core._methods', 'numpy.lib.format'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['test', 'tests', 'unittest', 'doctest', 'pdb', 'pstats', 'tkinter'],
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

    print("Archivo .spec creado: simplex_solver.spec")


def build_executable():
    """Construye el archivo ejecutable usando PyInstaller."""
    print("\nIniciando construcción del ejecutable...")

    try:
        # Usar el archivo .spec para mayor control
        cmd = [sys.executable, "-m", "PyInstaller", "simplex_solver.spec", "--clean"]

        print(f"Ejecutando: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            print("Ejecutable creado exitosamente")
            return True
        else:
            print("Error durante la construcción:")
            print(result.stderr)
            return False

    except Exception as e:
        print(f"Error: {e}")
        return False


def verify_executable():
    """Verifica que el ejecutable se haya creado correctamente."""
    exe_path = Path("dist/SimplexSolver.exe")

    if exe_path.exists():
        size_mb = exe_path.stat().st_size / (1024 * 1024)
        print(f"✓ Ejecutable creado: {exe_path}")
        print(f"  Tamaño: {size_mb:.1f} MB")

        # Probar que el ejecutable funcione
        print("\nProbando el ejecutable...")
        try:
            result = subprocess.run(
                [str(exe_path), "--help"], capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                print("✓ El ejecutable funciona correctamente")
                return True
            else:
                print("✗ El ejecutable no funciona correctamente")
                print(result.stderr)
                return False
        except subprocess.TimeoutExpired:
            print("✗ Timeout al probar el ejecutable")
            return False
        except Exception as e:
            print(f"✗ Error al probar el ejecutable: {e}")
            return False
    else:
        print("✗ No se encontró el ejecutable en dist/SimplexSolver.exe")
        return False


def main():
    """Función principal del script de construcción."""
    print("=" * 60)
    print("SIMPLEX SOLVER - GENERADOR DE EJECUTABLE")
    print("=" * 60)

    # Verificar que estamos en el directorio correcto
    if not os.path.exists("simplex.py"):
        print("✗ Error: No se encontró simplex.py en el directorio actual")
        print(
            "  Asegúrate de ejecutar este script desde el directorio raíz del proyecto"
        )
        sys.exit(1)

    # Paso 1: Instalar PyInstaller
    if not install_pyinstaller():
        sys.exit(1)

    # Paso 2: Limpiar directorios anteriores
    clean_build_directories()

    # Paso 3: Crear archivo .spec
    create_spec_file()

    # Paso 4: Construir ejecutable
    if not build_executable():
        sys.exit(1)

    # Paso 5: Verificar el ejecutable
    if not verify_executable():
        sys.exit(1)

    print("\n" + "=" * 60)
    print("✓ PROCESO COMPLETADO EXITOSAMENTE")
    print("=" * 60)
    print("El ejecutable se encuentra en: dist/SimplexSolver.exe")
    print("\nPuedes probarlo con:")
    print("  .\\dist\\SimplexSolver.exe --help")
    print("  .\\dist\\SimplexSolver.exe --interactive")
    print("  .\\dist\\SimplexSolver.exe ejemplos\\maximizar_basico.txt")


if __name__ == "__main__":
    main()
