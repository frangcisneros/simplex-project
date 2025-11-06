"""
Módulo para procesamiento de archivos de entrada.
Lee y parsea archivos con problemas de programación lineal.
"""

import sys
import os
from typing import List, Tuple, Optional

# Agregar import del validador
from simplex_solver.input_validator import InputValidator
from simplex_solver.logging_system import logger
from simplex_solver.config import FileConfig


class FileParser:
    """Parser para archivos de problemas de programación lineal."""

    @staticmethod
    def parse_file(
        filename: str,
    ) -> Tuple[List[float], List[List[float]], List[float], List[str], bool]:
        """
        Lee y parsea un archivo con el problema de programación lineal.
        """
        logger.info(f"Iniciando parseo de archivo: {filename}")
        try:
            if not os.path.exists(filename):
                logger.error(f"Archivo no encontrado: {filename}")
                raise FileNotFoundError(f"No se pudo encontrar el archivo {filename}")

            file_size = os.path.getsize(filename)
            logger.debug(f"Tamaño del archivo: {file_size} bytes")

            with open(filename, "r", encoding=FileConfig.DEFAULT_ENCODING) as f:
                lines = [line.strip() for line in f.readlines() if line.strip()]

            logger.log_file_operation("read", filename, True)

            if not lines:
                logger.error("Archivo vacío")
                raise ValueError("Archivo vacío")

            logger.debug(f"Líneas leídas: {len(lines)}")
            maximize = FileParser._parse_optimization_type(lines[0])
            logger.debug(f"Tipo de optimización: {'Maximización' if maximize else 'Minimización'}")

            c = FileParser._parse_objective_function(lines[1])
            logger.debug(f"Función objetivo parseada: {len(c)} variables")

            A, b, constraint_types = FileParser._parse_constraints(lines, len(c))
            logger.debug(f"Restricciones parseadas: {len(A)} restricciones")

            # Validar el problema parseado
            is_valid, error_msg = InputValidator.validate_problem(
                c, A, b, constraint_types, maximize
            )
            if not is_valid:
                logger.error(f"Problema en archivo inválido: {error_msg}")
                raise ValueError(f"Problema en archivo inválido: {error_msg}")

            logger.info(f"Archivo parseado exitosamente: {len(c)} vars, {len(A)} restricciones")
            return c, A, b, constraint_types, maximize

        except FileNotFoundError as e:
            logger.log_file_operation("read", filename, False, str(e))
            raise
        except Exception as e:
            logger.error(f"Error al parsear archivo '{filename}': {str(e)}", exception=e)
            logger.log_file_operation("read", filename, False, str(e))
            raise ValueError(f"Error al leer el archivo: {e}")

    @staticmethod
    def _parse_optimization_type(line: str) -> bool:
        """Parsea el tipo de optimización (MAXIMIZE/MINIMIZE)."""
        line_upper = line.upper()

        if line_upper in FileConfig.MAXIMIZE_KEYWORDS:
            return True
        elif line_upper in FileConfig.MINIMIZE_KEYWORDS:
            return False
        else:
            raise ValueError(
                f"Primera línea debe ser una palabra clave de optimización válida: "
                f"{FileConfig.MAXIMIZE_KEYWORDS} o {FileConfig.MINIMIZE_KEYWORDS}"
            )

    @staticmethod
    def _parse_objective_function(line: str) -> List[float]:
        """Parsea los coeficientes de la función objetivo."""
        try:
            return list(map(float, line.split()))
        except ValueError:
            raise ValueError("Coeficientes de función objetivo inválidos")

    @staticmethod
    def _parse_constraints(
        lines: List[str], num_vars: int
    ) -> Tuple[List[List[float]], List[float], List[str]]:
        """Parsea las restricciones del problema."""
        # Buscar "SUBJECT TO"
        subject_to_idx = -1
        for i, line in enumerate(lines):
            if FileConfig.SUBJECT_TO_KEYWORD in line.upper():
                subject_to_idx = i
                break

        if subject_to_idx == -1:
            raise ValueError(f"No se encontró '{FileConfig.SUBJECT_TO_KEYWORD}'")

        A = []
        b = []
        constraint_types = []

        for line in lines[subject_to_idx + 1 :]:
            line = line.strip()
            if not line:
                continue

            # Detectar tipo de restricción
            if "<=" in line:
                parts = line.split("<=")
                const_type = "<="
            elif ">=" in line:
                parts = line.split(">=")
                const_type = ">="
            elif "=" in line:
                parts = line.split("=")
                const_type = "="
            else:
                print(f"Advertencia: línea ignorada (formato no reconocido): {line}")
                continue

            if len(parts) != 2:
                print(f"Advertencia: línea ignorada (formato inválido): {line}")
                continue

            try:
                coeffs = list(map(float, parts[0].split()))
                rhs = float(parts[1])

                if len(coeffs) != num_vars:
                    raise ValueError(
                        f"Número de coeficientes ({len(coeffs)}) no coincide con variables ({num_vars})"
                    )

                A.append(coeffs)
                b.append(rhs)
                constraint_types.append(const_type)

            except ValueError as e:
                print(f"Advertencia: línea ignorada (error en números): {line} - {e}")
                continue

        if not A:
            raise ValueError("Debe haber al menos una restricción válida")

        return A, b, constraint_types
