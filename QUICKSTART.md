# Quick Start Guide - Organizador de Terapias

## 🚀 Inicio Rápido para Desarrolladores

### 1. Instalar Dependencias
```bash
pip install -r requirements.txt
```

### 2. Ejecutar Aplicación
```bash
python terapias.py
```

---

## 📦 Crear Distribución Completa

### Paso 1: Construir Ejecutable
```bash
build_exe.bat
```

Esto creará: `dist/terapias.exe`

### Paso 2: Compilar Instalador
```bash
build_installer.bat
```

Esto creará: `installer_output/OrganizadorTerapias_Setup_v3.0.0.exe`

---

## ✅ Verificación Rápida

### Ejecutar Tests
```bash
python -m pytest tests/ -v
```
o
```bash
python run_tests.py
```

### Probar Ejecutable
```bash
cd dist
terapias.exe
```

---

## 📋 Requisitos

- **Python 3.9+** (3.12+ recomendado para desarrollo)
- **Microsoft Word** (para conversión PDF)
- **Inno Setup 6.0+** (para crear instalador)

---

## 🔧 Solución Rápida de Problemas

### Error: "pywin32 not found"
```bash
pip install pywin32
```

### Error: "ISCC.exe not found"
Instalar Inno Setup desde: https://jrsoftware.org/isdl.php

### Error: "Permission denied" al compilar
Cerrar todas las instancias de `terapias.exe`:
```bash
taskkill /F /IM terapias.exe
```

---

## 📚 Documentación Completa

Ver [BUILD_INSTRUCTIONS.md](BUILD_INSTRUCTIONS.md) para instrucciones detalladas.

---

**Versión**: 3.0.0
