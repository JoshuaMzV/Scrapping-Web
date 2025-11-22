# -*- mode: python ; coding: utf-8 -*-
"""
Especificación para PyInstaller - PyQt6 GUI
"""
import sys
import os
from PyInstaller.utils.hooks import collect_all, collect_submodules

block_cipher = None
basedir = os.path.abspath('.')

# Recopilar todas las dependencias importantes
datas = []
binaries = []
hiddenimports = []

# 1. Recopilar PyQt6 completo (necesario para plugins/estilos)
try:
    tmp_ret = collect_all('PyQt6')
    datas += tmp_ret[0]
    binaries += tmp_ret[1]
    hiddenimports += tmp_ret[2]
except Exception as e:
    print(f"Warning: Could not collect PyQt6: {e}")

# 2. Agregar archivos del proyecto
datas.append((os.path.join(basedir, 'scrapers'), 'scrapers'))
datas.append((os.path.join(basedir, 'src'), 'src'))
datas.append((os.path.join(basedir, 'version.txt'), '.'))

# 3. Imports ocultos explícitos para asegurar que PyInstaller los vea
# Estos módulos suelen tener hooks, pero los forzamos por si acaso
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

# Recopilar submodulos de paquetes grandes para evitar problemas de importación
hiddenimports += collect_submodules('selenium')
hiddenimports += collect_submodules('pandas')
hiddenimports += collect_submodules('requests')

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
