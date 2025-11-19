#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test completo: Sephora desde 3 sitios
"""

import sys
sys.stdout.reconfigure(encoding='utf-8')

import pandas as pd
from scrapers.sephora import scrape_sephora
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import time
import os

# URLs de Sephora en diferentes sitios
URLS = {
    "Sephora.com": "https://www.sephora.com/product/the-ordinary-hyaluronic-acid-2-b5-hydrating-serum-P427419",
    "Amazon": "https://www.amazon.com/Ordinary-Hyaluronic-Hydrating-Serum-Ceramides/dp/B0868NYYX3",
    "eBay": "https://www.ebay.com/itm/175839772883"
}

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
wait = WebDriverWait(driver, 10)

results = []

try:
    for sitio, url in URLS.items():
        print(f"\n{'='*60}")
        print(f"Scrapeando {sitio}...")
        print(f"URL: {url[:80]}...")
        print('='*60)
        
        try:
            result = scrape_sephora(driver, wait, url)
            
            if result:
                print(f"✅ {sitio} completado")
                print(f"   Nombre: {result['nombre'][:60]}")
                print(f"   Precio: {result['precio']}")
                print(f"   Tallas: {result['tallas'][:50]}")
                results.append(result)
            else:
                print(f"❌ No se pudo scrapear {sitio}")
                
        except Exception as e:
            print(f"❌ Error: {str(e)[:100]}")
        
        time.sleep(2)

finally:
    driver.quit()

# Generar Excel
if results:
    print(f"\n{'='*60}")
    print(f"📊 Generando Excel con {len(results)} registros...")
    print('='*60)
    
    df = pd.DataFrame(results)
    downloads = os.path.expanduser("~/Downloads")
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    excel_path = os.path.join(downloads, f"test_sephora_3sitios_{timestamp}.xlsx")
    df.to_excel(excel_path, index=False)
    
    print(f"✅ Excel guardado: {excel_path}")
    print(f"\n📋 Contenido:")
    print(df.to_string())
else:
    print("❌ No hay datos para generar Excel")
