# Ejemplos de Problemas de Simplex

Esta carpeta contiene archivos de ejemplo con problemas de programación lineal en formato de texto.

## Archivos de Ejemplo

### 1. ejemplo_maximizacion.txt

Problema básico de maximización con restricciones de tipo `<=`.

**Descripción**: Maximizar una función objetivo sujeta a restricciones de recursos limitados.

**Estado esperado**: Solución óptima

### 2. ejemplo_minimizacion.txt

Problema de minimización con restricciones de tipo `>=`.

**Descripción**: Minimizar costos cumpliendo con requisitos mínimos.

**Estado esperado**: Solución óptima

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

**Estado esperado**: Solución óptima

### 4. max_4tablas.txt

Problema complejo con múltiples restricciones.

**Estado esperado**: Solución óptima

### 5. ejemplo_infactible.txt

Problema sin solución factible (restricciones contradictorias).

**Descripción**: Las restricciones se contradicen entre sí, haciendo imposible encontrar una solución que las satisfaga todas.

**Estado esperado**: Infactible (no existe solución)

**Ejemplo de output:**

```
El problema es infactible (no existe solución que satisfaga todas las restricciones)
```

### 6. ejemplo_no_acotado.txt

Problema no acotado (la función objetivo puede crecer infinitamente).

**Descripción**: No hay restricciones suficientes que limiten el crecimiento de la función objetivo.

**Estado esperado**: No acotado (unbounded)

**Ejemplo de output:**

```
El problema es no acotado (la solución puede crecer infinitamente)
```

### 7. ejemplo_dos_fases.txt

**Problema que requiere el Método de Dos Fases** (restricciones mixtas: `>=`, `=`, `<=`).

**Descripción**: Problema de minimización con:

- 2 restricciones de tipo `>=` (requieren variables de exceso y artificiales)
- 1 restricción de tipo `=` (requiere variable artificial)
- El método de Dos Fases encuentra una solución básica factible inicial (Fase 1) y luego resuelve el problema original (Fase 2)

**Tipo**: Minimización

**Variables**: 3 (x₁, x₂, x₃)

**Restricciones**:

- 2x₁ + x₂ + x₃ ≥ 4 (requiere variable de exceso s₁ y artificial a₁)
- x₁ + 2x₂ + x₃ ≥ 6 (requiere variable de exceso s₂ y artificial a₂)
- x₁ + x₂ + 2x₃ = 5 (requiere variable artificial a₃)

**Estado esperado**: Solución óptima (factible)

**Método utilizado**: Método de Dos Fases

- **Fase 1**: Minimiza w = a₁ + a₂ + a₃ para encontrar una solución básica factible inicial
- **Fase 2**: Si w\* = 0, resuelve el problema original minimizando z = x₁ + 2x₂ + 3x₃

**Documentación técnica**: Ver `docs/METODO_DOS_FASES.md` para detalles completos del algoritmo.

**Ejemplo de output** (con verbosity 2):

```
=== FASE 1: Encontrando solución básica factible ===
...
Fase 1 completada. w* = 0.0000 (problema factible)
=== FASE 2: Resolviendo problema original ===
...
Solución óptima encontrada
```

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

# Con análisis de sensibilidad
python simplex.py ejemplos/ejemplo_carpinteria.txt --sensitivity

# Combinar opciones
python simplex.py ejemplos/ejemplo_carpinteria.txt -s --pdf reporte.pdf
```

### Opción 4: Análisis de Sensibilidad

Para problemas con solución óptima, puedes obtener análisis de sensibilidad:

```bash
python simplex.py ejemplos/ejemplo_carpinteria.txt --sensitivity
```

El análisis de sensibilidad proporciona:

**1. Precios Sombra**: Valor marginal de cada recurso

```
restriccion_1:    15.000000  ← Cada unidad extra de madera vale $15
restriccion_2:    20.000000  ← Cada hora extra vale $20
```

**2. Rangos de Optimalidad**: Variaciones permitidas en coeficientes de la función objetivo

```
x1: [60.0000, 120.0000]   ← Precio de mesas puede variar entre $60 y $120
x2: [25.0000, 100.0000]   ← Precio de sillas puede variar entre $25 y $100
```

**3. Rangos de Factibilidad**: Variaciones permitidas en recursos disponibles

```
restriccion_1: [120.0000, 240.0000]  ← Madera puede variar entre 120 y 240
restriccion_2: [50.0000, 100.0000]   ← Trabajo puede variar entre 50 y 100
```

Ejemplo completo:

```bash
$ python simplex.py ejemplos/ejemplo_carpinteria.txt --sensitivity

# ... solución óptima ...

============================================================
ANÁLISIS DE SENSIBILIDAD
============================================================

1. PRECIOS SOMBRA (Shadow Prices):
   restriccion_1:    15.000000
   restriccion_2:    20.000000

2. RANGOS DE OPTIMALIDAD:
   x1: [     60.0000,     120.0000]
   x2: [     25.0000,     100.0000]

3. RANGOS DE FACTIBILIDAD:
   restriccion_1: [    120.0000,     240.0000]
   restriccion_2: [     50.0000,     100.0000]
============================================================
```

**Casos de uso prácticos:**

- **Decisiones de compra**: Si el precio sombra > costo del recurso, vale la pena comprarlo
- **Negociación de precios**: Evaluar si cambios de precio afectan la decisión óptima
- **Planificación de capacidad**: Determinar rangos seguros para cambios en recursos

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

- Formato correcto del archivo
- Consistencia en el número de variables
- Tipos de restricciones válidos
- Valores numéricos correctos
- Factibilidad de la solución

## Más Información

- [Documentación Principal](../README.md)
- [Guía del Usuario](../GUIA_USUARIO.md)
- [Guía del Desarrollador](../GUIA_DESARROLLADOR.md)

## Errores Comunes

### "Error en el formato del archivo"

- Verifica que la primera línea sea `MAXIMIZE` o `MINIMIZE`
- Asegúrate de incluir `SUBJECT TO` antes de las restricciones
- Revisa que todas las restricciones tengan `<=`, `>=` o `=`

### "Número de coeficientes no coincide con variables"

- Todas las restricciones deben tener el mismo número de coeficientes que la función objetivo

### "El problema no tiene solución óptima"

- El problema puede ser no acotado o infactible
- Revisa las restricciones y la función objetivo
