@echo off
:: Script para desinstalar el menú contextual de Simplex Solver
:: Ejecutar como Administrador

echo ===============================================
echo  DESINSTALADOR DE MENU CONTEXTUAL - SIMPLEX SOLVER
echo ===============================================
echo.

:: Verificar permisos de administrador
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo ADVERTENCIA: Este script requiere permisos de administrador.
    echo Por favor, ejecutelo haciendo clic derecho y "Ejecutar como administrador"
    pause
    exit /b 1
)

echo Eliminando entrada del Registro de Windows...
echo.

:: Eliminar la entrada del registro
reg delete "HKEY_CLASSES_ROOT\txtfile\shell\SimplexSolver" /f

echo.
echo ===============================================
echo  DESINSTALACION COMPLETADA EXITOSAMENTE
echo ===============================================
echo.
echo El menu contextual ha sido desinstalado.
echo.
pause
