"""
Script para ver el historial de problemas resueltos.
"""

import sys
import os

# Agregar src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from problem_history import show_history_menu

if __name__ == "__main__":
    temp_file = show_history_menu()

    if temp_file:
        # Usuario quiere re-resolver un problema
        print("\n¿Deseas ejecutar el Simplex Solver con este problema? (s/n)")
        choice = input().strip().lower()

        if choice == "s":
            print(f"\nEjecutando: python simplex.py {temp_file}")
            os.system(f'python simplex.py "{temp_file}"')
        else:
            print(f"\nPuedes ejecutarlo manualmente con:")
            print(f'python simplex.py "{temp_file}"')
