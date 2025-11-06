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

        try:
            cmd = [sys.executable, "-m", "PyInstaller", str(spec_file), "--clean"]

            result = subprocess.run(cmd, capture_output=True, text=True, check=True)

            print(f"[OK] {name} construido correctamente")
            return True

        except subprocess.CalledProcessError as e:
            print(f"[ERROR] Falló la construcción de {name}")
            print(e.stderr)
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
            ],
            hidden_imports=[
                "numpy",
                "numpy.core._methods",
                "numpy.lib.format",
                "psutil",
                "psutil._psutil_windows",
                "tabulate",
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
        """Construir todos los objetivos."""
        print("\n[BUILD] Construyendo todos los objetivos...\n")

        success = True
        for target in self.CONFIGS.keys():
            if not self.build(target):
                success = False

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
  python tools/build.py --installer      # Construir solo el instalador
  python tools/build.py --solver         # Construir solo el solver
  python tools/build.py --all            # Construir todo
  python tools/build.py --clean          # Limpiar artefactos
        """,
    )

    parser.add_argument(
        "--installer", action="store_true", help="Construir el ejecutable del instalador"
    )
    parser.add_argument("--solver", action="store_true", help="Construir el ejecutable del solver")
    parser.add_argument("--all", action="store_true", help="Construir todos los ejecutables")
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
