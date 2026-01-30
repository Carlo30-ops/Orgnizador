# Análisis: Cómo combinar el proyecto actual y Orgnizador-main

Este documento resume lo mejor de cada proyecto y propone una estrategia de fusión en un solo código base.

---

## 1. Resumen de cada proyecto

### Proyecto actual (raíz del workspace)

| Aspecto | Detalle |
|--------|--------|
| **UI** | Tkinter estándar, tema claro (teal/verde), ventana única |
| **Config** | `organizar_config.ini` en la carpeta del ejecutable o del script |
| **Log** | Rotación manual (`_rotate_log_if_needed`) + escritura con `log_action()` |
| **Flujo** | Selector de carpeta en ventana → Buscar último .doc/.docx → Pedir nombre → Confirmar → Mover → Abrir Word (**/WAIT**) → Recordatorios PDF → Mover original a respaldo con **reintentos** (3) |
| **Dependencias** | Solo estándar (tkinter, configparser, etc.) |
| **Build** | `terapias.spec` mínimo (solo `terapias_logic`) |
| **Tests** | `test_terapias_logic`, `test_integration` |

**Puntos fuertes:**
- El usuario puede **elegir la carpeta de búsqueda** en cada ejecución (no solo en configuración).
- **Confirmación explícita** antes de mover el archivo (nombre, paciente, destino).
- Word se abre con `start /WAIT`, y hay **recordatorios** para guardar como PDF; flujo claro sin depender de automatización.
- **Respaldo con reintentos** (hasta 3) si falla el movimiento al backup.
- Mensajes de estado detallados y validación de longitud de ruta.
- Sin dependencias extra: funciona en cualquier Python con Tkinter.
- README con **tabla de configuración** (incluye `logfile`).

---

### Orgnizador-main

| Aspecto | Detalle |
|--------|--------|
| **UI** | CustomTkinter + `ui_components` (VisionSys, GlassFrame, FloatingButton, etc.), tema oscuro, **sidebar** con vistas |
| **Config** | `organizar_config.ini` en **AppData** (`%APPDATA%\OrganizadorTerapias`) para evitar permisos en Program Files |
| **Log** | `logging` estándar con `RotatingFileHandler` |
| **Vistas** | Inicio (Home), Configuración, Historial, Buscar paciente |
| **Flujo** | Carpeta fija (config) → Buscar → Pedir nombre → Validación SS (corregir si falta) → Mover → Abrir Word → Botón **"Finalizar (PDF)"** con **conversión automática** vía `win32com` |
| **Dependencias** | `customtkinter`, `packaging`, `pywin32` |
| **Build** | `terapias.spec` con CustomTkinter, `ui_components`, `win32com`; **Inno Setup** (`installer.iss`), icono, `build_installer.bat` |
| **Docs** | `QUICKSTART.md`, `BUILD_INSTRUCTIONS.md` |
| **Tests** | `test_terapias_logic`, `test_integration`, `test_features`, `test_pdf_conversion` |

**Puntos fuertes:**
- **Interfaz moderna** (sidebar, tarjetas, botones con estilo).
- **Configuración desde la app** (ConfigView) y guardado en AppData adecuado para instalador.
- **Historial** de archivos procesados (HistoryView) leyendo el log.
- **Búsqueda de pacientes** (SearchView) por nombre en la estructura Año/Mes/Día.
- **Conversión automática Word → PDF** con `win32com` (opción “Finalizar (PDF)”).
- **Instalador** completo (Inno Setup), icono, documentación de build y quickstart.
- Más **cobertura de tests** (incl. PDF y características).

**Problema detectado:** En `HomeView`, se usa `self.btn_open_folder` en `run_organize()` pero no se crea en `__init__`; eso provocará error al pulsar “Buscar y Organizar”.

---

## 2. Qué tomar de cada uno

### Del proyecto actual

1. **Selector de carpeta** en la ventana principal (no solo carpeta por defecto de config).
2. **Confirmación clara** antes de mover (archivo, nombre, paciente, destino).
3. **Abrir Word con `/WAIT`** y recordatorios para guardar como PDF (para quien no use conversión automática).
4. **Respaldo con reintentos** (p. ej. 3 intentos) antes de dar error.
5. **Log con rotación** (puede mantenerse estilo actual o unificar con `RotatingFileHandler`).
6. **Mensajes de estado** detallados en cada paso.
7. **Tabla de configuración** en README (incl. `logfile`, `word_path`).
8. Opción de **config en carpeta del ejecutable** cuando se corre sin instalador (documentado).

### De Orgnizador-main

1. **UI con CustomTkinter y `ui_components`** (sidebar, vistas, GlassCard, etc.).
2. **Configuración desde la app** (ConfigView) y **AppData** cuando se instala con instalador.
3. **Historial** (HistoryView) y **búsqueda de pacientes** (SearchView).
4. **Conversión automática a PDF** (`convert_doc_to_pdf`) como opción “Finalizar (PDF)”.
5. **requirements.txt**, **QUICKSTART.md**, **BUILD_INSTRUCTIONS.md**.
6. **Instalador** (Inno Setup), **icono**, **build_installer.bat**.
7. **Tests** adicionales: `test_features`, `test_pdf_conversion`.
8. **terapias.spec** que incluya CustomTkinter, `ui_components` y `pywin32`.

