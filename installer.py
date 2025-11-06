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

# Importar el analizador de sistema desde tools
sys.path.insert(0, str(Path(__file__).parent / "tools"))
from system_analyzer import SystemAnalyzer  # type: ignore

# Importar UI reutilizable
sys.path.insert(0, str(Path(__file__).parent))
from simplex_solver.ui import ConsoleUI, ConsoleColors, enable_ansi_colors


def is_admin():
    """
    Verifica si el script se está ejecutando con permisos de administrador.
    En sistemas Unix/Linux, verifica si el usuario es root.
    """
    if platform.system() == "Windows":
        try:
            import ctypes

            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        except:
            return False
    else:
        # En Unix/Linux, verificar si es root
        try:
            return os.geteuid() == 0  # type: ignore
        except AttributeError:
            # os.geteuid no está disponible en este sistema
            return False


class SimplexInstaller:
    """
    Clase principal para gestionar la instalación interactiva del Simplex Solver.
    Proporciona opciones para analizar el sistema, instalar componentes y configurar el entorno.
    """

    def __init__(self):
        """
        Inicializa el instalador, detectando permisos y configurando rutas necesarias.
        """
        self.ui = ConsoleUI()
        self.analyzer = SystemAnalyzer()
        self.install_ollama = False
        self.selected_models = []
        self.install_context_menu = False
        self.is_admin = is_admin()  # Detectar si tiene permisos de administrador
        self.installation_log = []  # Log de operaciones realizadas
        # Detectar si estamos corriendo como .exe empaquetado
        if getattr(sys, "frozen", False):
            # Corriendo como .exe - PyInstaller extrae archivos a sys._MEIPASS
            self.project_root = Path(getattr(sys, "_MEIPASS", "."))
        else:
            # Corriendo como script normal
            self.project_root = Path(__file__).parent.resolve()

    def _find_python_executable(self) -> Optional[str]:
        """
        Busca el ejecutable de Python en el sistema utilizando varios métodos.
        Retorna la ruta del ejecutable si se encuentra, o None en caso contrario.
        """
        # Si estamos corriendo como .exe, sys.executable apunta al .exe
        # Necesitamos buscar el Python del sistema

        # Intentar varios métodos para encontrar Python
        possible_pythons = []

        # 1. Buscar en PATH
        try:
            result = subprocess.run(
                ["where", "python"] if os.name == "nt" else ["which", "python"],
                capture_output=True,
                text=True,
                check=True,
            )
            if result.returncode == 0:
                pythons = result.stdout.strip().split("\n")
                possible_pythons.extend([p.strip() for p in pythons if p.strip()])
        except:
            pass

        # 2. Verificar rutas comunes en Windows
        if os.name == "nt":
            common_paths = [
                Path(os.environ.get("LOCALAPPDATA", "")) / "Programs" / "Python",
                Path("C:/Python314"),
                Path("C:/Python313"),
                Path("C:/Python312"),
                Path("C:/Python311"),
                Path("C:/Python310"),
                Path("C:/Python39"),
            ]

            for base_path in common_paths:
                if base_path.exists():
                    python_exe = base_path / "python.exe"
                    if python_exe.exists():
                        possible_pythons.append(str(python_exe))

        # 3. Si sys.executable no es un .exe del instalador, usarlo
        if not sys.executable.endswith("SimplexInstaller.exe"):
            possible_pythons.insert(0, sys.executable)

        # Verificar que el Python encontrado funcione
        for python_path in possible_pythons:
            try:
                result = subprocess.run(
                    [python_path, "--version"], capture_output=True, text=True, timeout=5
                )
                if result.returncode == 0:
                    return python_path
            except:
                continue

        return None

    def log_operation(self, operation: str, success: bool, details: str = ""):
        """
        Registra una operación en el log de instalación con su estado y detalles.
        """
        status = "✓" if success else "✗"
        self.installation_log.append(
            {"operation": operation, "success": success, "details": details, "status": status}
        )

    def show_welcome(self):
        """
        Muestra la pantalla de bienvenida con información general sobre el instalador.
        """
        self.ui.clear_screen()
        self.ui.print_header("INSTALADOR DE SIMPLEX SOLVER")

        if self.is_admin:
            print(
                f"{ConsoleColors.GREEN}✓ Ejecutando con permisos de administrador{ConsoleColors.RESET}"
            )
            print(
                f"{ConsoleColors.GREEN}  El menú contextual se instalará automáticamente{ConsoleColors.RESET}"
            )
        else:
            print(
                f"{ConsoleColors.YELLOW}⚠ Ejecutando sin permisos de administrador{ConsoleColors.RESET}"
            )
            print(
                f"{ConsoleColors.YELLOW}  El menú contextual no se podrá instalar{ConsoleColors.RESET}"
            )
        print()
        print(
            f"{ConsoleColors.WHITE}Bienvenido al instalador interactivo del Simplex Solver.{ConsoleColors.RESET}"
        )
        print(f"{ConsoleColors.WHITE}Este asistente te ayudará a:{ConsoleColors.RESET}\n")
        print("  • Analizar las capacidades de tu sistema")
        print("  • Instalar Ollama (opcional)")
        print("  • Descargar modelos de IA recomendados")
        print(
            "  • Configurar el menú contextual de Windows"
            + (
                f" {ConsoleColors.GREEN}(automático){ConsoleColors.RESET}"
                if self.is_admin
                else f" {ConsoleColors.YELLOW}(requiere admin){ConsoleColors.RESET}"
            )
        )
        print("  • Instalar todas las dependencias necesarias")

        print(f"\n{ConsoleColors.CYAN}Presiona Enter para continuar...{ConsoleColors.RESET}")
        input()

    def show_system_analysis(self):
        """
        Realiza y muestra un análisis del sistema, incluyendo compatibilidad con Ollama.
        """
        self.ui.clear_screen()
        self.ui.print_header("ANÁLISIS DEL SISTEMA")

        # Mostrar información del sistema
        info = self.analyzer.get_system_info()
        for key, value in info.items():
            print(
                f"  {ConsoleColors.WHITE}{key:20}{ConsoleColors.RESET}: {ConsoleColors.CYAN}{value}{ConsoleColors.RESET}"
            )

        # Verificar compatibilidad con Ollama
        print()
        can_run, reason = self.analyzer.can_run_ollama()
        if can_run:
            self.ui.print_success(f"Ollama compatible: {reason}")
        else:
            self.ui.print_error(f"Ollama no compatible: {reason}")

        print(f"\n{ConsoleColors.CYAN}Presiona Enter para continuar...{ConsoleColors.RESET}")
        input()

    def ask_ollama_installation(self):
        """
        Pregunta al usuario si desea instalar Ollama, mostrando sus beneficios.
        """
        self.ui.clear_screen()
        self.ui.print_header("INSTALACIÓN DE OLLAMA")

        print(
            f"{ConsoleColors.WHITE}Ollama es un motor de IA local que permite ejecutar modelos de lenguaje.{ConsoleColors.RESET}"
        )
        print(f"{ConsoleColors.WHITE}Beneficios:{ConsoleColors.RESET}")
        print("  • Procesamiento de lenguaje natural para problemas de Simplex")
        print("  • Funciona completamente offline (sin enviar datos a internet)")
        print("  • Múltiples modelos optimizados disponibles")
        print()

        can_run, reason = self.analyzer.can_run_ollama()

        if not can_run:
            self.ui.print_warning(f"Tu sistema no cumple los requisitos: {reason}")
            self.ui.print_info("Puedes continuar sin Ollama usando solo el solver básico.")
            self.install_ollama = False
        else:
            self.install_ollama = self.ui.ask_yes_no("¿Deseas instalar Ollama?", default=True)

    def select_ai_models(self):
        """
        Permite al usuario seleccionar los modelos de IA a instalar, si aplica.
        """
        if not self.install_ollama:
            return

        self.ui.clear_screen()
        self.ui.print_header("SELECCIÓN DE MODELOS DE IA")

        recommendations = self.analyzer.get_model_recommendations()

        print(
            f"{ConsoleColors.WHITE}Modelos disponibles (ordenados por tamaño):{ConsoleColors.RESET}\n"
        )

        # Mostrar modelos con información detallada
        for i, rec in enumerate(recommendations, 1):
            status = (
                f"{ConsoleColors.GREEN}✓ RECOMENDADO{ConsoleColors.RESET}"
                if rec.recommended
                else f"{ConsoleColors.YELLOW}⚠ REQUIERE MÁS RAM{ConsoleColors.RESET}"
            )

            print(f"{ConsoleColors.BOLD}{i}. {rec.name}{ConsoleColors.RESET}")
            print(f"   Tamaño: {rec.size} | RAM requerida: {rec.ram_required_gb} GB")
            print(f"   {rec.description}")
            print(f"   Estado: {status} - {rec.reason}")
            print()

        # Opción de instalar todos los recomendados
        print(f"\n{ConsoleColors.CYAN}Opciones de instalación:{ConsoleColors.RESET}")
        print(f"  A. Instalar todos los modelos recomendados")
        print(f"  B. Seleccionar modelos manualmente")
        print(f"  C. No instalar ningún modelo ahora (puedes hacerlo después)")

        while True:
            choice = (
                input(f"\n{ConsoleColors.YELLOW}Elige una opción (A/B/C): {ConsoleColors.RESET}")
                .strip()
                .upper()
            )

            if choice == "A":
                self.selected_models = [rec.name for rec in recommendations if rec.recommended]
                if self.selected_models:
                    print(f"\n{ConsoleColors.GREEN}Modelos seleccionados:{ConsoleColors.RESET}")
                    for model in self.selected_models:
                        print(f"  • {model}")
                else:
                    self.ui.print_warning("No hay modelos recomendados para tu sistema.")
                    self.ui.print_info("Puedes instalar modelos manualmente después.")
                break

            elif choice == "B":
                self.selected_models = self._select_models_manually(recommendations)
                break

            elif choice == "C":
                self.selected_models = []
                self.ui.print_info(
                    "No se instalarán modelos. Puedes hacerlo después con 'ollama pull <modelo>'"
                )
                break

            else:
                self.ui.print_warning("Por favor elige A, B o C")

        print(f"\n{ConsoleColors.CYAN}Presiona Enter para continuar...{ConsoleColors.RESET}")
        input()

    def _select_models_manually(self, recommendations) -> List[str]:
        """
        Permite al usuario seleccionar manualmente los modelos de IA de una lista.
        """
        selected = []

        print(
            f"\n{ConsoleColors.WHITE}Selecciona los modelos que deseas instalar:{ConsoleColors.RESET}"
        )
        print(
            f"{ConsoleColors.CYAN}(Ingresa los números separados por comas, ej: 1,3,5){ConsoleColors.RESET}"
        )

        while True:
            try:
                response = input(
                    f"\n{ConsoleColors.YELLOW}Números de modelos: {ConsoleColors.RESET}"
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
                        self.ui.print_warning(f"Índice {idx + 1} fuera de rango")

                if selected:
                    print(f"\n{ConsoleColors.GREEN}Modelos seleccionados:{ConsoleColors.RESET}")
                    for model in selected:
                        print(f"  • {model}")
                    break

            except ValueError:
                self.ui.print_warning("Por favor ingresa números válidos separados por comas")

        return selected

    def ask_context_menu(self):
        """
        Pregunta al usuario si desea instalar el menú contextual de Windows.
        Si se ejecuta como administrador, lo instala automáticamente.
        """
        self.ui.clear_screen()
        self.ui.print_header("MENÚ CONTEXTUAL DE WINDOWS")

        print(
            f"{ConsoleColors.WHITE}El menú contextual permite resolver problemas desde el explorador:{ConsoleColors.RESET}\n"
        )
        print("  • Click derecho en archivos .txt con problemas de Simplex")
        print("  • Opción 'Resolver con Simplex Solver'")
        print("  • Opción 'Resolver con IA' (si Ollama está instalado)")
        print("  • Acceso rápido sin abrir la línea de comandos")
        print()

        # Si estamos ejecutando como administrador, instalar automáticamente
        if self.is_admin and platform.system() == "Windows":
            self.ui.print_success(
                "✓ Ejecutando como administrador - El menú contextual se instalará automáticamente"
            )
            self.install_context_menu = True
            print(f"\n{ConsoleColors.CYAN}Presiona Enter para continuar...{ConsoleColors.RESET}")
            input()
        else:
            # Si no es admin, preguntar (aunque probablemente no se pueda instalar)
            if platform.system() == "Windows" and not self.is_admin:
                self.ui.print_warning("⚠ No se detectaron permisos de administrador")
                self.ui.print_info(
                    "  El menú contextual requiere permisos de administrador para instalarse"
                )
                print()

            self.install_context_menu = self.ui.ask_yes_no(
                "¿Deseas instalar el menú contextual?", default=self.is_admin
            )

    def show_installation_summary(self):
        """
        Muestra un resumen de los componentes que se instalarán.
        """
        self.ui.clear_screen()
        self.ui.print_header("RESUMEN DE INSTALACIÓN")

        print(
            f"{ConsoleColors.WHITE}Se instalarán los siguientes componentes:{ConsoleColors.RESET}\n"
        )

        # Componentes base
        self.ui.print_section("Componentes Base")
        print("  ✓ Simplex Solver (siempre se instala)")
        print("  ✓ Dependencias de Python (numpy, psutil, etc.)")

        # Ollama
        self.ui.print_section("Ollama")
        if self.install_ollama:
            self.ui.print_success("Se instalará Ollama")
            if self.selected_models:
                print(f"\n  {ConsoleColors.WHITE}Modelos de IA a descargar:{ConsoleColors.RESET}")
                total_size = 0
                for model in self.selected_models:
                    # Buscar el tamaño del modelo
                    for rec in self.analyzer.get_model_recommendations():
                        if rec.name == model:
                            print(f"    • {model} ({rec.size})")
                            break
            else:
                self.ui.print_info("No se descargarán modelos (puedes hacerlo después)")
        else:
            self.ui.print_info("No se instalará Ollama")

        # Menú contextual
        self.ui.print_section("Menú Contextual")
        if self.install_context_menu:
            self.ui.print_success("Se instalará el menú contextual de Windows")
        else:
            self.ui.print_info("No se instalará el menú contextual")

        print()
        if not self.ui.ask_yes_no("¿Deseas continuar con la instalación?", default=True):
            self.ui.print_info("Instalación cancelada por el usuario")
            sys.exit(0)

    def install_python_dependencies(self):
        """
        Instala las dependencias de Python necesarias para el Simplex Solver.
        Verifica la existencia de un ejecutable de Python y el archivo de requisitos.
        """
        self.ui.print_section("Instalando Dependencias de Python")

        # Detectar el ejecutable de Python del sistema
        python_exe = self._find_python_executable()
        if not python_exe:
            self.ui.print_error("No se pudo encontrar Python en el sistema")
            self.ui.print_info("Por favor, instala Python desde https://www.python.org/")
            return False

        self.ui.print_info(f"Usando Python: {python_exe}")

        requirements_file = self.project_root / "requirements.txt"

        if not requirements_file.exists():
            self.ui.print_error(f"No se encontró {requirements_file}")
            return False

        try:
            # Leer las dependencias del archivo
            with open(requirements_file, "r") as f:
                packages = [line.strip() for line in f if line.strip() and not line.startswith("#")]

            total_packages = len(packages)
            self.ui.print_info(f"Se instalarán {total_packages} paquetes...")
            print()

            # Instalar cada paquete y mostrar progreso
            installed = 0
            for i, package in enumerate(packages, 1):
                # Barra de progreso
                progress = int((i / total_packages) * 40)
                bar = "█" * progress + "░" * (40 - progress)
                percentage = int((i / total_packages) * 100)

                print(
                    f"\r  [{bar}] {percentage}% - Instalando: {package[:40]:<40}",
                    end="",
                    flush=True,
                )

                # Instalar el paquete
                cmd = [python_exe, "-m", "pip", "install", package, "-q"]
                result = subprocess.run(cmd, capture_output=True, text=True)

                if result.returncode == 0:
                    installed += 1
                else:
                    print()  # Nueva línea
                    self.ui.print_warning(f"No se pudo instalar {package}")

            print()  # Nueva línea después de la barra
            print()

            if installed == total_packages:
                self.ui.print_success(
                    f"✓ {installed}/{total_packages} dependencias instaladas correctamente"
                )
                self.log_operation(
                    "Dependencias Python", True, f"{installed}/{total_packages} paquetes"
                )
                return True
            elif installed > 0:
                self.ui.print_warning(
                    f"⚠ {installed}/{total_packages} dependencias instaladas (algunas fallaron)"
                )
                self.log_operation(
                    "Dependencias Python",
                    True,
                    f"{installed}/{total_packages} paquetes (algunas fallaron)",
                )
                return True
            else:
                self.ui.print_error("✗ No se pudieron instalar las dependencias")
                self.log_operation("Dependencias Python", False, "Error al instalar paquetes")
                return False

        except Exception as e:
            print()  # Nueva línea
            self.ui.print_error(f"Error: {e}")
            self.log_operation("Dependencias Python", False, str(e))
            return False

    def install_ollama_component(self):
        """
        Gestiona la instalación de Ollama, verificando su disponibilidad en el sistema.
        """
        if not self.install_ollama:
            return True

        self.ui.print_section("Instalando Ollama")

        # Verificar si ya está instalado
        try:
            result = subprocess.run(
                ["ollama", "--version"], capture_output=True, text=True, timeout=5
            )

            if result.returncode == 0:
                self.ui.print_success(f"Ollama ya está instalado: {result.stdout.strip()}")
                self.log_operation("Ollama", True, "Ya instalado")
                return True
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass

        # Instrucciones para instalar Ollama
        self.ui.print_info("Ollama no está instalado en el sistema")
        print(f"\n{ConsoleColors.WHITE}Para instalar Ollama:{ConsoleColors.RESET}")
        print(f"  1. Visita: {ConsoleColors.CYAN}https://ollama.ai/download{ConsoleColors.RESET}")
        print(f"  2. Descarga el instalador para Windows")
        print(f"  3. Ejecuta el instalador")
        print(f"  4. Reinicia el terminal")

        if self.ui.ask_yes_no("¿Deseas abrir el sitio de descarga ahora?", default=True):
            try:
                if platform.system() == "Windows":
                    os.startfile("https://ollama.ai/download")
                else:
                    subprocess.run(["xdg-open", "https://ollama.ai/download"])
            except:
                self.ui.print_warning("No se pudo abrir el navegador automáticamente")

        self.ui.print_warning(
            "Completa la instalación de Ollama y vuelve a ejecutar este instalador"
        )
        self.log_operation("Ollama", False, "No instalado - requiere instalación manual")
        return False

    def download_ai_models(self):
        """
        Descarga los modelos de IA seleccionados por el usuario.
        Verifica que Ollama esté disponible antes de proceder.
        """
        if not self.selected_models:
            return True

        self.ui.print_section("Descargando Modelos de IA")

        # Verificar que Ollama esté disponible
        try:
            subprocess.run(["ollama", "--version"], capture_output=True, timeout=5, check=True)
        except (
            FileNotFoundError,
            subprocess.TimeoutExpired,
            subprocess.CalledProcessError,
        ):
            self.ui.print_error("Ollama no está disponible. Instálalo primero.")
            return False

        success = True
        total_models = len(self.selected_models)

        for idx, model in enumerate(self.selected_models, 1):
            print(
                f"\n{ConsoleColors.CYAN}[{idx}/{total_models}] Descargando {model}...{ConsoleColors.RESET}"
            )
            print("-" * 70)

            try:
                # Mostrar progreso en tiempo real
                process = subprocess.Popen(
                    ["ollama", "pull", model],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    encoding="utf-8",
                    errors="replace",  # Reemplaza caracteres inválidos en lugar de fallar
                    bufsize=1,
                )

                if process.stdout:
                    for line in process.stdout:
                        # Limpiar y mostrar la línea con indentación
                        clean_line = line.rstrip()
                        if clean_line:
                            print(f"  {clean_line}")

                process.wait()

                if process.returncode == 0:
                    self.ui.print_success(f"✓ Modelo {model} descargado correctamente")
                    self.log_operation(f"Modelo IA: {model}", True, "Descargado")
                else:
                    self.ui.print_error(f"✗ Error al descargar {model}")
                    self.log_operation(f"Modelo IA: {model}", False, "Error en descarga")
                    success = False

            except Exception as e:
                self.ui.print_error(f"✗ Error al descargar {model}: {e}")
                self.log_operation(f"Modelo IA: {model}", False, str(e))
                success = False

        return success

    def install_context_menu_component(self):
        """
        Configura el menú contextual de Windows para facilitar el uso del Simplex Solver.
        """
        if not self.install_context_menu:
            return True

        self.ui.print_section("Instalando Menú Contextual")

        # Verificar permisos de administrador
        if not self.is_admin and platform.system() == "Windows":
            self.ui.print_error(
                "Se requieren permisos de administrador para instalar el menú contextual"
            )
            self.ui.print_info("Por favor, ejecuta el instalador como administrador")
            self.log_operation("Menú Contextual", False, "Sin permisos de administrador")
            return False

        if platform.system() != "Windows":
            self.ui.print_error("El menú contextual solo está disponible en Windows")
            self.log_operation("Menú Contextual", False, "Solo disponible en Windows")
            return False

        try:
            self.ui.print_info("Configurando menú contextual de Windows...")
            print()
            print(f"  {ConsoleColors.CYAN}► Creando entradas en el registro{ConsoleColors.RESET}")
            print(f"  {ConsoleColors.CYAN}► Configurando comandos del menú{ConsoleColors.RESET}")
            print()

            # Rutas necesarias
            context_menu_dir = self.project_root / "context_menu"
            bat_wrapper = context_menu_dir / "run_solver.bat"
            bat_wrapper_ai = context_menu_dir / "run_solver_ai.bat"

            # Verificar que existen los archivos
            if not bat_wrapper.exists():
                self.ui.print_error(f"No se encontró {bat_wrapper}")
                self.log_operation(
                    "Menú Contextual", False, f"Archivo no encontrado: run_solver.bat"
                )
                return False

            if not bat_wrapper_ai.exists():
                self.ui.print_error(f"No se encontró {bat_wrapper_ai}")
                self.log_operation(
                    "Menú Contextual", False, f"Archivo no encontrado: run_solver_ai.bat"
                )
                return False

            # Crear las entradas del registro usando Python directamente
            import winreg

            # Configurar para archivos .txt
            entries = [
                # Opción normal
                (r"txtfile\shell\SimplexSolver", "", "Resolver con Simplex Solver"),
                (r"txtfile\shell\SimplexSolver\command", "", f'"{bat_wrapper}" "%1"'),
                # Opción con IA
                (r"txtfile\shell\SimplexSolverAI", "", "Resolver con Simplex Solver (IA)"),
                (r"txtfile\shell\SimplexSolverAI\command", "", f'"{bat_wrapper_ai}" "%1"'),
            ]

            # Agregar entradas
            for key_path, value_name, value_data in entries:
                try:
                    key = winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, key_path)
                    winreg.SetValueEx(key, value_name, 0, winreg.REG_SZ, value_data)
                    winreg.CloseKey(key)
                except Exception as e:
                    self.ui.print_error(f"Error al crear {key_path}: {e}")
                    self.log_operation(
                        "Menú Contextual", False, f"Error en registro: {str(e)[:100]}"
                    )
                    return False

            print(f"  {ConsoleColors.GREEN}✓ Entradas del registro creadas{ConsoleColors.RESET}")
            print(f"  {ConsoleColors.GREEN}✓ Comandos configurados{ConsoleColors.RESET}")
            self.ui.print_success("✓ Menú contextual instalado correctamente")
            self.log_operation("Menú Contextual", True, "Registrado en Windows")
            return True

        except Exception as e:
            self.ui.print_error(f"Error inesperado: {e}")
            self.log_operation("Menú Contextual", False, str(e))
            return False

    def show_completion(self):
        """
        Muestra un mensaje final con el log de instalación y próximos pasos.
        """
        self.ui.clear_screen()
        self.ui.print_header("INSTALACIÓN COMPLETADA")

        # Mostrar log de instalación
        print(
            f"\n{ConsoleColors.WHITE}═══ REGISTRO DE INSTALACIÓN ══════════════════════════════════════{ConsoleColors.RESET}\n"
        )

        if self.installation_log:
            for entry in self.installation_log:
                status_color = ConsoleColors.GREEN if entry["success"] else ConsoleColors.RED
                print(
                    f"  {status_color}{entry['status']}{ConsoleColors.RESET} {ConsoleColors.WHITE}{entry['operation']:<30}{ConsoleColors.RESET}",
                    end="",
                )
                if entry["details"]:
                    print(f" - {ConsoleColors.CYAN}{entry['details']}{ConsoleColors.RESET}")
                else:
                    print()
        else:
            print(f"  {ConsoleColors.YELLOW}(No hay operaciones registradas){ConsoleColors.RESET}")

        print(
            f"\n{ConsoleColors.WHITE}══════════════════════════════════════════════════════════════════{ConsoleColors.RESET}\n"
        )

        # Contar éxitos y fallos
        total = len(self.installation_log)
        successes = sum(1 for entry in self.installation_log if entry["success"])
        failures = total - successes

        if failures == 0:
            self.ui.print_success(
                f"✓ Todas las operaciones completadas exitosamente ({successes}/{total})"
            )
        else:
            self.ui.print_warning(
                f"⚠ {successes}/{total} operaciones exitosas, {failures} con problemas"
            )

            # Mostrar detalles de los errores
            print(f"\n{ConsoleColors.YELLOW}Detalles de los problemas:{ConsoleColors.RESET}")
            for entry in self.installation_log:
                if not entry["success"]:
                    print(
                        f"  {ConsoleColors.RED}•{ConsoleColors.RESET} {ConsoleColors.WHITE}{entry['operation']}{ConsoleColors.RESET}"
                    )
                    if entry["details"]:
                        # Mostrar detalles completos del error
                        details_lines = entry["details"].split(" | ")
                        for detail in details_lines:
                            print(f"    {ConsoleColors.CYAN}{detail}{ConsoleColors.RESET}")
            print()

        print(f"\n{ConsoleColors.WHITE}Próximos pasos:{ConsoleColors.RESET}\n")

        print(f"1. Para usar el solver interactivo:")
        print(f"   {ConsoleColors.CYAN}python simplex.py --interactive{ConsoleColors.RESET}")

        print(f"\n2. Para resolver un archivo:")
        print(
            f"   {ConsoleColors.CYAN}python simplex.py ejemplos/ejemplo_maximizacion.txt{ConsoleColors.RESET}"
        )

        if self.install_ollama and self.selected_models:
            print(f"\n3. Para usar el modo IA:")
            print(
                f'   {ConsoleColors.CYAN}python simplex.py --ai "tu problema en lenguaje natural"{ConsoleColors.RESET}'
            )

        if self.install_context_menu:
            print(f"\n4. Desde el explorador de Windows:")
            print(
                f"   {ConsoleColors.CYAN}Click derecho en un archivo .txt > Resolver con Simplex{ConsoleColors.RESET}"
            )

        print(f"\n{ConsoleColors.WHITE}Documentación:{ConsoleColors.RESET}")
        print(f"  • README.md - Guía general")
        print(f"  • docs/GUIA_IA.md - Guía del sistema de IA")
        print(f"  • ejemplos/ - Problemas de ejemplo")

        print(f"\n{ConsoleColors.GREEN}¡Gracias por usar Simplex Solver!{ConsoleColors.RESET}\n")

        # Esperar antes de cerrar
        print(
            f"{ConsoleColors.CYAN}Presiona Enter para cerrar el instalador...{ConsoleColors.RESET}"
        )
        input()

    def run(self):
        """
        Ejecuta el flujo completo del instalador, desde la bienvenida hasta la finalización.
        """
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
            self.ui.clear_screen()
            self.ui.print_header("PROCESO DE INSTALACIÓN")

            # Calcular total de tareas
            total_tasks = 1  # Dependencias siempre
            if self.install_ollama:
                total_tasks += 1
                if self.selected_models:
                    total_tasks += len(self.selected_models)
            if self.install_context_menu:
                total_tasks += 1

            current_task = 0

            def show_overall_progress(task_name, task_num, total):
                """Muestra el progreso general."""
                progress = int((task_num / total) * 50)
                bar = "█" * progress + "░" * (50 - progress)
                percentage = int((task_num / total) * 100)
                print(
                    f"\n{ConsoleColors.CYAN}╔══════════════════════════════════════════════════════════════════════╗{ConsoleColors.RESET}"
                )
                print(
                    f"{ConsoleColors.CYAN}║{ConsoleColors.RESET} PROGRESO GENERAL: [{bar}] {percentage}%{' ' * (70 - 34 - len(str(percentage)))}║"
                )
                print(
                    f"{ConsoleColors.CYAN}║{ConsoleColors.RESET} Tarea {task_num}/{total}: {task_name[:52]:<52}{' ' * (70 - 67)}║"
                )
                print(
                    f"{ConsoleColors.CYAN}╚══════════════════════════════════════════════════════════════════════╝{ConsoleColors.RESET}\n"
                )

            # Instalar dependencias de Python
            current_task += 1
            show_overall_progress("Instalando dependencias de Python", current_task, total_tasks)
            if not self.install_python_dependencies():
                self.ui.print_error("Fallo en la instalación de dependencias")
                return False

            # Instalar Ollama
            if self.install_ollama:
                current_task += 1
                show_overall_progress("Verificando Ollama", current_task, total_tasks)
                if not self.install_ollama_component():
                    self.ui.print_warning("Continúa la instalación sin Ollama")
                else:
                    # Descargar modelos
                    if self.selected_models:
                        for idx, model in enumerate(self.selected_models, 1):
                            current_task += 1
                            show_overall_progress(
                                f"Descargando modelo {model}", current_task, total_tasks
                            )
                            # La descarga ya muestra su propio progreso
                        self.download_ai_models()

            # Instalar menú contextual
            if self.install_context_menu:
                current_task += 1
                show_overall_progress("Instalando menú contextual", current_task, total_tasks)
                self.install_context_menu_component()

            # Mostrar completado
            print(
                f"\n{ConsoleColors.CYAN}╔══════════════════════════════════════════════════════════════════════╗{ConsoleColors.RESET}"
            )
            print(
                f"{ConsoleColors.CYAN}║{ConsoleColors.RESET} PROGRESO GENERAL: [{'█' * 50}] 100%{' ' * 13}║"
            )
            print(
                f"{ConsoleColors.CYAN}║{ConsoleColors.RESET} {ConsoleColors.GREEN}✓ TODAS LAS TAREAS COMPLETADAS{ConsoleColors.RESET}{' ' * 39}║"
            )
            print(
                f"{ConsoleColors.CYAN}╚══════════════════════════════════════════════════════════════════════╝{ConsoleColors.RESET}\n"
            )

            # Paso 8: Finalización
            self.show_completion()

            return True

        except KeyboardInterrupt:
            print(
                f"\n\n{ConsoleColors.YELLOW}Instalación cancelada por el usuario{ConsoleColors.RESET}"
            )
            return False
        except Exception as e:
            self.ui.print_error(f"Error inesperado: {e}")
            import traceback

            traceback.print_exc()
            return False


def main():
    """
    Punto de entrada principal del script.
    Crea una instancia del instalador y ejecuta el proceso.
    """
    installer = SimplexInstaller()
    success = installer.run()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
