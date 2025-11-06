# Tarjeta CRC: FileParser

### Clase: FileParser

**Responsabilidades:**

- Leer y parsear archivos de problemas de programación lineal
- Verificar existencia del archivo
- Parsear tipo de optimización (MAXIMIZE/MINIMIZE)
- Extraer coeficientes de la función objetivo
- Buscar sección "SUBJECT TO" en el archivo
- Parsear restricciones con sus operadores (<=, >=, =)
- Validar formato de cada línea de restricción
- Manejar líneas con formato inválido (advertencias)
- Validar consistencia dimensional entre restricciones
- Validar el problema completo antes de retornarlo
- Registrar operaciones de lectura de archivos
- Manejar errores de encoding y formato

**Colaboradores:**

- `InputValidator` - Valida problemas parseados
- `LoggingSystem` - Registra operaciones de archivo
- Sistema de archivos

**Ubicación:** `simplex_solver/file_parser.py`

**Tipo:** Parser (File Parser)
