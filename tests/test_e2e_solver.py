import sys
from pathlib import Path

import pytest

from simplex_solver.main import main


def test_main_resolves_example_file(monkeypatch, capsys):
    base = Path(__file__).parent.parent
    ejemplo = str(base / "ejemplos" / "ejemplo_carpinteria.txt")

    monkeypatch.setattr(sys, "argv", ["simplex.py", ejemplo])

    # Running main should not raise; capture output
    try:
        main()
    except SystemExit as e:
        # main may call sys.exit(0) on success; ignore
        assert e.code == None or e.code == 0

    captured = capsys.readouterr()
    out = captured.out + captured.err

    # Expect final solution printing or validation message
    assert "Valor óptimo" in out or "Solución óptima" in out or "Estado" in out
