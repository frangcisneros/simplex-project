@echo off
:: Script rápido para reinstalar el menú contextual de Simplex Solver.
:: Este script combina la desinstalación y la instalación en un solo paso.
:: Debe ejecutarse con permisos de administrador.

echo ===============================================
echo  REINSTALACION DE MENU CONTEXTUAL
echo ===============================================
echo.

:: Verificar permisos de administrador
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Este script requiere permisos de administrador.
    echo Por favor, ejecutelo haciendo clic derecho y "Ejecutar como administrador"
    pause
    exit /b 1
)

:: Paso 1: Llamar al script de desinstalación
echo Paso 1: Desinstalando configuracion anterior...
call "%~dp0uninstall.bat"

echo.
:: Paso 2: Llamar al script de instalación
echo Paso 2: Instalando nueva configuracion...
call "%~dp0install.bat"

echo.
echo ===============================================
echo  REINSTALACION COMPLETADA
echo ===============================================
echo.
pause
