"""
Tests para el sistema de menú contextual de Windows.
Verifica que los scripts del context menu funcionen correctamente.
"""

import unittest
import sys
import os
from pathlib import Path
from unittest.mock import patch, MagicMock
import tempfile

# Agregar el directorio raíz al path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "context_menu"))


class TestContextMenuIntegration(unittest.TestCase):
    """Tests de integración para el menú contextual."""

    def setUp(self):
        """Configuración antes de cada test."""
        self.test_dir = tempfile.mkdtemp()
        self.test_file = Path(self.test_dir) / "test_problem.txt"

    def tearDown(self):
        """Limpieza después de cada test."""
        import shutil

        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def create_test_file(self, content):
        """Crea un archivo de prueba con el contenido especificado."""
        with open(self.test_file, "w", encoding="utf-8") as f:
            f.write(content)
        return str(self.test_file)

    def test_solve_from_context_maximization(self):
        """Test resolver problema de maximización desde context menu."""
        # Crear archivo de prueba
        content = """MAXIMIZE
3 2
SUBJECT TO
2 1 <= 18
2 3 <= 42
3 1 <= 24
"""
        filepath = self.create_test_file(content)

        # Importar el módulo
        import solve_from_context

        # Mock de input para evitar que se detenga esperando entrada
        with patch("builtins.input", return_value="N"):
            # Mock de print para capturar salida
            with patch("builtins.print") as mock_print:
                # Ejecutar la función principal
                solve_from_context.solve_from_file(filepath)

                # Verificar que se imprimieron mensajes clave
                printed_text = " ".join(
                    [str(arg) for call in mock_print.call_args_list for arg in call[0] if call[0]]
                )

                self.assertIn("SIMPLEX SOLVER", printed_text)
                self.assertIn("validado correctamente", printed_text)
                self.assertIn("Resolviendo problema", printed_text)
                self.assertIn("RESULTADOS", printed_text)

    def test_solve_from_context_minimization(self):
        """Test resolver problema de minimización desde context menu."""
        content = """MINIMIZE
4 3
SUBJECT TO
2 3 >= 12
3 1 >= 9
1 2 >= 8
"""
        filepath = self.create_test_file(content)

        import solve_from_context

        with patch("builtins.input", return_value="N"):
            with patch("builtins.print") as mock_print:
                solve_from_context.solve_from_file(filepath)

                printed_text = " ".join(
                    [str(arg) for call in mock_print.call_args_list for arg in call[0] if call[0]]
                )

                self.assertIn("SIMPLEX SOLVER", printed_text)
                self.assertIn("validado correctamente", printed_text)
                self.assertIn("Proceso completado", printed_text)

    def test_solve_from_context_invalid_file(self):
        """Test manejo de archivo inválido."""
        import solve_from_context

        # Mock de input para evitar que se detenga esperando entrada del usuario
        with patch("builtins.input", return_value=""):
            with patch("builtins.print"):
                # Debe salir con error (sys.exit(1))
                with self.assertRaises(SystemExit) as cm:
                    solve_from_context.solve_from_file("archivo_inexistente.txt")

                # Verificar que el código de salida es 1 (error)
                self.assertEqual(cm.exception.code, 1)

    def test_solve_from_context_invalid_format(self):
        """Test manejo de formato inválido."""
        content = """ESTO NO ES VALIDO
1 2 3
"""
        filepath = self.create_test_file(content)

        import solve_from_context

        # Mock de input para evitar que se detenga esperando entrada del usuario
        with patch("builtins.input", return_value=""):
            with patch("builtins.print"):
                # Debe salir con error (sys.exit(1))
                with self.assertRaises(SystemExit) as cm:
                    solve_from_context.solve_from_file(filepath)

                # Verificar que el código de salida es 1 (error)
                self.assertEqual(cm.exception.code, 1)


