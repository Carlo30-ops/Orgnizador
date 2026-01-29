# Análisis del proyecto "Organizador robusto"

## 1. Resumen ejecutivo

**Organizador robusto** es una aplicación de escritorio para **Windows** que automatiza el flujo de trabajo con informes de terapia: toma el documento Word más reciente de una carpeta, pide un nombre al usuario, lo organiza en una estructura **Año → Mes → Día → Paciente**, abre Word para editarlo/guardar como PDF, y mueve el original a respaldo. Todo se controla por un INI y se registra en un log.

El proyecto incluye **código fuente** (`terapias.py`), spec de PyInstaller (`terapias.spec`) y el producto empaquetado en `dist/`.

---

## 2. Estructura del proyecto

```
Organizador robusto/
├── terapias.py              # Código fuente principal
├── terapias_logic.py        # Lógica pura (testeable)
├── terapias.spec            # Especificación PyInstaller
├── organizar_config.ini.ejemplo  # Plantilla de configuración
├── docs/                    # Documentación
└── tests/                   # Tests unitarios
```

---

## 3. Configuración (`organizar_config.ini`)

Si no existe el archivo, el script lo crea con valores por defecto. Claves:

| Clave       | Uso |
|------------|-----|
| **source** | Carpeta de origen: solo se consideran `.doc` y `.docx`; se usa el **más reciente por fecha de modificación**. |
| **base_dest** | Raíz de destino: bajo ella se crea `AÑO\MM- MES\DD DE MES\PACIENTE`. |
| **backup** | Carpeta de respaldo: ahí se mueve el Word después de que el usuario cierra Word. |
| **logfile** | Ruta del archivo de log. |

---

## 4. Stack técnico

- **Lenguaje:** Python 3.9+
- **Solo librería estándar:** `os`, `shutil`, `datetime`, `subprocess`, `configparser`, `tkinter`
- **Empaquetado:** PyInstaller, un solo ejecutable, sin ventana de consola

---

## 5. Conclusión

El proyecto es una **herramienta de flujo de trabajo** para informes de terapia en Windows: localiza el Word más reciente en una carpeta, pide nombre y deriva el nombre de paciente, organiza en carpetas por fecha y paciente, abre Word para edición/exportar a PDF, respalda el Word y registra la acción en un log.
