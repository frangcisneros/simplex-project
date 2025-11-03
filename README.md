# Simplex Solver con Inteligencia Artificial

Sistema de optimización lineal que combina el algoritmo Simplex con modelos de lenguaje (Ollama) para resolver problemas de programación lineal descritos en español.

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## Características

- **IA Integrada**: Usa modelos de lenguaje (Llama 3.1, Mistral) para entender problemas en español
- **Lenguaje Natural**: Describe problemas con texto normal, sin necesidad de fórmulas matemáticas
- **Procesamiento Local**: Funciona completamente en tu computadora usando Ollama
- **Múltiples Tipos de Problemas**: Producción, transporte, dieta, mezclas, asignación de recursos
- **🆕 Menú Contextual de Windows**: Resuelve problemas con clic derecho en archivos .txt

---

## Instalación

### 🚀 Instalación Rápida (Recomendado)

**Con el Instalador Interactivo** (Windows):

1. Descarga el paquete de distribución
2. Ejecuta `SimplexInstaller.exe`
3. El instalador:
   - Analiza automáticamente las capacidades de tu PC
   - Recomienda modelos de IA compatibles con tu hardware
   - Te guía en la instalación de todos los componentes
   - Configura el menú contextual de Windows (opcional)

Ver [Guía del Instalador](docs/INSTALLER_README.md) para más detalles.

### 📦 Instalación Manual

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

---

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

---

## Estructura del Proyecto

```
simplex-project/
├── README.md
├── requirements.txt
├── simplex.py                       # Script principal
│
├── src/                             # Código fuente
│   ├── solver.py                    # Algoritmo Simplex
│   ├── file_parser.py               # Parser de archivos
│   ├── user_interface.py            # Interfaz de usuario
│   ├── reporting_pdf.py             # Generación de reportes
│   └── nlp/                         # Sistema NLP
│       ├── connector.py             # Orquestador principal
│       ├── ollama_processor.py      # Procesador con Ollama
│       ├── model_generator.py       # Generador de modelos
│       └── ...
│
├── context_menu/                    # 🆕 Menú contextual de Windows
│   ├── solve_from_context.py       # Script del menú contextual
│   ├── install.bat                  # Instalador
│   ├── uninstall.bat                # Desinstalador
│   └── README.md                    # Documentación
│
├── ejemplos/                        # 🆕 Archivos de ejemplo
│   ├── ejemplo_maximizacion.txt
│   ├── ejemplo_minimizacion.txt
│   ├── ejemplo_carpinteria.txt
│   └── README.md
│
├── tests/                           # Suite de tests
│   └── test_nlp_system.py
│
└── docs/                            # Documentación
    ├── CONTEXT_MENU_GUIDE.md        # Guía del menú contextual
    └── BUILD_INSTRUCTIONS.md
```

---

## Documentación

- **ARQUITECTURA.md**: Diseño técnico del sistema
- **GUIA_IA.md**: Guía detallada de instalación y uso
- **docs/CONTEXT_MENU_GUIDE.md**: Guía del menú contextual de Windows
- **ESTRUCTURA.md**: Organización de archivos
- **LIMPIEZA.md**: Cambios recientes

---

## Uso

### 🖱️ Menú Contextual de Windows (¡NUEVO!)

**Resuelve problemas de Simplex con solo un clic derecho:**

1. **Instala el menú contextual** (solo una vez):

   - Navega a la carpeta `context_menu/`
   - Haz clic derecho en `install.bat`
   - Selecciona "Ejecutar como administrador"

2. **Usa el menú contextual**:
   - Crea un archivo `.txt` con tu problema de Simplex (ver ejemplos en `ejemplos/`)
   - Haz clic derecho en el archivo
   - Selecciona "Resolver con Simplex Solver"
   - ¡Listo! Se abrirá una ventana con la solución

📖 **Guía completa**: [docs/CONTEXT_MENU_GUIDE.md](docs/CONTEXT_MENU_GUIDE.md)  
📁 **Ejemplos**: [ejemplos/](ejemplos/)

### Desde Python

```python
from src.nlp import NLPConnectorFactory, NLPModelType

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

---

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

---

## Tipos de Problemas Soportados

- **Producción**: Maximizar ganancias con recursos limitados
- **Transporte**: Minimizar costos de distribución
- **Dieta**: Optimizar nutrición con presupuesto
- **Mezclas**: Combinar materias primas óptimamente
- **Asignación**: Distribuir recursos eficientemente

Ver ejemplos de archivos .txt en carpeta [`ejemplos/`](ejemplos/)  
Ver ejemplos de lenguaje natural en carpeta `ejemplos/nlp/`

---

## Configuración

### Cambiar Modelo

Editar `src/nlp/config.py`:

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

---

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

Ver GUIA_IA.md para más ayuda.

---

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

---

## Autor

- Francisco - [@frangcisneros](https://github.com/frangcisneros)
- Emiliana
- Marcelo
- Guillermo
- Lucia

---

## Soporte

- Documentación: ARQUITECTURA.md | GUIA_IA.md
- Issues: [GitHub Issues](https://github.com/frangcisneros/simplex-project/issues)

---

_Versión 3.0 - Octubre 2025_
