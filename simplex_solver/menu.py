"""
Menú interactivo principal del Simplex Solver.
Proporciona acceso a todas las funcionalidades del sistema.
"""

import os
import sys
import platform
from pathlib import Path
from typing import Optional
from simplex_solver.logging_system import logger


class Color:
    """Códigos de color para la consola."""

    RESET = "\033[0m"
    BOLD = "\033[1m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"


def enable_ansi_colors():
    """Habilita los códigos ANSI en Windows 10+."""
    if platform.system() == "Windows":
        try:
            import ctypes

            kernel32 = ctypes.windll.kernel32
            kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
        except Exception:
            pass


class SimplexMenu:
    """Menú interactivo principal del Simplex Solver."""

    def __init__(self):
        enable_ansi_colors()
        self.running = True

    def clear_screen(self):
        """Limpia la pantalla de la consola."""
        os.system("cls" if os.name == "nt" else "clear")

    def print_header(self):
        """Imprime el encabezado del menú."""
        print(f"{Color.CYAN}{'='*70}{Color.RESET}")
        print(f"{Color.CYAN}{Color.BOLD}{'SIMPLEX SOLVER - Menú Principal':^70}{Color.RESET}")
        print(f"{Color.CYAN}{'='*70}{Color.RESET}")

    def print_menu_options(self):
        """Imprime las opciones del menú."""
        print(f"\n{Color.WHITE}Opciones disponibles:{Color.RESET}\n")
        print(f"  {Color.GREEN}1.{Color.RESET} Resolver problema desde archivo")
        print(f"  {Color.GREEN}2.{Color.RESET} Modo interactivo (ingresar problema manualmente)")
        print(f"  {Color.GREEN}3.{Color.RESET} Ver historial de problemas resueltos")
        print(f"  {Color.GREEN}4.{Color.RESET} Ver logs del sistema")
        print(f"  {Color.GREEN}5.{Color.RESET} Ver ubicación de logs")
        print(f"  {Color.GREEN}6.{Color.RESET} Ver ejemplos disponibles")
        print(f"  {Color.GREEN}7.{Color.RESET} Ayuda y documentación")
        print(f"  {Color.GREEN}0.{Color.RESET} Salir")
        print(f"\n{Color.CYAN}{'-'*70}{Color.RESET}")

    def get_user_choice(self) -> str:
        """Obtiene la elección del usuario."""
        try:
            choice = input(f"\n{Color.YELLOW}Selecciona una opción: {Color.RESET}").strip()
            return choice
        except (KeyboardInterrupt, EOFError):
            return "0"

    def pause(self, message: str = "Presiona Enter para continuar..."):
        """Pausa la ejecución hasta que el usuario presione Enter."""
        try:
            input(f"\n{Color.CYAN}{message}{Color.RESET}")
        except (KeyboardInterrupt, EOFError):
            pass

    def option_solve_file(self):
        """Opción 1: Resolver problema desde archivo."""
        self.clear_screen()
        print(f"\n{Color.BLUE}{Color.BOLD}▶ Resolver problema desde archivo{Color.RESET}")
        print(f"{Color.CYAN}{'-'*70}{Color.RESET}\n")

        # Pedir ruta del archivo
        file_path = input(
            f"{Color.YELLOW}Ingresa la ruta del archivo (o arrastra el archivo aquí): {Color.RESET}"
        ).strip()

        # Limpiar comillas si el usuario arrastró el archivo
        file_path = file_path.strip('"').strip("'")

        if not file_path:
            print(f"\n{Color.RED}✗ No se proporcionó ningún archivo{Color.RESET}")
            self.pause()
            return

        if not os.path.exists(file_path):
            print(f"\n{Color.RED}✗ El archivo no existe: {file_path}{Color.RESET}")
            self.pause()
            return

        print(f"\n{Color.GREEN}✓ Archivo encontrado: {file_path}{Color.RESET}")

        # Preguntar opciones adicionales
        print(f"\n{Color.WHITE}Opciones adicionales:{Color.RESET}")

        gen_pdf = input(f"¿Generar reporte PDF? (s/N): {Color.RESET}").strip().lower()
        sensitivity = (
            input(f"¿Mostrar análisis de sensibilidad? (s/N): {Color.RESET}").strip().lower()
        )

        # Construir argumentos
        args = [file_path]

        if gen_pdf in ["s", "si", "sí", "y", "yes"]:
            pdf_name = input(f"Nombre del PDF (Enter para 'reporte.pdf'): {Color.RESET}").strip()
            if not pdf_name:
                pdf_name = "reporte.pdf"
            if not pdf_name.endswith(".pdf"):
                pdf_name += ".pdf"
            args.extend(["--pdf", pdf_name])

        if sensitivity in ["s", "si", "sí", "y", "yes"]:
            args.append("--sensitivity")

        print(f"\n{Color.CYAN}{'='*70}{Color.RESET}\n")

        # Importar y ejecutar
        from simplex_solver.main import ApplicationOrchestrator, create_parser

        parser = create_parser()
        parsed_args = parser.parse_args(args)
        orchestrator = ApplicationOrchestrator()

        try:
            orchestrator.run(parsed_args)
        except SystemExit:
            pass  # Capturar sys.exit() del solver

        self.pause()

    def option_interactive_mode(self):
        """Opción 2: Modo interactivo."""
        self.clear_screen()
        print(f"\n{Color.BLUE}{Color.BOLD}▶ Modo Interactivo{Color.RESET}")
        print(f"{Color.CYAN}{'-'*70}{Color.RESET}\n")

        from simplex_solver.main import ApplicationOrchestrator, create_parser

        parser = create_parser()
        parsed_args = parser.parse_args(["--interactive"])
        orchestrator = ApplicationOrchestrator()

        try:
            orchestrator.run(parsed_args)
        except SystemExit:
            pass

        self.pause()

    def option_view_history(self):
        """Opción 3: Ver historial."""
        self.clear_screen()
        print(f"\n{Color.BLUE}{Color.BOLD}▶ Historial de Problemas Resueltos{Color.RESET}")
        print(f"{Color.CYAN}{'-'*70}{Color.RESET}\n")

        from simplex_solver.main import ApplicationOrchestrator, create_parser

        parser = create_parser()
        parsed_args = parser.parse_args(["--history"])
        orchestrator = ApplicationOrchestrator()

        try:
            orchestrator.run(parsed_args)
        except SystemExit:
            pass

        self.pause()

    def option_view_logs(self):
        """Opción 4: Ver logs del sistema."""
        self.clear_screen()
        print(f"\n{Color.BLUE}{Color.BOLD}▶ Visor de Logs del Sistema{Color.RESET}")
        print(f"{Color.CYAN}{'-'*70}{Color.RESET}\n")

        try:
            from simplex_solver.log_viewer import LogViewer

            viewer = LogViewer()
            viewer.run()
        except ImportError as e:
            print(f"{Color.RED}✗ Error al importar el visor de logs: {e}{Color.RESET}")
        except Exception as e:
            print(f"{Color.RED}✗ Error al abrir el visor de logs: {e}{Color.RESET}")
            print(
                f"\n{Color.YELLOW}Puedes acceder directamente a la base de datos en:{Color.RESET}"
            )
            logs_path = self._get_logs_path()
            print(f"{Color.CYAN}{logs_path}{Color.RESET}")

        self.pause()

    def option_logs_location(self):
        """Opción 5: Ver ubicación de logs."""
        self.clear_screen()
        print(f"\n{Color.BLUE}{Color.BOLD}▶ Ubicación de Logs{Color.RESET}")
        print(f"{Color.CYAN}{'-'*70}{Color.RESET}\n")

        logs_path = self._get_logs_path()

        print(f"{Color.WHITE}La base de datos de logs se encuentra en:{Color.RESET}\n")
        print(f"  {Color.CYAN}{logs_path}{Color.RESET}\n")

        if os.path.exists(logs_path):
            size = os.path.getsize(logs_path)
            print(f"  {Color.GREEN}✓ Estado: Base de datos ENCONTRADA{Color.RESET}")
            print(f"  {Color.WHITE}Tamaño: {size:,} bytes ({size/1024:.2f} KB){Color.RESET}\n")
            print(f"{Color.WHITE}Puedes abrir este archivo con:{Color.RESET}")
            print(f"  • DB Browser for SQLite (https://sqlitebrowser.org/)")
            print(f"  • Cualquier cliente SQLite")
            print(f"  • O usar el visor integrado (opción 4 del menú)")
        else:
            print(f"  {Color.YELLOW}⚠ Estado: Base de datos NO ENCONTRADA{Color.RESET}")
            print(
                f"  {Color.WHITE}Ejecuta el programa al menos una vez para crear los logs.{Color.RESET}"
            )

        self.pause()

    def option_view_examples(self):
        """Opción 6: Ver ejemplos disponibles."""
        self.clear_screen()
        print(f"\n{Color.BLUE}{Color.BOLD}▶ Ejemplos Disponibles{Color.RESET}")
        print(f"{Color.CYAN}{'-'*70}{Color.RESET}\n")

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
            print(f"{Color.RED}✗ No se encontró la carpeta de ejemplos{Color.RESET}")
            self.pause()
            return

        # Listar archivos .txt
        example_files = sorted(examples_dir.glob("*.txt"))

        if not example_files:
            print(f"{Color.YELLOW}⚠ No se encontraron archivos de ejemplo{Color.RESET}")
            self.pause()
            return

        print(f"{Color.WHITE}Archivos de ejemplo encontrados:{Color.RESET}\n")

        for i, file in enumerate(example_files, 1):
            size = file.stat().st_size
            print(
                f"  {Color.GREEN}{i:2}.{Color.RESET} {Color.CYAN}{file.name:<40}{Color.RESET} ({size} bytes)"
            )

        print(f"\n{Color.WHITE}Para ejecutar un ejemplo:{Color.RESET}")
        print(f"  • Usa la opción 1 del menú")
        print(
            f"  • Ingresa la ruta: {Color.CYAN}{examples_dir / 'nombre_archivo.txt'}{Color.RESET}"
        )

        self.pause()

    def option_help(self):
        """Opción 7: Ayuda y documentación."""
        self.clear_screen()
        print(f"\n{Color.BLUE}{Color.BOLD}▶ Ayuda y Documentación{Color.RESET}")
        print(f"{Color.CYAN}{'-'*70}{Color.RESET}\n")

        print(f"{Color.WHITE}SIMPLEX SOLVER - Sistema de Programación Lineal{Color.RESET}\n")

        print(f"{Color.GREEN}Uso básico:{Color.RESET}")
        print(f"  1. Selecciona la opción 1 para resolver un archivo")
        print(f"  2. O usa la opción 2 para ingresar el problema manualmente")
        print(f"  3. El programa mostrará el paso a paso del método Simplex\n")

        print(f"{Color.GREEN}Formato de archivos:{Color.RESET}")
        print(f"  • Primera línea: 'MAX' o 'MIN'")
        print(f"  • Segunda línea: Coeficientes de la función objetivo")
        print(f"  • Líneas siguientes: Restricciones en formato:")
        print(f"    coef1 coef2 ... coefN <= valor  (o >=, =)\n")

        print(f"{Color.GREEN}Ejemplo:{Color.RESET}")
        print(f"  {Color.CYAN}MAX")
        print(f"  3 2")
        print(f"  2 1 <= 100")
        print(f"  1 1 <= 80{Color.RESET}\n")

        print(f"{Color.GREEN}Documentación:{Color.RESET}")
        docs_files = [
            ("README.md", "Guía general del proyecto"),
            ("GUIA_USUARIO.md", "Guía completa para usuarios"),
            ("GUIA_DESARROLLADOR.md", "Guía para desarrolladores"),
        ]

        for doc_file, description in docs_files:
            doc_path = Path(__file__).parent.parent / doc_file
            if doc_path.exists():
                print(f"  • {Color.CYAN}{doc_file:<25}{Color.RESET} - {description}")

        print(f"\n{Color.GREEN}Características avanzadas:{Color.RESET}")
        print(f"  • Análisis de sensibilidad (--sensitivity)")
        print(f"  • Generación de reportes PDF (--pdf)")
        print(f"  • Historial de problemas resueltos")
        print(f"  • Sistema de logging completo")
        print(f"  • Validación automática de soluciones")

        self.pause()

    def option_exit(self):
        """Opción 0: Salir del programa."""
        self.clear_screen()
        print(f"\n{Color.GREEN}¡Gracias por usar Simplex Solver!{Color.RESET}\n")
        self.running = False

    def _get_logs_path(self) -> str:
        """Obtiene la ruta de la base de datos de logs."""
        if platform.system() == "Windows":
            appdata = os.getenv("APPDATA", "")
            logs_dir = os.path.join(appdata, "SimplexSolver", "logs")
        else:
            home = os.path.expanduser("~")
            logs_dir = os.path.join(home, ".simplex_solver", "logs")

        return os.path.join(logs_dir, "simplex_logs.db")

    def run(self):
        """Ejecuta el menú principal."""
        logger.info("=== Iniciando Simplex Solver - Menú Interactivo ===")

        while self.running:
            self.clear_screen()
            self.print_header()
            self.print_menu_options()

            choice = self.get_user_choice()

            if choice == "1":
                self.option_solve_file()
            elif choice == "2":
                self.option_interactive_mode()
            elif choice == "3":
                self.option_view_history()
            elif choice == "4":
                self.option_view_logs()
            elif choice == "5":
                self.option_logs_location()
            elif choice == "6":
                self.option_view_examples()
            elif choice == "7":
                self.option_help()
            elif choice == "0":
                self.option_exit()
            else:
                print(
                    f"\n{Color.RED}✗ Opción no válida. Por favor, selecciona una opción del 0 al 7.{Color.RESET}"
                )
                self.pause("Presiona Enter para volver al menú...")

        logger.info("=== Finalizando Simplex Solver - Menú Interactivo ===")


def show_menu():
    """Función principal para mostrar el menú."""
    menu = SimplexMenu()
    menu.run()


if __name__ == "__main__":
    show_menu()
