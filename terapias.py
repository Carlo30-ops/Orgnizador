"""
Organizador de Terapias - Aplicación unificada.
Combina UI moderna (CustomTkinter), selector de carpeta, confirmación explícita,
reintentos de respaldo y conversión automática a PDF (win32com).
"""
__version__ = "3.0.0"

import os
import sys
import shutil
import time
import datetime
import subprocess
import logging
import threading
from logging.handlers import RotatingFileHandler
import configparser
import tkinter as tk
from tkinter import filedialog, messagebox

import customtkinter as ctk

from ui_components import (
    VisionSys, apply_acrylic, GlassFrame, FloatingButton,
    GlassCard, SectionHeader, add_tooltip, center_window
)
from terapias_logic import (
    sanitize_filename,
    patient_from_user_input,
    check_path_length,
    build_folder_structure,
)

# =========================
# Configuración Global (tema se aplica tras cargar config)
# =========================
ctk.set_default_color_theme("blue")

# =========================
# Ruta del archivo de configuración
# =========================
if getattr(sys, "frozen", False):
    _base_dir = os.path.dirname(sys.executable)
else:
    _base_dir = os.path.dirname(os.path.abspath(__file__))

_user_home = os.path.expanduser("~")
# Instalador: config en AppData. Ejecución desde script/exe en carpeta: config junto al exe/script.
_app_data = os.path.join(os.environ.get("APPDATA", _user_home), "OrganizadorTerapias")
def _get_config_path():
    if getattr(sys, "frozen", False):
        os.makedirs(_app_data, exist_ok=True)
        return os.path.join(_app_data, "organizar_config.ini")
    return os.path.join(_base_dir, "organizar_config.ini")

CONFIG_FILE = _get_config_path()

_REQUIRED_KEYS = ("source", "base_dest", "backup", "logfile")
_DEFAULT_RUTAS = {
    "source": os.path.join(_user_home, "Documents", "TERAPIAS", "DOCUMENTOS PARA ARMAR"),
    "base_dest": os.path.join(_user_home, "Documents", "TERAPIAS", "TERAPIAS"),
    "backup": os.path.join(_user_home, "Documents", "TERAPIAS", "Respaldo"),
    "logfile": os.path.join(_user_home, "Documents", "TERAPIAS", "organizar_log.txt"),
    "word_path": "winword.exe",
}


def load_config() -> configparser.ConfigParser:
    config = configparser.ConfigParser()
    if not os.path.exists(CONFIG_FILE):
        config["RUTAS"] = _DEFAULT_RUTAS
        config["UI"] = {"appearance": "Dark"}
        try:
            os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                config.write(f)
        except OSError:
            pass
    config.read(CONFIG_FILE, encoding="utf-8")
    if "UI" not in config:
        config["UI"] = {"appearance": "Dark"}
    return config


config = load_config()
# Aplicar modo claro/oscuro antes de construir la ventana
_appearance = config.get("UI", "appearance", fallback="Dark") if "UI" in config else "Dark"
ctk.set_appearance_mode(_appearance)
if "RUTAS" not in config:
    _err_msg = "Error: En organizar_config.ini falta la sección [RUTAS]."
    sys.stderr.write(_err_msg + "\n")
    try:
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("Error de configuración", _err_msg)
        root.destroy()
    except Exception:
        pass
    sys.exit(1)

SOURCE_DEFAULT = config["RUTAS"].get("source", _DEFAULT_RUTAS["source"])
BASE_DEST = config["RUTAS"].get("base_dest", _DEFAULT_RUTAS["base_dest"])
BACKUP = config["RUTAS"].get("backup", _DEFAULT_RUTAS["backup"])
LOGFILE = config["RUTAS"].get("logfile", _DEFAULT_RUTAS["logfile"])
WORD_PATH = config["RUTAS"].get("word_path", "winword.exe").strip() or "winword.exe"

for ruta in (BASE_DEST, BACKUP):
    try:
        os.makedirs(ruta, exist_ok=True)
    except OSError:
        pass

# Logging
try:
    os.makedirs(os.path.dirname(LOGFILE), exist_ok=True)
except OSError:
    pass
_log_handler = RotatingFileHandler(LOGFILE, maxBytes=1024 * 1024, backupCount=1, encoding="utf-8")
_log_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"))
_logger = logging.getLogger()
_logger.setLevel(logging.INFO)
if not any(getattr(h, "baseFilename", None) == getattr(_log_handler, "baseFilename", "") for h in _logger.handlers):
    _logger.addHandler(_log_handler)

MESES = {
    1: "ENERO", 2: "FEBRERO", 3: "MARZO", 4: "ABRIL",
    5: "MAYO", 6: "JUNIO", 7: "JULIO", 8: "AGOSTO",
    9: "SEPTIEMBRE", 10: "OCTUBRE", 11: "NOVIEMBRE", 12: "DICIEMBRE"
}
_MAX_PATH_LEN = 250
_MAX_BACKUP_RETRIES = 3
_WORD_PATHS = [
    "winword.exe",
    os.path.join(os.environ.get("ProgramFiles", r"C:\Program Files"), "Microsoft Office", "root", "Office16", "WINWORD.EXE"),
    os.path.join(os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)"), "Microsoft Office", "root", "Office16", "WINWORD.EXE"),
    r"C:\Program Files\Microsoft Office\Office16\WINWORD.EXE",
    r"C:\Program Files (x86)\Microsoft Office\Office16\WINWORD.EXE",
]

# =========================
# Funciones de lógica
# =========================
def find_latest_doc(source_dir: str) -> str | None:
    """Devuelve el .doc/.docx más reciente por fecha de modificación, o None."""
    docs = find_docs_ordered(source_dir)
    return docs[0][0] if docs else None


def find_docs_ordered(source_dir: str, max_count: int = 50) -> list[tuple[str, float]]:
    """Lista .doc/.docx en source_dir ordenados por mtime descendente. Devuelve [(ruta, mtime), ...]."""
    if not os.path.isdir(source_dir):
        return []
    result = []
    for fname in os.listdir(source_dir):
        if fname.lower().endswith((".doc", ".docx")):
            fpath = os.path.join(source_dir, fname)
            try:
                mtime = os.path.getmtime(fpath)
                result.append((fpath, mtime))
            except OSError:
                continue
    result.sort(key=lambda x: x[1], reverse=True)
    return result[:max_count]


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


