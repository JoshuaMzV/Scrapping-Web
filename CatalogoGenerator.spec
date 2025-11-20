# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_submodules

hiddenimports = ['flask', 'pandas', 'selenium', 'openpyxl']
hiddenimports += collect_submodules('scrapers')
hiddenimports += collect_submodules('src')


a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=[],
    datas=[('D:\\Documentos Joshua\\VS\\scraping_project\\scraping_project\\templates', 'templates'), ('D:\\Documentos Joshua\\VS\\scraping_project\\scraping_project\\static', 'static')],
    hiddenimports=hiddenimports,
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
