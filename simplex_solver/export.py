"""
Módulo encargado de la exportación detallada de resultados a formato PDF.
Implementa la lógica completa de generación del documento utilizando ReportLab. Incluyendo
formateo de texto, resumen del problema, tablas del método simplex, iteraciones, junto al estado
y solución final del problema. Este módulo es invocado por `reporting_pdf.py`.
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Paragraph,
    Spacer,
    KeepTogether,
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib.enums import TA_CENTER
import re

try:
    from logging_system import logger

    LOGGING_AVAILABLE = True
except ImportError:
    LOGGING_AVAILABLE = False


def export_to_pdf(result: dict, filename: str):
    """
    Genera un PDF con:
    - resumen del problema (usando result['problem'])
    - Estado y solución final
    - Detalle de iteraciones (incluyendo tablas intermedias).
    """
    if LOGGING_AVAILABLE:
        logger.info(f"Iniciando exportación a PDF: {filename}")

    try:
        doc = SimpleDocTemplate(filename, pagesize=letter)
        elements = []
        styles = getSampleStyleSheet()

        # Color y estilo para títulos
        title_color = colors.HexColor("#595959")
        custom_title_style = ParagraphStyle(
            "CustomTitle",
            parent=styles["Title"],
            textColor=title_color,
            alignment=2,  # TA_RIGHT
            rightIndent=20,  # deja 20 puntos desde el borde derecho
        )

        custom_heading2_style = ParagraphStyle(
            "CustomHeading2", parent=styles["Heading2"], textColor=title_color
        )

        # --- Configuración inicial del layout ---
        left_margin = 30
        right_margin = 30
        available_width = (
            540 - left_margin - right_margin
        )  # ancho utilizable para todo el documento(tener en cuenta márgenes)

        # Color para resaltado
        highlight_color = "#595959"

        # Título
        elements.append(Paragraph("Reporte Simplex Solver", custom_title_style))
        elements.append(Spacer(1, 12))

        # --- Resumen del problema ---
        if "problem" in result:
            problem = result["problem"]
            elements.append(Paragraph("Resumen del problema", custom_heading2_style))
            elements.append(Spacer(1, 4))

            # --- Función auxiliar para agregar espacio entre coeficiente y variable ---
            def add_space(expr: str) -> str:
                # Agregar espacio antes de cada variable
                expr = re.sub(r"(\d)(x\d+)", r"\1 \2", expr)
                # Espaciado alrededor de + y -
                expr = re.sub(r"\+", " + ", expr)
                expr = re.sub(r"(?<!^)-", " - ", expr)  # evita espacio al inicio si es negativo
                # Quitar posibles espacios dobles
                expr = re.sub(r"\s+", " ", expr)
                return expr.strip()

            # --- Construir contenido del resumen ---
            problem_content = []

            # Función objetivo
            objective_str = result["problem"]["objective_str"]
            if objective_str.startswith("Maximizar"):
                expr = objective_str[len("Maximizar ") :]
                expr = add_space(expr)
                problem_content.append(
                    Paragraph(
                        f"<b>Maximizar:</b> <b><font color='{highlight_color}'>{expr}</font></b>",
                        styles["Normal"],
                    )
                )
            elif objective_str.startswith("Minimizar"):
                expr = objective_str[len("Minimizar ") :]
                expr = add_space(expr)
                problem_content.append(
                    Paragraph(
                        f"<b>Minimizar:</b> <b><font color='{highlight_color}'>{expr}</font></b>",
                        styles["Normal"],
                    )
                )
            else:
                expr = add_space(objective_str)
                problem_content.append(
                    Paragraph(
                        f"<font color='{highlight_color}'>{objective_str}</font>",
                        styles["Normal"],
                    )
                )

            problem_content.append(Spacer(1, 4))

            # Restricciones
            problem_content.append(Paragraph("<b>Sujeto a:</b>", styles["Normal"]))
            problem_content.append(Spacer(1, 4))
            for constr in problem["constraints_str"]:
                constr_fmt = add_space(constr)
                problem_content.append(
                    Paragraph(
                        f"<b><font color='{highlight_color}'>{constr_fmt}</font></b>",
                        styles["Normal"],
                    )
                )

            # --- Crear la tabla de una celda ---
            problem_table = Table(
                [[problem_content]], colWidths=[available_width * 0.95]
            )  # centrado dentro del ancho útil
            problem_table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, -1), colors.lavender),  # fondo
                        ("BOX", (0, 0), (-1, -1), 1, colors.grey),  # borde
                        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                        ("ALIGN", (0, 0), (-1, -1), "CENTER"),  # centra contenido
                        ("LEFTPADDING", (0, 0), (-1, -1), 6),
                        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                        ("TOPPADDING", (0, 0), (-1, -1), 6),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                    ]
                )
            )

            elements.append(problem_table)
            elements.append(Spacer(1, 8))

        # --- Resumen de la solución ---
        elements.append(Paragraph("Resumen de la solución", custom_heading2_style))
        elements.append(Spacer(1, 4))

        status = result.get("status", "")
        solution_content = []  # lista para los elementos del recuadro

        if status == "optimal":
            optimal_value = result.get("optimal_value", None)
            solution_content.append(
                Paragraph(
                    f"<b>Valor óptimo:</b> <b><font color='{highlight_color}'>z={optimal_value:.2f}</font></b>",
                    styles["Normal"],
                )
            )
            solution_content.append(Spacer(1, 4))  # Espaciado extra antes de las variables

            solution = result.get("solution", {})
            if solution:
                vars_str = ", ".join(
                    f"<b><font color='{highlight_color}'>{var}={val:.2f}</font></b>"
                    for var, val in solution.items()
                )
                solution_content.append(Paragraph(f"<b>Para</b> {vars_str}", styles["Normal"]))

            # Mostrar soluciones alternativas si existen
            if result.get("has_alternative_solutions", False):
                num_alt = result.get("num_alternative_solutions", 0)
                solution_content.append(Spacer(1, 6))
                solution_content.append(
                    Paragraph(
                        f"<b>⚠️ Soluciones alternativas:</b> Se encontraron {num_alt} soluciones alternativas óptimas",
                        styles["Normal"],
                    )
                )

                # Mostrar todas las soluciones alternativas
                if "solutions" in result and len(result["solutions"]) > 1:
                    for idx, alt_solution in enumerate(result["solutions"][1:], start=2):
                        solution_content.append(Spacer(1, 4))
                        alt_vars_str = ", ".join(
                            f"<b><font color='{highlight_color}'>{var}={val:.2f}</font></b>"
                            for var, val in alt_solution.items()
                        )
                        solution_content.append(
                            Paragraph(
                                f"<b>Solución alternativa #{idx - 1}:</b> {alt_vars_str}",
                                styles["Normal"],
                            )
                        )

        elif status == "unbounded":
            solution_content.append(Paragraph("Problema no acotado", styles["Heading3"]))

        else:
            solution_content.append(
                Paragraph(f"Error: {result.get('message','')}", styles["Heading3"])
            )

        # Crear tabla de 1 celda si hay contenido
        if solution_content:
            solution_table = Table(
                [[solution_content]], colWidths=[available_width * 0.95]
            )  # # mismo ancho que el bloque del problema
            solution_table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, -1), "#DDFBDF"),  # fondo
                        ("BOX", (0, 0), (-1, -1), 1, colors.grey),  # borde gris
                        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                        ("ALIGN", (0, 0), (-1, -1), "CENTER"),  # centra contenido
                        ("LEFTPADDING", (0, 0), (-1, -1), 6),
                        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                        ("TOPPADDING", (0, 0), (-1, -1), 6),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                    ]
                )
            )

            elements.append(solution_table)

        elements.append(Spacer(1, 8))

        # --- Análisis de Sensibilidad ---
        if (
            status == "optimal"
            and "sensitivity_analysis" in result
            and result["sensitivity_analysis"] is not None
        ):
            analysis = result["sensitivity_analysis"]

            elements.append(Paragraph("Análisis de Sensibilidad", custom_heading2_style))
            elements.append(Spacer(1, 4))

            sensitivity_content = []

            # Precios Sombra
            if "shadow_prices" in analysis:
                sensitivity_content.append(
                    Paragraph("<b>Precios Sombra (Valores Duales):</b>", styles["Normal"])
                )
                sensitivity_content.append(Spacer(1, 2))

                shadow_prices = analysis["shadow_prices"]
                for constraint, price in sorted(shadow_prices.items()):
                    sensitivity_content.append(
                        Paragraph(
                            f"<b><font color='{highlight_color}'>{constraint}:</font></b> {price:.6f}",
                            styles["Normal"],
                        )
                    )
                sensitivity_content.append(Spacer(1, 6))

            # Rangos de Optimalidad
            if "optimality_ranges" in analysis:
                sensitivity_content.append(
                    Paragraph("<b>Rangos de Optimalidad:</b>", styles["Normal"])
                )
                sensitivity_content.append(
                    Paragraph(
                        "<i>(Rangos donde los coeficientes de la F.O. mantienen la solución actual)</i>",
                        styles["Normal"],
                    )
                )
                sensitivity_content.append(Spacer(1, 2))

                opt_ranges = analysis["optimality_ranges"]
                for var, (lower, upper) in sorted(opt_ranges.items()):
                    if lower == float("-inf"):
                        lower_str = "-∞"
                    else:
                        lower_str = f"{lower:.6f}"
                    if upper == float("inf"):
                        upper_str = "+∞"
                    else:
                        upper_str = f"{upper:.6f}"

                    sensitivity_content.append(
                        Paragraph(
                            f"<b><font color='{highlight_color}'>{var}:</font></b> [{lower_str}, {upper_str}]",
                            styles["Normal"],
                        )
                    )
                sensitivity_content.append(Spacer(1, 6))

            # Rangos de Factibilidad
            if "feasibility_ranges" in analysis:
                sensitivity_content.append(
                    Paragraph("<b>Rangos de Factibilidad:</b>", styles["Normal"])
                )
                sensitivity_content.append(
                    Paragraph(
                        "<i>(Rangos donde los valores RHS mantienen la misma base óptima)</i>",
                        styles["Normal"],
                    )
                )
                sensitivity_content.append(Spacer(1, 2))

                feas_ranges = analysis["feasibility_ranges"]
                for constraint, (lower, upper) in sorted(feas_ranges.items()):
                    if lower == float("-inf"):
                        lower_str = "-∞"
                    else:
                        lower_str = f"{lower:.6f}"
                    if upper == float("inf"):
                        upper_str = "+∞"
                    else:
                        upper_str = f"{upper:.6f}"

                    sensitivity_content.append(
                        Paragraph(
                            f"<b><font color='{highlight_color}'>{constraint}:</font></b> [{lower_str}, {upper_str}]",
                            styles["Normal"],
                        )
                    )

            # Crear tabla de análisis de sensibilidad
            if sensitivity_content:
                sensitivity_table = Table(
                    [[sensitivity_content]], colWidths=[available_width * 0.95]
                )
                sensitivity_table.setStyle(
                    TableStyle(
                        [
                            ("BACKGROUND", (0, 0), (-1, -1), colors.lightyellow),
                            ("BOX", (0, 0), (-1, -1), 1, colors.grey),
                            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                            ("LEFTPADDING", (0, 0), (-1, -1), 6),
                            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                            ("TOPPADDING", (0, 0), (-1, -1), 6),
                            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                        ]
                    )
                )
                elements.append(sensitivity_table)
                elements.append(Spacer(1, 8))

        # Función auxiliar para formatear nombres de variables
        def format_var_name(var_idx, n_original_vars):
            if isinstance(var_idx, int):
                if var_idx < n_original_vars:
                    return f"x{var_idx+1}"
                else:
                    holg_idx = var_idx - n_original_vars + 1
                    return f"s{holg_idx}"
            else:
                return str(var_idx)

        # Mostrar pasos iterativos (Detalle de iteraciones)
        if "steps" in result:

            elements.append(Paragraph("Detalle de iteraciones", custom_heading2_style))
            elements.append(Spacer(1, 0))

            steps = result["steps"]
            n_original_vars = result.get("n_original_vars", 0)  # Número de variables originales

            for idx, step in enumerate(steps):
                iter_num = step["iteration"]

                # Detectar título de la iteración
                if step["entering_var"] is None:
                    iter_title = f"Iteración {iter_num} – Estado inicial (tableau inicial)"
                elif idx == len(steps) - 1:
                    iter_title = f"Iteración {iter_num} – Estado final (tableau final)"
                else:
                    iter_title = f"Iteración {iter_num}"

                # Bloque de la iteración
                iteration_block = []

                # --- Título y subtítulo (a la izquierda) ---
                iteration_block.append(Paragraph(iter_title, styles["Heading3"]))
                if step["entering_var"] is not None:
                    entering_name = format_var_name(step["entering_var"], n_original_vars)
                    leaving_name = format_var_name(step["leaving_var"], n_original_vars)
                    iteration_block.append(
                        Paragraph(
                            f"Variable que entra: {entering_name}, Variable que sale: {leaving_name}",
                            styles["Normal"],
                        )
                    )

                # 3- Espacio antes de la tabla
                iteration_block.append(Spacer(1, 10))

                # 4- Construcción de la tabla
                tableau_to_show = step["tableau"]
                m, n_plus = tableau_to_show.shape
                n = n_plus - 1  # columnas de variables (RHS no incluida)

                # Cabecera: VB + nombres (usando format_var_name para consistencia) + b
                header = ["VB"] + [format_var_name(i, n_original_vars) for i in range(n)] + ["b"]
                data = [header]

                # Variables básicas de la iteración
                basic_vars = step.get("basic_vars", [])
                # Filas
                for row_idx, row in enumerate(tableau_to_show):
                    vb_name = (
                        format_var_name(basic_vars[row_idx], n_original_vars)
                        if row_idx < len(basic_vars)
                        else "z"
                    )
                    data_row = [vb_name] + [f"{val:.2f}" for val in row]
                    data.append(data_row)

                table = Table(data, repeatRows=1)

                # Estilos de la tabla
                styles_list = [
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
                    ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),  # cabecera
                    ("ALIGN", (0, 0), (-1, 0), "CENTER"),  # centra fila superior
                    ("ALIGN", (0, 1), (0, -1), "CENTER"),  # centra columna VB
                    ("ALIGN", (1, 1), (-1, -1), "CENTER"),  # centra resto de celdas
                    (
                        "LINEABOVE",
                        (0, m),
                        (-1, m),
                        1,
                        colors.black,
                    ),  # línea superior de la última fila
                ]

                # Resaltar pivote si existe
                pivot_info = step.get("pivot_coords_next")
                if pivot_info:
                    entering_col = pivot_info["entering_col"] + 1  # +1 por columna VB
                    leaving_row = pivot_info["leaving_row"] + 1  # +1 por fila header
                    styles_list += [
                        (
                            "BACKGROUND",
                            (entering_col, 1),
                            (entering_col, m),
                            colors.lavender,
                        ),  # Columna pivote
                        (
                            "BACKGROUND",
                            (1, leaving_row),
                            (-1, leaving_row),
                            colors.lavender,
                        ),  # Fila pivote
                        (
                            "BACKGROUND",
                            (entering_col, leaving_row),
                            (entering_col, leaving_row),
                            colors.lightblue,
                        ),  # Celda pivote
                        (
                            "TEXTCOLOR",
                            (entering_col, leaving_row),
                            (entering_col, leaving_row),
                            colors.darkblue,
                        ),
                        ("BACKGROUND", (0, 1), (0, m - 1), colors.whitesmoke),  # VB
                        (
                            "BACKGROUND",
                            (0, m),
                            (0, m),
                            colors.lightgrey,
                        ),  # Última fila VB
                    ]

                # Última iteración: resaltar z, VB y RHS
                if idx == len(steps) - 1:
                    styles_list += [
                        ("BACKGROUND", (0, m), (0, m), colors.lightgrey),  # celda 'z'
                        ("BACKGROUND", (-1, m), (-1, m), colors.lightgrey),  # valor z
                        ("TEXTCOLOR", (0, m), (0, m), colors.black),
                        ("TEXTCOLOR", (-1, m), (-1, m), colors.black),
                        ("BACKGROUND", (0, 1), (0, m - 1), colors.whitesmoke),  # VB
                        ("BACKGROUND", (-1, 1), (-1, m - 1), colors.whitesmoke),  # RHS
                    ]

                    # Resaltar variables básicas de decisión (no de holgura)
                    for row_idx, vb in enumerate(basic_vars):
                        if isinstance(vb, int) and vb < n_original_vars:  # Filtra VB reales
                            styles_list.append(
                                (
                                    "BACKGROUND",
                                    (0, row_idx + 1),
                                    (0, row_idx + 1),
                                    colors.lavender,
                                )
                            )  # VB
                            styles_list.append(
                                (
                                    "BACKGROUND",
                                    (-1, row_idx + 1),
                                    (-1, row_idx + 1),
                                    colors.lavender,
                                )
                            )  # RHS

                table.setStyle(TableStyle(styles_list))
                # Centrar horizontalmente la tabla dentro de su columna
                table.hAlign = "CENTER"

                # Flecha con número de iteración
                arrow_text = f"{iter_num} ➤"
                arrow_para = Paragraph(
                    arrow_text,
                    ParagraphStyle(
                        name="ArrowStyle",
                        fontSize=14,
                        alignment=TA_CENTER,
                        textColor=colors.darkblue,
                    ),
                )
                arrow_para = Paragraph(
                    f"<font size=14>{iter_num}</font> <font size=14>➤</font>",
                    ParagraphStyle(
                        name="ArrowStyle", alignment=TA_CENTER, textColor=colors.HexColor("#7F7F7F")
                    ),
                )

                # Ancho de columnas flecha y tabla
                arrow_col_frac = 0.25  # % para la flecha
                arrow_col_width = available_width * arrow_col_frac
                table_col_width = available_width * (1 - arrow_col_frac)

                # Encapsular flecha y bloque iteración en tabla de 2 columnas
                wrapper_table = Table(
                    [[arrow_para, table]],  # tabla a la derecha dentro de la mini tabla
                    colWidths=[arrow_col_width, table_col_width],
                    hAlign="LEFT",  # alineación desde el margen izquierdo
                )
                wrapper_table.setStyle(
                    TableStyle(
                        [
                            (
                                "VALIGN",
                                (0, 0),
                                (0, -1),
                                "MIDDLE",
                            ),  # Columna 0: flecha centrada verticalmente
                            (
                                "VALIGN",
                                (1, 0),
                                (1, -1),
                                "TOP",
                            ),  # Columna 1: tabla mantiene alineación superior
                            ("LEFTPADDING", (0, 0), (0, 0), 0),
                            ("RIGHTPADDING", (0, 0), (0, 0), 0),
                        ]
                    )
                )

                # Agregar wrapper_table al bloque de iteración y mantener todo junto
                iteration_block.append(wrapper_table)
                iteration_block.append(Spacer(1, 6))

                elements.append(KeepTogether(iteration_block))

            # Generar PDF
            doc.build(elements)
            print(f"PDF generado exitosamente: {filename}")
            if LOGGING_AVAILABLE:
                logger.info(f"PDF exportado exitosamente: {filename}")
                logger.log_file_operation("export_pdf", filename, True)

    except Exception as e:
        if LOGGING_AVAILABLE:
            logger.error(f"Error al exportar PDF '{filename}': {str(e)}", exception=e)
            logger.log_file_operation("export_pdf", filename, False, str(e))
        raise
