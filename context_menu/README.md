# Menú Contextual de Windows - Simplex Solver

Esta carpeta contiene los archivos necesarios para integrar el Simplex Solver con el menú contextual de Windows.

## 📁 Contenido

- **`solve_from_context.py`**: Script principal que se ejecuta desde el menú contextual
- **`run_solver.bat`**: Wrapper batch que ejecuta el script de Python
- **`install.bat`**: Instalador automático del menú contextual
- **`uninstall.bat`**: Desinstalador del menú contextual
- **`simplex_icon.ico`**: Icono para el menú contextual (opcional)

## 🚀 Instalación Rápida

1. Haz clic derecho en **`install.bat`**
2. Selecciona **"Ejecutar como administrador"**
3. Sigue las instrucciones en pantalla

## 📖 Documentación Completa

Para una guía detallada de instalación, uso y solución de problemas, consulta:

👉 **[docs/CONTEXT_MENU_GUIDE.md](../docs/CONTEXT_MENU_GUIDE.md)**

## 🔧 Uso

Una vez instalado:

1. Haz clic derecho en cualquier archivo `.txt` con un problema de Simplex
2. Selecciona **"Resolver con Simplex Solver"**
3. Se abrirá una ventana con la solución

## 🗑️ Desinstalación

1. Haz clic derecho en **`uninstall.bat`**
2. Selecciona **"Ejecutar como administrador"**

## 📝 Formato de Archivos

Los archivos `.txt` deben seguir este formato:

```
MAXIMIZE
3 2
SUBJECT TO
2 1 <= 18
2 3 <= 42
3 1 <= 24
```

Ver ejemplos en la carpeta **`ejemplos/`**
