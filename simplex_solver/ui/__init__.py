"""
Paquete de interfaz de usuario.

Este paquete contiene componentes reutilizables para interfaces de consola.
Proporciona utilidades para formateo, colores y interacción con el usuario.

Módulos:
- console: Utilidades para interfaces de texto en consola con colores ANSI
"""

from simplex_solver.ui.console import ConsoleUI, ConsoleColors, enable_ansi_colors

# Lista de elementos públicos del paquete
__all__ = ["ConsoleUI", "ConsoleColors", "enable_ansi_colors"]
