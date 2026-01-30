# Preparar y ejecutar el instalador .iss (con iconos)

Guía para generar el instalador de **Organizador de Terapias** con Inno Setup, usando iconos en el .exe y en el instalador.

---

## Requisitos previos

1. **Python 3.9+** con dependencias instaladas:
   ```bash
   pip install -r requirements.txt
   pip install pyinstaller
   ```

2. **Inno Setup 6.0 o superior**  
   Descarga: https://jrsoftware.org/isdl.php  
   Durante la instalación, opción de agregar al PATH recomendada.

3. **Icono en la raíz del proyecto**  
   Debe existir el archivo:
   - `image-removebg-preview.ico`  
   Si no está, cópialo desde `Orgnizador-main\image-removebg-preview.ico` a la raíz del proyecto.

---

## Pasos para generar el instalador

### Paso 1: Generar el ejecutable (con icono)

Desde la raíz del proyecto:

```bash
build_exe.bat
```

- Crea `dist\terapias.exe`.
- Si existe `image-removebg-preview.ico` en la raíz, el .exe usará ese icono (barra de tareas, ventana, acceso directo).

### Paso 2: Compilar el instalador .iss

```bash
build_installer.bat
```

- Usa Inno Setup para compilar `installer.iss`.
- Genera: `installer_output\OrganizadorTerapias_Setup_v3.0.0.exe`.

### Verificación rápida

Antes de ejecutar el instalador, comprueba:

| Elemento | Ubicación |
|----------|-----------|
| Ejecutable | `dist\terapias.exe` |
| Icono | `image-removebg-preview.ico` (raíz) |
| Script Inno | `installer.iss` (raíz) |

Si falta el icono, el instalador puede fallar al compilar; el .exe se generará igual pero sin icono propio.

---

## Uso de iconos en el proyecto

| Uso | Dónde se configura |
|-----|---------------------|
| Icono del .exe (ventana, barra de tareas) | `terapias.spec` → parámetro `icon=` |
| Icono del instalador (ventana del setup) | `installer.iss` → `SetupIconFile=image-removebg-preview.ico` |
| Icono en Menú Inicio / Escritorio | `installer.iss` → `[Icons]` → `IconFilename: "{app}\image-removebg-preview.ico"` |
| Icono del desinstalador | `installer.iss` → `UninstallDisplayIcon={app}\terapias.exe` (hereda del .exe) |

El archivo `image-removebg-preview.ico` se copia a la carpeta de instalación para que los accesos directos sigan mostrando el icono.

---

## Solución de problemas

- **"No se encuentra dist\terapias.exe"**  
  Ejecuta antes `build_exe.bat`.

- **"No se encuentra Inno Setup (ISCC.exe)"**  
  Instala Inno Setup 6 y, si hace falta, ejecuta el instalador desde la ruta completa, por ejemplo:
  `"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer.iss`

- **Error de compilación por icono**  
  Comprueba que `image-removebg-preview.ico` existe en la raíz y que es un .ico válido.

- **Cambiar versión del instalador**  
  Edita `installer.iss` y modifica la línea:
  `#define MyAppVersion "3.0.0"`

---

## Resumen de archivos implicados

```
raíz del proyecto/
├── image-removebg-preview.ico   ← Icono (obligatorio para instalador con iconos)
├── installer.iss               ← Script Inno Setup
├── build_exe.bat               ← Genera dist\terapias.exe
├── build_installer.bat         ← Compila installer.iss
├── terapias.spec               ← Incluye icono para el .exe
└── dist/
    └── terapias.exe            ← Generado por build_exe.bat
```

Salida del instalador:

```
installer_output/
└── OrganizadorTerapias_Setup_v3.0.0.exe
```
