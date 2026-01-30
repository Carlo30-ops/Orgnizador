# Build and Install Instructions

## Requisitos Previos

### 1. Instalar Dependencias Python
```bash
pip install -r requirements.txt
```

### 2. Instalar PyInstaller (si no está instalado)
```bash
pip install pyinstaller
```

### 3. Instalar Inno Setup
Descarga e instala Inno Setup desde: https://jrsoftware.org/isdl.php
- Versión recomendada: 6.0 o superior
- Durante la instalación, asegúrate de agregar Inno Setup al PATH del sistema

---

## Paso 1: Construir el Ejecutable

### Opción A: Usar el script batch (Recomendado)
```bash
build_exe.bat
```

### Opción B: Comando manual
```bash
pyinstaller --clean terapias.spec
```

Esto creará el ejecutable en: `dist/terapias.exe` y generará `version.txt` con la versión de `terapias.__version__` para mantener una sola fuente de verdad. Si actualizas la versión en el código, vuelve a ejecutar `build_exe.bat` antes de compilar el instalador; opcionalmente puedes sincronizar `MyAppVersion` en `installer.iss` con el valor de `version.txt`.

---

## Paso 2: Verificar el Ejecutable

Antes de crear el instalador, prueba que el ejecutable funcione:

```bash
cd dist
terapias.exe
```

Verifica:
- ✅ La aplicación se abre correctamente
- ✅ La interfaz se muestra sin errores
- ✅ Puedes acceder a Configuración, Historial, Buscar
- ✅ Los botones responden

---

## Paso 3: Crear el Instalador

### Opción A: Desde Inno Setup IDE
1. Abre Inno Setup Compiler
2. File → Open → Selecciona `installer.iss`
3. Build → Compile (o presiona Ctrl+F9)

### Opción B: Desde línea de comandos
```bash
build_installer.bat
```
o
```bash
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer.iss
```

El instalador se creará en: `installer_output/OrganizadorTerapias_Setup_v3.0.0.exe`

---

## Paso 4: Probar el Instalador

1. Ejecuta `OrganizadorTerapias_Setup_v3.0.0.exe`
2. Sigue el asistente de instalación
3. Configura las carpetas de trabajo (Origen, Destino, Respaldo)
4. Completa la instalación
5. Ejecuta la aplicación desde el acceso directo

---

## Estructura del Instalador

El instalador incluye:

- ✅ **Ejecutable principal** (`terapias.exe`)
- ✅ **Icono de la aplicación** (`image-removebg-preview.ico`)
- ✅ **Documentación** (README.md, LICENSE, CONTRIBUTING.md)
- ✅ **Carpeta docs** con documentación adicional
- ✅ **Configuración automática** en AppData (OrganizadorTerapias)
- ✅ **Accesos directos** en Menú Inicio y opcionalmente en Escritorio
- ✅ **Desinstalador** completo

---

## Solución de Problemas

### Error: "PyInstaller no encontrado"
```bash
pip install pyinstaller
```

### Error: "ISCC.exe no encontrado"
Ejecuta `build_installer.bat` (busca Inno Setup automáticamente) o instala Inno Setup y agrégalo al PATH.

### El ejecutable no se crea
1. Limpia builds anteriores: borra las carpetas `build` y `dist`
2. Vuelve a ejecutar: `build_exe.bat`

### Error al compilar el instalador
Verifica que existan en la raíz del proyecto:
- `dist/terapias.exe` (generado con `build_exe.bat`)
- `image-removebg-preview.ico` (icono del .exe y del instalador)
- `LICENSE`, `README.md`

Para una guía paso a paso con iconos, ver [docs/PREPARAR_INSTALADOR.md](docs/PREPARAR_INSTALADOR.md).

---

**Versión del instalador**: 3.0.0  
**Última actualización**: 2026-01-29
