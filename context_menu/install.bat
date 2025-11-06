@echo off
setlocal enabledelayedexpansion
:: Script para instalar el menú contextual de Simplex Solver
:: Este script debe ejecutarse con permisos de administrador.

:: Mostrar encabezado informativo
echo ===============================================
echo  INSTALADOR DE MENU CONTEXTUAL - SIMPLEX SOLVER
echo ===============================================
echo.

:: Obtener la ruta del directorio del proyecto (padre de context_menu)
set "SCRIPT_DIR=%~dp0"  # Obtiene la ruta del directorio donde se encuentra este script.
set "PROJECT_DIR=%SCRIPT_DIR%.."  # Asume que el proyecto está en el directorio padre.
set "PYTHON_SCRIPT=%SCRIPT_DIR%solve_from_context.py"  # Ruta al script de Python principal.
set "BAT_WRAPPER=%SCRIPT_DIR%run_solver.bat"  # Ruta al archivo batch para resolver.
set "BAT_WRAPPER_AI=%SCRIPT_DIR%run_solver_ai.bat"  # Ruta al archivo batch para resolver con IA.
set "ICON_PATH=%SCRIPT_DIR%simplex_icon.ico"  # Ruta al icono del menú contextual.

:: Verificar que existe el script de Python
if not exist "%PYTHON_SCRIPT%" (
    echo ERROR: No se encontro el archivo solve_from_context.py
    echo Asegurese de ejecutar este script desde la carpeta context_menu.
    pause
    exit /b 1
)

:: Verificar que existe el wrapper batch para el método clásico
if not exist "%BAT_WRAPPER%" (
    echo ERROR: No se encontro el archivo run_solver.bat
    echo Asegurese de ejecutar este script desde la carpeta context_menu.
    pause
    exit /b 1
)

:: Verificar que existe el wrapper batch para el método con IA
if not exist "%BAT_WRAPPER_AI%" (
    echo ERROR: No se encontro el archivo run_solver_ai.bat
    echo Asegurese de ejecutar este script desde la carpeta context_menu.
    pause
    exit /b 1
)

:: Mostrar información de las rutas detectadas
echo Directorio del proyecto: %PROJECT_DIR%
echo Script de Python: %PYTHON_SCRIPT%
echo Wrapper Batch: %BAT_WRAPPER%
echo.

:: Verificar que Python está disponible en el sistema
echo Verificando Python...
where python >nul 2>&1  # Comprueba si el comando "python" está en el PATH.
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
    python --version  # Muestra la versión de Python detectada.
    echo Python detectado correctamente
)
echo.

:: Detectar versión de Windows
echo Detectando version de Windows...
for /f "tokens=4-5 delims=. " %%i in ('ver') do set VERSION=%%i.%%j  # Extrae la versión de Windows.
if "%VERSION%" == "10.0" (
    for /f "tokens=3" %%a in ('reg query "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion" /v CurrentBuild ^| findstr CurrentBuild') do set BUILD=%%a
    if !BUILD! GEQ 22000 (
        set "WIN_VERSION=11"  # Si el build es mayor o igual a 22000, es Windows 11.
        echo Windows 11 detectado ^(Build !BUILD!^)
    ) else (
        set "WIN_VERSION=10"  # De lo contrario, es Windows 10.
        echo Windows 10 detectado ^(Build !BUILD!^)
    )
) else (
    set "WIN_VERSION=10"  # Por defecto, se asume Windows 10.
    echo Windows %VERSION% detectado - usando modo Windows 10
)
echo.

:: Verificar permisos de administrador
net session >nul 2>&1  # Comprueba si el script tiene permisos de administrador.
if %errorlevel% neq 0 (
    echo ADVERTENCIA: Este script requiere permisos de administrador.
    echo Por favor, ejecutelo haciendo clic derecho y "Ejecutar como administrador"
    pause
    exit /b 1
)

:: Agregar entradas al Registro de Windows
echo Agregando entrada al Registro de Windows...
echo.

:: Registrar para Windows 10 (funciona en todas las versiones)
echo Registrando para compatibilidad con Windows 10...
reg add "HKEY_CLASSES_ROOT\txtfile\shell\SimplexSolver" /ve /d "Resolver con Simplex Solver" /f
reg add "HKEY_CLASSES_ROOT\txtfile\shell\SimplexSolver\command" /ve /d "\"%BAT_WRAPPER%\" \"%%1\"" /f

:: Agregar opción con IA
reg add "HKEY_CLASSES_ROOT\txtfile\shell\SimplexSolverAI" /ve /d "Resolver con Simplex Solver (IA)" /f
reg add "HKEY_CLASSES_ROOT\txtfile\shell\SimplexSolverAI\command" /ve /d "\"%BAT_WRAPPER_AI%\" \"%%1\"" /f

:: Si es Windows 11, agregar también a SystemFileAssociations
if "%WIN_VERSION%"=="11" (
    echo Registrando para Windows 11...
    reg add "HKEY_CLASSES_ROOT\SystemFileAssociations\.txt\shell\SimplexSolver" /ve /d "Resolver con Simplex Solver" /f
    reg add "HKEY_CLASSES_ROOT\SystemFileAssociations\.txt\shell\SimplexSolver\command" /ve /d "\"%BAT_WRAPPER%\" \"%%1\"" /f
    
    reg add "HKEY_CLASSES_ROOT\SystemFileAssociations\.txt\shell\SimplexSolverAI" /ve /d "Resolver con Simplex Solver (IA)" /f
    reg add "HKEY_CLASSES_ROOT\SystemFileAssociations\.txt\shell\SimplexSolverAI\command" /ve /d "\"%BAT_WRAPPER_AI%\" \"%%1\"" /f
)

:: Si hay un icono, agregarlo
if exist "%ICON_PATH%" (
    reg add "HKEY_CLASSES_ROOT\txtfile\shell\SimplexSolver" /v "Icon" /d "%ICON_PATH%" /f
    reg add "HKEY_CLASSES_ROOT\txtfile\shell\SimplexSolverAI" /v "Icon" /d "%ICON_PATH%" /f
    if "%WIN_VERSION%"=="11" (
        reg add "HKEY_CLASSES_ROOT\SystemFileAssociations\.txt\shell\SimplexSolver" /v "Icon" /d "%ICON_PATH%" /f
        reg add "HKEY_CLASSES_ROOT\SystemFileAssociations\.txt\shell\SimplexSolverAI" /v "Icon" /d "%ICON_PATH%" /f
    )
    echo Icono configurado
)

echo.
echo ===============================================
echo  INSTALACION COMPLETADA EXITOSAMENTE
echo ===============================================
echo.
echo El menu contextual ha sido instalado para Windows %WIN_VERSION%.
echo.
if "%WIN_VERSION%"=="11" (
    echo NOTA: En Windows 11, si no ves la opcion al hacer clic derecho:
    echo   1. Presiona Shift + Clic derecho
    echo   2. O selecciona "Mostrar mas opciones"
    echo.
)
echo Ahora puede hacer clic derecho en cualquier archivo .txt y ver:
echo   - "Resolver con Simplex Solver" (metodo clasico)
echo   - "Resolver con Simplex Solver (IA)" (usa lenguaje natural)
echo.
echo NOTA: Para usar IA, asegurese de tener Ollama instalado y corriendo.
echo.
pause
