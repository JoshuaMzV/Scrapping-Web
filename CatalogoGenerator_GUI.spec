# -*- mode: python ; coding: utf-8 -*-
"""
Especificación para PyInstaller - PyQt6 GUI (Debug Version)
"""
import sys
import os
import importlib.util

# --- DEBUG SECTION ---
print("--- DEBUG: SYS.PATH ---")
for p in sys.path:
    print(p)
print("-----------------------")

def check_import(name):
    try:
        spec = importlib.util.find_spec(name)
        if spec:
            print(f"DEBUG: Found {name} at {spec.origin}")
        else:
            print(f"DEBUG: Could NOT find {name} (spec is None)")
    except Exception as e:
        print(f"DEBUG: Error finding {name}: {e}")

check_import('requests')
check_import('pandas')
check_import('selenium')
check_import('PyQt6')
check_import('openpyxl')
# ---------------------

block_cipher = None
basedir = os.path.abspath('.')

# Recopilar todas las dependencias importantes
datas = []
binaries = []
hiddenimports = []

# Agregar archivos del proyecto
datas.append((os.path.join(basedir, 'scrapers'), 'scrapers'))
datas.append((os.path.join(basedir, 'src'), 'src'))
datas.append((os.path.join(basedir, 'version.txt'), '.'))

# Imports ocultos explícitos
hiddenimports += [
    'scrapers.nike',
    'scrapers.sephora',
    'src.config.settings',
    'openpyxl',
    'requests',
    'selenium',
    'pandas',
    'webdriver_manager',
    'certifi',
    'urllib3',
    'idna',
    'charset_normalizer',
    'json',
    'base64',
    'logging',
    're',
    'subprocess',
    'time',
    'datetime',
    'io',
    'pathlib',
    'threading'
]

a = Analysis(
    ['app_gui.py'],
    pathex=[basedir],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['matplotlib', 'tkinter', 'test', 'tests', 'notebook', 'ipython'],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='CatalogoGenerator',
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
