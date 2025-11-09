#!/usr/bin/env python3
"""
Sistema Unificado de Construcción para el Solver Simplex
========================================================

Este script consolida toda la funcionalidad de construcción en una única herramienta mantenible.
Sigue los principios SOLID con una clara separación de responsabilidades.

Uso:
    python tools/build.py --installer    # Construir el instalador exe
    python tools/build.py --solver       # Construir el solver exe
    python tools/build.py --all          # Construir ambos
    python tools/build.py --clean        # Limpiar artefactos de construcción

Autor: Francisco Cisneros
"""

from __future__ import annotations

import sys
import subprocess
import shutil
import argparse
import time
from pathlib import Path
from typing import List, Optional
from dataclasses import dataclass


@dataclass
class BuildConfig:
    """Configuración para un objetivo de construcción específico."""

    name: str
    script: str
    output_name: str
    add_data: List[str]
    hidden_imports: List[str]
    excludes: List[str]
    manifest: Optional[str] = None
    uac_admin: bool = False


class BuildCleaner:
    """Responsable de limpiar artefactos de construcción (Principio de Responsabilidad Única)."""

    @staticmethod
    def clean_all() -> None:
        """Eliminar todos los artefactos de construcción."""
        artifacts = ["build", "dist", "__pycache__"]

        for artifact in artifacts:
            path = Path(artifact)
            if path.exists():
                print(f"Eliminando {path}")
                shutil.rmtree(path, ignore_errors=True)

        # Eliminar archivos .spec
        for spec_file in Path(".").glob("*.spec"):
            print(f"Eliminando {spec_file}")
            spec_file.unlink(missing_ok=True)

        print("[OK] Limpieza completada")


class PyInstallerManager:
    """Gestiona la instalación y disponibilidad de PyInstaller (Responsabilidad Única)."""

    @staticmethod
    def ensure_available() -> bool:
        """Asegurarse de que PyInstaller esté instalado y disponible."""
        try:
            import PyInstaller  # type: ignore

            print("[OK] PyInstaller detectado")
            return True
        except ImportError:
            print("[ADVERTENCIA] PyInstaller no encontrado. Instalando...")
            return PyInstallerManager._install()

    @staticmethod
    def _install() -> bool:
        """Instalar PyInstaller desde requirements o pip."""
        req_file = Path("requirements-build.txt")

        try:
            if req_file.exists():
                subprocess.check_call(
                    [sys.executable, "-m", "pip", "install", "-r", str(req_file)],
                    stdout=subprocess.DEVNULL,
                )
            else:
                subprocess.check_call(
                    [sys.executable, "-m", "pip", "install", "pyinstaller"],
                    stdout=subprocess.DEVNULL,
                )
            print("[OK] PyInstaller instalado correctamente")
            return True
        except subprocess.CalledProcessError as e:
            print(f"[ERROR] Falló la instalación de PyInstaller: {e}")
            return False


class SpecFileGenerator:
    """Genera archivos .spec para PyInstaller (Responsabilidad Única)."""

    @staticmethod
    def generate(config: BuildConfig) -> Path:
        """Generar un archivo .spec a partir de la configuración."""
        spec_path = Path(f"{config.output_name.lower()}.spec")

        # Convertir la lista add_data al formato de .spec
        datas_str = ",\n        ".join(
            [f"('{src}', '{dst}')" for src, dst in [item.split(";") for item in config.add_data]]
        )

        # Convertir hidden_imports al formato de .spec
        imports_str = ",\n        ".join([f"'{imp}'" for imp in config.hidden_imports])

        # Convertir excludes al formato de .spec
        excludes_str = ",\n        ".join([f"'{exc}'" for exc in config.excludes])

        spec_content = f"""# -*- mode: python ; coding: utf-8 -*-
# Archivo .spec auto-generado para {config.name}

block_cipher = None

a = Analysis(
    ['{config.script}'],
    pathex=[],
    binaries=[],
    datas=[
        {datas_str}
    ],
    hiddenimports=[
        {imports_str}
    ],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[
        {excludes_str}
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
    name='{config.output_name}',
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
    icon=None,"""

        if config.manifest:
            spec_content += f"\n    manifest='{config.manifest}',"

        if config.uac_admin:
            spec_content += "\n    uac_admin=True,"

        spec_content += "\n)\n"

        spec_path.write_text(spec_content, encoding="utf-8")
        print(f"[OK] Generado {spec_path}")

        return spec_path


