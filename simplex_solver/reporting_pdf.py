"""
Módulo encargado de la generación de reportes PDF.
Gestiona la creación de carpetas, el formateo mínimo de datos y delega la generación a `export.export_to_pdf`.
"""

import os
from typing import Dict, Optional
from simplex_solver.logging_system import logger

try:
    from simplex_solver.export import export_to_pdf
except Exception as e:
    # Manejo de errores al importar el módulo export
    logger.error(f"Error al importar módulo export: {str(e)}", exception=e)
    raise


def generate_pdf(result: Dict, filename: str, reports_dir: str = "reports") -> str:
    """Genera un reporte en formato PDF basado en los resultados proporcionados.

    Args:
        result: Diccionario con la información del problema y los pasos de resolución.
        filename: Nombre del archivo de salida (solo se utiliza el nombre base).
        reports_dir: Directorio donde se guardará el PDF (se crea si no existe)

    Returns:
        str: Ruta completa del archivo PDF generado.

    Raises:
        TypeError: Si el parámetro `result` no es un diccionario válido.
        Exception: Si ocurre un error durante la generación del PDF.
    """
    logger.info(f"Generando reporte PDF: {filename} en directorio: {reports_dir}")

    if not isinstance(result, dict):
        logger.error("El resultado proporcionado no es un diccionario válido")
        raise TypeError("result debe ser un diccionario con la estructura esperada")

    # Asegurar que el directorio de salida exista
    os.makedirs(reports_dir, exist_ok=True)

    output_filename = os.path.basename(filename)
    output_path = os.path.join(reports_dir, output_filename)

    # Preparar información mínima del problema si falta la clave 'problem'
    if "problem" not in result:
        c = result.get("c")
        A = result.get("A")
        b = result.get("b")
        constraint_types = result.get("constraint_types")
        maximize = result.get("maximize")
        if c is not None and A is not None and b is not None and constraint_types is not None:

            def format_constraint(row, rhs, ctype):
                """
                Formatea una restricción en forma de cadena legible.

                Args:
                    row: Coeficientes de la restricción.
                    rhs: Término independiente de la restricción.
                    ctype: Tipo de restricción (<=, >=, =).

                Returns:
                    str: Representación formateada de la restricción.
                """
                coeffs = []
                for j, coef in enumerate(row):
                    sign = "+" if coef >= 0 and j > 0 else ""
                    coeffs.append(f"{sign}{coef}x{j+1}")
                return " ".join(coeffs) + f" {ctype} {rhs}"

            # Formatear la función objetivo
            objective_str = (
                ("Maximizar" if maximize else "Minimizar")
                + " z = "
                + " + ".join(f"{coef}x{i+1}" for i, coef in enumerate(c))
            )

            # Formatear las restricciones
            constraints_str = [
                format_constraint(row, rhs, ctype)
                for row, rhs, ctype in zip(A, b, constraint_types)
            ]

            result["problem"] = {
                "objective_str": objective_str,
                "constraints_str": constraints_str,
            }
            logger.debug("Información del problema preparada para el reporte")

    # Delegar la generación del PDF al módulo export
    try:
        export_to_pdf(result, output_path)
        logger.info(f"Reporte PDF generado exitosamente: {output_path}")
        logger.log_file_operation("generate_pdf", output_path, True)
    except Exception as e:
        logger.error(f"Error al generar PDF: {str(e)}", exception=e)
        logger.log_file_operation("generate_pdf", output_path, False, str(e))
        raise

    return output_path
