# Subir el proyecto a GitHub

Guía para preparar y publicar **Organizador de Terapias** en GitHub.

---

## 1. Antes de subir

### Comprobar que no se suben datos sensibles

El `.gitignore` ya excluye:

- `organizar_config.ini` (rutas del usuario)
- `organizar_log.txt` (puede contener nombres de pacientes)
- `build/`, `dist/`, `installer_output/`, `version.txt`
- `__pycache__/`, `venv/`, `.env`
- `Orgnizador-main/` (carpeta duplicada/antigua)

### Estructura que sí se sube

```
organizador-terapias/
├── .gitattributes
├── .gitignore
├── README.md
├── CHANGELOG.md
├── LICENSE
├── CONTRIBUTING.md
├── BUILD_INSTRUCTIONS.md
├── QUICKSTART.md
├── requirements.txt
├── organizar_config.ini.ejemplo
├── terapias.py
├── terapias_logic.py
├── ui_components.py
├── terapias.spec
├── build_exe.bat
├── build_installer.bat
├── run_tests.py
├── installer.iss
├── image-removebg-preview.ico
├── docs/
│   ├── GITHUB_SETUP.md
│   ├── PREPARAR_INSTALADOR.md
│   └── ...
└── tests/
    ├── __init__.py
    ├── test_terapias_logic.py
    ├── test_integration.py
    └── ...
```

---

## 2. Crear el repositorio en GitHub

1. Entra en [github.com](https://github.com) e inicia sesión.
2. Clic en **New repository** (o **+** → **New repository**).
3. **Repository name:** por ejemplo `organizador-terapias` o `Organizador-Terapias`.
4. **Description:** `Aplicación de escritorio para organizar documentos de terapia en Windows (CustomTkinter, Word, PDF)`.
5. Elige **Public** o **Private**.
6. **No** marques "Add a README" (ya existe en el proyecto).
7. Clic en **Create repository**.

---

## 3. Inicializar Git y subir

En la carpeta raíz del proyecto (donde está `terapias.py`):

```bash
# Inicializar Git (si aún no está inicializado)
git init

# Comprobar que Orgnizador-main no se incluye
git status

# Añadir todos los archivos (respetando .gitignore)
git add .

# Primer commit
git commit -m "Initial commit: Organizador de Terapias v3.0.0"

# Nombrar rama main
git branch -M main

# Añadir el remoto (reemplaza TU-USUARIO y NOMBRE-REPO)
git remote add origin https://github.com/TU-USUARIO/NOMBRE-REPO.git

# Subir
git push -u origin main
```

Si el repositorio ya existía y tiene historial:

```bash
git remote add origin https://github.com/TU-USUARIO/NOMBRE-REPO.git
git branch -M main
git push -u origin main
```

---

## 4. Después de subir

### Actualizar la URL del clone en README

En `README.md`, sustituye `tu-usuario/organizador-terapias` por tu usuario y nombre de repo reales en la línea del `git clone`.

### Opcional: Releases

Para publicar instaladores:

1. En el repo: **Releases** → **Create a new release**.
2. Tag: por ejemplo `v3.0.0`.
3. Adjunta `OrganizadorTerapias_Setup_v3.0.0.exe` (generado con Inno Setup desde `installer_output/`).

---

## 5. Archivos que no se suben (.gitignore)

| Archivo o carpeta        | Motivo                          |
|--------------------------|----------------------------------|
| `build/`, `dist/`        | Artefactos de PyInstaller       |
| `installer_output/`      | Instaladores generados         |
| `organizar_config.ini`   | Configuración local (rutas)     |
| `organizar_log.txt`      | Log (puede contener datos)      |
| `version.txt`            | Generado por `build_exe.bat`    |
| `__pycache__/`, `venv/`  | Caché y entornos virtuales     |
| `Orgnizador-main/`       | Copia antigua del proyecto      |

---

## 6. Colaboración

- **Issues:** para bugs o mejoras (plantillas en `.github/ISSUE_TEMPLATE/`).
- **Pull requests:** ver `CONTRIBUTING.md` y plantilla en `.github/PULL_REQUEST_TEMPLATE.md`.

---

## Checklist antes del primer push

- [ ] No hay `organizar_config.ini` ni `organizar_log.txt` en la carpeta (o están en `.gitignore`).
- [ ] La carpeta `Orgnizador-main/` no se sube (está en `.gitignore`).
- [ ] `git status` no muestra `dist/`, `build/`, `__pycache__/`.
- [ ] Has sustituido `TU-USUARIO` y `NOMBRE-REPO` en la URL del remoto.
- [ ] En `README.md` has actualizado la URL del `git clone` con tu usuario y repo.
