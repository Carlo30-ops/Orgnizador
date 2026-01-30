# Mejoras propuestas – Organizador de Terapias

Sugerencias concretas tras la auditoría y la refinación de UI (v3.0.0). Ordenadas por impacto y esfuerzo.

---

## 1. UX e interfaz

### 1.1 Modo claro / oscuro desde la app
**Impacto:** Alto para usuarios que prefieren tema claro.  
**Esfuerzo:** Bajo.  
- Añadir en **Configuración** (o en un menú/ajustes) la opción "Apariencia: Oscuro / Claro / Sistema".
- Usar `ctk.set_appearance_mode("Dark" | "Light" | "System")` y guardar la preferencia en el .ini (ej. `[UI] appearance=Dark`).
- Al arrancar, leer esa clave y aplicar el modo antes de construir la ventana.

### 1.2 Tooltips en botones y campos
**Impacto:** Medio – reduce dudas en primera uso.  
**Esfuerzo:** Bajo.  
- Añadir textos de ayuda cortos (tooltips) en: "Buscar y Organizar", "Finalizar (PDF)", "Abrir carpeta del paciente", campos de Configuración.
- CustomTkinter no tiene tooltip nativo: se puede usar un `CTkLabel` que aparece al hacer hover (con `bind("<Enter>"/"<Leave>")`) o una ventana pequeña junto al cursor.

### 1.3 Atajos de teclado
**Impacto:** Medio para usuarios frecuentes.  
**Esfuerzo:** Bajo.  
- `Ctrl+O`: abrir selector de carpeta (Inicio).
- `Ctrl+Enter` o `F5`: lanzar "Buscar y Organizar" cuando el foco esté en la vista Inicio.
- `Ctrl+R`: actualizar Historial.
- `Ctrl+F`: foco en búsqueda (vista Buscar).
- Documentar atajos en README o en un diálogo "Ayuda → Atajos".

### 1.4 Indicador de "trabajando" durante operaciones largas
**Impacto:** Medio – evita sensación de cuelgue.  
**Esfuerzo:** Medio.  
- Al buscar/organizar o al generar PDF, mostrar un indicador discreto (spinner o barra indeterminada) y deshabilitar botones implicados hasta que termine.
- Opcional: ejecutar la lógica pesada en un hilo y actualizar la UI al terminar (con `after()` desde el hilo principal) para no bloquear la ventana.

---

## 2. Funcionalidad

### 2.1 Elegir archivo cuando hay varios .doc/.docx
**Impacto:** Alto si suelen tener varios documentos en la carpeta origen.  
**Esfuerzo:** Medio.  
- Si `find_latest_doc` devuelve varios candidatos (o se cambia a "listar últimos N por fecha"), mostrar un diálogo con lista de archivos para que el usuario elija cuál organizar.
- Mantener "el más reciente" como opción por defecto o predeterminada en el diálogo.

### 2.2 Arrastrar y soltar carpeta en Inicio *(no prioritario)*
**Impacto:** Medio – más rápido que Examinar.  
**Esfuerzo:** Medio.  
- Permitir arrastrar una carpeta desde el Explorador sobre el `path_entry` o sobre un área "Suelta aquí la carpeta" y actualizar la ruta.
- En Tk/CustomTkinter se puede usar `tkinter.dnd` o eventos de ventana (en Windows, comprobar si el sistema expone D&D de archivos).
- **Estado:** Pospuesto; por ahora no es prioritario.

### 2.3 Ruta de Word editable en la interfaz
**Impacto:** Bajo–medio (casos con Office en rutas no estándar).  
**Esfuerzo:** Bajo.  
- Ya existe `word_path` en el .ini. Añadir en **Configuración** un campo opcional "Ruta de Word" (o botón "Detectar" que pruebe rutas típicas y rellene).
- Al guardar, escribir `word_path` en el .ini y usarlo en `find_word_executable()`.

### 2.4 Campo "Archivo de log" en Configuración (opcional)
**Impacto:** Bajo.  
**Esfuerzo:** Medio.  
- Si se quiere que el usuario pueda cambiar la ruta del log sin tocar el .ini: añadir campo en ConfigView, guardar en .ini y, al guardar, reconfigurar el `RotatingFileHandler` con la nueva ruta y actualizar la global `LOGFILE`.

---

## 3. Robustez y rendimiento

