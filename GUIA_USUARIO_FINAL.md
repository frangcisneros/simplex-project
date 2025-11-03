# 🚀 Guía Rápida de Inicio - Simplex Solver

## Para Usuarios Finales

### 📥 Instalación en 3 Pasos

#### Paso 1: Descargar

- Descarga el archivo `SimplexSolver-v1.0.zip`
- Descomprime en una carpeta de tu elección

#### Paso 2: Ejecutar el Instalador

- Abre la carpeta `SimplexSolver`
- Doble click en `SimplexInstaller.exe`
- **Importante**: Si Windows SmartScreen lo bloquea:
  - Click en "Más información"
  - Click en "Ejecutar de todas formas"

#### Paso 3: Seguir el Asistente

El instalador te guiará paso a paso. Solo sigue las instrucciones en pantalla.

---

## ❓ Preguntas Frecuentes Durante la Instalación

### "¿Qué es Ollama?"

Es un programa que permite que la computadora entienda problemas en lenguaje normal (español). Es opcional, pero recomendado.

**Responde "S" si**: Quieres escribir problemas en español natural  
**Responde "N" si**: Solo vas a usar archivos .txt con formato específico

### "¿Qué modelo de IA elegir?"

El instalador te recomendará automáticamente según tu PC.

**Opción A (Recomendada)**: Instala todos los modelos que tu PC puede manejar  
**Opción B**: Si sabes lo que haces, elige específicos  
**Opción C**: Si no tienes internet o espacio, instala después

### "¿Instalar el menú contextual?"

Te permite resolver problemas haciendo click derecho en archivos.

**Responde "S" si**: Quieres la forma más fácil de usar el programa  
**Responde "N" si**: Prefieres usar la línea de comandos

---

## 🎯 Después de la Instalación

### Opción 1: Modo Interactivo (Más Fácil)

1. Abre PowerShell o CMD
2. Navega a la carpeta del programa
3. Ejecuta:
   ```bash
   SimplexSolver.exe --interactive
   ```
4. Sigue las instrucciones en pantalla

### Opción 2: Con Archivos de Ejemplo

1. Abre PowerShell o CMD
2. Ejecuta:
   ```bash
   SimplexSolver.exe ejemplos\ejemplo_maximizacion.txt
   ```
3. Ver el resultado

### Opción 3: Menú Contextual (Si lo instalaste)

1. Abre el explorador de Windows
2. Busca un archivo .txt con un problema
3. Click derecho → "Resolver con Simplex Solver"
4. Listo!

### Opción 4: Con Lenguaje Natural (Si instalaste Ollama)

1. Abre PowerShell o CMD
2. Ejecuta:
   ```bash
   SimplexSolver.exe --ai "Una carpintería produce mesas y sillas..."
   ```
3. El sistema entenderá y resolverá el problema

---

## 📝 Formatos de Problemas

### Formato Simple (Archivo .txt)

Ejemplo: `mi_problema.txt`

```
MAXIMIZAR 3x + 5y

SUJETO A:
x <= 4
2y <= 12
3x + 2y <= 18
x >= 0
y >= 0
```

### Lenguaje Natural (Con Ollama)

Ejemplo:

```
"Una fábrica produce productos A y B.
El producto A da $30 de ganancia y B da $50.
Hay 100 horas de trabajo disponibles.
A requiere 2 horas y B requiere 3 horas.
¿Cuánto producir de cada uno para maximizar ganancias?"
```

---

## 🔧 Solución de Problemas Comunes

### "No puedo ejecutar SimplexInstaller.exe"

**Solución**: Click derecho → "Ejecutar como administrador"

### "El instalador dice que no tengo suficiente RAM"

**Solución**:

- Aún puedes usar el solver básico (sin IA)
- El instalador solo advertirá sobre los modelos de IA
- Continúa con "N" cuando pregunte por Ollama

### "Ollama no se instala automáticamente"

**Explicación**: Ollama requiere instalación manual
**Solución**:

1. El instalador te mostrará un enlace
2. Descarga desde https://ollama.ai/download
3. Instala Ollama
4. Vuelve a ejecutar SimplexInstaller.exe

### "Los modelos tardan mucho en descargar"

**Explicación**: Los modelos son archivos grandes (1-5 GB cada uno)
**Solución**:

- Es normal, especialmente con internet lento
- Puedes cancelar (Ctrl+C) e instalar después con:
  ```bash
  ollama pull nombre-del-modelo
  ```

### "No aparece el menú contextual"

**Solución**:

1. Cierra todas las ventanas del explorador
2. Reinicia el explorador de Windows
3. Si persiste: Ejecuta `context_menu\install.bat` como administrador

