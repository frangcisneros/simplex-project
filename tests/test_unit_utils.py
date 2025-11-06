import os
import sqlite3
from unittest import mock

import pytest

from simplex_solver.logging_system import LoggingSystem, logger
from simplex_solver.reporting_pdf import generate_pdf


def test_logging_system_write_and_db(tmp_path, monkeypatch):
    """Prueba que el sistema de logging escriba mensajes y los almacene en la base de datos."""
    # Crear una ruta de base de datos aislada mediante monkeypatch antes de la instanciación
    monkeypatch.setattr(LoggingSystem, "_get_db_path", lambda self: str(tmp_path / "test_logs.db"))
    # Reiniciar el singleton
    LoggingSystem._instance = None
    ls = LoggingSystem()

    # Registrar un mensaje
    ls.info("test message", module="tests", function="test")

    # Verificar que la base de datos tiene una entrada
    conn = sqlite3.connect(ls.get_db_path())
    cur = conn.cursor()
    cur.execute("SELECT COUNT(1) FROM logs")
    count = cur.fetchone()[0]
    conn.close()

    assert count >= 1, "La base de datos debería contener al menos un registro."


def test_generate_pdf_delegates_to_export(monkeypatch, tmp_path):
    """Prueba que la generación de PDF delegue correctamente al método de exportación."""
    # Preparar un resultado simulado
    result = {
        "c": [7, 4],
        "A": [[2, 1], [1, 1], [1, 0]],
        "b": [20, 18, 8],
        "constraint_types": ["<=", "<=", "<="],
        "maximize": True,
        "status": "optimal",
        "solution": {"x1": 1.0, "x2": 2.0},
        "optimal_value": 100.0,
        "steps": [],
    }

    called = {}

    def fake_export(res, filename):
        """Simula la exportación a PDF creando un archivo vacío."""
        called["res"] = res
        # Crear un archivo vacío para simular la salida
        open(filename, "wb").close()

    # Parchear la función en el módulo reporting_pdf donde se utiliza
    monkeypatch.setattr("simplex_solver.reporting_pdf.export_to_pdf", fake_export)

    out = generate_pdf(result, filename=str(tmp_path / "out.pdf"), reports_dir=str(tmp_path))

    # Verificar que el archivo se haya creado y que el método de exportación haya sido llamado
    assert os.path.exists(out), "El archivo PDF no fue creado."
    assert "res" in called, "El método de exportación no fue llamado correctamente."
