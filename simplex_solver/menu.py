"""
Menú interactivo principal del Simplex Solver v2.0.
Terminal User Interface (TUI) profesional siguiendo principios SOLID, DRY y KISS.

Responsabilidades (SRP):
- Presentación de opciones al usuario
- Captura y validación de entrada
- Orquestación de llamadas a servicios
- NO contiene lógica de negocio
"""

import os
import sys
import platform
import subprocess
import json
import tempfile
from pathlib import Path
from typing import Optional, Dict, Any, List
from simplex_solver.logging_system import logger
from simplex_solver.ui import ConsoleUI, ConsoleColors, enable_ansi_colors


class TUIFormatter:
    """Utilidades de formateo para la TUI."""

    @staticmethod
    def format_number(value: float, decimals: int = 6) -> str:
        """Formatea un número con decimales específicos y separadores de miles."""
        return f"{value:,.{decimals}f}"

    @staticmethod
    def format_duration(ms: float) -> str:
        """Formatea duración en milisegundos a formato legible."""
        if ms < 1000:
            return f"{ms:.2f} ms"
        else:
            return f"{ms/1000:.2f} s"

    @staticmethod
    def truncate_text(text: str, max_length: int = 40) -> str:
        """Trunca texto largo agregando '...'"""
        if len(text) <= max_length:
            return text
        return text[: max_length - 3] + "..."

    @staticmethod
    def format_table_row(columns: List[str], widths: List[int]) -> str:
        """Formatea una fila de tabla con columnas alineadas."""
        parts = []
        for col, width in zip(columns, widths):
            parts.append(f"{col:<{width}}")
        return "  │  ".join(parts)

    @staticmethod
    def visual_len(text: str) -> int:
        """
        Calcula la longitud visual de un texto, excluyendo códigos de escape ANSI.

        Args:
            text: Texto que puede contener códigos de escape ANSI

        Returns:
            int: Longitud visual del texto (sin contar códigos de escape)
        """
        import re

        # Patrón para detectar secuencias de escape ANSI
        ansi_escape = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")
        return len(ansi_escape.sub("", text))

    @staticmethod
    def pad_line(text: str, width: int) -> str:
        """
        Rellena una línea con espacios para que tenga el ancho visual especificado.

        Args:
            text: Texto a rellenar (puede contener códigos ANSI)
            width: Ancho visual objetivo

        Returns:
            str: Texto rellenado con espacios al final
        """
        visual_length = TUIFormatter.visual_len(text)
        padding_needed = width - visual_length
        if padding_needed > 0:
            return text + " " * padding_needed
        return text


