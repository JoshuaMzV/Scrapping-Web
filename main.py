#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Catálogo Generator - Punto de Entrada Principal

Este es el archivo para iniciar la aplicación.
Ejecutar con: python main.py
"""

import os
import sys
import webbrowser
from time import sleep

# Agregar el directorio actual al path de Python
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    """Función principal - Inicia la aplicación Flask"""
    
    print("=" * 60)
    print("🚀 CATÁLOGO GENERATOR")
    print("=" * 60)
    print()
    
    # Importar configuración
    from src.config import FLASK_HOST, FLASK_PORT
    
    # Importar aplicación Flask
    from app import app
    
    # URL local
    url = f"http://{FLASK_HOST}:{FLASK_PORT}"
    
    print(f"📍 Servidor iniciando en: {url}")
    print()
    print("✅ El navegador se abrirá automáticamente...")
    print("⏳ Si no se abre, visita: " + url)
    print()
    print("📝 Presiona Ctrl+C para detener el servidor")
    print()
    print("=" * 60)
    print()
    
    # Abrir navegador después de 1 segundo
    sleep(1)
    try:
        webbrowser.open(url)
    except:
        print("⚠️  No se pudo abrir el navegador automáticamente")
        print(f"   Abre manualmente: {url}")
    
    # Iniciar servidor Flask
    app.run(host=FLASK_HOST, port=FLASK_PORT, debug=False)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Servidor detenido.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
