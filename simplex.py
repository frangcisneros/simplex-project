#!/usr/bin/env python3
"""
Script principal para ejecutar el Simplex Solver
"""

import sys
import os

"""import argparse

# Flags
parser = argparse.ArgumentParser()
parser.add_argument("input_file", help="Archivo .txt con el problema")
parser.add_argument("--debug", choices=['NONE','L','M','XL'], default='NONE', help="Nivel de debug")
parser.add_argument("--debug-out", help="Guardar trace en JSON")
args = parser.parse_args()"""

# Agregar la carpeta src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from src.main import main

if __name__ == "__main__":
    main()
