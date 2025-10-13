# 📝 Guía de Reformulación de Problemas para IA

## 🎯 Objetivo

Esta guía te ayuda a **reescribir problemas de optimización** de manera más clara para que la IA los entienda mejor, **sin cambiar su contenido matemático**.

## ✨ Principios Clave

### 1. **Estructura Clara**: Separa la información en secciones

### 2. **Explícito > Implícito**: Di las cosas claramente

### 3. **Números antes de referencias**: Define valores antes de usarlos

### 4. **Usa listas numeradas**: Para elementos múltiples

### 5. **Menciona todas las combinaciones**: En problemas multi-instalación

---

## 📖 Ejemplo Práctico: Problema Complejo 1

### ❌ Versión Original (Difícil para IA)

```
Cierta compañía tiene tres plantas con un exceso en su capacidad de producción.
Por fortuna, la corporación tiene un nuevo producto listo para producción y las
tres plantas pueden fabricarlo, así que se podrá usar parte de este exceso de
capacidad. El producto puede hacerse en tres tamaños: grande, mediano y chico;
y darán una ganancia neta de $420, $360 y $300, respectivamente. Las plantas
1 2 y 3 tienen capacidad de mano de obra y equipo para producir 750, 900 y 450
unidades diarias de este producto respectivamente, sin importar el tamaño o la
combinación de tamaños de que se trate.
```

**Problemas identificados:**

- ❌ "Las plantas 1 2 y 3" (sin comas, confuso)
- ❌ Información dispersa
- ❌ No menciona explícitamente que cada planta produce cada tamaño
- ❌ Demasiado narrativo

### ✅ Versión Reformulada (Clara para IA)

```
PROBLEMA: Una compañía tiene 3 plantas de producción y fabrica un producto
en 3 tamaños diferentes. Necesita decidir cuántas unidades de cada tamaño
producir en cada planta para maximizar la ganancia.

PLANTAS:
- Planta 1: capacidad 750 unidades/día (cualquier tamaño)
- Planta 2: capacidad 900 unidades/día (cualquier tamaño)
- Planta 3: capacidad 450 unidades/día (cualquier tamaño)

PRODUCTOS (cada planta puede fabricar los 3 tamaños):
- Tamaño grande: ganancia $420 por unidad
- Tamaño mediano: ganancia $360 por unidad
- Tamaño chico: ganancia $300 por unidad

NOTA IMPORTANTE: Cada planta puede producir cualquier combinación de los 3 tamaños.
Por lo tanto, hay 9 decisiones a tomar: cuánto producir de cada tamaño en cada planta.

RESTRICCIONES POR PLANTA:
- Planta 1:
  * Total producción ≤ 750 unidades
  * Espacio: 13,000 pies cuadrados para almacenamiento

- Planta 2:
  * Total producción ≤ 900 unidades
  * Espacio: 12,000 pies cuadrados para almacenamiento

- Planta 3:
  * Total producción ≤ 450 unidades
  * Espacio: 5,000 pies cuadrados para almacenamiento

ESPACIO REQUERIDO POR UNIDAD:
- Grande: 20 pies cuadrados
- Mediano: 15 pies cuadrados
- Chico: 12 pies cuadrados

RESTRICCIONES DE DEMANDA TOTAL (suma de las 3 plantas):
- Tamaño grande: máximo 900 unidades totales
- Tamaño mediano: máximo 1,200 unidades totales
- Tamaño chico: máximo 750 unidades totales

OBJETIVO: Maximizar ganancia total.
```

**Mejoras aplicadas:**

- ✅ Estructura clara con secciones
- ✅ Números explícitos: "3 plantas", "3 tamaños"
- ✅ Lista de plantas con capacidades
- ✅ Nota explícita: "9 decisiones a tomar"
- ✅ Restricciones organizadas por tipo

---

## 🛠️ Plantilla para Problemas Multi-Instalación

Usa esta plantilla cuando tengas **N plantas × M productos**:

