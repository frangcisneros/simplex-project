#!/usr/bin/env python3
"""
Script to launch the Simplex Solver log viewer.
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from simplex_solver.log_viewer import main

if __name__ == "__main__":
    main()