def parse_log_history(max_entries=20):
    entries = []
    if not os.path.exists(LOGFILE):
        return entries
    try:
        with open(LOGFILE, "r", encoding="utf-8") as f:
            lines = f.readlines()
        for line in reversed(lines[-100:]):
            if "Paciente:" in line and "→" in line:
                try:
                    parts = line.split(" - ", 2)
                    if len(parts) >= 3:
                        timestamp_str = parts[0].strip()
                        message = parts[2] if len(parts) > 2 else ""
                        if "| Paciente:" in message:
                            patient_part = message.split("| Paciente:")[1].split("|")[0].strip()
                            dest_part = message.split("→")[1].split("|")[0].strip()
                            entries.append({"timestamp": timestamp_str, "patient": patient_part, "path": dest_part})
                            if len(entries) >= max_entries:
                                break
                except Exception as e:
                    logging.debug("parse_log_history line skipped: %s", e)
                    continue
    except Exception as e:
        logging.error("Error parsing log: %s", e)
    return entries


def search_patients(query, max_results=100):
    """Busca carpetas de paciente cuyo nombre contenga query. Devuelve como máximo max_results."""
    if not query or not os.path.isdir(BASE_DEST):
        return []
    query_lower = query.lower()
    results = []
    try:
        for year in os.listdir(BASE_DEST):
            if len(results) >= max_results:
                break
            year_path = os.path.join(BASE_DEST, year)
            if not os.path.isdir(year_path):
                continue
            for month in os.listdir(year_path):
                if len(results) >= max_results:
                    break
                month_path = os.path.join(year_path, month)
                if not os.path.isdir(month_path):
                    continue
                for day in os.listdir(month_path):
                    if len(results) >= max_results:
                        break
                    day_path = os.path.join(month_path, day)
                    if not os.path.isdir(day_path):
                        continue
                    for patient in os.listdir(day_path):
                        if len(results) >= max_results:
                            break
                        patient_path = os.path.join(day_path, patient)
                        if os.path.isdir(patient_path) and query_lower in patient.lower():
                            results.append({"patient": patient, "path": patient_path, "date": f"{year}/{month}/{day}"})
    except Exception as e:
        logging.error("Error searching patients: %s", e)
    return results


def convert_doc_to_pdf(doc_path: str, pdf_path: str) -> bool:
    try:
        import win32com.client
        import pythoncom
        pythoncom.CoInitialize()
        try:
            doc_path = os.path.abspath(doc_path)
            pdf_path = os.path.abspath(pdf_path)
            doc_path_lower = doc_path.lower()
            word = None
            doc = None
            used_existing = False
            try:
                word = win32com.client.GetActiveObject("Word.Application")
                for open_doc in word.Documents:
                    try:
                        if os.path.abspath(open_doc.FullName).lower() == doc_path_lower:
                            doc = open_doc
                            used_existing = True
                            break
                    except Exception:
                        continue
            except Exception:
                pass
            if not doc:
                try:
                    if not word:
                        word = win32com.client.DispatchEx("Word.Application")
                        word.Visible = False
                        word.DisplayAlerts = 0
                    doc = word.Documents.Open(doc_path, ReadOnly=False)
                except Exception as e:
                    logging.error("Error opening Word: %s", e)
                    if word and not used_existing:
                        try:
                            word.Quit()
                        except Exception:
                            pass
                    return False
            try:
                doc.SaveAs(pdf_path, FileFormat=17)
                doc.Close(SaveChanges=False)
                return True
            except Exception as e:
                logging.error("Error saving PDF: %s", e)
                return False
            finally:
                if word and not used_existing:
                    try:
                        word.Quit()
                    except Exception:
                        pass
        finally:
            try:
                pythoncom.CoUninitialize()
            except Exception:
                pass
    except Exception as e:
        logging.error("PDF conversion error: %s", e)
        return False


def open_folder(path):
    """Abre la carpeta en el explorador. Solo abre si path es un directorio existente."""
    if path and os.path.isdir(path):
        try:
            os.startfile(path)
        except Exception as e:
            logging.error("Error opening folder: %s", e)


def save_config(new_source: str, new_dest: str, new_backup: str, word_path: str | None = None, appearance: str | None = None) -> bool:
    """Guarda rutas y opciones en el .ini. Devuelve False si las rutas son inválidas o falla la escritura."""
    s = (new_source or "").strip()
    d = (new_dest or "").strip()
    b = (new_backup or "").strip()
    if not s or not d or not b:
        logging.warning("save_config: alguna ruta está vacía")
        return False
    if s == d or s == b or d == b:
        logging.warning("save_config: las tres carpetas deben ser distintas")
        return False
    for path, name in ((s, "Origen"), (d, "Destino"), (b, "Respaldo")):
        if os.path.exists(path) and os.path.isfile(path):
            logging.warning("save_config: %s no puede ser un archivo", name)
            return False
    global SOURCE_DEFAULT, BASE_DEST, BACKUP, WORD_PATH
    config["RUTAS"]["source"] = s
    config["RUTAS"]["base_dest"] = d
    config["RUTAS"]["backup"] = b
    if word_path is not None and (word_path := (word_path or "").strip()):
        config["RUTAS"]["word_path"] = word_path
        WORD_PATH = word_path
    if appearance is not None and appearance.strip() in ("Dark", "Light", "System"):
        if "UI" not in config:
            config["UI"] = {}
        config["UI"]["appearance"] = appearance.strip()
        ctk.set_appearance_mode(config["UI"]["appearance"])
    try:
        os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            config.write(f)
        SOURCE_DEFAULT = s
        BASE_DEST = d
        BACKUP = b
        return True
    except Exception as e:
        logging.error("Error saving config: %s", e)
        return False


