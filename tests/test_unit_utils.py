import os
import sqlite3
from unittest import mock

import pytest

from simplex_solver.logging_system import LoggingSystem, logger
from simplex_solver.reporting_pdf import generate_pdf


def test_logging_system_write_and_db(tmp_path, monkeypatch):
    # Create an isolated DB path by monkeypatching _get_db_path before instantiation
    monkeypatch.setattr(LoggingSystem, "_get_db_path", lambda self: str(tmp_path / "test_logs.db"))
    # Reset singleton
    LoggingSystem._instance = None
    ls = LoggingSystem()

    # Log a message
    ls.info("test message", module="tests", function="test")

    # Verify DB has an entry
    conn = sqlite3.connect(ls.get_db_path())
    cur = conn.cursor()
    cur.execute("SELECT COUNT(1) FROM logs")
    count = cur.fetchone()[0]
    conn.close()

    assert count >= 1


def test_generate_pdf_delegates_to_export(monkeypatch, tmp_path):
    # Prepare a fake result
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
        called["res"] = res
        # create an empty file to simulate output
        open(filename, "wb").close()

    # Patch the function in the reporting_pdf module where it's used
    monkeypatch.setattr("simplex_solver.reporting_pdf.export_to_pdf", fake_export)

    out = generate_pdf(result, filename=str(tmp_path / "out.pdf"), reports_dir=str(tmp_path))

    assert os.path.exists(out)
    assert "res" in called
