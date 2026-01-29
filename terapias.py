import os
import sys
import shutil
import time
import datetime
import subprocess
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import configparser

from terapias_logic import sanitize_filename, patient_from_user_input, check_path_length

# =========================
# Tema y estilos del frontend
# =========================
_COLORS = {
    "primary": "#0d9488",
    "primary_hover": "#0f766e",
    "bg_light": "#f0fdfa",
    "bg_card": "#ffffff",
    "text_dark": "#134e4a",
    "text_muted": "#64748b",
    "error": "#dc2626",
    "error_bg": "#fef2f2",
    "success": "#059669",
}
_FONT_TITLE = ("Segoe UI", 14, "bold")
_FONT_BODY = ("Segoe UI", 10)
_FONT_SMALL = ("Segoe UI", 9)
_PAD = 12

# =========================
# Configuración desde .ini
# =========================
if getattr(sys, "frozen", False):
    _base_dir = os.path.dirname(sys.executable)
else:
    _base_dir = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(_base_dir, "organizar_config.ini")

_REQUIRED_KEYS = ("source", "base_dest", "backup", "logfile")
_user_home = os.path.expanduser("~")
_DEFAULT_RUTAS = {
    "source": os.path.join(_user_home, "Documents", "TERAPIAS", "DOCUMENTOS PARA ARMAR"),
    "base_dest": os.path.join(_user_home, "Documents", "TERAPIAS", "TERAPIAS"),
    "backup": os.path.join(_user_home, "Documents", "TERAPIAS", "Respaldo"),
    "logfile": os.path.join(_user_home, "Documents", "TERAPIAS", "organizar_log.txt"),
    "word_path": "winword.exe",
}

config = configparser.ConfigParser()
if not os.path.exists(CONFIG_FILE):
    config["RUTAS"] = _DEFAULT_RUTAS
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            config.write(f)
    except OSError:
        pass

config.read(CONFIG_FILE, encoding="utf-8")

if "RUTAS" not in config:
    messagebox.showerror("Error", "En organizar_config.ini falta la sección [RUTAS].")
    sys.exit(1)
missing = [k for k in _REQUIRED_KEYS if k not in config["RUTAS"]]
if missing:
    messagebox.showerror("Error", f"En organizar_config.ini faltan las claves: {', '.join(missing)}")
    sys.exit(1)

SOURCE_DEFAULT = config["RUTAS"]["source"]
BASE_DEST = config["RUTAS"]["base_dest"]
BACKUP = config["RUTAS"]["backup"]
LOGFILE = config["RUTAS"]["logfile"]
try:
    WORD_PATH = config.get("RUTAS", "word_path").strip() or "winword.exe"
except (configparser.NoOptionError, configparser.NoSectionError):
    WORD_PATH = "winword.exe"

for ruta in (BASE_DEST, BACKUP):
    try:
        os.makedirs(ruta, exist_ok=True)
    except OSError:
        pass

MESES = {
    1: "ENERO", 2: "FEBRERO", 3: "MARZO", 4: "ABRIL",
    5: "MAYO", 6: "JUNIO", 7: "JULIO", 8: "AGOSTO",
    9: "SEPTIEMBRE", 10: "OCTUBRE", 11: "NOVIEMBRE", 12: "DICIEMBRE"
}
_MAX_PATH_LEN = 250
_LOG_MAX_SIZE = 1024 * 1024
_WORD_PATHS = [
    "winword.exe",
    os.path.join(os.environ.get("ProgramFiles", "C:\\Program Files"), "Microsoft Office", "root", "Office16", "WINWORD.EXE"),
    os.path.join(os.environ.get("ProgramFiles(x86)", "C:\\Program Files (x86)"), "Microsoft Office", "root", "Office16", "WINWORD.EXE"),
]


def _configure_theme(root: tk.Tk):
    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except tk.TclError:
        pass
    style.configure("TFrame", background=_COLORS["bg_light"])
    style.configure("TLabel", background=_COLORS["bg_light"], foreground=_COLORS["text_dark"], font=_FONT_BODY)
    style.configure("TEntry", font=_FONT_BODY, padding=6)
    style.configure("TButton", font=_FONT_BODY, padding=(12, 6))