class SimplexMenu:
    """
    Menú principal del Simplex Solver v2.0.

    TUI profesional que orquesta todas las funcionalidades del sistema:
    - Resolver problemas (archivo, manual, IA)
    - Análisis y reportes (historial, logs)
    - Utilidades (configuración IA, ejemplos, sistema)
    - Ayuda y documentación

    Attributes:
        running (bool): Controla el bucle principal del menú
        ui (ConsoleUI): Instancia de la interfaz de consola
    """

    def __init__(self):
        enable_ansi_colors()
        self.running = True
        self.ui = ConsoleUI()
        logger.info("Inicializando Simplex Solver v2.0")

    # ========================================================================
    # MÉTODOS PRINCIPALES
    # ========================================================================

    def run(self):
        """
        Ejecuta el bucle principal del menú interactivo.

        Muestra el menú repetidamente hasta que el usuario seleccione
        la opción de salir.
        """
        logger.info("=== Iniciando Simplex Solver - Menú Interactivo v2.0 ===")

        while self.running:
            self._show_main_menu()
            choice = self._get_choice()
            self._handle_main_menu_choice(choice)

        logger.info("=== Finalizando Simplex Solver - Menú Interactivo ===")

    def _show_main_menu(self):
        """Muestra el menú principal con diseño profesional."""
        self.ui.clear_screen()

        # Header
        print("┌" + "─" * 70 + "┐")
        title = f"{ConsoleColors.BOLD}{ConsoleColors.CYAN}SIMPLEX SOLVER v2.0{ConsoleColors.RESET}"
        title_padded = TUIFormatter.pad_line("│ " + title, 70)
        print(title_padded + " │")
        subtitle_padded = TUIFormatter.pad_line("│ Sistema de Optimización Lineal con IA", 70)
        print(subtitle_padded + " │")
        print("└" + "─" * 70 + "┘\n")

        # Menú principal
        print("┌" + "─" * 70 + "┐")
        menu_title = f"│ {ConsoleColors.BOLD}MENÚ PRINCIPAL{ConsoleColors.RESET}"
        menu_title_padded = TUIFormatter.pad_line(menu_title, 69)
        print(menu_title_padded + " │")
        print("├" + "─" * 70 + "┤")
        print("│" + " " * 70 + "│")

        opt1 = f"│  {ConsoleColors.GREEN}[1]{ConsoleColors.RESET} Resolver Problema"
        opt1_padded = TUIFormatter.pad_line(opt1, 69)
        print(opt1_padded + " │")
        print("│      ├─ Desde archivo de texto" + " " * 39 + "│")
        print("│      ├─ Entrada manual (interactivo)" + " " * 33 + "│")
        print("│      └─ Procesamiento con IA (NLP)" + " " * 35 + "│")
        print("│" + " " * 70 + "│")

        opt2 = f"│  {ConsoleColors.GREEN}[2]{ConsoleColors.RESET} Análisis y Reportes"
        opt2_padded = TUIFormatter.pad_line(opt2, 69)
        print(opt2_padded + " │")
        print("│      ├─ Historial de problemas resueltos" + " " * 28 + "│")
        print("│      └─ Logs del sistema" + " " * 45 + "│")
        print("│" + " " * 70 + "│")

        opt3 = f"│  {ConsoleColors.GREEN}[3]{ConsoleColors.RESET} Utilidades"
        opt3_padded = TUIFormatter.pad_line(opt3, 69)
        print(opt3_padded + " │")
        print("│      ├─ Configuración de IA" + " " * 42 + "│")
        print("│      ├─ Ver ejemplos disponibles" + " " * 36 + "│")
        print("│      └─ Información del sistema" + " " * 38 + "│")
        print("│" + " " * 70 + "│")

        opt4 = f"│  {ConsoleColors.GREEN}[4]{ConsoleColors.RESET} Ayuda"
        opt4_padded = TUIFormatter.pad_line(opt4, 69)
        print(opt4_padded + " │")
        print("│" + " " * 70 + "│")

        opt0 = f"│  {ConsoleColors.GREEN}[0]{ConsoleColors.RESET} Salir"
        opt0_padded = TUIFormatter.pad_line(opt0, 69)
        print(opt0_padded + " │")
        print("│" + " " * 70 + "│")
        print("└" + "─" * 70 + "┘\n")

        # Barra de estado
        self._show_status_bar()

    def _show_status_bar(self):
        """Muestra la barra de estado del sistema."""
        python_version = platform.python_version()
        os_name = platform.system()

        # Contar problemas en historial
        try:
            from simplex_solver.problem_history import ProblemHistory

            history = ProblemHistory()
            problems = history.get_all_problems(limit=1000)
            num_problems = len(problems)
        except Exception:
            num_problems = 0

        # Tamaño de logs
        logs_path = self._get_logs_path()
        if os.path.exists(logs_path):
            log_size_kb = os.path.getsize(logs_path) / 1024
            log_info = f"{log_size_kb:.1f} KB"
        else:
            log_info = "N/A"

        status = (
            f"Sistema: {os_name} │ "
            f"Python: {python_version} │ "
            f"Logs: {log_info} │ "
            f"Historial: {num_problems} problemas"
        )

        print(f"{ConsoleColors.CYAN}{status}{ConsoleColors.RESET}\n")

    def _get_choice(self) -> str:
        """Obtiene la elección del usuario."""
        return self.ui.get_input("Opción").strip()

    def _handle_main_menu_choice(self, choice: str):
        """Maneja la elección del menú principal."""
        if choice == "1":
            self._show_solve_submenu()
        elif choice == "2":
            self._show_analysis_submenu()
        elif choice == "3":
            self._show_utilities_submenu()
        elif choice == "4":
            self._show_help()
        elif choice == "0":
            self._option_exit()
        else:
            self.ui.print_error("✗ Opción no válida. Selecciona un número del 0 al 4.")
            self.ui.pause()

    # ========================================================================
    # SUBMENÚ 1: RESOLVER PROBLEMA
    # ========================================================================

    def _show_solve_submenu(self):
        """Muestra el submenú de resolver problema."""
        while True:
            self.ui.clear_screen()

            print("┌" + "─" * 70 + "┐")
            title = f"│ {ConsoleColors.BOLD}RESOLVER PROBLEMA{ConsoleColors.RESET}"
            title_padded = TUIFormatter.pad_line(title, 69)
            print(title_padded + " │")
            print("└" + "─" * 70 + "┘\n")

            print("┌" + "─" * 70 + "┐")
            print("│ " + "Selecciona el método de entrada" + " " * 38 + "│")
            print("├" + "─" * 70 + "┤")
            print("│" + " " * 70 + "│")

            opt1 = f"│  {ConsoleColors.GREEN}[1]{ConsoleColors.RESET} Cargar desde Archivo"
            opt1_padded = TUIFormatter.pad_line(opt1, 69)
            print(opt1_padded + " │")
            print(
                "│      Lee un problema de programación lineal desde un archivo .txt"
                + " " * 3
                + "│"
            )
            print("│" + " " * 70 + "│")

            opt2 = f"│  {ConsoleColors.GREEN}[2]{ConsoleColors.RESET} Entrada Manual (Interactivo)"
            opt2_padded = TUIFormatter.pad_line(opt2, 69)
            print(opt2_padded + " │")
            print("│      Ingresa el problema paso a paso a través de la consola" + " " * 9 + "│")
            print("│" + " " * 70 + "│")

            opt3 = f"│  {ConsoleColors.GREEN}[3]{ConsoleColors.RESET} Usar Procesamiento NLP (IA)"
            opt3_padded = TUIFormatter.pad_line(opt3, 69)
            print(opt3_padded + " │")
            print("│      Describe el problema en lenguaje natural con Ollama" + " " * 12 + "│")
            print("│" + " " * 70 + "│")

            opt0 = f"│  {ConsoleColors.GREEN}[0]{ConsoleColors.RESET} Volver al Menú Principal"
            opt0_padded = TUIFormatter.pad_line(opt0, 69)
            print(opt0_padded + " │")
            print("│" + " " * 70 + "│")
            print("└" + "─" * 70 + "┘\n")

            choice = self._get_choice()

            if choice == "1":
                self._option_solve_from_file()
            elif choice == "2":
                self._option_interactive_mode()
            elif choice == "3":
                self._option_solve_with_ai()
            elif choice == "0":
                break
            else:
                self.ui.print_error("Opción no válida")
                self.ui.pause()

    def _option_solve_from_file(self):
        """
        Opción: Resolver problema desde archivo.

        Solicita ruta del archivo, valida su existencia y resuelve el problema.
        """
        self.ui.clear_screen()
        self.ui.print_section("Resolver problema desde archivo")

        # Pedir ruta del archivo
        file_path = self.ui.get_input("Ingresa la ruta del archivo (o arrastra el archivo aquí)")

        # Limpiar comillas si el usuario arrastró el archivo
        file_path = file_path.strip('"').strip("'")

        if not file_path:
            self.ui.print_error("No se proporcionó ningún archivo")
            self.ui.pause()
            return

        if not os.path.exists(file_path):
            self.ui.print_error(f"El archivo no existe: {file_path}")
            self.ui.pause()
            return

        self.ui.print_success(f"Archivo encontrado: {file_path}")

        # Preguntar opciones adicionales
        print(f"\n{ConsoleColors.WHITE}Opciones adicionales:{ConsoleColors.RESET}")

        gen_pdf = self.ui.ask_yes_no("¿Generar reporte PDF?", default=False)
        sensitivity = self.ui.ask_yes_no("¿Mostrar análisis de sensibilidad?", default=False)

        # Construir argumentos
        args = [file_path]

        if gen_pdf:
            pdf_name = self.ui.get_input("Nombre del PDF", default="reporte.pdf")
            if not pdf_name.endswith(".pdf"):
                pdf_name += ".pdf"
            args.extend(["--pdf", pdf_name])

        if sensitivity:
            args.append("--sensitivity")

        print(f"\n{ConsoleColors.CYAN}{'='*70}{ConsoleColors.RESET}\n")

        # Importar y ejecutar
        from simplex_solver.main import ApplicationOrchestrator, create_parser

        parser = create_parser()
        parsed_args = parser.parse_args(args)
        orchestrator = ApplicationOrchestrator()

        try:
            orchestrator.run(parsed_args)
        except SystemExit:
            pass  # Capturar sys.exit() del solver

        self.ui.pause()

    def _option_interactive_mode(self):
        """Opción: Modo interactivo."""
        self.ui.clear_screen()
        self.ui.print_section("Modo Interactivo")

        from simplex_solver.main import ApplicationOrchestrator, create_parser

        parser = create_parser()
        parsed_args = parser.parse_args(["--interactive"])
        orchestrator = ApplicationOrchestrator()

        try:
            orchestrator.run(parsed_args)
        except SystemExit:
            pass

        self.ui.pause()

    def _option_solve_with_ai(self):
        """Opción: Resolver con procesamiento NLP/IA."""
        self.ui.clear_screen()
        self.ui.print_section("Procesamiento con IA (NLP)")

        # Verificar Ollama
        try:
            result = subprocess.run(
                ["ollama", "list"], capture_output=True, text=True, timeout=3, check=False
            )

            if result.returncode != 0:
                self.ui.print_error("Ollama no está disponible")
                self.ui.print_info("Instala Ollama desde: https://ollama.ai/download")
                self.ui.pause()
                return
        except FileNotFoundError:
            self.ui.print_error("Ollama no está instalado en el sistema")
            self.ui.print_info("Instala Ollama desde: https://ollama.ai/download")
            self.ui.pause()
            return
        except Exception as e:
            self.ui.print_error(f"Error al verificar Ollama: {e}")
            self.ui.pause()
            return

        # Solicitar descripción del problema
        print(
            f"\n{ConsoleColors.WHITE}Describe el problema en lenguaje natural:{ConsoleColors.RESET}"
        )
        print("Ejemplo: 'Maximizar 3x + 2y sujeto a 2x + y <= 100, x + y <= 80'\n")

        description = self.ui.get_input("Descripción del problema")

        if not description:
            self.ui.print_error("No se proporcionó descripción")
            self.ui.pause()
            return

        # Crear archivo temporal con la descripción
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as tmp:
            tmp.write(description)
            tmp_path = tmp.name

        try:
            # Preguntar si desea generar PDF
            print(f"\n{ConsoleColors.WHITE}Opciones adicionales:{ConsoleColors.RESET}")
            gen_pdf = self.ui.ask_yes_no("¿Generar reporte PDF?", default=False)

            # Construir argumentos
            args = ["--nlp", tmp_path]

            if gen_pdf:
                pdf_name = self.ui.get_input("Nombre del PDF", default="reporte_ia.pdf")
                if not pdf_name.endswith(".pdf"):
                    pdf_name += ".pdf"
                args.extend(["--pdf", pdf_name])

            print(f"\n{ConsoleColors.CYAN}{'='*70}{ConsoleColors.RESET}\n")

            # Importar y ejecutar
            from simplex_solver.main import ApplicationOrchestrator, create_parser

            parser = create_parser()
            parsed_args = parser.parse_args(args)
            orchestrator = ApplicationOrchestrator()

            orchestrator.run(parsed_args)

        except SystemExit:
            pass
        finally:
            # Limpiar archivo temporal
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

        self.ui.pause()

    # ========================================================================
    # SUBMENÚ 2: ANÁLISIS Y REPORTES
    # ========================================================================

    def _show_analysis_submenu(self):
        """Muestra el submenú de análisis y reportes."""
        while True:
            self.ui.clear_screen()

            print("┌" + "─" * 70 + "┐")
            title = f"│ {ConsoleColors.BOLD}ANÁLISIS Y REPORTES{ConsoleColors.RESET}"
            title_padded = TUIFormatter.pad_line(title, 69)
            print(title_padded + " │")
            print("└" + "─" * 70 + "┘\n")

            print("┌" + "─" * 70 + "┐")
            print("│" + " " * 70 + "│")

            opt1 = (
                f"│  {ConsoleColors.GREEN}[1]{ConsoleColors.RESET} Historial de Problemas Resueltos"
            )
            opt1_padded = TUIFormatter.pad_line(opt1, 69)
            print(opt1_padded + " │")
            print("│      Ver, buscar y re-resolver problemas anteriores" + " " * 17 + "│")
            print("│" + " " * 70 + "│")

            opt2 = f"│  {ConsoleColors.GREEN}[2]{ConsoleColors.RESET} Logs del Sistema"
            opt2_padded = TUIFormatter.pad_line(opt2, 69)
            print(opt2_padded + " │")
            print("│      Visor interactivo de logs con filtros y búsqueda" + " " * 15 + "│")
            print("│" + " " * 70 + "│")

            opt0 = f"│  {ConsoleColors.GREEN}[0]{ConsoleColors.RESET} Volver al Menú Principal"
            opt0_padded = TUIFormatter.pad_line(opt0, 69)
            print(opt0_padded + " │")
            print("│" + " " * 70 + "│")
            print("└" + "─" * 70 + "┘\n")

            choice = self._get_choice()

            if choice == "1":
                self._option_view_history()
            elif choice == "2":
                self._option_view_logs()
            elif choice == "0":
                break
            else:
                self.ui.print_error("Opción no válida")
                self.ui.pause()

    def _option_view_history(self):
        """Opción: Ver historial de problemas resueltos."""
        self.ui.clear_screen()
        self.ui.print_section("Historial de Problemas Resueltos")

        from simplex_solver.main import ApplicationOrchestrator, create_parser

        parser = create_parser()
        parsed_args = parser.parse_args(["--history"])
        orchestrator = ApplicationOrchestrator()

        try:
            orchestrator.run(parsed_args)
        except SystemExit:
            pass

        self.ui.pause()

    def _option_view_logs(self):
        """Opción: Ver logs del sistema."""
        self.ui.clear_screen()
        self.ui.print_section("Visor de Logs del Sistema")

        try:
            from simplex_solver.log_viewer import LogViewer

            logs_path = self._get_logs_path()

            if not os.path.exists(logs_path):
                self.ui.print_warning("No se encontró la base de datos de logs")
                self.ui.print_info("Ejecuta el programa al menos una vez para crear los logs.")
                self.ui.pause()
                return

            viewer = LogViewer(logs_path)
            viewer.show_menu()
        except ImportError as e:
            self.ui.print_error(f"Error al importar el visor de logs: {e}")
        except FileNotFoundError as e:
            self.ui.print_error(f"Error: {e}")
            self.ui.print_info("Puedes acceder directamente a la base de datos en:")
            logs_path = self._get_logs_path()
            print(f"{ConsoleColors.CYAN}{logs_path}{ConsoleColors.RESET}")
        except Exception as e:
            self.ui.print_error(f"Error al abrir el visor de logs: {e}")
            self.ui.print_info("Puedes acceder directamente a la base de datos en:")
            logs_path = self._get_logs_path()
            print(f"{ConsoleColors.CYAN}{logs_path}{ConsoleColors.RESET}")

        self.ui.pause()

    # ========================================================================
    # SUBMENÚ 3: UTILIDADES
    # ========================================================================

    def _show_utilities_submenu(self):
        """Muestra el submenú de utilidades."""
        while True:
            self.ui.clear_screen()

            print("┌" + "─" * 70 + "┐")
            title = f"│ {ConsoleColors.BOLD}UTILIDADES{ConsoleColors.RESET}"
            title_padded = TUIFormatter.pad_line(title, 69)
            print(title_padded + " │")
            print("└" + "─" * 70 + "┘\n")

            print("┌" + "─" * 70 + "┐")
            print("│" + " " * 70 + "│")

            opt1 = f"│  {ConsoleColors.GREEN}[1]{ConsoleColors.RESET} Configuración de IA"
            opt1_padded = TUIFormatter.pad_line(opt1, 69)
            print(opt1_padded + " │")
            print("│      Listar y seleccionar modelos de Ollama" + " " * 25 + "│")
            print("│" + " " * 70 + "│")

            opt2 = f"│  {ConsoleColors.GREEN}[2]{ConsoleColors.RESET} Ver Ejemplos Disponibles"
            opt2_padded = TUIFormatter.pad_line(opt2, 69)
            print(opt2_padded + " │")
            print("│      Lista de archivos de ejemplo incluidos" + " " * 25 + "│")
            print("│" + " " * 70 + "│")

            opt3 = f"│  {ConsoleColors.GREEN}[3]{ConsoleColors.RESET} Información del Sistema"
            opt3_padded = TUIFormatter.pad_line(opt3, 69)
            print(opt3_padded + " │")
            print("│      Ubicaciones, versión y configuración" + " " * 27 + "│")
            print("│" + " " * 70 + "│")

            opt0 = f"│  {ConsoleColors.GREEN}[0]{ConsoleColors.RESET} Volver al Menú Principal"
            opt0_padded = TUIFormatter.pad_line(opt0, 69)
            print(opt0_padded + " │")
            print("│" + " " * 70 + "│")
            print("└" + "─" * 70 + "┘\n")

            choice = self._get_choice()

            if choice == "1":
                self._option_ai_configuration()
            elif choice == "2":
                self._option_view_examples()
            elif choice == "3":
                self._option_system_info()
            elif choice == "0":
                break
            else:
                self.ui.print_error("Opción no válida")
                self.ui.pause()

    def _option_ai_configuration(self):
        """Opción: Configuración de IA."""
        self.ui.clear_screen()
        self.ui.print_section("Configuración de IA")

        # Verificar si Ollama está instalado
        try:
            result = subprocess.run(
                ["ollama", "list"], capture_output=True, text=True, timeout=5, check=False
            )

            if result.returncode != 0:
                self.ui.print_error("Ollama no está disponible")
                self.ui.print_info("Instala Ollama desde: https://ollama.ai/download")
                self.ui.pause()
                return

            # Parsear la lista de modelos
            lines = result.stdout.strip().split("\n")
            if len(lines) <= 1:
                self.ui.print_warning("No hay modelos instalados")
                self.ui.print_info("Puedes instalar un modelo con: ollama pull <modelo>")
                self.ui.print_info("Modelos recomendados: llama3.2, mistral, phi3")
                self.ui.pause()
                return

            # Mostrar modelos disponibles (saltar la línea de encabezado)
            models = []
            self.ui.print_success("Modelos instalados:")
            print()
            for i, line in enumerate(lines[1:], 1):
                parts = line.split()
                if parts:
                    model_name = parts[0]
                    models.append(model_name)
                    print(
                        f"  {ConsoleColors.GREEN}{i}.{ConsoleColors.RESET} {ConsoleColors.CYAN}{model_name}{ConsoleColors.RESET}"
                    )

            print()

            # Cargar configuración actual
            config_path = self._get_config_path()
            current_model = self._load_current_model(config_path)

            if current_model:
                self.ui.print_info(f"Modelo actual: {current_model}")
            else:
                self.ui.print_info("No hay modelo configurado (se usará el predeterminado)")

            print()

            # Preguntar si quiere cambiar el modelo
            if not self.ui.ask_yes_no("¿Deseas cambiar el modelo de IA?", default=False):
                self.ui.pause()
                return

            # Solicitar selección
            while True:
                choice = self.ui.get_input(
                    f"Selecciona un modelo (1-{len(models)}) o 0 para cancelar"
                )

                if choice == "0":
                    self.ui.print_info("Operación cancelada")
                    self.ui.pause()
                    return

                try:
                    idx = int(choice) - 1
                    if 0 <= idx < len(models):
                        selected_model = models[idx]

                        # Guardar configuración
                        if self._save_model_config(config_path, selected_model):
                            self.ui.print_success(f"Modelo configurado: {selected_model}")
                            self.ui.print_info(
                                "El nuevo modelo se usará en las próximas ejecuciones"
                            )
                        else:
                            self.ui.print_error("No se pudo guardar la configuración")

                        self.ui.pause()
                        return
                    else:
                        self.ui.print_warning(
                            f"Por favor selecciona un número entre 1 y {len(models)}"
                        )
                except ValueError:
                    self.ui.print_warning("Por favor ingresa un número válido")

        except FileNotFoundError:
            self.ui.print_error("Ollama no está instalado en el sistema")
            self.ui.print_info("Instala Ollama desde: https://ollama.ai/download")
        except subprocess.TimeoutExpired:
            self.ui.print_error("Timeout al conectar con Ollama")
            self.ui.print_info("Verifica que Ollama esté funcionando correctamente")
        except Exception as e:
            self.ui.print_error(f"Error al acceder a la configuración de IA: {e}")

        self.ui.pause()

    def _option_view_examples(self):
        """Opción: Ver ejemplos disponibles."""
        self.ui.clear_screen()
        self.ui.print_section("Ejemplos Disponibles")

        # Buscar carpeta de ejemplos
        examples_dirs = [
            Path("ejemplos"),
            Path(__file__).parent.parent / "ejemplos",
        ]

        examples_dir = None
        for dir_path in examples_dirs:
            if dir_path.exists() and dir_path.is_dir():
                examples_dir = dir_path
                break

        if not examples_dir:
            self.ui.print_error("No se encontró la carpeta de ejemplos")
            self.ui.pause()
            return

        # Listar archivos .txt
        example_files = sorted(examples_dir.glob("*.txt"))

        if not example_files:
            self.ui.print_warning("No se encontraron archivos de ejemplo")
            self.ui.pause()
            return

        self.ui.print_info("Archivos de ejemplo encontrados:\n")

        for i, file in enumerate(example_files, 1):
            size = file.stat().st_size
            print(
                f"  {ConsoleColors.GREEN}{i:2}.{ConsoleColors.RESET} {ConsoleColors.CYAN}{file.name:<40}{ConsoleColors.RESET} ({size} bytes)"
            )

        print()
        self.ui.print_info("Para ejecutar un ejemplo:")
        print(f"  • Selecciona la opción 1 del menú principal")
        print(f"  • Luego opción 1 (Cargar desde Archivo)")
        print(
            f"  • Ingresa la ruta: {ConsoleColors.CYAN}{examples_dir / 'nombre_archivo.txt'}{ConsoleColors.RESET}"
        )

        self.ui.pause()

    def _option_system_info(self):
        """Opción: Información del sistema."""
        self.ui.clear_screen()

        print("┌" + "─" * 70 + "┐")
        print(
            "│ "
            + f"{ConsoleColors.BOLD}INFORMACIÓN DEL SISTEMA{ConsoleColors.RESET}"
            + " " * 46
            + "│"
        )
        print("└" + "─" * 70 + "┘\n")

        # Información del sistema
        print("┌" + "─" * 70 + "┐")
        print("│ " + f"{ConsoleColors.BOLD}Sistema Operativo{ConsoleColors.RESET}" + " " * 52 + "│")
        print("├" + "─" * 70 + "┤")
        print("│" + " " * 70 + "│")

        os_name = platform.system()
        os_release = platform.release()
        os_line = f"  Sistema:  {os_name} {os_release}"
        print(f"│{os_line:<70}│")

        python_version = platform.python_version()
        py_line = f"  Python:   {python_version}"
        print(f"│{py_line:<70}│")

        print("│" + " " * 70 + "│")
        print("└" + "─" * 70 + "┘\n")

        # Ubicaciones de datos
        print("┌" + "─" * 70 + "┐")
        print(
            "│ " + f"{ConsoleColors.BOLD}Ubicaciones de Datos{ConsoleColors.RESET}" + " " * 49 + "│"
        )
        print("├" + "─" * 70 + "┤")
        print("│" + " " * 70 + "│")

        logs_path = self._get_logs_path()
        logs_dir = os.path.dirname(logs_path)
        logs_line = f"  Logs:     {TUIFormatter.truncate_text(logs_dir, 54)}"
        print(f"│{logs_line:<70}│")

        reports_dir = os.path.dirname(logs_path).replace("logs", "reports")
        reports_line = f"  Reportes: {TUIFormatter.truncate_text(reports_dir, 54)}"
        print(f"│{reports_line:<70}│")

        config_path = self._get_config_path()
        config_dir = os.path.dirname(str(config_path))
        config_line = f"  Config:   {TUIFormatter.truncate_text(config_dir, 54)}"
        print(f"│{config_line:<70}│")

        print("│" + " " * 70 + "│")
        print("└" + "─" * 70 + "┘\n")

        # Versión
        print("┌" + "─" * 70 + "┐")
        print(
            "│ " + f"{ConsoleColors.BOLD}Versión del Software{ConsoleColors.RESET}" + " " * 49 + "│"
        )
        print("├" + "─" * 70 + "┤")
        print("│" + " " * 70 + "│")
        print("│  Simplex Solver: v2.0" + " " * 48 + "│")
        print("│  TUI Version:    v2.0 (Diseño profesional)" + " " * 27 + "│")
        print("│" + " " * 70 + "│")
        print("└" + "─" * 70 + "┘\n")

        # Estado de componentes
        print("┌" + "─" * 70 + "┐")
        print(
            "│ "
            + f"{ConsoleColors.BOLD}Estado de Componentes{ConsoleColors.RESET}"
            + " " * 48
            + "│"
        )
        print("├" + "─" * 70 + "┤")
        print("│" + " " * 70 + "│")

        # Verificar Ollama
        try:
            result = subprocess.run(
                ["ollama", "list"], capture_output=True, text=True, timeout=2, check=False
            )
            ollama_status = "● Disponible" if result.returncode == 0 else "✗ No disponible"
        except Exception:
            ollama_status = "✗ No instalado"

        ollama_line = f"  Ollama (IA):    {ollama_status}"
        print(f"│{ollama_line:<70}│")

        # Verificar base de datos de logs
        if os.path.exists(logs_path):
            db_status = "● Activa"
        else:
            db_status = "○ No creada"

        db_line = f"  Base de Datos:  {db_status}"
        print(f"│{db_line:<70}│")

        print("│" + " " * 70 + "│")
        print("└" + "─" * 70 + "┘\n")

        self.ui.pause()

    # ========================================================================
    # AYUDA
    # ========================================================================

    def _show_help(self):
        """Muestra la ayuda y documentación."""
        self.ui.clear_screen()

        print("┌" + "─" * 70 + "┐")
        print(
            "│ "
            + f"{ConsoleColors.BOLD}AYUDA Y DOCUMENTACIÓN{ConsoleColors.RESET}"
            + " " * 48
            + "│"
        )
        print("└" + "─" * 70 + "┘\n")

        print(
            f"{ConsoleColors.WHITE}SIMPLEX SOLVER - Sistema de Programación Lineal{ConsoleColors.RESET}\n"
        )

        self.ui.print_success("Uso básico:")
        print(f"  1. Selecciona la opción 1 para resolver un problema")
        print(f"  2. Elige el método de entrada (archivo, manual o IA)")
        print(f"  3. El programa mostrará el paso a paso del método Simplex\n")

        self.ui.print_success("Formato de archivos:")
        print(f"  • Primera línea: 'MAX' o 'MIN'")
        print(f"  • Segunda línea: 'SUBJECT TO'")
        print(f"  • Tercera línea: Coeficientes de la función objetivo")
        print(f"  • Líneas siguientes: Restricciones en formato:")
        print(f"    coef1 coef2 ... coefN <= valor  (o >=, =)\n")

        self.ui.print_success("Ejemplo:")
        print(f"  {ConsoleColors.CYAN}MAX")
        print(f"  SUBJECT TO")
        print(f"  3 2")
        print(f"  2 1 <= 100")
        print(f"  1 1 <= 80{ConsoleColors.RESET}\n")

        self.ui.print_success("Documentación completa:")
        docs_files = [
            ("README.md", "Guía general del proyecto"),
            ("GUIA_USUARIO.md", "Guía completa para usuarios"),
            ("GUIA_DESARROLLADOR.md", "Guía para desarrolladores"),
        ]

        for doc_file, description in docs_files:
            doc_path = Path(__file__).parent.parent / doc_file
            if doc_path.exists():
                print(
                    f"  • {ConsoleColors.CYAN}{doc_file:<25}{ConsoleColors.RESET} - {description}"
                )

        print()
        self.ui.print_success("Características avanzadas:")
        print(f"  • Análisis de sensibilidad (precios sombra, rangos)")
        print(f"  • Generación de reportes PDF")
        print(f"  • Historial de problemas resueltos con búsqueda")
        print(f"  • Sistema de logging completo con filtros")
        print(f"  • Validación automática de soluciones")
        print(f"  • Procesamiento con IA (Ollama)")

        print()
        self.ui.pause()

    # ========================================================================
    # SALIR
    # ========================================================================

    def _option_exit(self):
        """Opción: Salir del programa."""
        self.ui.clear_screen()
        self.ui.print_success("\n¡Gracias por usar Simplex Solver v2.0!\n")
        self.running = False

    # ========================================================================
    # MÉTODOS AUXILIARES
    # ========================================================================

    def _get_logs_path(self) -> str:
        """
        Obtiene la ruta completa de la base de datos de logs.

        Returns:
            str: Ruta absoluta al archivo de base de datos de logs
        """
        if platform.system() == "Windows":
            appdata = os.getenv("APPDATA", "")
            logs_dir = os.path.join(appdata, "SimplexSolver", "logs")
        else:
            home = os.path.expanduser("~")
            logs_dir = os.path.join(home, ".simplex_solver", "logs")

        return os.path.join(logs_dir, "simplex_logs.db")

    def _get_config_path(self) -> Path:
        """
        Obtiene la ruta del archivo de configuración.

        Returns:
            Path: Ruta al archivo de configuración
        """
        if platform.system() == "Windows":
            appdata = os.getenv("APPDATA", "")
            config_dir = Path(appdata) / "SimplexSolver"
        else:
            home = os.path.expanduser("~")
            config_dir = Path(home) / ".simplex_solver"

        config_dir.mkdir(parents=True, exist_ok=True)
        return config_dir / "config.json"

    def _load_current_model(self, config_path: Path) -> Optional[str]:
        """
        Carga el modelo actual desde la configuración.

        Args:
            config_path: Ruta al archivo de configuración

        Returns:
            Optional[str]: Nombre del modelo configurado o None
        """
        try:
            if config_path.exists():
                with open(config_path, "r", encoding="utf-8") as f:
                    config = json.load(f)
                    return config.get("ai_model")
        except Exception:
            pass
        return None

    def _save_model_config(self, config_path: Path, model_name: str) -> bool:
        """
        Guarda el modelo seleccionado en la configuración.

        Args:
            config_path: Ruta al archivo de configuración
            model_name: Nombre del modelo a guardar

        Returns:
            bool: True si se guardó correctamente, False en caso contrario
        """
        try:
            # Cargar configuración existente o crear nueva
            config = {}
            if config_path.exists():
                with open(config_path, "r", encoding="utf-8") as f:
                    config = json.load(f)

            # Actualizar modelo
            config["ai_model"] = model_name

            # Guardar
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2)

            return True
        except Exception as e:
            logger.error(f"Error al guardar configuración: {e}")
            return False


# ========================================================================
# FUNCIÓN DE ENTRADA
# ========================================================================


def show_menu():
    """
    Función principal para inicializar y mostrar el menú interactivo.

    Crea una instancia de SimplexMenu y ejecuta su bucle principal.
    Esta es la función que debe ser llamada desde main.py cuando
    no se proporcionan argumentos de línea de comandos.
    """
    menu = SimplexMenu()
    menu.run()


if __name__ == "__main__":
    show_menu()
