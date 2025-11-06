import pytest
import os
from pathlib import Path

from simplex_solver.file_parser import FileParser
from simplex_solver.user_interface import UserInterface


def test_parse_valid_example_file():
    """Prueba el parseo de un archivo de ejemplo válido."""
    # Usar el archivo de ejemplo proporcionado
    base = Path(__file__).parent.parent
    ejemplo = base / "ejemplos" / "ejemplo_carpinteria.txt"
    assert ejemplo.exists(), "El archivo de ejemplo no existe."

    c, A, b, constraint_types, maximize = FileParser.parse_file(str(ejemplo))

    # Verificar que el problema se parseó correctamente
    assert maximize is True, "El problema debería ser de maximización."
    assert isinstance(c, list) and len(c) == 2, "La función objetivo debe tener 2 coeficientes."
    assert isinstance(A, list) and len(A) >= 1, "Debe haber al menos una restricción."


def test_parse_invalid_file(tmp_path):
    """Prueba el manejo de un archivo inválido."""
    bad = tmp_path / "bad.txt"
    bad.write_text("NOT VALID\nblah blah")

    # Verificar que se lanza un error al intentar parsear un archivo inválido
    with pytest.raises(ValueError, match=".*"):  # Aceptar cualquier mensaje de error
        FileParser.parse_file(str(bad))


def test_interactive_input_monkeypatch(monkeypatch):
    """Simula la entrada del usuario para ingresar un problema de optimización."""
    # Secuencia de entradas para el flujo interactivo:
    # tipo de optimización, coeficientes de la función objetivo, una restricción, 'fin'
    inputs = iter(["max", "3 4", "1 1 <= 10", "fin"])

    # Reemplazar la función input para devolver valores de la secuencia
    monkeypatch.setattr("builtins.input", lambda prompt="": next(inputs))

    c, A, b, constraint_types, maximize = UserInterface.interactive_input()

    # Verificar que los datos ingresados se procesaron correctamente
    assert maximize is True, "El problema debería ser de maximización."
    assert c == [3.0, 4.0], "Los coeficientes de la función objetivo son incorrectos."
    assert len(A) == 1, "Debe haber exactamente una restricción."
    assert constraint_types[0] == "<=", "El tipo de restricción es incorrecto."
