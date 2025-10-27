@echo off
setlocal enabledelayedexpansion
:: Script para instalar el menú contextual de Simplex Solver
:: Ejecutar como Administrador

echo ===============================================
echo  INSTALADOR DE MENU CONTEXTUAL - SIMPLEX SOLVER
echo ===============================================
echo.

:: Obtener la ruta del directorio del proyecto (parent de context_menu)
set "SCRIPT_DIR=%~dp0"
set "PROJECT_DIR=%SCRIPT_DIR%.."
set "PYTHON_SCRIPT=%SCRIPT_DIR%solve_from_context.py"
set "BAT_WRAPPER=%SCRIPT_DIR%run_solver.bat"
set "ICON_PATH=%SCRIPT_DIR%simplex_icon.ico"

:: Verificar que existe el script de Python
if not exist "%PYTHON_SCRIPT%" (
    echo ERROR: No se encontro el archivo solve_from_context.py
    echo Asegurese de ejecutar este script desde la carpeta context_menu.
    pause
    exit /b 1
)

:: Verificar que existe el wrapper batch
if not exist "%BAT_WRAPPER%" (
    echo ERROR: No se encontro el archivo run_solver.bat
    echo Asegurese de ejecutar este script desde la carpeta context_menu.
    pause
    exit /b 1
)

echo Directorio del proyecto: %PROJECT_DIR%
echo Script de Python: %PYTHON_SCRIPT%
echo Wrapper Batch: %BAT_WRAPPER%
echo.

:: Verificar que Python está disponible
echo Verificando Python...
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo ADVERTENCIA: Python no esta en el PATH del sistema.
    echo Asegurese de que Python esta instalado y accesible desde la linea de comandos.
    echo.
    set /p continue="Desea continuar de todas formas? (S/N): "
    if /i not "!continue!"=="S" (
        echo Instalacion cancelada.
        pause
        exit /b 1
    )
) else (
    python --version
    echo Python detectado correctamente
)
echo.

:: Verificar permisos de administrador
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo ADVERTENCIA: Este script requiere permisos de administrador.
    echo Por favor, ejecutelo haciendo clic derecho y "Ejecutar como administrador"
    pause
    exit /b 1
)

echo Agregando entrada al Registro de Windows...
echo.

:: Crear la entrada en el registro para archivos .txt
:: Usamos el wrapper .bat en lugar de llamar directamente a Python
reg add "HKEY_CLASSES_ROOT\txtfile\shell\SimplexSolver" /ve /d "Resolver con Simplex Solver" /f
reg add "HKEY_CLASSES_ROOT\txtfile\shell\SimplexSolver\command" /ve /d "\"%BAT_WRAPPER%\" \"%%1\"" /f

:: Si hay un icono, agregarlo
if exist "%ICON_PATH%" (
    reg add "HKEY_CLASSES_ROOT\txtfile\shell\SimplexSolver" /v "Icon" /d "%ICON_PATH%" /f
    echo Icono configurado
)

echo.
echo ===============================================
echo  INSTALACION COMPLETADA EXITOSAMENTE
echo ===============================================
echo.
echo El menu contextual ha sido instalado.
echo Ahora puede hacer clic derecho en cualquier archivo .txt
echo y seleccionar "Resolver con Simplex Solver"
echo.
pause
