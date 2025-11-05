# Ejemplos de Problemas de Simplex

Esta carpeta contiene archivos de ejemplo con problemas de programación lineal en formato de texto.

## Archivos de Ejemplo

### 1. ejemplo_maximizacion.txt

Problema básico de maximización con restricciones de tipo `<=`.

**Descripción**: Maximizar una función objetivo sujeta a restricciones de recursos limitados.

### 2. ejemplo_minimizacion.txt

Problema de minimización con restricciones de tipo `>=`.

**Descripción**: Minimizar costos cumpliendo con requisitos mínimos.

### 3. ejemplo_carpinteria.txt

Problema realista de una carpintería que fabrica mesas y sillas.

**Descripción**:

- Una carpintería fabrica mesas y sillas
- Cada mesa genera $80 de ganancia
- Cada silla genera $50 de ganancia
- Hay 200 horas de trabajo disponibles
- Cada mesa requiere 4 horas, cada silla 2 horas
- Máximo 60 unidades en total
- **Objetivo**: Maximizar la ganancia

## Cómo Usar los Ejemplos

### Opción 1: Menú Contextual (Windows)

Si tienes instalado el menú contextual:

1. Haz clic derecho en cualquier archivo `.txt`
2. Selecciona **"Resolver con Simplex Solver"**
3. Observa la solución en la ventana que se abre

### Opción 2: Línea de Comandos

```bash
# Desde la raíz del proyecto
python simplex.py ejemplos/ejemplo_maximizacion.txt

# Con generación de PDF
python simplex.py ejemplos/ejemplo_carpinteria.txt --pdf resultado.pdf
```

### Opción 3: Modo Interactivo

```bash
python simplex.py --interactive
```

## Formato de Archivos

Todos los archivos siguen esta estructura:

```
MAXIMIZE                    # O MINIMIZE
c1 c2 c3 ...               # Coeficientes de función objetivo
SUBJECT TO
a11 a12 a13 ... <= b1      # Restricciones (<=, >=, o =)
a21 a22 a23 ... >= b2
a31 a32 a33 ... = b3
```

### Ejemplo Completo:

```
MAXIMIZE
3 2
SUBJECT TO
2 1 <= 18
2 3 <= 42
3 1 <= 24
```

Esto representa:

- **Función Objetivo**: Maximizar Z = 3x₁ + 2x₂
- **Restricción 1**: 2x₁ + x₂ ≤ 18
- **Restricción 2**: 2x₁ + 3x₂ ≤ 42
- **Restricción 3**: 3x₁ + x₂ ≤ 24

## Crear tus Propios Problemas

1. Crea un nuevo archivo `.txt`
2. Sigue el formato especificado arriba
3. Guárdalo en esta carpeta (opcional)
4. Resuélvelo usando cualquiera de los métodos anteriores

## Validación

El programa validará automáticamente:

- ✅ Formato correcto del archivo
- ✅ Consistencia en el número de variables
- ✅ Tipos de restricciones válidos
- ✅ Valores numéricos correctos
- ✅ Factibilidad de la solución

## 📚 Más Información

- [Documentación Principal](../README.md)
- [Guía del Menú Contextual](../docs/CONTEXT_MENU_GUIDE.md)
- [Arquitectura del Sistema](../ARQUITECTURA.md)

## 🆘 Errores Comunes

### "Error en el formato del archivo"

- Verifica que la primera línea sea `MAXIMIZE` o `MINIMIZE`
- Asegúrate de incluir `SUBJECT TO` antes de las restricciones
- Revisa que todas las restricciones tengan `<=`, `>=` o `=`

### "Número de coeficientes no coincide con variables"

- Todas las restricciones deben tener el mismo número de coeficientes que la función objetivo

### "El problema no tiene solución óptima"

- El problema puede ser no acotado o infactible
- Revisa las restricciones y la función objetivo
