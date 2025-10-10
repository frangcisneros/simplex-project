#!/usr/bin/env python3
"""
Script principal para ejecutar el Simplex Solver
"""

import sys
import os

# Agregar la carpeta src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from src.main import main

if __name__ == "__main__":
    main()
