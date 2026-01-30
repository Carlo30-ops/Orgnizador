# -*- mode: python ; coding: utf-8 -*-
import os
from PyInstaller.utils.hooks import collect_data_files

project_dir = os.path.dirname(os.path.abspath(SPEC))
ctk_datas = collect_data_files("customtkinter")
icon_path = os.path.join(project_dir, "image-removebg-preview.ico")

a = Analysis(
    ["terapias.py"],
    pathex=[project_dir],
    binaries=[],
    datas=ctk_datas,
    hiddenimports=[
        "terapias_logic",
        "ui_components",
        "win32com.client",
        "pythoncom",
        "pywintypes",
        "win32api",
        "win32con",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="terapias",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=icon_path if os.path.isfile(icon_path) else None,
)
