#!/usr/bin/env python3
"""
Unified Build System for Simplex Solver
========================================

This script consolidates all build functionality into a single, maintainable tool.
It follows SOLID principles with clear separation of concerns.

Usage:
    python tools/build.py --installer    # Build the installer exe
    python tools/build.py --solver       # Build the solver exe
    python tools/build.py --all          # Build both
    python tools/build.py --clean        # Clean build artifacts

Author: Francisco Cisneros
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
    """Configuration for a specific build target."""

    name: str
    script: str
    output_name: str
    add_data: List[str]
    hidden_imports: List[str]
    excludes: List[str]
    manifest: Optional[str] = None
    uac_admin: bool = False


class BuildCleaner:
    """Responsible for cleaning build artifacts (Single Responsibility Principle)."""

    @staticmethod
    def clean_all() -> None:
        """Remove all build artifacts."""
        artifacts = ["build", "dist", "__pycache__"]

        for artifact in artifacts:
            path = Path(artifact)
            if path.exists():
                print(f"Removing {path}")
                shutil.rmtree(path, ignore_errors=True)

        # Remove .spec files
        for spec_file in Path(".").glob("*.spec"):
            print(f"Removing {spec_file}")
            spec_file.unlink(missing_ok=True)

        print("[OK] Cleanup completed")


class PyInstallerManager:
    """Manages PyInstaller installation and availability (Single Responsibility)."""

    @staticmethod
    def ensure_available() -> bool:
        """Ensure PyInstaller is installed and available."""
        try:
            import PyInstaller  # type: ignore

            print("[OK] PyInstaller detected")
            return True
        except ImportError:
            print("[WARNING] PyInstaller not found. Installing...")
            return PyInstallerManager._install()

    @staticmethod
    def _install() -> bool:
        """Install PyInstaller from requirements or pip."""
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
            print("[OK] PyInstaller installed successfully")
            return True
        except subprocess.CalledProcessError as e:
            print(f"[ERROR] Failed to install PyInstaller: {e}")
            return False


class SpecFileGenerator:
    """Generates PyInstaller .spec files (Single Responsibility)."""

    @staticmethod
    def generate(config: BuildConfig) -> Path:
        """Generate a .spec file from configuration."""
        spec_path = Path(f"{config.output_name.lower()}.spec")

        # Convert add_data list to spec format
        datas_str = ",\n        ".join(
            [f"('{src}', '{dst}')" for src, dst in [item.split(";") for item in config.add_data]]
        )

        # Convert hidden imports to spec format
        imports_str = ",\n        ".join([f"'{imp}'" for imp in config.hidden_imports])

        # Convert excludes to spec format
        excludes_str = ",\n        ".join([f"'{exc}'" for exc in config.excludes])

        spec_content = f"""# -*- mode: python ; coding: utf-8 -*-
# Auto-generated spec file for {config.name}

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
        print(f"[OK] Generated {spec_path}")

        return spec_path


class ExecutableBuilder:
    """Builds executables using PyInstaller (Single Responsibility)."""

    @staticmethod
    def build(spec_file: Path, name: str) -> bool:
        """Build an executable from a spec file."""
        print(f"\n[BUILD] Building {name}...")

        try:
            cmd = [sys.executable, "-m", "PyInstaller", str(spec_file), "--clean"]

            result = subprocess.run(cmd, capture_output=True, text=True, check=True)

            print(f"[OK] {name} built successfully")
            return True

        except subprocess.CalledProcessError as e:
            print(f"[ERROR] Build failed for {name}")
            print(e.stderr)
            return False

    @staticmethod
    def verify(exe_path: Path, name: str) -> bool:
        """Verify that an executable was created successfully."""
        if exe_path.exists():
            size_mb = exe_path.stat().st_size / (1024 * 1024)
            print(f"[OK] {name}: {exe_path} ({size_mb:.1f} MB)")
            return True
        else:
            print(f"[ERROR] {name} not found at {exe_path}")
            return False


class BuildOrchestrator:
    """
    Orchestrates the entire build process (Open/Closed Principle).
    Can be extended with new build configs without modifying existing code.
    """

    # Build configurations (easily extendable)
    CONFIGS = {
        "installer": BuildConfig(
            name="Simplex Installer",
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
            name="Simplex Solver",
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
        ),
    }

    def __init__(self):
        self.cleaner = BuildCleaner()
        self.pyinstaller = PyInstallerManager()
        self.spec_generator = SpecFileGenerator()
        self.builder = ExecutableBuilder()

    def build(self, target: str) -> bool:
        """Build a specific target."""
        if target not in self.CONFIGS:
            print(f"[ERROR] Unknown target: {target}")
            print(f"Available targets: {', '.join(self.CONFIGS.keys())}")
            return False

        config = self.CONFIGS[target]

        print(f"\n{'='*70}")
        print(f"  Building {config.name}")
        print(f"{'='*70}")

        # Ensure PyInstaller is available
        if not self.pyinstaller.ensure_available():
            return False

        # Generate spec file
        spec_file = self.spec_generator.generate(config)

        # Build executable
        if not self.builder.build(spec_file, config.name):
            return False

        # Verify output
        exe_path = Path("dist") / f"{config.output_name}.exe"
        return self.builder.verify(exe_path, config.name)

    def build_all(self) -> bool:
        """Build all targets."""
        print("\n[BUILD] Building all targets...\n")

        success = True
        for target in self.CONFIGS.keys():
            if not self.build(target):
                success = False

        return success

    def clean(self) -> None:
        """Clean all build artifacts."""
        print("\n[CLEAN] Cleaning build artifacts...\n")
        self.cleaner.clean_all()


def main() -> int:
    """Main entry point."""
    # Verify we're in the project root
    if not Path("pyproject.toml").exists() and not Path("README.md").exists():
        print("[ERROR] Run this script from the project root directory")
        return 1

    # Parse arguments
    parser = argparse.ArgumentParser(
        description="Unified build system for Simplex Solver",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python tools/build.py --installer      # Build installer only
  python tools/build.py --solver         # Build solver only
  python tools/build.py --all            # Build everything
  python tools/build.py --clean          # Clean artifacts
        """,
    )

    parser.add_argument("--installer", action="store_true", help="Build the installer executable")
    parser.add_argument("--solver", action="store_true", help="Build the solver executable")
    parser.add_argument("--all", action="store_true", help="Build all executables")
    parser.add_argument("--clean", action="store_true", help="Clean build artifacts")

    args = parser.parse_args()

    # If no arguments, show help
    if not any(vars(args).values()):
        parser.print_help()
        return 0

    orchestrator = BuildOrchestrator()

    # Handle clean
    if args.clean:
        orchestrator.clean()
        if not any([args.installer, args.solver, args.all]):
            return 0

    # Handle builds
    success = True

    if args.all:
        success = orchestrator.build_all()
    else:
        if args.installer:
            success = orchestrator.build("installer") and success
        if args.solver:
            success = orchestrator.build("solver") and success

    # Summary
    print("\n" + "=" * 70)
    if success:
        print("[SUCCESS] BUILD COMPLETED SUCCESSFULLY")
    else:
        print("[FAILED] BUILD FAILED")
    print("=" * 70)

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
