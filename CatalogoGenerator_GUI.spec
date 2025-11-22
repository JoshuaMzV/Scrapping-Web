# -*- mode: python ; coding: utf-8 -*-
"""
Especificación para PyInstaller - PyQt6 GUI
"""
import sys
import os
import site
from PyInstaller.utils.hooks import collect_all

block_cipher = None
basedir = os.path.abspath('.')

# Intentar obtener site-packages
try:
    site_packages = site.getsitepackages()
except AttributeError:
    # Fallback para virtualenvs que a veces no tienen getsitepackages
    site_packages = [os.path.join(sys.prefix, 'Lib', 'site-packages')]

print(f"DEBUG: Site packages: {site_packages}")

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
    print(f"Collecting {package}...")
    # Eliminamos try-except para que falle si no encuentra algo
    tmp_ret = collect_all(package)
    datas += tmp_ret[0]
    binaries += tmp_ret[1]
    hiddenimports += tmp_ret[2]

# 2. Agregar archivos del proyecto
datas.append((os.path.join(basedir, 'scrapers'), 'scrapers'))
datas.append((os.path.join(basedir, 'src'), 'src'))
datas.append((os.path.join(basedir, 'version.txt'), '.'))

# 3. Imports ocultos adicionales explícitos
hiddenimports += [
    'scrapers.nike',
    'scrapers.sephora',
    'src.config.settings',
    'openpyxl',
    'requests', # Forzar requests
]

a = Analysis(
    ['app_gui.py'],
    pathex=[basedir] + site_packages, # Agregar site-packages explícitamente
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