class TestContextMenuScripts(unittest.TestCase):
    """Tests para verificar la existencia y estructura de los scripts."""

    def setUp(self):
        """Configuración antes de cada test."""
        self.context_menu_dir = PROJECT_ROOT / "context_menu"

    def test_solve_from_context_exists(self):
        """Verifica que el script solve_from_context.py existe."""
        script_path = self.context_menu_dir / "solve_from_context.py"
        self.assertTrue(script_path.exists(), "solve_from_context.py debe existir")

    def test_solve_from_context_ai_exists(self):
        """Verifica que el script solve_from_context_ai.py existe."""
        script_path = self.context_menu_dir / "solve_from_context_ai.py"
        self.assertTrue(script_path.exists(), "solve_from_context_ai.py debe existir")

    def test_run_solver_bat_exists(self):
        """Verifica que el wrapper run_solver.bat existe."""
        bat_path = self.context_menu_dir / "run_solver.bat"
        self.assertTrue(bat_path.exists(), "run_solver.bat debe existir")

    def test_run_solver_ai_bat_exists(self):
        """Verifica que el wrapper run_solver_ai.bat existe."""
        bat_path = self.context_menu_dir / "run_solver_ai.bat"
        self.assertTrue(bat_path.exists(), "run_solver_ai.bat debe existir")

    def test_install_bat_exists(self):
        """Verifica que el instalador install.bat existe."""
        bat_path = self.context_menu_dir / "install.bat"
        self.assertTrue(bat_path.exists(), "install.bat debe existir")

    def test_uninstall_bat_exists(self):
        """Verifica que el desinstalador uninstall.bat existe."""
        bat_path = self.context_menu_dir / "uninstall.bat"
        self.assertTrue(bat_path.exists(), "uninstall.bat debe existir")

    def test_run_solver_bat_content(self):
        """Verifica que run_solver.bat contiene los comandos correctos."""
        bat_path = self.context_menu_dir / "run_solver.bat"
        with open(bat_path, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertIn("python", content.lower(), "Debe ejecutar python")
        self.assertIn("solve_from_context.py", content, "Debe llamar a solve_from_context.py")
        self.assertIn("pause", content.lower(), "Debe tener pause al final")

    def test_install_bat_content(self):
        """Verifica que install.bat contiene las configuraciones del registro."""
        bat_path = self.context_menu_dir / "install.bat"
        with open(bat_path, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertIn("reg add", content.lower(), "Debe agregar entradas al registro")
        self.assertIn("SimplexSolver", content, "Debe registrar SimplexSolver")
        self.assertIn("txtfile", content.lower(), "Debe asociarse con archivos txt")


class TestContextMenuExamples(unittest.TestCase):
    """Tests para verificar los archivos de ejemplo."""

    def setUp(self):
        """Configuración antes de cada test."""
        self.ejemplos_dir = PROJECT_ROOT / "ejemplos"

    def test_ejemplos_directory_exists(self):
        """Verifica que la carpeta ejemplos existe."""
        self.assertTrue(self.ejemplos_dir.exists(), "Carpeta ejemplos debe existir")

    def test_ejemplo_maximizacion_exists(self):
        """Verifica que ejemplo_maximizacion.txt existe."""
        ejemplo_path = self.ejemplos_dir / "ejemplo_maximizacion.txt"
        self.assertTrue(ejemplo_path.exists(), "ejemplo_maximizacion.txt debe existir")

    def test_ejemplo_minimizacion_exists(self):
        """Verifica que ejemplo_minimizacion.txt existe."""
        ejemplo_path = self.ejemplos_dir / "ejemplo_minimizacion.txt"
        self.assertTrue(ejemplo_path.exists(), "ejemplo_minimizacion.txt debe existir")

    def test_ejemplo_carpinteria_exists(self):
        """Verifica que ejemplo_carpinteria.txt existe."""
        ejemplo_path = self.ejemplos_dir / "ejemplo_carpinteria.txt"
        self.assertTrue(ejemplo_path.exists(), "ejemplo_carpinteria.txt debe existir")

    def test_ejemplo_maximizacion_format(self):
        """Verifica que ejemplo_maximizacion.txt tiene el formato correcto."""
        ejemplo_path = self.ejemplos_dir / "ejemplo_maximizacion.txt"
        with open(ejemplo_path, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertIn("MAXIMIZE", content, "Debe tener MAXIMIZE")
        self.assertIn("SUBJECT TO", content, "Debe tener SUBJECT TO")

    def test_ejemplo_minimizacion_format(self):
        """Verifica que ejemplo_minimizacion.txt tiene el formato correcto."""
        ejemplo_path = self.ejemplos_dir / "ejemplo_minimizacion.txt"
        with open(ejemplo_path, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertIn("MINIMIZE", content, "Debe tener MINIMIZE")
        self.assertIn("SUBJECT TO", content, "Debe tener SUBJECT TO")

    def test_ejemplos_are_parseable(self):
        """Verifica que los ejemplos se pueden parsear correctamente."""
        from simplex_solver.file_parser import FileParser

        ejemplos = [
            "ejemplo_maximizacion.txt",
            "ejemplo_minimizacion.txt",
            "ejemplo_carpinteria.txt",
        ]

        for ejemplo in ejemplos:
            ejemplo_path = self.ejemplos_dir / ejemplo
            if ejemplo_path.exists():
                try:
                    c, A, b, constraint_types, maximize = FileParser.parse_file(str(ejemplo_path))

                    # Verificar que los datos parseados son válidos
                    self.assertIsNotNone(c, f"{ejemplo}: c no debe ser None")
                    self.assertIsNotNone(A, f"{ejemplo}: A no debe ser None")
                    self.assertIsNotNone(b, f"{ejemplo}: b no debe ser None")
                    self.assertIsNotNone(
                        constraint_types,
                        f"{ejemplo}: constraint_types no debe ser None",
                    )
                    self.assertIsInstance(maximize, bool, f"{ejemplo}: maximize debe ser bool")

                except Exception as e:
                    self.fail(f"{ejemplo} falló al parsear: {e}")


if __name__ == "__main__":
    unittest.main()
