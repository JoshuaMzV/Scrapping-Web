#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para compilar el proyecto a ejecutable con PyInstaller
Uso: python build_exe.py
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

# Asegurar que stdout usa UTF-8
sys.stdout.reconfigure(encoding='utf-8') if hasattr(sys.stdout, 'reconfigure') else None

def build_exe():
    """Compilar proyecto a .exe"""
    
    project_root = os.path.dirname(os.path.abspath(__file__))
    dist_dir = os.path.join(project_root, 'dist')
    build_dir = os.path.join(project_root, 'build')
    spec_file = os.path.join(project_root, 'CatalogoGenerator.spec')
    
    print("=" * 60)
    print("🔨 Compilando Catálogo Generator a .exe")
    print("=" * 60)
    
    # Limpiar compilaciones previas
    print("\n🧹 Limpiando compilaciones previas...")
    for dir_to_remove in [dist_dir, build_dir]:
        if os.path.exists(dir_to_remove):
            shutil.rmtree(dir_to_remove)
            print(f"   ✅ {dir_to_remove} eliminado")
    
    if os.path.exists(spec_file):
        os.remove(spec_file)
        print(f"   ✅ {spec_file} eliminado")
    
    # Comando PyInstaller
    print("\n📦 Compilando con PyInstaller...")
    cmd = [
        sys.executable, '-m', 'PyInstaller',
        '--name=CatalogoGenerator',
        '--onefile',
        '--windowed',
        '--add-data', f'{os.path.join(project_root, "templates")}' + os.pathsep + 'templates',
        '--add-data', f'{os.path.join(project_root, "static")}' + os.pathsep + 'static',
        '--hidden-import=flask',
        '--hidden-import=flask.templating',
        '--hidden-import=jinja2',
        '--hidden-import=werkzeug',
        '--hidden-import=click',
        '--hidden-import=itsdangerous',
        '--hidden-import=markupsafe',
        '--hidden-import=pandas',
        '--hidden-import=numpy',
        '--hidden-import=selenium',
        '--hidden-import=selenium.webdriver',
        '--hidden-import=selenium.webdriver.chrome.service',
        '--hidden-import=selenium.webdriver.common.by',
        '--hidden-import=openpyxl',
        '--hidden-import=openpyxl.styles',
        '--hidden-import=requests',
        '--hidden-import=urllib3',
        '--hidden-import=certifi',
        '--hidden-import=charset_normalizer',
        '--hidden-import=idna',
        '--collect-all=flask',
        '--collect-all=jinja2',
        '--collect-all=werkzeug',
        '--collect-submodules=scrapers',
        '--collect-submodules=src',
        '--distpath', dist_dir,
        '--workpath', build_dir,
        'app.py'
    ]
    
    result = subprocess.run(cmd, cwd=project_root)
    
    if result.returncode == 0:
        print("\n" + "=" * 60)
        print("✅ ¡COMPILACIÓN EXITOSA!")
        print("=" * 60)
        exe_path = os.path.join(dist_dir, 'CatalogoGenerator.exe')
        print(f"\n📍 Ejecutable creado en:")
        print(f"   {exe_path}")
        print(f"\n📊 Tamaño: {os.path.getsize(exe_path) / (1024*1024):.1f} MB")
        print(f"\n🚀 Para ejecutar: Abre {exe_path}")
        print("=" * 60)
        return True
    else:
        print("\n❌ Error en compilación")
        return False

if __name__ == '__main__':
    success = build_exe()
    sys.exit(0 if success else 1)
