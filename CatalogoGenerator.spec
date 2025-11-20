# -*- mode: python ; coding: utf-8 -*-
import sys
import os
from PyInstaller.utils.hooks import collect_all, collect_submodules, collect_data_files

block_cipher = None

# Directorio base
basedir = os.path.abspath('.')

# Inicializar listas
datas = []
binaries = []
hiddenimports = []

# Agregar templates y static PRIMERO
datas.append((os.path.join(basedir, 'templates'), 'templates'))
datas.append((os.path.join(basedir, 'static'), 'static'))

# IMPORTS OCULTOS CRÍTICOS - Agregar TODOS los submódulos explícitamente
print("[INFO] Recopilando submódulos de Flask...")
hiddenimports += collect_submodules('flask')
hiddenimports += collect_submodules('werkzeug')
hiddenimports += collect_submodules('jinja2')
hiddenimports += collect_submodules('click')
hiddenimports += collect_submodules('itsdangerous')
hiddenimports += collect_submodules('markupsafe')

print("[INFO] Recopilando submódulos de Selenium...")
hiddenimports += collect_submodules('selenium')

print("[INFO] Recopilando submódulos de Pandas...")
hiddenimports += collect_submodules('pandas')
hiddenimports += collect_submodules('numpy')

print("[INFO] Recopilando submódulos de OpenPyXL...")
hiddenimports += collect_submodules('openpyxl')

print("[INFO] Recopilando submódulos de Requests...")
hiddenimports += collect_submodules('requests')
hiddenimports += collect_submodules('urllib3')
hiddenimports += collect_submodules('certifi')
hiddenimports += collect_submodules('charset_normalizer')
hiddenimports += collect_submodules('idna')

print("[INFO] Recopilando submódulos del proyecto...")
hiddenimports += collect_submodules('scrapers')
hiddenimports += collect_submodules('src')

# Ahora recopilar datos y binarios de los paquetes principales
packages_for_data = ['werkzeug', 'jinja2', 'selenium', 'pandas', 'numpy', 'openpyxl']

for pkg in packages_for_data:
    try:
        pkg_datas, pkg_binaries, _ = collect_all(pkg)
        datas += pkg_datas
        binaries += pkg_binaries
        print(f"[OK] Datos/binarios recopilados: {pkg}")
    except Exception as e:
        print(f"[WARNING] Error recopilando {pkg}: {e}")

# Imports adicionales específicos
hiddenimports += [
    'flask',
    'flask.app',
    'flask.blueprints',
    'flask.cli',
    'flask.config',
    'flask.ctx',
    'flask.globals',
    'flask.helpers',
    'flask.json',
    'flask.json.tag',
    'flask.logging',
    'flask.sessions',
    'flask.signals',
    'flask.templating',
    'flask.testing',
    'flask.views',
    'flask.wrappers',
    'werkzeug.routing',
    'werkzeug.security',
    'werkzeug.serving',
    'werkzeug.middleware.dispatcher',
    'werkzeug.middleware.shared_data',
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