```markdown
PROBLEMA: [Empresa] tiene [N] plantas que producen [M] productos diferentes.

PLANTAS (cada una puede fabricar todos los productos):

- Planta 1: [capacidades y características]
- Planta 2: [capacidades y características]
- Planta N: [capacidades y características]

PRODUCTOS (fabricables en todas las plantas):

- Producto 1: ganancia $[X] por unidad
- Producto 2: ganancia $[Y] por unidad
- Producto M: ganancia $[Z] por unidad

NOTA: Hay [N × M] decisiones: cuánto producir de cada producto en cada planta.

RESTRICCIONES DE CAPACIDAD:
[Lista por planta]

RESTRICCIONES DE DEMANDA:
[Lista por producto]

OBJETIVO: [Maximizar/Minimizar] [ganancia/costo].
```

---

## 🧪 Ejemplo Práctico: Problema de Mezclas

### ❌ Versión Original (Confusa)

```
Una refinería produce 4 tipos de gasolina (gas 1, gas 2, gas 3 y gas 4).
Dos características importantes de cada gasolina son su número de performance
(NP) y su presión de vapor (PV). En el caso de la gas1, el NP es 107 y el PV
de 5, Gas2 el NP es 93 y PV de 8, gas 3 NP 87 y PV igual a 4 y para gas 4
el NP es 108 y PV de 21.
```

### ✅ Versión Reformulada

```
PROBLEMA: Una refinería tiene 4 tipos de gasolina base que puede vender
directamente o mezclar para crear 2 productos premium (avgas A y avgas B).

GASOLINAS BASE (pueden venderse directamente o usarse en mezclas):
1. Gas 1: producción 3,814 barriles/día, NP=107, PV=5, utilidad venta directa $21.33/barril
2. Gas 2: producción 2,666 barriles/día, NP=93, PV=8, utilidad venta directa $22.53/barril
3. Gas 3: producción 4,016 barriles/día, NP=87, PV=4, utilidad venta directa $23.48/barril
4. Gas 4: producción 1,300 barriles/día, NP=108, PV=21, utilidad venta directa $22.33/barril

PRODUCTOS PREMIUM (mezclas de las 4 gasolinas base):
- Avgas A: utilidad $26.45/barril, requiere NP≥100 y PV≤7
- Avgas B: utilidad $25.91/barril, requiere NP≥91 y PV≤6

NOTA IMPORTANTE: El NP y PV de cada mezcla es el promedio ponderado de sus componentes.

DECISIONES A TOMAR:
1. Cuántos barriles de cada gas vender directamente (4 variables)
2. Cuántos barriles de avgas A y avgas B producir (2 variables)
3. Cuánto de cada gas usar en cada avgas (4 gases × 2 avgas = 8 variables)
Total: 14 variables de decisión

RESTRICCIONES:
- Balance de material: lo vendido + lo usado en mezclas = producción disponible
- Calidad de mezclas: cumplir especificaciones de NP y PV

OBJETIVO: Maximizar utilidad total.
```

---

## 📋 Checklist para Reformular tu Problema

Antes de enviar tu problema a la IA, verifica:

### ✅ Estructura

- [ ] Tiene un título/encabezado claro
- [ ] Información organizada en secciones
- [ ] Usa listas con viñetas o números
- [ ] Flujo lógico: datos → decisiones → restricciones → objetivo

### ✅ Claridad Numérica

- [ ] Dice explícitamente cuántas plantas/instalaciones hay
- [ ] Dice explícitamente cuántos productos/tamaños hay
- [ ] Menciona el número total de variables/decisiones
- [ ] Todos los números están con sus unidades

### ✅ Explicitud

- [ ] Dice claramente "cada planta puede producir cada producto"
- [ ] Menciona todas las combinaciones posibles
- [ ] No usa "respectivamente" sin lista clara
- [ ] Define términos técnicos si es necesario

### ✅ Formato

- [ ] Usa mayúsculas para secciones (PLANTAS:, PRODUCTOS:)
- [ ] Usa - o números para listas
- [ ] Separa párrafos con líneas en blanco
- [ ] Destaca información clave con NOTA IMPORTANTE

