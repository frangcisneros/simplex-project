# export.py
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet


def export_to_pdf(result: dict, filename: str):
    """
    Genera un PDF con el resumen del problema, el paso a paso del método simplex y la solución final.

    Args:
        result (dict): Diccionario devuelto por SimplexSolver.solve(), debe incluir 'steps'.
        filename (str): Nombre del archivo PDF a generar.
    """
    doc = SimpleDocTemplate(filename, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()

    # Título
    elements.append(Paragraph("Reporte Simplex Solver", styles['Title']))
    elements.append(Spacer(1, 12))

    # Resumen del problema
    elements.append(Paragraph("Resumen del problema:", styles['Heading2']))
    if "solution" in result:
        optimal_value = result.get("optimal_value", None)
        status = result.get("status", "")
        elements.append(Paragraph(f"Estado: {status}", styles['Normal']))
        if optimal_value is not None:
            elements.append(Paragraph(f"Valor óptimo: {optimal_value:.4f}", styles['Normal']))
        elements.append(Spacer(1, 12))

    # Mostrar pasos iterativos
    if "steps" in result:
        elements.append(Paragraph("Detalle de iteraciones:", styles['Heading2']))
        for step in result["steps"]:
            iter_num = step['iteration']
            elements.append(Paragraph(f"Iteración {iter_num}", styles['Heading3']))
            if step["entering_var"] is not None:
                elements.append(Paragraph(
                    f"Variable que entra: x{step['entering_var']+1}, "
                    f"Variable que sale: x{step['leaving_var']+1}, "
                    f"Pivote: {step['pivot']:.4f}", styles['Normal']
                ))
            else:
                elements.append(Paragraph("Estado inicial (tableau inicial)", styles['Normal']))

            # Tabla del tableau
            tableau = step['tableau']
            data = [[f"{val:.2f}" for val in row] for row in tableau]
            table = Table(data)
            table.setStyle(TableStyle([
                ('GRID', (0,0), (-1,-1), 0.5, colors.black),
                ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
            ]))
            elements.append(table)
            elements.append(Spacer(1, 12))

    # Solución final
    if "solution" in result:
        elements.append(Paragraph("Solución final:", styles['Heading2']))
        solution_data = [["Variable", "Valor"]]
        for var, val in result["solution"].items():
            solution_data.append([var, f"{val:.4f}"])
        solution_table = Table(solution_data)
        solution_table.setStyle(TableStyle([
            ('GRID', (0,0), (-1,-1), 0.5, colors.black),
            ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
        ]))
        elements.append(solution_table)

    # Generar PDF
    doc.build(elements)
    print(f"PDF generado exitosamente: {filename}")
