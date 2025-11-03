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

:: Eliminar las entradas del registro (Windows 10 y 11)
reg delete "HKEY_CLASSES_ROOT\txtfile\shell\SimplexSolver" /f 2>nul
reg delete "HKEY_CLASSES_ROOT\txtfile\shell\SimplexSolverAI" /f 2>nul
reg delete "HKEY_CLASSES_ROOT\SystemFileAssociations\.txt\shell\SimplexSolver" /f 2>nul
reg delete "HKEY_CLASSES_ROOT\SystemFileAssociations\.txt\shell\SimplexSolverAI" /f 2>nul

echo.
echo ===============================================
echo  DESINSTALACION COMPLETADA EXITOSAMENTE
echo ===============================================
echo.
echo El menu contextual ha sido desinstalado.
echo.
pause
