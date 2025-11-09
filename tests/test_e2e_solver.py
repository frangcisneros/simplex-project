import sys
from pathlib import Path

import pytest

from simplex_solver.main import main


def test_main_resolves_example_file(monkeypatch, capsys):
    """
    Verifica que el programa principal resuelve correctamente un archivo de ejemplo.

    Este test utiliza el archivo de ejemplo "ejemplo_carpinteria.txt" y simula
    la ejecución del programa principal, capturando su salida para verificar
    que se produce una solución válida o un mensaje de validación.
    """
    base = Path(__file__).parent.parent
    ejemplo = str(base / "ejemplos" / "ejemplo_carpinteria.txt")

    # Simular los argumentos de línea de comandos
    monkeypatch.setattr(sys, "argv", ["simplex.py", ejemplo])

    # Ejecutar la función principal y capturar la salida
    try:
        main()
    except SystemExit as e:
        # Ignorar llamadas a sys.exit(0) en caso de éxito
        assert e.code is None or e.code == 0

    captured = capsys.readouterr()
    out = captured.out + captured.err

    # Verificar que la salida contiene información esperada
    assert "Valor óptimo" in out or "Solución óptima" in out or "Estado" in out
