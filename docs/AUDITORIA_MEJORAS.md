# Auditoría del proyecto – Posibles mejoras

Documento de auditoría del **Organizador de Terapias** (código unificado). Se listan mejoras por prioridad y tipo.

**Estado:** Todas las mejoras listadas han sido implementadas o documentadas (2.3, 2.4, 3.2, 3.5, 3.6, 4.2, 5.1 completadas en esta ronda).

---

## 1. Prioridad alta (correcciones y robustez)

### 1.1 COM / PDF: `CoUninitialize` en rutas de error ✅

En `convert_doc_to_pdf`, si falla `Documents.Open()` se hace `return False` sin ejecutar el `finally` que llama a `pythoncom.CoUninitialize()`. Así se puede dejar COM sin desinicializar en el hilo.

**Recomendación:** Envolver todo el bloque que usa COM en un `try/finally` y llamar siempre a `CoUninitialize()` en ese `finally` (y `Quit()` si corresponde), para que se ejecute tanto en éxito como en error.

### 1.2 Validación en ConfigView y `save_config` ✅

- **ConfigView:** No se comprueba que las tres rutas no estén vacías ni que sean distintas entre sí.
- **save_config:** No valida nada; si el usuario deja un campo vacío o repite la misma carpeta, se guarda igual.

**Recomendación:**

- En `ConfigView.save()`: comprobar que `s`, `d` y `b` no estén vacíos y que sean distintas dos a dos; si no, mostrar mensaje de error y no llamar a `save_config`.
- Opcionalmente en `save_config`: validar y devolver `False` si las rutas no son válidas.

### 1.3 Error de arranque sin GUI ✅

Si falta la sección `[RUTAS]` en el .ini, se hace `sys.exit(1)` tras escribir en stderr. Si el usuario abre el .exe con doble clic, no verá nada.

**Recomendación:** Antes de `sys.exit(1)`, si hay ventana disponible (tk/ctk ya inicializado), mostrar `messagebox.showerror` con el mensaje; si no, al menos intentar abrir un `tk.Tk()` oculto solo para poder mostrar el messagebox.

### 1.4 `open_folder`: distinguir archivo de carpeta ✅

`open_folder(path)` usa `os.path.exists(path)` pero no comprueba que sea carpeta. Si se pasa un archivo, `os.startfile(path)` lo abrirá con la aplicación por defecto, no como carpeta.

**Recomendación:** Comprobar `os.path.isdir(path)` antes de abrir; si es archivo, no llamar a `os.startfile` para “abrir carpeta” o documentar que la función es solo para carpetas y filtrar en las llamadas.

---

## 2. Prioridad media (consistencia y UX)

### 2.1 Uso de `build_folder_structure` (terapias_logic) ✅

En `terapias_logic` existe `build_folder_structure(base_dest, year, month, day, meses)` que devuelve `(ruta_anio, ruta_mes, ruta_dia, ruta_dia)`. En `terapias.py` las rutas se construyen a mano (líneas 558–561).

**Recomendación:** Usar `build_folder_structure(BASE_DEST, hoy.year, hoy.month, hoy.day, MESES)` y luego `destino_paciente = os.path.join(ruta_dia, paciente)` para no duplicar lógica y mantener una sola fuente de verdad para el formato de carpetas.

### 2.2 Historial: actualización al volver a la vista ✅

`HistoryView` carga `parse_log_history()` solo en `__init__`. Si el usuario organiza un archivo y luego va a Historial, sigue viendo los datos antiguos.

**Recomendación:** Refrescar la lista al mostrar la vista (por ejemplo sobrescribir un método que se llame al cambiar de vista, o un botón “Actualizar”) para que Historial refleje el último estado del log.

### 2.3 Configuración guardada vs. vista Inicio ✅

Tras guardar en ConfigView, `SOURCE_DEFAULT` (y resto de rutas) se actualizan en memoria, pero en HomeView el `path_entry` y la “Carpeta Origen por defecto” siguen mostrando el valor anterior hasta cambiar de vista o reiniciar.

**Recomendación:** Al volver a Inicio (o al guardar configuración), actualizar el texto del `path_entry` y del `folder_card` con los valores actuales de `SOURCE_DEFAULT` / `BASE_DEST` / etc., o recargar HomeView al cambiar a esa pestaña.

### 2.4 `save_config` no actualiza `LOGFILE` ✅

`save_config` solo escribe `source`, `base_dest` y `backup` en el .ini y en las globales. No toca `logfile` ni el handler de logging. El logger sigue escribiendo en el `LOGFILE` leído al arranque.

**Recomendación:** Decidir si la ruta del log es editable desde la app:

- Si **sí**: añadir campo “Archivo de log” en ConfigView, guardarlo en el .ini y, al guardar, reconfigurar el `RotatingFileHandler` con la nueva ruta (y actualizar la global `LOGFILE`).
- Si **no**: dejarlo como está y documentar en README/Config que “logfile solo se lee al iniciar la aplicación”.

### 2.5 Búsqueda de pacientes: límite de resultados ✅

`search_patients(query)` recorre toda la estructura Año/Mes/Día y devuelve todos los resultados. Con muchos años y pacientes puede ser lento y devolver cientos de entradas.

**Recomendación:** Añadir un límite (por ejemplo `max_results=100`) y cortar el recorrido al alcanzarlo, o mostrar los primeros N y un mensaje “Mostrando los primeros 100 resultados”.

---

## 3. Prioridad baja (calidad de código y mantenimiento)

### 3.1 Excepciones demasiado genéricas ✅

Hay varios `except Exception` y algún `except:` que tragan cualquier error y en algunos casos solo hacen `continue` sin registrar nada (p. ej. en `parse_log_history`).

**Recomendación:**

