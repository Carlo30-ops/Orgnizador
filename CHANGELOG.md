# Changelog

Todos los cambios notables del proyecto se documentan aquí.

---

## [3.0.0] – 2025

### Añadido

- Interfaz con CustomTkinter: sidebar (Inicio, Configuración, Historial, Buscar).
- Selector de carpeta en Inicio para elegir dónde buscar archivos en cada uso.
- Confirmación explícita antes de mover el archivo (nombre, paciente, destino).
- Respaldo con reintentos (hasta 3) al mover el Word a la carpeta de respaldo.
- Historial de archivos procesados y búsqueda de pacientes por nombre.
- Botón "Abrir carpeta del paciente" tras organizar.
- Configuración guardada en `%APPDATA%\OrganizadorTerapias` cuando se usa el instalador.
- **Modo claro/oscuro:** opción en Configuración (Oscuro / Claro / Sistema).
- **Ruta de Word editable** en Configuración (opcional).
- **Elegir archivo:** si hay varios .doc/.docx en la carpeta, diálogo para elegir cuál organizar.
- **Tooltips** en los botones principales (Buscar y Organizar, Finalizar PDF, Abrir carpeta).
- **Atajos de teclado:** Ctrl+O (carpeta), F5 / Ctrl+Enter (organizar), Ctrl+R (actualizar historial), Ctrl+F (buscar).
- **Búsqueda en segundo plano:** la búsqueda de pacientes no bloquea la ventana.
- **Validación:** al guardar configuración, las rutas deben ser carpetas (no archivos).

### Cambiado

- UI refinada: bordes sutiles, tipografía Segoe UI, paleta modo oscuro (grises profundos).
- Uso de `build_folder_structure` (terapias_logic) para construir rutas.
- Log con `RotatingFileHandler` (máx. 1 MB, 1 respaldo).

### Corregido

- `convert_doc_to_pdf`: `CoUninitialize()` en todas las rutas (éxito/error).
- `open_folder`: solo abre si la ruta es un directorio.
- Arranque: messagebox si falta la sección [RUTAS] en el .ini.

---

## [2.x]

- Versiones anteriores (proyecto base con tkinter estándar, flujo de organización y respaldo).

---

Formato basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/).
