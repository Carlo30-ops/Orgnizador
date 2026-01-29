# Mejoras adicionales sugeridas

Las mejoras anteriores ya están aplicadas. Estas son **nuevas mejoras** que se pueden implementar:

---

## 1. Configuración y rutas

### 1.1 Rutas por defecto con usuario actual
Generar rutas por defecto con `os.path.expanduser("~")` para el usuario actual.

### 1.2 Ruta de Word configurable en el INI
Añadir clave `word_path` en `[RUTAS]` con valor por defecto `winword.exe`.

### 1.3 Validar que las carpetas existen al iniciar
Comprobar que `source` existe; crear `base_dest` y `backup` si no existen.

---

## 2. Flujo y confirmación

### 2.1 Confirmación antes de mover
Mostrar diálogo de confirmación antes de mover el archivo.

### 2.2 Mensaje recordatorio al cerrar Word
Mostrar mensaje después de que Word se cierre.

---

## 3. Respaldo y errores

### 3.1 Reintentar si falla el respaldo
Ofrecer botón "Reintentar" cuando falla el movimiento a Respaldo.

### 3.2 Crear carpetas base si no existen
Crear automáticamente `base_dest` y `backup` al cargar la config.

---

## 4. Interfaz y UX

### 4.1 Permitir elegir archivo si hay varios
Si hay más de un archivo en `source`, mostrar lista para elegir.

### 4.2 Soporte para "SS" al final
"Juan Pérez SS" → paciente "Juan Pérez".

---

## 5. Log y depuración

### 5.1 Rotación del log
Si el log supera 1 MB, renombrar a `.old` y crear uno nuevo.

### 5.2 Buscar Word en rutas típicas
Si `winword.exe` no está en PATH, buscar en Program Files.
