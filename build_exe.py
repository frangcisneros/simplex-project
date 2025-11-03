#!/usr/bin/env python3#!/usr/bin/env python3#!/usr/bin/env python3

"""

Script simple para generar SimplexInstaller.exe""""""

Ejecuta: python build_exe.py

"""Script para generar el INSTALADOR como un único archivo .EXEScript para generar el INSTALADOR como un único archivo .EXE

import subprocess

import sysEjecuta: python build_exe.pyEjecuta: python build_exe.py

from pathlib import Path

Resultado: dist/SimplexInstaller.exe (archivo único standalone)Resultado: dist/SimplexInstaller.exe (archivo único standalone)

def main():

    print("=" * 70)""""""

    print("GENERANDO SimplexInstaller.exe")

    print("=" * 70)import osimport os

    

    # Verificar que installer.py existeimport sysimport sys

    if not Path("installer.py").exists():

        print("ERROR: No se encontró installer.py")import subprocessimport subprocess

        return 1

    import shutilimport shutil

    # Comando PyInstaller

    cmd = [from pathlib import Pathfrom pathlib import Path

        sys.executable, "-m", "PyInstaller",

        "--onefile",

        "--console",

        "--name=SimplexInstaller",

        "--clean",

        "--hidden-import=psutil",def install_pyinstaller():def install_pyinstaller():

        "--hidden-import=psutil._psutil_windows",

        "--hidden-import=numpy",    """Instala PyInstaller si no está disponible."""    """Instala PyInstaller si no está disponible."""

        "--add-data=requirements.txt;.",

        "--add-data=context_menu;context_menu",    print("=" * 70)    print("=" * 70)

        "--add-data=ejemplos;ejemplos",

        "--add-data=docs;docs",    print("Verificando PyInstaller...")    print("Verificando PyInstaller...")

        "--add-data=README.md;.",

        "--add-data=src;src",    print("=" * 70)    print("=" * 70)

        "installer.py"

    ]    try:    try:

    

    print("\nCompilando... (puede tardar varios minutos)")        import PyInstaller        import PyInstaller

    result = subprocess.run(cmd)

            print("✓ PyInstaller ya está instalado")        print("✓ PyInstaller ya está instalado")

    if result.returncode == 0:

        exe_path = Path("dist/SimplexInstaller.exe")        return True        return True

        if exe_path.exists():

            size_mb = exe_path.stat().st_size / (1024 * 1024)    except ImportError:    except ImportError:

            print("\n" + "=" * 70)

            print("¡ÉXITO!")        print("PyInstaller no encontrado. Instalando...")        print("PyInstaller no encontrado. Instalando...")

            print("=" * 70)

            print(f"Archivo: dist/SimplexInstaller.exe")        try:        try:

            print(f"Tamaño: {size_mb:.1f} MB")

            print("\nPrueba el instalador con:")            subprocess.check_call(            subprocess.check_call(

            print("  .\\dist\\SimplexInstaller.exe")

            return 0                [sys.executable, "-m", "pip", "install", "pyinstaller"]                [sys.executable, "-m", "pip", "install", "pyinstaller"]

    

    print("\nERROR: La compilación falló")            )            )

    return 1

            print("✓ PyInstaller instalado correctamente")            print("✓ PyInstaller instalado correctamente")

if __name__ == "__main__":

    sys.exit(main())            return True            return True


        except subprocess.CalledProcessError:        except subprocess.CalledProcessError:

            print("✗ Error al instalar PyInstaller")            print("✗ Error al instalar PyInstaller")

            return False            return False





