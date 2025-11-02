#!/usr/bin/env python3
"""
Script para lanzar el visor de logs del Simplex Solver.
"""

import sys
import os

# Agregar la carpeta src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from src.log_viewer import main

if __name__ == "__main__":
    main()