def _center_window(win: tk.Toplevel | tk.Tk, width: int = 500, height: int = 380):
    win.update_idletasks()
    x = (win.winfo_screenwidth() // 2) - (width // 2)
    y = (win.winfo_screenheight() // 2) - (height // 2)
    win.geometry(f"{width}x{height}+{x}+{y}")


def find_latest_doc(source_dir: str) -> str | None:
    if not os.path.isdir(source_dir):
        return None
    latest_file = None
    latest_time = -1
    for fname in os.listdir(source_dir):
        if fname.lower().endswith(".doc") or fname.lower().endswith(".docx"):
            fpath = os.path.join(source_dir, fname)
            try:
                mtime = os.path.getmtime(fpath)
            except OSError:
                continue
            if mtime > latest_time:
                latest_time = mtime
                latest_file = fpath
    return latest_file


def _rotate_log_if_needed():
    try:
        if os.path.exists(LOGFILE) and os.path.getsize(LOGFILE) > _LOG_MAX_SIZE:
            backup_log = LOGFILE + ".old"
            if os.path.exists(backup_log):
                os.remove(backup_log)
            shutil.move(LOGFILE, backup_log)
    except OSError:
        pass


def log_action(msg: str):
    _rotate_log_if_needed()
    try:
        with open(LOGFILE, "a", encoding="utf-8") as f:
            f.write(f"{datetime.datetime.now()} - {msg}\n")
    except OSError:
        pass


def find_word_executable() -> str | None:
    candidates = [WORD_PATH] + _WORD_PATHS
    for path in candidates:
        if os.path.isabs(path):
            if os.path.isfile(path):
                return path
        else:
            found = shutil.which(path)
            if found:
                return found
    return None


def show_error_dialog(parent: tk.Tk, msg: str):
    win = tk.Toplevel(parent)
    win.title("Error")
    win.configure(bg=_COLORS["error_bg"])
    frame = tk.Frame(win, bg=_COLORS["error_bg"], padx=_PAD, pady=_PAD)
    frame.pack(fill=tk.BOTH, expand=True)
    tk.Label(frame, text="Error", font=_FONT_TITLE, fg=_COLORS["error"], bg=_COLORS["error_bg"]).pack(anchor=tk.W)
    tk.Label(frame, text=msg, font=_FONT_BODY, fg=_COLORS["text_dark"], bg=_COLORS["error_bg"], wraplength=400, justify=tk.LEFT).pack(anchor=tk.W, pady=(8, 16))
    ttk.Button(frame, text="Aceptar", command=win.destroy).pack(anchor=tk.E)
    win.transient(parent)
    win.grab_set()


def show_info_dialog(parent: tk.Tk, msg: str):
    win = tk.Toplevel(parent)
    win.title("Información")
    win.configure(bg=_COLORS["bg_light"])
    frame = tk.Frame(win, bg=_COLORS["bg_light"], padx=_PAD, pady=_PAD)
    frame.pack(fill=tk.BOTH, expand=True)
    tk.Label(frame, text="Información", font=_FONT_TITLE, fg=_COLORS["primary"], bg=_COLORS["bg_light"]).pack(anchor=tk.W)
    tk.Label(frame, text=msg, font=_FONT_BODY, fg=_COLORS["text_dark"], bg=_COLORS["bg_light"], wraplength=400, justify=tk.LEFT).pack(anchor=tk.W, pady=(8, 16))
    ttk.Button(frame, text="Aceptar", command=win.destroy).pack(anchor=tk.E)
    win.transient(parent)
    win.grab_set()


def ask_yesno_dialog(parent: tk.Tk, question: str, title: str = "Confirmar") -> bool:
    result = [None]

    def on_yes():
        result[0] = True
        win.destroy()

    def on_no():
        result[0] = False
        win.destroy()

    win = tk.Toplevel(parent)
    win.title(title)
    win.configure(bg=_COLORS["bg_light"])
    frame = tk.Frame(win, bg=_COLORS["bg_light"], padx=_PAD, pady=_PAD)
    frame.pack(fill=tk.BOTH, expand=True)
    tk.Label(frame, text=title, font=_FONT_TITLE, fg=_COLORS["primary"], bg=_COLORS["bg_light"]).pack(anchor=tk.W)
    tk.Label(frame, text=question, font=_FONT_BODY, fg=_COLORS["text_dark"], bg=_COLORS["bg_light"], wraplength=420, justify=tk.LEFT).pack(anchor=tk.W, pady=(8, 20))
    btn_frame = tk.Frame(frame, bg=_COLORS["bg_light"])
    btn_frame.pack(anchor=tk.E)
    tk.Button(btn_frame, text="Sí", font=_FONT_BODY, bg=_COLORS["primary"], fg="white", relief=tk.FLAT, padx=16, pady=6, cursor="hand2", command=on_yes).pack(side=tk.LEFT, padx=(0, 8))
    ttk.Button(btn_frame, text="No", command=on_no).pack(side=tk.LEFT)
    win.transient(parent)
    win.grab_set()
    win.wait_window()
    return result[0] is True


def ask_text_dialog(parent: tk.Tk, prompt: str, default: str = "", title: str = "Nombre del archivo") -> str | None:
    result = [None]

    def on_ok():
        result[0] = entry.get().strip()
        win.destroy()

    def on_cancel():
        result[0] = None
        win.destroy()

    win = tk.Toplevel(parent)
    win.title(title)
    win.configure(bg=_COLORS["bg_light"])
    frame = tk.Frame(win, bg=_COLORS["bg_light"], padx=_PAD, pady=_PAD)
    frame.pack(fill=tk.BOTH, expand=True)
    tk.Label(frame, text=title, font=_FONT_TITLE, fg=_COLORS["primary"], bg=_COLORS["bg_light"]).pack(anchor=tk.W)
    tk.Label(frame, text=prompt, font=_FONT_BODY, fg=_COLORS["text_dark"], bg=_COLORS["bg_light"], wraplength=420, justify=tk.LEFT).pack(anchor=tk.W, pady=(8, 8))
    entry = ttk.Entry(frame, font=_FONT_BODY, width=45)
    entry.pack(fill=tk.X, pady=(0, 16), ipady=6)
    entry.insert(0, default)
    entry.select_range(0, tk.END)
    entry.focus_set()
    win.bind("<Return>", lambda e: on_ok())
    win.bind("<Escape>", lambda e: on_cancel())
    btn_frame = tk.Frame(frame, bg=_COLORS["bg_light"])
    btn_frame.pack(anchor=tk.E)
    tk.Button(btn_frame, text="Aceptar", font=_FONT_BODY, bg=_COLORS["primary"], fg="white", relief=tk.FLAT, padx=16, pady=6, cursor="hand2", command=on_ok).pack(side=tk.LEFT, padx=(0, 8))
    ttk.Button(btn_frame, text="Cancelar", command=on_cancel).pack(side=tk.LEFT)
    win.transient(parent)
    win.grab_set()
    win.wait_window()
    return result[0]


# =========================
# Aplicación principal
# =========================
def main():
    root = tk.Tk()
    _configure_theme(root)
    root.title("Organizador de Terapias")
    root.configure(bg=_COLORS["bg_light"])
    root.minsize(500, 380)
    root.resizable(True, True)

    main_frame = tk.Frame(root, bg=_COLORS["bg_light"], padx=24, pady=20)
    main_frame.pack(fill=tk.BOTH, expand=True)

    # Título
    tk.Label(main_frame, text="Organizador de Terapias", font=("Segoe UI", 18, "bold"), fg=_COLORS["primary"], bg=_COLORS["bg_light"]).pack(anchor=tk.W)
    tk.Label(main_frame, text="Organiza documentos de terapia (.doc, .docx)", font=_FONT_SMALL, fg=_COLORS["text_muted"], bg=_COLORS["bg_light"]).pack(anchor=tk.W, pady=(0, 20))

    # Carpeta de búsqueda
    folder_frame = tk.Frame(main_frame, bg=_COLORS["bg_light"])
    folder_frame.pack(fill=tk.X, pady=(0, 8))
    tk.Label(folder_frame, text="Carpeta donde buscar archivos:", font=_FONT_BODY, fg=_COLORS["text_dark"], bg=_COLORS["bg_light"]).pack(anchor=tk.W)
    path_var = tk.StringVar(value=SOURCE_DEFAULT if os.path.isdir(SOURCE_DEFAULT) else _user_home)

    path_entry_frame = tk.Frame(main_frame, bg=_COLORS["bg_light"])
    path_entry_frame.pack(fill=tk.X, pady=(4, 16))
    path_entry = ttk.Entry(path_entry_frame, textvariable=path_var, font=_FONT_BODY, width=50)
    path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8), ipady=4)

    def browse_folder():
        initial = path_var.get() if os.path.isdir(path_var.get()) else _user_home
        folder = filedialog.askdirectory(title="Seleccionar carpeta para buscar archivos", initialdir=initial)
        if folder:
            path_var.set(folder)

    tk.Button(path_entry_frame, text="Examinar...", font=_FONT_BODY, bg=_COLORS["primary"], fg="white", relief=tk.FLAT, padx=12, pady=6, cursor="hand2", command=browse_folder).pack(side=tk.LEFT)

    # Área de estado
    status_frame = tk.LabelFrame(main_frame, text=" Estado ", font=_FONT_BODY, fg=_COLORS["text_muted"], bg=_COLORS["bg_light"])
    status_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 16))
    status_label = tk.Label(status_frame, text="Listo. Selecciona una carpeta y haz clic en \"Buscar y organizar\".", font=_FONT_BODY, fg=_COLORS["text_dark"], bg=_COLORS["bg_light"], wraplength=440, justify=tk.LEFT)
    status_label.pack(anchor=tk.W, padx=12, pady=12, fill=tk.BOTH, expand=True)

    def set_status(msg: str, is_error: bool = False):
        status_label.config(text=msg, fg=_COLORS["error"] if is_error else _COLORS["text_dark"])

    def run_organize():
        source_folder = path_var.get().strip()
        if not source_folder:
            set_status("Selecciona una carpeta donde buscar los archivos.", is_error=True)
            return
        if not os.path.isdir(source_folder):
            set_status(f"La carpeta no existe:\n{source_folder}", is_error=True)
            return

        set_status("Buscando archivos .doc y .docx...")
        root.update()

        latest_file = find_latest_doc(source_folder)
        if not latest_file:
            set_status("No se encontró ningún archivo .doc o .docx en la carpeta seleccionada.\n\nSelecciona otra carpeta o añade un documento y vuelve a intentar.", is_error=True)
            return

        archivo_a_organizar = os.path.basename(latest_file)
        set_status(f"Archivo encontrado: {archivo_a_organizar}\nSolicitando nombre...")
        root.update()

        prompt = (
            f"Archivo a organizar: {archivo_a_organizar}\n\n"
            "Escribe el nuevo nombre (sin extensión).\n"
            "Si escribes 'SS Nombre Paciente', la carpeta del paciente se creará con ese nombre."
        )
        user_name = ask_text_dialog(root, prompt, title="Nombre del archivo")

        if user_name is None:
            set_status("Operación cancelada.")
            return
        if not user_name.strip():
            set_status("El nombre no puede estar vacío. Operación cancelada.", is_error=True)
            return

        user_name = sanitize_filename(user_name)
        paciente = patient_from_user_input(user_name)

        hoy = datetime.date.today()
        anio = str(hoy.year)
        mes_nombre = f"{hoy.month:02d}- {MESES[hoy.month]}"
        dia_nombre = f"{hoy.day:02d} DE {MESES[hoy.month]}"

        ruta_anio = os.path.join(BASE_DEST, anio)
        ruta_mes = os.path.join(ruta_anio, mes_nombre)
        ruta_dia = os.path.join(ruta_mes, dia_nombre)
        destino_paciente = os.path.join(ruta_dia, paciente)

        for ruta in (ruta_anio, ruta_mes, ruta_dia, destino_paciente, BACKUP):
            os.makedirs(ruta, exist_ok=True)

        ext = os.path.splitext(latest_file)[1].lower()
        if ext not in (".doc", ".docx"):
            ext = ".docx"

        stem, ext_suffix = user_name, ext
        n = 0
        while True:
            doc_name = f"{stem}_{n}" if n else stem
            new_doc_path = os.path.join(destino_paciente, doc_name + ext_suffix)
            if not os.path.exists(new_doc_path):
                break
            n += 1

        if not check_path_length(new_doc_path, _MAX_PATH_LEN):
            set_status(f"La ruta del archivo es demasiado larga para Windows.\nUsa un nombre más corto.", is_error=True)
            return

        confirmacion = (
            f"¿Organizar el archivo\n{archivo_a_organizar}\n\n"
            f"como: {user_name}{ext}\n"
            f"Paciente: {paciente}\n"
            f"Destino: {destino_paciente}\n\n"
            "¿Continuar?"
        )
        if not ask_yesno_dialog(root, confirmacion, title="Confirmar organización"):
            set_status("Operación cancelada.")
            return

        try:
            shutil.move(latest_file, new_doc_path)
        except Exception as e:
            log_action(f"ERROR: No se pudo mover {latest_file} → {new_doc_path}: {e}")
            set_status(f"No se pudo mover el archivo:\n{e}", is_error=True)
            return

        subprocess.Popen(["explorer", destino_paciente])
        show_info_dialog(root, f"Abriendo Word...\n\nGuarda como PDF con el nombre:\n{user_name}.pdf\n\nCarpeta destino:\n{destino_paciente}")

        word_exe = find_word_executable()
        if not word_exe:
            log_action("ERROR: No se encontró winword.exe")
            set_status("No se encontró Microsoft Word (winword.exe). Verifica la instalación.", is_error=True)
            return

        try:
            subprocess.call(["start", "/WAIT", word_exe, new_doc_path], shell=True)
        except Exception as e:
            log_action(f"ERROR: No se pudo abrir Word: {e}")
            set_status(f"No se pudo abrir Microsoft Word:\n{e}", is_error=True)
            return

        show_info_dialog(root, f"Recuerda: el PDF debe guardarse en:\n{destino_paciente}\n\nCon el nombre: {user_name}.pdf")

        if os.path.exists(new_doc_path):
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            base_backup = os.path.splitext(os.path.basename(new_doc_path))[0]
            ext_backup = os.path.splitext(new_doc_path)[1]
            backup_path = os.path.join(BACKUP, f"{base_backup}_{timestamp}{ext_backup}")

            max_retries = 3
            for intento in range(max_retries):
                try:
                    shutil.move(new_doc_path, backup_path)
                    set_status(f"✓ Completado. Respaldo: {os.path.basename(backup_path)}\nEl PDF debe estar en la carpeta del paciente.")
                    break
                except Exception as e:
                    log_action(f"ERROR (intento {intento + 1}/{max_retries}): No se pudo mover a Respaldo: {e}")
                    if intento < max_retries - 1:
                        set_status(f"Reintentando respaldo... ({intento + 1}/{max_retries})")
                        root.update()
                        time.sleep(3)
                    else:
                        set_status(f"No se pudo mover a Respaldo tras {max_retries} intentos.\nDeja el archivo en la carpeta del paciente.", is_error=True)

        log_action(f"Esperado PDF: {user_name}.pdf → {destino_paciente} | Paciente: {paciente} | Fecha: {anio}/{mes_nombre}/{dia_nombre}")

    # Botón principal
    tk.Button(main_frame, text="Buscar y organizar", font=("Segoe UI", 11, "bold"), bg=_COLORS["primary"], fg="white", relief=tk.FLAT, padx=24, pady=10, cursor="hand2", command=run_organize).pack(pady=(0, 8))

    _center_window(root, 500, 380)
    root.mainloop()


if __name__ == "__main__":
    main()
