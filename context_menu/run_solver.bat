@echo off
:: Wrapper batch para ejecutar el solver desde el menú contextual

:: Verificar que se pasó un argumento
if "%~1"=="" (
    echo ERROR: No se proporciono un archivo
    pause
    exit /b 1
)

:: Obtener la ruta del archivo que se pasó como argumento
set "INPUT_FILE=%~1"

:: Obtener la ruta del proyecto (parent de context_menu)
set "SCRIPT_DIR=%~dp0"
set "PROJECT_DIR=%SCRIPT_DIR%.."
set "PYTHON_SCRIPT=%SCRIPT_DIR%solve_from_context.py"

:: Verificar que existe el script de Python
if not exist "%PYTHON_SCRIPT%" (
    echo ERROR: No se encontro el script solve_from_context.py
    echo Ruta esperada: %PYTHON_SCRIPT%
    pause
    exit /b 1
)

:: Cambiar al directorio del proyecto
cd /d "%PROJECT_DIR%"

:: Verificar que Python está disponible
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python no esta disponible en el PATH del sistema
    echo Por favor, instale Python o agregelo al PATH
    pause
    exit /b 1
)

:: Ejecutar el script de Python con el archivo como argumento
python "%PYTHON_SCRIPT%" "%INPUT_FILE%"

:: El script ya tiene su propio pause al final, pero por si acaso
if %errorlevel% neq 0 (
    echo.
    echo Hubo un error al ejecutar el script
    pause
)
