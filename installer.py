#!/usr/bin/env python3
"""
Instalador interactivo del Simplex Solver.
Permite elegir componentes y configura el sistema según las capacidades detectadas.
"""
import os
import sys
import subprocess
import platform
import shutil
from pathlib import Path
from typing import List, Optional

# Importar el analizador de sistema
sys.path.insert(0, str(Path(__file__).parent / "src"))
from system_analyzer import SystemAnalyzer


class Color:
    """Códigos de color para la consola (compatible con Windows)."""

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
        except:
            pass


class SimplexInstaller:
    """Instalador interactivo del Simplex Solver."""

    def __init__(self):
        self.analyzer = SystemAnalyzer()
        self.install_ollama = False
        self.selected_models = []
        self.install_context_menu = False
        self.project_root = Path(__file__).parent.resolve()

    def clear_screen(self):
        """Limpia la pantalla de la consola."""
        os.system("cls" if os.name == "nt" else "clear")

    def print_header(self, title: str):
        """Imprime un encabezado formateado."""
        print("\n" + "=" * 70)
        print(f"{Color.CYAN}{Color.BOLD}{title:^70}{Color.RESET}")
        print("=" * 70 + "\n")

    def print_section(self, title: str):
        """Imprime un título de sección."""
        print(f"\n{Color.BLUE}{Color.BOLD}▶ {title}{Color.RESET}")
        print("-" * 70)

    def print_info(self, message: str):
        """Imprime un mensaje informativo."""
        print(f"{Color.CYAN}ℹ {message}{Color.RESET}")

    def print_success(self, message: str):
        """Imprime un mensaje de éxito."""
        print(f"{Color.GREEN}✓ {message}{Color.RESET}")

    def print_warning(self, message: str):
        """Imprime una advertencia."""
        print(f"{Color.YELLOW}⚠ {message}{Color.RESET}")

    def print_error(self, message: str):
        """Imprime un error."""
        print(f"{Color.RED}✗ {message}{Color.RESET}")

    def ask_yes_no(self, question: str, default: bool = True) -> bool:
        """Pregunta sí/no al usuario."""
        options = "[S/n]" if default else "[s/N]"
        while True:
            response = (
                input(f"{Color.YELLOW}? {question} {options}: {Color.RESET}")
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
                self.print_warning("Por favor responde 's' o 'n'")

    def ask_choice(self, question: str, options: List[str]) -> int:
        """Pregunta al usuario que elija entre varias opciones."""
        print(f"\n{Color.YELLOW}? {question}{Color.RESET}")
        for i, option in enumerate(options, 1):
            print(f"  {i}. {option}")

        while True:
            try:
                response = input(
                    f"{Color.YELLOW}Elige una opción (1-{len(options)}): {Color.RESET}"
                )
                choice = int(response)
                if 1 <= choice <= len(options):
                    return choice - 1
                else:
                    self.print_warning(
                        f"Por favor elige un número entre 1 y {len(options)}"
                    )
            except ValueError:
                self.print_warning("Por favor ingresa un número válido")

    def show_welcome(self):
        """Muestra la pantalla de bienvenida."""
        self.clear_screen()
        self.print_header("INSTALADOR DE SIMPLEX SOLVER")

        print(
            f"{Color.WHITE}Bienvenido al instalador interactivo del Simplex Solver.{Color.RESET}"
        )
        print(f"{Color.WHITE}Este asistente te ayudará a:{Color.RESET}\n")
        print("  • Analizar las capacidades de tu sistema")
        print("  • Instalar Ollama (opcional)")
        print("  • Descargar modelos de IA recomendados")
        print("  • Configurar el menú contextual de Windows")
        print("  • Instalar todas las dependencias necesarias")

        print(f"\n{Color.CYAN}Presiona Enter para continuar...{Color.RESET}")
        input()

    def show_system_analysis(self):
        """Muestra el análisis del sistema."""
        self.clear_screen()
        self.print_header("ANÁLISIS DEL SISTEMA")

        # Mostrar información del sistema
        info = self.analyzer.get_system_info()
        for key, value in info.items():
            print(
                f"  {Color.WHITE}{key:20}{Color.RESET}: {Color.CYAN}{value}{Color.RESET}"
            )

        # Verificar compatibilidad con Ollama
        print()
        can_run, reason = self.analyzer.can_run_ollama()
        if can_run:
            self.print_success(f"Ollama compatible: {reason}")
        else:
            self.print_error(f"Ollama no compatible: {reason}")

        print(f"\n{Color.CYAN}Presiona Enter para continuar...{Color.RESET}")
        input()

    def ask_ollama_installation(self):
        """Pregunta si desea instalar Ollama."""
        self.clear_screen()
        self.print_header("INSTALACIÓN DE OLLAMA")

        print(
            f"{Color.WHITE}Ollama es un motor de IA local que permite ejecutar modelos de lenguaje.{Color.RESET}"
        )
        print(f"{Color.WHITE}Beneficios:{Color.RESET}")
        print("  • Procesamiento de lenguaje natural para problemas de Simplex")
        print("  • Funciona completamente offline (sin enviar datos a internet)")
        print("  • Múltiples modelos optimizados disponibles")
        print()

        can_run, reason = self.analyzer.can_run_ollama()

        if not can_run:
            self.print_warning(f"Tu sistema no cumple los requisitos: {reason}")
            self.print_info("Puedes continuar sin Ollama usando solo el solver básico.")
            self.install_ollama = False
        else:
            self.install_ollama = self.ask_yes_no(
                "¿Deseas instalar Ollama?", default=True
            )

    def select_ai_models(self):
        """Permite seleccionar los modelos de IA a instalar."""
        if not self.install_ollama:
            return

        self.clear_screen()
        self.print_header("SELECCIÓN DE MODELOS DE IA")

        recommendations = self.analyzer.get_model_recommendations()

        print(
            f"{Color.WHITE}Modelos disponibles (ordenados por tamaño):{Color.RESET}\n"
        )

        # Mostrar modelos con información detallada
        for i, rec in enumerate(recommendations, 1):
            status = (
                f"{Color.GREEN}✓ RECOMENDADO{Color.RESET}"
                if rec.recommended
                else f"{Color.YELLOW}⚠ REQUIERE MÁS RAM{Color.RESET}"
            )

            print(f"{Color.BOLD}{i}. {rec.name}{Color.RESET}")
            print(f"   Tamaño: {rec.size} | RAM requerida: {rec.ram_required_gb} GB")
            print(f"   {rec.description}")
            print(f"   Estado: {status} - {rec.reason}")
            print()

        # Opción de instalar todos los recomendados
        print(f"\n{Color.CYAN}Opciones de instalación:{Color.RESET}")
        print(f"  A. Instalar todos los modelos recomendados")
        print(f"  B. Seleccionar modelos manualmente")
        print(f"  C. No instalar ningún modelo ahora (puedes hacerlo después)")

        while True:
            choice = (
                input(f"\n{Color.YELLOW}Elige una opción (A/B/C): {Color.RESET}")
                .strip()
                .upper()
            )

            if choice == "A":
                self.selected_models = [
                    rec.name for rec in recommendations if rec.recommended
                ]
                if self.selected_models:
                    print(f"\n{Color.GREEN}Modelos seleccionados:{Color.RESET}")
                    for model in self.selected_models:
                        print(f"  • {model}")
                else:
                    self.print_warning("No hay modelos recomendados para tu sistema.")
                    self.print_info("Puedes instalar modelos manualmente después.")
                break

            elif choice == "B":
                self.selected_models = self._select_models_manually(recommendations)
                break

            elif choice == "C":
                self.selected_models = []
                self.print_info(
                    "No se instalarán modelos. Puedes hacerlo después con 'ollama pull <modelo>'"
                )
                break

            else:
                self.print_warning("Por favor elige A, B o C")

        print(f"\n{Color.CYAN}Presiona Enter para continuar...{Color.RESET}")
        input()

    def _select_models_manually(self, recommendations) -> List[str]:
        """Permite seleccionar modelos manualmente."""
        selected = []

        print(
            f"\n{Color.WHITE}Selecciona los modelos que deseas instalar:{Color.RESET}"
        )
        print(
            f"{Color.CYAN}(Ingresa los números separados por comas, ej: 1,3,5){Color.RESET}"
        )

        while True:
            try:
                response = input(
                    f"\n{Color.YELLOW}Números de modelos: {Color.RESET}"
                ).strip()

                if not response:
                    break

                indices = [int(x.strip()) - 1 for x in response.split(",")]

                for idx in indices:
                    if 0 <= idx < len(recommendations):
                        model_name = recommendations[idx].name
                        if model_name not in selected:
                            selected.append(model_name)
                    else:
                        self.print_warning(f"Índice {idx + 1} fuera de rango")

                if selected:
                    print(f"\n{Color.GREEN}Modelos seleccionados:{Color.RESET}")
                    for model in selected:
                        print(f"  • {model}")
                    break

            except ValueError:
                self.print_warning(
                    "Por favor ingresa números válidos separados por comas"
                )

        return selected

    def ask_context_menu(self):
        """Pregunta si desea instalar el menú contextual."""
        self.clear_screen()
        self.print_header("MENÚ CONTEXTUAL DE WINDOWS")

        print(
            f"{Color.WHITE}El menú contextual permite resolver problemas desde el explorador:{Color.RESET}\n"
        )
        print("  • Click derecho en archivos .txt con problemas de Simplex")
        print("  • Opción 'Resolver con Simplex Solver'")
        print("  • Opción 'Resolver con IA' (si Ollama está instalado)")
        print("  • Acceso rápido sin abrir la línea de comandos")
        print()

        self.install_context_menu = self.ask_yes_no(
            "¿Deseas instalar el menú contextual?", default=True
        )

    def show_installation_summary(self):
        """Muestra un resumen de lo que se va a instalar."""
        self.clear_screen()
        self.print_header("RESUMEN DE INSTALACIÓN")

        print(f"{Color.WHITE}Se instalarán los siguientes componentes:{Color.RESET}\n")

        # Componentes base
        self.print_section("Componentes Base")
        print("  ✓ Simplex Solver (siempre se instala)")
        print("  ✓ Dependencias de Python (numpy, psutil, etc.)")

        # Ollama
        self.print_section("Ollama")
        if self.install_ollama:
            self.print_success("Se instalará Ollama")
            if self.selected_models:
                print(f"\n  {Color.WHITE}Modelos de IA a descargar:{Color.RESET}")
                total_size = 0
                for model in self.selected_models:
                    # Buscar el tamaño del modelo
                    for rec in self.analyzer.get_model_recommendations():
                        if rec.name == model:
                            print(f"    • {model} ({rec.size})")
                            break
            else:
                self.print_info("No se descargarán modelos (puedes hacerlo después)")
        else:
            self.print_info("No se instalará Ollama")

        # Menú contextual
        self.print_section("Menú Contextual")
        if self.install_context_menu:
            self.print_success("Se instalará el menú contextual de Windows")
        else:
            self.print_info("No se instalará el menú contextual")

        print()
        if not self.ask_yes_no("¿Deseas continuar con la instalación?", default=True):
            self.print_info("Instalación cancelada por el usuario")
            sys.exit(0)

    def install_python_dependencies(self):
        """Instala las dependencias de Python."""
        self.print_section("Instalando Dependencias de Python")

        requirements_file = self.project_root / "requirements.txt"

        if not requirements_file.exists():
            self.print_error(f"No se encontró {requirements_file}")
            return False

        try:
            self.print_info("Instalando dependencias básicas...")
            cmd = [sys.executable, "-m", "pip", "install", "-r", str(requirements_file)]

            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode == 0:
                self.print_success("Dependencias instaladas correctamente")
                return True
            else:
                self.print_error("Error al instalar dependencias")
                print(result.stderr)
                return False

        except Exception as e:
            self.print_error(f"Error: {e}")
            return False

    def install_ollama_component(self):
        """Instala Ollama."""
        if not self.install_ollama:
            return True

        self.print_section("Instalando Ollama")

        # Verificar si ya está instalado
        try:
            result = subprocess.run(
                ["ollama", "--version"], capture_output=True, text=True, timeout=5
            )

            if result.returncode == 0:
                self.print_success(f"Ollama ya está instalado: {result.stdout.strip()}")
                return True
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass

        # Instrucciones para instalar Ollama
        self.print_info("Ollama no está instalado en el sistema")
        print(f"\n{Color.WHITE}Para instalar Ollama:{Color.RESET}")
        print(f"  1. Visita: {Color.CYAN}https://ollama.ai/download{Color.RESET}")
        print(f"  2. Descarga el instalador para Windows")
        print(f"  3. Ejecuta el instalador")
        print(f"  4. Reinicia el terminal")

        if self.ask_yes_no("¿Deseas abrir el sitio de descarga ahora?", default=True):
            try:
                if platform.system() == "Windows":
                    os.startfile("https://ollama.ai/download")
                else:
                    subprocess.run(["xdg-open", "https://ollama.ai/download"])
            except:
                self.print_warning("No se pudo abrir el navegador automáticamente")

        self.print_warning(
            "Completa la instalación de Ollama y vuelve a ejecutar este instalador"
        )
        return False

    def download_ai_models(self):
        """Descarga los modelos de IA seleccionados."""
        if not self.selected_models:
            return True

        self.print_section("Descargando Modelos de IA")

        # Verificar que Ollama esté disponible
        try:
            subprocess.run(
                ["ollama", "--version"], capture_output=True, timeout=5, check=True
            )
        except (
            FileNotFoundError,
            subprocess.TimeoutExpired,
            subprocess.CalledProcessError,
        ):
            self.print_error("Ollama no está disponible. Instálalo primero.")
            return False

        success = True
        for model in self.selected_models:
            self.print_info(f"Descargando {model}...")

            try:
                # Mostrar progreso en tiempo real
                process = subprocess.Popen(
                    ["ollama", "pull", model],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1,
                )

                for line in process.stdout:
                    print(f"  {line.rstrip()}")

                process.wait()

                if process.returncode == 0:
                    self.print_success(f"Modelo {model} descargado correctamente")
                else:
                    self.print_error(f"Error al descargar {model}")
                    success = False

            except Exception as e:
                self.print_error(f"Error al descargar {model}: {e}")
                success = False

        return success

    def install_context_menu_component(self):
        """Instala el menú contextual de Windows."""
        if not self.install_context_menu:
            return True

        self.print_section("Instalando Menú Contextual")

        install_bat = self.project_root / "context_menu" / "install.bat"

        if not install_bat.exists():
            self.print_error(f"No se encontró {install_bat}")
            return False

        try:
            self.print_info("Ejecutando instalador del menú contextual...")
            self.print_warning("Esto requiere permisos de administrador")

            # Ejecutar el batch con permisos de administrador
            if platform.system() == "Windows":
                subprocess.run(
                    ["cmd", "/c", str(install_bat)],
                    cwd=str(install_bat.parent),
                    check=True,
                )

                self.print_success("Menú contextual instalado correctamente")
                return True
            else:
                self.print_error("El menú contextual solo está disponible en Windows")
                return False

        except subprocess.CalledProcessError as e:
            self.print_error(f"Error al instalar el menú contextual: {e}")
            return False
        except Exception as e:
            self.print_error(f"Error inesperado: {e}")
            return False

    def show_completion(self):
        """Muestra el mensaje de finalización."""
        self.clear_screen()
        self.print_header("INSTALACIÓN COMPLETADA")

        self.print_success("El Simplex Solver ha sido instalado correctamente")

        print(f"\n{Color.WHITE}Próximos pasos:{Color.RESET}\n")

        print(f"1. Para usar el solver interactivo:")
        print(f"   {Color.CYAN}python simplex.py --interactive{Color.RESET}")

        print(f"\n2. Para resolver un archivo:")
        print(
            f"   {Color.CYAN}python simplex.py ejemplos/ejemplo_maximizacion.txt{Color.RESET}"
        )

        if self.install_ollama and self.selected_models:
            print(f"\n3. Para usar el modo IA:")
            print(
                f'   {Color.CYAN}python simplex.py --ai "tu problema en lenguaje natural"{Color.RESET}'
            )

        if self.install_context_menu:
            print(f"\n4. Desde el explorador de Windows:")
            print(
                f"   {Color.CYAN}Click derecho en un archivo .txt > Resolver con Simplex{Color.RESET}"
            )

        print(f"\n{Color.WHITE}Documentación:{Color.RESET}")
        print(f"  • README.md - Guía general")
        print(f"  • docs/GUIA_IA.md - Guía del sistema de IA")
        print(f"  • ejemplos/ - Problemas de ejemplo")

        print(f"\n{Color.GREEN}¡Gracias por usar Simplex Solver!{Color.RESET}\n")

    def run(self):
        """Ejecuta el instalador."""
        enable_ansi_colors()

        try:
            # Paso 1: Bienvenida
            self.show_welcome()

            # Paso 2: Análisis del sistema
            self.show_system_analysis()

            # Paso 3: Preguntar por Ollama
            self.ask_ollama_installation()

            # Paso 4: Seleccionar modelos (si se instala Ollama)
            self.select_ai_models()

            # Paso 5: Preguntar por menú contextual
            self.ask_context_menu()

            # Paso 6: Mostrar resumen
            self.show_installation_summary()

            # Paso 7: Instalación
            self.clear_screen()
            self.print_header("PROCESO DE INSTALACIÓN")

            # Instalar dependencias de Python
            if not self.install_python_dependencies():
                self.print_error("Fallo en la instalación de dependencias")
                return False

            # Instalar Ollama
            if self.install_ollama:
                if not self.install_ollama_component():
                    self.print_warning("Continúa la instalación sin Ollama")
                else:
                    # Descargar modelos
                    self.download_ai_models()

            # Instalar menú contextual
            if self.install_context_menu:
                self.install_context_menu_component()

            # Paso 8: Finalización
            self.show_completion()

            return True

        except KeyboardInterrupt:
            print(
                f"\n\n{Color.YELLOW}Instalación cancelada por el usuario{Color.RESET}"
            )
            return False
        except Exception as e:
            self.print_error(f"Error inesperado: {e}")
            import traceback

            traceback.print_exc()
            return False


def main():
    """Función principal."""
    installer = SimplexInstaller()
    success = installer.run()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