# =========================
# Diálogos
# =========================
class DialogBase(ctk.CTkToplevel):
    def __init__(self, parent, title, width=440, height=240):
        super().__init__(parent)
        self.title(title)
        self.geometry(f"{width}x{height}")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        self.configure(fg_color=VisionSys.CARD_DARK)
        center_window(self, width, height)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)


def show_info_dialog(parent, msg: str):
    win = DialogBase(parent, "Información", height=260)
    GlassFrame(win).place(relx=0, rely=0, relwidth=1, relheight=1)
    ctk.CTkLabel(win, text="Información", font=VisionSys.FONT_H2, text_color=VisionSys.ACCENT).pack(pady=(VisionSys.SPACE_L, VisionSys.SPACE_S), padx=VisionSys.SPACE_L, anchor="w")
    ctk.CTkLabel(win, text=msg, font=VisionSys.FONT_BODY_M, wraplength=380, justify="left", text_color=VisionSys.TEXT_PRIMARY_DARK).pack(pady=(0, VisionSys.SPACE_L), padx=VisionSys.SPACE_L, anchor="w")
    FloatingButton(win, text="Aceptar", command=win.destroy, width=120).pack(pady=VisionSys.SPACE_L, padx=VisionSys.SPACE_L, side="bottom", anchor="e")


def ask_yesno_dialog(parent, question: str, title: str = "Confirmar") -> bool:
    result = [False]
    win = DialogBase(parent, title, height=280)
    GlassFrame(win).place(relx=0, rely=0, relwidth=1, relheight=1)
    ctk.CTkLabel(win, text=title, font=VisionSys.FONT_H2, text_color=VisionSys.TEXT_PRIMARY_DARK).pack(pady=(VisionSys.SPACE_L, VisionSys.SPACE_S), padx=VisionSys.SPACE_L, anchor="w")
    ctk.CTkLabel(win, text=question, font=VisionSys.FONT_BODY_L, wraplength=380, justify="left", text_color=VisionSys.TEXT_SECONDARY_DARK).pack(pady=(0, VisionSys.SPACE_L), padx=VisionSys.SPACE_L, anchor="w", fill="both", expand=True)
    btn_frame = ctk.CTkFrame(win, fg_color="transparent")
    btn_frame.pack(pady=VisionSys.SPACE_L, padx=VisionSys.SPACE_L, side="bottom", fill="x")
    def on_yes():
        result[0] = True
        win.destroy()
    def on_no():
        result[0] = False
        win.destroy()
    FloatingButton(btn_frame, text="Sí", command=on_yes, width=110).pack(side="left", padx=(0, VisionSys.SPACE_S), expand=True)
    FloatingButton(btn_frame, text="No", command=on_no, width=110, fg_color="transparent", border_width=VisionSys.BORDER_WIDTH_SUBTLE, border_color=VisionSys.BORDER_DARK).pack(side="left", expand=True)
    parent.wait_window(win)
    return result[0]


def ask_text_dialog(parent, prompt: str, default: str = "", title: str = "Nombre del archivo") -> str | None:
    result = [None]
    win = DialogBase(parent, title, height=300)
    GlassFrame(win).place(relx=0, rely=0, relwidth=1, relheight=1)
    ctk.CTkLabel(win, text=title, font=VisionSys.FONT_H2, text_color=VisionSys.TEXT_PRIMARY_DARK).pack(pady=(VisionSys.SPACE_L, VisionSys.SPACE_XXS), padx=VisionSys.SPACE_L, anchor="w")
    ctk.CTkLabel(win, text=prompt, font=VisionSys.FONT_CAPTION, wraplength=380, justify="left", text_color=VisionSys.TEXT_SECONDARY_DARK).pack(pady=(0, VisionSys.SPACE_S), padx=VisionSys.SPACE_L, anchor="w")
    entry = ctk.CTkEntry(win, width=380, height=44, corner_radius=VisionSys.RADIUS_M, font=VisionSys.FONT_BODY_L, border_width=VisionSys.BORDER_WIDTH_SUBTLE, border_color=VisionSys.BORDER_DARK_SOFT)
    entry.pack(pady=(0, VisionSys.SPACE_S), padx=VisionSys.SPACE_L)
    entry.insert(0, default)
    def on_ok():
        result[0] = entry.get().strip()
        win.destroy()
    def on_cancel():
        result[0] = None
        win.destroy()
    entry.bind("<Return>", lambda e: on_ok())
    entry.bind("<Escape>", lambda e: on_cancel())
    entry.focus_set()
    btn_frame = ctk.CTkFrame(win, fg_color="transparent")
    btn_frame.pack(pady=VisionSys.SPACE_L, padx=VisionSys.SPACE_L, side="bottom", fill="x")
    FloatingButton(btn_frame, text="Aceptar", command=on_ok, width=110).pack(side="right", padx=(VisionSys.SPACE_S, 0))
    FloatingButton(btn_frame, text="Cancelar", command=on_cancel, width=110, fg_color="transparent", border_width=VisionSys.BORDER_WIDTH_SUBTLE, border_color=VisionSys.BORDER_DARK).pack(side="right")
    parent.wait_window(win)
    return result[0]


