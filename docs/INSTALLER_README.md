# Instalador Interactivo del Simplex Solver

## 📦 Descripción

El instalador interactivo es una herramienta con interfaz de consola que facilita la instalación y configuración completa del Simplex Solver, incluyendo componentes opcionales como Ollama y modelos de IA.

## ✨ Características

### 🔍 Análisis Automático del Sistema

- Detecta automáticamente las capacidades de tu PC:
  - RAM total y disponible
  - Núcleos de CPU y frecuencia
  - GPU NVIDIA (si está disponible)
  - Sistema operativo y arquitectura

### 🤖 Recomendaciones Inteligentes

- Sugiere modelos de IA compatibles con tu hardware
- Indica cuáles modelos funcionarán mejor en tu sistema
- Advierte sobre modelos que requieren más recursos

### 📋 Componentes Instalables

1. **Dependencias Base** (siempre se instalan)

   - NumPy, psutil, tabulate
   - Todas las librerías necesarias para el solver

2. **Ollama** (opcional)

   - Motor de IA local para procesamiento de lenguaje natural
   - Permite resolver problemas descritos en lenguaje natural
   - Funciona completamente offline

3. **Modelos de IA** (opcional)

   - `llama3.2:1b` - Ligero (2 GB RAM)
   - `llama3.2:3b` - Balanceado (4 GB RAM)
   - `phi3:mini` - Optimizado Microsoft (4 GB RAM)
   - `llama3.1:8b` - Calidad media (8 GB RAM)
   - `mistral:7b` - Excelente general (8 GB RAM)
   - `gemma2:9b` - Alta capacidad (10 GB RAM)
   - `llama3.1:70b` - Máxima calidad (48 GB RAM)

4. **Menú Contextual de Windows** (opcional)
   - Click derecho en archivos .txt
   - Opción "Resolver con Simplex Solver"
   - Opción "Resolver con IA"

## 🚀 Uso

### Ejecutar el Instalador

#### Desde Python:

```bash
python installer.py
```

#### Desde el Ejecutable:

```bash
SimplexInstaller.exe
```

### Flujo del Instalador

1. **Pantalla de Bienvenida**

   - Información general sobre el proceso

2. **Análisis del Sistema**

   - Muestra las capacidades detectadas
   - Indica compatibilidad con Ollama

3. **Instalación de Ollama**

   - Pregunta si deseas instalar Ollama
   - Proporciona enlace de descarga si no está instalado

4. **Selección de Modelos**

   - Muestra modelos disponibles
   - Indica cuáles son recomendados para tu sistema
   - Opciones:
     - A: Instalar todos los recomendados
     - B: Seleccionar manualmente
     - C: No instalar ahora

5. **Menú Contextual**

   - Pregunta si deseas instalar el menú contextual
   - Explica las funcionalidades

6. **Resumen de Instalación**

   - Muestra todo lo que se va a instalar
   - Confirmación final

7. **Proceso de Instalación**

   - Instala dependencias de Python
   - Configura Ollama (si se eligió)
   - Descarga modelos seleccionados
   - Instala menú contextual (si se eligió)

8. **Finalización**
   - Muestra instrucciones de uso
   - Próximos pasos recomendados

## 🎨 Interfaz

El instalador utiliza colores ANSI para mejorar la experiencia visual:

- 🔵 **Azul**: Secciones y títulos
- 🟢 **Verde**: Éxito y elementos recomendados
- 🟡 **Amarillo**: Advertencias y preguntas
- 🔴 **Rojo**: Errores
- ⚪ **Cyan**: Información general

Compatible con Windows 10+ (habilita automáticamente los códigos ANSI).

## 🛠️ Generar el Instalador Ejecutable

Para crear el instalador como archivo .exe:

```bash
python build_installer.py
```

Esto generará:

- `dist/SimplexSolver/SimplexInstaller.exe` - Instalador interactivo
- `dist/SimplexSolver/SimplexSolver.exe` - Aplicación principal
- `dist/SimplexSolver/INSTALACION.txt` - Instrucciones
- Ejemplos y documentación incluidos

## 📊 Requisitos del Sistema

### Mínimos (solo solver básico):

- Windows 10 o superior
- 2 GB RAM
- 500 MB espacio en disco
- Python 3.8+ (si se usa desde código)

### Recomendados (con IA):

- Windows 10 o superior
- 8 GB RAM
- 20 GB espacio en disco (para Ollama y modelos)
- GPU NVIDIA (opcional, mejora rendimiento)

## 🔧 Componentes Técnicos

### `installer.py`

Script principal del instalador con:

