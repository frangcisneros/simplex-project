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
from simplex_solver.ui import ConsoleUI, ConsoleColors, enable_ansi_colors


class SimplexMenu:
    """
    Menú interactivo principal del Simplex Solver.

    Proporciona una interfaz de usuario basada en texto con opciones para:
    - Resolver problemas desde archivos
    - Entrada interactiva de problemas
    - Visualización de historial
    - Gestión de logs
    - Acceso a documentación y ejemplos

    Attributes:
        running (bool): Controla el bucle principal del menú
    """

    def __init__(self):
        enable_ansi_colors()
        self.running = True
        self.ui = ConsoleUI()  # Instancia de la interfaz de consola

    def clear_screen(self):
        """Limpia la pantalla de la consola."""
        self.ui.clear_screen()

    def print_header(self):
        """Imprime el encabezado del menú."""
        self.ui.print_header("SIMPLEX SOLVER - Menú Principal")

    def print_menu_options(self):
        """
        Imprime las opciones del menú principal.

        Muestra una lista numerada de todas las opciones disponibles
        para el usuario, con formato colorizado para mejor legibilidad.
        """
        print(f"\n{ConsoleColors.WHITE}Opciones disponibles:{ConsoleColors.RESET}\n")
        print(f"  {ConsoleColors.GREEN}1.{ConsoleColors.RESET} Resolver problema desde archivo")
        print(
            f"  {ConsoleColors.GREEN}2.{ConsoleColors.RESET} Modo interactivo (ingresar problema manualmente)"
        )
        print(
            f"  {ConsoleColors.GREEN}3.{ConsoleColors.RESET} Ver historial de problemas resueltos"
        )
        print(f"  {ConsoleColors.GREEN}4.{ConsoleColors.RESET} Ver logs del sistema")
        print(f"  {ConsoleColors.GREEN}5.{ConsoleColors.RESET} Ver ubicación de logs")
        print(f"  {ConsoleColors.GREEN}6.{ConsoleColors.RESET} Ver ejemplos disponibles")
        print(f"  {ConsoleColors.GREEN}7.{ConsoleColors.RESET} Configuración de IA")
        print(f"  {ConsoleColors.GREEN}8.{ConsoleColors.RESET} Ayuda y documentación")
        print(f"  {ConsoleColors.GREEN}0.{ConsoleColors.RESET} Salir")
        print(f"\n{ConsoleColors.CYAN}{'-'*70}{ConsoleColors.RESET}")

    def get_user_choice(self) -> str:
        """
        Obtiene la elección del usuario desde la entrada estándar.

        Returns:
            str: La opción seleccionada por el usuario (sin espacios en blanco)

        Note:
            Si el usuario presiona Ctrl+C o Ctrl+D, retorna "0" para salir.
        """
        return self.ui.get_input("Selecciona una opción")

    def pause(self, message: str = "Presiona Enter para continuar..."):
        """
        Pausa la ejecución hasta que el usuario presione Enter.

        Args:
            message: Mensaje a mostrar al usuario mientras espera

        Note:
            Si el usuario presiona Ctrl+C o Ctrl+D, la función continúa
            sin error para permitir salir del menú de forma elegante.
        """
        self.ui.pause(message)

    def option_solve_file(self):
        """
        Opción 1: Resolver problema desde archivo.

        Solicita al usuario la ruta de un archivo con un problema de programación
        lineal, valida su existencia y permite configurar opciones adicionales
        como generación de PDF y análisis de sensibilidad.
        """
        self.clear_screen()
        self.ui.print_section("Resolver problema desde archivo")

        # Pedir ruta del archivo
        file_path = self.ui.get_input("Ingresa la ruta del archivo (o arrastra el archivo aquí)")

        # Limpiar comillas si el usuario arrastró el archivo
        file_path = file_path.strip('"').strip("'")

        if not file_path:
            self.ui.print_error("No se proporcionó ningún archivo")
            self.pause()
            return

        if not os.path.exists(file_path):
            self.ui.print_error(f"El archivo no existe: {file_path}")
            self.pause()
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

        self.pause()

    def option_interactive_mode(self):
        """
        Opción 2: Modo interactivo.

        Inicia el modo de entrada interactiva donde el usuario puede
        ingresar manualmente todos los datos del problema (función objetivo,
        restricciones, etc.) a través de la consola.
        """
        self.clear_screen()
        self.ui.print_section("Modo Interactivo")

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
        """
        Opción 3: Ver historial de problemas resueltos.

        Muestra el historial de todos los problemas que han sido resueltos
        exitosamente, permitiendo al usuario ver detalles y re-resolver
        problemas anteriores.
        """
        self.clear_screen()
        self.ui.print_section("Historial de Problemas Resueltos")

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
        """
        Opción 4: Ver logs del sistema.

        Abre el visor interactivo de logs que permite navegar por todos
        los registros del sistema, filtrar por nivel de severidad, buscar
        y exportar logs.
        """
        self.clear_screen()
        self.ui.print_section("Visor de Logs del Sistema")

        try:
            from simplex_solver.log_viewer import LogViewer

            logs_path = self._get_logs_path()

            if not os.path.exists(logs_path):
                self.ui.print_warning("No se encontró la base de datos de logs")
                self.ui.print_info("Ejecuta el programa al menos una vez para crear los logs.")
                self.pause()
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

        self.pause()

    def option_logs_location(self):
        """
        Opción 5: Ver ubicación de logs.

        Muestra la ruta completa donde se almacena la base de datos de logs,
        su tamaño y estado actual. Proporciona información sobre cómo acceder
        a los logs con herramientas externas.
        """
        self.clear_screen()
        self.ui.print_section("Ubicación de Logs")

        logs_path = self._get_logs_path()

        self.ui.print_info("La base de datos de logs se encuentra en:")
        print(f"  {ConsoleColors.CYAN}{logs_path}{ConsoleColors.RESET}\n")

        if os.path.exists(logs_path):
            size = os.path.getsize(logs_path)
            self.ui.print_success(f"Estado: Base de datos ENCONTRADA")
            print(
                f"  {ConsoleColors.WHITE}Tamaño: {size:,} bytes ({size/1024:.2f} KB){ConsoleColors.RESET}\n"
            )
            self.ui.print_info("Puedes abrir este archivo con:")
            print(f"  • DB Browser for SQLite (https://sqlitebrowser.org/)")
            print(f"  • Cualquier cliente SQLite")
            print(f"  • O usar el visor integrado (opción 4 del menú)")
        else:
            self.ui.print_warning("Estado: Base de datos NO ENCONTRADA")
            self.ui.print_info("Ejecuta el programa al menos una vez para crear los logs.")

        self.pause()

    def option_view_examples(self):
        """
        Opción 6: Ver ejemplos disponibles.

        Lista todos los archivos de ejemplo disponibles en el proyecto,
        mostrando sus nombres y tamaños. Proporciona instrucciones sobre
        cómo ejecutar estos ejemplos.
        """
        self.clear_screen()
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
            self.pause()
            return

        # Listar archivos .txt
        example_files = sorted(examples_dir.glob("*.txt"))

        if not example_files:
            self.ui.print_warning("No se encontraron archivos de ejemplo")
            self.pause()
            return

        self.ui.print_info("Archivos de ejemplo encontrados:")

        for i, file in enumerate(example_files, 1):
            size = file.stat().st_size
            print(
                f"  {ConsoleColors.GREEN}{i:2}.{ConsoleColors.RESET} {ConsoleColors.CYAN}{file.name:<40}{ConsoleColors.RESET} ({size} bytes)"
            )

        self.ui.print_info("\nPara ejecutar un ejemplo:")
        print(f"  • Usa la opción 1 del menú")
        print(
            f"  • Ingresa la ruta: {ConsoleColors.CYAN}{examples_dir / 'nombre_archivo.txt'}{ConsoleColors.RESET}"
        )

        self.pause()

    def option_ai_configuration(self):
        """
        Opción 7: Configuración de IA.

        Permite al usuario configurar los parámetros del sistema de IA,
        incluyendo la selección del modelo de Ollama a utilizar.
        """
        self.clear_screen()
        self.ui.print_section("Configuración de IA")

        # Verificar si Ollama está instalado
        try:
            import subprocess

            result = subprocess.run(["ollama", "list"], capture_output=True, text=True, timeout=5)

            if result.returncode != 0:
                self.ui.print_error("Ollama no está disponible")
                self.ui.print_info("Instala Ollama desde: https://ollama.ai/download")
                self.pause()
                return

            # Parsear la lista de modelos
            lines = result.stdout.strip().split("\n")
            if len(lines) <= 1:
                self.ui.print_warning("No hay modelos instalados")
                self.ui.print_info("Puedes instalar un modelo con: ollama pull <modelo>")
                self.ui.print_info("Modelos recomendados: llama3.2, mistral, phi3")
                self.pause()
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
                self.pause()
                return

            # Solicitar selección
            while True:
                choice = self.ui.get_input(
                    f"Selecciona un modelo (1-{len(models)}) o 0 para cancelar"
                )

                if choice == "0":
                    self.ui.print_info("Operación cancelada")
                    self.pause()
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

                        self.pause()
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

        self.pause()

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
                import json

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
            import json

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

    def option_help(self):
        """
        Opción 8: Ayuda y documentación.

        Muestra información completa sobre el uso del programa, incluyendo:
        - Formato de archivos de entrada
        - Ejemplos de uso
        - Características avanzadas disponibles
        - Referencias a documentación adicional
        """
        self.clear_screen()
        self.ui.print_section("Ayuda y Documentación")

        print(
            f"{ConsoleColors.WHITE}SIMPLEX SOLVER - Sistema de Programación Lineal{ConsoleColors.RESET}\n"
        )

        self.ui.print_success("Uso básico:")
        print(f"  1. Selecciona la opción 1 para resolver un archivo")
        print(f"  2. O usa la opción 2 para ingresar el problema manualmente")
        print(f"  3. El programa mostrará el paso a paso del método Simplex\n")

        self.ui.print_success("Formato de archivos:")
        print(f"  • Primera línea: 'MAX' o 'MIN'")
        print(f"  • Segunda línea: Coeficientes de la función objetivo")
        print(f"  • Líneas siguientes: Restricciones en formato:")
        print(f"    coef1 coef2 ... coefN <= valor  (o >=, =)\n")

        self.ui.print_success("Ejemplo:")
        print(f"  {ConsoleColors.CYAN}MAX")
        print(f"  3 2")
        print(f"  2 1 <= 100")
        print(f"  1 1 <= 80{ConsoleColors.RESET}\n")

        self.ui.print_success("Documentación:")
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

        self.ui.print_success("\nCaracterísticas avanzadas:")
        print(f"  • Análisis de sensibilidad (--sensitivity)")
        print(f"  • Generación de reportes PDF (--pdf)")
        print(f"  • Historial de problemas resueltos")
        print(f"  • Sistema de logging completo")
        print(f"  • Validación automática de soluciones")

        self.pause()

    def option_exit(self):
        """
        Opción 0: Salir del programa.

        Finaliza la ejecución del menú y cierra el programa de forma limpia,
        mostrando un mensaje de despedida al usuario.
        """
        self.clear_screen()
        self.ui.print_success("\n¡Gracias por usar Simplex Solver!\n")
        self.running = False

    def _get_logs_path(self) -> str:
        """
        Obtiene la ruta completa de la base de datos de logs.

        La ubicación varía según el sistema operativo:
        - Windows: %APPDATA%/SimplexSolver/logs/simplex_logs.db
        - Linux/macOS: ~/.simplex_solver/logs/simplex_logs.db

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

    def run(self):
        """
        Ejecuta el bucle principal del menú interactivo.

        Muestra el menú repetidamente hasta que el usuario seleccione
        la opción de salir. Maneja todas las opciones del menú y
        redirige a las funciones correspondientes.

        Note:
            Este método registra el inicio y fin de la sesión en el
            sistema de logging.
        """
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
                self.option_ai_configuration()
            elif choice == "8":
                self.option_help()
            elif choice == "0":
                self.option_exit()
            else:
                print(
                    f"\n{ConsoleColors.RED}✗ Opción no válida. Por favor, selecciona una opción del 0 al 8.{ConsoleColors.RESET}"
                )
                self.pause("Presiona Enter para volver al menú...")

        logger.info("=== Finalizando Simplex Solver - Menú Interactivo ===")


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
