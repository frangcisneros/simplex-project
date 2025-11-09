"""
Módulo de interfaz de usuario para consola.
Proporciona utilidades para crear interfaces de texto con colores y formato.
"""

import os
import platform
from typing import List, Optional


class ConsoleColors:
    """
    Códigos de escape ANSI para dar color y formato al texto en la consola.

    Proporciona constantes para diferentes colores y estilos de texto
    que funcionan en terminales compatibles con ANSI (Linux, macOS, Windows 10+).
    """

    RESET = "\033[0m"  # Resetea todos los estilos y colores
    BOLD = "\033[1m"  # Texto en negrita
    RED = "\033[91m"  # Texto rojo (para errores)
    GREEN = "\033[92m"  # Texto verde (para éxito)
    YELLOW = "\033[93m"  # Texto amarillo (para advertencias)
    BLUE = "\033[94m"  # Texto azul (para títulos)
    CYAN = "\033[96m"  # Texto cyan (para información)
    WHITE = "\033[97m"  # Texto blanco (para texto normal)


def enable_ansi_colors():
    """
    Habilita el soporte para códigos de escape ANSI en la consola de Windows.

    En Windows 10 y versiones posteriores, activa el modo de terminal virtual
    que permite procesar correctamente los códigos de color ANSI. En otros
    sistemas operativos esta función no hace nada ya que ANSI está habilitado
    por defecto.

    Note:
        Esta función utiliza ctypes para llamar a la API de Windows.
        Si falla, simplemente no se mostrarán colores pero el programa
        continuará funcionando normalmente.
    """
    if platform.system() == "Windows":
        try:
            import ctypes

            # Obtener handle de la consola de salida estándar
            kernel32 = ctypes.windll.kernel32
            # Activar modo de terminal virtual (flag 7 = ENABLE_VIRTUAL_TERMINAL_PROCESSING)
            kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
        except Exception:
            # Si falla, continuar sin colores
            pass


