@echo off
:: Script para desinstalar el menú contextual de Simplex Solver.
:: Este script elimina las entradas del registro asociadas al menú contextual.
:: Debe ejecutarse con permisos de administrador.

echo ===============================================
echo  DESINSTALADOR DE MENU CONTEXTUAL - SIMPLEX SOLVER
echo ===============================================
echo.

:: Verificar permisos de administrador
net session >nul 2>&1  # Comprueba si el script tiene permisos de administrador.
if %errorlevel% neq 0 (
    echo ADVERTENCIA: Este script requiere permisos de administrador.
    echo Por favor, ejecutelo haciendo clic derecho y "Ejecutar como administrador"
    pause
    exit /b 1
)

:: Eliminar las entradas del registro asociadas al menú contextual
echo Eliminando entrada del Registro de Windows...
echo.

:: Eliminar las entradas del registro para Windows 10 y 11
reg delete "HKEY_CLASSES_ROOT\txtfile\shell\SimplexSolver" /f 2>nul  # Elimina la entrada para "Resolver con Simplex Solver".
reg delete "HKEY_CLASSES_ROOT\txtfile\shell\SimplexSolverAI" /f 2>nul  # Elimina la entrada para "Resolver con Simplex Solver (IA)".
reg delete "HKEY_CLASSES_ROOT\SystemFileAssociations\.txt\shell\SimplexSolver" /f 2>nul  # Elimina la entrada para Windows 11 (clásico).
reg delete "HKEY_CLASSES_ROOT\SystemFileAssociations\.txt\shell\SimplexSolverAI" /f 2>nul  # Elimina la entrada para Windows 11 (IA).

echo.
echo ===============================================
echo  DESINSTALACION COMPLETADA EXITOSAMENTE
echo ===============================================
echo.
echo El menu contextual ha sido desinstalado.
echo.
pause  # Pausa para que el usuario pueda leer el mensaje final antes de cerrar la ventana.
