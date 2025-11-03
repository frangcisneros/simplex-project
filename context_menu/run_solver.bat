@echo off
:: Wrapper batch para ejecutar el solver desde el menú contextual

:: Obtener la ruta del archivo que se pasó como argumento
set "INPUT_FILE=%~1"

:: Obtener la ruta del proyecto (parent de context_menu)
set "SCRIPT_DIR=%~dp0"
set "PROJECT_DIR=%SCRIPT_DIR%.."

:: Cambiar al directorio del proyecto y ejecutar con --pdf opcional
cd /d "%PROJECT_DIR%"
python simplex.py "%INPUT_FILE%"

pause
