# ✅ Mejora: Detección Automática de Formato

## 🎯 Problema Resuelto

**Antes:**

```bash
python nlp_simplex.py ejemplos/nlp/problema_complejo.txt
# ❌ Error: Primera línea debe ser MAXIMIZE o MINIMIZE
```

El usuario tenía que especificar manualmente el modo NLP:

```bash
python nlp_simplex.py --nlp --file ejemplos/nlp/problema_complejo.txt
```

**Ahora:**

```bash
python nlp_simplex.py ejemplos/nlp/problema_complejo.txt
# ✅ === SIMPLEX SOLVER - Detectado: Lenguaje Natural ===
```

El sistema **detecta automáticamente** el formato del archivo.

---

## 🔧 Cambios Implementados

### Archivo Modificado: `nlp_simplex.py`

#### 1. Nueva Función: `detect_file_format()`

```python
def detect_file_format(filename):
    """
    Detecta si un archivo es formato clásico de Simplex o lenguaje natural.

    Returns:
        'classic' si es formato MAXIMIZE/MINIMIZE
        'nlp' si es lenguaje natural
    """
```

**Criterios de Detección:**

1. ✅ **Primera línea es MAXIMIZE/MINIMIZE** → Formato clásico
2. ✅ **Archivo en carpeta `nlp/`** → Lenguaje natural
3. ✅ **Primera línea larga (>50 caracteres)** → Lenguaje natural
4. ✅ **Por defecto** → Lenguaje natural

#### 2. Lógica de Detección Automática

```python
elif args.filename:
    # Detectar automáticamente el formato del archivo
    file_format = detect_file_format(args.filename)

    if file_format == 'nlp':
        # Usar modo NLP
        print(f"=== SIMPLEX SOLVER - Detectado: Lenguaje Natural ===")
        args.file = args.filename
        nlp_mode(args)
    else:
        # Usar solver original
        print(f"=== SIMPLEX SOLVER - Detectado: Formato Clásico ===")
        original_main()
```

#### 3. Nuevos Argumentos de Línea de Comando

- `--classic` / `-c`: Forzar modo clásico
- `--nlp`: Forzar modo NLP (ahora opcional)
- `filename`: Ahora con detección automática

---

## 📖 Documentación Actualizada

### Archivos Actualizados:

1. **`GUIA_NLP.md`**

   - Sección "Uso Básico" mejorada
   - Explicación de detección automática
   - Nuevos ejemplos de comandos

2. **`README.md`**
   - Inicio rápido simplificado
   - Ejemplos con detección automática
   - Comandos más intuitivos

---

## 💡 Ejemplos de Uso

### Detección Automática (Recomendado)

```bash
# El sistema detecta el formato automáticamente
python nlp_simplex.py ejemplos/nlp/problema_complejo.txt
python nlp_simplex.py ejemplos/maximizar_basico.txt
```

**Salida:**

```
=== SIMPLEX SOLVER - Detectado: Lenguaje Natural ===
# o
=== SIMPLEX SOLVER - Detectado: Formato Clásico ===
```

### Texto Directo (Siempre NLP)

```bash
python nlp_simplex.py --text "Maximizar 3x + 2y sujeto a x + y <= 4"
```

### Forzar Modo Específico

```bash
# Forzar NLP (útil si la detección falla)
python nlp_simplex.py --nlp --file mi_archivo.txt

# Forzar clásico
python nlp_simplex.py --classic archivo.txt
```

### Modo Verbose

```bash
# Ver información detallada del procesamiento
python nlp_simplex.py --verbose ejemplos/nlp/problema_complejo.txt
```

---

## 🎯 Beneficios

### 1. **Experiencia de Usuario Mejorada**

- ✅ Más intuitivo: no necesitas recordar usar `--nlp`
- ✅ Menos errores: el sistema elige el modo correcto
- ✅ Más rápido: menos teclas que escribir

### 2. **Compatibilidad**

- ✅ Funciona con archivos antiguos (formato clásico)
- ✅ Funciona con archivos nuevos (lenguaje natural)
- ✅ Detecta automáticamente la estructura

### 3. **Flexibilidad**

- ✅ Detección automática por defecto
- ✅ Opción de forzar modo específico cuando sea necesario
- ✅ Compatible con todos los modos existentes

---

## 🔍 Lógica de Detección Detallada

### Algoritmo de Detección

