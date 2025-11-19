#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test script: Scrape Nike desde 3 sitios simultáneamente
- Nike.com (EU sizes)
- Amazon (US sizes)
- eBay (variable sizes)
"""

import sys
sys.stdout.reconfigure(encoding='utf-8')

import pandas as pd
from scrapers.nike import scrape_nike
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import time
import os

# URLs de prueba
URLS = {
    "Nike.com": "https://www.nike.com/w/mens-shoes-nik1zy7ok",  # Página de productos
    "Amazon": "https://www.amazon.com/Nike-Air-Force-Basketball-White/dp/B07QH7SCWW",
    "eBay": "https://a.co/d/h7L71Qy"
}

def test_3sitios():
    """Scrape Nike desde los 3 sitios y generar Excel"""
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    wait = WebDriverWait(driver, 10)
    
    results = []
    
    try:
        for sitio, url in URLS.items():
            print(f"\n{'='*60}")
            print(f"🔍 Scrapeando {sitio}...")
            print(f"   URL: {url[:80]}...")
            print('='*60)
            
            try:
                # Llamar al scraper
                data = scrape_nike(driver, wait, url)
                
                if data:
                    print(f"✅ {sitio} completado")
                    print(f"   Nombre: {data.get('nombre', 'N/A')[:60]}...")
                    print(f"   Precio: {data.get('precio', 'N/A')}")
                    print(f"   Tallas: {data.get('tallas', 'N/A')}")
                    print(f"   Sitio: {data.get('sitio', 'N/A')}")
                    results.append(data)
                else:
                    print(f"❌ No se pudo scrapear {sitio}")
                    
            except Exception as e:
                print(f"❌ Error en {sitio}: {str(e)[:100]}")
            
            time.sleep(2)
    
    finally:
        driver.quit()
    
    # Generar Excel
    if results:
        print(f"\n{'='*60}")
        print(f"📊 Generando Excel con {len(results)} registros...")
        print('='*60)
        
        df = pd.DataFrame(results)
        
        # Descargas folder
        downloads = os.path.expanduser("~/Downloads")
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        excel_path = os.path.join(downloads, f"test_3sitios_nike_{timestamp}.xlsx")
        
        df.to_excel(excel_path, index=False)
        
        print(f"✅ Excel guardado: {excel_path}")
        print(f"\n📋 Contenido:")
        print(df.to_string())
    else:
        print("❌ No hay datos para generar Excel")

if __name__ == "__main__":
    test_3sitios()
