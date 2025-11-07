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

try:
    import winshell
    from winshell.shortcut import Shortcut

    WINSHELL_AVAILABLE = True
except ImportError:
    WINSHELL_AVAILABLE = False

# Alternativa usando win32com
try:
    import win32com.client

    WIN32COM_AVAILABLE = True
except ImportError:
    WIN32COM_AVAILABLE = False

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
        try:
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

            # Verificar que project_root existe
            if not self.project_root.exists():
                raise RuntimeError(f"El directorio del proyecto no existe: {self.project_root}")

        except Exception as e:
            print(f"ERROR CRÍTICO al inicializar el instalador: {e}")
            import traceback

            traceback.print_exc()
            raise

    def _get_install_dir(self) -> Path:
        """
        Obtiene la ruta de instalación del programa.

        Returns:
            Path: Ruta donde se instala el programa
        """
        program_files = Path(os.environ.get("ProgramFiles", "C:/Program Files"))
        return program_files / "SimplexSolver"

    def _is_already_installed(self) -> bool:
        """
        Verifica si el programa ya está instalado en el sistema.

        Returns:
            bool: True si está instalado, False en caso contrario
        """
        install_dir = self._get_install_dir()
        exe_path = install_dir / "simplex.exe"
        return exe_path.exists()

    def _get_installed_version(self) -> Optional[str]:
        """
        Obtiene la versión del programa instalado.

        Returns:
            Optional[str]: Versión instalada o None si no se puede determinar
        """
        try:
            install_dir = self._get_install_dir()
            exe_path = install_dir / "simplex.exe"

            if exe_path.exists():
                result = subprocess.run(
                    [str(exe_path), "--version"], capture_output=True, text=True, timeout=5
                )
                if result.returncode == 0:
                    # Extraer versión del output
                    version = result.stdout.strip()
                    return version if version else "Desconocida"
        except Exception:
            pass
        return None

    def show_reinstall_options(self) -> str:
        """
        Muestra opciones cuando el programa ya está instalado.

        Returns:
            str: Opción seleccionada ('reinstall', 'update', 'uninstall', 'cancel')
        """
        self.ui.clear_screen()
        self.ui.print_header("INSTALACIÓN EXISTENTE DETECTADA")

        install_dir = self._get_install_dir()
        version = self._get_installed_version()

        print(
            f"{ConsoleColors.YELLOW}⚠ Simplex Solver ya está instalado en el sistema{ConsoleColors.RESET}\n"
        )
        print(f"{ConsoleColors.WHITE}Detalles de la instalación actual:{ConsoleColors.RESET}")
        print(f"  • Ubicación: {ConsoleColors.CYAN}{install_dir}{ConsoleColors.RESET}")
        if version:
            print(f"  • Versión: {ConsoleColors.CYAN}{version}{ConsoleColors.RESET}")
        print()

        print(f"{ConsoleColors.WHITE}¿Qué deseas hacer?{ConsoleColors.RESET}\n")
        print(
            f"  {ConsoleColors.GREEN}1.{ConsoleColors.RESET} Reinstalar (eliminar e instalar de nuevo)"
        )
        print(f"     - Configuración limpia desde cero")
        print(f"     - Se perderán configuraciones personalizadas")
        print()
        print(
            f"  {ConsoleColors.GREEN}2.{ConsoleColors.RESET} Actualizar/Reparar (mantener configuración)"
        )
        print(f"     - Actualiza archivos del programa")
        print(f"     - Mantiene tu configuración de IA y historial")
        print()
        print(f"  {ConsoleColors.GREEN}3.{ConsoleColors.RESET} Desinstalar")
        print(f"     - Elimina el programa completamente")
        print(f"     - Limpia PATH y menú contextual")
        print()
        print(f"  {ConsoleColors.GREEN}4.{ConsoleColors.RESET} Cancelar (no hacer nada)")
        print()

        while True:
            choice = self.ui.get_input("Selecciona una opción (1-4)")

            if choice == "1":
                if self.ui.ask_yes_no(
                    "¿Confirmas que deseas REINSTALAR? (se perderá la configuración)", default=False
                ):
                    return "reinstall"
            elif choice == "2":
                if self.ui.ask_yes_no("¿Confirmas que deseas ACTUALIZAR/REPARAR?", default=True):
                    return "update"
            elif choice == "3":
                if self.ui.ask_yes_no("¿Confirmas que deseas DESINSTALAR?", default=False):
                    return "uninstall"
            elif choice == "4":
                return "cancel"
            else:
                self.ui.print_warning("Por favor selecciona una opción válida (1-4)")

    def uninstall_program(self) -> bool:
        """
        Desinstala el programa completamente.

        Returns:
            bool: True si se desinstaló correctamente
        """
        self.ui.clear_screen()
        self.ui.print_header("DESINSTALANDO SIMPLEX SOLVER")

        success = True
        install_dir = self._get_install_dir()

        # 1. Eliminar directorio de instalación
        if install_dir.exists():
            try:
                self.ui.print_info(f"Eliminando archivos de {install_dir}...")
                shutil.rmtree(install_dir)
                self.ui.print_success("✓ Archivos del programa eliminados")
            except Exception as e:
                self.ui.print_error(f"✗ Error al eliminar archivos: {e}")
                success = False

        # 2. Eliminar acceso directo del escritorio
        try:
            desktop = os.path.join(os.path.expanduser("~"), "Desktop")
            shortcut_path = os.path.join(desktop, "Simplex Solver (Consola).lnk")
            if os.path.exists(shortcut_path):
                os.remove(shortcut_path)
                self.ui.print_success("✓ Acceso directo eliminado")
        except Exception as e:
            self.ui.print_warning(f"⚠ No se pudo eliminar acceso directo: {e}")

        # 3. Limpiar menú contextual
        try:
            if platform.system() == "Windows":
                import winreg

                keys_to_delete = [r"txtfile\shell\SimplexSolver", r"txtfile\shell\SimplexSolverAI"]

                for key_path in keys_to_delete:
                    try:
                        winreg.DeleteKey(winreg.HKEY_CLASSES_ROOT, key_path + r"\command")
                        winreg.DeleteKey(winreg.HKEY_CLASSES_ROOT, key_path)
                    except WindowsError:
                        pass  # La clave no existe o no se puede eliminar

                self.ui.print_success("✓ Menú contextual limpiado")
        except Exception as e:
            self.ui.print_warning(f"⚠ No se pudo limpiar menú contextual: {e}")

        # 4. Informar sobre PATH (no se puede limpiar automáticamente de forma segura)
        if success:
            print()
            self.ui.print_success("✓ Desinstalación completada")
            print()
            self.ui.print_info("NOTA: El PATH del sistema no se modificó automáticamente")
            print(f"  Si deseas eliminarlo manualmente:")
            print(f"  1. Abre 'Variables de entorno'")
            print(f"  2. Edita la variable PATH")
            print(
                f"  3. Elimina la entrada: {ConsoleColors.CYAN}{install_dir}{ConsoleColors.RESET}"
            )
            print()

            # Preguntar si desea eliminar configuración de usuario
            if self.ui.ask_yes_no(
                "¿Deseas eliminar también la configuración de usuario?", default=False
            ):
                self._delete_user_config()

        return success

    def _delete_user_config(self):
        """
        Elimina la configuración de usuario (config, historial, logs).
        """
        try:
            if platform.system() == "Windows":
                appdata = os.getenv("APPDATA", "")
                config_dir = Path(appdata) / "SimplexSolver"
            else:
                home = os.path.expanduser("~")
                config_dir = Path(home) / ".simplex_solver"

            if config_dir.exists():
                shutil.rmtree(config_dir)
                self.ui.print_success(f"✓ Configuración de usuario eliminada: {config_dir}")
            else:
                self.ui.print_info("No se encontró configuración de usuario")
        except Exception as e:
            self.ui.print_warning(f"⚠ No se pudo eliminar configuración: {e}")

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
        Detecta si hay una instalación previa y ofrece opciones.
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

        # Verificar si ya está instalado
        if self._is_already_installed():
            print(f"{ConsoleColors.CYAN}Presiona Enter para continuar...{ConsoleColors.RESET}")
            input()
            return  # Continuará al método run() que manejará las opciones

        # Instalación nueva - mostrar bienvenida normal
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

        # Mostrar RAM disponible para que el usuario entienda las recomendaciones
        ram_total = self.analyzer.capabilities.total_ram_gb
        ram_usable = ram_total * 0.8  # 80% de la RAM total es usable
        print(
            f"{ConsoleColors.CYAN}RAM del sistema: {ram_total:.1f} GB (aprox. {ram_usable:.1f} GB usables para modelos){ConsoleColors.RESET}\n"
        )

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

    def install_program_files(self) -> Optional[str]:
        """
        Copia el SimplexSolver.exe a Program Files.
        """
        try:
            # Determina la ruta de instalación
            program_files = Path(os.environ.get("ProgramFiles", "C:/Program Files"))
            install_dir = program_files / "SimplexSolver"
            install_dir.mkdir(parents=True, exist_ok=True)

            # Determina la ruta de origen (donde PyInstaller desempaquetó el solver)
            source_exe_path = Path(getattr(sys, "_MEIPASS", ".")) / "SimplexSolver.exe"

            if not source_exe_path.exists():
                self.ui.print_error(
                    "Error: SimplexSolver.exe no se encontró dentro del instalador."
                )
                self.log_operation("Copiar Archivos", False, "Solver no encontrado")
                return None

            # Copia el archivo
            target_exe_path = install_dir / "SimplexSolver.exe"
            shutil.copy(source_exe_path, target_exe_path)
            self.ui.print_success(f"Programa instalado en {install_dir}")
            self.log_operation("Copiar Archivos", True, str(install_dir))

            # Renombrar a 'simplex.exe'
            final_exe_path = install_dir / "simplex.exe"
            if final_exe_path.exists():
                final_exe_path.unlink()
            target_exe_path.rename(final_exe_path)
            self.ui.print_info(f"Renombrado a {final_exe_path.name}")

            return str(install_dir)  # Devuelve la ruta de instalación

        except Exception as e:
            self.ui.print_error(f"Error al copiar archivos: {e}")
            self.log_operation("Copiar Archivos", False, str(e))
            return None

    def setup_environment_path(self, install_dir: str):
        """
        Agrega el directorio de instalación al PATH del sistema.
        """
        if not self.is_admin:
            self.ui.print_warning("Se requieren permisos de admin para modificar el PATH.")
            self.log_operation("Modificar PATH", False, "Sin admin")
            return False

        try:
            self.ui.print_info("Agregando al PATH del sistema...")
            # Usar setx /M para modificar el PATH de MÁQUINA (requiere admin)
            cmd = ["setx", "/M", "PATH", f"%PATH%;{install_dir}"]
            subprocess.run(cmd, check=True, capture_output=True, text=True, shell=False)

            self.ui.print_success("PATH del sistema actualizado.")
            self.ui.print_warning(
                "Es posible que necesites reiniciar la consola (cmd) para ver los cambios."
            )
            self.log_operation("Modificar PATH", True, install_dir)
            return True

        except Exception as e:
            error_detail = str(e)
            if hasattr(e, "stderr"):
                error_detail = e.stderr
            self.ui.print_error(f"No se pudo modificar el PATH: {error_detail}")
            self.log_operation("Modificar PATH", False, error_detail)
            return False

    def create_desktop_shortcut(self, install_dir: str):
        """
        Crea un acceso directo en el escritorio que abre la consola interactiva.
        """
        # Intentar primero con PowerShell (siempre disponible en Windows)
        if platform.system() == "Windows":
            return self._create_shortcut_powershell(install_dir)
        # Intentar con win32com si PowerShell falla
        elif WIN32COM_AVAILABLE:
            return self._create_shortcut_win32com(install_dir)
        elif WINSHELL_AVAILABLE:
            return self._create_shortcut_winshell(install_dir)
        else:
            self.ui.print_warning("No hay módulos disponibles para crear accesos directos.")
            self.ui.print_info("Instala: pip install pywin32 winshell")
            self.log_operation("Acceso Directo", False, "Módulos no disponibles")
            return False

    def _create_shortcut_powershell(self, install_dir: str):
        """
        Crea acceso directo usando PowerShell (el método más confiable en Windows).
        """
        try:
            self.ui.print_info("Creando acceso directo en el escritorio (PowerShell)...")

            # Obtener ruta del escritorio
            desktop = os.path.join(os.path.expanduser("~"), "Desktop")
            link_filepath = os.path.join(desktop, "Simplex Solver (Consola).lnk")
            solver_exe_path = str(Path(install_dir) / "simplex.exe")

            # Script de PowerShell para crear el acceso directo
            ps_script = f"""
$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("{link_filepath}")
$Shortcut.TargetPath = "cmd.exe"
$Shortcut.Arguments = '/K "{solver_exe_path}"'
$Shortcut.WorkingDirectory = "{install_dir}"
$Shortcut.Description = "Consola interactiva de Simplex Solver"
$Shortcut.IconLocation = "{solver_exe_path},0"
$Shortcut.Save()
"""

            # Ejecutar PowerShell
            result = subprocess.run(
                ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps_script],
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode == 0 and os.path.exists(link_filepath):
                self.ui.print_success("✓ Acceso directo creado en el escritorio.")
                self.log_operation("Acceso Directo", True, link_filepath)
                return True
            else:
                error_msg = result.stderr if result.stderr else "Error desconocido"
                self.ui.print_warning(f"PowerShell falló: {error_msg}")
                # Intentar método alternativo
                if WIN32COM_AVAILABLE:
                    self.ui.print_info("Intentando método alternativo...")
                    return self._create_shortcut_win32com(install_dir)
                return False

        except subprocess.TimeoutExpired:
            self.ui.print_error("Timeout al ejecutar PowerShell")
            self.log_operation("Acceso Directo", False, "Timeout en PowerShell")
            return False
        except Exception as e:
            self.ui.print_error(f"Error creando acceso directo (PowerShell): {e}")
            self.log_operation("Acceso Directo", False, str(e))
            # Intentar método alternativo
            if WIN32COM_AVAILABLE:
                self.ui.print_info("Intentando método alternativo...")
                return self._create_shortcut_win32com(install_dir)
            return False

    def _create_shortcut_win32com(self, install_dir: str):
        """
        Crea acceso directo usando win32com (más compatible con PyInstaller).
        """
        try:
            import win32com.client
            import os

            self.ui.print_info("Creando acceso directo en el escritorio (win32com)...")

            # Obtener ruta del escritorio
            desktop = os.path.join(os.path.expanduser("~"), "Desktop")
            link_filepath = os.path.join(desktop, "Simplex Solver (Consola).lnk")

            solver_exe_path = str(Path(install_dir) / "simplex.exe")

            # Crear el acceso directo
            shell = win32com.client.Dispatch("WScript.Shell")
            shortcut = shell.CreateShortcut(link_filepath)
            shortcut.TargetPath = "cmd.exe"
            shortcut.Arguments = f'/K "{solver_exe_path}"'
            shortcut.WorkingDirectory = install_dir
            shortcut.Description = "Consola interactiva de Simplex Solver"
            shortcut.IconLocation = solver_exe_path
            shortcut.Save()

            self.ui.print_success("Acceso directo creado en el escritorio.")
            self.log_operation("Acceso Directo", True, link_filepath)
            return True

        except Exception as e:
            self.ui.print_error(f"Error creando acceso directo (win32com): {e}")
            self.log_operation("Acceso Directo", False, str(e))
            return False

    def _create_shortcut_winshell(self, install_dir: str):
        """
        Crea acceso directo usando winshell (método alternativo).
        """
        try:
            desktop = winshell.desktop()
            link_filepath = str(Path(desktop) / "Simplex Solver (Consola).lnk")

            solver_exe_path = str(Path(install_dir) / "simplex.exe")

            with Shortcut(link_filepath) as link:
                link.path = "cmd.exe"
                # /K mantiene la consola abierta y ejecuta "simplex.exe"
                link.arguments = f'/K ""{solver_exe_path}""'
                link.description = "Consola interactiva de Simplex Solver"
                link.working_directory = install_dir

            self.ui.print_success("Acceso directo creado en el escritorio.")
            self.log_operation("Acceso Directo", True, link_filepath)
            return True

        except Exception as e:
            self.ui.print_error(f"No se pudo crear el acceso directo: {e}")
            self.log_operation("Acceso Directo", False, str(e))
            return False

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
            with open(requirements_file, "r", encoding="utf-8") as f:
                packages = []
                for line in f:
                    line = line.strip()
                    # Saltar líneas vacías o comentarios completos
                    if not line or line.startswith("#"):
                        continue
                    # Eliminar comentarios inline (después del #)
                    if "#" in line:
                        line = line.split("#")[0].strip()
                    # Agregar solo si quedó algo después de limpiar
                    if line:
                        packages.append(line)

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
            # Los comandos deben ejecutarse con cmd.exe /c para que funcionen desde el menú contextual
            entries = [
                # Opción normal
                (r"txtfile\shell\SimplexSolver", "", "Resolver con Simplex Solver"),
                (
                    r"txtfile\shell\SimplexSolver\command",
                    "",
                    f'cmd.exe /c ""{bat_wrapper}"" ""%1""',
                ),
                # Opción con IA
                (r"txtfile\shell\SimplexSolverAI", "", "Resolver con Simplex Solver (IA)"),
                (
                    r"txtfile\shell\SimplexSolverAI\command",
                    "",
                    f'cmd.exe /c ""{bat_wrapper_ai}"" ""%1""',
                ),
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

        print(f"1. Para usar el solver desde cualquier lugar:")
        print(f"   {ConsoleColors.CYAN}simplex --interactive{ConsoleColors.RESET}")
        print(
            f"   {ConsoleColors.YELLOW}(Reinicia tu consola/terminal para que el PATH se actualice){ConsoleColors.RESET}"
        )

        print(f"\n2. Para resolver un archivo:")
        print(f"   {ConsoleColors.CYAN}simplex ruta\\archivo.txt{ConsoleColors.RESET}")

        print(f"\n3. Desde el acceso directo del escritorio:")
        print(
            f"   {ConsoleColors.CYAN}Haz doble clic en 'Simplex Solver (Consola)'{ConsoleColors.RESET}"
        )

        if self.install_ollama and self.selected_models:
            print(f"\n4. Para usar el modo IA:")
            print(
                f'   {ConsoleColors.CYAN}simplex --ai "tu problema en lenguaje natural"{ConsoleColors.RESET}'
            )

        if self.install_context_menu:
            print(f"\n5. Desde el explorador de Windows:")
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
        try:
            enable_ansi_colors()
        except Exception as e:
            print(f"Advertencia: No se pudieron habilitar colores ANSI: {e}")
            print("Continuando sin colores...")

        try:
            # Paso 1: Bienvenida
            self.show_welcome()

            # Verificar si ya está instalado y manejar opciones
            if self._is_already_installed():
                action = self.show_reinstall_options()

                if action == "cancel":
                    self.ui.print_info("Instalación cancelada por el usuario")
                    self.ui.pause("Presiona Enter para salir...")
                    return True

                elif action == "uninstall":
                    if self.uninstall_program():
                        self.ui.pause("Presiona Enter para salir...")
                        return True
                    else:
                        self.ui.print_error("La desinstalación tuvo problemas")
                        self.ui.pause("Presiona Enter para salir...")
                        return False

                elif action == "reinstall":
                    self.ui.clear_screen()
                    self.ui.print_header("REINSTALACIÓN")
                    self.ui.print_info("Eliminando instalación anterior...")

                    # Eliminar instalación previa
                    install_dir = self._get_install_dir()
                    if install_dir.exists():
                        try:
                            shutil.rmtree(install_dir)
                            self.ui.print_success("✓ Instalación anterior eliminada")
                        except Exception as e:
                            self.ui.print_error(f"Error al eliminar instalación previa: {e}")
                            return False

                    # Continuar con instalación normal
                    self.ui.print_info("Continuando con instalación limpia...")
                    self.ui.pause()

                elif action == "update":
                    self.ui.clear_screen()
                    self.ui.print_header("ACTUALIZACIÓN/REPARACIÓN")
                    self.ui.print_info(
                        "Se actualizarán los archivos del programa manteniendo tu configuración"
                    )
                    self.ui.pause()
                    # Continuar con instalación (sobrescribirá archivos)

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
            total_tasks = 3  # Instalar archivos, configurar PATH, crear acceso directo (siempre)
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

            # Tarea 1: Instalar archivos
            current_task += 1
            show_overall_progress("Instalando archivos del programa", current_task, total_tasks)
            install_dir = self.install_program_files()

            if not install_dir:
                self.ui.print_error("Fallo en la instalación de archivos. Abortando.")
                self.show_completion()
                return False

            # Tarea 2: Configurar PATH
            current_task += 1
            show_overall_progress(
                "Configurando variables de entorno (PATH)", current_task, total_tasks
            )
            self.setup_environment_path(install_dir)

            # Tarea 3: Crear Acceso Directo
            current_task += 1
            show_overall_progress("Creando accesos directos", current_task, total_tasks)
            self.create_desktop_shortcut(install_dir)

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
            print(f"{ConsoleColors.CYAN}Presiona Enter para salir...{ConsoleColors.RESET}")
            try:
                input()
            except:
                pass
            return False
        except Exception as e:
            self.ui.print_error(f"Error inesperado durante la instalación: {e}")
            print(f"\n{ConsoleColors.WHITE}Tipo de error:{ConsoleColors.RESET} {type(e).__name__}")
            print(f"{ConsoleColors.WHITE}Detalles:{ConsoleColors.RESET} {str(e)}\n")

            import traceback

            print(f"{ConsoleColors.YELLOW}Stack trace completo:{ConsoleColors.RESET}")
            traceback.print_exc()

            print(
                f"\n{ConsoleColors.CYAN}Presiona Enter para ver el log y salir...{ConsoleColors.RESET}"
            )
            try:
                input()
            except:
                pass

            return False


def main():
    """
    Punto de entrada principal del script.
    Crea una instancia del instalador y ejecuta el proceso.
    """
    try:
        installer = SimplexInstaller()
        success = installer.run()

        if not success:
            print(
                f"\n{ConsoleColors.RED}═══════════════════════════════════════════════════════════════════════{ConsoleColors.RESET}"
            )
            print(
                f"{ConsoleColors.RED}║ La instalación no se completó exitosamente                           ║{ConsoleColors.RESET}"
            )
            print(
                f"{ConsoleColors.RED}═══════════════════════════════════════════════════════════════════════{ConsoleColors.RESET}\n"
            )

    except Exception as e:
        print(
            f"\n{ConsoleColors.RED}═══════════════════════════════════════════════════════════════════════{ConsoleColors.RESET}"
        )
        print(
            f"{ConsoleColors.RED}║ ERROR CRÍTICO EN EL INSTALADOR                                       ║{ConsoleColors.RESET}"
        )
        print(
            f"{ConsoleColors.RED}═══════════════════════════════════════════════════════════════════════{ConsoleColors.RESET}"
        )
        print(f"\n{ConsoleColors.WHITE}Tipo de error:{ConsoleColors.RESET} {type(e).__name__}")
        print(f"{ConsoleColors.WHITE}Mensaje:{ConsoleColors.RESET} {str(e)}\n")

        import traceback

        print(f"{ConsoleColors.YELLOW}Stack trace completo:{ConsoleColors.RESET}")
        traceback.print_exc()

        success = False

    finally:
        # PAUSA FINAL - Siempre esperar antes de cerrar
        print(
            f"\n{ConsoleColors.CYAN}═══════════════════════════════════════════════════════════════════════{ConsoleColors.RESET}"
        )
        print(
            f"{ConsoleColors.CYAN}Presiona Enter para cerrar esta ventana...{ConsoleColors.RESET}"
        )
        print(
            f"{ConsoleColors.CYAN}═══════════════════════════════════════════════════════════════════════{ConsoleColors.RESET}"
        )
        try:
            input()
        except:
            pass  # Si input() falla, al menos intentamos

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
