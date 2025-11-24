# -*- mode: python ; coding: utf-8 -*-
import sys
import os

block_cipher = None
basedir = os.path.abspath('.')

a = Analysis(
    ['app_gui.py'],
    pathex=[basedir],
    binaries=[],
    datas=[
        (os.path.join(basedir, 'scrapers'), 'scrapers'),
        (os.path.join(basedir, 'src'), 'src'),
        (os.path.join(basedir, 'version.txt'), '.')
    ],
    hiddenimports=[
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
        'threading',
        'pyperclip'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['matplotlib', 'tkinter', 'test', 'tests', 'notebook', 'ipython', 'PyQt5', 'Qt5'],
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
