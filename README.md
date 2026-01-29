# Organizador de Terapias

Aplicación de escritorio para **Windows** que automatiza el flujo de trabajo con informes de terapia: toma el documento Word más reciente de una carpeta, pide un nombre al usuario, lo organiza en una estructura **Año → Mes → Día → Paciente**, abre Word para editarlo/guardar como PDF, y mueve el original a respaldo.

![Python](https://img.shields.io/badge/python-3.9+-blue.svg)
![Platform](https://img.shields.io/badge/platform-Windows-lightgrey.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## Características

- **Selector de carpeta:** Elige dónde buscar archivos .doc/.docx
- **Ventana principal visible:** App de escritorio con área de estado
- **No se cierra si no hay archivos:** Muestra mensaje y permite reintentar
- **Regla "SS":** Extrae automáticamente el nombre del paciente
- **Estructura organizada:** `Año/Mes/Día/Paciente`
- **Respaldo automático:** Mueve el Word original a carpeta de backup

## Requisitos

- **Windows**
- **Python 3.9+** (para ejecutar el script)
- **Microsoft Word** (para editar y guardar como PDF)
- **Tkinter** (incluido con Python)

## Instalación

```bash
git clone https://github.com/tu-usuario/organizador-terapias.git
cd organizador-terapias
```

## Uso

### Opción 1: Ejecutar con Python

```bash
python terapias.py
```

La primera vez se creará `organizar_config.ini` con rutas por defecto. Edítalo para ajustar las carpetas.

### Opción 2: Ejecutable (.exe)

```bash
# Ejecutar el script de build
build_exe.bat
```

El ejecutable estará en `dist/terapias.exe`. Copia `organizar_config.ini.ejemplo` como `organizar_config.ini` y ajusta las rutas.

## Configuración

Copia `organizar_config.ini.ejemplo` como `organizar_config.ini` y edita las rutas:

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
| **logfile** | Archivo de log |
| **word_path** | Ruta de Microsoft Word (opcional) |

## Regla "SS" para el paciente

- **"Informe SS Juan Pérez"** → paciente: "Juan Pérez"
- **"Juan Pérez SS"** → paciente: "Juan Pérez"
- Sin "SS" → "PACIENTE_DESCONOCIDO"

## Tests

```bash
python -m unittest discover -s tests -v
# o
python run_tests.py
```

## Estructura del proyecto

```
organizador-terapias/
├── terapias.py              # Aplicación principal
├── terapias_logic.py         # Lógica pura (testeable)
├── terapias.spec             # PyInstaller
├── build_exe.bat             # Generar .exe
├── run_tests.py              # Ejecutar tests
├── organizar_config.ini.ejemplo  # Plantilla de configuración
├── docs/                     # Documentación
├── tests/                    # Tests unitarios
├── LICENSE
├── CONTRIBUTING.md
└── README.md
```

## Documentación

- [Análisis del proyecto](docs/ANALISIS_PROYECTO.md)
- [Mejoras sugeridas](docs/MEJORAS_SUGERIDAS.md)
- [Mejoras adicionales](docs/MEJORAS_ADICIONALES.md)

## Contribuir

Ver [CONTRIBUTING.md](CONTRIBUTING.md).

## Licencia

[MIT License](LICENSE)
