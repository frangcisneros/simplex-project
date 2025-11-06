# Tarjeta CRC: PDFExporter (export_to_pdf)

### Función: export_to_pdf

**Responsabilidades:**

- Generar documentos PDF profesionales con los resultados del Simplex
- Formatear título y encabezados del documento
- Crear sección de resumen del problema (función objetivo y restricciones)
- Generar tabla visual con recuadro para el problema
- Formatear expresiones matemáticas con espaciado adecuado
- Crear sección de resumen de la solución con valor óptimo
- Mostrar variables de decisión con sus valores
- Generar detalle de iteraciones del algoritmo Simplex
- Crear tablas del tableau para cada iteración
- Resaltar elementos pivote (celda, fila, columna)
- Mostrar variables básicas y no básicas
- Formatear nombres de variables (originales vs holgura/artificiales)
- Diferenciar estado inicial, iteraciones intermedias y estado final
- Agregar flechas numeradas para indicar progresión de iteraciones
- Aplicar estilos visuales (colores, bordes, alineación)
- Mantener elementos juntos para evitar fragmentación
- Registrar operaciones de exportación PDF

**Colaboradores:**

- `reportlab` - Generación de documentos PDF
- `LoggingSystem` - Registro de operaciones (si disponible)

**Ubicación:** `simplex_solver/export.py`

**Tipo:** Exportador/Generador de reportes (Report Generator)
