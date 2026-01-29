@echo off
chcp 65001 >nul
setlocal EnableDelayedExpansion

:: Ir al directorio del script
cd /d "%~dp0"

echo ========================================
echo   Organizador de Terapias - Build
echo ========================================
echo.

:: 1. Verificar Python
echo [1/4] Verificando Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python no encontrado. Instala Python desde python.org
    pause
    exit /b 1
)
python --version
echo.

:: 2. Instalar dependencias (PyInstaller)
echo [2/4] Instalando dependencias...
python -m pip install --upgrade pip --quiet
python -m pip install pyinstaller --quiet
if errorlevel 1 (
    echo ERROR: No se pudo instalar PyInstaller
    pause
    exit /b 1
)
echo PyInstaller instalado correctamente.
echo.

:: 3. Limpiar build anterior (opcional, evita artefactos obsoletos)
echo [3/4] Limpiando build anterior...
if exist "build" rmdir /s /q "build"
echo.

:: 4. Generar el ejecutable
echo [4/4] Generando terapias.exe...
python -m PyInstaller --noconfirm --clean terapias.spec
if errorlevel 1 (
    echo ERROR: Fallo al generar el ejecutable
    pause
    exit /b 1
)

:: Copiar configuracion a dist
echo.
echo Copiando configuracion...
if exist "organizar_config.ini" (
    copy /Y "organizar_config.ini" "dist\organizar_config.ini" >nul
    echo   - organizar_config.ini copiado
) else (
    if exist "organizar_config.ini.ejemplo" (
        copy "organizar_config.ini.ejemplo" "dist\organizar_config.ini" >nul
        echo   - Plantilla organizar_config.ini.ejemplo copiada como organizar_config.ini
    )
)
if not exist "dist\organizar_config.ini" (
    echo   - ADVERTENCIA: No hay organizar_config.ini en dist. Crea uno manualmente.
)

echo.
echo ========================================
echo   Build completado
echo ========================================
echo.
echo Ejecutable: dist\terapias.exe
echo Config:     dist\organizar_config.ini
echo.
echo Para distribuir: copia la carpeta dist completa.
echo.
pause
