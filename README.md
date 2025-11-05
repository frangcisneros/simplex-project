# Simplex Solver con Inteligencia Artificial

Sistema de optimización lineal que combina el algoritmo Simplex con modelos de lenguaje (Ollama) para resolver problemas de programación lineal descritos en español.

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Características

- **IA Integrada**: Usa modelos de lenguaje (Llama 3.1, Mistral) para entender problemas en español
- **Lenguaje Natural**: Describe problemas con texto normal, sin necesidad de fórmulas matemáticas
- **Procesamiento Local**: Funciona completamente en tu computadora usando Ollama
- **Múltiples Tipos de Problemas**: Producción, transporte, dieta, mezclas, asignación de recursos
- **Menú Contextual de Windows**: Resuelve problemas con clic derecho en archivos .txt

## Instalación

### Instalación Rápida (Recomendado)

**Con el Instalador Interactivo** (Windows):

1. Descarga el paquete de distribución
2. Ejecuta `SimplexInstaller.exe` como administrador
   - El instalador solicita permisos de administrador automáticamente
   - Necesarios para instalar el menú contextual de Windows
3. El instalador:
   - Analiza automáticamente las capacidades de tu PC
   - Recomienda modelos de IA compatibles con tu hardware
   - Te guía en la instalación de todos los componentes
   - Configura el menú contextual de Windows (opcional)

Para más información, consulte GUIA_USUARIO.md.

### Instalación Manual

#### 1. Clonar el repositorio

```bash
git clone https://github.com/frangcisneros/simplex-project
cd simplex-project
pip install -r requirements.txt
```

#### 2. Instalar Ollama (opcional, para funcionalidades de IA)

Descargar desde: https://ollama.ai/download

Después de instalar:

```bash
ollama pull llama3.1:8b
```

#### 3. Probar el sistema

```bash
cd tests
python test_nlp_system.py
```

## Ejemplo de Uso

**Entrada:**

```
Una carpintería fabrica mesas y sillas.
Cada mesa da $80 de ganancia, cada silla $50.
Hay 200 horas de trabajo disponibles.
Cada mesa requiere 4 horas, cada silla 2 horas.
¿Cuántas hacer para maximizar ganancia?
```

**Proceso:**

1. La IA identifica 2 variables (mesas, sillas)
2. Extrae la función objetivo (maximizar ganancia)
3. Detecta las restricciones (200 horas disponibles)
4. Resuelve el problema con el algoritmo Simplex

**Salida:**

```
Solución óptima encontrada
Valor óptimo: $4,000.00

Variables:
  mesas = 50.00
  sillas = 0.00
```

## Estructura del Proyecto

```
simplex-project/
├── README.md
├── pyproject.toml                   # Configuración del proyecto
├── requirements.txt                 # Dependencias runtime
├── requirements-full.txt            # Todas las dependencias
├── requirements-dev.txt             # Herramientas de desarrollo
├── requirements-build.txt           # Herramientas de compilación
├── simplex.py                       # Script principal
├── installer.py                     # Instalador interactivo
│
├── simplex_solver/                  # Paquete principal (antes src/)
│   ├── solver.py                    # Algoritmo Simplex
│   ├── file_parser.py               # Parser de archivos
│   ├── user_interface.py            # Interfaz de usuario
│   ├── reporting_pdf.py             # Generación de reportes
│   ├── core/                        # Lógica del algoritmo
│   │   └── algorithm.py
│   ├── utils/                       # Utilidades
│   │   └── tableau.py
│   └── nlp/                         # Sistema NLP
│       ├── connector.py             # Orquestador principal
│       ├── ollama_processor.py      # Procesador con Ollama
│       ├── model_generator.py       # Generador de modelos
│       └── ...
│
├── context_menu/                    # Menú contextual de Windows
│   ├── solve_from_context.py       # Script del menú contextual
│   ├── install.bat                  # Instalador
│   ├── uninstall.bat                # Desinstalador
│   └── README.md                    # Documentación
│
├── ejemplos/                        # Archivos de ejemplo
│   ├── ejemplo_maximizacion.txt
│   ├── ejemplo_minimizacion.txt
│   ├── ejemplo_carpinteria.txt
│   └── README.md
│
├── tests/                           # Suite de tests
│   ├── test_nlp_system.py
│   ├── test_maximizacion.py
│   └── test_minimizacion.py
│
├── tools/                           # Herramientas de desarrollo
│   ├── build.py                     # Sistema unificado de build
│   ├── logs.py                      # Gestión unificada de logs
│   ├── history.py                   # Gestión de historial
│   ├── test_installer.py            # Tests del instalador
│   └── README.md                    # Guía de herramientas
│
└── logs/                           # Base de datos de logging
```

## Documentación

Consulte las siguientes guías para información completa:

**Guías Principales:**

- **GUIA_USUARIO.md**: Guía completa de instalación y uso para usuarios finales
- **GUIA_DESARROLLADOR.md**: Documentación técnica para desarrolladores

**Documentación Adicional:**

- **tools/README.md**: Guía de herramientas de desarrollo
- **ejemplos/README.md**: Información sobre archivos de ejemplo

## Uso

### Menú Contextual de Windows

**Resuelve problemas de Simplex con solo un clic derecho:**

1. **Instala el menú contextual** (solo una vez):

   - Navega a la carpeta `context_menu/`
   - Haz clic derecho en `install.bat`
   - Selecciona "Ejecutar como administrador"