class ExecutableBuilder:
    """Construye ejecutables usando PyInstaller (Responsabilidad Única)."""

    @staticmethod
    def build(spec_file: Path, name: str) -> bool:
        """Construir un ejecutable a partir de un archivo .spec."""
        print(f"\n[BUILD] Construyendo {name}...")
        print(f"[INFO] Este proceso puede tomar varios minutos...")
        print(f"[INFO] Mostrando salida de PyInstaller (filtrado):\n")
        print("=" * 70)

        # Patrones a filtrar (advertencias ruidosas que no afectan el funcionamiento)
        filter_patterns = [
            "Library not found: could not resolve 'cublas",
            "Library not found: could not resolve 'cusparse",
            "Library not found: could not resolve 'cudart",
            "DeprecationWarning: `torch.distributed.",
            "NOTE: Redirects are currently not supported",
            "pkg_resources is deprecated as an API",
            "DeprecationWarning: builtin type swigvarlink",
            "SyntaxWarning: 'return' in a 'finally' block",
            "Setuptools: '",  # Filtra los mensajes de setuptools-vendored
        ]

        # ERROR conocido de numpy que es inofensivo
        ignore_errors = ["ERROR: Hidden import 'numpy.core._methods' not found"]

        try:
            cmd = [sys.executable, "-m", "PyInstaller", str(spec_file), "--clean"]

            # Usar Popen para mostrar salida en tiempo real
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True,
            )

            # Leer y mostrar salida línea por línea, filtrando ruido
            for line in process.stdout:
                # Verificar si la línea debe ser filtrada
                should_filter = False

                # Filtrar advertencias ruidosas
                for pattern in filter_patterns:
                    if pattern in line:
                        should_filter = True
                        break

                # No filtrar errores reales, solo los conocidos como inofensivos
                if "ERROR:" in line:
                    for ignored in ignore_errors:
                        if ignored in line:
                            should_filter = True
                            break

                # Mostrar solo líneas no filtradas
                if not should_filter:
                    print(line, end="")

            # Esperar a que el proceso termine
            process.wait()

            print("=" * 70)

            if process.returncode == 0:
                print(f"\n[OK] {name} construido correctamente")
                return True
            else:
                print(f"\n[ERROR] Falló la construcción de {name}")
                print(f"[ERROR] Código de salida: {process.returncode}")
                return False

        except KeyboardInterrupt:
            print("\n[WARN] Build interrumpido por el usuario (Ctrl+C)")
            if process:
                process.terminate()
                process.wait()
            return False
        except Exception as e:
            print(f"[ERROR] Error inesperado durante la construcción de {name}")
            print(f"[ERROR] {str(e)}")
            return False

    @staticmethod
    def verify(exe_path: Path, name: str) -> bool:
        """Verificar que un ejecutable se haya creado correctamente."""
        if exe_path.exists():
            size_mb = exe_path.stat().st_size / (1024 * 1024)
            print(f"[OK] {name}: {exe_path} ({size_mb:.1f} MB)")
            return True
        else:
            print(f"[ERROR] {name} no encontrado en {exe_path}")
            return False