def ask_file_picker_dialog(parent, files_with_mtime: list[tuple[str, float]], title: str = "Elegir archivo") -> str | None:
    """Muestra lista de archivos (ruta, mtime); devuelve la ruta elegida o None."""
    if not files_with_mtime:
        return None
    if len(files_with_mtime) == 1:
        return files_with_mtime[0][0]
    result = [None]
    win = DialogBase(parent, title, width=480, height=340)
    GlassFrame(win).place(relx=0, rely=0, relwidth=1, relheight=1)
    ctk.CTkLabel(win, text=title, font=VisionSys.FONT_H2, text_color=VisionSys.TEXT_PRIMARY_DARK).pack(pady=(VisionSys.SPACE_L, VisionSys.SPACE_S), padx=VisionSys.SPACE_L, anchor="w")
    ctk.CTkLabel(win, text="Se encontró más de un documento. Elige cuál organizar (el primero es el más reciente).", font=VisionSys.FONT_CAPTION, text_color=VisionSys.TEXT_SECONDARY_DARK, wraplength=420).pack(anchor="w", padx=VisionSys.SPACE_L, pady=(0, VisionSys.SPACE_S))
    list_frame = ctk.CTkScrollableFrame(win, fg_color=VisionSys.GLASS_DARK, height=160)
    list_frame.pack(fill="x", padx=VisionSys.SPACE_L, pady=VisionSys.SPACE_S)
    for fpath, mtime in files_with_mtime:
        try:
            dt = datetime.datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M")
        except Exception:
            dt = ""
        lbl = os.path.basename(fpath) + (f"  —  {dt}" if dt else "")
        btn = ctk.CTkButton(list_frame, text=lbl, anchor="w", fg_color="transparent", hover_color=VisionSys.BORDER_DARK_HOVER, command=lambda p=fpath: (result.__setitem__(0, p), win.destroy()))
        btn.pack(fill="x", pady=2)
    def on_cancel():
        result[0] = None
        win.destroy()
    FloatingButton(win, text="Cancelar", command=on_cancel, width=110, fg_color="transparent", border_width=VisionSys.BORDER_WIDTH_SUBTLE, border_color=VisionSys.BORDER_DARK).pack(pady=VisionSys.SPACE_L)
    parent.wait_window(win)
    return result[0]


# =========================
# Vistas
# =========================
class ConfigView(ctk.CTkFrame):
    def __init__(self, parent, main_app):
        super().__init__(parent, fg_color="transparent")
        self.main_app = main_app
        SectionHeader(self, "Configuración", "Rutas de carpetas y apariencia").pack(anchor="w", pady=(0, VisionSys.SPACE_L))
        self.entries = {}
        container = GlassFrame(self)
        container.pack(fill="x", padx=0, pady=0)
        self._add_row(container, "Carpeta Origen", SOURCE_DEFAULT, "source")
        self._add_row(container, "Carpeta Destino", BASE_DEST, "dest")
        self._add_row(container, "Carpeta Respaldo", BACKUP, "backup")
        self._add_row(container, "Ruta de Word (opcional)", WORD_PATH, "word_path")
        ap_row = ctk.CTkFrame(container, fg_color="transparent")
        ap_row.pack(fill="x", padx=VisionSys.SPACE_L, pady=VisionSys.SPACE_S)
        ctk.CTkLabel(ap_row, text="Apariencia", font=VisionSys.FONT_CAPTION, text_color=VisionSys.TEXT_SECONDARY_DARK, width=140, anchor="w").pack(side="left")
        self.appearance_var = ctk.StringVar(value=config.get("UI", "appearance", fallback="Dark") if "UI" in config else "Dark")
        self.appearance_menu = ctk.CTkOptionMenu(ap_row, values=["Dark", "Light", "System"], variable=self.appearance_var, width=120, height=40)
        self.appearance_menu.pack(side="left", padx=VisionSys.SPACE_S)
        FloatingButton(self, text="Guardar Cambios", command=self.save, fg_color=VisionSys.ACCENT, hover_color=VisionSys.ACCENT_HOVER, width=200).pack(pady=VisionSys.SPACE_XL, anchor="e")

    def _add_row(self, parent, label_text, default_val, key):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", padx=VisionSys.SPACE_L, pady=VisionSys.SPACE_S)
        ctk.CTkLabel(row, text=label_text, font=VisionSys.FONT_CAPTION, text_color=VisionSys.TEXT_SECONDARY_DARK, width=140, anchor="w").pack(side="left")
        entry = ctk.CTkEntry(row, border_width=VisionSys.BORDER_WIDTH_SUBTLE, border_color=VisionSys.BORDER_DARK_SOFT, fg_color=VisionSys.GLASS_DARK, height=40, corner_radius=VisionSys.RADIUS_M, text_color=VisionSys.TEXT_PRIMARY_DARK, font=VisionSys.FONT_BODY_M)
        entry.pack(side="left", fill="x", expand=True, padx=VisionSys.SPACE_S)
        entry.insert(0, default_val)
        self.entries[key] = entry
        ctk.CTkButton(row, text="📂", width=40, height=40, fg_color=VisionSys.GLASS_DARK, hover_color=VisionSys.BORDER_DARK_HOVER, corner_radius=VisionSys.RADIUS_M, border_width=VisionSys.BORDER_WIDTH_SUBTLE, border_color=VisionSys.BORDER_DARK_SOFT,
                      command=lambda e=entry: self._browse(e)).pack(side="right")

    def _browse(self, entry_widget):
        d = filedialog.askdirectory()
        if d:
            entry_widget.delete(0, "end")
            entry_widget.insert(0, d)

    def save(self):
        s = self.entries["source"].get().strip()
        d = self.entries["dest"].get().strip()
        b = self.entries["backup"].get().strip()
        wp = self.entries.get("word_path")
        word_path_val = wp.get().strip() if wp else ""
        appearance_val = self.appearance_var.get().strip() if hasattr(self, "appearance_var") else "Dark"
        if not s or not d or not b:
            show_info_dialog(self, "Las tres carpetas son obligatorias. No dejes ninguna vacía.")
            return
        if s == d or s == b or d == b:
            show_info_dialog(self, "Las tres carpetas deben ser distintas entre sí (origen, destino, respaldo).")
            return
        for path, name in [(s, "Origen"), (d, "Destino"), (b, "Respaldo")]:
            if os.path.exists(path) and os.path.isfile(path):
                show_info_dialog(self, f"«{name}» debe ser una carpeta, no un archivo.")
                return
        if save_config(s, d, b, word_path=word_path_val or None, appearance=appearance_val):
            show_info_dialog(self, "Configuración guardada correctamente.")
        else:
            show_info_dialog(self, "No se pudo guardar la configuración.")


