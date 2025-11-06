@echo off
:: Wrapper batch para ejecutar el solver desde el menú contextual.
:: Este script se asegura de que se cumplan todas las dependencias y ejecuta el script de Python correspondiente.

:: Verificar que se pasó un argumento
if "%~1"=="" (
    echo ERROR: No se proporciono un archivo
    pause
    exit /b 1
)

:: Obtener la ruta del archivo que se pasó como argumento
set "INPUT_FILE=%~1"

:: Obtener la ruta del proyecto (padre de context_menu)
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

:: Intentar encontrar Python en diferentes ubicaciones
set "PYTHON_EXE="

:: 1. Intentar python en PATH
where python >nul 2>&1
if %errorlevel% equ 0 (
    set "PYTHON_EXE=python"
    goto :found_python
)

:: 2. Intentar py launcher de Windows
where py >nul 2>&1
if %errorlevel% equ 0 (
    set "PYTHON_EXE=py"
    goto :found_python
)

:: 3. Buscar en ubicaciones comunes de Windows
if exist "C:\Python314\python.exe" (
    set "PYTHON_EXE=C:\Python314\python.exe"
    goto :found_python
)

if exist "C:\Python313\python.exe" (
    set "PYTHON_EXE=C:\Python313\python.exe"
    goto :found_python
)

if exist "C:\Python312\python.exe" (
    set "PYTHON_EXE=C:\Python312\python.exe"
    goto :found_python
)

if exist "C:\Python311\python.exe" (
    set "PYTHON_EXE=C:\Python311\python.exe"
    goto :found_python
)

if exist "%LOCALAPPDATA%\Programs\Python\Python314\python.exe" (
    set "PYTHON_EXE=%LOCALAPPDATA%\Programs\Python\Python314\python.exe"
    goto :found_python
)

if exist "%LOCALAPPDATA%\Programs\Python\Python313\python.exe" (
    set "PYTHON_EXE=%LOCALAPPDATA%\Programs\Python\Python313\python.exe"
    goto :found_python
)

if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" (
    set "PYTHON_EXE=%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
    goto :found_python
)

:: Si no se encontró Python
echo.
echo ================================================================
echo ERROR: Python no esta instalado o no se encuentra en el sistema
echo ================================================================
echo.
echo Por favor instale Python desde: https://www.python.org/
echo O agregue Python al PATH del sistema
echo.
pause
exit /b 1

:found_python
echo Python encontrado: %PYTHON_EXE%
echo.

:: Ejecutar el script de Python con el archivo como argumento
echo Ejecutando Simplex Solver...
echo ================================================================
echo.
"%PYTHON_EXE%" "%PYTHON_SCRIPT%" "%INPUT_FILE%"

:: Capturar el código de salida
set EXIT_CODE=%errorlevel%

:: Si hubo error, mostrar mensaje adicional
if %EXIT_CODE% neq 0 (
    echo.
    echo ================================================================
    echo ERROR: El script termino con codigo de error %EXIT_CODE%
    echo ================================================================
    echo.
    pause
    exit /b %EXIT_CODE%
)

exit /b 0
