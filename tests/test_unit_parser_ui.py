import pytest
import os
from pathlib import Path

from simplex_solver.file_parser import FileParser
from simplex_solver.user_interface import UserInterface


def test_parse_valid_example_file():
    # Use provided ejemplo file
    base = Path(__file__).parent.parent
    ejemplo = base / "ejemplos" / "ejemplo_carpinteria.txt"
    assert ejemplo.exists()

    c, A, b, constraint_types, maximize = FileParser.parse_file(str(ejemplo))

    assert maximize is True
    assert isinstance(c, list) and len(c) == 2
    assert isinstance(A, list) and len(A) >= 1


def test_parse_invalid_file(tmp_path):
    bad = tmp_path / "bad.txt"
    bad.write_text("NOT VALID\nblah blah")

    with pytest.raises(ValueError):
        FileParser.parse_file(str(bad))


def test_interactive_input_monkeypatch(monkeypatch):
    """Simulate user entering optimization type, objective and one constraint."""
    # Sequence of inputs for interactive flow:
    # optimization type, objective coefficients, one constraint, 'fin'
    inputs = iter(["max", "3 4", "1 1 <= 10", "fin"])

    monkeypatch.setattr("builtins.input", lambda prompt="": next(inputs))

    c, A, b, constraint_types, maximize = UserInterface.interactive_input()

    assert maximize is True
    assert c == [3.0, 4.0]
    assert len(A) == 1
    assert constraint_types[0] == "<="
