#!/usr/bin/env python3
"""
tools/build_exe.py

Small, robust helper to build the standalone SimplexInstaller.exe using PyInstaller.

Usage:
  python tools/build_exe.py

The script will:
 - Ensure PyInstaller is installed (uses requirements-build.txt if present)
 - Clean previous build artifacts (build/, dist/, *.spec)
 - Run PyInstaller with the recommended options for this project
 - Report success and the size of the generated executable

Designed to be easy to maintain and safe to run from project root on Windows.
"""

from __future__ import annotations

import sys
import subprocess
import shutil
from pathlib import Path
from typing import List


def ensure_pyinstaller() -> bool:
    """Ensure PyInstaller is available; install it (from requirements-build.txt) if missing.

    Returns True if PyInstaller is available (already or after install), False otherwise.
    """
    try:
        import PyInstaller  # type: ignore

        print(" PyInstaller detected")
        return True
    except Exception:
        print(
            "PyInstaller not found. Installing from requirements-build.txt (or pip install pyinstaller)"
        )
        req_file = Path("requirements-build.txt")
        try:
            if req_file.exists():
                subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", str(req_file)])
            else:
                subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
            print(" PyInstaller installed successfully")
            return True
        except subprocess.CalledProcessError as e:
            print(f" Failed to install PyInstaller: {e}")
            return False


def clean_build_directories() -> None:
    """Remove build artifacts: build/, dist/, and .spec files."""
    to_clean = ["build", "dist", "__pycache__"]
    for d in to_clean:
        p = Path(d)
        if p.exists():
            print(f"Removing {p}")
            shutil.rmtree(p, ignore_errors=True)

    # Remove .spec files in the repo root
    for spec in Path(".").glob("*.spec"):
        try:
            print(f"Removing spec file: {spec}")
            spec.unlink()
        except Exception:
            pass


def build_pyinstaller(cmd_args: List[str]) -> bool:
    """Run PyInstaller with given arguments. Returns True on success."""
    print("Running PyInstaller...")
    try:
        result = subprocess.run(cmd_args, capture_output=True, text=True)
        if result.returncode == 0:
            print(" PyInstaller finished successfully")
            return True
        else:
            print(" PyInstaller failed:")
            print(result.stdout)
            print(result.stderr)
            return False
    except Exception as e:
        print(f" Exception invoking PyInstaller: {e}")
        return False


def verify_executable(exe_path: Path) -> bool:
    """Verify the generated executable exists and report its size."""
    if exe_path.exists():
        size_mb = exe_path.stat().st_size / (1024 * 1024)
        print(f" Executable created: {exe_path} ({size_mb:.1f} MB)")
        return True
    else:
        print(f" Executable not found at: {exe_path}")
        return False


def main() -> int:
    # Ensure script is run from repository root
    if not Path("pyproject.toml").exists() and not Path("README.md").exists():
        print(
            "Error: this script should be run from the project root (where pyproject.toml / README.md live)"
        )
        return 1

    if not ensure_pyinstaller():
        return 1

    # Clean previous builds
    clean_build_directories()

    # Build command. Use Windows style add-data separator ";" (PyInstaller expects platform-specific separator).
    exe_name = "SimplexInstaller"
    add_datas = [
        "requirements.txt;.",
        "context_menu;context_menu",
        "docs;docs",
        "README.md;.",
        "simplex_solver;simplex_solver",
    ]

    cmd: List[str] = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--onefile",
        "--console",
        f"--name={exe_name}",
        "--clean",
        "--manifest=installer.manifest",
        "--hidden-import=psutil",
        "--hidden-import=psutil._psutil_windows",
        "--hidden-import=numpy",
        "--hidden-import=tabulate",
    ]

    for ad in add_datas:
        cmd.append(f"--add-data={ad}")

    # Main entrypoint
    cmd.append("installer.py")

    print("PyInstaller command:")
    print(" ".join(cmd))

    success = build_pyinstaller(cmd)
    if not success:
        return 2

    exe_path = Path("dist") / f"{exe_name}.exe"
    if not verify_executable(exe_path):
        return 3

    print("\nBuild completed successfully.")
    print(f"Executable: {exe_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