class ConsoleUI:
    """
    Clase para gestionar interfaces de usuario en consola con formato y colores.

    Proporciona métodos para:
    - Limpiar pantalla
    - Imprimir encabezados y secciones
    - Mensajes con formato (info, éxito, advertencia, error)
    - Interacción con el usuario (preguntas sí/no, opciones múltiples)
    - Pausas y esperas

    Esta clase sigue el patrón de diseño Singleton implícito donde todos
    los métodos son estáticos, permitiendo su uso sin instanciación.
    """

    @staticmethod
    def clear_screen():
        """
        Limpia la pantalla de la consola.

        Utiliza el comando apropiado según el sistema operativo:
        - Windows: cls
        - Unix/Linux/macOS: clear
        """
        os.system("cls" if os.name == "nt" else "clear")

    @staticmethod
    def print_header(title: str, width: int = 70):
        """
        Imprime un encabezado formateado con el título centrado.

        Args:
            title: Texto del encabezado
            width: Ancho total del encabezado (por defecto 70 caracteres)
        """
        print("\n" + "=" * width)
        print(f"{ConsoleColors.CYAN}{ConsoleColors.BOLD}{title:^{width}}{ConsoleColors.RESET}")
        print("=" * width + "\n")

    @staticmethod
    def print_section(title: str, width: int = 70):
        """
        Imprime un título de sección destacado.

        Args:
            title: Texto de la sección
            width: Ancho de la línea separadora (por defecto 70 caracteres)
        """
        print(f"\n{ConsoleColors.BLUE}{ConsoleColors.BOLD}▶ {title}{ConsoleColors.RESET}")
        print("-" * width)

    @staticmethod
    def print_info(message: str, prefix: str = "ℹ"):
        """
        Muestra un mensaje informativo en la consola.

        Args:
            message: Mensaje a mostrar
            prefix: Prefijo/icono para el mensaje (por defecto "ℹ")
        """
        print(f"{ConsoleColors.CYAN}{prefix} {message}{ConsoleColors.RESET}")

    @staticmethod
    def print_success(message: str, prefix: str = "✓"):
        """
        Muestra un mensaje indicando éxito en la operación.

        Args:
            message: Mensaje a mostrar
            prefix: Prefijo/icono para el mensaje (por defecto "✓")
        """
        print(f"{ConsoleColors.GREEN}{prefix} {message}{ConsoleColors.RESET}")

    @staticmethod
    def print_warning(message: str, prefix: str = "⚠"):
        """
        Muestra una advertencia en la consola.

        Args:
            message: Mensaje a mostrar
            prefix: Prefijo/icono para el mensaje (por defecto "⚠")
        """
        print(f"{ConsoleColors.YELLOW}{prefix} {message}{ConsoleColors.RESET}")

    @staticmethod
    def print_error(message: str, prefix: str = "✗"):
        """
        Muestra un mensaje de error en la consola.

        Args:
            message: Mensaje a mostrar
            prefix: Prefijo/icono para el mensaje (por defecto "✗")
        """
        print(f"{ConsoleColors.RED}{prefix} {message}{ConsoleColors.RESET}")

    @staticmethod
    def pause(message: str = "Presiona Enter para continuar..."):
        """
        Pausa la ejecución hasta que el usuario presione Enter.

        Args:
            message: Mensaje a mostrar al usuario mientras espera

        Note:
            Si el usuario presiona Ctrl+C o Ctrl+D, la función continúa
            sin error para permitir salir de forma elegante.
        """
        try:
            input(f"\n{ConsoleColors.CYAN}{message}{ConsoleColors.RESET}")
        except (KeyboardInterrupt, EOFError):
            pass

    @staticmethod
    def ask_yes_no(question: str, default: bool = True) -> bool:
        """
        Realiza una pregunta de tipo sí/no al usuario y retorna la respuesta.

        Args:
            question: Pregunta a realizar
            default: Valor por defecto si el usuario presiona Enter sin responder

        Returns:
            bool: True si la respuesta es afirmativa, False si es negativa

        Example:
            >>> if ConsoleUI.ask_yes_no("¿Deseas continuar?"):
            ...     print("Continuando...")
        """
        options = "[S/n]" if default else "[s/N]"

        while True:
            response = (
                input(f"{ConsoleColors.YELLOW}? {question} {options}: {ConsoleColors.RESET}")
                .strip()
                .lower()
            )

            if response == "":
                return default
            elif response in ["s", "si", "sí", "y", "yes"]:
                return True
            elif response in ["n", "no"]:
                return False
            else:
                ConsoleUI.print_warning("Por favor responde 's' o 'n'")

    @staticmethod
    def ask_choice(question: str, options: List[str]) -> int:
        """
        Presenta una lista de opciones al usuario y retorna la selección realizada.

        Args:
            question: Pregunta a realizar
            options: Lista de opciones disponibles

        Returns:
            int: Índice de la opción seleccionada (0-indexed)

        Example:
            >>> options = ["Opción A", "Opción B", "Opción C"]
            >>> choice = ConsoleUI.ask_choice("Selecciona una opción", options)
            >>> print(f"Elegiste: {options[choice]}")
        """
        print(f"\n{ConsoleColors.YELLOW}? {question}{ConsoleColors.RESET}")
        for i, option in enumerate(options, 1):
            print(f"  {i}. {option}")

        while True:
            try:
                response = input(
                    f"{ConsoleColors.YELLOW}Elige una opción (1-{len(options)}): {ConsoleColors.RESET}"
                )
                choice = int(response)

                if 1 <= choice <= len(options):
                    return choice - 1  # Retornar índice 0-based
                else:
                    ConsoleUI.print_warning(f"Por favor elige un número entre 1 y {len(options)}")
            except ValueError:
                ConsoleUI.print_warning("Por favor ingresa un número válido")

    @staticmethod
    def get_input(prompt: str, default: Optional[str] = None) -> str:
        """
        Solicita una entrada de texto al usuario.

        Args:
            prompt: Mensaje a mostrar al usuario
            default: Valor por defecto si el usuario presiona Enter sin escribir

        Returns:
            str: Texto ingresado por el usuario (o valor por defecto)
        """
        if default:
            prompt_text = f"{ConsoleColors.YELLOW}{prompt} [{default}]: {ConsoleColors.RESET}"
        else:
            prompt_text = f"{ConsoleColors.YELLOW}{prompt}: {ConsoleColors.RESET}"

        response = input(prompt_text).strip()
        return response if response else (default or "")

    @staticmethod
    def print_progress_bar(
        current: int, total: int, prefix: str = "", suffix: str = "", bar_length: int = 40
    ):
        """
        Imprime una barra de progreso en la consola.

        Args:
            current: Valor actual de progreso
            total: Valor total/máximo
            prefix: Texto a mostrar antes de la barra
            suffix: Texto a mostrar después de la barra
            bar_length: Longitud de la barra en caracteres

        Example:
            >>> for i in range(100):
            ...     ConsoleUI.print_progress_bar(i, 100, prefix="Progreso:")
        """
        percentage = int((current / total) * 100)
        filled_length = int(bar_length * current // total)
        bar = "█" * filled_length + "░" * (bar_length - filled_length)

        print(f"\r{prefix} [{bar}] {percentage}% {suffix}", end="", flush=True)

        if current == total:
            print()  # Nueva línea al completar

    @staticmethod
    def print_box(title: str, content: List[str], width: int = 70, style: str = "single"):
        """
        Imprime contenido dentro de una caja con bordes.

        Args:
            title: Título de la caja
            content: Lista de líneas de contenido
            width: Ancho de la caja
            style: Estilo de borde ("single", "double", "bold")
        """
        if style == "double":
            top = "╔" + "═" * (width - 2) + "╗"
            mid = "║"
            bot = "╚" + "═" * (width - 2) + "╝"
        elif style == "bold":
            top = "┏" + "━" * (width - 2) + "┓"
            mid = "┃"
            bot = "┗" + "━" * (width - 2) + "┛"
        else:  # single
            top = "┌" + "─" * (width - 2) + "┐"
            mid = "│"
            bot = "└" + "─" * (width - 2) + "┘"

        print(f"\n{ConsoleColors.CYAN}{top}{ConsoleColors.RESET}")

        if title:
            title_line = f"{mid} {title:<{width-4}} {mid}"
            print(f"{ConsoleColors.CYAN}{title_line}{ConsoleColors.RESET}")
            separator = mid + "─" * (width - 2) + mid
            print(f"{ConsoleColors.CYAN}{separator}{ConsoleColors.RESET}")

        for line in content:
            padded_line = f"{mid} {line:<{width-4}} {mid}"
            print(f"{ConsoleColors.CYAN}{padded_line}{ConsoleColors.RESET}")

        print(f"{ConsoleColors.CYAN}{bot}{ConsoleColors.RESET}\n")


# Exportar los nombres principales
__all__ = ["ConsoleUI", "ConsoleColors", "enable_ansi_colors"]