class HistoryView(ctk.CTkFrame):
    def __init__(self, parent, main_app):
        super().__init__(parent, fg_color="transparent")
        self.main_app = main_app
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", pady=(0, VisionSys.SPACE_S))
        header.grid_columnconfigure(0, weight=1)
        SectionHeader(header, "Historial", "Últimos archivos procesados").grid(row=0, column=0, sticky="w")
        FloatingButton(header, text="Actualizar", width=120, command=self._refresh).grid(row=0, column=1, padx=VisionSys.SPACE_S)
        self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_frame.pack(fill="both", expand=True, pady=(VisionSys.SPACE_M, 0))
        self._refresh()

    def _refresh(self):
        for w in self.scroll_frame.winfo_children():
            w.destroy()
        entries = parse_log_history()
        if not entries:
            ctk.CTkLabel(self.scroll_frame, text="No hay historial disponible", font=VisionSys.FONT_BODY_M, text_color=VisionSys.TEXT_TERTIARY_DARK).pack(pady=VisionSys.SPACE_XXL)
        else:
            for entry in entries:
                GlassCard(self.scroll_frame, icon="🕒", title=entry["patient"], subtitle=entry["timestamp"],
                          command=lambda p=entry["path"]: open_folder(p)).pack(fill="x", pady=VisionSys.SPACE_XS)


class SearchView(ctk.CTkFrame):
    def __init__(self, parent, main_app):
        super().__init__(parent, fg_color="transparent")
        self.main_app = main_app
        SectionHeader(self, "Buscar Paciente", "Escribe el nombre para buscar en las carpetas").pack(anchor="w", pady=(0, VisionSys.SPACE_L))
        search_frame = GlassFrame(self)
        search_frame.pack(fill="x", pady=(0, VisionSys.SPACE_L))
        self.search_entry = ctk.CTkEntry(search_frame, placeholder_text="Escribe el nombre…",
                                         border_width=VisionSys.BORDER_WIDTH_SUBTLE, border_color=VisionSys.BORDER_DARK_SOFT, height=48, font=VisionSys.FONT_BODY_L, fg_color="transparent", text_color=VisionSys.TEXT_PRIMARY_DARK, corner_radius=VisionSys.RADIUS_M)
        self.search_entry.pack(side="left", fill="x", expand=True, padx=VisionSys.SPACE_L, pady=VisionSys.SPACE_S)
        self.search_entry.bind("<Return>", lambda e: self.perform_search())
        FloatingButton(search_frame, text="🔍", width=52, height=44, command=self.perform_search).pack(side="right", padx=VisionSys.SPACE_S, pady=VisionSys.SPACE_S)
        self.results_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.results_frame.pack(fill="both", expand=True, pady=(VisionSys.SPACE_M, 0))
        ctk.CTkLabel(self.results_frame, text="Resultados aparecerán aquí", font=VisionSys.FONT_BODY_M, text_color=VisionSys.TEXT_TERTIARY_DARK).pack(pady=VisionSys.SPACE_XXL)

    def perform_search(self):
        query = self.search_entry.get().strip()
        for w in self.results_frame.winfo_children():
            w.destroy()
        if not query:
            return
        ctk.CTkLabel(self.results_frame, text="Buscando…", font=VisionSys.FONT_BODY_M, text_color=VisionSys.TEXT_SECONDARY_DARK).pack(pady=VisionSys.SPACE_XXL)
        self.results_frame.update()

        def run_in_background():
            results = search_patients(query)
            self.after(0, lambda: self._show_search_results(query, results))

        threading.Thread(target=run_in_background, daemon=True).start()

    def _show_search_results(self, query: str, results: list):
        for w in self.results_frame.winfo_children():
            w.destroy()
        if not results:
            ctk.CTkLabel(self.results_frame, text=f"Sin resultados para «{query}»", font=VisionSys.FONT_BODY_M, text_color=VisionSys.TEXT_SECONDARY_DARK).pack(pady=VisionSys.SPACE_XXL)
        else:
            _max = 100
            if len(results) >= _max:
                ctk.CTkLabel(self.results_frame, text=f"Mostrando los primeros {_max} resultados.", font=VisionSys.FONT_CAPTION, text_color=VisionSys.TEXT_SECONDARY_DARK).pack(anchor="w", pady=(0, VisionSys.SPACE_S))
            for r in results:
                GlassCard(self.results_frame, icon="📂", title=r["patient"], subtitle=r["date"],
                          command=lambda p=r["path"]: open_folder(p)).pack(fill="x", pady=VisionSys.SPACE_XS)


