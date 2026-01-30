# Organizador de Terapias

**Última versión: 3.0.0**

Aplicación de escritorio para **Windows** que automatiza el flujo de trabajo con informes de terapia: toma el documento Word más reciente de una carpeta, pide un nombre al usuario, lo organiza en una estructura **Año → Mes → Día → Paciente**, abre Word para editarlo/guardar como PDF, y mueve el original a respaldo.

![Python](https://img.shields.io/badge/python-3.9+-blue.svg)
![Platform](https://img.shields.io/badge/platform-Windows-lightgrey.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## Características

- **Selector de carpeta:** En Inicio puedes elegir la carpeta donde buscar archivos .doc/.docx en cada uso (además de la carpeta por defecto en Configuración).
- **Interfaz moderna:** Sidebar con vistas **Inicio**, **Configuración**, **Historial** y **Buscar paciente** (CustomTkinter).
- **Confirmación explícita:** Antes de mover el archivo se muestra nombre, paciente, destino y se pide confirmación.
- **Regla "SS":** Extrae automáticamente el nombre del paciente; si falta "SS" puedes corregirlo.
- **Estructura organizada:** `Año/Mes/Día/Paciente`.
- **Respaldo con reintentos:** Hasta 3 intentos al mover el Word a la carpeta de respaldo.
- **Conversión automática a PDF:** Botón "Finalizar (PDF)" con win32com (opcional).
- **Historial y búsqueda:** Historial de archivos procesados y búsqueda de pacientes por nombre.
- **Modo claro/oscuro:** En Configuración puedes elegir Apariencia (Oscuro / Claro / Sistema).
- **Atajos de teclado:** `Ctrl+O` carpeta, `F5` o `Ctrl+Enter` organizar, `Ctrl+R` actualizar historial, `Ctrl+F` buscar.

## Requisitos

- **Windows**
- **Python 3.9+** (probado con 3.9–3.12; ver `requirements.txt`)
- **Microsoft Word** (para editar y guardar como PDF)
- Dependencias: `customtkinter`, `pywin32` (versiones mínimas en `requirements.txt`)

## Instalación

```bash
git clone https://github.com/tu-usuario/organizador-terapias.git
cd organizador-terapias
pip install -r requirements.txt
```

## Uso

### Opción 1: Ejecutar con Python

```bash
python terapias.py
```

La primera vez se creará `organizar_config.ini` (en la carpeta del script o en AppData si se ejecuta el .exe instalado). Edítalo o usa **Configuración** en la app para ajustar las carpetas.

### Opción 2: Ejecutable (.exe)

```bash
build_exe.bat
```

El ejecutable estará en `dist/terapias.exe`. Copia `organizar_config.ini.ejemplo` como `organizar_config.ini` en la misma carpeta (o en `%APPDATA%\OrganizadorTerapias` si usas el instalador) y ajusta las rutas.

### Opción 3: Instalador (Inno Setup)

```bash
build_exe.bat
build_installer.bat
```

Ver [QUICKSTART.md](QUICKSTART.md), [BUILD_INSTRUCTIONS.md](BUILD_INSTRUCTIONS.md) y [Preparar instalador con iconos](docs/PREPARAR_INSTALADOR.md) para más detalles.

## Configuración

Copia `organizar_config.ini.ejemplo` como `organizar_config.ini` (o edita el que se crea automáticamente) y ajusta las rutas:

```ini
[RUTAS]
source = C:\Users\TuUsuario\Documents\TERAPIAS\DOCUMENTOS PARA ARMAR
base_dest = C:\Users\TuUsuario\Documents\TERAPIAS\TERAPIAS
backup = C:\Users\TuUsuario\Documents\TERAPIAS\Respaldo
logfile = C:\Users\TuUsuario\Documents\TERAPIAS\organizar_log.txt
word_path = winword.exe
```

| Clave       | Descripción |
|-------------|-------------|
| **source**  | Carpeta por defecto para buscar .doc/.docx |
| **base_dest** | Raíz de destino: `AÑO\MM- MES\DD DE MES\PACIENTE` |
| **backup**  | Carpeta de respaldo del Word |
| **logfile** | Archivo de log (solo se lee al iniciar la aplicación; no se puede cambiar desde Configuración) |
| **word_path** | Ruta de Microsoft Word (opcional) |

- Si ejecutas desde **script**: el config se lee/escribe en la carpeta del script.
- Si ejecutas el **exe instalado**: el config se usa en `%APPDATA%\OrganizadorTerapias\organizar_config.ini`.
- **Nota sobre el log:** El archivo de log puede contener nombres de pacientes y rutas; conviene proteger el directorio donde se guarda (permisos, no compartir la carpeta sin control).

## Regla "SS" para el paciente

- **"Informe SS Juan Pérez"** → paciente: "Juan Pérez"
- **"Juan Pérez SS"** → paciente: "Juan Pérez"
- Sin "SS" → "PACIENTE_DESCONOCIDO" (la app te pregunta si quieres corregir)

## Tests

```bash
python -m unittest discover -s tests -v
# o
python run_tests.py
# o
python -m pytest tests/ -v
```

## Estructura del proyecto

```
organizador-terapias/
├── terapias.py              # Aplicación principal (UI unificada)
├── terapias_logic.py         # Lógica pura (testeable)
├── ui_components.py          # Componentes CustomTkinter (GlassFrame, etc.)
├── terapias.spec             # PyInstaller
├── build_exe.bat             # Generar .exe
├── build_installer.bat       # Generar instalador (Inno Setup)
├── installer.iss             # Script Inno Setup
├── image-removebg-preview.ico # Icono de la app
├── requirements.txt          # Dependencias Python
├── run_tests.py              # Ejecutar tests
├── organizar_config.ini.ejemplo
├── docs/                     # Documentación
├── tests/                    # Tests unitarios
├── QUICKSTART.md             # Inicio rápido
├── BUILD_INSTRUCTIONS.md     # Instrucciones de build e instalador
├── LICENSE
├── CONTRIBUTING.md
└── README.md
```

## Documentación

- [Análisis del proyecto](docs/ANALISIS_PROYECTO.md)
- [Fusión de proyectos](docs/FUSION_PROYECTOS.md)
- [Mejoras sugeridas](docs/MEJORAS_SUGERIDAS.md)
- [Mejoras adicionales](docs/MEJORAS_ADICIONALES.md)
- [Inicio rápido y build](QUICKSTART.md) · [Instrucciones de instalador](BUILD_INSTRUCTIONS.md)
- [Subir el proyecto a GitHub](docs/GITHUB_SETUP.md)

## Contribuir

Ver [CONTRIBUTING.md](CONTRIBUTING.md).

## Licencia

[MIT License](LICENSE)
