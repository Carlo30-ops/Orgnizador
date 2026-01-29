# -*- mode: python ; coding: utf-8 -*-
import os

# Directorio del proyecto (terapias.py, terapias_logic.py)
project_dir = os.path.dirname(os.path.abspath(SPEC))

a = Analysis(
    ['terapias.py'],
    pathex=[project_dir],
    binaries=[],
    datas=[],
    hiddenimports=['terapias_logic'],
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
    name='terapias',
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
)