### "SimplexSolver.exe no funciona"

**Verificación**:

```bash
SimplexSolver.exe --help
```

Si no funciona:

- Verifica que descargaste el paquete completo
- Reinstala con SimplexInstaller.exe

---

## 📚 Ejemplos Incluidos

En la carpeta `ejemplos/` encontrarás:

| Archivo                    | Descripción                     |
| -------------------------- | ------------------------------- |
| `ejemplo_maximizacion.txt` | Problema básico de maximización |
| `ejemplo_minimizacion.txt` | Problema de minimización        |
| `ejemplo_carpinteria.txt`  | Problema de producción          |
| `max_4tablas.txt`          | Problema con 4 variables        |

**Para probar cualquiera**:

```bash
SimplexSolver.exe ejemplos\nombre-del-archivo.txt
```

---

## 🎓 Tutoriales Paso a Paso

### Tutorial 1: Mi Primer Problema

1. **Crea un archivo**: `problema1.txt`

2. **Escribe**:

   ```
   MAXIMIZAR 2x + 3y

   SUJETO A:
   x + y <= 10
   x <= 6
   y <= 8
   x >= 0
   y >= 0
   ```

3. **Resuelve**:

   ```bash
   SimplexSolver.exe problema1.txt
   ```

4. **Resultado**: Verás el valor óptimo y las variables

### Tutorial 2: Usar el Modo Interactivo

1. **Ejecuta**:

   ```bash
   SimplexSolver.exe --interactive
   ```

2. **Sigue las preguntas**:

   - ¿Maximizar o minimizar?
   - ¿Cuántas variables?
   - Ingresa la función objetivo
   - Ingresa las restricciones

3. **Ver resultado**

### Tutorial 3: Lenguaje Natural (Con Ollama)

1. **Piensa en un problema real**

2. **Escríbelo naturalmente**:

   ```bash
   SimplexSolver.exe --ai "Tengo una panadería. Hago pan y pasteles. El pan da $2 de ganancia y los pasteles $5. Tengo 50kg de harina. El pan usa 0.5kg y los pasteles 1kg. ¿Cuánto hacer de cada uno?"
   ```

3. **La IA lo entenderá y resolverá**

---

## 🆘 ¿Necesitas Ayuda?

### Documentación Completa

- `README.md` - Información general del proyecto
- `docs/GUIA_IA.md` - Guía del sistema de IA
- `docs/INSTALLER_README.md` - Detalles del instalador

### Comandos Útiles

```bash
# Ver ayuda
SimplexSolver.exe --help

# Modo interactivo
SimplexSolver.exe --interactive

# Ver versión
SimplexSolver.exe --version

# Resolver archivo
SimplexSolver.exe mi_problema.txt

# Con IA (requiere Ollama)
SimplexSolver.exe --ai "tu problema"
```

### Reportar Problemas

Si encuentras un error:

1. Anota el mensaje de error
2. Reporta en: https://github.com/frangcisneros/simplex-project/issues

---

## ✅ Checklist de Instalación Exitosa

- [ ] SimplexInstaller.exe ejecutado sin errores
- [ ] SimplexSolver.exe funciona (prueba con `--help`)
- [ ] Puedo resolver archivos de ejemplo
- [ ] (Opcional) Ollama instalado y funcionando
- [ ] (Opcional) Al menos un modelo de IA descargado
- [ ] (Opcional) Menú contextual aparece en archivos .txt

Si marcaste todos los obligatorios, ¡estás listo! 🎉

---

## 💡 Consejos Finales

1. **Empieza simple**: Usa los ejemplos incluidos primero
2. **Aprende el formato**: Observa cómo están escritos los ejemplos
3. **Experimenta**: Modifica los ejemplos para entender mejor
4. **Usa la IA**: Si instalaste Ollama, describe problemas naturalmente
5. **Lee la documentación**: Para casos avanzados

---

## 🎯 Resumen Visual

```
┌─────────────────────────────────────┐
│   INSTALADOR                        │
│   SimplexInstaller.exe              │
│   • Analiza tu PC                   │
│   • Recomienda modelos              │
│   • Instala todo                    │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│   USAR EL PROGRAMA                  │
│   SimplexSolver.exe                 │
│                                     │
│   Opción 1: Archivos .txt           │
│   Opción 2: Modo interactivo        │
│   Opción 3: Lenguaje natural (IA)   │
│   Opción 4: Menú contextual         │
└─────────────────────────────────────┘
```

---

**¡Disfruta usando Simplex Solver!** 🚀

Para más información, consulta la documentación completa en la carpeta `docs/`.