```
1. Leer primera línea del archivo
2. SI primera_línea == "MAXIMIZE" o "MINIMIZE":
   → Formato CLÁSICO
3. SI NO, SI archivo está en carpeta "nlp/":
   → Lenguaje NATURAL
4. SI NO, SI longitud(primera_línea) > 50 caracteres:
   → Lenguaje NATURAL
5. SI NO:
   → Lenguaje NATURAL (por defecto)
```

### Ejemplos de Detección

**Archivo: `ejemplos/nlp/problema_complejo.txt`**

- Primera línea: "Cierta compañía tiene tres plantas..."
- Carpeta: contiene "nlp"
- **Resultado:** Lenguaje Natural ✅

**Archivo: `ejemplos/maximizar_basico.txt`**

- Primera línea: "MAXIMIZE"
- **Resultado:** Formato Clásico ✅

**Archivo: `mi_problema.txt`**

- Primera línea: "Una empresa quiere maximizar sus ganancias produciendo..."
- Longitud: >50 caracteres
- **Resultado:** Lenguaje Natural ✅

---

## 🧪 Casos de Prueba

### Caso 1: Archivo NLP en carpeta nlp/

```bash
python nlp_simplex.py ejemplos/nlp/problema_complejo.txt
# ✅ Detectado: Lenguaje Natural
```

### Caso 2: Archivo clásico con MAXIMIZE

```bash
python nlp_simplex.py ejemplos/maximizar_basico.txt
# ✅ Detectado: Formato Clásico
```

### Caso 3: Texto directo

```bash
python nlp_simplex.py --text "Maximizar x + y..."
# ✅ Modo NLP directo
```

### Caso 4: Forzar modo

```bash
python nlp_simplex.py --nlp --file archivo.txt
# ✅ Forzado a NLP
```

---

## 📊 Comparación Antes/Después

### Antes de la Mejora

```bash
# Usuario NO sabía qué comando usar
python nlp_simplex.py ejemplos/nlp/problema_complejo.txt
# ❌ Error: Primera línea debe ser MAXIMIZE o MINIMIZE

# Usuario tenía que buscar en documentación
python nlp_simplex.py --nlp --file ejemplos/nlp/problema_complejo.txt
# ✅ Funciona pero es más complejo
```

### Después de la Mejora

```bash
# Usuario usa comando simple
python nlp_simplex.py ejemplos/nlp/problema_complejo.txt
# ✅ === Detectado: Lenguaje Natural ===
# ✅ Funciona automáticamente
```

---

## 🎓 Casos de Uso

### Nuevo Usuario

**Antes:**

1. Lee README
2. Ve ejemplo: `python nlp_simplex.py --nlp --file problema.txt`
3. Escribe comando largo
4. ¿Olvida `--nlp`? → Error

**Ahora:**

1. Lee README
2. Ve ejemplo: `python nlp_simplex.py problema.txt`
3. Escribe comando simple
4. ✅ Funciona inmediatamente

### Usuario Avanzado

**Antes:**

- Necesita recordar usar `--nlp` para lenguaje natural
- Necesita recordar NO usar `--nlp` para formato clásico

**Ahora:**

- Usa el mismo comando para ambos formatos
- El sistema elige automáticamente
- Puede forzar modo si lo necesita con `--nlp` o `--classic`

---

## ✅ Checklist de Mejoras

- [x] Implementada función `detect_file_format()`
- [x] Agregada lógica de detección automática
- [x] Nuevos argumentos `--classic` y `--nlp` (opcionales)
- [x] Mensajes informativos de detección
- [x] Actualizada `GUIA_NLP.md`
- [x] Actualizado `README.md`
- [x] Probado con archivos NLP
- [x] Compatible con archivos clásicos
- [x] Documentados todos los casos de uso

---

## 🚀 Resultado Final

El sistema ahora es **más intuitivo y fácil de usar**:

✅ **Un solo comando** para todos los formatos  
✅ **Detección automática** inteligente  
✅ **Mensajes claros** sobre el formato detectado  
✅ **Flexibilidad** para forzar modo cuando sea necesario  
✅ **Compatibilidad** con flujos de trabajo existentes

---

**Fecha de implementación:** Octubre 7, 2025  
**Impacto:** Alto - Mejora significativa en experiencia de usuario  
**Compatibilidad:** 100% compatible con código existente
