"""
Módulo encargado de la generación de reportes PDF.
Encapsula la lógica de creación de carpetas, formateo mínimo y delega a `export.export_to_pdf`.
"""

import os
from typing import Dict, Optional
from simplex_solver.logging_system import logger

try:
    from simplex_solver.export import export_to_pdf
except Exception as e:
    # Si export.py no existe o falla la importación, lanzamos una excepción clara
    logger.error(f"Error al importar módulo export: {str(e)}", exception=e)
    raise


def generate_pdf(result: Dict, filename: str, reports_dir: str = "reports") -> str:
    """Genera un PDF para `result` y lo guarda en `reports_dir/filename`.

    Args:
        result: diccionario con la información del problema y pasos (la misma estructura que espera export_to_pdf)
        filename: nombre de archivo de salida (puede incluir subruta; solo se usa el basename)
        reports_dir: carpeta donde se guardará el PDF (se crea si no existe)

    Returns:
        La ruta completa del archivo generado.
    """
    logger.info(f"Generando reporte PDF: {filename} en directorio: {reports_dir}")

    if not isinstance(result, dict):
        logger.error("Resultado no es un diccionario válido")
        raise TypeError("result debe ser un diccionario con la estructura esperada")

    # Asegurar carpeta de salida
    os.makedirs(reports_dir, exist_ok=True)

    output_filename = os.path.basename(filename)
    output_path = os.path.join(reports_dir, output_filename)

    # Si el result no tuviera la clave 'problem', no forzamos su creación aquí; se asume que el llamante
    # (main) prepara 'result' con la información necesaria. Sin embargo, por robustez, hacemos un intento
    # minimal para evitar errores en export_to_pdf.
    if "problem" not in result:
        # Intentamos crear un resumen mínimo si existen claves comunes
        c = result.get("c")
        A = result.get("A")
        b = result.get("b")
        constraint_types = result.get("constraint_types")
        maximize = result.get("maximize")
        if c is not None and A is not None and b is not None and constraint_types is not None:

            def format_constraint(row, rhs, ctype):
                coeffs = []
                for j, coef in enumerate(row):
                    sign = "+" if coef >= 0 and j > 0 else ""
                    coeffs.append(f"{sign}{coef}x{j+1}")
                return " ".join(coeffs) + f" {ctype} {rhs}"

            objective_str = (
                ("Maximizar" if maximize else "Minimizar")
                + " z = "
                + " + ".join(f"{coef}x{i+1}" for i, coef in enumerate(c))
            )

            constraints_str = [
                format_constraint(row, rhs, ctype)
                for row, rhs, ctype in zip(A, b, constraint_types)
            ]

            result["problem"] = {
                "objective_str": objective_str,
                "constraints_str": constraints_str,
            }
            logger.debug("Información del problema preparada para el reporte")

    # Delegar la generación del PDF al módulo export (reportlab)
    try:
        export_to_pdf(result, output_path)
        logger.info(f"Reporte PDF generado exitosamente: {output_path}")
        logger.log_file_operation("generate_pdf", output_path, True)
    except Exception as e:
        logger.error(f"Error al generar PDF: {str(e)}", exception=e)
        logger.log_file_operation("generate_pdf", output_path, False, str(e))
        raise

    return output_path