def clean_build_directories():def clean_build_directories():

    """Limpia directorios de compilación anteriores."""    """Limpia directorios de compilación anteriores."""

    print("\n" + "=" * 70)    print("\n" + "=" * 70)

    print("Limpiando builds anteriores...")    print("Limpiando builds anteriores...")

    print("=" * 70)    print("=" * 70)

        

    dirs_to_clean = ["build", "dist", "__pycache__"]    dirs_to_clean = ["build", "dist", "__pycache__"]

        

    for dir_name in dirs_to_clean:    for dir_name in dirs_to_clean:

        if os.path.exists(dir_name):        if os.path.exists(dir_name):

            print(f"  Limpiando: {dir_name}")            print(f"  Limpiando: {dir_name}")

            shutil.rmtree(dir_name)            shutil.rmtree(dir_name)

        

    # Limpiar archivos .spec    # Limpiar archivos .spec

    for spec_file in Path(".").glob("*.spec"):    for spec_file in Path(".").glob("*.spec"):

        print(f"  Eliminando: {spec_file}")        print(f"  Eliminando: {spec_file}")

        spec_file.unlink()        spec_file.unlink()

        

    print("✓ Limpieza completada")    print("✓ Limpieza completada")





def build_installer():def build_installer():

    """Construye el instalador como un único archivo .exe"""    """Construye el instalador como un único archivo .exe"""

    print("\n" + "=" * 70)    print("\n" + "=" * 70)

    print("Construyendo SimplexInstaller.exe...")    print("Construyendo SimplexInstaller.exe...")

    print("=" * 70)    print("=" * 70)

        

    # Comando PyInstaller con todas las opciones en línea    # Comando PyInstaller con todas las opciones en línea

    cmd = [    cmd = [

        sys.executable, "-m", "PyInstaller",        sys.executable, "-m", "PyInstaller",

        "--onefile",                          # UN SOLO ARCHIVO .exe        "--onefile",                          # UN SOLO ARCHIVO .exe

        "--console",                          # Ventana de consola        "--console",                          # Ventana de consola

        "--name=SimplexInstaller",            # Nombre del ejecutable        "--name=SimplexInstaller",            # Nombre del ejecutable

        "--clean",                            # Limpiar cache        "--clean",                            # Limpiar cache

                

        # Incluir módulos necesarios        # Incluir módulos necesarios

        "--hidden-import=psutil",        "--hidden-import=psutil",

        "--hidden-import=psutil._psutil_windows",        "--hidden-import=psutil._psutil_windows",

        "--hidden-import=numpy",        "--hidden-import=numpy",

        "--hidden-import=numpy.core._methods",        "--hidden-import=numpy.core._methods",

        "--hidden-import=numpy.lib.format",        "--hidden-import=numpy.lib.format",

                

        # Agregar archivos de datos (usar ; en Windows)        # Agregar archivos de datos (usar ; en Windows)

        "--add-data=requirements.txt;.",        "--add-data=requirements.txt;.",

        "--add-data=context_menu;context_menu",        "--add-data=context_menu;context_menu",

        "--add-data=ejemplos;ejemplos",        "--add-data=ejemplos;ejemplos",

        "--add-data=docs;docs",        "--add-data=docs;docs",

        "--add-data=README.md;.",        "--add-data=README.md;.",

        "--add-data=src;src",        "--add-data=src;src",

                

        # Excluir módulos innecesarios para reducir tamaño        # Excluir módulos innecesarios para reducir tamaño

        "--exclude-module=tkinter",        "--exclude-module=tkinter",

        "--exclude-module=matplotlib",        "--exclude-module=matplotlib",

        "--exclude-module=PIL",        "--exclude-module=PIL",

        "--exclude-module=test",        "--exclude-module=test",

        "--exclude-module=unittest",        "--exclude-module=unittest",

                

        # Archivo principal        # Archivo principal

        "installer.py"        "installer.py"

    ]    ]

        

    print(f"Ejecutando PyInstaller...")    print(f"Ejecutando PyInstaller...")

    print(f"(Esto puede tardar varios minutos)\n")    print(f"(Esto puede tardar varios minutos)")

        

    try:    try:

        result = subprocess.run(cmd, capture_output=True, text=True)        result = subprocess.run(cmd, capture_output=True, text=True)

                

        if result.returncode == 0:        if result.returncode == 0:

            print("✓ Compilación exitosa")            print("✓ Compilación exitosa")

            return True            return True

        else:        else:

            print("✗ Error durante la compilación:")            print("✗ Error durante la compilación:")

            print(result.stderr)            print(result.stderr)

            return False            return False

        

    except Exception as e:    except Exception as e:

        print(f"✗ Error: {e}")        print(f"✗ Error: {e}")

        return False        return False





