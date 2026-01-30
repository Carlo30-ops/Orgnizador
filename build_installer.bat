@echo off
REM Script para compilar el instalador con Inno Setup (con iconos)
REM Requiere Inno Setup 6.0 o superior - https://jrsoftware.org/isdl.php
cd /d "%~dp0"

echo ========================================
echo Compilador de Instalador - Organizador de Terapias
echo ========================================
echo.

if not exist "dist\terapias.exe" (
    echo [ERROR] No se encuentra dist\terapias.exe
    echo Primero ejecuta: build_exe.bat
    exit /b 1
)
if not exist "image-removebg-preview.ico" (
    echo [ERROR] No se encuentra image-removebg-preview.ico en la raiz del proyecto.
    echo Copia el icono desde Orgnizador-main\image-removebg-preview.ico
    echo Ver docs\PREPARAR_INSTALADOR.md
    exit /b 1
)
echo [OK] dist\terapias.exe y icono encontrados.

set ISCC_PATH=
if exist "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" set ISCC_PATH="C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
if exist "C:\Program Files\Inno Setup 6\ISCC.exe" set ISCC_PATH="C:\Program Files\Inno Setup 6\ISCC.exe"

if %ISCC_PATH%=="" (
    echo [ERROR] No se encuentra Inno Setup (ISCC.exe). Instala desde https://jrsoftware.org/isdl.php
    exit /b 1
)

if not exist "installer_output" mkdir installer_output
echo Compilando instalador...
%ISCC_PATH% "installer.iss"
if %ERRORLEVEL% EQU 0 (
    echo [OK] Instalador creado en installer_output\OrganizadorTerapias_Setup_v3.0.0.exe
) else (
    echo [ERROR] Fallo al compilar el instalador
    exit /b 1
)