2. **Usa el menú contextual**:
   - Crea un archivo `.txt` con tu problema de Simplex (ver ejemplos en `ejemplos/`)
   - Haz clic derecho en el archivo
   - Selecciona "Resolver con Simplex Solver"
   - Se abrirá una ventana con la solución

**Guía completa**: Consulte GUIA_USUARIO.md  
**Ejemplos**: Vea la carpeta `ejemplos/`

### Desde Python

```python
from simplex_solver.nlp import NLPConnectorFactory, NLPModelType

# Crear conector
connector = NLPConnectorFactory.create_connector(
    nlp_model_type=NLPModelType.LLAMA3_1_8B
)

# Resolver problema
resultado = connector.process_and_solve("""
    Una empresa fabrica productos A y B.
    A da $50 de ganancia, B da $40.
    Cada A requiere 2 horas, cada B 1 hora.
    Hay 100 horas disponibles.
    Maximizar ganancia.
""")

# Mostrar resultado
if resultado["success"]:
    print(f"Valor óptimo: ${resultado['solution']['optimal_value']:.2f}")
```

### Tests Incluidos

```bash
# Ejecutar suite completa de tests
cd tests
python test_nlp_system.py
```

## Modelos Soportados

| Modelo      | Tamaño | Precisión | Recomendado Para                  |
| ----------- | ------ | --------- | --------------------------------- |
| llama3.1:8b | 4.9 GB | Alta      | Problemas complejos (recomendado) |
| llama3.2:3b | 2.0 GB | Media     | Problemas simples                 |
| mistral:7b  | 4.0 GB | Alta      | Uso general                       |
| qwen2.5:14b | 8.0 GB | Muy Alta  | Problemas muy complejos           |

**Instalación:**

```bash
ollama pull llama3.1:8b    # Modelo por defecto
```

## Tipos de Problemas Soportados

- **Producción**: Maximizar ganancias con recursos limitados
- **Transporte**: Minimizar costos de distribución
- **Dieta**: Optimizar nutrición con presupuesto
- **Mezclas**: Combinar materias primas óptimamente
- **Asignación**: Distribuir recursos eficientemente

Ver ejemplos de archivos .txt en carpeta `ejemplos/`

## Configuración

### Cambiar Modelo

Editar `simplex_solver/nlp/config.py`:

```python
class DefaultSettings:
    DEFAULT_MODEL = NLPModelType.LLAMA3_1_8B  # Cambiar aquí
```

### Ajustar Parámetros

```python
ModelConfig.DEFAULT_CONFIGS[NLPModelType.LLAMA3_1_8B] = {
    "temperature": 0.1,  # Precisión (0-1)
    "max_tokens": 2048,
    "top_p": 0.9
}
```

## Solución de Problemas

### Ollama no responde

```bash
# Verificar que está corriendo
ollama list

# Instalar modelo si falta
ollama pull llama3.1:8b
```

### Modelo lento

Primera vez es normal (30-60s para cargar). Si siempre es lento, usar un modelo más pequeño:

```bash
ollama pull llama3.2:3b
```

### Error de dependencias

```bash
pip install -r requirements.txt
```

Ver GUIA_USUARIO.md para más ayuda.

## Compilar Ejecutables

Para generar los ejecutables, usa el **sistema unificado de build** (NUEVO):

```bash
# Generar el instalador
python tools/build.py --installer

# Generar el solver
python tools/build.py --solver

# Generar ambos
python tools/build.py --all

# Limpiar artifacts de compilación
python tools/build.py --clean
```

Los ejecutables se generarán en `dist/`:

- `dist/SimplexInstaller.exe` - Instalador interactivo
- `dist/SimplexSolver.exe` - Solver standalone

**Guía completa**: Consulte GUIA_DESARROLLADOR.md  
**Herramientas**: Consulte tools/README.md

## Herramientas de Desarrollo

El proyecto incluye herramientas consolidadas siguiendo principios SOLID:

### Build System

```bash
python tools/build.py --all     # Compilar todo
python tools/build.py --clean   # Limpiar artifacts
```

### Log Management

```bash
python tools/logs.py            # Visor interactivo
python tools/logs.py --stats    # Estadísticas rápidas
python tools/logs.py --verify   # Verificar integridad
```

### History Management

```bash
python tools/history.py         # Menú interactivo
python tools/history.py --test  # Test del sistema
python tools/history.py --stats # Estadísticas
```

**Documentación completa**: Consulte tools/README.md

## Testing

```bash
# Suite completa de tests del sistema NLP
cd tests
python test_nlp_system.py
```

Los tests incluyen:

- Tests unitarios de cada componente
- Tests de integración del pipeline completo
- Tests de extremo a extremo con problemas reales
- Validación de modelos y estructuras

## Autor

- Francisco - [@frangcisneros](https://github.com/frangcisneros)
- Emiliana
- Marcelo
- Guillermo
- Lucia

## Soporte

- **Documentación completa**: Ver GUIA_USUARIO.md y GUIA_DESARROLLADOR.md
- **Issues**: [GitHub Issues](https://github.com/frangcisneros/simplex-project/issues)

## Versión

Versión 3.1 - Noviembre 2025

**Novedades v3.1:**

- Sistema de build unificado siguiendo principios SOLID
- Herramientas consolidadas para desarrollo
- Documentación mejorada y reorganizada
- Eliminación de código duplicado (-50% de scripts)
- Guías consolidadas para usuarios y desarrolladores