def verify_executable():def verify_executable():

    """Verifica que el ejecutable se haya creado correctamente."""    """Verifica que el ejecutable se haya creado correctamente."""

    print("\n" + "=" * 70)    print("\n" + "=" * 70)

    print("Verificando ejecutable...")    print("Verificando ejecutable...")

    print("=" * 70)    print("=" * 70)

        

    exe_path = Path("dist/SimplexInstaller.exe")    exe_path = Path("dist/SimplexInstaller.exe")

        

    if exe_path.exists():    if exe_path.exists():

        size_mb = exe_path.stat().st_size / (1024 * 1024)        size_mb = exe_path.stat().st_size / (1024 * 1024)

        print(f"✓ Ejecutable creado: {exe_path}")        print(f"✓ Ejecutable creado: {exe_path}")

        print(f"  Tamaño: {size_mb:.1f} MB")        print(f"  Tamaño: {size_mb:.1f} MB")

                

        # Crear archivo de instrucciones junto al ejecutable        # Crear archivo de instrucciones junto al ejecutable

        create_instructions()        create_instructions()

                

        return True        return True

    else:    else:

        print("✗ No se encontró el ejecutable en dist/SimplexInstaller.exe")        print("✗ No se encontró el ejecutable en dist/SimplexInstaller.exe")

        return False        return False





def create_instructions():def create_instructions():

    """Crea un archivo de instrucciones junto al ejecutable."""    """Crea un archivo de instrucciones junto al ejecutable."""

    instructions = """SIMPLEX SOLVER - INSTALADOR INTERACTIVO    instructions = """SIMPLEX SOLVER - INSTALADOR INTERACTIVO

================================================================================



INSTRUCCIONES:INSTRUCCIONES:

----------------------------

1. Ejecuta SimplexInstaller.exe1. Ejecuta SimplexInstaller.exe

2. El instalador analizará automáticamente tu sistema2. El instalador analizará automáticamente tu sistema

3. Te recomendará modelos de IA compatibles con tu PC3. Te recomendará modelos de IA compatibles con tu PC

4. Elige los componentes que deseas instalar4. Elige los componentes que deseas instalar

5. Sigue las instrucciones en pantalla5. Sigue las instrucciones en pantalla



NOTA: Si Windows SmartScreen bloquea el ejecutable:NOTA: Si Windows SmartScreen bloquea el ejecutable:

  - Click en "Más información"  - Click en "Más información"

  - Click en "Ejecutar de todas formas"  - Click en "Ejecutar de todas formas"



COMPONENTES DISPONIBLES:COMPONENTES DISPONIBLES:

------------------------------------------------

• Dependencias Python (obligatorio)• Dependencias Python (obligatorio)

• Ollama - Motor de IA local (opcional)• Ollama - Motor de IA local (opcional)

• Modelos de IA - Varios tamaños disponibles (opcional)• Modelos de IA - Varios tamaños disponibles (opcional)

• Menú Contextual Windows (opcional)• Menú Contextual Windows (opcional)



DESPUÉS DE LA INSTALACIÓN:DESPUÉS DE LA INSTALACIÓN:

------------------------------------------------------

Podrás usar el Simplex Solver para:Podrás usar el Simplex Solver para:

  • Resolver problemas de programación lineal  • Resolver problemas de programación lineal

  • Usar lenguaje natural con IA  • Usar lenguaje natural con IA

  • Integración con el explorador de Windows  • Integración con el explorador de Windows



Para más información, visita:Para más información, visita:

https://github.com/frangcisneros/simplex-projecthttps://github.com/frangcisneros/simplex-project

