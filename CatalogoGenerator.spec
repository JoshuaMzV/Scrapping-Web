# -*- mode: python ; coding: utf-8 -*-
import sys
import os
from PyInstaller.utils.hooks import collect_all, collect_submodules, collect_data_files

block_cipher = None

# Recopilar TODAS las dependencias de forma agresiva
datas = []
binaries = []
hiddenimports = []

# Módulos principales que DEBEN incluirse
packages = [
    'flask',
    'werkzeug',
    'jinja2',
    'click',
    'itsdangerous',
    'markupsafe',
    'selenium',
    'pandas',
    'numpy',
    'openpyxl',
    'requests',
    'urllib3',
    'certifi',
    'charset_normalizer',
    'idna',
]

# Agregar templates y static manualmente
# Usar el directorio actual de trabajo que será la raíz del proyecto
import os
basedir = os.path.abspath('.')
datas.append((os.path.join(basedir, 'templates'), 'templates'))
datas.append((os.path.join(basedir, 'static'), 'static'))

# Recopilar TODO de cada paquete (datos, binarios, submódulos)
for pkg in packages:
    try:
        pkg_datas, pkg_binaries, pkg_hiddenimports = collect_all(pkg)
        datas += pkg_datas
        binaries += pkg_binaries
        hiddenimports += pkg_hiddenimports
        print(f"[OK] Recopilado: {pkg}")
    except Exception as e:
        print(f"[WARNING] No se pudo recopilar {pkg}: {e}")

# Agregar submódulos explícitamente
hiddenimports += collect_submodules('scrapers')
hiddenimports += collect_submodules('src')
hiddenimports += collect_submodules('flask')
hiddenimports += collect_submodules('selenium')
hiddenimports += collect_submodules('pandas')

# Imports ocultos críticos adicionales
hiddenimports += [
    'flask.json',
    'flask.json.tag',
    'werkzeug.routing',
    'werkzeug.security',
    'werkzeug.serving',
    'selenium.webdriver.chrome.service',
    'selenium.webdriver.common.by',
    'pandas._libs',
    'pandas._libs.tslibs',
    'openpyxl.cell._writer',
]

a = Analysis(
    ['app.py'],
    pathex=[basedir],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['matplotlib', 'tkinter', 'test'],
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
