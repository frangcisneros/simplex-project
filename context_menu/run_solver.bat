@echo off
:: Wrapper batch para ejecutar el solver desde el menú contextual.
:: Este script se asegura de que se cumplan todas las dependencias y ejecuta el script de Python correspondiente.

:: Verificar que se pasó un argumento
if "%~1"=="" (
    echo ERROR: No se proporciono un archivo  # Asegura que el usuario pase un archivo como argumento.
    pause
    exit /b 1
)

:: Obtener la ruta del archivo que se pasó como argumento
set "INPUT_FILE=%~1"  # Guarda la ruta del archivo proporcionado como argumento.

:: Obtener la ruta del proyecto (padre de context_menu)
set "SCRIPT_DIR=%~dp0"  # Obtiene la ruta del directorio donde se encuentra este script.
set "PROJECT_DIR=%SCRIPT_DIR%.."  # Asume que el proyecto está en el directorio padre.
set "PYTHON_SCRIPT=%SCRIPT_DIR%solve_from_context.py"  # Ruta al script de Python para resolver problemas.

:: Verificar que existe el script de Python
if not exist "%PYTHON_SCRIPT%" (
    echo ERROR: No se encontro el script solve_from_context.py  # Asegura que el script de Python requerido exista.
    echo Ruta esperada: %PYTHON_SCRIPT%
    pause
    exit /b 1
)

:: Cambiar al directorio del proyecto
cd /d "%PROJECT_DIR%"  # Cambia al directorio del proyecto para garantizar que las rutas relativas funcionen correctamente.

:: Verificar que Python está disponible
echo Verificando disponibilidad de Python...
where python >nul 2>&1  # Comprueba si el comando "python" está en el PATH.
if %errorlevel% neq 0 (
    echo ERROR: Python no esta disponible en el PATH del sistema  # Informa si Python no está configurado correctamente.
    echo Por favor, instale Python o agregelo al PATH
    pause
    exit /b 1
)

:: Ejecutar el script de Python con el archivo como argumento
echo Ejecutando el script de Python...
python "%PYTHON_SCRIPT%" "%INPUT_FILE%"  # Llama al script de Python con el archivo proporcionado como argumento.

:: Manejar errores en la ejecución del script
if %errorlevel% neq 0 (
    echo.
    echo Hubo un error al ejecutar el script  # Informa si hubo un error durante la ejecución del script de Python.
    pause
)