class HomeView(ctk.CTkFrame):
    def __init__(self, parent, main_app):
        super().__init__(parent, fg_color="transparent")
        self.main_app = main_app
        # Títulos grandes y seguros, mucho espacio
        ctk.CTkLabel(self, text="Organizador", font=VisionSys.FONT_H1, text_color=VisionSys.TEXT_PRIMARY_DARK).pack(anchor="w")
        ctk.CTkLabel(self, text="de Terapias", font=VisionSys.FONT_H1, text_color=VisionSys.TEXT_SECONDARY_DARK).pack(anchor="w", pady=(VisionSys.SPACE_XXS, 0))

        # Widget integrado: selector de carpeta dentro de panel tipo vidrio
        path_card = GlassFrame(self)
        path_card.pack(fill="x", pady=(VisionSys.SPACE_XL, VisionSys.SPACE_M))
        ctk.CTkLabel(path_card, text="Carpeta donde buscar archivos", font=VisionSys.FONT_CAPTION, text_color=VisionSys.TEXT_SECONDARY_DARK).pack(anchor="w", padx=VisionSys.SPACE_L, pady=(VisionSys.SPACE_L, VisionSys.SPACE_XXS))
        path_inner = ctk.CTkFrame(path_card, fg_color="transparent")
        path_inner.pack(fill="x", padx=VisionSys.SPACE_L, pady=(0, VisionSys.SPACE_L))
        path_inner.grid_columnconfigure(0, weight=1)
        self.path_entry = ctk.CTkEntry(path_inner, height=44, font=VisionSys.FONT_BODY_M, placeholder_text=SOURCE_DEFAULT, border_width=VisionSys.BORDER_WIDTH_SUBTLE, border_color=VisionSys.BORDER_DARK_SOFT, fg_color=VisionSys.GLASS_DARK, corner_radius=VisionSys.RADIUS_M)
        self.path_entry.grid(row=0, column=0, sticky="ew", padx=(0, VisionSys.SPACE_S))
        initial = SOURCE_DEFAULT if os.path.isdir(SOURCE_DEFAULT) else _user_home
        self.path_entry.insert(0, initial)
        ctk.CTkButton(path_inner, text="Examinar…", width=110, height=44, fg_color=VisionSys.ACCENT, hover_color=VisionSys.ACCENT_HOVER, corner_radius=VisionSys.RADIUS_M, command=self._browse_folder).grid(row=0, column=1)

        # Barra de estado: limpia, redondeada, no invasiva
        self.status_frame = ctk.CTkFrame(self, fg_color=VisionSys.GLASS_DARK, corner_radius=VisionSys.RADIUS_L, height=48, border_width=VisionSys.BORDER_WIDTH_SUBTLE, border_color=VisionSys.BORDER_DARK_SOFT)
        self.status_frame.pack(fill="x", pady=VisionSys.SPACE_L)
        self.status_lbl = ctk.CTkLabel(self.status_frame, text="Listo. Selecciona carpeta y haz clic en Buscar y organizar.", font=VisionSys.FONT_BODY_M, text_color=VisionSys.TEXT_SECONDARY_DARK)
        self.status_lbl.pack(pady=VisionSys.SPACE_S, padx=VisionSys.SPACE_L)

        # Acciones principales: botones protagonistas, bien separados
        self.btn_organize = FloatingButton(self, text="Buscar y Organizar (Word)", height=56, font=VisionSys.FONT_H2, command=self.run_organize)
        self.btn_organize.pack(fill="x", pady=VisionSys.SPACE_S)
        add_tooltip(self.btn_organize, "Busca el documento más reciente en la carpeta, pide el nombre y lo organiza en la estructura Año/Mes/Día/Paciente.")

        self.btn_open_folder = FloatingButton(
            self, text="Abrir carpeta del paciente",
            height=48, font=VisionSys.FONT_BODY_L,
            command=self.open_patient_folder,
            fg_color=VisionSys.GLASS_DARK, hover_color=VisionSys.BORDER_DARK_HOVER, text_color=VisionSys.TEXT_SECONDARY_DARK,
            state="disabled"
        )
        self.btn_open_folder.pack(fill="x", pady=VisionSys.SPACE_S)
        add_tooltip(self.btn_open_folder, "Abre la carpeta del paciente del último archivo organizado.")

        self.btn_pdf = FloatingButton(self, text="Finalizar (PDF)", height=56, font=VisionSys.FONT_H2,
                                      fg_color=VisionSys.WARNING, hover_color=VisionSys.WARNING_HOVER, text_color="#1d1d1f",
                                      state="disabled", command=self.run_pdf_conversion)
        self.btn_pdf.pack(fill="x", pady=VisionSys.SPACE_S)
        add_tooltip(self.btn_pdf, "Genera el PDF desde el documento Word y mueve el .doc a respaldo.")

        # Tarjeta que flota: acceso rápido a carpeta origen
        self.folder_card = GlassCard(self, icon="📁", title="Carpeta Origen por defecto",
                                     subtitle=os.path.basename(SOURCE_DEFAULT) or "...",
                                     command=lambda: open_folder(SOURCE_DEFAULT))
        self.folder_card.pack(fill="x", pady=VisionSys.SPACE_XL)

        self.current_doc_path = None
        self.current_pdf_path = None
        self.last_patient_folder = None

    def on_show(self):
        """Actualiza path_entry y folder_card con los valores actuales de configuración (al volver a Inicio)."""
        self.path_entry.delete(0, "end")
        initial = SOURCE_DEFAULT if os.path.isdir(SOURCE_DEFAULT) else _user_home
        self.path_entry.insert(0, initial)
        self.folder_card.lbl_sub.configure(text=os.path.basename(SOURCE_DEFAULT) or "...")

    def _browse_folder(self):
        initial = self.path_entry.get().strip() if self.path_entry.get().strip() and os.path.isdir(self.path_entry.get().strip()) else _user_home
        folder = filedialog.askdirectory(title="Seleccionar carpeta para buscar archivos", initialdir=initial)
        if folder:
            self.path_entry.delete(0, "end")
            self.path_entry.insert(0, folder)

    def set_status(self, msg, is_error=False):
        color = VisionSys.ERROR if is_error else "gray80"
        self.status_lbl.configure(text=msg, text_color=color)
        self.update()

    def open_patient_folder(self):
        if self.last_patient_folder and os.path.exists(self.last_patient_folder):
            open_folder(self.last_patient_folder)
        else:
            self.set_status("No hay carpeta de paciente disponible.", True)

    def run_organize(self):
        set_status = self.set_status
        source_folder = self.path_entry.get().strip() or SOURCE_DEFAULT
        if not source_folder:
            set_status("Selecciona una carpeta donde buscar los archivos.", True)
            return
        if not os.path.isdir(source_folder):
            set_status(f"La carpeta no existe:\n{source_folder}", True)
            return

        set_status("Buscando archivos .doc y .docx...")
        self.update()
        docs_ordered = find_docs_ordered(source_folder)
        if not docs_ordered:
            set_status("No se encontró ningún archivo .doc o .docx. Elige otra carpeta o añade un documento.", True)
            return
        latest_file = ask_file_picker_dialog(self, docs_ordered, title="Elegir archivo a organizar")
        if not latest_file:
            set_status("Operación cancelada.")
            return

        archivo_a_organizar = os.path.basename(latest_file)
        set_status(f"Archivo encontrado: {archivo_a_organizar}. Solicitando nombre...")

        prompt = (
            f"Archivo a organizar: {archivo_a_organizar}\n\n"
            "Escribe el nuevo nombre (sin extensión).\n"
            "Si escribes 'SS Nombre Paciente', la carpeta del paciente se creará con ese nombre."
        )
        user_name = ask_text_dialog(self, prompt, title="Nombre del archivo")
        if user_name is None:
            set_status("Operación cancelada.")
            return
        if not user_name.strip():
            set_status("El nombre no puede estar vacío.", True)
            return

        user_name = sanitize_filename(user_name)
        paciente = patient_from_user_input(user_name)
        if paciente == "PACIENTE_DESCONOCIDO":
            if ask_yesno_dialog(self, "⚠️ Faltó 'SS' en el nombre.\n¿Quieres corregirlo?", title="Validación"):
                return self.run_organize()
            # Si no corrige, continuamos con PACIENTE_DESCONOCIDO

        hoy = datetime.date.today()
        ruta_anio, ruta_mes, ruta_dia, _ = build_folder_structure(BASE_DEST, hoy.year, hoy.month, hoy.day, MESES)
        destino_paciente = os.path.join(ruta_dia, paciente)
        anio = os.path.basename(ruta_anio)
        mes_nombre = os.path.basename(ruta_mes)
        dia_nombre = os.path.basename(ruta_dia)

        for r in (ruta_anio, ruta_mes, ruta_dia, destino_paciente, BACKUP):
            os.makedirs(r, exist_ok=True)

        ext = os.path.splitext(latest_file)[1].lower()
        if ext not in (".doc", ".docx"):
            ext = ".docx"
        stem, n = user_name, 0
        while True:
            doc_name = f"{stem}_{n}" if n else stem
            new_doc_path = os.path.join(destino_paciente, doc_name + ext)
            if not os.path.exists(new_doc_path):
                break
            n += 1

        if not check_path_length(new_doc_path, _MAX_PATH_LEN):
            set_status("La ruta del archivo es demasiado larga para Windows. Usa un nombre más corto.", True)
            return

        confirmacion = (
            f"¿Organizar el archivo\n{archivo_a_organizar}\n\n"
            f"como: {user_name}{ext}\n"
            f"Paciente: {paciente}\n"
            f"Destino: {destino_paciente}\n\n"
            "¿Continuar?"
        )
        if not ask_yesno_dialog(self, confirmacion, title="Confirmar organización"):
            set_status("Operación cancelada.")
            return

        try:
            shutil.move(latest_file, new_doc_path)
        except Exception as e:
            logging.error("No se pudo mover %s → %s: %s", latest_file, new_doc_path, e)
            set_status(f"No se pudo mover el archivo:\n{e}", True)
            return

        open_folder(destino_paciente)
        show_info_dialog(
            self,
            f"Abriendo Word…\n\n"
            f"Guarda como PDF con el nombre: {user_name}.pdf\n"
            f"Carpeta destino: {destino_paciente}\n\n"
            "Cuando termines, cierra Word y pulsa «Finalizar (PDF)» en esta ventana.\n"
            "La app no se bloqueará mientras Word esté abierto."
        )

        word_exe = find_word_executable()
        if word_exe:
            try:
                subprocess.Popen(["start", "", word_exe, new_doc_path], shell=True)
            except Exception as e:
                logging.error("No se pudo abrir Word: %s", e)
                set_status(f"No se pudo abrir Word:\n{e}", True)
        else:
            subprocess.Popen(["start", new_doc_path], shell=True)

        show_info_dialog(
            self,
            f"Recuerda: guarda el PDF en:\n{destino_paciente}\n\n"
            f"Nombre: {user_name}.pdf\n\n"
            "Cuando cierres Word, pulsa «Finalizar (PDF)» para generar el PDF y mover el .doc a respaldo."
        )

        self.current_doc_path = new_doc_path
        self.current_pdf_path = os.path.join(destino_paciente, user_name + ".pdf")
        self.last_patient_folder = destino_paciente
        self.btn_organize.configure(state="disabled", fg_color=VisionSys.GLASS_DARK)
        self.btn_pdf.configure(state="normal", fg_color=VisionSys.WARNING)
        self.btn_open_folder.configure(state="normal", fg_color=VisionSys.ACCENT, hover_color=VisionSys.ACCENT_HOVER, text_color="#ffffff")

        # Mover Word a respaldo con reintentos (mejora del proyecto actual)
        if os.path.exists(new_doc_path):
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            base_backup = os.path.splitext(os.path.basename(new_doc_path))[0]
            ext_backup = os.path.splitext(new_doc_path)[1]
            backup_path = os.path.join(BACKUP, f"{base_backup}_{timestamp}{ext_backup}")
            for intento in range(_MAX_BACKUP_RETRIES):
                try:
                    shutil.move(new_doc_path, backup_path)
                    set_status(f"✓ Completado. Respaldo: {os.path.basename(backup_path)}\nEl PDF debe estar en la carpeta del paciente.")
                    break
                except Exception as e:
                    logging.error("Intento %s/%s respaldo: %s", intento + 1, _MAX_BACKUP_RETRIES, e)
                    if intento < _MAX_BACKUP_RETRIES - 1:
                        set_status(f"Reintentando respaldo... ({intento + 1}/{_MAX_BACKUP_RETRIES})")
                        self.update()
                        time.sleep(3)
                    else:
                        set_status(f"No se pudo mover a Respaldo tras {_MAX_BACKUP_RETRIES} intentos.", True)
        else:
            set_status("Proceso completado. Recuerda guardar el PDF en la carpeta del paciente.")

        logging.info(
            "Esperado PDF: %s → %s | Paciente: %s | Fecha: %s/%s/%s",
            user_name + ".pdf", destino_paciente, paciente, anio, mes_nombre, dia_nombre
        )

    def run_pdf_conversion(self):
        if not self.current_doc_path or not os.path.exists(self.current_doc_path):
            self.set_status("Error: Archivo original no encontrado.", True)
            self._reset_ui()
            return
        self.set_status("Generando PDF...")
        self.update()
        success = convert_doc_to_pdf(self.current_doc_path, self.current_pdf_path)
        if not success:
            self.set_status("No se pudo crear el PDF. ¿Cerraste Word?", True)
            return
        if os.path.exists(self.current_pdf_path):
            self.set_status("Moviendo a respaldo...")
            self.update()
            try:
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                base = os.path.basename(self.current_doc_path)
                backup_path = os.path.join(BACKUP, f"{timestamp}_{base}")
                shutil.move(self.current_doc_path, backup_path)
                show_info_dialog(self, "¡Listo!\nPDF creado en la carpeta del paciente.")
                self.set_status("Proceso finalizado.")
            except Exception as e:
                self.set_status(f"Error al mover a respaldo: {e}", True)
        else:
            self.set_status("PDF no detectado en la carpeta.", True)
        self._reset_ui()

    def _reset_ui(self):
        self.btn_organize.configure(state="normal", fg_color=VisionSys.ACCENT_GREEN)
        self.btn_pdf.configure(state="disabled", fg_color=VisionSys.WARNING)
        self.current_doc_path = None
        self.btn_open_folder.configure(state="disabled", fg_color=VisionSys.GLASS_DARK, hover_color=VisionSys.BORDER_DARK_HOVER, text_color=VisionSys.TEXT_SECONDARY_DARK)


