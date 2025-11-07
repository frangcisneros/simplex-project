"""
Archivo de configuración central para Simplex Solver.
Contiene todas las constantes y configuraciones de la aplicación.
"""

import os
from typing import Final


# ===== CONFIGURACIÓN DEL ALGORITMO =====


class AlgorithmConfig:
    """Configuración del algoritmo Simplex."""

    # Número máximo de iteraciones permitidas
    MAX_ITERATIONS: Final[int] = 100

    # Iteraciones de seguridad antes de advertir sobre posible loop infinito
    SAFETY_ITERATION_LIMIT: Final[int] = 50

    # Tolerancia numérica para comparaciones de punto flotante
    NUMERICAL_TOLERANCE: Final[float] = 1e-10

    # Tolerancia para detectar pivotes casi nulos
    PIVOT_TOLERANCE: Final[float] = 1e-10


# ===== CONFIGURACIÓN DE VALIDACIÓN =====


class ValidationConfig:
    """Configuración para validación de problemas."""

    # Número mínimo de variables permitidas
    MIN_VARIABLES: Final[int] = 1

    # Número máximo de variables (límite práctico)
    MAX_VARIABLES: Final[int] = 1000

    # Número mínimo de restricciones
    MIN_CONSTRAINTS: Final[int] = 1

    # Número máximo de restricciones (límite práctico)
    MAX_CONSTRAINTS: Final[int] = 1000

    # Tolerancia para validación de factibilidad de soluciones
    FEASIBILITY_TOLERANCE: Final[float] = 1e-6


# ===== CONFIGURACIÓN DE ARCHIVOS =====


class FileConfig:
    """Configuración relacionada con archivos."""

    # Codificación por defecto para archivos
    DEFAULT_ENCODING: Final[str] = "utf-8"

    # Palabras clave reconocidas para maximización
    MAXIMIZE_KEYWORDS: Final[tuple] = ("MAXIMIZE", "MAXIMIZAR", "MAX")

    # Palabras clave reconocidas para minimización
    MINIMIZE_KEYWORDS: Final[tuple] = ("MINIMIZE", "MINIMIZAR", "MIN")

    # Palabra clave para inicio de restricciones
    SUBJECT_TO_KEYWORD: Final[str] = "SUBJECT TO"

    # Tipos de restricción válidos
    VALID_CONSTRAINT_TYPES: Final[tuple] = ("<=", ">=", "=")


# ===== CONFIGURACIÓN DE LOGGING =====


class LoggingConfig:
    """Configuración del sistema de logging."""

    # Días de retención de logs
    RETENTION_DAYS: Final[int] = 180  # 6 meses

    # Nombre de la base de datos de logs
    LOG_DATABASE_NAME: Final[str] = "simplex_logs.db"

    # Niveles de verbosidad
    class VerbosityLevel:
        SILENT: Final[int] = 0
        BASIC: Final[int] = 1
        DETAILED: Final[int] = 2


# ===== CONFIGURACIÓN DE REPORTES =====


class ReportConfig:
    """Configuración para generación de reportes."""

    # Carpeta por defecto para reportes PDF
    DEFAULT_REPORTS_DIR: Final[str] = os.path.join(os.path.expanduser("~"), "Desktop")

    # Tamaño de página para PDFs
    PAGE_SIZE: Final[str] = "letter"

    # Máximo de iteraciones a incluir en reportes detallados
    MAX_ITERATIONS_IN_REPORT: Final[int] = 50


# ===== CONFIGURACIÓN DE HISTORIAL =====


class HistoryConfig:
    """Configuración del historial de problemas."""

    # Número máximo de problemas a mostrar por defecto
    DEFAULT_DISPLAY_LIMIT: Final[int] = 50

    # Prefijo para archivos temporales del historial
    TEMP_FILE_PREFIX: Final[str] = "simplex_history_"


# ===== MENSAJES DE USUARIO =====


class Messages:
    """Mensajes estándar mostrados al usuario."""

    # Mensajes de inicio
    APP_TITLE: Final[str] = "=== SIMPLEX SOLVER ==="
    INTERACTIVE_MODE_TITLE: Final[str] = "=== SIMPLEX SOLVER - Modo Interactivo ==="

    # Mensajes de validación
    VALIDATING: Final[str] = "✓ Validando problema..."
    VALIDATION_SUCCESS: Final[str] = "✓ Problema validado correctamente"
    VALIDATION_FAILED: Final[str] = "❌ ERROR: {error}"

    # Mensajes de resolución
    SOLVING: Final[str] = "⚙️  Resolviendo problema..."
    SOLVE_SUCCESS: Final[str] = "✓ Resolución completada"

    # Mensajes de solución
    VALIDATING_SOLUTION: Final[str] = "✓ Validando factibilidad de la solución..."
    SOLUTION_FEASIBLE: Final[str] = "✓ Solución validada como factible"
    SOLUTION_NOT_FEASIBLE: Final[str] = "⚠️  ADVERTENCIA: La solución podría no ser factible:"

    # Mensajes de interrupción
    USER_INTERRUPTED: Final[str] = "\n\n⚠️  Ejecución interrumpida por el usuario"
    CRITICAL_ERROR: Final[str] = "\n❌ ERROR: {error}"

    # Mensajes de reportes
    PDF_GENERATED: Final[str] = "\n📄 Reporte PDF generado: {path}"


# ===== CONFIGURACIÓN DE PATHS =====


class PathConfig:
    """Configuración de rutas de la aplicación."""

    # Nombre del directorio de logs (relativo)
    LOGS_DIR: Final[str] = "logs"

    # Nombre del directorio de la aplicación en AppData (Windows)
    APP_DATA_DIR: Final[str] = "SimplexSolver"


# ===== VALORES POR DEFECTO =====


class Defaults:
    """Valores por defecto de la aplicación."""

    # Nombre de archivo para modo interactivo
    INTERACTIVE_FILENAME: Final[str] = "interactive_input"

    # Contenido de archivo vacío
    EMPTY_FILE_CONTENT: Final[str] = ""

    # Tipo de problema por defecto
    DEFAULT_MAXIMIZE: Final[bool] = True


# Exportar todas las clases de configuración
__all__ = [
    "AlgorithmConfig",
    "ValidationConfig",
    "FileConfig",
    "LoggingConfig",
    "ReportConfig",
    "HistoryConfig",
    "Messages",
    "PathConfig",
    "Defaults",
]