---

## 3. Estrategia de fusión recomendada

### 3.1 Base de código

- **Mantener una sola rama de código** en la raíz del workspace (no dentro de `Orgnizador-main`).
- **`terapias_logic.py`** queda igual en ambos; usarlo como única fuente de lógica pura.

### 3.2 Frontend (terapias.py)

- **Base:** estructura de Orgnizador-main (CustomTkinter, sidebar, vistas).
- **HomeView:**
  - Añadir **selector de carpeta** en la vista Inicio (como en el proyecto actual), además de la carpeta por defecto de config.
  - Mantener flujo: buscar último .doc/.docx → pedir nombre → **confirmación** (archivo, nombre, paciente, destino) → mover → abrir Word.
  - Opción **“Finalizar (PDF)”**: si está disponible (pywin32), conversión automática; si no, mantener recordatorios para guardar manualmente.
  - **Corregir** el uso de `self.btn_open_folder`: crearlo en `__init__` o sustituir por otro mecanismo (p. ej. enlace a carpeta del paciente).
- **Respaldo:** reutilizar lógica del proyecto actual (reintentos y mensajes claros) en el flujo que mueve el Word a Respaldo.
- **Config:**
  - Si hay instalador (ejecutable en Program Files / carpeta de instalación): usar **AppData** para `organizar_config.ini` (como Orgnizador-main).
  - Si se ejecuta desde script o exe en carpeta de usuario: permitir **config en carpeta del ejecutable** y documentarlo en README.

### 3.3 Configuración y log

- **Un solo formato de config** (mismo .ini y claves).
- **Log:** unificar en `logging` con `RotatingFileHandler` (como Orgnizador-main), manteniendo mensajes útiles del proyecto actual (incl. “Esperado PDF …”, paciente, fecha).
- En README, **tabla de configuración** del proyecto actual (incl. `logfile`, `word_path`).

### 3.4 Documentación

- **README único:** tabla de config del proyecto actual + instrucciones de uso, ejecutable e instalador (QUICKSTART + BUILD).
- Traer **QUICKSTART.md** y **BUILD_INSTRUCTIONS.md** (referenciando instalador, icono, Inno Setup).

### 3.5 Build y distribución

- **Un solo `terapias.spec`** en la raíz: incluir `terapias_logic`, `ui_components`, CustomTkinter, `pywin32` (y datos de CustomTkinter si aplica).
- **Un solo `build_exe.bat`** y **build_installer.bat** en la raíz.
- **installer.iss** e **icono** en la raíz; salida del instalador, p. ej. `installer_output/`.
- **requirements.txt** en la raíz: `customtkinter`, `packaging`, `pywin32`.

### 3.6 Tests

- Mantener **todos** los tests: `test_terapias_logic`, `test_integration`, `test_features`, `test_pdf_conversion`.
- Ubicación: carpeta `tests/` en la raíz.
- Ajustar imports y rutas si algo depende de estar dentro de `Orgnizador-main`.

---

## 4. Plan de tareas (orden sugerido)

1. **Corregir bug en Orgnizador-main:** definir o crear `btn_open_folder` en `HomeView` (o reemplazar por otro control).
2. **Copiar/actualizar en la raíz** desde Orgnizador-main: `ui_components.py`, `requirements.txt`, `QUICKSTART.md`, `BUILD_INSTRUCTIONS.md`, `build_installer.bat`, `installer.iss`, icono, y tests extra (`test_features`, `test_pdf_conversion`).
3. **Unificar `terapias.py`** en la raíz: estructura y vistas de Orgnizador-main + selector de carpeta, confirmación, reintentos de respaldo y mensajes del proyecto actual.
4. **Unificar configuración y log:** AppData cuando corresponda, mismo .ini, logging con RotatingFileHandler.
5. **Unificar README** y enlaces a QUICKSTART y BUILD_INSTRUCTIONS.
6. **Un solo `terapias.spec`** con todas las dependencias necesarias para exe + instalador.
7. **Ejecutar todos los tests** y probar flujo completo (organizar + opción PDF manual/automática + instalador).

---

## 5. Resultado esperado

- **Una sola aplicación** que tenga:
  - UI moderna (sidebar, Config, Historial, Buscar).
  - Selector de carpeta en Inicio y confirmación antes de mover.
  - Respaldo con reintentos y mensajes claros.
  - Opción de conversión automática a PDF cuando haya pywin32.
  - Config en AppData con instalador y en carpeta del exe/script cuando aplique.
  - Documentación y build unificados (exe + instalador) y todos los tests en la raíz.

Si quieres, el siguiente paso puede ser aplicar la fusión en el código (empezando por corregir `HomeView` y luego unificar `terapias.py` y la config en la raíz).
