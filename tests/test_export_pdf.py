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
    """
    Tests de generación de reportes PDF.
    """

    def setUp(self):
        """
        Configura un problema sencillo de maximización para los tests.
        """
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
        """
        Verifica que se genere un archivo PDF correctamente para un problema de maximización.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "test_report.pdf")

            # Generar el PDF
            pdf_path = generate_pdf(self.result, filename=output_path, reports_dir=tmpdir)

            # Verificar que el archivo se haya creado
            self.assertTrue(os.path.exists(pdf_path), "El archivo PDF no fue generado.")

            # Verificar que tenga tamaño mayor a 0
            self.assertGreater(
                os.path.getsize(pdf_path),
                1000,
                "El PDF generado está vacío o incompleto.",
            )

            # Verificar que las claves esperadas estén en result
            self.assertIn("steps", self.result, "El resultado no contiene pasos del simplex.")
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

    def test_pdf_generation_minimization(self):
        """
        Verifica que también se genere un archivo PDF para un problema de minimización.
        """

        c = [4, 3]
        A = [[2, 1], [1, 3]]
        b = [10, 15]
        constraint_types = [">=", ">="]  # <-- Clave del cambio

        solver = SimplexSolver()
        result = solver.solve(c, A, b, constraint_types, maximize=False)

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "test_min_report.pdf")

            pdf_path = generate_pdf(result, filename=output_path, reports_dir=tmpdir)

            # Verificar que el archivo se haya creado
            self.assertTrue(os.path.exists(pdf_path), "El archivo PDF no fue generado.")

            # Verificar que tenga tamaño mayor a 0
            self.assertGreater(
                os.path.getsize(pdf_path),
                1000,
                "El PDF generado está vacío o incompleto.",
            )

    def test_pdf_includes_sensitivity_analysis(self):
        """
        Verifica que el PDF incluya el análisis de sensibilidad para problemas óptimos.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "test_sensitivity_report.pdf")

            # Verificar que el resultado tenga análisis de sensibilidad
            self.assertIn(
                "sensitivity_analysis",
                self.result,
                "El resultado no contiene análisis de sensibilidad.",
            )
            self.assertIsNotNone(
                self.result["sensitivity_analysis"],
                "El análisis de sensibilidad es None.",
            )

            # Generar el PDF
            pdf_path = generate_pdf(self.result, filename=output_path, reports_dir=tmpdir)

            # Verificar que el archivo se haya creado
            self.assertTrue(os.path.exists(pdf_path), "El archivo PDF no fue generado.")

            # Verificar que tenga tamaño mayor a 0
            self.assertGreater(
                os.path.getsize(pdf_path),
                1000,
                "El PDF generado está vacío o incompleto.",
            )

            # Verificar estructura del análisis de sensibilidad
            analysis = self.result["sensitivity_analysis"]
            self.assertIn("shadow_prices", analysis)
            self.assertIn("optimality_ranges", analysis)
            self.assertIn("feasibility_ranges", analysis)


if __name__ == "__main__":
    unittest.main()
