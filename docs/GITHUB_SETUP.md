# Subir el proyecto a GitHub

## Pasos para crear el repositorio

### 1. Crear el repositorio en GitHub

1. Ve a [github.com](https://github.com) e inicia sesión
2. Clic en **New repository**
3. Nombre sugerido: `organizador-terapias` o `Organizador-robusto`
4. Descripción: "Aplicación de escritorio para organizar documentos de terapia en Windows"
5. Elige **Public** o **Private**
6. **No** marques "Add a README" (ya existe)
7. Clic en **Create repository**

### 2. Inicializar Git e subir

Abre la terminal en la carpeta del proyecto y ejecuta:

```bash
# Inicializar Git
git init

# Añadir todos los archivos
git add .

# Primer commit
git commit -m "Initial commit: Organizador de Terapias"

# Añadir el remoto (reemplaza TU-USUARIO y NOMBRE-REPO con los tuyos)
git remote add origin https://github.com/TU-USUARIO/NOMBRE-REPO.git

# Subir a la rama main
git branch -M main
git push -u origin main
```

### 3. Actualizar la URL del clone en README

Edita `README.md` y reemplaza `tu-usuario/organizador-terapias` por tu usuario y nombre de repo reales en la línea del `git clone`.

## Archivos que se suben

- Código fuente: `terapias.py`, `terapias_logic.py`
- Configuración: `terapias.spec`, `organizar_config.ini.ejemplo`
- Scripts: `build_exe.bat`, `run_tests.py`
- Tests: `tests/`
- Documentación: `docs/`, `README.md`, `CONTRIBUTING.md`, `LICENSE`
- Config: `.gitignore`, `.gitattributes`

## Archivos que NO se suben (.gitignore)

- `build/` – Artefactos de PyInstaller
- `dist/` – Ejecutable generado
- `__pycache__/` – Caché de Python
- `organizar_config.ini` – Configuración local (rutas del usuario)
- `*.log` – Archivos de log
