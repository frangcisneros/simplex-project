@echo off
:: Script rápido para reinstalar el menú contextual
:: Ejecutar como Administrador

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

echo Paso 1: Desinstalando configuracion anterior...
call "%~dp0uninstall.bat"

echo.
echo Paso 2: Instalando nueva configuracion...
call "%~dp0install.bat"

echo.
echo ===============================================
echo  REINSTALACION COMPLETADA
echo ===============================================
echo.
pause