### 3.1 Búsqueda en segundo plano
**Impacto:** Medio cuando hay muchas carpetas.  
**Esfuerzo:** Medio.  
- Lanzar `search_patients()` en un hilo o con `after()` en lotes, para no bloquear la UI mientras se recorre la estructura.
- Mostrar "Buscando…" y actualizar la lista de resultados cuando termine (el límite de 100 resultados ya está; mantenerlo).

### 3.2 Timeout o aviso si Word no responde ✅
**Impacto:** Bajo–medio.  
**Esfuerzo:** Medio.  
- **Implementado:** Ya no se usa `/WAIT` al abrir Word. La app abre Word con `subprocess.Popen` (sin esperar), de modo que la ventana no se bloquea. Los mensajes indican: "Cuando termines, cierra Word y pulsa Finalizar (PDF)". Así se recupera el control de la ventana y no hay espera indefinida.

### 3.3 Validación de rutas al guardar configuración
**Impacto:** Medio.  
**Esfuerzo:** Bajo.  
- Además de "no vacías" y "distintas entre sí": comprobar que las rutas no son archivos (solo carpetas), opcionalmente que el disco existe, y advertir si la carpeta origen no existe (sin impedir guardar).

---

## 4. Código y mantenimiento

### 4.1 Una sola fuente de verdad para la versión
**Impacto:** Bajo – evita desincronizar instalador y app.  
**Esfuerzo:** Bajo.  
- En `installer.iss` leer la versión desde un archivo generado en el build (ej. `version.txt` que escriba `build_exe.bat` desde `terapias.__version__`), o documentar en BUILD_INSTRUCTIONS que hay que actualizar manualmente `MyAppVersion` y `__version__` juntos.

### 4.2 Type hints en funciones públicas
**Impacto:** Bajo – mejor documentación y soporte IDE.  
**Esfuerzo:** Bajo–medio.  
- Añadir anotaciones en `terapias_logic.py` (ya tiene algunas) y en las funciones de `terapias.py` que se usan desde varias partes (ej. `load_config`, `save_config`, `find_latest_doc`, `convert_doc_to_pdf`).

### 4.3 Tests que no dependan de GUI
**Impacto:** Bajo – CI y entornos sin display.  
**Esfuerzo:** Bajo.  
- Mantener los tests de GUI con `skipIf` cuando falle `import terapias` (o falte customtkinter), para que `run_tests.py` o `pytest tests/` pasen solo con tests de lógica e integración cuando no haya GUI.

---

## 5. Documentación y despliegue

### 5.1 Changelog (CHANGELOG.md)
**Impacto:** Medio para usuarios y mantenimiento.  
**Esfuerzo:** Bajo.  
- Archivo `CHANGELOG.md` con secciones por versión (3.0.0, 2.x, etc.): novedades, correcciones, mejoras de UI. Facilita saber qué trae cada instalador y qué probar.

### 5.2 README: sección "Última versión"
**Impacto:** Bajo.  
**Esfuerzo:** Bajo.  
- Una línea al inicio del README: "Última versión: 3.0.0" (o enlace al instalador más reciente si se publica en Releases de GitHub).

### 5.3 Build reproducible
**Impacto:** Bajo.  
**Esfuerzo:** Medio.  
- En `build_exe.bat` (o script equivalente): fijar versión de PyInstaller y de dependencias críticas (customtkinter, pywin32) para que el ejecutable sea reproducible. Opcional: paso que genere `version.txt` para el instalador.

---

## 6. Resumen por prioridad sugerida

| Prioridad | Mejora | Esfuerzo |
|-----------|--------|----------|
| Alta      | Modo claro/oscuro en la app | Bajo |
| Alta      | Elegir archivo cuando hay varios .doc/.docx | Medio |
| Media     | Tooltips en botones y campos | Bajo |
| Media     | Atajos de teclado | Bajo |
| Media     | Ruta de Word editable en Configuración | Bajo |
| Media     | Indicador "trabajando" en operaciones largas | Medio |
| Media     | Búsqueda en segundo plano | Medio |
| Baja      | Arrastrar y soltar carpeta *(no prioritario)* | Medio |
| Baja      | CHANGELOG.md y versión en README | Bajo |
| Baja      | Una sola fuente de versión (build + .iss) | Bajo |

Si quieres, se puede bajar al detalle de implementación (código concreto) para cualquiera de estas mejoras.