- Clase `SimplexInstaller`: Maneja todo el flujo de instalación
- Clase `Color`: Códigos ANSI para colores
- Interfaz interactiva completa

### `src/system_analyzer.py`

Módulo de análisis de sistema:

- Clase `SystemAnalyzer`: Analiza capacidades del sistema
- Clase `SystemCapabilities`: Información del sistema
- Clase `ModelRecommendation`: Recomendaciones de modelos
- Detección de GPU NVIDIA con nvidia-smi

### `build_installer.py`

Script de construcción:

- Crea archivos .spec para PyInstaller
- Compila instalador y solver
- Genera paquete de distribución completo

## 📖 Ejemplos de Uso

### Instalación Rápida

```
SimplexInstaller.exe

Bienvenido al instalador...
[Análisis automático del sistema]
Tu sistema tiene 16 GB RAM, 8 núcleos CPU
✓ Compatible con Ollama

¿Deseas instalar Ollama? [S/n]: s
[Modelos recomendados: llama3.1:8b, mistral:7b, phi3:mini]
Elige opción (A/B/C): A

¿Deseas instalar el menú contextual? [S/n]: s

Resumen:
  ✓ Dependencias Python
  ✓ Ollama + 3 modelos
  ✓ Menú contextual

¿Continuar? [S/n]: s
[Instalación en progreso...]
✓ Completado!
```

### Instalación Personalizada

```
SimplexInstaller.exe

[... análisis del sistema ...]
¿Deseas instalar Ollama? [S/n]: s
Elige opción (A/B/C): B

Modelos disponibles:
  1. llama3.2:1b (1.3 GB)
  2. phi3:mini (2.3 GB)
  3. llama3.1:8b (4.7 GB)

Números de modelos: 2,3

Modelos seleccionados:
  • phi3:mini
  • llama3.1:8b

[Continúa instalación...]
```

### Solo Solver Básico

```
SimplexInstaller.exe

[... análisis del sistema ...]
¿Deseas instalar Ollama? [S/n]: n
¿Deseas instalar el menú contextual? [S/n]: n

Resumen:
  ✓ Dependencias Python solamente

[Instalación básica...]
```

## 🎯 Decisiones de Diseño

### ¿Por qué consola en lugar de GUI?

1. **Compatibilidad**: Funciona en cualquier Windows sin dependencias adicionales
2. **Tamaño**: El ejecutable es mucho más pequeño
3. **Simplicidad**: Más fácil de mantener y depurar
4. **Experiencia**: Interfaz clara y directa para desarrolladores
5. **Recursos**: Consume menos memoria y CPU

### Análisis Automático

El instalador analiza:

- **RAM**: Para recomendar modelos apropiados
- **GPU**: Para indicar si habrá aceleración
- **Espacio**: Para verificar que hay suficiente disco
- **CPU**: Para estimar rendimiento

### Modelos Recomendados

Los criterios de recomendación:

- RAM disponible >= 1.2x RAM requerida
- Prioriza modelos con mejor balance calidad/tamaño
- Advierte sobre modelos que podrían causar problemas

## 🐛 Solución de Problemas

### El instalador no detecta mi GPU

- Asegúrate de tener drivers NVIDIA instalados
- Verifica que `nvidia-smi` funcione desde terminal
- La GPU es opcional, el sistema funciona sin ella

### Error al instalar dependencias

- Verifica conexión a internet
- Ejecuta como administrador
- Actualiza pip: `python -m pip install --upgrade pip`

### Ollama no se descarga

- El instalador solo proporciona el enlace
- Debes descargar e instalar Ollama manualmente
- Reinicia el terminal después de instalar Ollama

### Modelos no se descargan

- Verifica que Ollama esté instalado: `ollama --version`
- Requiere conexión a internet
- Puede tardar según tu conexión (modelos grandes)

### Menú contextual no aparece

- Requiere permisos de administrador
- Reinicia el explorador de Windows
- Verifica en el registro: `HKEY_CLASSES_ROOT\*\shell`

## 📝 Licencia

Parte del proyecto Simplex Solver.
Consulta LICENSE en el directorio raíz del proyecto.

## 🤝 Contribuir

¿Mejoras para el instalador?

1. Fork del repositorio
2. Crea una rama: `git checkout -b feature/mejora-instalador`
3. Commits: `git commit -m 'Mejora en instalador'`
4. Push: `git push origin feature/mejora-instalador`
5. Pull Request

## 📧 Soporte

Para problemas o sugerencias sobre el instalador:

- GitHub Issues: https://github.com/frangcisneros/simplex-project/issues
- Tag: `instalador`