# =========================
# App principal
# =========================
class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Organizador de Terapias")
        self.geometry("920x680")
        self.deiconify()
        self.lift()
        self.focus_force()
        self.attributes("-alpha", 1.0)
        self.configure(fg_color=VisionSys.BG_DARK)

        self.last_width = 0
        self.last_height = 0
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Sidebar: listas claras, iconografía sutil, separaciones limpias, sensación fluida
        self.sidebar = ctk.CTkFrame(self, width=240, fg_color=VisionSys.SURFACE_DARK, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="ns", padx=0, pady=0)
        self.sidebar.grid_propagate(False)
        ctk.CTkLabel(self.sidebar, text="SCRIPS", font=VisionSys.FONT_H1, text_color=VisionSys.TEXT_PRIMARY_DARK, anchor="w").pack(pady=(VisionSys.SPACE_XL, VisionSys.SPACE_XXL), padx=VisionSys.SPACE_L, fill="x")

        self.nav_btns = {}
        self._create_nav_btn("Inicio", HomeView, "🏠")
        self._create_nav_btn("Configuración", ConfigView, "⚙")
        self._create_nav_btn("Historial", HistoryView, "📜")
        self._create_nav_btn("Buscar", SearchView, "🔍")
        ctk.CTkButton(self.sidebar, text="Salir", command=self.quit_app, fg_color=VisionSys.ERROR, hover_color=VisionSys.ERROR_HOVER, corner_radius=VisionSys.RADIUS_M, height=44, font=VisionSys.FONT_BODY_M).pack(side="bottom", pady=VisionSys.SPACE_L, padx=VisionSys.SPACE_S, fill="x")

        self.main_container = ctk.CTkFrame(self, fg_color=VisionSys.BG_DARK)
        self.main_container.grid(row=0, column=1, sticky="nsew", padx=VisionSys.SPACE_L, pady=VisionSys.SPACE_L)
        self.main_container.grid_columnconfigure(0, weight=1)
        self.main_container.grid_rowconfigure(0, weight=1)
        self.current_view = None
        self.show_view("Inicio")
        self._bind_shortcuts()

        # Efecto Acrylic/Blur tras mostrar ventana (Windows 11)
        self.after(100, lambda: apply_acrylic(self))

    def _bind_shortcuts(self):
        self.bind("<Control-o>", lambda e: (self.show_view("Inicio"), self.after(50, lambda: getattr(self.current_view, "path_entry", None) and self.current_view.path_entry.focus_set())))
        self.bind("<Control-O>", lambda e: (self.show_view("Inicio"), self.after(50, lambda: getattr(self.current_view, "path_entry", None) and self.current_view.path_entry.focus_set())))
        self.bind("<F5>", self._on_f5)
        self.bind("<Control-Return>", self._on_f5)
        self.bind("<Control-r>", self._on_ctrl_r)
        self.bind("<Control-R>", self._on_ctrl_r)
        self.bind("<Control-f>", self._on_ctrl_f)
        self.bind("<Control-F>", self._on_ctrl_f)

    def _on_f5(self, event=None):
        if isinstance(self.current_view, HomeView):
            self.current_view.run_organize()

    def _on_ctrl_r(self, event=None):
        if isinstance(self.current_view, HistoryView):
            self.current_view._refresh()

    def _on_ctrl_f(self, event=None):
        self.show_view("Buscar")
        self.after(50, lambda: getattr(self.current_view, "search_entry", None) and self.current_view.search_entry.focus_set())

    def _create_nav_btn(self, name, view_class, icon):
        btn = ctk.CTkButton(
            self.sidebar, text=f"   {icon}   {name}", anchor="w",
            font=VisionSys.FONT_BODY_M, height=46, corner_radius=VisionSys.RADIUS_M,
            fg_color="transparent", text_color=VisionSys.TEXT_PRIMARY_DARK,
            hover_color=VisionSys.BORDER_DARK_HOVER,
            command=lambda: self.show_view(name)
        )
        btn.pack(pady=VisionSys.SPACE_XS, padx=VisionSys.SPACE_S, fill="x")
        self.nav_btns[name] = {"btn": btn, "view": view_class}

    def show_view(self, name):
        for key, val in self.nav_btns.items():
            val["btn"].configure(fg_color=VisionSys.GLASS_DARK if key == name else "transparent")
        # Sensación de transición: el contenido se actualiza sin cortes
        if self.current_view:
            self.current_view.pack_forget()
            self.current_view.destroy()
        try:
            self.current_view = self.nav_btns[name]["view"](self.main_container, self)
            self.current_view.pack(fill="both", expand=True, padx=VisionSys.SPACE_M, pady=VisionSys.SPACE_M)
            getattr(self.current_view, "on_show", lambda: None)()
        except Exception as e:
            lbl = ctk.CTkLabel(self.main_container, text=f"Error al cargar vista: {e}", text_color=VisionSys.ERROR)
            lbl.pack()
            logging.exception("View error: %s", e)

    def quit_app(self):
        self.destroy()


if __name__ == "__main__":
    try:
        app = App()
        center_window(app, 920, 680)
        app.mainloop()
    except Exception as e:
        with open("error_crash.txt", "w", encoding="utf-8") as f:
            f.write(f"Startup Crash: {e}\n")
            import traceback
            traceback.print_exc(file=f)
        messagebox.showerror("Error Fatal", f"La aplicación ha fallado al iniciar.\n\n{e}")
