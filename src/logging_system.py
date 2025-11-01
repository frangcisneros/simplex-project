"""
Sistema de Logging con SQLite para Simplex Solver.
Proporciona logging completo con almacenamiento en base de datos.
"""

import sqlite3
import os
import sys
import platform
import traceback
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from pathlib import Path
import threading


class LogLevel:
    """Niveles de log disponibles."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class LoggingSystem:
    """
    Sistema centralizado de logging con SQLite.
    Captura eventos del sistema con información detallada.
    """

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        """Singleton pattern para asegurar una sola instancia."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """Inicializa el sistema de logging."""
        if not hasattr(self, "initialized"):
            self.db_path = self._get_db_path()
            self.retention_days = 180  # 6 meses
            self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            self._init_database()
            self._log_system_info()
            self.initialized = True

    def _get_db_path(self) -> str:
        """Obtiene la ruta de la base de datos."""
        if getattr(sys, "frozen", False):
            # Si es ejecutable, guardar en carpeta del usuario
            app_data = os.getenv("APPDATA") or os.path.expanduser("~")
            log_dir = os.path.join(app_data, "SimplexSolver", "logs")
        else:
            # Si es desarrollo, guardar en carpeta del proyecto
            log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")

        os.makedirs(log_dir, exist_ok=True)
        return os.path.join(log_dir, "simplex_logs.db")

    def _init_database(self):
        """Inicializa la base de datos y crea las tablas necesarias."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Tabla principal de logs
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                session_id TEXT NOT NULL,
                level TEXT NOT NULL,
                module TEXT NOT NULL,
                function TEXT,
                line_number INTEGER,
                message TEXT NOT NULL,
                exception_type TEXT,
                exception_message TEXT,
                stack_trace TEXT,
                user_data TEXT,
                system_info TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        # Tabla de sesiones
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT UNIQUE NOT NULL,
                start_time TEXT NOT NULL,
                end_time TEXT,
                python_version TEXT,
                os_system TEXT,
                os_version TEXT,
                machine TEXT,
                processor TEXT,
                app_version TEXT,
                execution_mode TEXT,
                command_line_args TEXT
            )
        """
        )

        # Tabla de eventos específicos del solver
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS solver_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                event_type TEXT NOT NULL,
                problem_type TEXT,
                num_variables INTEGER,
                num_constraints INTEGER,
                iterations INTEGER,
                execution_time_ms REAL,
                status TEXT,
                optimal_value REAL,
                additional_data TEXT
            )
        """
        )

        # Tabla de archivos procesados
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS file_operations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                operation_type TEXT NOT NULL,
                file_path TEXT NOT NULL,
                file_size INTEGER,
                success INTEGER,
                error_message TEXT
            )
        """
        )

        # Tabla de historial de problemas resueltos
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS problem_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                file_path TEXT NOT NULL,
                file_name TEXT NOT NULL,
                file_content TEXT NOT NULL,
                problem_type TEXT,
                num_variables INTEGER,
                num_constraints INTEGER,
                iterations INTEGER,
                execution_time_ms REAL,
                status TEXT,
                optimal_value REAL,
                solution_variables TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        # Índices para mejorar el rendimiento
        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_logs_timestamp 
            ON logs(timestamp)
        """
        )
        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_logs_level 
            ON logs(level)
        """
        )
        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_logs_session 
            ON logs(session_id)
        """
        )
        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_sessions_start 
            ON sessions(start_time)
        """
        )

        conn.commit()
        conn.close()

        # Limpiar logs antiguos
        self._cleanup_old_logs()

    def _log_system_info(self):
        """Registra información del sistema al inicio de la sesión."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute(
                """
                INSERT INTO sessions (
                    session_id, start_time, python_version, os_system, 
                    os_version, machine, processor, execution_mode, 
                    command_line_args
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    self.session_id,
                    datetime.now().isoformat(),
                    sys.version,
                    platform.system(),
                    platform.version(),
                    platform.machine(),
                    platform.processor(),
                    "executable" if getattr(sys, "frozen", False) else "development",
                    " ".join(sys.argv),
                ),
            )
            conn.commit()
        except Exception as e:
            print(f"Error logging system info: {e}")
        finally:
            conn.close()

    def log(
        self,
        level: str,
        message: str,
        module: str = None,
        function: str = None,
        exception: Exception = None,
        user_data: Dict[str, Any] = None,
    ):
        """
        Registra un evento en el sistema de logs.

        Args:
            level: Nivel del log (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            message: Mensaje del log
            module: Nombre del módulo que genera el log
            function: Nombre de la función que genera el log
            exception: Excepción capturada (opcional)
            user_data: Datos adicionales del usuario (opcional)
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # Obtener información del stack trace
            frame = sys._getframe(1)
            if not module:
                module = frame.f_code.co_filename.split(os.sep)[-1]
            if not function:
                function = frame.f_code.co_name
            line_number = frame.f_lineno

            # Información de la excepción
            exception_type = None
            exception_message = None
            stack_trace = None

            if exception:
                exception_type = type(exception).__name__
                exception_message = str(exception)
                stack_trace = "".join(
                    traceback.format_exception(
                        type(exception), exception, exception.__traceback__
                    )
                )

            # Convertir user_data a string si existe
            user_data_str = str(user_data) if user_data else None

            cursor.execute(
                """
                INSERT INTO logs (
                    timestamp, session_id, level, module, function, 
                    line_number, message, exception_type, exception_message, 
                    stack_trace, user_data
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    datetime.now().isoformat(),
                    self.session_id,
                    level,
                    module,
                    function,
                    line_number,
                    message,
                    exception_type,
                    exception_message,
                    stack_trace,
                    user_data_str,
                ),
            )

            conn.commit()

            # Imprimir en consola según el nivel
            self._print_log(level, message, module, function)

        except Exception as e:
            print(f"Error in logging system: {e}")
        finally:
            conn.close()

    def _print_log(self, level: str, message: str, module: str, function: str):
        """Imprime el log en consola con formato."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Colores ANSI para Windows
        colors = {
            "DEBUG": "\033[36m",  # Cyan
            "INFO": "\033[32m",  # Green
            "WARNING": "\033[33m",  # Yellow
            "ERROR": "\033[31m",  # Red
            "CRITICAL": "\033[35m",  # Magenta
        }
        reset = "\033[0m"

        color = colors.get(level, "")
        print(f"{color}[{timestamp}] [{level}] [{module}.{function}]{reset} {message}")

    def log_solver_event(
        self,
        event_type: str,
        problem_type: str = None,
        num_variables: int = None,
        num_constraints: int = None,
        iterations: int = None,
        execution_time_ms: float = None,
        status: str = None,
        optimal_value: float = None,
        additional_data: Dict[str, Any] = None,
    ):
        """Registra eventos específicos del solver."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute(
                """
                INSERT INTO solver_events (
                    session_id, timestamp, event_type, problem_type, 
                    num_variables, num_constraints, iterations, 
                    execution_time_ms, status, optimal_value, additional_data
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    self.session_id,
                    datetime.now().isoformat(),
                    event_type,
                    problem_type,
                    num_variables,
                    num_constraints,
                    iterations,
                    execution_time_ms,
                    status,
                    optimal_value,
                    str(additional_data) if additional_data else None,
                ),
            )
            conn.commit()
        except Exception as e:
            print(f"Error logging solver event: {e}")
        finally:
            conn.close()

    def log_file_operation(
        self,
        operation_type: str,
        file_path: str,
        success: bool,
        error_message: str = None,
    ):
        """Registra operaciones con archivos."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            file_size = None
            if os.path.exists(file_path):
                file_size = os.path.getsize(file_path)

            cursor.execute(
                """
                INSERT INTO file_operations (
                    session_id, timestamp, operation_type, file_path, 
                    file_size, success, error_message
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    self.session_id,
                    datetime.now().isoformat(),
                    operation_type,
                    file_path,
                    file_size,
                    1 if success else 0,
                    error_message,
                ),
            )
            conn.commit()
        except Exception as e:
            print(f"Error logging file operation: {e}")
        finally:
            conn.close()

    def save_problem_to_history(
        self,
        file_path: str,
        file_content: str,
        problem_type: str = None,
        num_variables: int = None,
        num_constraints: int = None,
        iterations: int = None,
        execution_time_ms: float = None,
        status: str = None,
        optimal_value: float = None,
        solution_variables: str = None,
    ):
        """
        Guarda un problema resuelto en el historial para poder re-resolverlo después.

        Args:
            file_path: Ruta del archivo original
            file_content: Contenido completo del archivo
            problem_type: 'maximización' o 'minimización'
            num_variables: Número de variables del problema
            num_constraints: Número de restricciones
            iterations: Número de iteraciones necesarias
            execution_time_ms: Tiempo de ejecución en ms
            status: Estado final ('optimal', 'infeasible', etc.)
            optimal_value: Valor óptimo encontrado
            solution_variables: JSON string con la solución (ej: '{"x1": 20, "x2": 60}')
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            file_name = os.path.basename(file_path)

            cursor.execute(
                """
                INSERT INTO problem_history (
                    session_id, timestamp, file_path, file_name, file_content,
                    problem_type, num_variables, num_constraints, iterations,
                    execution_time_ms, status, optimal_value, solution_variables
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    self.session_id,
                    datetime.now().isoformat(),
                    file_path,
                    file_name,
                    file_content,
                    problem_type,
                    num_variables,
                    num_constraints,
                    iterations,
                    execution_time_ms,
                    status,
                    optimal_value,
                    solution_variables,
                ),
            )
            conn.commit()
            self.log(
                LogLevel.INFO,
                f"Problema guardado en historial: {file_name}",
            )
        except Exception as e:
            self.log(
                LogLevel.ERROR,
                f"Error guardando problema en historial: {e}",
            )
        finally:
            conn.close()

    def end_session(self):
        """Marca el fin de la sesión actual."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute(
                """
                UPDATE sessions 
                SET end_time = ? 
                WHERE session_id = ?
            """,
                (datetime.now().isoformat(), self.session_id),
            )
            conn.commit()
        except Exception as e:
            print(f"Error ending session: {e}")
        finally:
            conn.close()

    def _cleanup_old_logs(self):
        """Elimina logs más antiguos que el período de retención."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cutoff_date = (
                datetime.now() - timedelta(days=self.retention_days)
            ).isoformat()

            # Limpiar logs antiguos
            cursor.execute("DELETE FROM logs WHERE timestamp < ?", (cutoff_date,))
            cursor.execute(
                "DELETE FROM solver_events WHERE timestamp < ?", (cutoff_date,)
            )
            cursor.execute(
                "DELETE FROM file_operations WHERE timestamp < ?", (cutoff_date,)
            )
            cursor.execute(
                "DELETE FROM problem_history WHERE timestamp < ?", (cutoff_date,)
            )
            cursor.execute("DELETE FROM sessions WHERE start_time < ?", (cutoff_date,))

            deleted_count = cursor.rowcount
            conn.commit()

            if deleted_count > 0:
                self.log(
                    LogLevel.INFO,
                    f"Limpieza automática: {deleted_count} registros antiguos eliminados",
                )

        except Exception as e:
            print(f"Error during cleanup: {e}")
        finally:
            conn.close()

    def get_db_path(self) -> str:
        """Retorna la ruta de la base de datos."""
        return self.db_path

    # Métodos de conveniencia para diferentes niveles
    def debug(self, message: str, **kwargs):
        """Log nivel DEBUG."""
        self.log(LogLevel.DEBUG, message, **kwargs)

    def info(self, message: str, **kwargs):
        """Log nivel INFO."""
        self.log(LogLevel.INFO, message, **kwargs)

    def warning(self, message: str, **kwargs):
        """Log nivel WARNING."""
        self.log(LogLevel.WARNING, message, **kwargs)

    def error(self, message: str, **kwargs):
        """Log nivel ERROR."""
        self.log(LogLevel.ERROR, message, **kwargs)

    def critical(self, message: str, **kwargs):
        """Log nivel CRITICAL."""
        self.log(LogLevel.CRITICAL, message, **kwargs)


# Instancia global del logger
logger = LoggingSystem()