---

## 🎓 Reglas de Oro

### 1. **La Regla del "N × M"**

Si tienes N instalaciones y M productos:

```
❌ "Hay varias plantas que producen distintos productos"
✅ "Hay 3 plantas y 4 productos, por lo que hay 3 × 4 = 12 variables"
```

### 2. **La Regla de la Tabla Mental**

Si puedes hacer una tabla de variables, descríbela:

```
❌ "Cada planta produce productos A, B y C"
✅ "Variables: xij donde i=planta (1,2,3) y j=producto (A,B,C)
    Esto da 9 variables: x1A, x1B, x1C, x2A, x2B, x2C, x3A, x3B, x3C"
```

### 3. **La Regla del "Puede vs Debe"**

```
❌ "La planta 1 produce grande y mediano" [¿solo esos?]
✅ "La planta 1 PUEDE producir grande, mediano Y chico" [todos]
```

### 4. **La Regla de la Ganancia Única**

Si la ganancia es la misma en todas partes:

```
❌ "Producto A vale $10 en planta 1 y $10 en planta 2"
✅ "Producto A: ganancia $10 por unidad (igual en todas las plantas)"
```

### 5. **La Regla del Contexto Matemático**

```
❌ "Maximizar beneficios" [¿qué beneficios?]
✅ "Maximizar la ganancia total sumando todas las unidades vendidas × su ganancia"
```

---

## 🔄 Ejemplo de Reformulación Rápida

**Técnica de 5 minutos:**

1. **Identifica las partes**: ¿Qué decides? → Variables
2. **Cuenta explícitamente**: ¿Cuántas decisiones? → N × M
3. **Lista todo**: Plantas, productos, restricciones
4. **Agrega nota**: "Hay X variables porque..."
5. **Verifica números**: ¿Están todos los valores?

---

## 📊 Comparación de Resultados

### Problema Original vs Reformulado

| Aspecto                          | Original | Reformulado | Mejora   |
| -------------------------------- | -------- | ----------- | -------- |
| Variables extraídas (Problema 1) | 3-6 de 9 | **?**       | A probar |
| Variables extraídas (Problema 2) | 13 de 14 | **?**       | A probar |
| Tiempo de procesamiento          | ~85s     | Similar     | -        |
| Claridad para humanos            | Media    | Alta        | ✅       |
| Mantenibilidad                   | Baja     | Alta        | ✅       |

---

## 💡 Tips Adicionales

### Para Problemas de Transporte

```
✅ "Desde origen i hasta destino j"
✅ Usa matriz de costos/distancias explícita
```

### Para Problemas de Mezclas

```
✅ Explica que el componente X va a la mezcla Y
✅ Menciona "N materiales × M mezclas = N×M variables de composición"
```

### Para Problemas con Múltiples Periodos

```
✅ "En cada periodo t (t=1,2,3) se decide..."
✅ "Total: N productos × T periodos = variables"
```

---

## 🚀 Próximos Pasos

1. **Prueba**: Reformula tu problema usando esta guía
2. **Compara**: Ejecuta con `python nlp_simplex.py --nlp --file problema_reformulado.txt`
3. **Itera**: Si no funciona, agrega más detalles numéricos
4. **Documenta**: Guarda las versiones que funcionan como ejemplos

---

## 📞 ¿Necesitas Ayuda?

Si después de reformular el problema la IA aún no extrae todas las variables:

1. **Verifica**: ¿Mencionaste explícitamente el número de variables?
2. **Simplifica**: ¿Puedes dividir el problema en sub-problemas?
3. **Consulta**: Revisa los ejemplos en `src/nlp/config.py`
4. **Considera**: Para >10 variables, usar API externa (GPT-4, Claude)

---

**Recuerda**: No estás cambiando el problema matemático, solo lo escribes de manera que la IA entienda mejor la estructura. ¡Es como usar un buen formato de código! 🎨
