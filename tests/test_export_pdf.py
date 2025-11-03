"""
Tests para la generación de reportes PDF del método simplex.
Verifica que se genere correctamente el archivo, contenga las claves esperadas
y no se produzcan errores durante el proceso de exportación.
"""

import unittest
import os
import sys
import tempfile

# Agregar el directorio padre al path para importar módulos desde src/
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from simplex_solver.solver import SimplexSolver
from simplex_solver.reporting_pdf import generate_pdf


class TestPDFExport(unittest.TestCase):
    """Tests de generación de reportes PDF."""

    def setUp(self):
        """Configura un problema sencillo de maximización."""
        self.c = [7, 4]
        self.A = [[2, 1], [1, 1], [1, 0]]
        self.b = [20, 18, 8]
        self.constraint_types = ["<=", "<=", "<="]
        self.maximize = True

        # Crear una instancia del solver
        self.solver = SimplexSolver()

        # Resolver el problema y obtener resultados
        self.result = self.solver.solve(
            self.c, self.A, self.b, self.constraint_types, maximize=self.maximize
        )

    def test_pdf_generation(self):
        """Verifica que se genere un archivo PDF correctamente (maximización)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "test_report.pdf")

            # Generar el PDF
            pdf_path = generate_pdf(
                self.result, filename=output_path, reports_dir=tmpdir
            )

            # Verificar que el archivo se haya creado
            self.assertTrue(os.path.exists(pdf_path), "El archivo PDF no fue generado.")

            # Verificar que tenga tamaño mayor a 0
            self.assertGreater(
                os.path.getsize(pdf_path),
                1000,
                "El PDF generado está vacío o incompleto.",
            )

            # Verificar que las claves esperadas estén en result
            self.assertIn(
                "steps", self.result, "El resultado no contiene pasos del simplex."
            )
            self.assertGreater(
                len(self.result["steps"]), 0, "No se encontraron pasos en el historial."
            )

            # Comprobar que el último tableau esté presente
            last_step = self.result["steps"][-1]
            self.assertIn(
                "tableau",
                last_step,
                "No se encontró el tableau final en el último paso.",
            )

    @unittest.skip(
        "Se desactiva temporalmente hasta corregir la resolución de minimización."
    )
    # ? EL PROBLEMA ES CORRECTO (la solución es 0,0 y el valor de Z es 0, faltaria agregar una restricción para evitar ese punto si eso es lo que se observo que estaba mal)
    def test_pdf_generation_minimization(self):
        """Verifica que también funcione para un problema de minimización."""
        c = [3, 5]
        A = [[1, 0], [0, 2], [3, 2]]
        b = [4, 12, 18]
        constraint_types = ["<=", "<=", "<="]

        solver = SimplexSolver()
        result = solver.solve(c, A, b, constraint_types, maximize=False)

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "test_min_report.pdf")

            pdf_path = generate_pdf(result, filename=output_path, reports_dir=tmpdir)

            self.assertTrue(os.path.exists(pdf_path))
            self.assertGreater(os.path.getsize(pdf_path), 1000)


if __name__ == "__main__":
    unittest.main()
