# -*- mode: python ; coding: utf-8 -*-
"""
Especificación para PyInstaller - PyQt6 GUI
"""
import sys
import os
from PyInstaller.utils.hooks import collect_all

block_cipher = None
basedir = os.path.abspath('.')

# Recopilar todas las dependencias importantes
datas = []
binaries = []
hiddenimports = []

# 1. Recopilar dependencias complejas
packages_to_collect = [
    'PyQt6',
    'selenium',
    'pandas',
    'webdriver_manager',
    'requests',
    'certifi',
    'urllib3',
    'idna',
    'charset_normalizer'
]

for package in packages_to_collect:
    try:
        tmp_ret = collect_all(package)
        datas += tmp_ret[0]
        binaries += tmp_ret[1]
        hiddenimports += tmp_ret[2]
    except Exception as e:
        print(f"Warning: Could not collect {package}: {e}")

# 2. Agregar archivos del proyecto
datas.append((os.path.join(basedir, 'scrapers'), 'scrapers'))
datas.append((os.path.join(basedir, 'src'), 'src'))
datas.append((os.path.join(basedir, 'version.txt'), '.'))  # Incluir version.txt en la raíz

# 3. Imports ocultos adicionales explícitos
hiddenimports += [
    'scrapers.nike',
    'scrapers.sephora',
    'src.config.settings',
    'openpyxl',
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
    console=False, # GUI application
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
