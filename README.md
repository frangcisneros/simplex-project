# Simplex Solver

Este programa resuelve problemas de programación lineal usando el método Simplex.

## Uso rápido

1. Coloca tu problema en un archivo de texto. Ejemplo:

```
MAXIMIZE
3 5
SUBJECT TO
1 0 <= 4
0 2 <= 12
3 2 <= 18
```

2. Ejecuta desde la terminal:

```
python simplex.py archivo.txt
```

3. También puedes usar el modo interactivo:

```
python simplex.py --interactive
```

## Problemas en lenguaje natural

Puedes resolver problemas escritos en español usando:

```
python nlp_simplex.py --nlp --file ejemplos/nlp/problema_produccion_simple.txt
```

O escribir el texto directamente:

```
python nlp_simplex.py --nlp --text "Maximizar 3x + 2y sujeto a x + y <= 4"
```

## Instalación

1. Instala las dependencias:

```
pip install -r requirements.txt
```

2. (Opcional) Para procesamiento de texto avanzado:

```
pip install torch transformers accelerate
```

## Ejemplo de salida

El programa muestra la solución óptima y los valores de las variables.

## Archivos de ejemplo

Revisa la carpeta `ejemplos/` para ver formatos y casos de prueba.