- Sustituir `except:` por `except Exception:` y, en bucles, hacer al menos `logging.debug(...)` o `logging.exception(...)` para no perder información en logs.
- Donde sea posible, capturar excepciones más concretas (p. ej. `OSError`, `configparser.Error`) en lugar de `Exception`.

### 3.2 `_reset_ui` y `btn_open_folder` ✅

`btn_open_folder` se crea en `__init__` pero solo se hace `pack()` tras “Buscar y organizar”. En `_reset_ui` se llama a `pack_forget()`. Si por algún camino se llama `_reset_ui` sin haber hecho antes `pack` del botón, el comportamiento podría ser confuso (aunque `pack_forget` suele ser seguro).

**Recomendación:** Comprobar si el widget está actualmente empaquetado antes de llamar a `pack_forget()`, o documentar que `_reset_ui` solo se usa tras un flujo que ya haya hecho `pack` del botón.

### 3.3 Tests que dependen de la GUI

`test_features` y `test_pdf_conversion` importan `terapias`, que a su vez importa `customtkinter`. Si no está instalado, `run_tests.py` o `pytest tests/` fallan en la recolección.

**Recomendación:** En esos tests, usar `import unittest; raise unittest.SkipTest("customtkinter no instalado")` si falla `import terapias`, o mover a un subpaquete `tests.gui` y marcar como skip cuando no haya customtkinter, para que el resto de tests (p. ej. `test_terapias_logic`, `test_integration`) se ejecuten siempre.

### 3.4 `run_tests.py` y descubrimiento de tests

`run_tests.py` hace `discover(start_dir="tests", pattern="test_*.py")`, por lo que incluye cualquier `test_*.py`, incluidos los que importan `terapias`. Si en el entorno no hay customtkinter, todo el descubrimiento falla.

**Recomendación:** Igual que arriba: hacer que los módulos que dependen de la GUI se salten de forma controlada si falta dependencia, para que `run_tests.py` pueda completar con los tests de lógica e integración.

### 3.5 Código muerto / imports no usados ✅

- **ui_components:** Eliminados los imports no usados `sys` y `darkdetect`.
- **terapias.py:** Imports en uso; sin cambios adicionales.

### 3.6 Directorios temporales en `tests/` ✅

- **test_integration:** `mkdtemp` ahora usa `tempfile.gettempdir()` con prefijo `terapias_test_`, para no crear carpetas bajo `tests/`.
- **.gitignore:** Añadido `tests/tmp*/` por si quedan restos de ejecuciones anteriores.

---

## 4. Seguridad y buenas prácticas

### 4.1 Rutas y inyección de path

Las rutas vienen del .ini y de los diálogos de carpeta. No se hace sanitización específica contra rutas maliciosas (p. ej. `\\servidor\netlogon` o rutas que salgan del disco esperado). Para un uso interno en un solo equipo el riesgo es bajo, pero conviene ser consciente.

**Recomendación:** Si en el futuro se añaden más fuentes de configuración (red, etc.), validar que las rutas sean locales y que no contengan secuencias peligrosas; por ahora puede quedar documentado como “uso en entorno controlado”.

### 4.2 Log: datos personales ✅

En el README (sección Configuración) se indica que el archivo de log puede contener nombres de pacientes y rutas, y que conviene proteger el directorio donde se guarda (permisos, no compartir la carpeta sin control).

---

## 5. Documentación y operación

### 5.1 README y requisitos de Python ✅

- **README:** Se indica Python 3.9+ probado con 3.9–3.12 y se enlaza a `requirements.txt`.
- **requirements.txt:** Añadidas versiones mínimas (`customtkinter>=5.2.0`, `pywin32>=306`) y comentario sobre Python 3.9–3.12.

### 5.2 Versión de la aplicación

No hay una variable o constante única con la versión (p. ej. `__version__ = "3.0.0"`) usada por el código, el instalador y la documentación.

**Recomendación:** Definir `__version__` en `terapias.py` (o en un módulo `version.py`) y referenciarla desde el script de Inno Setup y desde README/QUICKSTART si es posible, para evitar desincronizar 2.0.0 / 3.0.0 entre documentos y instalador.

### 5.3 .gitignore ✅

Ya se ignoran `organizar_config.ini`, `organizar_log.txt`, `build/`, `dist/`, etc. Opcional: añadir `error_crash.txt` y `installer_output/` si no deben subirse al repositorio.

---

## 6. Resumen de acciones sugeridas

| Prioridad | Acción |
|----------|--------|
| Alta     | Asegurar `CoUninitialize()` (y limpieza COM) en todas las rutas de `convert_doc_to_pdf`. |
| Alta     | Validar en ConfigView y/o `save_config`: rutas no vacías y distintas. |
| Alta     | Mostrar messagebox (o aviso visible) cuando falle el arranque por falta de [RUTAS]. |
| Media    | Usar `build_folder_structure` en `terapias.py` para construir rutas. |
| Media    | Refrescar Historial al entrar en la vista (o con botón “Actualizar”). |
| Media    | Actualizar path_entry y folder_card de HomeView al cambiar configuración o al volver a Inicio. |
| Media    | Definir si logfile es editable desde la app y documentar o implementar. |
| Media    | Limitar resultados de `search_patients` (p. ej. 100) y/o indicarlo en la UI. |
| Baja     | Evitar `except:` sin log; acotar excepciones donde sea posible. |
| Baja     | Hacer que tests que dependen de GUI se salten si falta customtkinter. |
| Baja     | Añadir `__version__` y usar una sola fuente de verdad para la versión. |
| Baja     | Revisar imports no usados y directorios temporales en tests. |

Si quieres, se puede bajar al detalle de implementación (parches concretos en `terapias.py`, `ConfigView`, `convert_doc_to_pdf`, etc.) en el siguiente paso.