class BuildOrchestrator:
    """
    Orquesta todo el proceso de construcción (Principio Abierto/Cerrado).
    Puede extenderse con nuevas configuraciones de construcción sin modificar el código existente.
    """

    # Configuraciones de construcción (fácilmente extensibles)
    CONFIGS = {
        "installer": BuildConfig(
            name="Instalador de Simplex",
            script="installer.py",
            output_name="SimplexInstaller",
            add_data=[
                "requirements.txt;.",
                "context_menu;context_menu",
                "docs;docs",
                "README.md;.",
                "tools/system_analyzer.py;tools",
                "simplex_solver/ui;simplex_solver/ui",
                "dist/SimplexSolver.exe;.",
            ],
            hidden_imports=[
                "numpy",
                "numpy.core._methods",
                "numpy.lib.format",
                "psutil",
                "psutil._psutil_windows",
                "tabulate",
                "system_analyzer",
                "simplex_solver.ui",
                "simplex_solver.ui.console",
            ],
            excludes=[
                "test",
                "tests",
                "unittest",
                "doctest",
                "pdb",
                "pstats",
                "tkinter",
                "matplotlib",
                "PIL",
            ],
            manifest="installer.manifest",
            uac_admin=True,
        ),
        "solver": BuildConfig(
            name="Solver de Simplex",
            script="simplex.py",
            output_name="SimplexSolver",
            add_data=[
                "simplex_solver;simplex_solver",
                "docs;docs",
                "README.md;.",
            ],
            hidden_imports=[
                "numpy",
                "numpy.core._methods",
                "numpy.lib.format",
                "psutil",
                "tabulate",
                "PIL",
                "PIL._imaging",
                "PIL.Image",
                "reportlab",
                "reportlab.pdfgen",
                "reportlab.pdfgen.canvas",
                "reportlab.lib",
                "reportlab.lib.pagesizes",
                "reportlab.lib.colors",
                "reportlab.lib.styles",
                "reportlab.lib.units",
                "reportlab.platypus",
                "reportlab.platypus.tables",
                "reportlab.platypus.paragraph",
                "reportlab.rl_config",
            ],
            excludes=[
                "test",
                "tests",
                "unittest",
                "doctest",
                "pdb",
                "pstats",
                "tkinter",
                "matplotlib",
            ],
        ),
    }

    def __init__(self):
        self.cleaner = BuildCleaner()
        self.pyinstaller = PyInstallerManager()
        self.spec_generator = SpecFileGenerator()
        self.builder = ExecutableBuilder()

    def build(self, target: str) -> bool:
        """Construir un objetivo específico."""
        if target not in self.CONFIGS:
            print(f"[ERROR] Objetivo desconocido: {target}")
            print(f"Objetivos disponibles: {', '.join(self.CONFIGS.keys())}")
            return False

        config = self.CONFIGS[target]

        print(f"\n{'='*70}")
        print(f"  Construyendo {config.name}")
        print(f"{'='*70}")

        # Verificación especial para el instalador
        if target == "installer":
            solver_exe = Path("dist") / "SimplexSolver.exe"
            if not solver_exe.exists():
                print(f"[ERROR] SimplexSolver.exe no encontrado en {solver_exe}")
                print("[INFO] Debes compilar el solver primero:")
                print("       python tools/build.py --solver")
                return False
            else:
                print(f"[OK] SimplexSolver.exe encontrado: {solver_exe}")

        # Asegurarse de que PyInstaller esté disponible
        if not self.pyinstaller.ensure_available():
            return False

        # Generar archivo .spec
        spec_file = self.spec_generator.generate(config)

        # Construir ejecutable
        if not self.builder.build(spec_file, config.name):
            return False

        # Verificar salida
        exe_path = Path("dist") / f"{config.output_name}.exe"
        return self.builder.verify(exe_path, config.name)

    def build_all(self) -> bool:
        """Construir todos los objetivos en el orden correcto."""
        print("\n[BUILD] Construyendo todos los objetivos...\n")
        print("[INFO] Este proceso puede tomar 5-10 minutos en total")
        print("[INFO] El solver puede tardar 3-5 minutos")
        print("[INFO] El instalador puede tardar 2-3 minutos\n")

        # Orden correcto: solver primero, luego instalador (que incluye el solver)
        build_order = ["solver", "installer"]

        success = True
        start_time = time.time()

        for target in build_order:
            if target in self.CONFIGS:
                print(f"\n{'='*70}")
                print(
                    f"  PASO {build_order.index(target) + 1}/{len(build_order)}: {target.upper()}"
                )
                print(f"{'='*70}")

                target_start = time.time()

                if not self.build(target):
                    elapsed = time.time() - target_start
                    print(f"\n[ERROR] Falló la construcción de {target} después de {elapsed:.1f}s")
                    success = False
                    break  # Detener si falla uno

                elapsed = time.time() - target_start
                print(f"\n[OK] {target} completado exitosamente en {elapsed:.1f}s")

        total_time = time.time() - start_time
        print(f"\n[INFO] Tiempo total: {total_time:.1f}s ({total_time/60:.1f} minutos)")

        return success

    def clean(self) -> None:
        """Limpiar todos los artefactos de construcción."""
        print("\n[CLEAN] Limpiando artefactos de construcción...\n")
        self.cleaner.clean_all()


