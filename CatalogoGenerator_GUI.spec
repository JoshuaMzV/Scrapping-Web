# -*- mode: python ; coding: utf-8 -*-
"""
Especificación simplificada para PyInstaller - PyQt6 GUI
"""
import sys
import os
from PyInstaller.utils.hooks import collect_all, collect_data_files

block_cipher = None
basedir = os.path.abspath('.')

datas = []
binaries = []
hiddenimports = [
    # PyQt6 - Requerimientos mínimos
    'PyQt6.QtCore',
    'PyQt6.QtGui',
    'PyQt6.QtWidgets',
    
    # HTTP requests (para auto-update)
    'requests',
    'urllib3',
    'certifi',
    'charset_normalizer',
    'idna',
    
    # Selenium
    'selenium.webdriver.chrome.service',
    'selenium.webdriver.common.by',
    'selenium.webdriver.support',
    'selenium.webdriver.support.ui',
    'selenium.webdriver.support.expected_conditions',
    'webdriver_manager.chrome',
    'webdriver_manager.drivers.chrome',
    
    # Pandas
    'pandas.core.arrays',
    'pandas.core.computation',
    'pandas._libs',
    
    # NumPy
    'numpy.core._multiarray_umath',
    'numpy.random',
    
    # OpenPyXL
    'openpyxl.cell._writer',
    'openpyxl.worksheet',
    'openpyxl.utils.dataframe',
    
    # Proyecto
    'scrapers.nike',
    'scrapers.sephora',
    'src.config.settings',
]

# Datos adicionales
datas.append((os.path.join(basedir, 'scrapers'), 'scrapers'))
datas.append((os.path.join(basedir, 'src'), 'src'))

# Recopilar solo lo esencial de PyQt6
try:
    pkg_datas, pkg_binaries, _ = collect_all('PyQt6')
    datas += pkg_datas
    binaries += pkg_binaries
except:
    pass

a = Analysis(
    ['app_gui.py'],
    pathex=[basedir],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['matplotlib', 'tkinter', 'test', 'tests', 'PyQt5'],
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
