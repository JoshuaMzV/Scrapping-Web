# -*- mode: python ; coding: utf-8 -*-
import sys
import os
from PyInstaller.utils.hooks import collect_all, collect_submodules, collect_data_files

block_cipher = None

basedir = os.path.abspath('.')

datas = []
binaries = []
hiddenimports = []

# Agregar templates y static
datas.append((os.path.join(basedir, 'templates'), 'templates'))
datas.append((os.path.join(basedir, 'static'), 'static'))

print("[INFO] Recopilando submódulos...")

# PyQt6 y dependencias
hiddenimports += collect_submodules('PyQt6')
hiddenimports += collect_submodules('pyqt6')

# Paquetes principales
hiddenimports += collect_submodules('selenium')
hiddenimports += collect_submodules('pandas')
hiddenimports += collect_submodules('numpy')
hiddenimports += collect_submodules('openpyxl')
hiddenimports += collect_submodules('requests')
hiddenimports += collect_submodules('webdriver_manager')

# Módulos del proyecto
hiddenimports += collect_submodules('scrapers')
hiddenimports += collect_submodules('src')

# Recopilar datos/binarios
packages_for_data = ['PyQt6', 'selenium', 'pandas', 'numpy', 'openpyxl']

for pkg in packages_for_data:
    try:
        pkg_datas, pkg_binaries, _ = collect_all(pkg)
        datas += pkg_datas
        binaries += pkg_binaries
        print(f"[OK] {pkg}")
    except Exception as e:
        print(f"[WARNING] {pkg}: {e}")

# Imports críticos explícitos
hiddenimports += [
    'PyQt6.QtCore',
    'PyQt6.QtGui',
    'PyQt6.QtWidgets',
    'selenium.webdriver.chrome.service',
    'selenium.webdriver.common.by',
    'pandas._libs',
    'pandas._libs.tslibs',
    'openpyxl.cell._writer',
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
    excludes=['matplotlib', 'tkinter', 'test', 'PyQt5'],
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