""""""

        

    instructions_path = Path("dist/LEEME.txt")    instructions_path = Path("dist/LEEME.txt")

    instructions_path.write_text(instructions, encoding="utf-8")    instructions_path.write_text(instructions, encoding="utf-8")

    print(f"✓ Instrucciones creadas: {instructions_path}")    print(f"✓ Instrucciones creadas: {instructions_path}")





def main():def main():

    """Función principal del script de construcción."""    """Función principal del script de construcción.

    print("\n")    pathex=[],

    print("█" * 70)    binaries=[],

    print("█" + " " * 68 + "█")    datas=[],

    print("█" + "    SIMPLEX SOLVER - GENERADOR DE INSTALADOR (.EXE)".center(68) + "█")    hiddenimports=['numpy', 'numpy.core._methods', 'numpy.lib.format'],

    print("█" + " " * 68 + "█")    hookspath=[],

    print("█" * 70)    hooksconfig={},

    print("\n")    runtime_hooks=[],

    excludes=['test', 'tests', 'unittest', 'doctest', 'pdb', 'pstats', 'tkinter'],

    # Verificar que estamos en el directorio correcto    win_no_prefer_redirects=False,

    if not os.path.exists("installer.py"):    win_private_assemblies=False,

        print("✗ Error: No se encontró installer.py en el directorio actual")    cipher=block_cipher,

        print("  Asegúrate de ejecutar este script desde el directorio raíz del proyecto")    noarchive=False,

        sys.exit(1))



    # Paso 1: Instalar PyInstallerpyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

    if not install_pyinstaller():

        sys.exit(1)exe = EXE(

    pyz,

    # Paso 2: Limpiar directorios anteriores    a.scripts,

    clean_build_directories()    a.binaries,

    a.zipfiles,

    # Paso 3: Construir ejecutable    a.datas,

    if not build_installer():    [],

        sys.exit(1)    name='SimplexSolver',

    debug=False,

    # Paso 4: Verificar el ejecutable    bootloader_ignore_signals=False,

    if not verify_executable():    strip=False,

        sys.exit(1)    upx=True,

    upx_exclude=[],

    # Resumen final    runtime_tmpdir=None,

    print("\n" + "█" * 70)    console=True,

    print("█" + " " * 68 + "█")    disable_windowed_traceback=False,

    print("█" + "✓ PROCESO COMPLETADO EXITOSAMENTE".center(68) + "█")    argv_emulation=False,

    print("█" + " " * 68 + "█")    target_arch=None,

    print("█" * 70)    cofile=None,

        icon=None,

    print("\n📦 ARCHIVO GENERADO:"))

    print("  • dist/SimplexInstaller.exe (UN SOLO ARCHIVO)")"""

    print("  • dist/LEEME.txt (instrucciones)")

        with open("simplex_solver.spec", "w", encoding="utf-8") as f:

    print("\n🚀 CÓMO USAR:")        f.write(spec_content)

    print("  1. Distribuye SOLO el archivo: dist/SimplexInstaller.exe")

    print("  2. El usuario lo ejecuta (doble click o desde cmd)")    print("Archivo .spec creado: simplex_solver.spec")

    print("  3. El instalador hace todo automáticamente")

    

    print("\n💡 PRÓXIMOS PASOS:")def build_executable():

    print("  • Prueba el instalador: .\\dist\\SimplexInstaller.exe")    """Construye el archivo ejecutable usando PyInstaller."""

    print("  • Compártelo con otros usuarios")    print("\nIniciando construcción del ejecutable...")

    print("  • Es un archivo portable, no necesita instalación previa")

        try:

    print("\n" + "=" * 70 + "\n")        # Usar el archivo .spec para mayor control

        cmd = [sys.executable, "-m", "PyInstaller", "simplex_solver.spec", "--clean"]



if __name__ == "__main__":        print(f"Ejecutando: {' '.join(cmd)}")

    main()        result = subprocess.run(cmd, capture_output=True, text=True)


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
