#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test rápido solo eBay
"""

import sys
sys.stdout.reconfigure(encoding='utf-8')

from scrapers.nike import scrape_nike
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import time
import pandas as pd
import os

# URL de eBay
EBAY_URL = "https://www.ebay.com/itm/357896320478"

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
wait = WebDriverWait(driver, 10)

try:
    print("="*60)
    print("Scrapeando eBay...")
    print("="*60)
    
    result = scrape_nike(driver, wait, EBAY_URL)
    
    if result:
        print("\n✅ Scraping completado")
        print(f"Nombre: {result['nombre'][:70]}")
        print(f"Precio: {result['precio']}")
        print(f"Tallas: {result['tallas']}")
        print(f"Sitio: {result['sitio']}")
        
        # Crear Excel
        df = pd.DataFrame([result])
        downloads = os.path.expanduser("~/Downloads")
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        excel_path = os.path.join(downloads, f"test_ebay_nike_{timestamp}.xlsx")
        df.to_excel(excel_path, index=False)
        print(f"\n📊 Excel guardado: {excel_path}")
    else:
        print("❌ No se pudo scrapear")
        
finally:
    driver.quit()