def main() -> int:
    """Punto de entrada principal."""
    # Verificar que estamos en el directorio raíz del proyecto
    if not Path("pyproject.toml").exists() and not Path("README.md").exists():
        print("[ERROR] Ejecute este script desde el directorio raíz del proyecto")
        return 1

    # Analizar argumentos
    parser = argparse.ArgumentParser(
        description="Sistema unificado de construcción para el Solver Simplex",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  python tools/build.py --solver         # Construir solo el solver
  python tools/build.py --installer      # Construir solo el instalador (requiere solver)
  python tools/build.py --all            # Construir todo en orden correcto
  python tools/build.py --clean          # Limpiar artefactos
  python tools/build.py --clean --all    # Limpiar y construir todo

IMPORTANTE:
  - Para construir el instalador, primero debes construir el solver.
  - Usa --all para construir ambos en el orden correcto automáticamente.
        """,
    )

    parser.add_argument(
        "--installer",
        action="store_true",
        help="Construir el ejecutable del instalador (requiere SimplexSolver.exe)",
    )
    parser.add_argument("--solver", action="store_true", help="Construir el ejecutable del solver")
    parser.add_argument(
        "--all", action="store_true", help="Construir todos los ejecutables en orden correcto"
    )
    parser.add_argument("--clean", action="store_true", help="Limpiar artefactos de construcción")

    args = parser.parse_args()

    # Si no hay argumentos, mostrar ayuda
    if not any(vars(args).values()):
        parser.print_help()
        return 0

    orchestrator = BuildOrchestrator()

    # Manejar limpieza
    if args.clean:
        orchestrator.clean()
        if not any([args.installer, args.solver, args.all]):
            return 0

    # Manejar construcciones
    success = True

    if args.all:
        success = orchestrator.build_all()
    else:
        # Si solo se solicita el instalador, verificar que exista el solver
        if args.installer and not args.solver:
            solver_exe = Path("dist") / "SimplexSolver.exe"
            if not solver_exe.exists():
                print("\n" + "=" * 70)
                print("[ERROR] No se puede construir el instalador sin el solver")
                print("=" * 70)
                print("\nOpciones:")
                print("  1. Construir ambos en orden:    python tools/build.py --all")
                print("  2. Construir solver primero:    python tools/build.py --solver")
                print("     Luego el instalador:         python tools/build.py --installer")
                print("=" * 70)
                return 1

        if args.solver:
            success = orchestrator.build("solver") and success
        if args.installer:
            success = orchestrator.build("installer") and success
        if args.solver:
            success = orchestrator.build("solver") and success

    # Resumen
    print("\n" + "=" * 70)
    if success:
        print("[SUCCESS] CONSTRUCCIÓN COMPLETADA EXITOSAMENTE")
    else:
        print("[FAILED] LA CONSTRUCCIÓN FALLÓ")
    print("=" * 70)

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
