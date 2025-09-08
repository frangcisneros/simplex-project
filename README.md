# simplex-project

## Integrantes

- Marcelo Sola Bru
- Francisco Cisneros
- Emiliana Bianchi

## Descripción del Proyecto

Este proyecto consiste en el desarrollo de un software que resuelve problemas mediante el método simplex. El objetivo es crear una aplicación de consola interactiva que solicite al usuario los datos necesarios (variables, restricciones, función objetivo, etc.), procese la información y devuelva la solución óptima del problema de programación lineal.

## Tecnología Utilizada

- **Lenguaje:** Python
- **Framework:** Ninguno (aplicación de consola)

## Metodología Ágil

El desarrollo del proyecto se realizará utilizando la metodología ágil **Scrum**.

## Objetivos

- Implementar el método simplex para resolver problemas de programación lineal.
- Permitir que el programa se ejecute como un comando que reciba un archivo `.txt` con las variables y restricciones, y devuelva la solución de forma rápida y automática.
- A futuro, integrar inteligencia artificial para identificar automáticamente las variables y restricciones a partir de un enunciado en lenguaje natural.

## Instalación

1. Clona el repositorio:

```bash
git clone https://github.com/frangcisneros/simplex-project.git
cd simplex-project
```

2. Instala las dependencias:

```bash
pip install -r requirements.txt
```

## Estructura del proyecto

```
simplex-project/
├── src/                    # Código fuente
│   └── solver.py          # Implementación del método simplex
├── ejemplos/              # Archivos de ejemplo
│   ├── maximizar_basico.txt
│   ├── minimizar_simple.txt
│   ├── minimizar_3variables.txt
│   └── problema_produccion.txt
├── docs/                  # Documentación
│   └── guia_ejemplos.md   # Guía de ejemplos detallada
├── simplex.py            # Script principal
├── requirements.txt      # Dependencias de Python
└── README.md            # Este archivo
```

## Cómo ejecutar

### Modo 1: Archivo de entrada

Ejecuta el solver con un archivo que contenga el problema:

```bash
python simplex.py ejemplos/maximizar_basico.txt
```

### Modo 2: Interactivo

Ejecuta el solver en modo interactivo:

```bash
python simplex.py --interactive
```

o simplemente:

```bash
python simplex.py
```

## Formato del archivo de entrada

El archivo debe seguir este formato:

```
MAXIMIZE (o MINIMIZE)
c1 c2 c3 ... (coeficientes de la función objetivo)
SUBJECT TO
a11 a12 a13 ... <= b1
a21 a22 a23 ... <= b2
...
```

### Ejemplo (archivo ejemplos/maximizar_basico.txt):

```
MAXIMIZE
3 5
SUBJECT TO
1 0 <= 4
0 2 <= 12
3 2 <= 18
```

Este ejemplo maximiza 3x1 + 5x2 sujeto a:

- x1 ≤ 4
- 2x2 ≤ 12
- 3x1 + 2x2 ≤ 18
- x1, x2 ≥ 0

## Ejemplos disponibles

- `ejemplos/maximizar_basico.txt` - Problema básico de maximización
- `ejemplos/minimizar_simple.txt` - Problema simple de minimización
- `ejemplos/minimizar_3variables.txt` - Problema de minimización con 3 variables
- `ejemplos/problema_produccion.txt` - Problema real de planificación de producción

Para más detalles sobre cada ejemplo, consulta `docs/guia_ejemplos.md`.
